"""Análise de erros do modelo ajustado, a partir das previsões salvas em results/.

Uso: PYTHONPATH=src python scripts/error_analysis.py

Gera results/error_analysis.md com:
  1. por que cada saída inválida foi rejeitada pelo schema;
  2. itens inventados (fp) e itens que faltaram (fn) por campo, modelo x regras;
  3. confusões de intenção;
  4. duas variações calculadas DEPOIS de ver o resultado no teste (análise posterior).

As variações da parte 4 foram escolhidas olhando os erros no próprio teste. Por isso
não são resultado oficial: servem para apontar o próximo experimento, que precisa
de frases novas para ser confirmado.
"""

import json
from collections import Counter
from pathlib import Path

from order_parser.metrics import avaliar
from order_parser.hybrid import descartando, estrito
from order_parser.hybrid import hibrido as _hibrido
from order_parser.schema import Categoria, Desejo, Pedido, Restricao  # noqa: F401

RAIZ = Path(__file__).resolve().parents[1]
CONJUNTOS = {"Principal": "test_main.jsonl", "Outro autor": "test_author2.jsonl", "Humano": "test_human.jsonl",
             "Humano, restaurante": "test_human_restaurant.jsonl", "Humano, segurança": "test_human_safety.jsonl"}
ENUMS = {"categories": Categoria, "exclude_categories": Categoria, "restrictions": Restricao,
         "partial_restrictions": Restricao, "wishes": Desejo}


def carregar_teste():
    return {nome: [json.loads(l) for l in open(RAIZ / "data/test" / arq, encoding="utf8")]
            for nome, arq in CONJUNTOS.items()}


def carregar_preds(slug):
    linhas = map(json.loads, open(RAIZ / "results" / f"preds_{slug}.jsonl", encoding="utf8"))
    return {r["id"]: r["saida"] for r in linhas}


def motivo_invalido(saida):
    """Classifica por que o schema rejeitou a saída."""
    try:
        inicio = saida.find("{")
        if inicio < 0:
            return "sem JSON na saída"
        dados, _ = json.JSONDecoder().raw_decode(saida[inicio:])
    except Exception:
        return "JSON malformado"
    for k, v in dados.items():
        if k not in Pedido.model_fields:
            return "chave que não existe no schema"
    for k, v in dados.items():
        if k in ENUMS and isinstance(v, list) and any(x not in {e.value for e in ENUMS[k]} for x in v):
            return "valor fora da lista permitida"
    return "outra regra do schema"


def hibrido(saida_modelo, saida_regras):
    return _hibrido(saida_modelo, estrito(saida_regras))


def pct(x):
    return "—" if x is None else f"{100 * x:.0f}%"


def main():
    teste = carregar_teste()
    lora, regras = carregar_preds("lora"), carregar_preds("rule_baseline")
    todos = [ex for exs in teste.values() for ex in exs]
    out = ["# Análise de erros do modelo ajustado (Qwen + LoRA)", "",
           "Gerado por `scripts/error_analysis.py` a partir de `results/preds_*.jsonl`.", ""]

    # 1. saídas inválidas
    motivos = Counter(motivo_invalido(lora[ex["id"]]) for ex in todos if estrito(lora[ex["id"]]) is None)
    total = sum(motivos.values())
    out += [f"## 1. Saídas rejeitadas pelo schema: {total} de {len(todos)}", "",
            "Na avaliação oficial, uma saída rejeitada conta como \"não extraiu nada\".", "",
            "| Motivo | Saídas |", "|---|---|"]
    out += [f"| {m} | {n} |" for m, n in motivos.most_common()]
    exemplos = [ex for ex in todos if estrito(lora[ex["id"]]) is None][:60]
    vistos, mostra = set(), []
    for ex in exemplos:
        m = motivo_invalido(lora[ex["id"]])
        if m not in vistos or len(mostra) < 6:
            vistos.add(m)
            mostra.append(f"- `{ex['id']}` ({m}): {lora[ex['id']][:110]}")
    out += ["", "Exemplos:", ""] + mostra[:8]

    # 2. inventados e faltantes por campo
    out += ["", "## 2. Itens inventados (fp) e itens que faltaram (fn), por campo", "",
            "Modelo com valores inválidos descartados, para contar só o que ele extraiu de fato. "
            "Todos os conjuntos somados.", "",
            "| Campo | Modelo: certos | Modelo: inventados | Modelo: faltaram | Regras: certos | Regras: inventados "
            "| Regras: faltaram |", "|---|---|---|---|---|---|---|"]
    ouros = [Pedido.model_validate(ex["rotulo"]) for ex in todos]
    rm = avaliar(ouros, [descartando(lora[ex["id"]]) for ex in todos])
    rr = avaliar(ouros, [estrito(regras[ex["id"]]) for ex in todos])
    for campo in rm["campos"]:
        a, b = rm["campos"][campo], rr["campos"][campo]
        out.append(f"| `{campo}` | {a['tp']} | {a['fp']} | {a['fn']} | {b['tp']} | {b['fp']} | {b['fn']} |")
    soma = lambda r, k: sum(v[k] for v in r["campos"].values())  # noqa: E731
    out.append(f"| **Total** | {soma(rm, 'tp')} | {soma(rm, 'fp')} | {soma(rm, 'fn')} "
               f"| {soma(rr, 'tp')} | {soma(rr, 'fp')} | {soma(rr, 'fn')} |")

    # 3. intenção
    conf = Counter()
    for ex, o in zip(todos, ouros):
        p = descartando(lora[ex["id"]])
        conf[(getattr(o.intent, "value", o.intent), getattr(p.intent, "value", p.intent) if p else "inválida")] += 1
    out += ["", "## 3. Intenção: o que era x o que o modelo respondeu", "", "| Era | Modelo respondeu | Mensagens |",
            "|---|---|---|"]
    out += [f"| {g} | {p} | {n} |" for (g, p), n in sorted(conf.items(), key=lambda kv: -kv[1])]

    # 4. variações posteriores
    sistemas = [("Regras", lambda ex: estrito(regras[ex["id"]])),
                ("Modelo (oficial)", lambda ex: estrito(lora[ex["id"]])),
                ("Modelo, descartando valores inválidos", lambda ex: descartando(lora[ex["id"]])),
                ("Híbrido: intenção do modelo + campos das regras", lambda ex: hibrido(lora[ex["id"]], regras[ex["id"]]))]
    out += ["", "## 4. Análise posterior (não é resultado oficial)", "",
            "As duas últimas colunas foram desenhadas depois de ver os erros no teste. Elas indicam o que "
            "experimentar em seguida; para valerem como resultado, precisam ser medidas em frases novas.", "",
            "| Acerto exato | " + " | ".join(n for n, _ in sistemas) + " |", "|---|" + "---|" * len(sistemas)]
    tot = {n: Counter() for n, _ in sistemas}
    for nome, exs in teste.items():
        o = [Pedido.model_validate(ex["rotulo"]) for ex in exs]
        linha = [f"{nome} (n={len(exs)})"]
        for n, f in sistemas:
            r = avaliar(o, [f(ex) for ex in exs])
            linha.append(pct(r["exato"]))
            for k, kn in [("restricoes_completas", "restricoes_completas_n"), ("alerta_saude_recall", "alerta_saude_n"),
                          ("inventou_em_vazios", "vazios_n")]:
                if r[kn]:
                    tot[n][k] += round(r[k] * r[kn]); tot[n][kn] += r[kn]
            for it in ("emergencia", "ataque"):
                tot[n][it] += r["intent"][it]["acertos"]; tot[n][it + "_n"] += r["intent"][it]["suporte"]
        out.append("| " + " | ".join(linha) + " |")
    out += ["", "| Todos os conjuntos somados | " + " | ".join(n for n, _ in sistemas) + " |",
            "|---|" + "---|" * len(sistemas)]
    for rot, k, kn in [("Restrições completas", "restricoes_completas", "restricoes_completas_n"),
                       ("Alerta de saúde", "alerta_saude_recall", "alerta_saude_n"),
                       ("Inventou campos em pedido vazio", "inventou_em_vazios", "vazios_n"),
                       ("Emergência detectada", "emergencia", "emergencia_n"), ("Ataque detectado", "ataque", "ataque_n")]:
        out.append(f"| {rot} | " + " | ".join(f"{tot[n][k]}/{tot[n][kn]}" for n, _ in sistemas) + " |")

    (RAIZ / "results" / "error_analysis.md").write_text("\n".join(out) + "\n", encoding="utf8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
