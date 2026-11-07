"""Formato de entrada e saída do modelo.

A saída é JSON compacto e esparso: só os campos preenchidos, sem espaços.
Menos tokens de saída = geração mais rápida e barata, e menos lugares para errar.
"""

import json

from order_parser.schema import Categoria, Desejo, Intencao, Pedido, Restricao

_vals = lambda e: "|".join(x.value for x in e)  # noqa: E731

SISTEMA = (
    "Converta a mensagem de um cliente de delivery em JSON. Responda só com o JSON, "
    "compacto, omitindo campos vazios ou falsos. Não invente o que a pessoa não disse.\n"
    f"intencao: {_vals(Intencao)} (omita se pedido; se não for pedido, nenhum outro campo)\n"
    f"categorias, excluir_categorias: lista de {_vals(Categoria)}\n"
    "excluir_ingredientes: lista de ingredientes curtos\n"
    f"restricoes (todas as opções), restricoes_parciais (pelo menos uma): lista de {_vals(Restricao)}\n"
    "alerta_saude: true se citar alergia, doença ou condição de saúde\n"
    "preco_max (reais, total), tempo_max_min (minutos), nota_min (0 a 5), pessoas: números\n"
    "frete_gratis: true se pedir entrega grátis\n"
    f"desejos: lista de {_vals(Desejo)}"
)

_ORDEM = list(Pedido.model_fields)


def para_json(p: Pedido) -> str:
    d = p.model_dump()
    saida = {}
    for k in _ORDEM:
        v = d[k]
        if k == "intencao" and v == Intencao.pedido.value:
            continue
        if v in (None, False, []):
            continue
        if isinstance(v, float) and v.is_integer():
            v = int(v)
        saida[k] = v
    return json.dumps(saida, ensure_ascii=False, separators=(",", ":"))


def de_json(texto: str) -> Pedido:
    """Lê a saída do modelo. Levanta erro se não for JSON válido no schema."""
    texto = texto.strip()
    if texto.startswith("```"):
        texto = texto.strip("`").removeprefix("json").strip()
    return Pedido.model_validate(json.loads(texto))


def mensagens(texto: str, rotulo: Pedido | None = None) -> list[dict]:
    m = [{"role": "system", "content": SISTEMA}, {"role": "user", "content": texto}]
    if rotulo is not None:
        m.append({"role": "assistant", "content": para_json(rotulo)})
    return m
