"""Avalia um sistema nos conjuntos de teste congelados.

Uso:
  PYTHONPATH=src python scripts/evaluate.py --sistema baseline
  PYTHONPATH=src python scripts/evaluate.py --preds results/zero_shot.jsonl --nome "Qwen sem ajuste"

O arquivo de previsões tem uma linha por frase: {"id": "t001", "saida": "<texto cru gerado pelo modelo>"}.
Saídas que não são JSON válido no schema contam como previsão vazia.
"""

import argparse
import json
from pathlib import Path

from order_parser.output_format import de_json
from order_parser.metrics import avaliar, campos_md, resumo_md
from order_parser.schema import Pedido

RAIZ = Path(__file__).resolve().parents[1]
CONJUNTOS = {"principal": "test_main.jsonl", "autor2": "test_author2.jsonl", "humano": "test_human.jsonl",
             "humano_seguranca": "test_human_safety.jsonl",
             "humano_restaurante": "test_human_restaurant.jsonl"}


def carregar(nome):
    return [json.loads(l) for l in open(RAIZ / "data/test" / CONJUNTOS[nome], encoding="utf8")]


def ler(saida):
    try:
        return de_json(saida)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sistema", choices=["baseline"])
    ap.add_argument("--preds")
    ap.add_argument("--nome")
    ap.add_argument("--slug", help="nome curto para os arquivos de saída")
    a = ap.parse_args()

    if a.sistema == "baseline":
        from order_parser.baseline import prever
        from order_parser.output_format import para_json
        nome = a.nome or "Baseline por regras"
        preds = {ex["id"]: para_json(prever(ex["texto"])) for c in CONJUNTOS for ex in carregar(c)}
        saida_preds = RAIZ / "results" / "preds_rule_baseline.jsonl"
        saida_preds.parent.mkdir(exist_ok=True)
        with open(saida_preds, "w", encoding="utf8") as f:
            for i, s in preds.items():
                f.write(json.dumps({"id": i, "saida": s}, ensure_ascii=False) + "\n")
    else:
        nome = a.nome or Path(a.preds).stem
        preds = {r["id"]: r["saida"] for r in map(json.loads, open(a.preds, encoding="utf8"))}

    resultados = {}
    for c in CONJUNTOS:
        exs = carregar(c)
        faltando = [ex["id"] for ex in exs if ex["id"] not in preds]
        assert not faltando, f"{c}: faltam previsões para {faltando[:5]}"
        ouros = [Pedido.model_validate(ex["rotulo"]) for ex in exs]
        prevs = [ler(preds[ex["id"]]) for ex in exs]
        resultados[c] = avaliar(ouros, prevs, [ex.get("tag", c) for ex in exs])

    slug = a.slug or ("rule_baseline" if a.sistema == "baseline" else Path(a.preds).stem.removeprefix("preds_"))
    out = RAIZ / "results"
    out.mkdir(exist_ok=True)
    (out / f"metrics_{slug}.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf8")
    md = resumo_md(nome, resultados) + "\n\n#### Campos (conjunto principal)\n\n" + campos_md(resultados["principal"])
    (out / f"metrics_{slug}.md").write_text(md + "\n", encoding="utf8")
    print(md)
    print("\nExato por tag (principal):")
    for t, (v, n) in resultados["principal"]["exato_por_tag"].items():
        print(f"  {t:15s} {100 * v:5.1f}%  (n={n})")


if __name__ == "__main__":
    main()
