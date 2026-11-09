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
    restrictions: set[str] = field(default_factory=set)
    exclude_ingredients: set[str] = field(default_factory=set)
    health_alert: bool = False

    def atualizar(self, p: Pedido) -> Pedido:
        """Registra o que deve persistir e devolve o pedido efetivo desta mensagem."""
        if p.intent != Intencao.pedido.value:
            return p
        self.restrictions |= set(p.restrictions)
        if p.health_alert:
            self.health_alert = True
            self.exclude_ingredients |= set(p.exclude_ingredients)
        d = p.model_dump()
        d["restrictions"] = sorted(self.restrictions | set(p.restrictions))
        d["exclude_ingredients"] = sorted(self.exclude_ingredients | set(p.exclude_ingredients))
        d["health_alert"] = self.health_alert or p.health_alert
        return Pedido.model_validate(d)

    def limpar(self) -> None:
        self.restrictions.clear()
        self.exclude_ingredients.clear()
        self.health_alert = False
