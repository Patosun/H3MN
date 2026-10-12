"""
Utilidades compartidas: leer una función f(x) escrita por el usuario y los
nodos de interpolación.

Ejemplos de funciones válidas:
    sin(x)/x      exp(-x^2)      1/(1+25*x^2)      x^3 - 2*x + 1      log(x)
"""

import math

# Nombres permitidos dentro de la expresión
PERMITIDOS = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
PERMITIDOS.update({"abs": abs, "ln": math.log})


def crear_funcion(texto):

    expresion = texto.strip().replace("^", "**")
    codigo = compile(expresion, "<f(x)>", "eval")
    for nombre in codigo.co_names:
        if nombre != "x" and nombre not in PERMITIDOS:
            raise ValueError(f"Nombre no permitido en la función: {nombre}")

    def f(x):
        return eval(codigo, {"__builtins__": {}}, {**PERMITIDOS, "x": x})

    return f


def leer_funcion(mensaje="f(x) = "):

    while True:
        texto = input(mensaje)
        try:
            f = crear_funcion(texto)
            return f, texto.strip()
        except (SyntaxError, ValueError) as e:
            print(f"Función no válida ({e}). Ejemplo: exp(-x^2) o sin(x)/x")


def leer_lista(mensaje):

    return [float(v) for v in input(mensaje).replace(",", " ").split()]


def leer_nodos():

    print("Nodos de interpolación:")
    print("  1) Equiespaciados en [a, b] con n intervalos (n + 1 puntos)")
    print("  2) Escribir los valores x0 x1 ... xn")
    if input("Opción: ").strip() == "2":
        return leer_lista("x0 x1 ... xn: ")
    a = float(input("a = "))
    b = float(input("b = "))
    n = int(input("n = "))
    return [a + i * (b - a) / n for i in range(n + 1)]


def evaluar_en_nodos(f, x):

    valores = []
    for xi in x:
        try:
            valores.append(float(f(xi)))
        except (ValueError, ZeroDivisionError, OverflowError) as e:
            raise ValueError(f"f no se puede evaluar en x = {xi:g} ({e})")
    return valores


def leer_csv(ruta):

    # Formato esperado (como x_f.csv):
    #   x,f
    #   0,1
    #   1,2.5
    # Acepta separador "," o ";" y omite encabezado y líneas vacías.
    import csv

    x, f = [], []
    with open(ruta, newline="", encoding="utf-8-sig") as archivo:
        contenido = archivo.read()
    separador = ";" if contenido.count(";") > contenido.count(",") else ","
    for numero, fila in enumerate(csv.reader(contenido.splitlines(), delimiter=separador), start=1):
        fila = [c.strip() for c in fila if c.strip()]
        if not fila:
            continue
        try:
            xi, fi = float(fila[0]), float(fila[1])
        except (ValueError, IndexError):
            if numero == 1:
                continue        # encabezado
            raise ValueError(f"{ruta}, línea {numero}: fila no válida {fila}")
        x.append(xi)
        f.append(fi)

    if len(set(x)) != len(x):
        raise ValueError(f"{ruta}: hay valores de x repetidos")
    # Ordena por x (los splines requieren x_i < x_(i+1))
    pares = sorted(zip(x, f))
    return [p[0] for p in pares], [p[1] for p in pares]


def pedir_csv(argumentos):

    # Usa la ruta pasada por línea de comandos o la pide por teclado
    ruta = argumentos[1] if len(argumentos) > 1 else input("Ruta del archivo .csv: ").strip().strip("'\"")
    return ruta, leer_csv(ruta)
