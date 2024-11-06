from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Stop, Side, Direction, Button, Color

from pybricks.tools      import wait, StopWatch
from pybricks.robotics   import DriveBase

from urandom import choice

import cores
import gui

TAM_FAIXA = 30
TAM_BLOCO   = 300
TAM_BLOCO_Y = 294 #na nossa arena os quadrados não são 30x30cm (são 29.4 por quase 30)
TAM_BLOCO_BECO = TAM_BLOCO_Y - TAM_FAIXA #os blocos dos becos são menores por causa do vermelho

DIST_EIXO_SENSOR = 80 #mm

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

    hub.display.orientation(Side.BOTTOM)
    hub.system.set_stop_button((Button.CENTER, Button.BLUETOOTH))
    return hub

def menu_calibracao(hub, sensor_cor, botao_parar=Button.BLUETOOTH,
                                     botao_aceitar=Button.CENTER,
                                     botao_anterior=Button.LEFT,
                                     botao_proximo=Button.RIGHT):
    selecao = 0

    wait(150)
    while True:
        botões = gui.tela_escolher_cor(hub, cores.cor, selecao)
        
        if   botao_proximo  in botões:
            selecao = (selecao + 1) % len(cores.cor)
        elif botao_anterior in botões:
            selecao = (selecao - 1) % len(cores.cor)

        elif botao_aceitar in botões:
            [wait(100) for _ in gui.mostrar_palavra(hub, "CAL...")]
            cores.mapa_rgb[selecao], *cores.mapa_hsv[selecao] = (
                cores.calibrar(hub, sensor_cor, botao_aceitar)
            )
        elif botao_parar   in botões:
            cores.salvar_cores()
            break

pista  = lambda cor: ((cor == Color.WHITE) or
                      (cor == Color.NONE ))
parede = lambda cor: ((cor == Color.BLACK) or
                      (cor == Color.NONE ) or
                      (cor == Color.YELLOW))
beco   = lambda cor: ((cor == Color.RED))

def dar_meia_volta():
    rodas.turn(180)
    rodas.straight(TAM_BLOCO)

DIST_PARAR=-0.4
def parar():
    rodas.straight(DIST_PARAR)
    rodas.stop()

def achar_limite() -> tuple[Color, Color]:
    rodas.reset()
    rodas.straight(TAM_BLOCO*6, wait=False)
    while not rodas.done():
        cor_dir = sensor_cor_dir.color()
        cor_esq = sensor_cor_esq.color()
        if not pista(cor_esq) or not pista(cor_dir):
            parar(); break

    return (cor_esq, cor_dir)

def re_meio_bloco(eixo_menor=False):
    if eixo_menor:
        rodas.straight(-(TAM_BLOCO_Y//2 - DIST_EIXO_SENSOR), wait=True)
    else:
        rodas.straight(-(TAM_BLOCO//2 - DIST_EIXO_SENSOR), wait=True)

def achar_azul():
    cor_esq, cor_dir = achar_limite() # anda reto até achar o limite

    if   beco(cor_esq) or beco(cor_dir): #! beco é menor que os outros blocos
        print(f"achar_azul:91: {cor_esq=}, {cor_dir=}")

        re_meio_bloco()
        rodas.straight(-TAM_BLOCO_BECO) 
        rodas.turn(choice((90, -90)))

        cor_esq, cor_dir = achar_limite() # anda reto até achar o limite
        print(f"achar_azul:97: {cor_esq=}, {cor_dir=}")

        if parede(cor_esq) or parede(cor_dir): rodas.turn(180)

        cor_esq, cor_dir = achar_limite() # anda reto até achar o limite
        print(f"achar_azul:105: {cor_esq=}, {cor_dir=}")

        return certificar_cor(sensor_cor_dir, sensor_cor_esq, Color.BLUE)
    elif parede(cor_esq) or parede(cor_dir):
        print(f"achar_azul:109: {cor_esq=}, {cor_dir=}")

        re_meio_bloco()
        rodas.turn(90)

        return False
    else: #azul
        print(f"achar_azul:114: {cor_esq=}, {cor_dir=}")

        cor_esq, cor_dir = achar_limite() # anda reto até achar o limite
        print(f"achar_azul:117: {cor_esq=}, {cor_dir=}")

        if certificar_cor(sensor_cor_dir, sensor_cor_esq, Color.BLUE):
            return True
        else:
            re_meio_bloco()
            rodas.turn(90)
            return False

def certificar_cor(sensor_dir, sensor_esq, cor, cor2=None,
                   num_amostras=41):
    cor2 = cor if cor2 is None else cor2

    esqs = sorted([sensor_esq.color()
                   for _ in range(num_amostras)], key=lambda c: c.h)
    dirs = sorted([sensor_dir.color()
                   for _ in range(num_amostras)], key=lambda c: c.h)

    mediana_esq = esqs[num_amostras//2]
    mediana_dir = dirs[num_amostras//2]

    print(f"certificar_cor:143: dir {mediana_dir}, esq {mediana_esq}")

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
    while crono.time() < 1000:
        botões = hub.buttons.pressed()
        if botao_calibrar in botões:
            hub.speaker.beep(frequency=300, duration=100)
            menu_calibracao(hub, sensor_cor_esq)  #! levar os dois sensores em consideração
            return

    hub.system.set_stop_button((Button.BLUETOOTH,))
    hub.speaker.beep(frequency=600, duration=100)
    while True:
        achou = achar_azul()
        if achou: return #!
