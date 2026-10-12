"""
Práctica H3 - Ejercicio 5
Trapecio y Simpson 1/3 para las integrales del PDF "Integración numérica",
con x y n variables.

  1. erf(x)  = 2/√π ∫_0^x e^(-t^2) dt
  2. C(x)    = ∫_0^x cos(πt²/2) dt        S(x) = ∫_0^x sin(πt²/2) dt
  3. Si(x)   = ∫_0^x sin(t)/t dt
  4. Li(x)   = ∫_2^x dt / ln(t)
"""

import math

from funciones import leer_funcion
from graficas import graficar_integracion


def trapecio(f, a, b, n):

    h = (b - a) / n
    suma = 0.0
    for i in range(1, n):
        suma += f(a + i * h)
    return (h / 2) * (f(a) + f(b) + 2 * suma)


def simpson_13(f, a, b, n):

    h = (b - a) / n
    suma_impares = 0.0
    suma_pares = 0.0
    for i in range(1, n):
        if i % 2 == 1:
            suma_impares += f(a + i * h)
        else:
            suma_pares += f(a + i * h)
    return (h / 3) * (f(a) + f(b) + 4 * suma_impares + 2 * suma_pares)


# ---------- Integrandos ----------

def f_erf(t):
    return math.exp(-t ** 2)


def f_fresnel_c(t):
    return math.cos(math.pi * t ** 2 / 2)


def f_fresnel_s(t):
    return math.sin(math.pi * t ** 2 / 2)


def f_si(t):
    # sin(t)/t -> 1 cuando t -> 0
    return 1.0 if t == 0 else math.sin(t) / t


def f_li(t):
    return 1 / math.log(t)


# ---------- Valores de referencia (series) para medir el error ----------

def serie(termino, x, maxk=200):

    total = 0.0
    for k in range(maxk):
        tk = termino(k, x)
        total += tk
        if abs(tk) < 1e-17 * max(1.0, abs(total)):
            break
    return total


def ref_fresnel_c(x):
    # C(x) = Σ (-1)^k (π/2)^(2k) x^(4k+1) / ((2k)! (4k+1))
    return serie(lambda k, x: (-1) ** k * (math.pi / 2) ** (2 * k) * x ** (4 * k + 1)
                 / (math.exp(math.lgamma(2 * k + 1)) * (4 * k + 1)), x)


def ref_fresnel_s(x):
    # S(x) = Σ (-1)^k (π/2)^(2k+1) x^(4k+3) / ((2k+1)! (4k+3))
    return serie(lambda k, x: (-1) ** k * (math.pi / 2) ** (2 * k + 1) * x ** (4 * k + 3)
                 / (math.exp(math.lgamma(2 * k + 2)) * (4 * k + 3)), x)


def ref_si(x):
    # Si(x) = Σ (-1)^k x^(2k+1) / ((2k+1) (2k+1)!)
    return serie(lambda k, x: (-1) ** k * x ** (2 * k + 1)
                 / ((2 * k + 1) * math.exp(math.lgamma(2 * k + 2))), x)


def li_ramanujan(x):
    # li(x) = γ + ln(ln x) + Σ_{k>=1} (ln x)^k / (k · k!)
    gamma = 0.5772156649015329
    L = math.log(x)
    return gamma + math.log(abs(L)) + serie(
        lambda k, L: L ** (k + 1) / ((k + 1) * math.factorial(k + 1)), L)


def ref_li(x):
    return li_ramanujan(x) - li_ramanujan(2)


# nombre: (integrando, límite inferior, factor delante de la integral, referencia, condición sobre x)
INTEGRALES = {
    "1": ("erf(x)", f_erf, 0.0, 2 / math.sqrt(math.pi), math.erf, None),
    "2": ("C(x) Fresnel coseno", f_fresnel_c, 0.0, 1.0, ref_fresnel_c, None),
    "3": ("S(x) Fresnel seno", f_fresnel_s, 0.0, 1.0, ref_fresnel_s, None),
    "4": ("Si(x) seno integral", f_si, 0.0, 1.0, ref_si, None),
    "5": ("Li(x) logarítmica euleriana", f_li, 2.0, 1.0, ref_li, lambda x: x > 1),
}

# Texto del integrando para la leyenda de la gráfica (incluye el factor)
INTEGRANDOS = {
    "1": "(2/√π)·exp(−t²)",
    "2": "cos(πt²/2)",
    "3": "sin(πt²/2)",
    "4": "sin(t)/t",
    "5": "1/ln(t)",
}


def comparar(nombre, f, a, b, n, factor, exacto, etiqueta_ref, etiqueta_f="f(x)"):

    print(f"\n{nombre},  intervalo [{a:g}, {b:g}]")
    print(f"Referencia ({etiqueta_ref}) = {exacto:.12f}")

    A_t = factor * trapecio(f, a, b, n)
    A_s = None
    print(f"Trapecio    n = {n:<5}  ≈ {A_t:.12f}   error = {abs(A_t - exacto):.3e}")
    if n % 2 == 0:
        A_s = factor * simpson_13(f, a, b, n)
        print(f"Simpson 1/3 n = {n:<5}  ≈ {A_s:.12f}   error = {abs(A_s - exacto):.3e}")
    else:
        print("Simpson 1/3: n debe ser par, se omite.")

    # Convergencia al duplicar n
    ns = [2, 4, 8, 16, 32, 64, 128]
    err_t, err_s = [], []
    print(f"\n{'n':>6} | {'Trapecio':>16} | {'error':>10} | {'Simpson 1/3':>16} | {'error':>10}")
    for m in ns:
        t = factor * trapecio(f, a, b, m)
        s = factor * simpson_13(f, a, b, m)
        err_t.append(abs(t - exacto))
        err_s.append(abs(s - exacto))
        print(f"{m:>6} | {t:>16.12f} | {err_t[-1]:>10.3e} | {s:>16.12f} | {err_s[-1]:>10.3e}")

    # Se grafica factor·f para que el área sombreada sea directamente A
    graficar_integracion(nombre, lambda t: factor * f(t), a, b, n, A_t, A_s, exacto,
                         etiqueta_f, ns, err_t, err_s)


def calcular(clave, x, n):

    nombre, f, a, factor, ref, valido = INTEGRALES[clave]
    if valido and not valido(x):
        print("Para Li(x) se requiere x > 1 (ln t no puede anularse en [2, x]).")
        return
    comparar(f"{nombre},  x = {x:g}", f, a, x, n, factor, ref(x), "serie / math", INTEGRANDOS[clave])


def calcular_personalizada():

    print("Escribe el integrando usando x como variable, p. ej. exp(-x^2), sin(x)/x, 1/ln(x)")
    f, texto = leer_funcion("f(x) = ")
    a = float(input("Límite inferior a: "))
    b = float(input("Límite superior b: "))
    n = int(input("Número de subintervalos n (par para Simpson): "))
    if n <= 0:
        print("n debe ser positivo.")
        return
    try:
        f(a), f(b), f((a + b) / 2)
    except (ValueError, ZeroDivisionError, OverflowError) as e:
        print(f"f no se puede evaluar en [a, b] ({e}). Si hay una singularidad removible,"
              " desplaza ligeramente el límite (p. ej. 1e-12 en vez de 0).")
        return

    exacto = input("Valor exacto, si lo conoces (Enter para omitir): ").strip()
    if exacto:
        ref = float(eval(exacto.replace("^", "**"), {"__builtins__": {}}, vars(math)))
        etiqueta = "valor exacto"
    else:
        ref = simpson_13(f, a, b, 200000)
        etiqueta = "Simpson n = 200000"
    comparar(f"∫ {texto} dx", f, a, b, n, 1.0, ref, etiqueta, f"f(x) = {texto}")


def main():
    print("Integración numérica: Trapecio y Simpson 1/3")
    for clave, datos in INTEGRALES.items():
        print(f"{clave}) {datos[0]}")
    print("6) Función personalizada f(x) en [a, b]")
    clave = input("Elige la integral: ").strip()
    if clave == "6":
        calcular_personalizada()
        return
    if clave not in INTEGRALES:
        print("Opción no válida.")
        return
    x = float(input("Valor de x: "))
    n = int(input("Número de subintervalos n (par para Simpson): "))
    if n <= 0:
        print("n debe ser positivo.")
        return
    calcular(clave, x, n)


if __name__ == "__main__":
    main()
