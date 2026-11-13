"""Gera docs/results_overview.png a partir de results/metrics_*.json.

Uso: PYTHONPATH=src python scripts/plot_results.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

from order_parser.metrics import wilson  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SISTEMAS = [("rule_baseline", "Regras", "#2a78d6"), ("few_shot", "Qwen + 8 exemplos no prompt", "#eb6834"),
            ("lora", "Qwen + LoRA", "#1baf7a")]
TEXTO, TEXTO2, GRADE, FUNDO = "#0b0b0b", "#52514e", "#e7e6e2", "#fcfcfb"


def contagens(m):
    soma = lambda f: tuple(map(sum, zip(*[f(r) for r in m.values()])))  # noqa: E731
    return {
        "Emergência detectada": soma(lambda r: (r["intent"]["emergencia"]["acertos"], r["intent"]["emergencia"]["suporte"])),
        "Ataque detectado": soma(lambda r: (r["intent"]["ataque"]["acertos"], r["intent"]["ataque"]["suporte"])),
        "Alerta de saúde": soma(lambda r: (round((r["alerta_saude_recall"] or 0) * r["alerta_saude_n"]), r["alerta_saude_n"])),
        "Acerto exato · principal": (round(m["principal"]["exato"] * m["principal"]["n"]), m["principal"]["n"]),
        "Acerto exato · outro autor": (round(m["autor2"]["exato"] * m["autor2"]["n"]), m["autor2"]["n"]),
        "Acerto exato · mensagens reais": (round(m["humano_restaurante"]["exato"] * m["humano_restaurante"]["n"]),
                                           m["humano_restaurante"]["n"]),
    }


def main():
    for f in font_manager.findSystemFonts():
        if "Inter-Regular" in f or "Inter-Medium" in f:
            font_manager.fontManager.addfont(f)
    plt.rcParams.update({"font.family": "Inter", "font.size": 10})
    dados = {s: contagens(json.load(open(RAIZ / f"results/metrics_{s}.json"))) for s, _, _ in SISTEMAS}
    metricas = list(dados["lora"])
    fig, ax = plt.subplots(figsize=(8.2, 6.4), dpi=200)
    fig.patch.set_facecolor(FUNDO); ax.set_facecolor(FUNDO)
    altura, passo = 0.24, 1.0
    for j, (s, nome, cor) in enumerate(SISTEMAS):
        for i, met in enumerate(metricas):
            a, n = dados[s][met]
            y = i * passo + (j - 1) * (altura + 0.04)
            lo, hi = wilson(a, n)
            ax.barh(y, a / n * 100, height=altura, color=cor, label=nome if i == 0 else None, zorder=2)
            ax.plot([lo * 100, hi * 100], [y, y], color=TEXTO2, lw=1, zorder=3)
            ax.text(hi * 100 + 1.2, y, f"{a / n * 100:.0f}%", va="center", fontsize=8.5, color=TEXTO2)
    ax.set_yticks([i * passo for i in range(len(metricas))])
    ax.set_yticklabels([f"{m}\n(n={dados['lora'][m][1]})" for m in metricas], color=TEXTO, fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 112)
    ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], color=TEXTO2)
    ax.grid(axis="x", color=GRADE, lw=0.8, zorder=0)
    for lado in ["top", "right", "left"]:
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(GRADE); ax.tick_params(length=0)
    ax.axhline(2.5, color=GRADE, lw=1, ls=(0, (3, 3)))
    ax.text(111, 0.0 - 0.55, "SEGURANÇA", ha="right", fontsize=8, color=TEXTO2, weight="medium")
    ax.text(111, 2.68, "EXTRAÇÃO", ha="right", fontsize=8, color=TEXTO2, weight="medium")
    fig.suptitle("O ajuste ganhou na detecção de emergências e ataques, não na extração", x=0.02, ha="left",
                 fontsize=13, weight="medium", color=TEXTO)
    fig.text(0.02, 0.925, "Recall e acerto exato nos conjuntos de teste congelados · linha cinza = intervalo de 95%",
             fontsize=9, color=TEXTO2)
    ax.legend(loc="upper left", bbox_to_anchor=(-0.36, 1.1), ncol=3, frameon=False, fontsize=9, labelcolor=TEXTO,
              handlelength=1.2, columnspacing=1.5)
    fig.subplots_adjust(left=0.27, right=0.98, top=0.85, bottom=0.06)
    fig.savefig(RAIZ / "docs/results_overview.png", facecolor=FUNDO)


if __name__ == "__main__":
    main()
