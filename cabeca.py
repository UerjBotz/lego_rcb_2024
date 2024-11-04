from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color

from pybricks.tools      import wait, StopWatch
from pybricks.robotics   import DriveBase

import cores
import gui

TAM_BLOCO = 300

def setup():
    global hub, sensor_cor_esq, sensor_cor_dir, rodas, botao_calibrar
    
    hub = PrimeHub()

    sensor_cor_esq = ColorSensor(Port.D)
    sensor_cor_dir = ColorSensor(Port.C)

    roda_esq = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
    roda_dir = Motor(Port.A, positive_direction=Direction.CLOCKWISE)

    rodas = DriveBase(roda_esq, roda_dir,
                      wheel_diameter=88, axle_track=145.5) #! ver depois se recalibrar

    botao_calibrar = Button.CENTER

    hub.system.set_stop_button((Button.CENTER, Button.BLUETOOTH))
    return hub

def menu_calibracao(hub, sensor_cor, botao_parar=Button.BLUETOOTH,
                                     botao_aceitar=Button.CENTER,
                                     botao_anterior=Button.LEFT,
                                     botao_proximo=Button.RIGHT):
    selecao = 0

    while True:
        botões = gui.tela_escolher_cor(hub, cores.cor, selecao)
        
        if   botao_proximo  in botões:
            selecao = (selecao + 1) % len(cores.cor)
        elif botao_anterior in botões:
            selecao = (selecao - 1) % len(cores.cor)

        elif botao_aceitar in botões:
            hub.display.text("CALIBRANDO...")
            cores.mapa_rgb[selecao], *cores.mapa_hsv[selecao] = (
                cores.calibrar(hub, sensor_cor, botao_aceitar)
            )
        elif botao_parar   in botões:
            cores.salvar_cores()
            break

pista = lambda cor: ((cor == Color.WHITE) or
                     (cor == Color.NONE ))
parede= lambda cor: ((cor == Color.BLACK) or
                     (cor == Color.YELLOW))
beco  = lambda cor: ((cor == Color.RED))

def dar_meia_volta():
    rodas.turn(180)
    rodas.straight(TAM_BLOCO)

def achar_limite() -> tuple[Color, Color]:
    rodas.reset()
    rodas.straight(TAM_BLOCO*6, wait=False)
    while not rodas.done():
        cor_dir = sensor_cor_dir.color()
        cor_esq = sensor_cor_esq.color()
        if not pista(cor_esq) or not pista(cor_dir):
            dist = rodas.distance()

            rodas.reset()
            rodas.straight(-min(dist, TAM_BLOCO//2), wait=True)
            break

    return (cor_esq, cor_dir)


def achar_azul():
    cor_esq, cor_dir = achar_limite() # anda reto até achar o limite
    print(f"achar_azul:84: {cor_esq=}, {cor_dir=}")

    if   beco(cor_esq) or beco(cor_dir):
        dar_meia_volta() #rodas.straight(-455) 
        rodas.turn(-90)
        cor_esq, cor_dir = achar_limite() # anda reto até achar o limite

        print(f"achar_azul:91: {cor_esq=}, {cor_dir=}")

        if parede(cor_esq) or parede(cor_dir): rodas.turn(180)

        cor_esq, cor_dir = achar_limite() # anda reto até achar o limite

        print(f"achar_azul:97: {cor_esq=}, {cor_dir=}")
        assert cor_esq == Color.BLUE or cor_dir == Color.BLUE
        #! isso assume que a gente tá alinhado

        return

    elif parede(cor_esq) or parede(cor_dir):
        print(f"achar_azul:104: {cor_esq=}, {cor_dir=}")
        rodas.turn(90)
    else: #azul
        return #!

def alinhar():
    pass

def main(hub):
    while True:
        botões = hub.buttons.pressed()
        if botao_calibrar in botões:
            hub.speaker.beep(frequency=300, duration=100)
            menu_calibracao(hub, sensor_cor_esq)  #! levar os dois sensores em consideração

            return
        
        achar_azul()
        return

