"""O filtro nunca sugere um item que viola uma restrição, incluindo as conversas da auditoria do Ailo."""
import itertools

from order_parser.catalog import CATALOGO, atende, recomendar, violacoes
from order_parser.schema import Pedido, Restricao
from order_parser.session import PerfilSessao


def test_alergia_a_amendoim_depois_doce():
    s = PerfilSessao()
    s.atualizar(Pedido(restrictions=["sem_amendoim"], health_alert=True))
    p = s.atualizar(Pedido(categories=["doce"]))
    r = recomendar(p)
    assert r.itens and not violacoes(p, r.itens) and r.avisos
    assert all("amendoim" not in it.contem for it in r.itens)


def test_alergia_a_leite_nao_recebe_brigadeiro_nem_pudim():
    s = PerfilSessao()
    s.atualizar(Pedido(exclude_ingredients=["leite"], restrictions=["sem_amendoim"], health_alert=True))
    p = s.atualizar(Pedido(categories=["doce"]))
    r = recomendar(p)
    assert r.itens and not violacoes(p, r.itens)
    assert all("leite" not in " ".join(it.ingredientes) and "lactose" not in it.contem for it in r.itens)
    # queijo não tem a palavra "leite", mas é laticínio: pizza de mussarela não pode aparecer
    pizzas = recomendar(s.atualizar(Pedido(categories=["pizza"])), n=10).itens
    assert pizzas and all("lactose" not in it.contem for it in pizzas)


def test_celiaca_e_vegetariana_pizza_e_lanche():
    s = PerfilSessao()
    s.atualizar(Pedido(restrictions=["sem_gluten", "vegetariano"], health_alert=True))
    for cat in ["pizza", "lanche"]:
        p = s.atualizar(Pedido(categories=[cat]))
        r = recomendar(p)
        assert r.itens, cat
        assert all(it.vegetariano and "gluten" not in it.contem for it in r.itens)


def test_conflito_nao_sugere_nada():
    r = recomendar(Pedido(categories=["churrasco"], restrictions=["vegano"]))
    assert r.itens == [] and "Não encontrei" in r.texto


def test_restricao_parcial_garante_pelo_menos_uma_opcao():
    p = Pedido(categories=["pizza"], people=2, partial_restrictions=["vegano"])
    assert any(it.vegano for it in recomendar(p).itens)


def test_emergencia_recebe_resposta_fixa():
    r = recomendar(Pedido(intent="emergencia"))
    assert "192" in r.texto and r.itens == []


def test_nenhuma_combinacao_de_restricoes_gera_violacao():
    todas = [x.value for x in Restricao]
    for k in (1, 2, 3):
        for combo in itertools.combinations(todas, k):
            p = Pedido(restrictions=list(combo))
            assert not violacoes(p, recomendar(p, n=10).itens), combo


def test_catalogo_coerente():
    for it in CATALOGO:
        assert not (it.vegano and not it.vegetariano)
        assert not (it.vegano and "lactose" in it.contem), it.nome
