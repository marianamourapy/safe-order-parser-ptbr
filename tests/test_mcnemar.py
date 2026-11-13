import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evaluate_fresh import mcnemar_exato  # noqa: E402


def test_mcnemar_conta_so_discordancias():
    a = [True, True, True, False, True]
    b = [True, False, False, False, True]
    assert mcnemar_exato(a, b)[:2] == (2, 0)


def test_mcnemar_valor_p_conhecido():
    # 11 contra 3: P(X <= 3 | n=14, p=0,5) * 2 = 0,0574
    a = [True] * 11 + [False] * 3
    b = [False] * 11 + [True] * 3
    assert abs(mcnemar_exato(a, b)[2] - 0.0574) < 1e-3
