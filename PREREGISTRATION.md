# Pré-registro: avaliação do sistema híbrido em frases novas

Registrado em 11/11/2026, **antes** de rotular as frases novas e antes de rodar qualquer sistema nelas.
O commit que contém este arquivo é a prova da ordem dos eventos.

## Por que
A análise de erros (`results/error_analysis.md`) sugeriu um sistema híbrido, mas ele foi desenhado olhando o próprio teste. No teste usado para desenhá-lo, o híbrido chega a 73% de acerto exato no conjunto principal, e esse número é otimista por construção. Para saber se a ideia se sustenta, ela precisa ser medida em frases que não influenciaram nenhuma decisão.

## Dados
- 80 mensagens geradas por outro LLM (GPT-6 Astra), a partir de um pedido genérico, sem ver exemplos do projeto. Texto bruto, sem edição: `data/test/raw/fresh_llm.txt` (SHA-256 `8a8d694106ca8f257eef71a5043d3f465323a21527f3c72a27c3e24c773dee09`).
- 2 removidas pelo critério de vazamento do projeto (similaridade ≥ 0,6 com frase existente): ficam 78 (`data/test/raw/fresh_llm_removed.txt`).
- Rótulos: escritos pela autora, só com `LABELING.md`, sem ver a saída de nenhum sistema. Na rotulagem às cegas anterior, a concordância da autora com os rótulos do teste foi de 92%.
- Congelamento com hash (`data/test/FROZEN_FRESH.md`) antes da avaliação.

## Sistemas (código fixado neste commit)
1. Regras (`src/order_parser/baseline.py`).
2. Qwen + LoRA, leitura oficial (`hybrid.estrito`).
3. Qwen + LoRA, descartando valores fora do schema (`hybrid.descartando`).
4. Híbrido (`hybrid.hibrido`): o modelo decide a intenção; quando modelo e regras concordam que é pedido, valem os campos das regras.

O adaptador é o publicado em 11/11/2026, sem novo treino. Geração gulosa, `max_new_tokens=128`, igual à avaliação principal.

## Métrica principal e hipóteses
Métrica principal: **acerto exato** (o JSON inteiro correto), com intervalo de Wilson de 95%.

- **H1:** o híbrido tem acerto exato maior que o das regras.
- **H2:** o híbrido tem acerto exato maior que o do Qwen + LoRA (leitura oficial).

Com 78 frases, os intervalos terão perto de ±11 pontos. Diferenças menores que isso serão relatadas como inconclusivas, não como ganho.

Métricas secundárias, relatadas sem hipótese: micro-F1 dos campos, intenção correta, fora de escopo detectado, restrições completas, alerta de saúde e campos inventados em pedido vazio.

## Compromissos
- Todos os resultados serão publicados no README, confirmem ou não as hipóteses.
- Nenhum sistema será alterado depois de ver o resultado neste conjunto.
- Se uma mensagem não puder ser rotulada no schema, ela fica no conjunto com o rótulo mais próximo, e isso é anotado; nenhuma frase é removida depois da avaliação.
