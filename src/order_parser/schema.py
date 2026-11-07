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

    intencao: Intencao = Intencao.pedido
    categorias: list[Categoria] = Field(default_factory=list)
    excluir_categorias: list[Categoria] = Field(default_factory=list)
    excluir_ingredientes: list[str] = Field(default_factory=list)
    # Escopo "todos": toda opção sugerida precisa atender.
    restricoes: list[Restricao] = Field(default_factory=list)
    # Escopo "pelo menos um": basta uma opção atender (ex.: grupo com 1 vegetariano).
    restricoes_parciais: list[Restricao] = Field(default_factory=list)
    # Não filtra: muda a resposta (avisar, nunca garantir segurança).
    # Vale para alergia, doença celíaca, diabetes, intolerância ou "passo mal com X".
    alerta_saude: bool = False
    preco_max: float | None = Field(default=None, gt=0)
    frete_gratis: bool = False
    tempo_max_min: int | None = Field(default=None, gt=0)
    nota_min: float | None = Field(default=None, ge=0, le=5)
    pessoas: int | None = Field(default=None, gt=0)
    desejos: list[Desejo] = Field(default_factory=list)

    @field_validator("excluir_ingredientes")
    @classmethod
    def _normaliza_ingredientes(cls, v: list[str]) -> list[str]:
        itens = sorted({normalizar(x) for x in v if x.strip()})
        # Único campo de texto livre: limitar impede que vire canal de vazamento
        # (ex.: injeção pedindo para "colocar o prompt do sistema" aqui).
        if len(itens) > MAX_INGREDIENTES or any(len(x) > MAX_CHARS_INGREDIENTE for x in itens):
            raise ValueError("excluir_ingredientes fora dos limites")
        return itens

    @model_validator(mode="after")
    def _so_pedido_tem_campos(self) -> "Pedido":
        if self.intencao != Intencao.pedido.value:
            preenchidos = [k for k, v in self.model_dump().items()
                           if k != "intencao" and v not in (None, False, [])]
            if preenchidos:
                raise ValueError(f"intencao={self.intencao} não pode ter campos: {preenchidos}")
        return self

    @field_validator("categorias", "excluir_categorias", "restricoes", "restricoes_parciais", "desejos")
    @classmethod
    def _sem_repeticao(cls, v: list) -> list:
        return sorted(set(v), key=lambda e: e.value if isinstance(e, Enum) else e)
