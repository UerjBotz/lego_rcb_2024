from os import system

python = ".venv/bin/python3"

def run_command(command):
    return system(command)

def main():
    # Passo 1: Concatenar os arquivos com o comando 'cat'
    run_command('cat .vscode/pre_cabeca.py main.py > __main_cabeca.py')
    run_command('cat .vscode/pre_braco.py main.py > __main_braco.py')
    
    # Passo 2: Rodar os scripts no dispositivo SPIKE com 'pybricksdev run ble'
    run_command(f'{python} -m pybricksdev run ble --name "spike0" __main_braco.py --no-wait &')
    run_command(f'{python} -m pybricksdev run ble --name "spike1" __main_cabeca.py --no-wait')
    
    # Passo 3: Remover os arquivos temporários com 'rm'
    run_command('rm __main_cabeca.py')
    run_command('rm __main_braco.py')

if __name__ == "__main__":
    main()
