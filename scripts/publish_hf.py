"""Publica no Hugging Face o cartão do modelo e, opcionalmente, a demo (Space privado).

Uso: python scripts/publish_hf.py SEU_USUARIO [--space]

Desde julho de 2026, criar um Space Gradio em CPU exige assinatura PRO no Hugging Face.
Sem --space, o script publica só o cartão do modelo.

Na primeira vez, pede o token do Hugging Face no terminal (a digitação fica oculta).
O token nunca é escrito em arquivo do repositório.
"""
import shutil
import sys
import tempfile
from pathlib import Path

from huggingface_hub import HfApi, get_token, login

RAIZ = Path(__file__).resolve().parents[1]


def main():
    args = [a for a in sys.argv[1:] if a != "--space"]
    if len(args) != 1:
        sys.exit("Uso: python scripts/publish_hf.py SEU_USUARIO [--space]")
    usuario = args[0]
    modelo = f"{usuario}/safe-order-parser-ptbr-qwen2.5-1.5b-lora"
    space = f"{usuario}/safe-order-parser-ptbr"
    if not get_token():
        login()
    api = HfApi()

    api.upload_file(path_or_fileobj=str(RAIZ / "MODEL_CARD.md"), path_in_repo="README.md", repo_id=modelo,
                    commit_message="docs: add model card with evaluation results")
    print("cartão do modelo publicado:", modelo)
    if "--space" not in sys.argv:
        return

    api.create_repo(space, repo_type="space", space_sdk="gradio", private=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copy(RAIZ / "demo/app.py", tmp / "app.py")
        shutil.copy(RAIZ / "demo/SPACE_README.md", tmp / "README.md")
        (tmp / "requirements.txt").write_text("pydantic>=2\ntransformers\npeft\ntorch\n", encoding="utf8")
        shutil.copytree(RAIZ / "src/order_parser", tmp / "order_parser", ignore=shutil.ignore_patterns("__pycache__"))
        api.upload_folder(folder_path=str(tmp), repo_id=space, repo_type="space", commit_message="feat: add demo")
    api.add_space_variable(space, "ADAPTER_ID", modelo)
    # enquanto o modelo for privado, o Space precisa de um token para baixá-lo
    api.add_space_secret(space, "HF_TOKEN", get_token())
    print("demo publicada (privada): https://huggingface.co/spaces/" + space)


if __name__ == "__main__":
    main()
