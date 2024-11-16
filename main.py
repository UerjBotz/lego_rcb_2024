from lib.bipes import bipe_inicio, bipe_final, bipe_falha

ID = None     if False else ID # pyright: ignore
id = ID.TESTE if False else id # pyright: ignore

if id == ID.CABECA:
    import cabeca
    hub = cabeca.setup()
    print(hub.battery.voltage())

    bipe_inicio(hub)
    cabeca.main()
    bipe_final(hub)
elif id == ID.BRACO:
    import braco
    hub = braco.setup()
    print(hub.battery.voltage())

    while True:
        try:
            bipe_inicio(hub)
            braco.main()
            bipe_final(hub)
        except Exception as e:
            bipe_falha(hub)
            print(f"braco: {e}")
            continue

elif id == ID.TESTE:
    from pybricks.hubs import PrimeHub

    from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor

    from pybricks.parameters import Port, Axis, Stop, Direction, Button, Color
    from pybricks.tools      import wait, StopWatch
    from pybricks.robotics   import DriveBase

    import cores
    import cabeca
    from lib.bipes import *

    hub = cabeca.setup()
    print(hub.battery.voltage())

    bipe_inicio(hub)
    while True:
        if Button.CENTER in hub.buttons.pressed():
            bipe_calibracao(hub)
            #! levar os dois sensores em consideração separadamente
            mapa_hsv = cabeca.menu_calibracao(hub, cabeca.sensor_cor_esq, cabeca.sensor_cor_dir)
            cores.repl_calibracao(mapa_hsv)#, lado="esq")
            while Button.RIGHT not in hub.buttons.pressed():
                pass
        if Button.BLUETOOTH in hub.buttons.pressed():
            break
        hsv_esq = cabeca.sensor_cor_esq.hsv()
        hsv_dir = cabeca.sensor_cor_dir.hsv()
        color_esq = cabeca.sensor_cor_esq.color()
        color_dir = cabeca.sensor_cor_dir.color()
        classif_cor = dict(
            deles_esq = color_esq,
            deles_dir = color_dir,
            nosso_esq = cores.cor(cores.identificar(hsv_esq)),
            nosso_dir = cores.cor(cores.identificar(hsv_dir)),
        )
        classif_categ = dict(
            pista=(
                cores.pista_unificado(color_esq, hsv_esq),
                cores.pista_unificado(color_dir, hsv_dir)
            ),
            lombada=(
                cores.lombada_unificado(color_esq, hsv_esq),
                cores.lombada_unificado(color_dir, hsv_dir)
            ),
            beco=(
                cores.beco_unificado(color_esq, hsv_esq),
                cores.beco_unificado(color_dir, hsv_dir)
            ),
            parede=(
                cores.parede_unificado(color_esq, hsv_esq),
                cores.parede_unificado(color_dir, hsv_dir)
            )
        )
        print(classif_cor, classif_categ, '\n', sep='\n')
        wait(200)

    bipe_final(hub)
else:
    assert False

