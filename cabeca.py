from pybricks.hubs import PrimeHub

from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Stop, Side, Direction, Button, Color

from pybricks.tools      import wait, StopWatch
from pybricks.robotics   import DriveBase

from bluetooth import comando_bt, TX_BRACO, TX_CABECA
from urandom import choice

import cores
import gui


TAM_BLOCO   = 300
TAM_BLOCO_Y = 294 # na nossa arena os quadrados não são 30x30cm (são 29.4 por quase 30)

TAM_FAIXA = 30
TAM_BLOCO_BECO = TAM_BLOCO_Y - TAM_FAIXA # os blocos dos becos são menores por causa do vermelho

DIST_EIXO_SENSOR = 80 #mm
DIST_EIXO_SENS_DIST = 45 #mm   #! checar

DIST_PASSAGEIRO_RUA = 220 #! checar

som_derrota = ["G4/4_", "F#4/4_", "F4/4_", "E4/3"]
som_vitoria = [ #! melhorar musiquinha (essa é quase mario)
                    "E3/4",
                    "E3/4",
                "R/4", 
                    "E3/4", 
                "R/4", 
                    "C3/4", "E3/4", 
                "R/4",
                    "G3/4",
                "R/4", "R/4", "R/4",
                    "G3/4",
                "R/4", "R/4", "R/4",
                    "C4/4",
                "R/4", "R/4",
                    "G3/4",
                "R/4", "R/4",
                    "E3/4", 
                "R/4", "R/4",
                    "A4/4",
                "R/4", 
                    "B4/4",
                "R/4", 
                    "A#4/4", "A4/4",
                "R/4",
                    "G3/3", "E3/3", "G3/3", "A4/4",
                "R/4", 
                    "F3/4", "G3/4",
                "R/4", 
                    "E3/4", 
                "R/4", 
                    "C3/4",
            ]


def setup():
    global hub, sensor_cor_esq, sensor_cor_dir, rodas, botao_calibrar
    global rodas_conf_padrao
    
    hub = PrimeHub(broadcast_channel=TX_CABECA, observe_channels=[TX_BRACO])

    hub.display.orientation(Side.BOTTOM)
    hub.system.set_stop_button((Button.CENTER, Button.BLUETOOTH))

    sensor_cor_esq = ColorSensor(Port.D)
    sensor_cor_dir = ColorSensor(Port.C)

    roda_esq = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
    roda_dir = Motor(Port.A, positive_direction=Direction.CLOCKWISE)

    rodas = DriveBase(roda_esq, roda_dir,
                      wheel_diameter=88, axle_track=145.5) #! ver depois se recalibrar

    botao_calibrar = Button.CENTER
    rodas_conf_padrao = rodas.settings()

    return hub

def menu_calibracao(hub, sensor_esq, sensor_dir,
                                     botao_parar=Button.BLUETOOTH,
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
                cores.coletar_valores(hub, botao_aceitar, dir=sensor_dir, esq=sensor_esq)
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

pista_hsv  = lambda hsv: ((cores.identificar(hsv) == cores.cor.BRANCO) or
                          (cores.identificar(hsv) == cores.cor.NENHUMA))
parede_hsv = lambda hsv: ((cores.identificar(hsv) == cores.cor.PRETO) or
                          (cores.identificar(hsv) == cores.cor.AMARELO) or
                          (cores.identificar(hsv) == cores.cor.NENHUMA))

def dar_meia_volta():
    rodas.turn(180)
    rodas.straight(TAM_BLOCO)

DIST_PARAR=-0.4
def parar():
    rodas.straight(DIST_PARAR)
    rodas.stop()

ANG_PARAR=-0.0
def parar_girar():
    rodas.turn(ANG_PARAR)
    rodas.stop()
    
def achar_limite() -> tuple[Color, hsv, Color, hsv]:
    rodas.reset()
    rodas.straight(TAM_BLOCO*6, wait=False)
    while not rodas.done():
        cor_esq = sensor_cor_esq.color()
        cor_dir = sensor_cor_dir.color()
        if not pista(cor_esq) or not pista(cor_dir):
            parar(); break

    hsv_esq = sensor_cor_esq.hsv()
    hsv_dir = sensor_cor_dir.hsv()
    return (cor_esq, hsv_esq, cor_dir, hsv_dir)

def ver_nao_pista():
    cor_esq = sensor_cor_esq.color()
    cor_dir = sensor_cor_dir.color()
    return (not pista(cor_esq) or not pista(cor_dir)), cor_esq, cor_dir

def ver_passageiro_perto():
    dist_esq, dist_dir = ver_distancias()
    return ((dist_esq < DIST_PASSAGEIRO_RUA or dist_dir < DIST_PASSAGEIRO_RUA),
            dist_esq, dist_dir)

def andar_ate(*conds_parada: Callable, dist_max=TAM_BLOCO*6) -> tuple[bool, Any]:
    rodas.reset()
    rodas.straight(dist_max, wait=False)
    while not rodas.done():
        for i, cond_parada in enumerate(conds_parada):
            chegou, *retorno = cond_parada()
            if not chegou: continue
            else:
                parar()
                return i+1, retorno
    return 0, ()

def re_meio_bloco(eixo_menor=False):
    if eixo_menor:
        rodas.straight(-(TAM_BLOCO_Y//2 - DIST_EIXO_SENSOR))
    else:
        rodas.straight(-(TAM_BLOCO//2   - DIST_EIXO_SENSOR))

def achar_azul():
    cor_esq, hsv_esq, cor_dir, hsv_dir = achar_limite() # anda reto até achar o limite

    if   beco(cor_esq) or beco(cor_dir): #! beco é menor que os outros blocos
        print(f"achar_azul:91: {cor_esq=}, {cor_dir=}")

        re_meio_bloco()
        rodas.straight(-TAM_BLOCO_BECO) 
        rodas.turn(choice((90, -90)))
        

        cor_esq, hsv_esq, cor_dir, hsv_dir = achar_limite() # anda reto até achar o limite
        print(f"achar_azul:97: {cor_esq=}, {cor_dir=}")

        if parede_hsv(hsv_esq) or parede_hsv(hsv_dir): rodas.turn(180)

        cor_esq, hsv_esq, cor_dir, hsv_dir = achar_limite() # anda reto até achar o limite
        print(f"achar_azul:105: {cor_esq=}, {cor_dir=}")

        return certificar_cor(sensor_cor_dir, sensor_cor_esq, Color.BLUE)
    elif parede(cor_esq) or parede(cor_dir): #! hsv
        print(f"achar_azul:109: {cor_esq=}, {cor_dir=}")

        re_meio_bloco()
        rodas.turn(90)

        return False
    else: #azul
        print(f"achar_azul:114: {cor_esq=}, {cor_dir=}")

        cor_esq, hsv_esq, cor_dir, hsv_dir = achar_limite() # anda reto até achar o limite
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
    while True:
        cor_dir = sensor_cor_dir.color()
        cor_esq = sensor_cor_esq.color()
        print(cor_dir, cor_esq)

        ang_girado = 0.0
        dist_percorrida = 0.0
        rodas.straight(TAM_BLOCO/10, wait=False)
        if rodas.distance() > TAM_BLOCO*4//5:
            rodas.straight(-rodas.distance(), wait=True)
            rodas.turn(90)
            rodas.reset()
            continue

        if not pista(cor_esq) or not pista(cor_dir):
            parar()
            dist_percorrida = rodas.distance()
            if not pista(cor_esq) and not pista(cor_dir):
                print("ENTREI RETO")
                rodas.straight(-dist_percorrida, wait=True)
                return True
            else:
                print("ENTREI TORTO")
                rodas.turn(-90, wait=False)
                cor_dir = sensor_cor_dir.color()
                cor_esq = sensor_cor_esq.color()
                if not (pista(cor_dir) ^ pista(cor_esq)):
                    print("cor_igual")
                    parar_girar()
                    ang_girado = rodas.angle()
                    rodas.turn(-ang_girado, wait=True)
                    rodas.straight(-dist_percorrida, wait=True)                
                    rodas.turn(ang_girado, wait=True)

                    rodas.turn(90)
                    rodas.reset()
                    return alinhar()


def esperar_resposta(esperado):
    comando = -1
    while comando != esperado:
        comando = hub.ble.observe(TX_BRACO)
        if comando is not None:
            comando, *args = comando
    return args

def fechar_garra():
    hub.ble.broadcast((comando_bt.fecha_garra,))
    return esperar_resposta(comando_bt.fechei)

def abrir_garra():
    hub.ble.broadcast((comando_bt.abre_garra,))
    return esperar_resposta(comando_bt.abri)

def ver_cor_passageiro():
    hub.ble.broadcast((comando_bt.ver_cor_passageiro,))
    return esperar_resposta(comando_bt.cor_passageiro)

def ver_distancias():
    hub.ble.broadcast((comando_bt.ver_distancias,))
    return esperar_resposta(comando_bt.distancias)

def pegar_primeiro_passageiro():
    #! a cor é pra ser azul
    _, *conf_resto  = rodas_conf_padrao
    vel, conf_atual = 50, conf_resto

    rodas.turn(90)
    achar_limite()
    #! a cor é pra ser vermelha

    rodas.turn(180)

    rodas.settings(vel, *conf_atual)
    res, extra = andar_ate(ver_nao_pista, ver_passageiro_perto,
                           dist_max=TAM_BLOCO*4)
    rodas.settings(*rodas_conf_padrao)
    if   res==1:
        (cor_esq, cor_dir) = extra
        parar()
        re_meio_bloco()
        return False # é pra ter chegado no vermelho #! a cor é pra ser vermelha
    elif res==2:
        (dist_esq, dist_dir) = extra
        dist = dist_esq if dist_esq < dist_dir else dist_dir
        parar()
        rodas.straight(-(DIST_EIXO_SENS_DIST-20)) #! desmagificar
        rodas.turn(90)
        abrir_garra()
        rodas.straight(dist)
        fechar_garra()
        return True
    else:
        return False #chegou na distância máxima

def main(hub):
    crono = StopWatch()
    while crono.time() < 0: #! ativar calibração quando for usar
        botões = hub.buttons.pressed()
        if botao_calibrar in botões:
            hub.speaker.beep(frequency=300, duration=100)
            #! levar os dois sensores em consideração separadamente
            mapa_hsv = menu_calibracao(hub, sensor_cor_esq, sensor_cor_dir)
            cores.repl_calibracao(mapa_hsv)#, lado="esq")
            return

    hub.system.set_stop_button((Button.BLUETOOTH,))
    hub.speaker.beep(frequency=600, duration=100)

    #! antes de qualquer coisa, era bom ver se na sua frente tem obstáculo
    #! sobre isso ^ ainda, tem que tomar cuidado pra não confundir eles com os passageiros
    alinhou = achou_azul = False
    while not alinhou:
        alinhou = alinhar()
    while not achou_azul:
        achou_azul = achar_azul()
        
    pegou = pegar_primeiro_passageiro()
    if pegou:
        dar_meia_volta()
        abrir_garra()
        hub.speaker.play_notes(som_vitoria, tempo=200)
    else:
        hub.speaker.play_notes(som_derrota)
        wait(1000)
        return #! fazer main retornar que nem em c e tocar o som com base nisso
