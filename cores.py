from pybricks.tools      import wait
from pybricks.parameters import Color

from lib.polyfill import Enum, rgb_to_hsv, hsv_to_rgb

from lib.cores_calibradas_ import mapa_hsv

cor = Enum("cor", ["AMARELO",
                   "VERDE",
                   "AZUL",
                   "VERMELHO",
                   "MARROM",
                   "PRETO",
                   "BRANCO",
                   "NENHUMA"])

def Color2tuple(color):
    return color.h, color.s, color.v

Color2cor = {
    Color2tuple(Color.YELLOW): cor.AMARELO,
    Color2tuple(Color.GREEN ): cor.VERDE, 
    Color2tuple(Color.BLUE  ): cor.AZUL,
    Color2tuple(Color.RED   ): cor.VERMELHO,
    Color2tuple(Color.BROWN ): cor.MARROM,
    Color2tuple(Color.BLACK ): cor.PRETO,
    Color2tuple(Color.WHITE ): cor.BRANCO,
}

cor2Color = [
    Color.YELLOW,
    Color.GREEN,
    Color.BLUE,
    Color.RED,
    Color.BROWN,
    Color.BLACK,
    Color.WHITE,
]

#hsv = tuple[float, float, float]

def norm_hsv(hsv):
    if type(hsv) != tuple:
        h, s, v = hsv.h, hsv.s, hsv.v
    else:
        h, s, v = hsv
    return (h/360, s/100, v/100)

def unnorm_hsv(hsv):
    h, s, v = hsv
    return (h*360, s*100, v*100)

def todas(sensor_esq, sensor_dir) -> tuple[tuple, tuple]:
    esq = sensor_esq.color(), sensor_esq.hsv()
    dir = sensor_dir.color(), sensor_dir.hsv()
    return (esq, dir)

def iter_coleta(hub, botao_parar, sensor):
    minm, maxm = (360, 100, 100), (0, 0, 0)
    soma, cont = (000, 000, 000), 0
    while botao_parar not in hub.buttons.pressed():
        hsv = sensor.hsv()
        hsv = hsv.h, hsv.s, hsv.v

        rgb_norm = hsv_to_rgb(norm_hsv(hsv))

        minm = tuple(map(min, minm, hsv))
        maxm = tuple(map(max, maxm, hsv))

        soma = tuple(map(lambda c,s: c+s, hsv, soma))
        cont += 1

        if 1:
            cor_txt_rgb = tuple(map("{:.2f}".format, rgb_norm))
            cor_txt_hsv = tuple(map("{:.2f}".format, hsv))
            print(cor_txt_hsv, cor_txt_rgb)

        yield (minm, soma, cont, maxm)


def coletar_valores(hub, botao_parar, esq=None, dir=None) -> tuple[hsv, hsv, hsv]: # type: ignore
    wait(200)
    if esq and dir:
        for info_esq, info_dir in zip(iter_coleta(hub, botao_parar, esq),
                                      iter_coleta(hub, botao_parar, dir)):
            minme, somae, conte, maxme = info_esq
            minmd, somad, contd, maxmd = info_dir

            minm = tuple(map(min, minme, minmd))
            soma = tuple(map(lambda c,s: c+s, somad, somae))
            cont = conte + contd
            maxm = tuple(map(max, maxme, maxmd))
            #! fiz assim provisoriamente, acho que devia ser separado por lado mesmo
    else:
        sensor = esq if esq else dir
        for info in iter_coleta(hub, botao_parar, sensor):
            minm, soma, cont, maxm = info

    med = tuple(map(lambda s: s/cont, soma))
    print("max:", maxm, "med:", med, "min:", minm)

    return (minm, tuple(map(round, med)), maxm)

def identificar_por_intervalo_hsv(hsv) -> cor: # type: ignore
    h, s, v = hsv
    
    if   v <= 20: #! usar valores do arquivo
        return cor.PRETO
    elif s <= 10 and v >= 90:
        return cor.BRANCO

    for i, (m, mm, M) in enumerate(mapa_hsv):
        hm, _, _ = m
        hM, _, _ = M

        if h in range(hm, hM): return i
    return cor.NENHUMA

def identificar(color) -> cor: # type: ignore
    try:
        return identificar_por_intervalo_hsv(color)
    except TypeError:
        hsv = color.h, color.s, color.v
        return identificar_por_intervalo_hsv(hsv)

def pista_unificado(color, hsv):
    deles = (color == Color.WHITE)
    return deles

def parede_unificado(color, hsv):
    deles = ((color == Color.BLACK) or
             (color == Color.NONE ) or
             (color == Color.YELLOW))

    combinado = (((color == Color.RED) or
                  (color == Color.BLUE)) and
                 ((identificar(hsv) == cor.PRETO) or
                  (identificar(hsv) == cor.BRANCO) or
                  (identificar(hsv) == cor.NENHUMA)))

    return deles or combinado

def beco_unificado(color, hsv):
    deles = (color == Color.RED)
    return deles

def lombada_unificado(color, hsv):
    combinado = ((color == Color.WHITE) and
                 (identificar(hsv) != cor.AZUL)) #! talvez == BRANCO, pq é isso
    return combinado

def azul_unificado(color, hsv):
    deles = ((color == Color.BLUE))
    return deles

def certificar(sensor_dir, sensor_esq, uni, uni2=None) -> bool:
    if uni2 is None:
        uni2 = uni
    esq, dir = todas(sensor_esq, sensor_dir)

    res = uni(*esq) and uni2(*dir)
    print(f"certificar_cor: {res=}")

    return res


def repl_calibracao(mapa_hsv, lado=""):
    print(f"mapa_hsv{lado} = [")
    for c in range(len(cor)-1): # -1 pula cor NENHUMA
        print(f"\t{mapa_hsv[c]}, #{cor(c)}")
    print("]")
