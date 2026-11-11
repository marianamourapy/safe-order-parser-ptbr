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
- LoRA: rank 16, alpha 32, dropout 0,05, em todas as projeções de atenção e MLP; 2 épocas; taxa de aprendizado 2e-4; GPU T4.
- Registro completo em `results/training_log.json`.

## Avaliação
_A preencher com `results/summary.md`._

## Limitações
Treinado só com texto sintético; poucos dados humanos na avaliação; lê uma mensagem por vez; não substitui moderação de segurança. Lista completa no README do repositório.
