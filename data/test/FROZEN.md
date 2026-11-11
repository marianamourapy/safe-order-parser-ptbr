# Conjunto de teste congelado

Congelado em 2026-11-10, antes de qualquer modelo ser avaliado.
Qualquer mudança nestes arquivos invalida a comparação com resultados anteriores.

## Histórico

- 07/11/2026: primeiro congelamento.
- 09/11/2026: só os nomes das chaves do rótulo passaram para inglês (ex.: `preco_max` → `max_price`).
  Textos e valores verificados idênticos por script. Até aqui, só o baseline por regras tinha sido
  avaliado, e as métricas dele continuaram idênticas. Nenhum modelo de linguagem foi avaliado antes.
- 10/11/2026: novo conjunto `test_human_restaurant.jsonl` (63 mensagens reais para um restaurante, em quatro lotes no mesmo dia),
  incluído antes da primeira avaliação de um modelo de linguagem.

| Arquivo | Frases | SHA-256 |
|---|---|---|
| `test_main.jsonl` | 438 | `ca327f0acc7402c63b800e7b818a4172e46f9f29652e45fdb0f34c10b3ba48a2` |
| `test_author2.jsonl` | 100 | `2a9afc64d55044de53fd9e2643f635431bd954a55f6efe36181986346e408cb3` |
| `test_human.jsonl` | 30 | `90c9c31105f0c255862a3b4a35a2c1ba3273c6ace88e75a6f3bb81fb2d20c684` |
| `test_human_safety.jsonl` | 10 | `9d607797105148f893e3cd86b2c3f07ea49a25b31e9ac229bf9005f7d0132668` |
| `test_human_restaurant.jsonl` | 63 | `d8d5527da33271dd4b68dc71cb989f3c2669e8bbac6787d6ddfb0bf8ad232b58` |
