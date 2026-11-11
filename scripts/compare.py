"""Junta as métricas de todos os sistemas em results/summary.md (tabela do README).

Uso: PYTHONPATH=src python scripts/compare.py
"""
import json
from pathlib import Path

from order_parser.metrics import wilson

RAIZ = Path(__file__).resolve().parents[1]
SISTEMAS = [("rule_baseline", "Regras (baseline)"), ("zero_shot", "Qwen sem ajuste"),
            ("few_shot", "Qwen + 8 exemplos no prompt"), ("lora", "Qwen + LoRA (este projeto)")]
CONJUNTOS = [("principal", "Principal (LLM, autor 1)"), ("autor2", "Outro autor (LLM)"), ("humano", "Humano"),
             ("humano_restaurante", "Humano, mensagens reais p/ restaurante")]
pct = lambda x: "—" if x is None else f"{100 * x:.0f}%"


def main():
    dados = {}
    for slug, _ in SISTEMAS:
        f = RAIZ / "results" / f"metrics_{slug}.json"
        if f.exists():
            dados[slug] = json.loads(f.read_text(encoding="utf8"))
    nomes = [(s, n) for s, n in SISTEMAS if s in dados]
    out = ["## Acerto exato (JSON inteiro correto), com intervalo de 95%", "",
           "| Conjunto | n | " + " | ".join(n for _, n in nomes) + " |", "|---|---|" + "---|" * len(nomes)]
    for c, rot in CONJUNTOS:
        linha = [rot, str(dados[nomes[0][0]][c]["n"])]
        for s, _ in nomes:
            r = dados[s][c]
            lo, hi = r["ic95_exato"]
            linha.append(f"{pct(r['exato'])} [{100 * lo:.0f}–{100 * hi:.0f}]")
        out.append("| " + " | ".join(linha) + " |")
    out += ["", "## Micro-F1 dos campos", "", "| Conjunto | " + " | ".join(n for _, n in nomes) + " |",
            "|---|" + "---|" * len(nomes)]
    for c, rot in CONJUNTOS:
        out.append("| " + rot + " | " + " | ".join(pct(dados[s][c]["micro_f1"]) for s, _ in nomes) + " |")

    def soma(s, chave_ok, chave_n, conjuntos):
        ok = n = 0
        for c in conjuntos:
            r = dados[s][c]
            if r[chave_n]:
                ok += round(r[chave_ok] * r[chave_n]); n += r[chave_n]
        return ok, n

    todos = [c for c, _ in CONJUNTOS]
    out += ["", "## Segurança e restrições (todos os conjuntos somados)", "",
            "| Métrica | " + " | ".join(n for _, n in nomes) + " |", "|---|" + "---|" * len(nomes)]
    linhas = [("JSON válido", None), ("Restrições completas", ("restricoes_completas", "restricoes_completas_n")),
              ("Alerta de saúde (recall)", ("alerta_saude_recall", "alerta_saude_n")),
              ("Inventou campos em pedido vazio", ("inventou_em_vazios", "vazios_n"))]
    for rot, ch in linhas:
        cel = []
        for s, _ in nomes:
            if ch is None:
                n = sum(dados[s][c]["n"] for c in dados[s]); ok = sum(round(dados[s][c]["json_valido"] * dados[s][c]["n"]) for c in dados[s])
            else:
                ok, n = soma(s, ch[0], ch[1], todos)
            lo, hi = wilson(ok, n)
            cel.append(f"{ok}/{n} ({pct(ok / n if n else None)}) [{100 * lo:.0f}–{100 * hi:.0f}]")
        out.append("| " + rot + " | " + " | ".join(cel) + " |")
    for classe, rot in [("emergencia", "Emergência detectada (recall)"), ("ataque", "Ataque detectado (recall)")]:
        cel = []
        for s, _ in nomes:
            ok = sum(dados[s][c]["intent"][classe]["acertos"] for c in dados[s]); n = sum(dados[s][c]["intent"][classe]["suporte"] for c in dados[s])
            lo, hi = wilson(ok, n)
            cel.append(f"{ok}/{n} ({pct(ok / n if n else None)}) [{100 * lo:.0f}–{100 * hi:.0f}]")
        out.append("| " + rot + " | " + " | ".join(cel) + " |")
    lat = RAIZ / "results" / "latency.json"
    if lat.exists():
        L = json.loads(lat.read_text())
        out += ["", "## Custo por mensagem (GPU T4, lote de 16)", "", "| Sistema | Tokens de entrada | Tokens de saída | Segundos por mensagem |", "|---|---|---|---|"]
        for s, n in nomes:
            if s in L:
                out.append(f"| {n} | {L[s]['tokens_entrada']:.0f} | {L[s]['tokens_saida']:.1f} | {L[s]['seg_por_msg']:.3f} |")
    (RAIZ / "results" / "summary.md").write_text("\n".join(out) + "\n", encoding="utf8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
