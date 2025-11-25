import random

numero_utilizados = set()

def generar_numeros_cuenta() ->str:
    while True:
        num = str(random.randint(1000000000, 9999999999))
        if num not in numero_utilizados:
            numero_utilizados.add(num)
            return num