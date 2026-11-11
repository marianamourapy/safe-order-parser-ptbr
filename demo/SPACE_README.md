---
title: Safe Order Parser PT-BR
emoji: 🍽️
colorFrom: red
colorTo: yellow
sdk: gradio
app_file: app.py
pinned: false
license: mit
short_description: Restrições alimentares que viram filtro, não só aviso
---

# Do desejo ao pedido

Demo do projeto [safe-order-parser-ptbr](https://github.com/marianamourapy/safe-order-parser-ptbr): um Qwen2.5-1.5B ajustado com LoRA lê a mensagem e devolve um pedido estruturado; um filtro com regras fixas aplica as restrições alimentares a um catálogo fictício e lembra delas durante a conversa.

**Catálogo, restaurantes e preços são fictícios. Não use para decisões reais sobre alergias.**

O modelo erra: ele perde o alerta de saúde em parte dos casos e às vezes inventa campos. Resultados, análise de erros e limitações estão no repositório.
