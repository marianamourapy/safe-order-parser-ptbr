---
language: pt
license: apache-2.0
base_model: Qwen/Qwen2.5-1.5B-Instruct
library_name: peft
tags: [lora, structured-output, portuguese, food-delivery]
---

# safe-order-parser-ptbr (adaptador LoRA)

Adaptador LoRA para o Qwen2.5-1.5B-Instruct que converte mensagens informais de delivery em português do Brasil em JSON estruturado (categorias, restrições alimentares, alerta de saúde, preço, prazo, pessoas) e classifica a intenção: `pedido`, `fora_escopo`, `emergencia` ou `ataque`.

Código, dados, avaliação e limitações: https://github.com/marianamourapy/safe-order-parser-ptbr

## Uso previsto
Demonstração e estudo. A saída deve ser validada pelo schema do repositório e aplicada como filtro por um sistema separado.

## Fora do uso previsto
Decisões reais sobre alergias ou saúde; detecção de emergências em produção; qualquer uso sem validação da saída.

## Treino
- Dados: 3.685 exemplos sintéticos gerados por templates, com rótulo por construção (`data/train/`).
- LoRA: rank 16, alpha 32, dropout 0,05, em todas as projeções de atenção e MLP; 2 épocas; taxa de aprendizado 2e-4; lote efetivo de 16 (4 × 4 de acumulação), com gradient checkpointing; GPU T4.
- 42 minutos de treino; perda de validação 0,041 na primeira época e 0,022 na segunda.
- Registro completo em `results/training_log.json`.

## Avaliação
641 frases de teste congeladas antes da avaliação, de quatro origens. Intervalos de 95% entre colchetes.

| Métrica | Regras | Qwen sem ajuste | Qwen + 8 exemplos | Este adaptador |
|---|---|---|---|---|
| Acerto exato, conjunto principal (438) | 66% [62–71] | 3% [2–6] | 20% [16–24] | 66% [62–70] |
| Acerto exato, outro autor (100) | 52% [42–62] | 10% [6–17] | 18% [12–27] | 23% [16–32] |
| Acerto exato, humano (30) | 50% [33–67] | 13% [5–30] | 23% [12–41] | 40% [25–58] |
| Acerto exato, mensagens reais (63) | 38% [27–50] | 3% [1–11] | 21% [12–32] | 29% [19–41] |
| JSON válido no schema | 100% | 46% | 64% | 94% |
| Alerta de saúde (recall) | 41/42 | 3/42 | 16/42 | 34/42 |
| Emergência detectada | 17/30 | 0/30 | 6/30 | 29/30 |
| Ataque detectado | 15/30 | 0/30 | 0/30 | 27/30 |
| Inventou campos em pedido vago | 3/32 | 19/32 | 12/32 | 18/32 |

O adaptador supera o modelo base com e sem exemplos no prompt, e supera um baseline por regras na detecção de emergências e ataques. Na extração de campos, empata com as regras no conjunto principal e perde em frases de outro autor: ele inventa categorias e desejos que a pessoa não disse, e 6% das saídas usam valores fora do schema. Análise completa em `results/error_analysis.md`.

Em 78 frases novas, avaliadas segundo um pré-registro, um sistema híbrido (este adaptador decide a intenção, regras extraem os campos) teve 49% de acerto exato, contra 38% das regras e 37% do adaptador sozinho. A diferença não é estatisticamente conclusiva (McNemar exato, p = 0,057 e 0,078). Detalhes em `results/fresh_eval.md`.

## Limitações
Perde o alerta de saúde em 8 de 42 casos, então não pode ser a única barreira para alergias; classifica alguns pedidos comuns como ataque ou fora de escopo; treinado só com texto sintético; poucos dados humanos na avaliação; lê uma mensagem por vez; não substitui moderação de segurança. Lista completa no README do repositório.
