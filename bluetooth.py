from lib.polyfill import Enum

TX_CABECA = 24
TX_BRACO  = 69

comando_bt = Enum("comando_bt", ["fecha_garra",
                                 "abre_garra",
                                 "ver_cor_passageiro",
                                 "ver_hsv_passageiro",
                                 "ver_distancias",
                                 #! fazer um enum comandos e outro respostas
                                 "fechei",
                                 "abri",
                                 "cor_passageiro",
                                 "hsv_passageiro",
                                 "distancias"])

def esperar_resposta(hub, esperado, canal=TX_BRACO):
    comando = -1
    while comando != esperado:
        comando = hub.ble.observe(canal)
        if comando is not None:
            comando, *args = comando
    return args

def fechar_garra(hub):
    print("fechar_garra:")
    hub.ble.broadcast((comando_bt.fecha_garra,))
    return esperar_resposta(hub, comando_bt.fechei)

def abrir_garra(hub):
    print("abrir_garra:")
    hub.ble.broadcast((comando_bt.abre_garra,))
    return esperar_resposta(hub, comando_bt.abri)

def ver_cor_passageiro(hub):
    print("ver_cor_passageiro:")
    hub.ble.broadcast((comando_bt.ver_cor_passageiro,))
    return esperar_resposta(hub, comando_bt.cor_passageiro)[0]

def ver_hsv_passageiro(hub):
    print("ver_hsv_passageiro:")
    hub.ble.broadcast((comando_bt.ver_hsv_passageiro,))
    return esperar_resposta(hub, comando_bt.hsv_passageiro)

def ver_distancias(hub):
    print("ver_distancias:")
    hub.ble.broadcast((comando_bt.ver_distancias,))
    return esperar_resposta(hub, comando_bt.distancias)
