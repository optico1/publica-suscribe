#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: procesador_de_posicion.py
# Capitulo: 3 Estilo Publica-Subscribe
# Autor(es): Perla Velasco & Yonathan Mtz.
# Version: 2.0.1 Mayo 2017
# Descripción:
#
#   Esta clase define el rol de un suscriptor, es decir, es un componente que recibe mensajes.
#
#   Las características de ésta clase son las siguientes:
#
#                                   procesador_de_posicion.py
#           +-----------------------+-------------------------+------------------------+
#           |  Nombre del elemento  |     Responsabilidad     |      Propiedades       |
#           +-----------------------+-------------------------+------------------------+
#           |                       |                         |  - Se suscribe a los   |
#           |                       |                         |    eventos generados   |
#           |                       |  - Procesar valores     |    por el wearable     |
#           |     Procesador de     |    extremos de          |    Xiaomi My Band.     |
#           |     Posición          |    aceleración.         |  - Define el valor ex- |
#           |                       |                         |    tremo de la         |
#           |                       |                         |    aceleración.        |
#           |                       |                         |  - Notifica al monitor |
#           |                       |                         |    cuando un valor ex- |
#           |                       |                         |    tremo es detectado. |
#           +-----------------------+-------------------------+------------------------+
#
#   A continuación se describen los métodos que se implementaron en ésta clase:
#
#                                               Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Recibe los signos  |
#           |       consume()        |          Ninguno         |    vitales desde el   |
#           |                        |                          |    distribuidor de    |
#           |                        |                          |    mensajes.          |
#           +------------------------+--------------------------+-----------------------+
#           |                        |  - ch: propio de Rabbit. |  - Procesa y detecta  |
#           |                        |  - method: propio de     |    valores extremos   |
#           |                        |     Rabbit.              |    de la aceleración. |
#           |       callback()       |  - properties: propio de |                       |
#           |                        |     Rabbit.              |                       |
#           |                        |  - body: mensaje recibi- |                       |
#           |                        |     do.                  |                       |
#           +------------------------+--------------------------+-----------------------+
#           |    string_to_json()    |  - string: texto a con-  |  - Convierte un string|
#           |                        |     vertir en JSON.      |    en un objeto JSON. |
#           +------------------------+--------------------------+-----------------------+
#           |                        |  - x: aceleración en el  |  - Calcula la señal de|
#           |                        |     eje de las x.        |    magnitud del       |
#           |                        |  - y: aceleración en el  |    vector             |
#           |       calc_svm()       |     eje de las y.        |    (aceleración del ) |
#           |                        |  - z: aceleración en el  |    cuerpo).           |
#           |                        |     eje de las z.        |                       |
#           |                        |                          |                       |
#           |                        |                          |                       |
#           +------------------------+--------------------------+-----------------------+
# 
#
#
#           Nota: "propio de Rabbit" implica que se utilizan de manera interna para realizar
#            de manera correcta la recepcion de datos, para éste ejemplo no hubo necesidad
#            de utilizarlos y para evitar la sobrecarga de información se han omitido sus
#            detalles. Para más información acerca del funcionamiento interno de RabbitMQ
#            puedes visitar: https://www.rabbitmq.com/
#
#-------------------------------------------------------------------------
import pika
import sys
sys.path.append('../')
from monitor import Monitor
import time
import math


class ProcesadorPosicion:

    prev_svm = None

    def consume(self):
        try:
            # Se establece la conexión con el Distribuidor de Mensajes
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            # Se solicita un canal por el cuál se enviarán los signos vitales
            channel = connection.channel()
            # Se declara una cola para leer los mensajes enviados por el
            # Publicador
            channel.queue_declare(queue='body_acceleration', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(on_message_callback=self.callback, queue='body_acceleration')
            channel.start_consuming()  # Se realiza la suscripción en el Distribuidor de Mensajes
        except (KeyboardInterrupt, SystemExit):
            channel.close()  # Se cierra la conexión
            sys.exit("Conexión finalizada...")
            time.sleep(1)
            sys.exit("Programa terminado...")

    def callback(self, ch, method, properties, body):
        json_message = self.string_to_json(body)
        svm = self.calc_svm(
            float(json_message['x']),
            float(json_message['y']),
            float(json_message['z'])
        )
        if self.prev_svm and (svm - self.prev_svm) >= 0.5:
            svm_diff = svm - self.prev_svm
            monitor = Monitor()
            monitor.print_notification(json_message['datetime'], json_message['id'], svm_diff, 'aceleración', json_message['model'])
        self.prev_svm = svm
        time.sleep(1)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def calc_svm(self, x, y, z):
        # Se calcula la aceleración del cuerpo SVM = √((𝐴𝑥)^2 + (𝐴𝑦)^2 + (𝐴𝑧)^2)
        x2 = pow(x, 2)
        y2 = pow(y, 2)
        z2 = pow(z, 2)
        sum = x2 + y2 + z2
        return math.sqrt(sum)

    def string_to_json(self, string):
        message = {}
        string = string.decode('utf-8')
        string = string.replace('{', '')
        string = string.replace('}', '')
        values = string.split(', ')
        for x in values:
            v = x.split(': ')
            message[v[0].replace('\'', '')] = v[1].replace('\'', '')
        return message

if __name__ == '__main__':
    p_posicion = ProcesadorPosicion()
    p_posicion.consume()