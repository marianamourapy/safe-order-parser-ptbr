"""Demo: mensagem -> pedido estruturado -> filtro no catálogo fictício.

Roda como Space do Hugging Face (SDK Gradio) ou localmente: `python demo/app.py`.
Defina ADAPTER_ID com o repositório do adaptador LoRA para usar o modelo ajustado;
sem isso, a demo usa o baseline por regras, para o filtro poder ser testado sozinho.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import gradio as gr

from order_parser.catalog import recomendar, violacoes
from order_parser.output_format import de_json, mensagens, para_json
from order_parser.schema import Pedido
from order_parser.session import PerfilSessao

ADAPTER_ID = os.environ.get("ADAPTER_ID")
_modelo = None


def _carregar():
    global _modelo
    if _modelo is None:
        import torch
        from peft import AutoPeftModelForCausalLM
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(ADAPTER_ID)
        model = AutoPeftModelForCausalLM.from_pretrained(ADAPTER_ID, torch_dtype=torch.float32)
        model.eval()
        _modelo = (tok, model)
    return _modelo


def interpretar(texto: str) -> tuple[Pedido, str]:
    if not ADAPTER_ID:
        from order_parser.baseline import prever
        return prever(texto), "baseline por regras"
    import torch
    tok, model = _carregar()
    prompt = tok.apply_chat_template(mensagens(texto), tokenize=False, add_generation_prompt=True)
    enc = tok(prompt, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=128, do_sample=False)
    bruto = tok.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True)
    try:
        return de_json(bruto), "modelo ajustado"
    except Exception:
        return Pedido(), "modelo ajustado (saída inválida, tratada como pedido vazio)"


def responder(texto, historico, perfil):
    perfil = perfil or PerfilSessao()
    pedido, origem = interpretar(texto)
    efetivo = perfil.atualizar(pedido)
    so_declarou = pedido.intent == "pedido" and not (pedido.categories or pedido.wishes or pedido.exclude_categories
                                                      or pedido.max_price or pedido.people or pedido.free_delivery
                                                      or pedido.max_delivery_min or pedido.min_rating)
    if so_declarou and (pedido.restrictions or pedido.exclude_ingredients or pedido.health_alert):
        from order_parser.catalog import Resposta
        r = Resposta("Anotado. Vou aplicar isso a todas as sugestões desta conversa. O que você quer comer?")
    else:
        r = recomendar(efetivo)
    assert not violacoes(efetivo, r.itens)
    partes = ["\n".join("⚠️ " + a for a in r.avisos), r.texto,
              f"`extraído ({origem}): {para_json(pedido)}`", f"`aplicado com o perfil da sessão: {para_json(efetivo)}`"]
    historico = (historico or []) + [{"role": "user", "content": texto},
                                     {"role": "assistant", "content": "\n\n".join(p for p in partes if p)}]
    return "", historico, perfil


with gr.Blocks(title="safe-order-parser-ptbr") as app:
    gr.Markdown("# Do desejo ao pedido\nRestrições alimentares que viram filtro, não só aviso. "
                "**Catálogo, restaurantes e preços são fictícios.** Não use para decisões reais sobre alergias.")
    chat = gr.Chatbot(type="messages", height=420)
    caixa = gr.Textbox(placeholder="Ex.: sou celíaca e vegetariana", label="Mensagem")
    perfil = gr.State()
    gr.Examples(["tenho alergia a leite", "me sugere um doce", "sou celíaca e vegetariana", "me vê uma pizza",
                 "quero um lanche", "sou vegano, mas me vê churrasco", "pizza pra 2, um é vegano, até 120 reais"], caixa)
    caixa.submit(responder, [caixa, chat, perfil], [caixa, chat, perfil])
    gr.Button("Nova conversa").click(lambda: ([], None), None, [chat, perfil])

if __name__ == "__main__":
    app.launch()
