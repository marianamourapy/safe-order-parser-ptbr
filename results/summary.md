## Acerto exato (JSON inteiro correto), com intervalo de 95%

| Conjunto | n | Regras (baseline) | Qwen sem ajuste | Qwen + 8 exemplos no prompt | Qwen + LoRA (este projeto) |
|---|---|---|---|---|---|
| Principal (LLM, autor 1) | 438 | 66% [62–71] | 3% [2–6] | 20% [16–24] | 66% [62–70] |
| Outro autor (LLM) | 100 | 52% [42–62] | 10% [6–17] | 18% [12–27] | 23% [16–32] |
| Humano | 30 | 50% [33–67] | 13% [5–30] | 23% [12–41] | 40% [25–58] |
| Humano, mensagens reais p/ restaurante | 63 | 38% [27–50] | 3% [1–11] | 21% [12–32] | 29% [19–41] |

## Micro-F1 dos campos

| Conjunto | Regras (baseline) | Qwen sem ajuste | Qwen + 8 exemplos no prompt | Qwen + LoRA (este projeto) |
|---|---|---|---|---|
| Principal (LLM, autor 1) | 90% | 29% | 51% | 86% |
| Outro autor (LLM) | 72% | 15% | 38% | 61% |
| Humano | 70% | 17% | 31% | 70% |
| Humano, mensagens reais p/ restaurante | 67% | 13% | 35% | 63% |

## Segurança e restrições (todos os conjuntos somados)

| Métrica | Regras (baseline) | Qwen sem ajuste | Qwen + 8 exemplos no prompt | Qwen + LoRA (este projeto) |
|---|---|---|---|---|
| JSON válido | 641/641 (100%) [99–100] | 298/641 (46%) [43–50] | 413/641 (64%) [61–68] | 604/641 (94%) [92–96] |
| Restrições completas | 89/97 (92%) [85–96] | 33/97 (34%) [25–44] | 33/97 (34%) [25–44] | 83/97 (86%) [77–91] |
| Alerta de saúde (recall) | 41/42 (98%) [88–100] | 3/42 (7%) [2–19] | 16/42 (38%) [25–53] | 34/42 (81%) [67–90] |
| Inventou campos em pedido vazio | 3/32 (9%) [3–24] | 19/32 (59%) [42–74] | 12/32 (38%) [23–55] | 18/32 (56%) [39–72] |
| Emergência detectada (recall) | 17/30 (57%) [39–73] | 0/30 (0%) [0–11] | 6/30 (20%) [10–37] | 29/30 (97%) [83–99] |
| Ataque detectado (recall) | 15/30 (50%) [33–67] | 0/30 (0%) [0–11] | 0/30 (0%) [0–11] | 27/30 (90%) [74–97] |

## Custo por mensagem (GPU T4, lote de 16)

| Sistema | Tokens de entrada | Tokens de saída | Segundos por mensagem |
|---|---|---|---|
| Qwen sem ajuste | 347 | 107.5 | 0.490 |
| Qwen + 8 exemplos no prompt | 662 | 20.9 | 0.326 |
| Qwen + LoRA (este projeto) | 347 | 14.7 | 0.221 |
