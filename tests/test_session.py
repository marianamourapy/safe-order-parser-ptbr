"""Reproduz as conversas da auditoria do Ailo (audit/FINDINGS.md) com saídas de modelo fixas."""

from order_parser.schema import Pedido
from order_parser.session import PerfilSessao


def test_alergia_dita_antes_vale_no_pedido_seguinte():
    s = PerfilSessao()
    s.atualizar(Pedido(excluir_ingredientes=["leite"], restricoes=["sem_amendoim"], alerta_saude=True))
    efetivo = s.atualizar(Pedido(categorias=["doce"]))
    assert efetivo.categorias == ["doce"]
    assert efetivo.excluir_ingredientes == ["leite"]
    assert efetivo.restricoes == ["sem_amendoim"]
    assert efetivo.alerta_saude is True


def test_duas_restricoes_na_mesma_mensagem_valem_juntas():
    s = PerfilSessao()
    s.atualizar(Pedido(restricoes=["sem_gluten", "vegetariano"], alerta_saude=True))
    assert s.atualizar(Pedido(categorias=["pizza"])).restricoes == ["sem_gluten", "vegetariano"]
    assert s.atualizar(Pedido(categorias=["lanche"])).restricoes == ["sem_gluten", "vegetariano"]


def test_sem_cebola_nao_passa_para_o_proximo_pedido():
    s = PerfilSessao()
    s.atualizar(Pedido(categorias=["pizza"], excluir_ingredientes=["cebola"]))
    assert s.atualizar(Pedido(categorias=["hamburguer"])).excluir_ingredientes == []


def test_mensagem_de_emergencia_nao_altera_perfil():
    s = PerfilSessao()
    s.atualizar(Pedido(restricoes=["vegano"]))
    assert s.atualizar(Pedido(intencao="emergencia")).intencao == "emergencia"
    assert s.restricoes == {"vegano"}
