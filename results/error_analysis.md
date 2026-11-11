# Análise de erros do modelo ajustado (Qwen + LoRA)

Gerado por `scripts/error_analysis.py` a partir de `results/preds_*.jsonl`.

## 1. Saídas rejeitadas pelo schema: 37 de 641

Na avaliação oficial, uma saída rejeitada conta como "não extraiu nada".

| Motivo | Saídas |
|---|---|
| valor fora da lista permitida | 27 |
| chave que não existe no schema | 7 |
| outra regra do schema | 1 |
| JSON malformado | 1 |
| sem JSON na saída | 1 |

Exemplos:

- `t004` (valor fora da lista permitida): {"categories":["japonesa"],"wishes":["bem_avaliado","aberto"]}
- `t023` (outra regra do schema): {"categories":["carne"],"intent":"fora_escopo"}
- `t044` (valor fora da lista permitida): {"categories":["brasileira","ovo"]}
- `t063` (valor fora da lista permitida): {"categories":["frango"],"wishes":["marmita"]}
- `t086` (valor fora da lista permitida): {"categories":["beach"],"wishes":["leve","refrescante"]}
- `t200` (valor fora da lista permitida): {"categories":["marmita"],"restrictions":["vegetariano","sem_carne"],"people":4}
- `t304` (chave que não existe no schema): {"categories":["acai"],"payment_method":"pix"}
- `h003` (JSON malformado): {"query":{"categories":["pizza"],"wishes":["bem_avaliado","barato"]}[]}

## 2. Itens inventados (fp) e itens que faltaram (fn), por campo

Modelo com valores inválidos descartados, para contar só o que ele extraiu de fato. Todos os conjuntos somados.

| Campo | Modelo: certos | Modelo: inventados | Modelo: faltaram | Regras: certos | Regras: inventados | Regras: faltaram |
|---|---|---|---|---|---|---|
| `categories` | 382 | 123 | 41 | 357 | 67 | 66 |
| `exclude_categories` | 33 | 6 | 9 | 30 | 6 | 12 |
| `exclude_ingredients` | 70 | 33 | 14 | 53 | 33 | 31 |
| `restrictions` | 60 | 15 | 12 | 65 | 15 | 7 |
| `partial_restrictions` | 26 | 13 | 6 | 20 | 2 | 12 |
| `wishes` | 113 | 91 | 20 | 111 | 11 | 22 |
| `max_price` | 66 | 7 | 4 | 65 | 14 | 5 |
| `max_delivery_min` | 31 | 2 | 3 | 33 | 1 | 1 |
| `min_rating` | 28 | 0 | 2 | 28 | 0 | 2 |
| `people` | 61 | 13 | 10 | 53 | 7 | 18 |
| `free_delivery` | 36 | 12 | 1 | 36 | 0 | 1 |
| `health_alert` | 36 | 3 | 6 | 41 | 1 | 1 |
| **Total** | 942 | 318 | 128 | 892 | 157 | 178 |

## 3. Intenção: o que era x o que o modelo respondeu

| Era | Modelo respondeu | Mensagens |
|---|---|---|
| pedido | pedido | 529 |
| emergencia | emergencia | 29 |
| fora_escopo | fora_escopo | 28 |
| ataque | ataque | 27 |
| pedido | fora_escopo | 11 |
| pedido | ataque | 7 |
| fora_escopo | pedido | 3 |
| ataque | fora_escopo | 2 |
| fora_escopo | ataque | 2 |
| emergencia | pedido | 1 |
| pedido | inválida | 1 |
| ataque | inválida | 1 |

## 4. Análise posterior (não é resultado oficial)

As duas últimas colunas foram desenhadas depois de ver os erros no teste. Elas indicam o que experimentar em seguida; para valerem como resultado, precisam ser medidas em frases novas.

| Acerto exato | Regras | Modelo (oficial) | Modelo, descartando valores inválidos | Híbrido: intenção do modelo + campos das regras |
|---|---|---|---|---|
| Principal (n=438) | 66% | 66% | 67% | 73% |
| Outro autor (n=100) | 52% | 23% | 25% | 49% |
| Humano (n=30) | 50% | 40% | 37% | 43% |
| Humano, restaurante (n=63) | 38% | 29% | 35% | 30% |
| Humano, segurança (n=10) | 70% | 90% | 90% | 100% |

| Todos os conjuntos somados | Regras | Modelo (oficial) | Modelo, descartando valores inválidos | Híbrido: intenção do modelo + campos das regras |
|---|---|---|---|---|
| Restrições completas | 89/97 | 83/97 | 92/97 | 88/97 |
| Alerta de saúde | 41/42 | 34/42 | 36/42 | 40/42 |
| Inventou campos em pedido vazio | 3/32 | 18/32 | 19/32 | 3/32 |
| Emergência detectada | 17/30 | 29/30 | 29/30 | 29/30 |
| Ataque detectado | 15/30 | 27/30 | 27/30 | 28/30 |
