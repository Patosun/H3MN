"""
Práctica H3 - Ejercicio 2
Interpolación de Newton por diferencias divididas.

Entrada : n + 1 puntos (x0, f0), (x1, f1), ..., (xn, fn)
Salida  : coeficientes c0, c1, ..., cn del polinomio
          P(x) = c0 + c1(x - x0) + c2(x - x0)(x - x1) + ... + cn(x - x0)...(x - x_{n-1})
"""


from funciones import leer_funcion, leer_lista, leer_nodos, evaluar_en_nodos, pedir_csv
from graficas import graficar_interpolacion, argumentos


# Ejemplo de la pizarra (14/9)
EJEMPLO_CLASE = {"x": [-1, 2, 2.5], "f": [3, 2.1, 3], "evaluar": [0, 1]}


def tabla_diferencias_divididas(x, f):

    n = len(x)
    # tabla[k][i] = f[x_i, x_{i+1}, ..., x_{i+k}]  (columna "kD" de la pizarra)
    tabla = [list(f)]
    for k in range(1, n):
        columna = []
        for i in range(n - k):
            columna.append((tabla[k - 1][i + 1] - tabla[k - 1][i]) / (x[i + k] - x[i]))
        tabla.append(columna)
    coef = [tabla[k][0] for k in range(n)]
    return tabla, coef


def evaluar_newton(coef, x, t):

    # Esquema de Horner anidado: c0 + (t - x0)(c1 + (t - x1)(c2 + ...))
    p = coef[-1]
    for k in range(len(coef) - 2, -1, -1):
        p = coef[k] + (t - x[k]) * p
    return p


def polinomio_texto(coef, x):

    partes = [f"{coef[0]:.6g}"]
    for k in range(1, len(coef)):
        factores = "".join("x" if x[j] == 0 else f"(x - {x[j]:g})" if x[j] > 0 else f"(x + {-x[j]:g})"
                           for j in range(k))
        signo = "-" if coef[k] < 0 else "+"
        partes.append(f" {signo} {abs(coef[k]):.6g}{factores}")
    return "P(x) = " + "".join(partes)


def imprimir_tabla(x, tabla):

    n = len(x)
    encabezado = f"{'x':>10} | {'f(x)':>12}" + "".join(f" | {str(k) + 'D':>12}" for k in range(1, n))
    print(encabezado)
    print("-" * len(encabezado))
    for i in range(n):
        fila = f"{x[i]:>10.6g}"
        for k in range(n - i):
            fila += f" | {tabla[k][i]:>12.6g}"
        print(fila)


def resolver(nombre, x, f, evaluar, funcion=None):

    if len(x) == 0 or len(x) != len(f):
        print(f"\n{nombre}: x y f deben tener la misma cantidad de valores.")
        return
    if len(set(x)) != len(x):
        print(f"\n{nombre}: los valores de x deben ser distintos.")
        return

    tabla, coef = tabla_diferencias_divididas(x, f)

    print(f"\n===== {nombre} =====")
    print("Tabla de diferencias divididas:")
    imprimir_tabla(x, tabla)
    print("\nCoeficientes: " + ", ".join(f"c{k} = {c:.6g}" for k, c in enumerate(coef)))
    print(polinomio_texto(coef, x))

    if evaluar and funcion is None:
        for t in evaluar:
            print(f"P({t:g}) = {evaluar_newton(coef, x, t):.6f}")
    elif evaluar:
        print(f"\n{'x':>10} | {'P(x)':>14} | {'f(x) real':>14} | {'error':>10}")
        for t in evaluar:
            p = evaluar_newton(coef, x, t)
            real = funcion(t)
            print(f"{t:>10.6g} | {p:>14.8f} | {real:>14.8f} | {abs(p - real):>10.3e}")

    graficar_interpolacion(f"Diferencias divididas - {nombre}", x, f,
                           [(f"Newton P_{len(x) - 1}(x)", lambda t: evaluar_newton(coef, x, t))],
                           evaluar, funcion)


def desde_csv():

    try:
        ruta, (x, f) = pedir_csv(argumentos())
    except (OSError, ValueError) as e:
        print(f"No se pudo leer el archivo: {e}")
        return
    print(f"Leídos {len(x)} puntos de {ruta}")
    evaluar = leer_lista("Puntos a evaluar (opcional, Enter para omitir): ")
    resolver(ruta, x, f, evaluar)


def main():
    print("Diferencias divididas de Newton")
    if len(argumentos()) > 1:
        # Uso directo: python3 programa.py datos.csv
        desde_csv()
        return

    print("0) Leer datos de un archivo .csv (columnas x, f)")
    print("1) Interpolar una función f(x) cualquiera")
    print("2) Ingresar una tabla de datos (x, f)")
    print("3) Ejemplo de clase")
    opcion = input("Opción: ").strip()

    if opcion == "0":
        desde_csv()
    elif opcion == "1":
        funcion, texto = leer_funcion()
        x = leer_nodos()
        try:
            f = evaluar_en_nodos(funcion, x)
        except ValueError as e:
            print(e)
            return
        evaluar = leer_lista("Puntos donde estimar f(x): ")
        resolver(f"f(x) = {texto}", x, f, evaluar, funcion)
    elif opcion == "2":
        x = leer_lista("Valores x0 x1 ... xn: ")
        f = leer_lista("Valores f0 f1 ... fn: ")
        evaluar = leer_lista("Puntos a evaluar (opcional): ")
        resolver("Datos ingresados", x, f, evaluar)
    else:
        resolver("Ejemplo de clase (14/9)", **EJEMPLO_CLASE)


if __name__ == "__main__":
    main()
