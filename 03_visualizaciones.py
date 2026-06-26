"""
Visualizaciones del analisis de portafolio:
precios normalizados, matriz de correlacion, riesgo-retorno y drawdown.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["figure.dpi"] = 110
plt.rcParams["font.size"] = 10

precios = pd.read_csv("precios.csv", index_col="fecha", parse_dates=True)
ret = pd.read_csv("retornos_diarios.csv", index_col="fecha", parse_dates=True)
met = pd.read_csv("metricas_activos.csv")

PALETA = ["#5B3DF5", "#00B8D4", "#FF6D00", "#00C853", "#1E1B4B"]

fig, axes = plt.subplots(2, 2, figsize=(13, 9))
fig.suptitle("Analisis de Portafolio de Inversiones", fontsize=15, fontweight="bold")

# 1. Precios normalizados (base 100)
norm = precios / precios.iloc[0] * 100
for i, col in enumerate(precios.columns):
    axes[0,0].plot(norm.index, norm[col], label=col, color=PALETA[i], linewidth=1.5)
axes[0,0].set_title("Evolucion normalizada (base 100)", fontweight="bold")
axes[0,0].legend(fontsize=8, ncol=2)
axes[0,0].grid(alpha=0.2)
axes[0,0].axhline(100, color="gray", linestyle="--", alpha=0.5)

# 2. Matriz de correlacion
corr = ret.corr()
im = axes[0,1].imshow(corr, cmap="Purples", vmin=0, vmax=1, aspect="auto")
axes[0,1].set_xticks(range(len(corr)))
axes[0,1].set_yticks(range(len(corr)))
axes[0,1].set_xticklabels(corr.columns, rotation=45)
axes[0,1].set_yticklabels(corr.columns)
axes[0,1].set_title("Matriz de correlacion", fontweight="bold")
for i in range(len(corr)):
    for j in range(len(corr)):
        axes[0,1].text(j, i, f"{corr.iloc[i,j]:.2f}", ha="center", va="center",
                       color="white" if corr.iloc[i,j] > 0.6 else "black", fontsize=8)
plt.colorbar(im, ax=axes[0,1], fraction=0.046)

# 3. Riesgo vs retorno
axes[1,0].scatter(met["volatilidad"], met["retorno"], s=120, c=PALETA[:len(met)], zorder=3)
for _, r in met.iterrows():
    axes[1,0].annotate(r["activo"], (r["volatilidad"], r["retorno"]),
                       xytext=(6, 6), textcoords="offset points", fontsize=9)
axes[1,0].set_xlabel("Volatilidad anual (riesgo)")
axes[1,0].set_ylabel("Retorno anual")
axes[1,0].set_title("Perfil riesgo - retorno", fontweight="bold")
axes[1,0].axhline(0, color="gray", linestyle="--", alpha=0.4)
axes[1,0].grid(alpha=0.2)
axes[1,0].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
axes[1,0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))

# 4. Drawdown de la cartera
pesos = np.array([0.25, 0.25, 0.25, 0.25])
ret_cartera = (ret[["AAPL","MSFT","GOOGL","AMZN"]] * pesos).sum(axis=1)
curva = (1 + ret_cartera).cumprod()
dd = (curva - curva.cummax()) / curva.cummax()
axes[1,1].fill_between(dd.index, dd * 100, 0, color="#FF6D00", alpha=0.4)
axes[1,1].plot(dd.index, dd * 100, color="#FF6D00", linewidth=1)
axes[1,1].set_title("Drawdown de la cartera (%)", fontweight="bold")
axes[1,1].grid(alpha=0.2)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("dashboard_portafolio.png", bbox_inches="tight")
print("Dashboard financiero guardado: dashboard_portafolio.png")
