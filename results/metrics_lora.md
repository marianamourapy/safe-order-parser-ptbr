### Qwen + LoRA

| Conjunto | n | JSON válido | Exato | Micro-F1 campos | Restrições completas | Alerta saúde (recall) | Emergência (recall) | Ataque (recall) | Inventou em vazios |
|---|---|---|---|---|---|---|---|---|---|
| principal | 438 | 96.6% | 66.2% [62–70] | 85.8% | 91.0% (n=78) | 86.2% (n=29) | 96.0% (n=25) | 92.0% (n=25) | 85.7% (n=7) |
| autor2 | 100 | 93.0% | 23.0% [16–32] | 61.4% | 70.0% (n=10) | 60.0% (n=5) | — (n=0) | — (n=0) | 70.0% (n=10) |
| humano | 30 | 83.3% | 40.0% [25–58] | 70.2% | 75.0% (n=4) | 50.0% (n=4) | — (n=0) | — (n=0) | 37.5% (n=8) |
| humano_seguranca | 10 | 90.0% | 90.0% [60–98] | — | — (n=0) | — (n=0) | 100.0% (n=5) | 80.0% (n=5) | — (n=0) |
| humano_restaurante | 63 | 85.7% | 28.6% [19–41] | 63.1% | 40.0% (n=5) | 100.0% (n=4) | — (n=0) | — (n=0) | 28.6% (n=7) |

#### Campos (conjunto principal)

| Campo | Precisão | Recall | F1 | tp | fp | fn |
|---|---|---|---|---|---|---|
| `categories` | 83.6% | 89.8% | 86.5% | 254 | 50 | 29 |
| `exclude_categories` | 82.4% | 80.0% | 81.2% | 28 | 6 | 7 |
| `exclude_ingredients` | 77.3% | 81.0% | 79.1% | 34 | 10 | 8 |
| `restrictions` | 82.7% | 78.2% | 80.4% | 43 | 9 | 12 |
| `partial_restrictions` | 77.4% | 82.8% | 80.0% | 24 | 7 | 5 |
| `wishes` | 62.9% | 86.5% | 72.8% | 83 | 49 | 13 |
| `max_price` | 98.3% | 98.3% | 98.3% | 57 | 1 | 1 |
| `max_delivery_min` | 96.7% | 93.5% | 95.1% | 29 | 1 | 2 |
| `min_rating` | 100.0% | 93.1% | 96.4% | 27 | 0 | 2 |
| `people` | 90.7% | 94.2% | 92.5% | 49 | 5 | 3 |
| `free_delivery` | 91.9% | 100.0% | 95.8% | 34 | 3 | 0 |
| `health_alert` | 96.2% | 86.2% | 90.9% | 25 | 1 | 4 |
