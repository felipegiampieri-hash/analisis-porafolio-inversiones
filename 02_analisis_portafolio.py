"""
Analisis cuantitativo de un portafolio de activos.
Calcula retornos, volatilidad anualizada, Sharpe ratio, maximo drawdown,
correlaciones y compara una cartera diversificada contra el indice (SPY).
"""
import numpy as np
import pandas as pd

precios = pd.read_csv("precios.csv", index_col="fecha", parse_dates=True)
activos = ["AAPL", "MSFT", "GOOGL", "AMZN"]
benchmark = "SPY"

# Retornos diarios logaritmicos
ret = np.log(precios / precios.shift(1)).dropna()

TASA_LIBRE = 0.04  # tasa libre de riesgo anual aprox

def metricas(serie_ret):
    ret_anual = serie_ret.mean() * 252
    vol_anual = serie_ret.std() * np.sqrt(252)
    sharpe = (ret_anual - TASA_LIBRE) / vol_anual
    # Maximo drawdown
    curva = (1 + serie_ret).cumprod()
    pico = curva.cummax()
    drawdown = (curva - pico) / pico
    max_dd = drawdown.min()
    return ret_anual, vol_anual, sharpe, max_dd

print("=" * 70)
print("METRICAS POR ACTIVO (anualizadas)")
print("=" * 70)
print(f"{'Activo':<8}{'Retorno':>10}{'Volatilidad':>14}{'Sharpe':>9}{'Max DD':>10}")
print("-" * 70)
filas = []
for t in activos + [benchmark]:
    ra, va, sh, dd = metricas(ret[t])
    print(f"{t:<8}{ra:>9.1%}{va:>13.1%}{sh:>9.2f}{dd:>10.1%}")
    filas.append({"activo": t, "retorno": ra, "volatilidad": va,
                  "sharpe": sh, "max_drawdown": dd})

# --- Cartera equiponderada (25% cada tech) ---
pesos = np.array([0.25, 0.25, 0.25, 0.25])
ret_cartera = (ret[activos] * pesos).sum(axis=1)
ra, va, sh, dd = metricas(ret_cartera)
print("-" * 70)
print(f"{'CARTERA':<8}{ra:>9.1%}{va:>13.1%}{sh:>9.2f}{dd:>10.1%}")
print(f"{'(equiponderada 25% c/u)'}")

# --- Comparacion cartera vs benchmark ---
print("\n" + "=" * 70)
print("CARTERA DIVERSIFICADA vs SPY (benchmark)")
print("=" * 70)
ra_c, va_c, sh_c, dd_c = metricas(ret_cartera)
ra_b, va_b, sh_b, dd_b = metricas(ret[benchmark])
print(f"Retorno anual:    Cartera {ra_c:>6.1%}  |  SPY {ra_b:>6.1%}")
print(f"Volatilidad:      Cartera {va_c:>6.1%}  |  SPY {va_b:>6.1%}")
print(f"Sharpe ratio:     Cartera {sh_c:>6.2f}  |  SPY {sh_b:>6.2f}")
print(f"Max drawdown:     Cartera {dd_c:>6.1%}  |  SPY {dd_b:>6.1%}")

# --- Matriz de correlacion ---
print("\n" + "=" * 70)
print("MATRIZ DE CORRELACION (retornos diarios)")
print("=" * 70)
print(ret.corr().round(2).to_string())

# Guardar resultados
pd.DataFrame(filas).to_csv("metricas_activos.csv", index=False)
ret.to_csv("retornos_diarios.csv")
print("\nResultados guardados.")
