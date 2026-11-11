"""Sistema híbrido: o modelo ajustado decide a intenção; nos pedidos, as regras extraem os campos.

Desenhado em 11/11/2026 a partir da análise de erros no teste principal (results/error_analysis.md)
e registrado em PREREGISTRATION.md antes de ser avaliado no conjunto novo (test_fresh_llm.jsonl).
Não alterar depois dessa avaliação.
"""

import json

from order_parser.output_format import de_json
from order_parser.schema import Categoria, Desejo, Pedido, Restricao

_ENUMS = {"categories": Categoria, "exclude_categories": Categoria, "restrictions": Restricao,
          "partial_restrictions": Restricao, "wishes": Desejo}


def estrito(saida: str) -> Pedido | None:
    """Leitura oficial: qualquer valor fora do schema invalida a saída inteira."""
    try:
        return de_json(saida)
    except Exception:
        return None


def descartando(saida: str) -> Pedido | None:
    """Descarta chaves e valores fora do schema em vez de rejeitar a saída inteira."""
    try:
        dados, _ = json.JSONDecoder().raw_decode(saida[saida.find("{"):])
    except Exception:
        return None
    if not isinstance(dados, dict):
        return None
    limpo = {}
    for k, v in dados.items():
        if k not in Pedido.model_fields or v is None:
            continue
        if k in _ENUMS and isinstance(v, list):
            permitidos = {e.value for e in _ENUMS[k]}
            v = [x for x in v if x in permitidos]
        limpo[k] = v
    if limpo.get("intent", "pedido") != "pedido":
        limpo = {"intent": limpo["intent"]}
    try:
        return Pedido.model_validate(limpo)
    except Exception:
        return None


def hibrido(saida_modelo: str, pedido_regras: Pedido) -> Pedido:
    """Se o modelo ou as regras disserem que não é pedido, vale a resposta do modelo.

    Se os dois disserem que é pedido, valem os campos extraídos pelas regras.
    Se a saída do modelo for ilegível, vale a resposta das regras.
    """
    m = descartando(saida_modelo)
    if m is None:
        return pedido_regras
    if m.intent != "pedido" or pedido_regras.intent != "pedido":
        return m
    return pedido_regras
