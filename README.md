# Do desejo ao pedido

Modelo pequeno, ajustado com fine-tuning, que transforma mensagens informais de delivery em português ("tô morta, quero algo leve sem lactose até 40 conto") em um pedido estruturado em JSON, e que separa pedidos de emergências, ataques e mensagens fora de escopo.

> Rascunho. Resultados, limitações e o texto final entram quando os experimentos terminarem.

## Como o sistema funciona

```
mensagem → [modelo] → JSON do pedido → [filtro no catálogo] → [resposta por template]
                         │
                         └─ intencao = emergencia / ataque / fora_escopo → resposta fixa de segurança
```

O modelo só interpreta. Preço, disponibilidade e avisos de segurança vêm de dados e regras fixas, nunca do modelo.

## Estrutura

| Caminho | O que é |
|---|---|
| `src/order_parser/schema.py` | O schema: campos, valores permitidos e validações |
| `src/order_parser/output_format.py` | Instrução do sistema e conversão entre JSON e `Pedido` |
| `src/order_parser/generator.py` | Gerador de dados de treino (sorteia o rótulo, depois escreve o texto) |
| `LABELING.md` | Guia de rotulagem: as regras do que é a resposta certa |
| `data/test/` | Conjuntos de teste (congelados; ver `FROZEN.md`) |
| `data/train/` | Treino e validação gerados |
| `tests/` | Testes automatizados (pytest) |

## Como rodar

```bash
python -m venv .venv && source .venv/bin/activate
pip install pydantic pytest openpyxl pandas
pytest -q                                              # testes do código
python -m order_parser.generator --n 4000 --seed 7             # gera data/train/
```

(No Windows, ative o ambiente com `.venv\Scripts\activate`. Rode a partir da raiz do projeto, com `src` no `PYTHONPATH`; o pytest já faz isso pelo `pyproject.toml`. Para o gerador: `PYTHONPATH=src python -m order_parser.generator ...`.)
