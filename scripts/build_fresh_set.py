"""Transforma a planilha rotulada pela autora no conjunto novo e o congela.

Uso: PYTHONPATH=src python scripts/build_fresh_set.py annotation/fresh_labeling.xlsx

Gera data/test/test_fresh_llm.jsonl, valida cada rótulo no schema e registra o hash
em data/test/FROZEN_FRESH.md. Rodar uma vez, antes de qualquer sistema ver essas frases.
"""
import datetime
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agreement import ler  # noqa: E402

from order_parser.output_format import para_json  # noqa: E402
from order_parser.schema import Pedido  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "data/test/test_fresh_llm.jsonl"
REGISTRO = RAIZ / "data/test/FROZEN_FRESH.md"


def main(caminho):
    if REGISTRO.exists():
        sys.exit("O conjunto novo já foi congelado. Não gere de novo.")
    linhas, erros = [], []
    for i, texto, bruto in ler(caminho):
        try:
            p = Pedido.model_validate(bruto)
        except Exception as e:
            erros.append(f"{i}: {str(e).splitlines()[0]} | {texto}")
            continue
        linhas.append({"id": i, "texto": texto, "rotulo": json.loads(para_json(p)), "tag": "fresh_llm"})
    if erros:
        sys.exit("Corrija estes rótulos na planilha e rode de novo:\n" + "\n".join(erros))
    SAIDA.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas), encoding="utf8")
    h = hashlib.sha256(SAIDA.read_bytes()).hexdigest()
    REGISTRO.write_text(
        "# Conjunto novo congelado\n\n"
        f"Congelado em {datetime.date.today().isoformat()}, antes de qualquer sistema ser avaliado nele.\n"
        "Mensagens escritas por outro LLM (GPT-6 Astra), rotuladas pela autora com LABELING.md.\n"
        "Duas mensagens foram removidas por serem iguais ou parecidas com frases já existentes "
        "(data/test/raw/fresh_llm_removed.txt).\n\n"
        "| Arquivo | Frases | SHA-256 |\n|---|---|---|\n"
        f"| `test_fresh_llm.jsonl` | {len(linhas)} | `{h}` |\n", encoding="utf8")
    print(f"{len(linhas)} frases congeladas. SHA-256: {h}")


if __name__ == "__main__":
    main(sys.argv[1])
