from os import system

python = ".venv/bin/python3"

def run_command(command):
    return system(command)

def main():
    run_command('cat build/pre_cabeca.py main.py > __main_cabeca.py')
    
    run_command(f'{python} -m pybricksdev run ble --name "spike1" __main_cabeca.py')
    
    run_command('rm __main_cabeca.py')

if __name__ == "__main__":
    main()
