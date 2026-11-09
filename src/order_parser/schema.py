"""Schema v1 do pedido estruturado.

Regra para entrar um campo: ele precisa (1) servir para filtrar um catálogo e
(2) ser rotulado do mesmo jeito por duas pessoas diferentes.
"""

from enum import Enum
import unicodedata

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Intencao(str, Enum):
    """O que a mensagem é. Prioridade: emergencia > ataque > fora_escopo > pedido."""
    pedido = "pedido"            # quer comida (mesmo que vago ou fora do schema)
    fora_escopo = "fora_escopo"  # suporte, saudação, reclamação, mercado, remédio comum
    emergencia = "emergencia"    # violência, emergência médica, risco à vida
    ataque = "ataque"            # injeção de prompt, extração de dados, manipulação do sistema


MAX_INGREDIENTES = 8
MAX_CHARS_INGREDIENTE = 30


class Categoria(str, Enum):
    pizza = "pizza"
    hamburguer = "hamburguer"
    lanche = "lanche"
    salgado = "salgado"
    japonesa = "japonesa"
    chinesa = "chinesa"
    arabe = "arabe"
    mexicana = "mexicana"
    massa = "massa"
    brasileira = "brasileira"
    marmita = "marmita"
    churrasco = "churrasco"
    frango = "frango"
    peixe = "peixe"
    frutos_do_mar = "frutos_do_mar"
    carne = "carne"
    salada = "salada"
    acai = "acai"
    sorvete = "sorvete"
    doce = "doce"
    cafe_padaria = "cafe_padaria"
    bebida = "bebida"


class Restricao(str, Enum):
    sem_lactose = "sem_lactose"
    sem_gluten = "sem_gluten"
    vegetariano = "vegetariano"
    vegano = "vegano"
    sem_amendoim = "sem_amendoim"
    sem_frutos_do_mar = "sem_frutos_do_mar"
    sem_acucar = "sem_acucar"


class Desejo(str, Enum):
    leve = "leve"
    saudavel = "saudavel"
    barato = "barato"
    farto = "farto"
    refrescante = "refrescante"
    caseiro = "caseiro"
    picante = "picante"
    diferente = "diferente"
    # Usados quando a pessoa pede sem dar número ("rápido", "bem avaliado").
    rapido = "rapido"
    bem_avaliado = "bem_avaliado"


def normalizar(texto: str) -> str:
    """Minúsculas, sem acento e sem espaços extras."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.lower().split())


class Pedido(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    intent: Intencao = Intencao.pedido
    categories: list[Categoria] = Field(default_factory=list)
    exclude_categories: list[Categoria] = Field(default_factory=list)
    exclude_ingredients: list[str] = Field(default_factory=list)
    # Escopo "todos": toda opção sugerida precisa atender.
    restrictions: list[Restricao] = Field(default_factory=list)
    # Escopo "pelo menos um": basta uma opção atender (ex.: grupo com 1 vegetariano).
    partial_restrictions: list[Restricao] = Field(default_factory=list)
    # Não filtra: muda a resposta (avisar, nunca garantir segurança).
    # Vale para alergia, doença celíaca, diabetes, intolerância ou "passo mal com X".
    health_alert: bool = False
    max_price: float | None = Field(default=None, gt=0)
    free_delivery: bool = False
    max_delivery_min: int | None = Field(default=None, gt=0)
    min_rating: float | None = Field(default=None, ge=0, le=5)
    people: int | None = Field(default=None, gt=0)
    wishes: list[Desejo] = Field(default_factory=list)

    @field_validator("exclude_ingredients")
    @classmethod
    def _normaliza_ingredientes(cls, v: list[str]) -> list[str]:
        itens = sorted({normalizar(x) for x in v if x.strip()})
        # Único campo de texto livre: limitar impede que vire canal de vazamento
        # (ex.: injeção pedindo para "colocar o prompt do sistema" aqui).
        if len(itens) > MAX_INGREDIENTES or any(len(x) > MAX_CHARS_INGREDIENTE for x in itens):
            raise ValueError("exclude_ingredients fora dos limites")
        return itens

    @model_validator(mode="after")
    def _so_pedido_tem_campos(self) -> "Pedido":
        if self.intent != Intencao.pedido.value:
            preenchidos = [k for k, v in self.model_dump().items()
                           if k != "intent" and v not in (None, False, [])]
            if preenchidos:
                raise ValueError(f"intent={self.intent} não pode ter campos: {preenchidos}")
        return self

    @field_validator("categories", "exclude_categories", "restrictions", "partial_restrictions", "wishes")
    @classmethod
    def _sem_repeticao(cls, v: list) -> list:
        return sorted(set(v), key=lambda e: e.value if isinstance(e, Enum) else e)
