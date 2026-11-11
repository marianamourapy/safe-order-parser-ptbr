### Qwen + 8 exemplos no prompt

| Conjunto | n | JSON válido | Exato | Micro-F1 campos | Restrições completas | Alerta saúde (recall) | Emergência (recall) | Ataque (recall) | Inventou em vazios |
|---|---|---|---|---|---|---|---|---|---|
| principal | 438 | 66.9% | 19.6% [16–24] | 51.1% | 33.3% (n=78) | 34.5% (n=29) | 20.0% (n=25) | 0.0% (n=25) | 42.9% (n=7) |
| autor2 | 100 | 66.0% | 18.0% [12–27] | 37.6% | 50.0% (n=10) | 60.0% (n=5) | — (n=0) | — (n=0) | 50.0% (n=10) |
| humano | 30 | 46.7% | 23.3% [12–41] | 30.6% | 25.0% (n=4) | 25.0% (n=4) | — (n=0) | — (n=0) | 25.0% (n=8) |
| humano_seguranca | 10 | 30.0% | 10.0% [2–40] | — | — (n=0) | — (n=0) | 20.0% (n=5) | 0.0% (n=5) | — (n=0) |
| humano_restaurante | 63 | 58.7% | 20.6% [12–32] | 34.6% | 20.0% (n=5) | 50.0% (n=4) | — (n=0) | — (n=0) | 28.6% (n=7) |

#### Campos (conjunto principal)

| Campo | Precisão | Recall | F1 | tp | fp | fn |
|---|---|---|---|---|---|---|
| `categories` | 74.9% | 60.1% | 66.7% | 170 | 57 | 113 |
| `exclude_categories` | 55.6% | 14.3% | 22.7% | 5 | 4 | 30 |
| `exclude_ingredients` | 23.2% | 31.0% | 26.5% | 13 | 43 | 29 |
| `restrictions` | 48.6% | 30.9% | 37.8% | 17 | 18 | 38 |
| `partial_restrictions` | — | 0.0% | — | 0 | 0 | 29 |
| `wishes` | 20.3% | 13.5% | 16.2% | 13 | 51 | 83 |
| `max_price` | 53.5% | 79.3% | 63.9% | 46 | 40 | 12 |
| `max_delivery_min` | 62.1% | 58.1% | 60.0% | 18 | 11 | 13 |
| `min_rating` | 69.0% | 69.0% | 69.0% | 20 | 9 | 9 |
| `people` | 49.1% | 50.0% | 49.5% | 26 | 27 | 26 |
| `free_delivery` | 95.2% | 58.8% | 72.7% | 20 | 1 | 14 |
| `health_alert` | 50.0% | 34.5% | 40.8% | 10 | 10 | 19 |
