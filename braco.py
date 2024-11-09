from pybricks.hubs import PrimeHub

from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Direction

from pybricks.tools      import wait, StopWatch

from bluetooth import comando_bt, TX_BRACO, TX_CABECA

import garra

def setup():
    global hub, motor_garra, sensor_cor_frente, ultra_dir, ultra_esq
    global garra_fechada

    hub = PrimeHub(broadcast_channel=TX_BRACO, observe_channels=[TX_CABECA])
    
    motor_garra = Motor(Port.C)

    sensor_cor_frente = ColorSensor(Port.A)
    ultra_esq = UltrasonicSensor(Port.E)
    ultra_dir = UltrasonicSensor(Port.F)

    garra_fechada = False

    hub.system.set_stop_button((Button.CENTER,))
    return hub

def main(hub):
    global garra_fechada

    #contador_msgs = 0
    while True:
        comando = hub.ble.observe(TX_CABECA)
        if comando is not None:
            #id_msg, 
            comando, *args = comando
        else: continue

        #if id_msg <= contador_msgs: continue

        if   comando == comando_bt.fecha_garra:
            if not garra_fechada:
                garra.fecha_garra(motor_garra)
                garra_fechada = True
            hub.ble.broadcast((comando_bt.fechei,))
        elif comando == comando_bt.abre_garra:
            if garra_fechada:
                garra.abre_garra(motor_garra)
                garra_fechada = False
            hub.ble.broadcast((comando_bt.abri,))
            
        elif comando == comando_bt.ver_cor_passageiro:
            cor = sensor_cor_frente.color() #! reclassificar co hsv se der NONE
            hub.ble.broadcast((comando_bt.cor_passageiro, cor.h,cor.s,cor.v))    
        elif comando == comando_bt.ver_distancias:
            dist_esq, dist_dir = ultra_esq.distance(), ultra_dir.distance()
            hub.ble.broadcast((comando_bt.distancias, dist_esq, dist_dir))
