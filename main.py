from polyfill import Enum

ID = Enum("ID", ["BRACO", "CABECA", "TESTE"])
id = ID.CABECA

if id == ID.CABECA:
    import cabeca
    hub = cabeca.setup()
    
    hub.speaker.beep(frequency=500, duration=100)
    cabeca.main(hub)
    hub.speaker.beep(frequency=250, duration=250)
elif id == ID.BRACO:
    import braco
    hub = braco.setup()

    hub.speaker.beep(frequency=500, duration=100)
    braco.main(hub)
    hub.speaker.beep(frequency=250, duration=250)

elif id == ID.TESTE:
    from pybricks.hubs import PrimeHub
    from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor

    from pybricks.parameters import Port, Axis, Stop, Direction, Button, Color
    from pybricks.tools      import wait, StopWatch
    from pybricks.robotics   import DriveBase
    
    hub = PrimeHub()
    
    hub.speaker.beep(frequency=500, duration=100)
    ...
    hub.speaker.beep(frequency=250, duration=200)
else:
    assert False

