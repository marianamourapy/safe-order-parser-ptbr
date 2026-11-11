"""Garante que o conjunto de teste não mudou desde o congelamento."""
import hashlib
import re
from pathlib import Path

PASTA = Path(__file__).resolve().parents[1] / "data" / "test"


def test_hashes_batem_com_o_congelamento():
    registro = (PASTA / "FROZEN.md").read_text(encoding="utf8")
    pares = re.findall(r"`([\w.]+\.jsonl)` \| \d+ \| `([0-9a-f]{64})`", registro)
    assert len(pares) == 5
    for nome, esperado in pares:
        assert hashlib.sha256((PASTA / nome).read_bytes()).hexdigest() == esperado, nome
