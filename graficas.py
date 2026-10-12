"""
Rutinas de graficación compartidas (matplotlib).

  graficar_interpolacion : nodos, curvas interpolantes, puntos evaluados y,
                           si se conoce f(x), la función real y el error.
  graficar_integracion   : áreas del trapecio y de Simpson 1/3 sobre f(x),
                           más la convergencia del error al aumentar n.

Cada gráfica se guarda como .png en la carpeta "graficas/" y se abre en una
ventana. Con la opción --sin-ventana solo se guarda el .png.
"""

import os
import sys

SIN_VENTANA = "--sin-ventana" in sys.argv
CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graficas")
MAX_FIGURAS = 60        # con n mayor ya no se distinguen trapecios ni parábolas


def argumentos():

    # sys.argv sin las opciones que empiezan con "--"
    return [a for a in sys.argv if not a.startswith("--")]


def _pyplot():

    try:
        import matplotlib
        if SIN_VENTANA:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        print("(matplotlib no está instalado: se omite la gráfica)")
        return None


def _guardar(plt, fig, titulo):

    os.makedirs(CARPETA, exist_ok=True)
    nombre = "".join(c if c.isalnum() else "_" for c in titulo)
    nombre = "_".join(p for p in nombre.split("_") if p)[:80]
    ruta = os.path.join(CARPETA, nombre + ".png")
    fig.tight_layout()
    fig.savefig(ruta, dpi=130)
    print(f"Gráfica guardada en {ruta}")
    if not SIN_VENTANA:
        plt.show()
    plt.close(fig)


def _muestreo(a, b, m=600):

    return [a + (b - a) * k / m for k in range(m + 1)]


def _evaluar_seguro(g, ts):

    ys = []
    for t in ts:
        try:
            ys.append(float(g(t)))
        except (ValueError, ZeroDivisionError, OverflowError):
            ys.append(float("nan"))
    return ys


# ---------------------------------------------------------------------------
# Interpolación
# ---------------------------------------------------------------------------

def graficar_interpolacion(titulo, x, f, curvas, evaluar=(), funcion=None):

    """
    curvas : lista de (etiqueta, g) donde g(t) evalúa el interpolante.
    evaluar: puntos donde se pidió estimar f(x); se marcan sobre cada curva.
    funcion: f(x) real si se conoce (agrega la curva real y un panel de error).
    """
    plt = _pyplot()
    if plt is None:
        return

    a = min([x[0]] + list(evaluar))
    b = max([x[-1]] + list(evaluar))
    ts = _muestreo(a, b)
    colores = ["tab:blue", "tab:orange", "tab:green", "tab:purple"]

    if funcion is not None:
        fig, (ax, ax_err) = plt.subplots(2, 1, figsize=(9, 7.5), sharex=True,
                                         gridspec_kw={"height_ratios": [3, 2]})
    else:
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax_err = None

    if funcion is not None:
        ax.plot(ts, _evaluar_seguro(funcion, ts), color="gray", lw=4, alpha=0.4, label="f(x) real")

    for k, (etiqueta, g) in enumerate(curvas):
        color = colores[k % len(colores)]
        estilo = "-" if k == 0 else "--"
        ax.plot(ts, _evaluar_seguro(g, ts), estilo, color=color, lw=1.8, label=etiqueta)
        for t in evaluar:
            y = g(t)
            ax.plot([t], [y], "X", color=color, ms=9, mec="black", mew=0.6, zorder=5)
            ax.annotate(f"{y:.4g}", (t, y), textcoords="offset points",
                        xytext=(6, 8 if k == 0 else -14), fontsize=8, color=color)

    ax.plot(x, f, "o", color="black", ms=6, zorder=6, label="Nodos (x_i, f_i)")
    for t in evaluar:
        ax.axvline(t, color="gray", ls=":", lw=0.8)

    ax.set_title(titulo)
    ax.set_ylabel("f(x)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)

    if ax_err is not None:
        real = _evaluar_seguro(funcion, ts)
        for k, (etiqueta, g) in enumerate(curvas):
            err = [abs(p - r) if p == p and r == r else float("nan")
                   for p, r in zip(_evaluar_seguro(g, ts), real)]
            # log(0) no existe: se reemplaza por un valor muy pequeño
            err = [e if e > 1e-16 else 1e-16 for e in err]
            ax_err.semilogy(ts, err, color=colores[k % len(colores)], lw=1.4, label=etiqueta)
        ax_err.set_ylabel("|P(x) − f(x)|")
        ax_err.set_xlabel("x")
        ax_err.grid(True, which="both", alpha=0.3)
        ax_err.legend(loc="best", fontsize=9)
    else:
        ax.set_xlabel("x")

    _guardar(plt, fig, titulo)


# ---------------------------------------------------------------------------
# Integración
# ---------------------------------------------------------------------------

def _parabola(x0, x1, x2, y0, y1, y2):

    # Polinomio de Lagrange de grado 2 por (x0,y0), (x1,y1), (x2,y2)
    def p(t):
        return (y0 * (t - x1) * (t - x2) / ((x0 - x1) * (x0 - x2))
                + y1 * (t - x0) * (t - x2) / ((x1 - x0) * (x1 - x2))
                + y2 * (t - x0) * (t - x1) / ((x2 - x0) * (x2 - x1)))
    return p


def _dibujar_curva(ax, f, a, b, etiqueta):

    margen = 0.05 * (b - a)
    ts = _muestreo(a - margen, b + margen)
    ax.plot(ts, _evaluar_seguro(f, ts), color="black", lw=1.6, label=etiqueta, zorder=4)
    ax.axhline(0, color="gray", lw=0.8)
    ax.grid(True, alpha=0.3)
    ax.set_xlabel("x")


def graficar_integracion(titulo, f, a, b, n, A_t, A_s, exacto, etiqueta_f,
                         ns, err_t, err_s):

    """
    f       : integrando ya multiplicado por el factor (el área sombreada = A).
    A_s     : None si n es impar (Simpson no aplica).
    ns, err_t, err_s: datos de la tabla de convergencia.
    """
    plt = _pyplot()
    if plt is None:
        return

    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]
    ys = _evaluar_seguro(f, xs)

    fig, (ax_t, ax_s, ax_c) = plt.subplots(1, 3, figsize=(16, 5))

    # --- Trapecio ---
    _dibujar_curva(ax_t, f, a, b, etiqueta_f)
    if n <= MAX_FIGURAS:
        for i in range(n):
            ax_t.fill([xs[i], xs[i], xs[i + 1], xs[i + 1]], [0, ys[i], ys[i + 1], 0],
                      facecolor="tab:blue", alpha=0.25, edgecolor="tab:blue", lw=0.8)
        ax_t.plot(xs, ys, "o", color="tab:blue", ms=4)
    else:
        ax_t.fill_between(xs, ys, color="tab:blue", alpha=0.25)
    ax_t.set_title(f"Trapecio (n = {n})\nA ≈ {A_t:.10f}   error = {abs(A_t - exacto):.2e}")
    ax_t.legend(fontsize=8)

    # --- Simpson 1/3 ---
    _dibujar_curva(ax_s, f, a, b, etiqueta_f)
    if A_s is None:
        ax_s.set_title(f"Simpson 1/3: no aplica\n(n = {n} es impar)")
    else:
        for k in range(0, n, 2):
            p = _parabola(xs[k], xs[k + 1], xs[k + 2], ys[k], ys[k + 1], ys[k + 2])
            ts = _muestreo(xs[k], xs[k + 2], 40)
            pt = [p(t) for t in ts]
            ax_s.fill_between(ts, pt, color="tab:orange", alpha=0.25,
                              edgecolor="tab:orange" if n <= MAX_FIGURAS else "none")
            if n <= MAX_FIGURAS:
                ax_s.plot(ts, pt, color="tab:orange", lw=1)
                ax_s.axvline(xs[k + 2], color="tab:orange", lw=0.6, alpha=0.6)
        if n <= MAX_FIGURAS:
            ax_s.plot(xs, ys, "o", color="tab:orange", ms=4)
        ax_s.set_title(f"Simpson 1/3 (n = {n}, {n // 2} parábolas)\n"
                       f"A ≈ {A_s:.10f}   error = {abs(A_s - exacto):.2e}")
    ax_s.legend(fontsize=8)

    # --- Convergencia ---
    hs = [(b - a) / m for m in ns]
    piso = 1e-16
    ax_c.loglog(ns, [max(e, piso) for e in err_t], "o-", color="tab:blue", label="Trapecio")
    ax_c.loglog(ns, [max(e, piso) for e in err_s], "s-", color="tab:orange", label="Simpson 1/3")
    # Rectas de referencia O(h^2) y O(h^4) que parten del primer punto
    if err_t[0] > 0:
        ax_c.loglog(ns, [err_t[0] * (hh / hs[0]) ** 2 for hh in hs], ":", color="tab:blue",
                    label="pendiente O(h²)")
    if err_s[0] > 0:
        ax_c.loglog(ns, [max(err_s[0] * (hh / hs[0]) ** 4, piso) for hh in hs], ":",
                    color="tab:orange", label="pendiente O(h⁴)")
    ax_c.set_title("Convergencia del error")
    ax_c.set_xlabel("n (número de subintervalos)")
    ax_c.set_ylabel("|A − referencia|")
    ax_c.grid(True, which="both", alpha=0.3)
    ax_c.legend(fontsize=8)

    fig.suptitle(titulo)
    _guardar(plt, fig, titulo)
