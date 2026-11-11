"""Catálogo SINTÉTICO e filtro de recomendações.

Todos os restaurantes e pratos são fictícios. O catálogo existe para demonstrar a ideia
central do projeto: uma restrição alimentar extraída pelo modelo vira um FILTRO obrigatório
sobre os candidatos, e não só um aviso no texto da resposta.
"""

from dataclasses import dataclass, field

from order_parser.schema import Intencao, Pedido, normalizar


@dataclass(frozen=True)
class Restaurante:
    nome: str
    nota: float
    frete: float
    tempo_min: int


@dataclass(frozen=True)
class Item:
    nome: str
    categoria: str
    preco: float
    ingredientes: tuple[str, ...]
    restaurante: Restaurante
    contem: frozenset[str] = frozenset()   # gluten, lactose, amendoim, frutos_do_mar, acucar
    vegetariano: bool = False
    vegano: bool = False
    frito: bool = False
    tags: frozenset[str] = frozenset()     # leve, saudavel, farto, refrescante, caseiro, picante, diferente


R = {
    "cantina": Restaurante("Cantina Fictícia", 4.7, 0.0, 40),
    "forno": Restaurante("Forno de Mentira", 4.5, 5.99, 35),
    "brasa": Restaurante("Brasa Inventada", 4.3, 6.99, 30),
    "verde": Restaurante("Verde Imaginário", 4.8, 4.99, 25),
    "sakura": Restaurante("Sakura de Faz de Conta", 4.6, 7.99, 45),
    "doceria": Restaurante("Doceria Hipotética", 4.9, 3.99, 20),
    "vovo": Restaurante("Panela da Vó Fictícia", 4.4, 0.0, 50),
    "esquina": Restaurante("Lanches da Esquina Inexistente", 4.1, 2.99, 15),
}


def _i(nome, cat, preco, ing, rest, contem="", veg=False, vegano=False, frito=False, tags=""):
    return Item(nome, cat, preco, tuple(ing.split(", ")), R[rest], frozenset(contem.split()),
                veg or vegano, vegano, frito, frozenset(tags.split()))


CATALOGO = [
    _i("Pizza marguerita", "pizza", 42, "massa de trigo, molho de tomate, mussarela, manjericão", "forno", "gluten lactose", veg=True),
    _i("Pizza calabresa", "pizza", 45, "massa de trigo, molho de tomate, mussarela, calabresa, cebola", "forno", "gluten lactose"),
    _i("Pizza frango com requeijão", "pizza", 48, "massa de trigo, frango, requeijão, milho", "forno", "gluten lactose"),
    _i("Pizza marguerita sem glúten", "pizza", 52, "massa de mandioca, molho de tomate, mussarela, manjericão", "verde", "lactose", veg=True),
    _i("Pizza vegana de legumes sem glúten", "pizza", 54, "massa de mandioca, molho de tomate, abobrinha, berinjela", "verde", vegano=True, tags="leve saudavel"),
    _i("Pizza doce de brigadeiro", "pizza", 44, "massa de trigo, chocolate, leite condensado", "forno", "gluten lactose acucar", veg=True),
    _i("X-burguer", "hamburguer", 24, "pão, carne bovina, queijo, maionese", "esquina", "gluten lactose"),
    _i("X-tudo", "hamburguer", 32, "pão, carne bovina, queijo, bacon, ovo, alface, tomate, cebola", "esquina", "gluten lactose", tags="farto"),
    _i("Hambúrguer de grão-de-bico", "hamburguer", 30, "pão, grão-de-bico, alface, tomate", "verde", "gluten", vegano=True),
    _i("Hambúrguer vegetal no pão sem glúten", "hamburguer", 36, "pão de arroz, lentilha, alface, tomate", "verde", vegano=True, tags="saudavel"),
    _i("Cachorro-quente completo", "lanche", 18, "pão, salsicha, purê de batata, milho, batata palha", "esquina", "gluten lactose", tags="farto"),
    _i("Sanduíche natural de frango", "lanche", 19, "pão integral, frango, cenoura, requeijão", "esquina", "gluten lactose", tags="leve"),
    _i("Wrap de falafel sem glúten", "lanche", 27, "tapioca, falafel, alface, tomate, tahine", "verde", vegano=True, tags="leve saudavel"),
    _i("Coxinha de frango", "salgado", 8, "massa de trigo, frango, requeijão", "esquina", "gluten lactose", frito=True),
    _i("Pastel de queijo", "salgado", 9, "massa de trigo, queijo", "esquina", "gluten lactose", veg=True, frito=True),
    _i("Empada de camarão", "salgado", 11, "massa de trigo, camarão, manteiga", "esquina", "gluten lactose frutos_do_mar"),
    _i("Combinado de sushi", "japonesa", 68, "arroz, salmão, atum, camarão, cream cheese", "sakura", "lactose frutos_do_mar"),
    _i("Sushi vegetariano", "japonesa", 46, "arroz, pepino, manga, cenoura", "sakura", vegano=True, tags="leve"),
    _i("Temaki de salmão", "japonesa", 29, "arroz, salmão, cebolinha", "sakura", tags="leve"),
    _i("Yakisoba misto", "chinesa", 38, "macarrão de trigo, carne bovina, frango, camarão, legumes, shoyu", "sakura", "gluten frutos_do_mar"),
    _i("Yakisoba de legumes", "chinesa", 34, "macarrão de trigo, brócolis, cenoura, repolho, shoyu", "sakura", "gluten", vegano=True),
    _i("Frango xadrez", "chinesa", 39, "frango, pimentão, cebola, amendoim, shoyu", "sakura", "gluten amendoim"),
    _i("Esfiha de carne", "arabe", 7, "massa de trigo, carne bovina, cebola, tomate", "brasa", "gluten"),
    _i("Esfiha de verdura", "arabe", 7, "massa de trigo, escarola, cebola", "brasa", "gluten", vegano=True),
    _i("Tacos de carne", "mexicana", 36, "tortilha de milho, carne bovina, queijo, pimenta, coentro", "brasa", "lactose", tags="picante diferente"),
    _i("Burrito de feijão", "mexicana", 33, "tortilha de trigo, feijão, arroz, guacamole, pimenta", "brasa", "gluten", vegano=True, tags="picante diferente"),
    _i("Lasanha à bolonhesa", "massa", 39, "massa de trigo, carne bovina, molho de tomate, queijo", "cantina", "gluten lactose", tags="farto caseiro"),
    _i("Fettuccine ao molho branco", "massa", 37, "massa de trigo, creme de leite, queijo, cogumelo", "cantina", "gluten lactose", veg=True),
    _i("Espaguete ao sugo", "massa", 31, "massa de trigo, molho de tomate, manjericão", "cantina", "gluten", vegano=True),
    _i("Penne sem glúten ao sugo", "massa", 36, "massa de arroz, molho de tomate, manjericão", "cantina", vegano=True),
    _i("Feijoada completa", "brasileira", 44, "feijão preto, carne de porco, linguiça, arroz, couve", "vovo", tags="farto caseiro"),
    _i("Moqueca de peixe", "brasileira", 58, "peixe, leite de coco, pimentão, coentro, arroz", "vovo", tags="caseiro"),
    _i("Bobó de camarão", "brasileira", 62, "camarão, mandioca, leite de coco, dendê, arroz", "vovo", "frutos_do_mar", tags="caseiro"),
    _i("Baião de dois", "brasileira", 35, "arroz, feijão, queijo coalho, carne de sol", "vovo", "lactose", tags="farto caseiro"),
    _i("Marmita de frango grelhado", "marmita", 22, "arroz, feijão, frango, salada", "vovo", tags="caseiro"),
    _i("Marmita de bife acebolado", "marmita", 24, "arroz, feijão, carne bovina, cebola, batata frita", "vovo", frito=True, tags="farto caseiro"),
    _i("Marmita vegana", "marmita", 23, "arroz integral, feijão, legumes, tofu", "verde", vegano=True, tags="saudavel caseiro"),
    _i("Espetinho misto", "churrasco", 28, "carne bovina, frango, linguiça, farofa", "brasa", "gluten"),
    _i("Frango assado com farofa", "frango", 46, "frango, farofa, batata", "brasa", "gluten", tags="farto"),
    _i("Frango grelhado com legumes", "frango", 34, "frango, abobrinha, cenoura, brócolis", "verde", tags="leve saudavel"),
    _i("Tilápia grelhada", "peixe", 42, "tilápia, arroz, legumes", "verde", tags="leve saudavel"),
    _i("Camarão alho e óleo", "frutos_do_mar", 64, "camarão, alho, azeite, arroz", "vovo", "frutos_do_mar"),
    _i("Picanha na chapa", "carne", 72, "picanha, arroz, farofa, vinagrete", "brasa", "gluten", tags="farto"),
    _i("Salada caesar", "salada", 29, "alface, frango, croutons, queijo parmesão", "verde", "gluten lactose", tags="leve"),
    _i("Bowl de salada com grão-de-bico", "salada", 31, "folhas, grão-de-bico, tomate, pepino, azeite", "verde", vegano=True, tags="leve saudavel refrescante"),
    _i("Açaí 500 ml com granola", "acai", 22, "açaí, granola, banana", "doceria", "gluten acucar", vegano=True, tags="refrescante"),
    _i("Açaí puro sem açúcar 500 ml", "acai", 24, "açaí", "doceria", vegano=True, tags="refrescante saudavel"),
    _i("Sorvete de creme", "sorvete", 16, "leite, creme de leite, açúcar", "doceria", "lactose acucar", veg=True, tags="refrescante"),
    _i("Sorbet de manga", "sorvete", 17, "manga, água, açúcar", "doceria", "acucar", vegano=True, tags="refrescante leve"),
    _i("Brigadeiro", "doce", 6, "leite condensado, chocolate, manteiga", "doceria", "lactose acucar", veg=True),
    _i("Paçoca cremosa", "doce", 9, "amendoim, açúcar, leite", "doceria", "amendoim lactose acucar", veg=True),
    _i("Bolo de chocolate com doce de leite", "doce", 14, "farinha de trigo, chocolate, doce de leite, ovo", "doceria", "gluten lactose acucar", veg=True),
    _i("Salada de frutas", "doce", 12, "mamão, banana, maçã, laranja", "doceria", vegano=True, tags="leve refrescante saudavel"),
    _i("Mousse de chocolate vegano sem açúcar", "doce", 15, "abacate, cacau, tâmara", "doceria", vegano=True, tags="saudavel"),
    _i("Brownie sem glúten e sem lactose", "doce", 13, "farinha de amêndoa, cacau, açúcar, ovo", "doceria", "acucar", veg=True),
    _i("Pão de queijo", "cafe_padaria", 5, "polvilho, queijo, leite, ovo", "doceria", "lactose", veg=True),
    _i("Pão na chapa com café", "cafe_padaria", 9, "pão francês, manteiga, café", "esquina", "gluten lactose", veg=True),
    _i("Tapioca de coco", "cafe_padaria", 12, "tapioca, coco", "verde", vegano=True, tags="leve"),
    _i("Refrigerante lata", "bebida", 6, "refrigerante", "esquina", "acucar", vegano=True),
    _i("Refrigerante zero lata", "bebida", 6, "refrigerante zero", "esquina", vegano=True),
    _i("Suco de laranja natural", "bebida", 10, "laranja", "verde", vegano=True, tags="refrescante saudavel"),
]

LATICINIOS = {"leite", "queijo", "laticinio", "laticinios", "derivados de leite"}
_PROIBE = {"sem_lactose": "lactose", "sem_gluten": "gluten", "sem_amendoim": "amendoim",
           "sem_frutos_do_mar": "frutos_do_mar", "sem_acucar": "acucar"}

AVISO_SAUDE = ("Você mencionou uma condição de saúde. Os pratos abaixo não têm o ingrediente no cadastro, mas eu não "
               "consigo garantir a ausência de traços nem de contato cruzado. Confirme com o restaurante antes de pedir.")
RESPOSTAS_FIXAS = {
    Intencao.emergencia.value: ("Isso parece uma emergência e eu não consigo ajudar por aqui. Ligue agora: 190 (Polícia), "
                                "192 (SAMU), 180 (Central de Atendimento à Mulher) ou 188 (CVV, apoio emocional, 24 horas)."),
    Intencao.ataque.value: "Não posso ajudar com isso. Posso ajudar você a encontrar algo para comer.",
    Intencao.fora_escopo.value: "Isso é com o suporte. Aqui eu só ajudo a encontrar o que pedir.",
}


def atende(item: Item, restricao: str) -> bool:
    if restricao == "vegetariano":
        return item.vegetariano
    if restricao == "vegano":
        return item.vegano
    return _PROIBE[restricao] not in item.contem


def _tem_ingrediente(item: Item, excluido: str) -> bool:
    if excluido == "fritura":
        return item.frito
    alvo = normalizar(excluido)
    # Alergia a leite: queijo, manteiga e requeijão não têm a palavra "leite" no nome.
    # Na dúvida, qualquer item marcado com laticínio é excluído.
    if alvo in LATICINIOS and "lactose" in item.contem:
        return True
    return any(alvo in normalizar(ing) for ing in item.ingredientes) or alvo in normalizar(item.nome)


def candidatos(p: Pedido, catalogo=CATALOGO) -> list[Item]:
    """Aplica TODOS os critérios obrigatórios. Um item que viola qualquer um não passa."""
    pessoas = p.people or 1
    out = []
    for it in catalogo:
        if p.categories and it.categoria not in p.categories:
            continue
        if it.categoria in p.exclude_categories:
            continue
        if any(_tem_ingrediente(it, x) for x in p.exclude_ingredients):
            continue
        if not all(atende(it, r) for r in p.restrictions):
            continue
        if p.max_price is not None and it.preco * pessoas + it.restaurante.frete > p.max_price:
            continue
        if p.free_delivery and it.restaurante.frete > 0:
            continue
        if p.max_delivery_min is not None and it.restaurante.tempo_min > p.max_delivery_min:
            continue
        if p.min_rating is not None and it.restaurante.nota < p.min_rating:
            continue
        out.append(it)
    return out


def _ordenar(itens: list[Item], p: Pedido) -> list[Item]:
    def chave(it: Item):
        afinidade = len(it.tags & set(p.wishes))
        return (-afinidade,
                it.preco if "barato" in p.wishes else 0,
                it.restaurante.tempo_min if "rapido" in p.wishes else 0,
                -it.restaurante.nota if "bem_avaliado" in p.wishes else 0,
                -it.restaurante.nota, it.preco)
    return sorted(itens, key=chave)


@dataclass
class Resposta:
    texto: str
    itens: list[Item] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)


def recomendar(p: Pedido, n: int = 3, catalogo=CATALOGO) -> Resposta:
    if p.intent != Intencao.pedido.value:
        return Resposta(RESPOSTAS_FIXAS[p.intent])
    avisos = [AVISO_SAUDE] if p.health_alert else []
    itens = _ordenar(candidatos(p, catalogo), p)
    if not itens:
        return Resposta("Não encontrei nada que atenda a todos os critérios ao mesmo tempo. "
                        "Prefiro não sugerir algo que viole uma restrição. Quer flexibilizar algum critério?", [], avisos)
    escolhidos = itens[:n]
    # restrições parciais: pelo menos uma opção da lista precisa atender a cada uma
    for r in p.partial_restrictions:
        if not any(atende(it, r) for it in escolhidos):
            extra = next((it for it in itens if atende(it, r)), None)
            if extra is None:
                avisos.append(f"Não encontrei opção que atenda a '{r}' dentro dos outros critérios.")
            else:
                escolhidos = escolhidos[:n - 1] + [extra]
    linhas = [f"- {it.nome} ({it.restaurante.nome}): R$ {it.preco:.2f} + R$ {it.restaurante.frete:.2f} de entrega, "
              f"{it.restaurante.tempo_min} min, nota {it.restaurante.nota}" for it in escolhidos]
    return Resposta("Opções que atendem a todos os critérios (catálogo fictício):\n" + "\n".join(linhas), escolhidos, avisos)


def violacoes(p: Pedido, itens: list[Item]) -> list[str]:
    """Lista toda restrição ou exclusão violada por um item sugerido. Deve ser sempre vazia."""
    out = []
    for it in itens:
        out += [f"{it.nome}: viola {r}" for r in p.restrictions if not atende(it, r)]
        out += [f"{it.nome}: contém {x}" for x in p.exclude_ingredients if _tem_ingrediente(it, x)]
        out += [f"{it.nome}: categoria excluída" for _ in [0] if it.categoria in p.exclude_categories]
    return out
