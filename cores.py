from pybricks.tools      import wait
from pybricks.parameters import Color

from umath import sqrt
from polyfill import Enum, rgb_to_hsv, hsv_to_rgb

from _cores_calibradas import mapa_rgb, mapa_hsv

cor = Enum("cor", ["AMARELO",
                   "VERDE",
                   "AZUL",
                   "VERMELHO",
                   "MARROM",
                   "PRETO",
                   "BRANCO"])

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
    if type(hsv) == Color:
        h, s, v = hsv.h, hsv.s, hsv.v
    else: #if type(hsv) == tuple:
        h, s, v = hsv
    return (h/360, s/100, v/100)


def calibrar(hub, sensor, botao_parar) -> tuple[rgb, hsv, hsv]:
    wait(200)

    minm, maxm = (1, 1, 1), (0, 0, 0)
    soma, cont = (0, 0, 0), 0
    while botao_parar not in hub.buttons.pressed():
        hsv = sensor.hsv()
        hsv = hsv.h, hsv.s, hsv.v

        rgb_norm = hsv_to_rgb(norm_hsv(hsv))

        minm = tuple(map(min, minm, hsv))
        maxm = tuple(map(max, maxm, hsv))

        soma = tuple(map(lambda c,s: c+s, rgb_norm, soma))
        cont += 1

        cor_txt_rgb = tuple(map("{:.2f}".format, rgb_norm))
        cor_txt_hsv = tuple(map("{:.2f}".format, hsv))
        print(cor_txt_hsv, cor_txt_rgb, "max:", maxm, "min:", minm)

    med = tuple(map(lambda s: s/cont, soma))
    return (med, minm, maxm)

def identificar_cor_hsv(hsv) -> cor:
    h, s, v = hsv
    for i, (m, M) in mapa_hsv:
        hm, _, _ = m
        hM, _, _ = M

        if h in range(hm, hM): return i

def dist(cor1, cor2) -> float:
    #! tem que ver se faz sentido usar com hsv também, mas a conta funciona
    r1, g1, b1 = cor1
    r2, g2, b2 = cor2
    return sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)

def identificar_cor_dist(rgb) -> cor:
    #! teria como usar com hsv também, mas usa o outro mapa
    min_dist, min_idx = 1, -1
    for i, cor_canonica in enumerate(mapa_rgb):
        d = dist(rgb, cor_canonica)
        if d < min_dist:
            min_dist, min_idx = d, i

    return min_idx

def identificar(rgb=None, hsv=None) -> cor:
    if   rgb is not None:
        hsv = rgb_to_hsv(rgb)
    elif hsv is not None:
        rgb = hsv_to_rgb(norm_hsv(hsv))
    else:
        raise ValueError("esperada cor de entrada")

    return identificar_cor_hsv(hsv) #ou identificar_cor_dist(rgb)

def salvar_cores():
    global mapa_rgb, mapa_hsv
    
    print(f"mapa_rgb = [")
    for c in range(len(cor)):
        print(f"\t{mapa_rgb[c]}, #{cor(c)}")
    print("]")
    
    print(f"mapa_hsv = [")
    for c in range(len(cor)):
        print(f"\t{mapa_hsv[c]}, #{cor(c)}")
    print("]")
