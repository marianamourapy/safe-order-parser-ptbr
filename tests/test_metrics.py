import pytest

from order_parser.metrics import avaliar, wilson
from order_parser.schema import Pedido


def test_wilson_contem_a_proporcao_e_estreita_com_n():
    lo, hi = wilson(7, 8)
    assert lo < 7 / 8 < hi
    assert (hi - lo) > (wilson(70, 80)[1] - wilson(70, 80)[0])


def test_previsao_perfeita():
    ouros = [Pedido(categories=["pizza"], max_price=40), Pedido(intent="emergencia")]
    r = avaliar(ouros, list(ouros))
    assert r["exato"] == 1 and r["micro_f1"] == 1 and r["intent"]["emergencia"]["recall"] == 1


def test_json_invalido_conta_como_vazio():
    r = avaliar([Pedido(categories=["pizza"])], [None])
    assert r["json_valido"] == 0 and r["campos"]["categories"]["fn"] == 1


def test_valor_errado_e_fp_e_fn():
    r = avaliar([Pedido(max_price=40)], [Pedido(max_price=50)])
    assert (r["campos"]["max_price"]["tp"], r["campos"]["max_price"]["fp"], r["campos"]["max_price"]["fn"]) == (0, 1, 1)


def test_restricao_incompleta_conta_como_erro():
    # O caso do Ailo: "celíaca e vegetariana", e só uma foi considerada.
    r = avaliar([Pedido(restrictions=["sem_gluten", "vegetariano"], health_alert=True)],
                [Pedido(restrictions=["sem_gluten"], health_alert=True)])
    assert r["restricoes_completas"] == 0 and r["multi_restricoes_completas"] == 0


def test_emergencia_nao_detectada_derruba_recall():
    r = avaliar([Pedido(intent="emergencia")] * 4, [Pedido(intent="emergencia")] * 3 + [Pedido()])
    assert r["intent"]["emergencia"]["recall"] == pytest.approx(0.75)
