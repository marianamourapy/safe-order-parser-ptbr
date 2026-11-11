"""Concordância entre a rotulagem às cegas da autora e os rótulos do conjunto de teste.

Uso: PYTHONPATH=src python scripts/agreement.py annotation/blind_labeling_filled.xlsx

annotation/blind_labeling.xlsx é a planilha em branco; blind_labeling_filled.xlsx, a preenchida.
"""
import json
import sys
from pathlib import Path

from openpyxl import load_workbook

from order_parser.metrics import CAMPOS, wilson
from order_parser.schema import Pedido

RAIZ = Path(__file__).resolve().parents[1]
LISTAS = {"categories", "exclude_categories", "exclude_ingredients", "restrictions", "partial_restrictions", "wishes"}


def ler(caminho):
    ws = load_workbook(caminho)["Rotular"]
    cab = [c.value for c in ws[1]]
    for linha in ws.iter_rows(min_row=2, values_only=True):
        d = dict(zip(cab, linha))
        if not d["id"]:
            continue
        p = {}
        for k in cab[2:]:
            v = d[k]
            if v in (None, ""):
                continue
            if k in LISTAS:
                p[k] = [x.strip() for x in str(v).replace(",", ";").split(";") if x.strip()]
            elif k in ("health_alert", "free_delivery"):
                p[k] = str(v).strip().lower() in ("true", "sim", "1", "x")
            elif k == "intent":
                p[k] = str(v).strip()
            else:
                p[k] = float(str(v).replace(",", "."))
        yield d["id"], d["texto"], p


def main(caminho):
    ouro = {}
    for f in (RAIZ / "data/test").glob("test_*.jsonl"):
        for l in open(f, encoding="utf8"):
            r = json.loads(l)
            ouro[r["id"]] = Pedido.model_validate(r["rotulo"])
    iguais = total = 0
    por_campo = {c: [0, 0] for c in ["intent"] + CAMPOS}
    divergencias = []
    for i, texto, bruto in ler(caminho):
        try:
            meu = Pedido.model_validate(bruto)
        except Exception as e:
            divergencias.append(f"- `{i}` rótulo inválido ({str(e).splitlines()[0]}): {texto}")
            total += 1
            continue
        o = ouro[i]
        total += 1
        iguais += meu == o
        difs = []
        for c in por_campo:
            a, b = getattr(meu, c), getattr(o, c)
            por_campo[c][1] += 1
            por_campo[c][0] += a == b
            if a != b:
                difs.append(f"{c}: autora={a} | teste={b}")
        if difs:
            divergencias.append(f"- `{i}` {texto}\n  - " + "\n  - ".join(difs))
    lo, hi = wilson(iguais, total)
    out = [f"# Concordância da rotulagem às cegas", "",
           f"Rótulo inteiro igual: {iguais}/{total} ({100 * iguais / total:.0f}%) [IC 95%: {100 * lo:.0f}–{100 * hi:.0f}]", "",
           "| Campo | Concordância |", "|---|---|"]
    out += [f"| `{c}` | {a}/{n} ({100 * a / n:.0f}%) |" for c, (a, n) in por_campo.items()]
    out += ["", "## Divergências", ""] + divergencias
    (RAIZ / "annotation" / "agreement.md").write_text("\n".join(out) + "\n", encoding="utf8")
    print("\n".join(out[:22]))


if __name__ == "__main__":
    main(sys.argv[1])
