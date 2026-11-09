### Baseline por regras

| Conjunto | n | JSON válido | Exato | Micro-F1 campos | Restrições completas | Alerta saúde (recall) | Emergência (recall) | Ataque (recall) | Inventou em vazios |
|---|---|---|---|---|---|---|---|---|---|
| principal | 438 | 100.0% | 66.4% [62–71] | 89.5% | 93.6% (n=78) | 100.0% (n=29) | 56.0% (n=25) | 44.0% (n=25) | 0.0% (n=7) |
| autor2 | 100 | 100.0% | 52.0% [42–62] | 72.5% | 100.0% (n=10) | 100.0% (n=5) | — (n=0) | — (n=0) | 20.0% (n=10) |
| humano | 30 | 100.0% | 50.0% [33–67] | 69.8% | 50.0% (n=4) | 75.0% (n=4) | — (n=0) | — (n=0) | 0.0% (n=8) |
| humano_seguranca | 10 | 100.0% | 70.0% [40–89] | — | — (n=0) | — (n=0) | 60.0% (n=5) | 80.0% (n=5) | — (n=0) |

#### Campos (conjunto principal)

| Campo | Precisão | Recall | F1 | tp | fp | fn |
|---|---|---|---|---|---|---|
| `categories` | 89.6% | 91.2% | 90.4% | 258 | 30 | 25 |
| `exclude_categories` | 90.3% | 80.0% | 84.8% | 28 | 3 | 7 |
| `exclude_ingredients` | 77.5% | 73.8% | 75.6% | 31 | 9 | 11 |
| `restrictions` | 82.0% | 90.9% | 86.2% | 50 | 11 | 5 |
| `partial_restrictions` | 90.9% | 69.0% | 78.4% | 20 | 2 | 9 |
| `wishes` | 96.5% | 85.4% | 90.6% | 82 | 3 | 14 |
| `max_price` | 81.5% | 91.4% | 86.2% | 53 | 12 | 5 |
| `max_delivery_min` | 96.8% | 96.8% | 96.8% | 30 | 1 | 1 |
| `min_rating` | 100.0% | 93.1% | 96.4% | 27 | 0 | 2 |
| `people` | 97.8% | 84.6% | 90.7% | 44 | 1 | 8 |
| `free_delivery` | 100.0% | 97.1% | 98.5% | 33 | 0 | 1 |
| `health_alert` | 100.0% | 100.0% | 100.0% | 29 | 0 | 0 |
