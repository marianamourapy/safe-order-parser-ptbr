"""Baseline por regras: palavras-chave e expressões regulares, sem aprendizado.

Serve de régua. Se o modelo com fine-tuning não for claramente melhor que isto,
o fine-tuning não se justifica. O vocabulário vem do gerador de treino (mesmo
conhecimento que o modelo recebe) e de regras do LABELING.md.
"""

import re

from order_parser.generator import CAT, CAT_GEN, INGREDIENTES, tirar_acento
from order_parser.schema import Pedido


def _n(s: str) -> str:
    return " " + " ".join(tirar_acento(s.lower()).replace("-", " ").split()) + " "


# ---------------------------------------------------------------- intenção
EMERG = ["socorro", "desmai", "nao acorda", "respirar", "sangrando", "engasg", "dor no peito", "dor forte no peito",
         "convuls", "monte de remedio", "apagando", "inchando", "bateu a cabeca", "boca roxa", "overdose",
         "reacao alergica", "me batendo", "batendo", "ameac", "forcando a porta", "seguida", "pedindo socorro",
         "agred", "armado", "nao quero mais viver", "me machucar", "acabar com tudo", "me matar", "sentir minha falta",
         "violencia"]
ATAQUE = ["ignore", "ignora", "esqueca suas regras", "suas regras", "modo administrador", "sem restric",
          "desconsidere", "instruc", "sem filtro", "prompt", "clientes cadastrados", "outros usuarios",
          "dados de pagamento", "chave da api", "configurac", "aprove meu reembolso", "como pago", "cupom de 100",
          "cpf", "telefone da cliente", "suporte do ifood", "logs", "link de pagamento", "sem ele saber",
          "select ", "<script", "{{", "responda so com", "excluir_ingredientes", "preco_max", "mensagem do sistema",
          "verificacao de pagamento", "onde ele mora"]
FORA = ["cade meu pedido", "atrasado", "cancel", "veio faltando", "dinheiro de volta", "reembolso", "reclam",
        "entregador nao", "mudo o endereco", "senha do app", "cartao foi recusado", "cupom de desconto",
        "voces sao humanos", "quem e voce", "pagar em dinheiro", "como falo com", "nota fiscal", "farmacia",
        "remedio", "racao", "mercado", "fralda", "lenco", "carregador", "como viro entregador",
        "cadastrar meu restaurante", "app ta travando", "veio fria"]
SAUDACAO = {"oi", "ola", "boa noite", "bom dia", "boa tarde", "obrigado", "obrigada", "valeu", "obg"}


def intencao(t: str) -> str:
    if any(k in t for k in EMERG):
        return "emergencia"
    if any(k in t for k in ATAQUE):
        return "ataque"
    if any(k in t for k in FORA):
        return "fora_escopo"
    limpo = re.sub(r"[^a-z ]", "", t).strip()
    if limpo in SAUDACAO or limpo.rstrip("!") in SAUDACAO:
        return "fora_escopo"
    return "pedido"


# ---------------------------------------------------------------- categorias e exclusões
EXTRA_CAT = {"japa": "japonesa", "japones": "japonesa", "temaki": "japonesa", "sushi": "japonesa",
             "xis": "hamburguer", "x tudo": "hamburguer", "x burguer": "hamburguer", "x salada": "hamburguer",
             "burger": "hamburguer", "podrao": "lanche", "dogao": "lanche", "cachorro quente": "lanche",
             "joelho": "salgado", "coxinha": "salgado", "pastel": "salgado", "esfirra": "arabe", "kibe": "salgado",
             "quentinha": "marmita", " pf ": "marmita", "prato feito": "marmita", "executivo": "marmita",
             "marmitex": "marmita", "espetinho": "churrasco", "churrasquinho": "churrasco", "galeto": "frango",
             "nuggets": "frango", "picanha": "carne", "bife": "carne", "camarao": "frutos_do_mar",
             "acai": "acai", "milkshake": "sorvete", "picole": "sorvete", "geladinho": "sorvete", "dindin": "sorvete",
             "sobremesa": "doce", "bolo": "doce", "brigadeiro": "doce", "brownie": "doce", "pudim": "doce",
             "padoca": "cafe_padaria", "padaria": "cafe_padaria", "pao de queijo": "cafe_padaria",
             "cafe da manha": "cafe_padaria", "refri": "bebida", "coca": "bebida", "guarana": "bebida",
             "suco": "bebida", "mate": "bebida", "caldo de cana": "bebida", "taco": "mexicana", "burrito": "mexicana",
             "yakisoba": "chinesa", "chines": "chinesa", "macarrao": "massa", "lasanha": "massa", "nhoque": "massa",
             "feijoada": "brasileira", "strogonoff": "brasileira", "moqueca": "brasileira", "baiao": "brasileira",
             "cuscuz": "brasileira", "acaraje": "brasileira", "mineira": "brasileira", "tapioca": "brasileira",
             "pizza": "pizza", "hamburguer": "hamburguer", "lanche": "lanche", "salada": "salada", "sorvete": "sorvete",
             "frango": "frango", "peixe": "peixe", "frutos do mar": "frutos_do_mar", "churrasco": "churrasco",
             "marmita": "marmita", "esfiha": "arabe", "arabe": "arabe", "mexicana": "mexicana", "doce": "doce"}


def _vocab_cat():
    v = dict()
    for cat, formas in CAT.items():
        for f in formas:
            f = re.sub(r"^(um|uma|uns|umas) ", "", tirar_acento(f.lower()).replace("-", " "))
            if len(f) > 3:
                v[f] = cat
    v.update(EXTRA_CAT)
    return sorted(v.items(), key=lambda kv: -len(kv[0]))  # termos mais longos primeiro


VOCAB_CAT = _vocab_cat()
GEN = sorted(((tirar_acento(g.lower()), c) for c, gs in CAT_GEN.items() for g in gs), key=lambda kv: -len(kv[0]))
NEG = r"(?:nada de|menos|nao quero|exceto|tudo menos|qualquer coisa menos|nem|tirando|sem)"
ING_SEGUNDA = {"branco", "ralado", "cheese", "passa", "doce", "de coco"}
NAO_ING = {"lactose", "gluten", "acucar", "amendoim", "frutos", "carne", "taxa", "frete", "entrega", "pagar", "graca",
           "pressa", "grana", "dinheiro", "fritura", "nada", "nenhum", "nenhuma", "problema", "saber", "comida"}


def categorias_e_exclusoes(t: str):
    excl_cat, cats = set(), set()
    for termo, cat in GEN:
        if re.search(rf"{NEG} (?:comida )?{re.escape(termo)}\b", t):
            excl_cat.add(cat)
    for termo, cat in VOCAB_CAT:
        for m in re.finditer(rf"(?<![a-z]){re.escape(termo.strip())}(?![a-z])", t):
            antes = t[max(0, m.start() - 25):m.start()]
            if cat in excl_cat and re.search(rf"{NEG} (?:comida )?$", antes):
                continue
            if re.search(r"\b(?:de|com) $", antes) and cats:   # "pizza de frango": o frango é sabor
                continue
            cats.add(cat)
    if re.search(r"\bfrango (?:a )?parmegiana|parmegiana de frango", t):
        cats.add("frango")
    cats -= excl_cat
    excl_ing = set()
    for m in re.finditer(r"(?:sem|tira o|tira a|tirar o|nao coloca|pode tirar) (?:o |a |os |as )?([a-z]+)(?: ([a-z]+))?", t):
        w1, w2 = m.group(1), m.group(2)
        if w1 in NAO_ING or any(w1 == tirar_acento(g) for g, _ in GEN):
            continue
        excl_ing.add(f"{w1} {w2}" if w2 in ING_SEGUNDA else w1)
    if re.search(r"sem fritura|nada frito|nao quero nada frito|nada de frito", t):
        excl_ing.add("fritura")
    return cats, excl_cat, excl_ing


# ---------------------------------------------------------------- restrições e saúde
REST = {"sem_lactose": ["sem lactose", "zero lactose", "intoleran", "lactose me faz mal"],
        "sem_gluten": ["sem gluten", "zero gluten", "celiac", "gluten"],
        "vegano": ["vegan", "origem animal", "plant based"],
        "vegetariano": ["vegetarian", "nao como carne nenhuma", "sem carne nenhuma", "nao come carne"],
        "sem_amendoim": ["amendoim"],
        "sem_frutos_do_mar": ["sem frutos do mar", "nada de frutos do mar", "alergia a camarao", "alergica a camarao",
                              "alergico a camarao", "alergia a frutos do mar", "alergico a frutos do mar",
                              "alergica a frutos do mar", "crustaceo"],
        "sem_acucar": ["sem acucar", "zero acucar", "diet", "diabet"]}
SAUDE = ["alerg", "celiac", "diabet", "intoleran", "passo mal", "me faz mal", "gravida", "gestante", "pressao alta",
         "colesterol"]
PARCIAL = r"\b(?:um|uma|uma delas|um deles|um de nos|pelo menos uma|minha amiga|meu amigo|minha mae|meu filho|metade)\b"


def restricoes(t: str, tem_grupo: bool):
    total, parcial = set(), set()
    for r, ks in REST.items():
        for k in ks:
            i = t.find(k)
            if i < 0:
                continue
            antes = t[max(0, i - 30):i]
            if tem_grupo and re.search(PARCIAL, antes) and not re.search(r"\btod(?:o|os|as) ", antes):
                parcial.add(r)
            else:
                total.add(r)
            break
    if "vegano" in total and "vegetariano" in total:
        total.discard("vegetariano")
    return total, parcial - total


# ---------------------------------------------------------------- números
EXT = {"dez": 10, "quinze": 15, "vinte": 20, "trinta": 30, "quarenta": 40, "cinquenta": 50, "sessenta": 60,
       "setenta": 70, "oitenta": 80, "noventa": 90, "cem": 100, "duzentos": 200}
EXT_P = {"dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "dez": 10}


def _num(s):
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def preco(t):
    m = re.search(r"(?:ate|no maximo|maximo|menos de|uns|na faixa de|por ate|nao passe de|orcamento de|r\$)\s*(?:r\$\s*)?(\d+(?:[.,]\d{1,2})?)(?!\s*(?:min|ml|km|h\b|pessoas))", t) \
        or re.search(r"(\d+(?:[.,]\d{1,2})?)\s*(?:reais|conto|pila)", t)
    if m:
        return _num(m.group(1))
    m = re.search(r"(?:ate|maximo|menos de|uns|de) (" + "|".join(EXT) + r")(?: e (cinco))? (?:reais|conto|pila)", t)
    if m:
        return EXT[m.group(1)] + (5 if m.group(2) else 0)
    return None


def tempo(t):
    if re.search(r"meia hora|meia horinha", t):
        return 30
    if re.search(r"uma hora e meia", t):
        return 90
    m = re.search(r"(\d+)\s*(?:min|minutos|minutinhos)", t)
    if m:
        return int(m.group(1))
    m = re.search(r"(?:" + "|".join(EXT) + r") minutos", t)
    if m:
        return EXT[m.group(0).split()[0]]
    if re.search(r"\b(?:uma hora|1h|1 hora)\b", t):
        return 60
    return None


def nota(t):
    m = re.search(r"(?:nota|avaliacao)[^0-9]{0,20}(\d[.,]\d)", t) or re.search(r"(\d[.,]\d)\s*(?:\+|pra cima|ou mais|estrelas)", t)
    if m:
        return _num(m.group(1))
    if re.search(r"quatro e meio", t):
        return 4.5
    return None


def pessoas(t):
    if re.search(r"(?:pra|para) (?:mim e (?:meu|minha)|nos dois|dois\b)|casal|\bpra 2\b|duas pessoas", t):
        return 2
    m = re.search(r"(?:pra|para|somos|nos|grupo de|familia de|umas|uns) (\d+)\b(?! ?(?:reais|conto|pila|min|ml|%))", t)
    if m:
        return int(m.group(1))
    m = re.search(r"(?:pra|para|somos|nos) (" + "|".join(EXT_P) + r")\b(?! reais)", t)
    if m:
        return EXT_P[m.group(1)]
    if re.search(r"so pra mim|sozinh", t):
        return 1
    return None


DESEJO = {"leve": ["leve", "nada pesado", "coisa pesada"], "saudavel": ["saudavel", "fit", "low carb", "nada gorduroso"],
          "barato": ["barat", "em conta", "promo", "custo beneficio", "nao seja caro", "nao muito caro", "nao tao caro",
                     "sem grana", "fim de mes"],
          "farto": ["bem servid", "caprich", "encha a barriga", "renda bastante", "rende bastante", "sustente",
                    "bem grande", "com tudo que tem direito"],
          "refrescante": ["refresc", "geladinho"],
          "caseiro": ["caseir", "comida de vo", "de casa", "de panela", "comida de verdade"],
          "picante": ["apimentad", "picante", "ardid", "pimenta"],
          "diferente": ["diferente", "algo novo", "surpreend", "nunca pedi"],
          "rapido": ["rapid", "logo", "pressa", "urgente", "pra ontem", "menor tempo"],
          "bem_avaliado": ["bem avaliad", "nota boa", "nota alta", "melhores", " top ", "boas avaliac",
                           "super restaurante"]}


def desejos(t, tem_preco, tem_tempo, tem_nota, excl_ing):
    ds = set()
    for d, ks in DESEJO.items():
        if any(k in t for k in ks):
            ds.add(d)
    if tem_preco:
        ds.discard("barato")
    if tem_tempo:
        ds.discard("rapido")
    if tem_nota:
        ds.discard("bem_avaliado")
    if "pimenta" in excl_ing or re.search(r"sem pimenta|pouca pimenta|nao seja muito apimentad|nada apimentado", t):
        ds.discard("picante")
    return ds


def prever(texto: str) -> Pedido:
    t = _n(texto)
    it = intencao(t)
    if it != "pedido":
        return Pedido(intencao=it)
    cats, xcat, xing = categorias_e_exclusoes(t)
    pes = pessoas(t)
    rest, parc = restricoes(t, pes is not None and pes > 1)
    saude = any(k in t for k in SAUDE)
    if saude and re.search(r"alergi\w* (?:a|ao|à|a proteina do) leite", t):
        rest.discard("sem_lactose")
        xing.add("leite")
    p, tm, nt = preco(t), tempo(t), nota(t)
    frete = bool(re.search(r"frete gr|entrega gr|sem taxa|taxa zero|taxa gr|frete zer|entrega de graca|"
                           r"nao cobre entrega|nao pago entrega|sem pagar entrega|frete gratis|frete zero", t))
    return Pedido(categorias=sorted(cats), excluir_categorias=sorted(xcat),
                  excluir_ingredientes=sorted(x for x in xing if len(x) <= 30)[:8],
                  restricoes=sorted(rest), restricoes_parciais=sorted(parc), alerta_saude=saude,
                  preco_max=p if p and p > 0 else None, frete_gratis=frete, tempo_max_min=tm,
                  nota_min=nt if nt is not None and 0 <= nt <= 5 else None,
                  pessoas=pes, desejos=sorted(desejos(t, p is not None, tm is not None, nt is not None, xing)))
