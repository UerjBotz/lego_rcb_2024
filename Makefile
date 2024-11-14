all: cabeca_imediato braco_imediato


cabeca: __main_cabeca.py
	.venv/bin/python3 -m pybricksdev run ble --name "spike1" __main_cabeca.py
	rm __main_cabeca.py
braco: __main_braco.py
	.venv/bin/python3 -m pybricksdev run ble --name "spike0" __main_braco.py
	rm __main_braco.py


cabeca_imediato: __main_cabeca.py
	.venv/bin/python3 -m pybricksdev run ble --name "spike1" __main_cabeca.py --no-wait
	rm __main_cabeca.py
braco_imediato: __main_braco.py
	.venv/bin/python3 -m pybricksdev run ble --name "spike0" __main_braco.py --no-wait
	rm __main_braco.py


__main_cabeca.py:
	cat build/pre_cabeca.py main.py > __main_cabeca.py

__main_braco.py:
	cat build/pre_braco.py main.py > __main_braco.py

