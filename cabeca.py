from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color

from pybricks.tools      import wait, StopWatch
from pybricks.robotics   import DriveBase

import cores
import gui

TAM_FAIXA = 30
TAM_BLOCO   = 300
TAM_BLOCO_Y = 294 #na nossa arena os quadrados não são 30x30cm (são 29.4 por quase 30)
TAM_BLOCO_BECO = TAM_BLOCO_Y - TAM_FAIXA #os blocos dos becos são menores por causa do vermelho

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

DIST_EIXO_SENSOR = 80 #mm

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
            rodas.stop(); break

    return (cor_esq, cor_dir)

def re_meio_bloco(eixo_menor=False):
    if eixo_menor:
        rodas.straight(-(TAM_BLOCO_Y//2 - DIST_EIXO_SENSOR), wait=True)
    else:
        rodas.straight(-(TAM_BLOCO//2 - DIST_EIXO_SENSOR), wait=True)

def achar_azul():
    cor_esq, cor_dir = achar_limite() # anda reto até achar o limite
    re_meio_bloco()

    print(f"achar_azul:84: {cor_esq=}, {cor_dir=}")

    if   beco(cor_esq) or beco(cor_dir): #! beco é menor que os outros blocos
        rodas.straight(-TAM_BLOCO_BECO) 
        rodas.turn(90)
        cor_esq, cor_dir = achar_limite() # anda reto até achar o limite

        print(f"achar_azul:91: {cor_esq=}, {cor_dir=}")

        if parede(cor_esq) or parede(cor_dir): rodas.turn(180)

        cor_esq, cor_dir = achar_limite() # anda reto até achar o limite

        print(f"achar_azul:97: {cor_esq=}, {cor_dir=}")

        return certificar_cor(sensor_cor_dir, sensor_cor_esq, cores.cor.AZUL)
    elif parede(cor_esq) or parede(cor_dir):
        print(f"achar_azul:104: {cor_esq=}, {cor_dir=}")
        rodas.turn(90)

        return False
    else: #azul
        cor_esq, cor_dir = sensor_cor_esq.color(), sensor_cor_dir.color()
        print(f"achar_azul:117: {cor_esq=}, {cor_dir=}")

        return certificar_cor(sensor_cor_dir, sensor_cor_esq, cores.cor.AZUL)



def certificar_cor(sensor_dir, sensor_esq, cor, cor2=None):
    cor2 = cor if cor2 is None else cor2

    tam_lista = 11
    esqs = [cores.Color2cor[sensor_esq.color()] for _ in range(tam_lista)]; esqs.sort()
    dirs = [cores.Color2cor[sensor_dir.color()] for _ in range(tam_lista)]; dirs.sort()
    mediana_esq = esqs[tam_lista//2]
    mediana_dir = dirs[tam_lista//2]

    if mediana_esq == mediana_dir:
        mediana = mediana_esq
        return mediana == cor == cor2

    if (mediana_esq == cor) or (mediana_dir == cor2):
        return True

    return False

def alinhar():
    pass

def main(hub):
    crono = StopWatch()
    while True:
        botões = hub.buttons.pressed()
        if botao_calibrar in botões:
            hub.speaker.beep(frequency=300, duration=100)
            menu_calibracao(hub, sensor_cor_esq)  #! levar os dois sensores em consideração

            return
        elif crono.time() > 400:
            if achar_azul():
                return #!


