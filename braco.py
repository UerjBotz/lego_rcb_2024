from pybricks.hubs import PrimeHub

from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Direction

from pybricks.tools      import wait, StopWatch

from bluetooth import comando_bt, TX_BRACO, TX_CABECA

import garra

def setup():
    global hub, motor_garra, sensor_cor_frente, ultra_dir, ultra_esq

    hub = PrimeHub(broadcast_channel=TX_BRACO, observe_channels=[TX_CABECA])
    
    motor_garra = Motor(Port.C, Direction.CLOCKWISE)

    sensor_cor_frente = ColorSensor(Port.A)
    ultra_esq = UltrasonicSensor(Port.E)
    ultra_dir = UltrasonicSensor(Port.F)

    hub.system.set_stop_button((Button.CENTER,))
    return hub


def main(hub):
    #contador_msgs = 0
    while True:
        #id_msg, 
        comando = hub.ble.observe(TX_CABECA)
        if comando is not None:
            comando, *args = comando
        else: continue

        #if id_msg <= contador_msgs: continue

        if   comando == comando_bt.fecha_garra:
            garra.fecha_garra(motor_garra)
            hub.ble.broadcast((comando_bt.fechei,))
        elif comando == comando_bt.abre_garra:
            garra.abre_garra(motor_garra)
            hub.ble.broadcast((comando_bt.abri,))

        elif comando == comando_bt.ver_cor_passageiro:
            cor = sensor_cor_frente.hsv()
            hub.ble.broadcast((comando_bt.cor_passageiro, cor.h,cor.s,cor.v))    
        elif comando == comando_bt.ver_distancias:
            dist_esq, dist_dir = ultra_esq.distance(), ultra_dir.distance()
            hub.ble.broadcast((comando_bt.distancias, dist_esq, dist_dir))
