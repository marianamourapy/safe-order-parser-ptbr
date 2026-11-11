### Qwen sem ajuste

| Conjunto | n | JSON válido | Exato | Micro-F1 campos | Restrições completas | Alerta saúde (recall) | Emergência (recall) | Ataque (recall) | Inventou em vazios |
|---|---|---|---|---|---|---|---|---|---|
| principal | 438 | 47.3% | 3.4% [2–6] | 28.6% | 39.7% (n=78) | 10.3% (n=29) | 0.0% (n=25) | 0.0% (n=25) | 71.4% (n=7) |
| autor2 | 100 | 45.0% | 10.0% [6–17] | 14.6% | 20.0% (n=10) | 0.0% (n=5) | — (n=0) | — (n=0) | 30.0% (n=10) |
| humano | 30 | 36.7% | 13.3% [5–30] | 16.7% | 0.0% (n=4) | 0.0% (n=4) | — (n=0) | — (n=0) | 50.0% (n=8) |
| humano_seguranca | 10 | 20.0% | 0.0% [0–28] | — | — (n=0) | — (n=0) | 0.0% (n=5) | 0.0% (n=5) | — (n=0) |
| humano_restaurante | 63 | 52.4% | 3.2% [1–11] | 13.2% | 0.0% (n=5) | 0.0% (n=4) | — (n=0) | — (n=0) | 100.0% (n=7) |

#### Campos (conjunto principal)

| Campo | Precisão | Recall | F1 | tp | fp | fn |
|---|---|---|---|---|---|---|
| `categories` | 43.6% | 32.5% | 37.2% | 92 | 119 | 191 |
| `exclude_categories` | 22.2% | 11.4% | 15.1% | 4 | 14 | 31 |
| `exclude_ingredients` | 12.2% | 23.8% | 16.1% | 10 | 72 | 32 |
| `restrictions` | 6.9% | 34.5% | 11.5% | 19 | 256 | 36 |
| `partial_restrictions` | 0.0% | 0.0% | 0.0% | 0 | 27 | 29 |
| `wishes` | 9.6% | 15.6% | 11.9% | 15 | 142 | 81 |
| `max_price` | 86.5% | 55.2% | 67.4% | 32 | 5 | 26 |
| `max_delivery_min` | 53.6% | 48.4% | 50.8% | 15 | 13 | 16 |
| `min_rating` | 60.0% | 51.7% | 55.6% | 15 | 10 | 14 |
| `people` | 42.0% | 40.4% | 41.2% | 21 | 29 | 31 |
| `free_delivery` | 55.6% | 58.8% | 57.1% | 20 | 16 | 14 |
| `health_alert` | 100.0% | 10.3% | 18.8% | 3 | 0 | 26 |
