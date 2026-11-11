# Concordância da rotulagem às cegas

Rótulo inteiro igual: 46/50 (92%) [IC 95%: 81–97]

| Campo | Concordância |
|---|---|
| `intent` | 50/50 (100%) |
| `categories` | 50/50 (100%) |
| `exclude_categories` | 50/50 (100%) |
| `exclude_ingredients` | 48/50 (96%) |
| `restrictions` | 50/50 (100%) |
| `partial_restrictions` | 50/50 (100%) |
| `wishes` | 49/50 (98%) |
| `max_price` | 50/50 (100%) |
| `max_delivery_min` | 50/50 (100%) |
| `min_rating` | 50/50 (100%) |
| `people` | 49/50 (98%) |
| `free_delivery` | 50/50 (100%) |
| `health_alert` | 50/50 (100%) |

## Divergências

- `a037` Manda uma pizza família. Aqui em casa família é eu e minha fome 😂
  - people: autora=None | teste=1
- `t208` sobremesa que não tenha açúcar nenhum, nem adoçada com mel
  - exclude_ingredients: autora=[] | teste=['mel']
- `t354` quero experimentar comida mexicana pela primeira vez, mas não gosto de muita pimenta
  - exclude_ingredients: autora=[] | teste=['pimenta']
- `r006` Bom dia Poderia mandar aquela minha refeição de sempre da minha dieta só salada e uma proteína.Vou ficar aguardando saio às 12h
  - wishes: autora=[] | teste=['saudavel']
