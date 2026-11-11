# Do desejo ao pedido

**Restrições alimentares que viram filtro, não só aviso.** Um modelo pequeno (Qwen2.5 de 1,5 bilhão de parâmetros), ajustado com LoRA, transforma mensagens informais de delivery em português em um pedido estruturado. Um filtro aplica esse pedido como regra obrigatória sobre um catálogo.

```
"sou celíaca e vegetariana" ... "me vê uma pizza"
        │
        ▼  modelo ajustado (só interpreta)
{"categories":["pizza"],"restrictions":["sem_gluten","vegetariano"],"health_alert":true}
        │
        ▼  filtro (regra fixa) + perfil da sessão (lembra das restrições)
só pizzas vegetarianas e sem glúten, com aviso de contato cruzado
```

> Projeto de portfólio. O catálogo é fictício e o sistema **não** deve ser usado para decisões reais sobre alergias.

## Por que este problema

Em um teste exploratório com o Ailo, o assistente do iFood no WhatsApp (4 conversas, uma pessoa, uma região), o texto das respostas reconhecia as restrições, mas a lista de sugestões não as aplicava: brigadeiro e pudim depois de "tenho alergia a leite", pizza de calabresa depois de "sou celíaca e vegetariana". O teste também registrou pontos fortes do Ailo, como pedir confirmação quando um pedido contradiz uma alergia. Detalhes, limites e o que **não** dá para concluir estão em [`audit/FINDINGS.md`](audit/FINDINGS.md).

A hipótese deste projeto: tratar a restrição como **dado estruturado e filtro**, e não como texto, elimina essa classe de erro.

## Resultados

<!-- RESULTADOS: cole aqui o conteúdo de results/summary.md depois de rodar notebooks/train_eval.ipynb -->
_A preencher com a saída do notebook: regras, Qwen sem ajuste, Qwen com 8 exemplos no prompt e Qwen com LoRA, nos quatro conjuntos de teste._

O que já está medido, com o baseline por regras: o acerto exato cai de 66% nas frases escritas pelo autor do gerador para 38% nas mensagens reais de clientes, e as regras deixam passar 44% das emergências. É esse espaço que o modelo ajustado precisa ocupar.

O filtro, por construção, não devolve item que viole uma restrição: um teste automatizado percorre todas as combinações de até 3 restrições e reproduz as conversas da auditoria.

## Como a avaliação foi feita

| Conjunto | Frases | Quem escreveu |
|---|---|---|
| `test_main` | 438 | LLM (Claude), incluindo 25 emergências e 25 ataques |
| `test_author2` | 100 | Outro LLM, sem ver o conjunto principal |
| `test_human` | 30 | Pessoas |
| `test_human_restaurant` | 63 | Pessoas: mensagens reais para um restaurante |
| `test_human_safety` | 10 | Pessoa, depois de ler a descrição das categorias (não independente) |

- **Teste congelado antes de avaliar qualquer modelo de linguagem**, com hashes em [`data/test/FROZEN.md`](data/test/FROZEN.md) e um teste automatizado que falha se um arquivo mudar.
- **Treino sintético, com rótulo por construção:** o gerador sorteia o pedido e depois escreve a frase. Um filtro remove do treino o que for parecido demais com o teste.
- **Métricas:** acerto exato, F1 por campo, completude das restrições (extrair uma de duas conta como erro), recall de emergência e de ataque, e taxa de campos inventados. Proporções vêm com intervalo de Wilson de 95%.
- **Comparações:** regras escritas à mão, modelo sem ajuste e modelo com exemplos no prompt. Sem a última, não daria para dizer se treinar foi necessário.
- **Concordância de rotulagem:** _a preencher com `annotation/agreement.md` (50 frases rotuladas às cegas pela autora)._

## Limitações

- **Poucos dados humanos (93 frases).** Os intervalos nesses conjuntos são largos; diferenças pequenas entre sistemas não são conclusivas.
- **O conjunto principal e o gerador de treino têm o mesmo autor (um LLM).** O resultado nele é otimista; os conjuntos de outros autores existem para medir isso.
- **Parte das regras de rotulagem foi escrita depois de ver frases de teste.** O guia é a especificação, mas isso favorece todos os sistemas que o seguem.
- **As mensagens reais foram escritas para um restaurante, não para um assistente.** Muitas são perguntas sobre cardápio e preço, que o schema representa mal.
- **O filtro pressupõe um catálogo com ingredientes e marcações confiáveis.** Em cardápios reais isso costuma faltar, e inferir esses atributos é outro problema.
- **Uma mensagem por vez.** O modelo não lê o histórico; quem lembra das restrições é o perfil da sessão. Pedidos como "o de sempre" ou "troca a bebida" não são representados.
- **Detecção de emergência por um modelo de 1,5 B não é solução de segurança.** Um sistema real precisa de moderação dedicada e encaminhamento humano.
- **A auditoria do Ailo é uma observação pequena**, não uma medida da qualidade do produto.

## Estrutura

| Caminho | O que é |
|---|---|
| `src/order_parser/schema.py` | Campos, valores permitidos e validações |
| `src/order_parser/generator.py` | Gerador de dados de treino |
| `src/order_parser/metrics.py`, `scripts/evaluate.py`, `scripts/compare.py` | Métricas e tabelas |
| `src/order_parser/baseline.py` | Baseline por regras |
| `src/order_parser/session.py`, `src/order_parser/catalog.py` | Perfil da sessão, catálogo fictício e filtro |
| `notebooks/train_eval.ipynb` | Avaliação dos modelos e fine-tuning (Colab, GPU T4) |
| `demo/app.py` | Demo em Gradio |
| `LABELING.md` | Guia de rotulagem |
| `data/test/`, `data/train/` | Testes congelados; treino e validação gerados |

## Como reproduzir

```bash
pip install pydantic pytest pandas openpyxl
pytest -q                                                        # 35 testes
PYTHONPATH=src python -m order_parser.generator --n 4000 --seed 7   # recria data/train/
PYTHONPATH=src python scripts/evaluate.py --sistema baseline        # baseline nos testes
```

Para os modelos: abra `notebooks/train_eval.ipynb` no Colab com GPU T4, envie o zip do repositório e execute tudo.

## Autoria e uso de IA

Projeto de Mariana Moura. O que eu fiz:

- **Defini o problema a partir de um teste real.** Conduzi a auditoria exploratória do Ailo no WhatsApp e identifiquei o padrão que orienta o projeto: o texto reconhece a restrição, a lista de sugestões não a aplica.
- **Coletei e organizei os dados humanos:** 93 mensagens de pessoas do meu convívio, incluindo 63 mensagens reais para um restaurante.
- **Tomei as decisões de projeto**, registradas no histórico de commits: separar emergências e ataques de pedidos comuns com um campo de intenção, tratar contradições como caso de treino, manter os dados humanos sem edição, e trocar as chaves do JSON para inglês depois de medir a economia de 13% em tokens.
- **Executei os experimentos e analisei os resultados**, incluindo a rotulagem às cegas de 50 frases para medir a concordância dos rótulos.

Usei um assistente de IA (Claude) como ferramenta de desenvolvimento: ele escreveu boa parte do código e o conjunto de teste sintético principal, sob a minha direção e com a minha revisão. Declaro isso porque a avaliação depende de saber quem escreveu cada conjunto de dados.

## Licença e modelo base

Código sob licença MIT. Modelo base: [Qwen/Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct), Apache 2.0.
