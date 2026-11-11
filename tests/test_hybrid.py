from order_parser.hybrid import descartando, hibrido
from order_parser.schema import Pedido

REGRAS = Pedido(categories=["pizza"], exclude_ingredients=["cebola"])


def test_modelo_decide_quando_nao_e_pedido():
    assert hibrido('{"intent":"emergencia"}', REGRAS).intent == "emergencia"


def test_regras_extraem_quando_os_dois_dizem_pedido():
    assert hibrido('{"categories":["hamburguer"],"wishes":["farto"]}', REGRAS) == REGRAS


def test_saida_ilegivel_cai_nas_regras():
    assert hibrido("não sei", REGRAS) == REGRAS


def test_descartando_remove_valores_fora_do_schema():
    p = descartando('{"categories":["acai","frutas"],"payment_method":"pix"}')
    assert p.categories == ["acai"]
