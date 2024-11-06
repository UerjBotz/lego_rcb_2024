from pybricks.tools import StopWatch, wait
from pybricks.parameters import Color

_ = 0
I = 100

letras = {
    "A": [
        [ _, I, I, _, ], 
        [ I, _, _, I, ], 
        [ I, I, I, I, ], 
        [ I, _, _, I, ], 
        [ I, _, _, I, ],
    ],
    "M": [
        [ I, _, _, _, I, ],
        [ I, I, _, I, I, ],
        [ I, _, I, _, I, ],
        [ I, _, _, _, I, ],
        [ I, _, _, _, I, ],
    ],
    "V": [
        [ I, _, _, _, I, ],
        [ I, _, _, _, I, ],
        [ I, _, _, _, I, ],
        [ _, I, _, I, _, ],
        [ _, _, I, _, _, ],
    ],
    "Z": [
        [ I, I, I, I, ],
        [ _, _, _, I, ],
        [ _, _, I, _, ],
        [ _, I, _, _, ],
        [ I, I, I, I, ],
    ],
    "D": [
        [ I, I, I, _, ],
        [ I, _, _, I, ],
        [ I, _, _, I, ],
        [ I, _, _, I, ],
        [ I, I, I, _, ],
    ],
    "P": [
        [ I, I, I, _, ],
        [ I, _, _, I, ],
        [ I, I, I, _, ],
        [ I, _, _, _, ],
        [ I, _, _, _, ],
    ],
    "B": [
        [ I, I, I, _, ],
        [ I, _, _, I, ],
        [ I, I, I, _, ],
        [ I, _, _, I, ],
        [ I, I, I, _, ],
    ],
    "R": [
        [ I, I, I, _, ],
        [ I, _, _, I, ],
        [ I, I, I, _, ],
        [ I, _, _, I, ],
        [ I, _, _, I, ],
    ],
    "C": [
        [ _, I, I, ],
        [ I, _, _, ],
        [ I, _, _, ],
        [ I, _, _, ],
        [ _, I, I, ],
    ],
    "L": [
        [ I, _, _, ],
        [ I, _, _, ],
        [ I, _, _, ],
        [ I, _, _, ],
        [ I, I, I, ],
    ],
    ".": [
        [ _, _, ],
        [ _, _, ],
        [ _, _, ],
        [ _, _, ],
        [ _, _, ],
    ],
    "nul": [
        [ _, _, ],
        [ _, _, ],
        [ _, _, ],
        [ _, _, ],
        [ _, _, ],
    ],
}

palavras = dict(
    AMARELO="AM",
    VERDE="VD",
    AZUL="AZ",
    VERMELHO="VM",
    MARROM="MR",
    PRETO="PR",
    BRANCO="BR",
)
cor2Color = [
    Color.YELLOW,
    Color.GREEN,
    Color.BLUE,
    Color.RED,
    Color.BROWN,
    Color.BLACK,
    Color.WHITE,
]

QTD_LINHAS = 5
def concatena_letras(*letras):
    ret = [[] for _ in range(QTD_LINHAS)]
    for i in range(QTD_LINHAS):
        for l in letras:
            ret[i] += l[i] + [_]
    return ret
        
def passo_anim(palavra, i):
    return [r[i:i+5] for r in palavra]

def mostrar_palavra(hub, nome):
    mat = concatena_letras(*(letras.get(letra) or letras["nul"]
                             for letra in palavras.get(nome) or nome))
    for i in range(len(mat[0])):        
        m = passo_anim(mat, i)
        if len(m[0]) < QTD_LINHAS:
            m = [l + [_]*(QTD_LINHAS - len(l)) for l in m]

        yield hub.display.icon(m)

def tela_escolher_cor(hub, enum_cor, selecao, intervalo_anim=110, intervalo_botao=100):
    cor = enum_cor(selecao)
    sw = StopWatch()
    
    for _ in mostrar_palavra(hub, cor):
        sw.reset()
        hub.light.on(cor2Color[selecao])
        while sw.time() < intervalo_anim:
            wait(intervalo_botao)
            botoes = hub.buttons.pressed()
            if botoes: return botoes
    
    return {}