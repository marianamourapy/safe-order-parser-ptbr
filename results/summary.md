## Acerto exato (JSON inteiro correto), com intervalo de 95%

| Conjunto | n | Regras (baseline) |
|---|---|---|
| Principal (LLM, autor 1) | 438 | 66% [62–71] |
| Outro autor (LLM) | 100 | 52% [42–62] |
| Humano | 30 | 50% [33–67] |
| Humano, mensagens reais p/ restaurante | 63 | 38% [27–50] |

## Micro-F1 dos campos

| Conjunto | Regras (baseline) |
|---|---|
| Principal (LLM, autor 1) | 90% |
| Outro autor (LLM) | 72% |
| Humano | 70% |
| Humano, mensagens reais p/ restaurante | 67% |

## Segurança e restrições (todos os conjuntos somados)

| Métrica | Regras (baseline) |
|---|---|
| JSON válido | 641/641 (100%) [99–100] |
| Restrições completas | 89/97 (92%) [85–96] |
| Alerta de saúde (recall) | 41/42 (98%) [88–100] |
| Inventou campos em pedido vazio | 3/32 (9%) [3–24] |
| Emergência detectada (recall) | 17/30 (57%) [39–73] |
| Ataque detectado (recall) | 15/30 (50%) [33–67] |
