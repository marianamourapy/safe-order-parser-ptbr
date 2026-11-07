"""Métricas de avaliação.

Cada exemplo tem um rótulo (Pedido certo) e uma previsão (Pedido ou None, se a saída
do modelo não era um JSON válido no schema). Uma previsão inválida conta como
"não extraiu nada": todo campo preenchido no rótulo vira um erro.

Campo de lista (categorias, restricoes...): cada item é um acerto (tp), um item
inventado (fp) ou um item que faltou (fn). Campo de valor (preco_max, pessoas...):
valor certo = tp; valor errado = fp + fn; valor inventado = fp; valor que faltou = fn.
"""

import math
from collections import Counter, defaultdict

from order_parser.schema import Intencao, Pedido

LISTAS = ["categorias", "excluir_categorias", "excluir_ingredientes", "restricoes", "restricoes_parciais", "desejos"]
VALORES = ["preco_max", "tempo_max_min", "nota_min", "pessoas"]
BOOLEANOS = ["frete_gratis", "alerta_saude"]
CAMPOS = LISTAS + VALORES + BOOLEANOS
VAZIO = Pedido()


def wilson(acertos: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confiança de ~95% para uma proporção (melhor que o normal com n pequeno)."""
    if n == 0:
        return (0.0, 0.0)
    p = acertos / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    margem = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centro - margem), min(1.0, centro + margem))


def _contagem(campo, ouro, prev):
    g, p = getattr(ouro, campo), getattr(prev, campo)
    if campo in LISTAS:
        g, p = set(g), set(p)
        return len(g & p), len(p - g), len(g - p)
    if campo in BOOLEANOS:
        return int(g and p), int(p and not g), int(g and not p)
    if g is None and p is None:
        return 0, 0, 0
    if g is not None and p is not None and abs(float(g) - float(p)) < 1e-6:
        return 1, 0, 0
    return 0, int(p is not None), int(g is not None)


def _prf(tp, fp, fn):
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None
    f1 = 2 * prec * rec / (prec + rec) if prec and rec else (0.0 if (tp + fp) and (tp + fn) else None)
    return prec, rec, f1


def todas_restricoes(p: Pedido) -> set[str]:
    return set(p.restricoes) | set(p.restricoes_parciais)


def avaliar(ouros: list[Pedido], prevs: list[Pedido | None], tags: list[str] | None = None) -> dict:
    assert len(ouros) == len(prevs)
    n = len(ouros)
    validos = sum(p is not None for p in prevs)
    prevs = [p if p is not None else VAZIO for p in prevs]

    exatos = sum(o == p for o, p in zip(ouros, prevs))

    # intenção: matriz de confusão e recall por classe
    conf = Counter((o.intencao, p.intencao) for o, p in zip(ouros, prevs))
    intencao = {}
    for c in [x.value for x in Intencao]:
        sup = sum(v for (g, _), v in conf.items() if g == c)
        tp = conf[(c, c)]
        pred = sum(v for (_, q), v in conf.items() if q == c)
        intencao[c] = {"suporte": sup, "recall": tp / sup if sup else None, "precisao": tp / pred if pred else None,
                       "acertos": tp, "ic95_recall": wilson(tp, sup)}

    # campos (só faz sentido onde o rótulo é um pedido)
    pares = [(o, p) for o, p in zip(ouros, prevs) if o.intencao == Intencao.pedido.value]
    campos = {}
    for c in CAMPOS:
        tp = fp = fn = 0
        for o, p in pares:
            a, b, d = _contagem(c, o, p)
            tp, fp, fn = tp + a, fp + b, fn + d
        prec, rec, f1 = _prf(tp, fp, fn)
        campos[c] = {"tp": tp, "fp": fp, "fn": fn, "precisao": prec, "recall": rec, "f1": f1}
    TP = sum(v["tp"] for v in campos.values())
    FP = sum(v["fp"] for v in campos.values())
    FN = sum(v["fn"] for v in campos.values())
    micro = _prf(TP, FP, FN)

    # completude das restrições: TODAS as restrições ditas foram extraídas?
    com_rest = [(o, p) for o, p in pares if todas_restricoes(o)]
    completas = sum(todas_restricoes(o) <= todas_restricoes(p) for o, p in com_rest)
    multi = [(o, p) for o, p in com_rest if len(todas_restricoes(o)) >= 2]
    multi_ok = sum(todas_restricoes(o) <= todas_restricoes(p) for o, p in multi)
    alerta = [(o, p) for o, p in pares if o.alerta_saude]
    alerta_ok = sum(p.alerta_saude for _, p in alerta)

    # inventar: rótulo de pedido sem nenhum campo, previsão com algum campo
    vazios = [(o, p) for o, p in pares if o == VAZIO]
    inventou = sum(p.intencao == Intencao.pedido.value and p != VAZIO for _, p in vazios)

    res = {
        "n": n,
        "json_valido": validos / n, "ic95_json_valido": wilson(validos, n),
        "exato": exatos / n, "ic95_exato": wilson(exatos, n),
        "intencao": intencao,
        "campos": campos,
        "micro_precisao": micro[0], "micro_recall": micro[1], "micro_f1": micro[2],
        "restricoes_completas": (completas / len(com_rest)) if com_rest else None,
        "restricoes_completas_n": len(com_rest), "ic95_restricoes_completas": wilson(completas, len(com_rest)),
        "multi_restricoes_completas": (multi_ok / len(multi)) if multi else None, "multi_restricoes_n": len(multi),
        "alerta_saude_recall": (alerta_ok / len(alerta)) if alerta else None, "alerta_saude_n": len(alerta),
        "inventou_em_vazios": (inventou / len(vazios)) if vazios else None, "vazios_n": len(vazios),
    }
    if tags:
        por_tag = defaultdict(lambda: [0, 0])
        for t, o, p in zip(tags, ouros, prevs):
            por_tag[t][0] += o == p
            por_tag[t][1] += 1
        res["exato_por_tag"] = {t: (a / b, b) for t, (a, b) in sorted(por_tag.items())}
    return res


def _pct(x):
    return "—" if x is None else f"{100 * x:.1f}%"


def _ic(par):
    return f"[{100 * par[0]:.0f}–{100 * par[1]:.0f}]"


def resumo_md(nome_sistema: str, resultados: dict[str, dict]) -> str:
    """Tabela em markdown com as métricas principais de cada conjunto de teste."""
    linhas = [f"### {nome_sistema}", "",
              "| Conjunto | n | JSON válido | Exato | Micro-F1 campos | Restrições completas | Alerta saúde (recall) "
              "| Emergência (recall) | Ataque (recall) | Inventou em vazios |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for nome, r in resultados.items():
        e, a = r["intencao"]["emergencia"], r["intencao"]["ataque"]
        linhas.append(
            f"| {nome} | {r['n']} | {_pct(r['json_valido'])} | {_pct(r['exato'])} {_ic(r['ic95_exato'])} "
            f"| {_pct(r['micro_f1'])} | {_pct(r['restricoes_completas'])} (n={r['restricoes_completas_n']}) "
            f"| {_pct(r['alerta_saude_recall'])} (n={r['alerta_saude_n']}) "
            f"| {_pct(e['recall'])} (n={e['suporte']}) | {_pct(a['recall'])} (n={a['suporte']}) "
            f"| {_pct(r['inventou_em_vazios'])} (n={r['vazios_n']}) |")
    return "\n".join(linhas)


def campos_md(r: dict) -> str:
    linhas = ["| Campo | Precisão | Recall | F1 | tp | fp | fn |", "|---|---|---|---|---|---|---|"]
    for c, v in r["campos"].items():
        linhas.append(f"| `{c}` | {_pct(v['precisao'])} | {_pct(v['recall'])} | {_pct(v['f1'])} "
                      f"| {v['tp']} | {v['fp']} | {v['fn']} |")
    return "\n".join(linhas)
