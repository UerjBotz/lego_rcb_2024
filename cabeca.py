from pybricks.hubs import PrimeHub

from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Stop, Side, Direction, Button, Color

from pybricks.tools      import wait, StopWatch
from pybricks.robotics   import DriveBase

from lib.bipes     import bipe_calibracao, bipe_cabeca, musica_vitoria, musica_derrota
from lib.caminhos  import achar_movimentos, tipo_movimento

from urandom import choice

import cores
import gui
import bluetooth as blt


TAM_BLOCO   = 300
TAM_BLOCO_Y = 294 # na nossa arena os quadrados não são 30x30cm (são 29.4 por quase 30)

TAM_FAIXA = 30
TAM_BLOCO_BECO = TAM_BLOCO_Y - TAM_FAIXA # os blocos dos becos são menores por causa do vermelho

PISTA_TODA = TAM_BLOCO*6

DIST_EIXO_SENSOR = 80 #mm
DIST_EIXO_SENS_DIST = 45 #mm   #! checar

DIST_PASSAGEIRO_RUA = 220 #! checar


def setup():
    global hub, rodas, sensor_cor_esq, sensor_cor_dir, sensor_ultra_esq, sensor_ultra_dir
    global botao_calibrar, rodas_conf_padrao, ori
    
    ori = ""
    hub = PrimeHub(broadcast_channel=blt.TX_CABECA, observe_channels=[blt.TX_BRACO])
    print(hub.system.name())
    while hub.system.name() != "spike1":
        hub.speaker.beep(frequency=1024)
        wait(200)
    else:
        hub.light.blink(Color.RED, [100,50,200,100])

    hub.display.orientation(Side.BOTTOM)
    hub.system.set_stop_button((Button.CENTER, Button.BLUETOOTH))

    sensor_cor_esq = ColorSensor(Port.D)
    sensor_cor_dir = ColorSensor(Port.C)

    sensor_ultra_esq = UltrasonicSensor(Port.F)
    sensor_ultra_dir = UltrasonicSensor(Port.E)

    roda_esq = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
    roda_dir = Motor(Port.A, positive_direction=Direction.CLOCKWISE)

    rodas = DriveBase(roda_esq, roda_dir,
                      wheel_diameter=88, axle_track=145.5) #! ver depois se recalibrar

    botao_calibrar = Button.CENTER
    rodas_conf_padrao = rodas.settings()
    vels_padrao = rodas_conf_padrao[0], rodas_conf_padrao[2] #! usar

    return hub

class mudar_velocidade():
    """
    gerenciador de contexto (bloco with) para (automaticamente):
    1. mudar a velocidade do robô
    2. restaurar a velocidade do robô
    """
    def __init__(self, rodas, vel, vel_ang=None): 
        self.rodas = rodas
        self.vel   = vel
        self.vel_ang = vel_ang
 
    def __enter__(self): 
        self.conf_anterior = self.rodas.settings()
        [_, *conf_resto]   = self.conf_anterior
        if self.vel_ang:
            conf_resto[1] = self.vel_ang
        self.rodas.settings(self.vel, *conf_resto)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback): 
        self.rodas.settings(*self.conf_anterior)

def inverte_orientacao():
    global ori
    if ori == "N": ori = "S"
    if ori == "S": ori = "N"
    if ori == "L": ori = "O"
    if ori == "O": ori = "L"

def ler_ultrassons():
    return sensor_ultra_esq.distance(), sensor_ultra_dir.distance()

def dar_meia_volta():
    inverte_orientacao()
    rodas.turn(180)
    
def virar_direita():
    global ori
    if   ori == "N": ori = "L"
    elif ori == "S": ori = "O"
    elif ori == "L": ori = "S"
    elif ori == "O": ori = "N"
    rodas.turn(90)

def virar_esquerda():
    global ori
    if ori == "N": ori = "O"
    elif ori == "S": ori = "L"
    elif ori == "L": ori = "N"
    elif ori == "O": ori = "S"
    rodas.turn(-90)

DIST_PARAR=-0.4
def parar():
    rodas.straight(DIST_PARAR)
    rodas.stop()
ANG_PARAR=-0.0
def parar_girar():
    rodas.turn(ANG_PARAR)
    rodas.stop()

def dar_re(dist):
    rodas.straight(-dist)

def dar_re_meio_bloco(eixo_menor=False):
    if eixo_menor:
        dar_re(TAM_BLOCO_Y//2 - DIST_EIXO_SENSOR)
    else:
        dar_re(TAM_BLOCO//2   - DIST_EIXO_SENSOR)

#! provavelmente mudar andar_ate pra receber uma fn -> bool e retornar só bool, dist (pegar as informações extras na própria função)

def ver_nao_pista() -> tuple[bool, tuple[Color, hsv], tuple[Color, hsv]]: # type: ignore
    #! usar verificar_cor em vez disso?
    esq, dir = cores.todas(sensor_cor_esq, sensor_cor_dir)
    return ((not cores.pista_unificado(*esq) or not cores.pista_unificado(*dir)),
            esq, dir)

def ver_azul_lado():
    esq, dir = cores.todas(sensor_cor_esq, sensor_cor_dir)
    return ((cores.azul_unificado(*esq) ^ cores.azul_unificado(*dir)),
            esq, dir)

def verificar_cor(func_cor) -> Callable[None, tuple[bool, int]]: # type: ignore
    def f():
        esq, dir = cores.todas(sensor_cor_esq, sensor_cor_dir)
        return func_cor(*esq) or func_cor(*dir), esq, dir
    return f

def ver_passageiro_perto():
    print("ver_passageiro_perto")
    dist_esq, dist_dir = ler_ultrassons()
    return ((dist_esq < DIST_PASSAGEIRO_RUA or dist_dir < DIST_PASSAGEIRO_RUA),
            dist_esq, dist_dir)

def nao_ver_passageiro_perto():
    print("nao_ver_passageiro_perto")
    dist_esq, dist_dir = ler_ultrassons()
    return ((dist_esq < DIST_PASSAGEIRO_RUA and dist_dir < DIST_PASSAGEIRO_RUA),
            dist_esq, dist_dir)

def andar_ate_idx(*conds_parada: Callable, dist_max=PISTA_TODA) -> tuple[bool, tuple[Any]]: # type: ignore
    rodas.reset()
    rodas.straight(dist_max, wait=False)
    while not rodas.done():
        for i, cond_parada in enumerate(conds_parada):
            chegou, *retorno = cond_parada()
            if not chegou: continue
            else:
                parar()
                return i+1, retorno
    return 0, (rodas.distance(),)

_nunca      = lambda: False, (False,)
_manter_res = lambda res, ext: (res, ext)
def andar_ate_bool(sucesso, neutro=_nunca, fracasso=ver_nao_pista,
                           ou=_manter_res, dist_max=PISTA_TODA):
    sucessos  = [sucesso]  #sucesso  if type(sucesso)  == tuple else [sucesso]
    neutros   = [neutro]   #neutro   if type(neutro)   == tuple else [neutro] #! nome neutro não diz exatamente o que é
    fracassos = [fracasso] #fracasso if type(fracasso) == tuple else [fracasso]

    succ_min = 1; succ_max = succ_min + 1 # 1;            succ_max = succ_min + len(sucessos)  + 1 #! conta
    neut_min = 2; neut_max = neut_min + 1 # succ_max + 1; neut_max = neut_min + len(neutros)   + 1 #! conta
    frac_min = 3; frac_max = frac_min + 1 # neut_max + 1; frac_max = frac_min + len(fracassos) + 1 #! conta

    while True:
        res, extra = andar_ate_idx(sucesso, neutro, fracasso, # *sucessos, *neutros, *fracassos,
                                   dist_max=dist_max)
        if   res in range(succ_min, succ_max):
            return True, extra
        if   res in range(neut_min, neut_max):
            continue
        elif res in range(frac_min, frac_max):
            return False, extra
        elif res == 0:
            print("andar_ate_cor: andou demais")
            return ou(res, extra)
        else: 
            print(res)
            assert False

def alinha_limite(max_tentativas=3):
    for i in range(max_tentativas):
        rodas.reset()
        dar_re_meio_bloco()
        alinhou = alinha_parede(vel=80, vel_ang=30, giro_max=70)
        ang  = rodas.angle()
        dist = rodas.distance()
        if alinhou: return
        else:
            with mudar_velocidade(rodas, 80, 30):
                rodas.turn(-ang)
                dar_re(dist)
                rodas.turn(ang)
    return

def achar_limite() -> tuple[tuple[Color, hsv], tuple[Color, hsv]]: # type: ignore
    achou, extra = andar_ate_idx(ver_nao_pista)
    if achou:
        return extra
    else:
        return cores.todas(sensor_cor_esq, sensor_cor_dir)

def achar_azul() -> bool:
    esq, dir = achar_limite(); alinha_limite() # anda reto até achar o limite

    if cores.beco_unificado(*esq) or cores.beco_unificado(*dir): #! beco é menor que os outros blocos
        print(f"achar_azul: beco")

        dar_re_meio_bloco()
        dar_re(TAM_BLOCO_BECO) 

        choice((virar_direita, virar_esquerda))() # divertido

        #! deixar mais andar_ate(ver_azul, ver_nao_branco) switch()
        esq, dir = achar_limite(); alinha_limite() # anda reto até achar o limite
        print(f"achar_azul: beco indo azul") 

        if cores.parede_unificado(*esq) or cores.parede_unificado(*dir): dar_meia_volta()

        #! deixar mais andar_ate(ver_azul, ver_nao_branco) switch()
        esq, dir = achar_limite() # anda reto até achar o limite #! alinha?
        print(f"achar_azul: beco indo azul certeza")

        return cores.certificar(sensor_cor_esq, sensor_cor_dir, cores.azul_unificado)
    elif cores.parede_unificado(*esq) or cores.parede_unificado(*dir):
        print(f"achar_azul: parede")

        dar_re_meio_bloco()
        choice((virar_direita, virar_esquerda))() # divertido      

        return False
    else: #azul
        print("achar_azul: vi azul")
        #! deixar mais andar_ate(ver_azul, ver_nao_branco) switch()
        esq, dir = achar_limite() # anda reto até achar o limite #! alinha?

        if cores.certificar(sensor_cor_esq, sensor_cor_dir, cores.azul_unificado):
            print("achar_azul: azul mesmo")
            return True
        else:
            print("achar_azul: não azul")
            dar_re_meio_bloco()
            virar_direita()
            return False

def alinha_parede(vel, vel_ang, giro_max=45) -> bool:
    alinhado_parede = lambda esq, dir: not cores.pista_unificado(*esq) and not cores.pista_unificado(*dir)
    alinhado_pista  = lambda esq, dir: cores.pista_unificado(*esq) and cores.pista_unificado(*dir)

    with mudar_velocidade(rodas, vel, vel_ang):
        parou, extra = andar_ate_idx(ver_nao_pista, dist_max=TAM_BLOCO//2)
        if not parou:
            (dist,) = extra
            print("reto branco", dist)
            return False # viu só branco, não sabemos se tá alinhado
    
        (dir, esq) = extra
        if  alinhado_parede(esq, dir):
            print("reto não pista")
            return True
        elif not cores.pista_unificado(*dir):
            print("torto pra direita")
            GIRO = -giro_max
        elif not cores.pista_unificado(*esq):
            print("torto pra esquerda")
            GIRO = giro_max

        rodas.turn(GIRO, wait=False) #! fazer gira_ate
        while not rodas.done():
            esq, dir = cores.todas(sensor_cor_esq, sensor_cor_dir)
            print(esq, dir)
            if  alinhado_parede(esq, dir):
                print("alinhado parede")
                parar_girar()
                return True # deve tar alinhado
            elif alinhado_pista(esq, dir):
                print("alinhado pista")
                parar_girar()
                return False #provv alinhado, talvez tentar de novo
        return False # girou tudo, não sabemos se tá alinhado

def alinhar(max_tentativas=4, virar=True, vel=80, vel_ang=20, giro_max=70) -> None:
    for _ in range(max_tentativas): #! esqueci mas tem alguma coisa
        rodas.reset()
        alinhou = alinha_parede(vel, vel_ang, giro_max=giro_max)

        ang  = rodas.angle()
        dist = rodas.distance()
        with mudar_velocidade(rodas, vel, vel_ang):
            rodas.turn(-ang)
            dar_re(dist)
            rodas.turn(ang)

        if alinhou: return
        else:
            if virar: virar_direita() #! testar agora
            continue
    return
        

def pegar_passageiro() -> bool:
    global ori

    print("pegar_passageiro")
    while True:
        with mudar_velocidade(rodas, 50):
            res, info = andar_ate_idx(ver_passageiro_perto,
                                      verificar_cor(cores.beco_unificado),
                                      dist_max=TAM_BLOCO*4)
        if res == 1:
            (dist_esq, dist_dir) = info
            if dist_esq < dist_dir:
                dist = dist_esq
                virar, desvirar = virar_esquerda, virar_direita
            else:
                dist = dist_dir
                virar, desvirar = virar_direita, virar_esquerda

            blt.abrir_garra(hub)
            dar_re(DIST_EIXO_SENS_DIST-20) #! desmagificar
            virar()
            rodas.straight(dist)
            print("tentando fechar garra")
            blt.fechar_garra(hub)
            cor_cano = blt.ver_cor_passageiro(hub)
            print(f"{cor_cano=}/{cores.cor(cores.identificar(cor_cano))}")

            if cores.identificar(cor_cano) == cores.cor.BRANCO:
                blt.abrir_garra(hub)
                rodas.straight(-dist)
                desvirar()
                return False
            return True
        elif res == 2:
            (cor_esq, cor_dir) = info
            print(f"{cor_esq=}, {cor_dir=}")
            dar_re_meio_bloco()
            dar_meia_volta()

            return False # é pra ter chegado no vermelho
        else:
            dar_re_meio_bloco()
            dar_meia_volta()
            return False # chegou na distância máxima

def pegar_primeiro_passageiro() -> bool:
    global ori
    print("pegar_primeiro_passageiro")
    #! a cor é pra ser azul
    virar_direita()
    #dar_re_meio_bloco()
    deu, _ = andar_ate_bool(verificar_cor(cores.beco_unificado),
                           neutro=verificar_cor(cores.azul_unificado))
    while not deu:
        deu, _ = andar_ate_bool(verificar_cor(cores.beco_unificado),
                               neutro=verificar_cor(cores.azul_unificado))

    dar_meia_volta() #!verificar
    pegou = pegar_passageiro()
    while not pegou:
        pegou = pegar_passageiro()
    
    return True

def seguir_caminho(pos, obj, ori): #! lidar com outras coisas
    def interpretar_movimento(mov):
        if   mov == tipo_movimento.FRENTE:
            rodas.straight(TAM_BLOCO)
        elif mov == tipo_movimento.TRAS:
            dar_meia_volta()
            rodas.straight(TAM_BLOCO)
        elif mov == tipo_movimento.ESQUERDA_FRENTE:
            virar_esquerda()
            rodas.straight(TAM_BLOCO)
        elif mov == tipo_movimento.DIREITA_FRENTE:
            virar_direita()
            rodas.straight(TAM_BLOCO)
        elif mov == tipo_movimento.ESQUERDA:
            virar_esquerda()
        elif mov == tipo_movimento.DIREITA:
            virar_direita()

    def interpretar_caminho(caminho): #! receber orientação?
        for mov in caminho: #! yield orientação nova?
            print(tipo_movimento(mov))
            interpretar_movimento(mov)
            yield rodas.distance()

    movs, ori_final = achar_movimentos(pos, obj, ori)
    #print(*(tipo_movimento(mov) for mov in movs))
    for _ in interpretar_caminho(movs):
        while not rodas.done():
            pass
        
    while ori != ori_final:
        virar_direita()

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
            [wait(100) for _ in gui.mostrar_palavra(hub, "CAL..")]
            mapa_hsv[selecao] = (
                cores.coletar_valores(hub, botao_aceitar, dir=sensor_dir, esq=sensor_esq)
            )
            wait(150)
        elif botao_parar   in botões:
            wait(100)
            return mapa_hsv


def main(hub):
    global ori

    crono = StopWatch()
    while crono.time() < 100: #! ativar calibração quando for usar
        botões = hub.buttons.pressed()
        if botao_calibrar in botões:
            bipe_calibracao(hub)
            #! levar os dois sensores em consideração separadamente
            mapa_hsv = menu_calibracao(hub, sensor_cor_esq, sensor_cor_dir)
            cores.repl_calibracao(mapa_hsv)#, lado="esq")
            return

    hub.system.set_stop_button((Button.BLUETOOTH,))
    bipe_cabeca(hub)

    #! antes de qualquer coisa, era bom ver se na sua frente tem obstáculo
    #! sobre isso ^ ainda, tem que tomar cuidado pra não confundir eles com os passageiros
    achou_azul = False
    alinhar()
    while not achou_azul:
        achou_azul = achar_azul()
    ori = "L"
    #achar_limite(); alinha_limite()
    pegou = pegar_primeiro_passageiro()
    if pegou:
        #! deixar mais andar_ate(ver_azul, ver_nao_branco) switch()
        achar_limite(); alinha_limite()
        cor = blt.ver_cor_passageiro()
        if cor == Color.GREEN:
            fim = (2,4)
        if cor == Color.RED:
            fim = (2,2)
        if cor == Color.BLUE:
            fim = (0,4)
        else:
            pass #!

        if ori == "N": pos = (0,5)
        if ori == "S": pos = (4,5)

        seguir_caminho(pos, fim, ori)
        rodas.straight(TAM_BLOCO//2)
        blt.abrir_garra(hub)
        rodas.straight(-TAM_BLOCO//2)
        main(hub) #!
        musica_vitoria(hub)
    else:
        musica_derrota(hub)
        wait(1000)
        return #! fazer main retornar que nem em c e tocar o som com base nisso
