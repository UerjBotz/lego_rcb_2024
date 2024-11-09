from pybricks.parameters import Port, Stop
from pybricks.tools      import wait

def fecha_garra(motor_garra, vel=240):
    motor_garra.run_until_stalled(vel, then=Stop.COAST, duty_limit=None)
    motor_garra.run_angle(vel, 30, then=Stop.COAST, wait=False)

def abre_garra(motor_garra, vel=240, ang_volta=42):
    motor_garra.run_angle(vel, -ang_volta, then=Stop.COAST, wait=True)
