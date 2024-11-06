from pybricks.hubs import PrimeHub

from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Stop, Side, Direction, Button, Color

from pybricks.tools      import wait, StopWatch
from pybricks.robotics   import DriveBase

from bluetooth import comando_bt, TX_BRACO, TX_CABECA
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
    
    hub = PrimeHub(broadcast_channel=1, observe_channels=[2])

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
    mapa_hsv = cores.mapa_hsv.copy()

    selecao = 0

    wait(150)
    while True:
        botões = gui.tela_escolher_cor(hub, cores.cor, selecao)
        
        if   botao_proximo  in botões:
            selecao = (selecao + 1) % len(cores.cor)
            wait(100)
        elif botao_anterior in botões:
            selecao = (selecao - 1) % len(cores.cor)
            wait(100)

        elif botao_aceitar in botões:
            [wait(100) for _ in gui.mostrar_palavra(hub, "CAL...")]
            mapa_hsv[selecao] = (
                cores.coletar_valores(hub, sensor_cor, botao_aceitar)
            )
            wait(150)
        elif botao_parar   in botões:
            wait(100)
            return mapa_hsv

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

def certificar_cor(sensor_dir, sensor_esq, cor, cor2=None):
    cor2 = cor if cor2 is None else cor2 #! levar em consideração

    cor_dir = cores.identificar(sensor_dir.hsv())
    cor_esq = cores.identificar(sensor_esq.hsv())
    print(f"certificar_cor:148: {cores.cor(cor_esq)}, {cores.cor(cor_dir)}")

    return ((cor_dir == cores.Color2cor[cor]) or
            (cor_esq == cores.Color2cor[cor]))

def alinhar():
    pass

def mandar_fechar_garra():
    hub.ble.broadcast((comando_bt.fecha_garra,))
    comando = -1
    while comando != comando_bt.fechei:
        comando = hub.ble.observe(TX_BRACO)
        if comando is not None:
            comando, *args = comando
        else: continue

def mandar_abrir_garra():
    hub.ble.broadcast((comando_bt.abre_garra,))
    comando = -1
    while comando != comando_bt.abri:
        comando = hub.ble.observe(TX_BRACO)
        if comando is not None:
            comando, *args = comando
        else: continue

def main(hub):
    crono = StopWatch()
    while crono.time() < 1000:
        botões = hub.buttons.pressed()
        if botao_calibrar in botões:
            hub.speaker.beep(frequency=300, duration=100)

            #! levar os dois sensores em consideração
            mapa_hsv = menu_calibracao(hub, sensor_cor_esq)
            cores.repl_calibracao(mapa_hsv)#, lado="esq")
            return

    hub.system.set_stop_button((Button.BLUETOOTH,))
    hub.speaker.beep(frequency=600, duration=100)
    while True:
        achou = achar_azul()
        if achou: return #!
