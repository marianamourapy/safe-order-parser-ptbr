"""Perfil da sessão: guarda restrições de uma mensagem para a outra.

O modelo lê uma mensagem por vez, sem memória. Quem lembra é o sistema:
cada saída do modelo atualiza o perfil, e o pedido efetivo de cada mensagem
é o pedido dela somado ao perfil.

O que fica guardado:
- restrições de quem fala ("sou vegetariana", "sou celíaca"), sempre;
- ingredientes excluídos, só quando há alerta de saúde ("alergia a leite");
- o próprio alerta de saúde.
"Sem cebola" num pedido específico NÃO fica guardado para o próximo pedido.
"""

from dataclasses import dataclass, field

from order_parser.schema import Intencao, Pedido


@dataclass
class PerfilSessao:
    restricoes: set[str] = field(default_factory=set)
    excluir_ingredientes: set[str] = field(default_factory=set)
    alerta_saude: bool = False

    def atualizar(self, p: Pedido) -> Pedido:
        """Registra o que deve persistir e devolve o pedido efetivo desta mensagem."""
        if p.intencao != Intencao.pedido.value:
            return p
        self.restricoes |= set(p.restricoes)
        if p.alerta_saude:
            self.alerta_saude = True
            self.excluir_ingredientes |= set(p.excluir_ingredientes)
        d = p.model_dump()
        d["restricoes"] = sorted(self.restricoes | set(p.restricoes))
        d["excluir_ingredientes"] = sorted(self.excluir_ingredientes | set(p.excluir_ingredientes))
        d["alerta_saude"] = self.alerta_saude or p.alerta_saude
        return Pedido.model_validate(d)

    def limpar(self) -> None:
        self.restricoes.clear()
        self.excluir_ingredientes.clear()
        self.alerta_saude = False
