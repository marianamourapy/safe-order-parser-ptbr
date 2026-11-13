# Conjunto novo (78 frases, outro LLM, rotuladas pela autora)

Avaliação definida em PREREGISTRATION.md antes de rotular e de rodar qualquer sistema.

| Métrica | Regras (baseline) | Qwen + LoRA (leitura oficial) | Qwen + LoRA, descartando valores inválidos | Híbrido (pré-registrado) |
|---|---|---|---|---|
| **Acerto exato (principal)** | **38%** [28–50] | **37%** [27–48] | **37%** [27–48] | **49%** [38–60] |
| Micro-F1 dos campos | 78% | 66% | 67% | 77% |
| JSON válido | 100% | 96% | 99% | 100% |
| Intenção correta | 76% | 85% | 85% | 85% |
| Fora de escopo detectado | 0/19 | 11/19 | 11/19 | 11/19 |
| Restrições completas | 90% (n=10) | 90% (n=10) | 100% (n=10) | 90% (n=10) |
| Alerta de saúde (recall) | 83% (n=6) | 67% (n=6) | 67% (n=6) | 83% (n=6) |
| Inventou campos em pedido vazio | 40% (n=5) | 60% (n=5) | 60% (n=5) | 40% (n=5) |

## Análise adicional (não pré-registrada): teste pareado de McNemar

Os sistemas responderam às mesmas frases, então dá para comparar só as frases em que um acertou e o outro errou. Valor-p exato, bilateral.

| Comparação | Só o híbrido acertou | Só o outro acertou | Valor-p |
|---|---|---|---|
| Híbrido x Regras (baseline) | 11 | 3 | 0.057 |
| Híbrido x Qwen + LoRA (leitura oficial) | 15 | 6 | 0.078 |
