"""Reproduz as conversas da auditoria do Ailo (audit/FINDINGS.md) com saídas de modelo fixas."""

from order_parser.schema import Pedido
from order_parser.session import PerfilSessao


def test_alergia_dita_antes_vale_no_pedido_seguinte():
    s = PerfilSessao()
    s.atualizar(Pedido(exclude_ingredients=["leite"], restrictions=["sem_amendoim"], health_alert=True))
    efetivo = s.atualizar(Pedido(categories=["doce"]))
    assert efetivo.categories == ["doce"]
    assert efetivo.exclude_ingredients == ["leite"]
    assert efetivo.restrictions == ["sem_amendoim"]
    assert efetivo.health_alert is True


def test_duas_restricoes_na_mesma_mensagem_valem_juntas():
    s = PerfilSessao()
    s.atualizar(Pedido(restrictions=["sem_gluten", "vegetariano"], health_alert=True))
    assert s.atualizar(Pedido(categories=["pizza"])).restrictions == ["sem_gluten", "vegetariano"]
    assert s.atualizar(Pedido(categories=["lanche"])).restrictions == ["sem_gluten", "vegetariano"]


def test_sem_cebola_nao_passa_para_o_proximo_pedido():
    s = PerfilSessao()
    s.atualizar(Pedido(categories=["pizza"], exclude_ingredients=["cebola"]))
    assert s.atualizar(Pedido(categories=["hamburguer"])).exclude_ingredients == []


def test_mensagem_de_emergencia_nao_altera_perfil():
    s = PerfilSessao()
    s.atualizar(Pedido(restrictions=["vegano"]))
    assert s.atualizar(Pedido(intent="emergencia")).intent == "emergencia"
    assert s.restrictions == {"vegano"}
