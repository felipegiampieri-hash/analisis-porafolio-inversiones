"""
Genera series de precios diarios realistas para un portafolio de activos.
Usa un modelo de movimiento browniano geometrico con drift y volatilidad
calibrados por activo, mas correlaciones entre ellos. Esto produce series
con las propiedades estadisticas de retornos financieros reales.
"""
import numpy as np
import pandas as pd

np.random.seed(7)

# Activos: ticker, precio inicial, retorno anual esperado, volatilidad anual
activos = {
    "AAPL": (185, 0.18, 0.25),
    "MSFT": (370, 0.16, 0.23),
    "GOOGL": (140, 0.14, 0.28),
    "AMZN": (155, 0.20, 0.32),
    "SPY":  (475, 0.10, 0.15),  # indice de referencia
}

dias = 504  # ~2 anios habiles
dt = 1 / 252
fechas = pd.bdate_range("2023-01-02", periods=dias)

# Matriz de correlacion realista (las big tech se mueven juntas)
tickers = list(activos.keys())
n = len(tickers)
corr = np.array([
    [1.00, 0.72, 0.65, 0.60, 0.78],
    [0.72, 1.00, 0.68, 0.58, 0.80],
    [0.65, 0.68, 1.00, 0.62, 0.75],
    [0.60, 0.58, 0.62, 1.00, 0.70],
    [0.78, 0.80, 0.75, 0.70, 1.00],
])
L = np.linalg.cholesky(corr)

# Generar shocks correlacionados
z = np.random.standard_normal((dias, n))
shocks = z @ L.T

precios = {}
for i, t in enumerate(tickers):
    p0, mu, sigma = activos[t]
    retornos = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * shocks[:, i]
    serie = p0 * np.exp(np.cumsum(retornos))
    precios[t] = np.round(serie, 2)

df = pd.DataFrame(precios, index=fechas)
df.index.name = "fecha"
df.to_csv("precios.csv")

print(f"Series generadas: {dias} dias habiles, {n} activos")
print(df.head().to_string())
print("...")
print(df.tail().to_string())
