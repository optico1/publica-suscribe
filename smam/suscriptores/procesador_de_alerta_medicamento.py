#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: procesador_de_alerta_medicamento.py
# Capitulo: 3 Estilo Publica-Subscribe
# Autor(es): Perla Velasco, Yonathan Mtz, Salvador Loera, Bryan Villa, Javier Sosa & Manuel Herrera.
# Version: 2.0.2 Marzo 2020
# Descripción:
#
#   Esta clase define el rol de un suscriptor, es decir, es un componente que recibe mensajes.
#
#   Las características de ésta clase son las siguientes:
#
#                                   procesador_de_alerta_medicamento.py
#           +-----------------------+-------------------------+------------------------+
#           |  Nombre del elemento  |     Responsabilidad     |      Propiedades       |
#           +-----------------------+-------------------------+------------------------+
#           |                       |                         |  - Se suscribe a los   |
#           |                       |                         |    eventos generados   |
#           |                       |  - Procesar el tiempo   |    por el wearable     |
#           |     Procesador de     |    para detectar que    |    Xiaomi My Band.     |
#           |     Alerta de         |    medicamento le toca a|  - Define el horario de|
#           |     Medicamento       |    cada adulto.         |    medicamento.        |
#           |                       |                         |  - Notifica al monitor |
#           |                       |                         |    cuando le toca un   |
#           |                       |                         |    medicamento al      |
#           |                       |                         |    adulto.             |
#           |                       |                         |                        |
#           +-----------------------+-------------------------+------------------------+
#
#   A continuación se describen los métodos que se implementaron en ésta clase:
#
#                                               Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Recibe los signos  |
#           |       consume()        |          Ninguno         |    vitales vitales    |
#           |                        |                          |    desde el distribui-|
#           |                        |                          |    dor de mensajes.   |
#           +------------------------+--------------------------+-----------------------+
#           |                        |  - ch: propio de Rabbit. |  - Procesa y detecta  |
#           |                        |  - method: propio de     |    valores extremos   |
#           |                        |     Rabbit.              |    de la temperatura. |
#           |       callback()       |  - properties: propio de |                       |
#           |                        |     Rabbit.              |                       |
#           |                        |  - body: mensaje recibi- |                       |
#           |                        |     do.                  |                       |
#           +------------------------+--------------------------+-----------------------+
#           |    check_schedule()    |  - time: tiempo actual   |  - Verifica el horario|
#           |                        |     a revisar.           |    y el medicamento   |
#           |                        |                          |    que le toca.       |
#           +------------------------+--------------------------+-----------------------+
#           |    string_to_json()    |  - string: texto a con-  |  - Convierte un string|
#           |                        |     vertir en JSON.      |    en un objeto JSON. |
#           +------------------------+--------------------------+-----------------------+
#
#
#           Nota: "propio de Rabbit" implica que se utilizan de manera interna para realizar
#            de manera correcta la recepcion de datos, para éste ejemplo no shubo necesidad
#            de utilizarlos y para evitar la sobrecarga de información se han omitido sus
#            detalles. Para más información acerca del funcionamiento interno de RabbitMQ
#            puedes visitar: https://www.rabbitmq.com/
#
#-------------------------------------------------------------------------
import pika
import sys
import time
import random
sys.path.append('../')
from monitor import Monitor
from datetime import datetime

MEDS = (
    "Paracetamol",
    "Ibuprofeno",
    "Insulina",
    "Furosemida",
    "Piroxicam",
    "Tolbutamida",
)

class ProcesadorAlertaMedicamento:

    def consume(self):
        try:
            # Se establece la conexión con el Distribuidor de Mensajes
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            # Se solicita un canal por el cuál se enviarán los signos vitales
            channel = connection.channel()
            # Se declara una cola para leer los mensajes enviados por el
            # Publicador
            channel.queue_declare(queue='time', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(on_message_callback=self.callback, queue='time')
            channel.start_consuming()  # Se realiza la suscripción en el Distribuidor de Mensajes
        except (KeyboardInterrupt, SystemExit):
            channel.close()  # Se cierra la conexión
            sys.exit("Conexión finalizada...")
            time.sleep(1)
            sys.exit("Programa terminado...")

    def callback(self, ch, method, properties, body):
        json_message = self.string_to_json(body)
        med = self.check_schedule(json_message['datetime'])
        # med = self.check_schedule(json_message['datetime'], json_message['datetime'])
        if med:
            monitor = Monitor()
            monitor.print_alarma(json_message['datetime'], json_message['id'], random.randint(10, 50), med, json_message['model'])
        time.sleep(1)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def check_schedule(self, time):
        med = None
        rand_hour = random.randint(0, 24)
        date = datetime.strptime(time, "%d:%m:%Y:%H:%M:%S")
        if int(datetime.strftime(date, "%H")) == rand_hour:
            med = random.choice(MEDS)
        return med
        

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
    p_medicamento = ProcesadorAlertaMedicamento()
    p_medicamento.consume()