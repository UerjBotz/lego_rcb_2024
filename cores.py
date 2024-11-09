from pybricks.tools      import wait
from pybricks.parameters import Color

from polyfill import Enum, rgb_to_hsv, hsv_to_rgb

from _cores_calibradas import mapa_hsv

cor = Enum("cor", ["AMARELO",
                   "VERDE",
                   "AZUL",
                   "VERMELHO",
                   "MARROM",
                   "PRETO",
                   "BRANCO",
                   "NENHUMA"])

Color2cor = {
    Color.YELLOW: cor.AMARELO,
    Color.GREEN:  cor.VERDE, 
    Color.BLUE:   cor.AZUL,
    Color.RED:    cor.VERMELHO,
    Color.BROWN:  cor.MARROM,
    Color.BLACK:  cor.PRETO,
    Color.WHITE:  cor.BRANCO,
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

def norm_hsv(hsv):
    if type(hsv) != tuple:
        h, s, v = hsv.h, hsv.s, hsv.v
    else:
        h, s, v = hsv
    return (h/360, s/100, v/100)

def unnorm_hsv(hsv):
    h, s, v = hsv
    return (h*360, s*100, v*100)

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


def coletar_valores(hub, botao_parar, esq=None, dir=None) -> tuple[hsv, hsv, hsv]:
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

def identificar_por_intervalo_hsv(hsv) -> cor:
    h, s, v = hsv
    for i, (m, mm, M) in enumerate(mapa_hsv):
        hm, _, _ = m
        hM, _, _ = M

        if h in range(hm, hM): return i
    return cor.NENHUMA

def identificar(color) -> cor:
    hsv = color.h, color.s, color.v
    return identificar_por_intervalo_hsv(hsv)

def repl_calibracao(mapa_hsv, lado=""):
    print(f"mapa_hsv{lado} = [")
    for c in range(len(cor)-1): # -1 pula cor NENHUMA
        print(f"\t{mapa_hsv[c]}, #{cor(c)}")
    print("]")
