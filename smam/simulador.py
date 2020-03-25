#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: simulador.py
# Capitulo: 3 Patrón Publica-Subscribe
# Autor(es): Perla Velasco & Yonathan Mtz.
# Version: 2.0.1 Mayo 2017
# Descripción:
#
#   Esta clase define el rol de un set-up, es decir, simular el funcionamiento de los wearables del caso de estudio.
#
#   Las características de ésta clase son las siguientes:
#
#                                          simulador.py
#           +-----------------------+-------------------------+------------------------+
#           |  Nombre del elemento  |     Responsabilidad     |      Propiedades       |
#           +-----------------------+-------------------------+------------------------+
#           |                       |  - Iniciar el entorno   |  - Define el id inicial|
#           |        set-up         |    de simulación.       |    a partir del cuál se|
#           |                       |                         |    iniciarán los weara-|
#           |                       |                         |    bles.               |
#           +-----------------------+-------------------------+------------------------+
#
#   A continuación se describen los métodos que se implementaron en ésta clase:
#
#                                               Métodos:
#           +-------------------------+--------------------------+-----------------------+
#           |         Nombre          |        Parámetros        |        Función        |
#           +-------------------------+--------------------------+-----------------------+
#           |                         |                          |  - Inicializa los     |
#           |                         |                          |    publicadores       |
#           |     set_up_sensors()    |          Ninguno         |    necesarios para co-|
#           |                         |                          |    menzar la simula-  |
#           |                         |                          |    ción.              |
#           +-------------------------+--------------------------+-----------------------+
#           |                         |                          |  - Ejecuta el método  |
#           |                         |                          |    publish de cada    |
#           |     start_sensors()     |          Ninguno         |    sensor para publi- |
#           |                         |                          |    car los signos vi- |
#           |                         |                          |    tales.             |
#           +-------------------------+--------------------------+-----------------------+
#
#-------------------------------------------------------------------------
import sys
sys.path.append('publicadores')
from xiaomi_my_band import XiaomiMyBand


class Simulador:
    sensores = []
    id_inicial = 39722608

    def set_up_sensors(self):
        print('+---------------------------------------------+')
        print('|  Bienvenido al Simulador Publica-Subscribe  |')
        print('+---------------------------------------------+')
        print('')
        input('presiona enter para continuar: ')
        print('+---------------------------------------------+')
        print('|        CONFIGURACIÓN DE LA SIMULACIÓN       |')
        print('+---------------------------------------------+')
        adultos_mayores = input('|        número de adultos mayores: ')
        print('+---------------------------------------------+')
        input('presiona enter para continuar: ')
        print('+---------------------------------------------+')
        print('|            ASIGNACIÓN DE SENSORES           |')
        print('+---------------------------------------------+')
        for x in range(0, int(adultos_mayores)):
            s = XiaomiMyBand(self.id_inicial)
            self.sensores.append(s)
            print('| wearable Xiaomi My Band asignado, id: ' + str(self.id_inicial))
            print('+---------------------------------------------+')
            self.id_inicial += 1
        print('+---------------------------------------------+')
        print('|        LISTO PARA INICIAR SIMULACIÓN            |')
        print('+---------------------------------------------+')
        input('presiona enter para iniciar: ')
        self.start_sensors()

    def start_sensors(self):
        for x in range(0, 1000):
            for s in self.sensores:
                s.publish()

if __name__ == '__main__':
    simulador = Simulador()
    simulador.set_up_sensors()
