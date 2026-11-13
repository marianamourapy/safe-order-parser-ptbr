"""Registra os hashes dos conjuntos de teste em FROZEN.md.

Rodar só antes da primeira avaliação de qualquer modelo. Depois disso, o teste
não muda mais, e tests/test_conjunto_teste.py falha se algum arquivo for alterado.
"""

import datetime
import hashlib
from pathlib import Path

PASTA = Path(__file__).resolve().parent
ARQUIVOS = ["test_main.jsonl", "test_author2.jsonl", "test_human.jsonl", "test_human_safety.jsonl",
            "test_human_restaurant.jsonl"]

linhas = [
    "# Conjunto de teste congelado", "",
    f"Congelado em {datetime.date.today().isoformat()}, antes de qualquer modelo ser avaliado.",
    "Qualquer mudança nestes arquivos invalida a comparação com resultados anteriores.", "",
    "## Histórico", "",
    "- 07/11/2026: primeiro congelamento.",
    "- 09/11/2026: só os nomes das chaves do rótulo passaram para inglês (ex.: `preco_max` → `max_price`).",
    "  Textos e valores verificados idênticos por script. Até aqui, só o baseline por regras tinha sido",
    "  avaliado, e as métricas dele continuaram idênticas. Nenhum modelo de linguagem foi avaliado antes.",
    "- 10/11/2026: novo conjunto `test_human_restaurant.jsonl` (63 mensagens reais para um restaurante, em quatro lotes no mesmo dia),",
    "  incluído antes da primeira avaliação de um modelo de linguagem.",
    "- 13/11/2026: em `test_human_restaurant.jsonl`, o nome de um bairro (frase `r011`) foi trocado por `[bairro]`, para não",
    "  expor a localização de quem escreveu. Rótulo inalterado; a saída do baseline para a frase é a mesma. Os modelos foram",
    "  avaliados com o texto original, que difere só nesse nome.", "",
    "| Arquivo | Frases | SHA-256 |", "|---|---|---|",
]
for nome in ARQUIVOS:
    dados = (PASTA / nome).read_bytes()
    n = dados.decode("utf8").count("\n")
    linhas.append(f"| `{nome}` | {n} | `{hashlib.sha256(dados).hexdigest()}` |")
(PASTA / "FROZEN.md").write_text("\n".join(linhas) + "\n", encoding="utf8")
print("\n".join(linhas))
