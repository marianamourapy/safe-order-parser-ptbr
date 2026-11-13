"""Avalia regras, modelo ajustado e híbrido no conjunto novo, como pré-registrado.

Uso: PYTHONPATH=src python scripts/evaluate_fresh.py results/preds_lora_fresh.jsonl

O arquivo de previsões vem da célula 8 do notebook. Gera results/fresh_eval.md.
"""
import hashlib
import json
import math
import re
import sys
from pathlib import Path

from order_parser.baseline import prever
from order_parser.hybrid import descartando, estrito, hibrido
from order_parser.metrics import avaliar
from order_parser.schema import Pedido

RAIZ = Path(__file__).resolve().parents[1]


def mcnemar_exato(a_certo, b_certo):
    """Teste pareado: só contam as frases em que um sistema acertou e o outro errou.

    Sob a hipótese de que os dois são iguais, cada discordância é cara ou coroa.
    Devolve (só A acertou, só B acertou, valor-p bilateral exato).
    """
    so_a = sum(a and not b for a, b in zip(a_certo, b_certo))
    so_b = sum(b and not a for a, b in zip(a_certo, b_certo))
    n, k = so_a + so_b, min(so_a, so_b)
    p = min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0
    return so_a, so_b, p


def pct(x):
    return "—" if x is None else f"{100 * x:.0f}%"


def main(arq_preds):
    conjunto = RAIZ / "data/test/test_fresh_llm.jsonl"
    registro = (RAIZ / "data/test/FROZEN_FRESH.md").read_text(encoding="utf8")
    esperado = re.search(r"`([0-9a-f]{64})`", registro).group(1)
    assert hashlib.sha256(conjunto.read_bytes()).hexdigest() == esperado, "o conjunto novo mudou depois do congelamento"

    exs = [json.loads(l) for l in open(conjunto, encoding="utf8")]
    preds = {r["id"]: r["saida"] for r in map(json.loads, open(arq_preds, encoding="utf8"))}
    assert all(e["id"] in preds for e in exs), "faltam previsões"
    ouros = [Pedido.model_validate(e["rotulo"]) for e in exs]
    regras = [prever(e["texto"]) for e in exs]

    sistemas = {
        "Regras (baseline)": regras,
        "Qwen + LoRA (leitura oficial)": [estrito(preds[e["id"]]) for e in exs],
        "Qwen + LoRA, descartando valores inválidos": [descartando(preds[e["id"]]) for e in exs],
        "Híbrido (pré-registrado)": [hibrido(preds[e["id"]], r) for e, r in zip(exs, regras)],
    }
    res = {n: avaliar(ouros, p) for n, p in sistemas.items()}
    n = len(exs)
    out = [f"# Conjunto novo ({n} frases, outro LLM, rotuladas pela autora)", "",
           "Avaliação definida em PREREGISTRATION.md antes de rotular e de rodar qualquer sistema.", "",
           "| Métrica | " + " | ".join(res) + " |", "|---|" + "---|" * len(res)]

    def linha(rot, f):
        out.append(f"| {rot} | " + " | ".join(f(r) for r in res.values()) + " |")

    linha("**Acerto exato (principal)**",
          lambda r: f"**{pct(r['exato'])}** [{100 * r['ic95_exato'][0]:.0f}–{100 * r['ic95_exato'][1]:.0f}]")
    linha("Micro-F1 dos campos", lambda r: pct(r["micro_f1"]))
    linha("JSON válido", lambda r: pct(r["json_valido"]))
    linha("Intenção correta", lambda r: pct(sum(v["acertos"] for v in r["intent"].values()) / n))
    linha("Fora de escopo detectado", lambda r: f"{r['intent']['fora_escopo']['acertos']}/{r['intent']['fora_escopo']['suporte']}")
    linha("Restrições completas", lambda r: f"{pct(r['restricoes_completas'])} (n={r['restricoes_completas_n']})")
    linha("Alerta de saúde (recall)", lambda r: f"{pct(r['alerta_saude_recall'])} (n={r['alerta_saude_n']})")
    linha("Inventou campos em pedido vazio", lambda r: f"{pct(r['inventou_em_vazios'])} (n={r['vazios_n']})")

    acertos = {nome: [o == (p or Pedido()) for o, p in zip(ouros, prevs)] for nome, prevs in sistemas.items()}
    h = acertos["Híbrido (pré-registrado)"]
    out += ["", "## Análise adicional (não pré-registrada): teste pareado de McNemar", "",
            "Os sistemas responderam às mesmas frases, então dá para comparar só as frases em que um acertou "
            "e o outro errou. Valor-p exato, bilateral.", "",
            "| Comparação | Só o híbrido acertou | Só o outro acertou | Valor-p |", "|---|---|---|---|"]
    for outro in ["Regras (baseline)", "Qwen + LoRA (leitura oficial)"]:
        a, b, p = mcnemar_exato(h, acertos[outro])
        out.append(f"| Híbrido x {outro} | {a} | {b} | {p:.3f} |")

    (RAIZ / "results" / "fresh_eval.md").write_text("\n".join(out) + "\n", encoding="utf8")
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
