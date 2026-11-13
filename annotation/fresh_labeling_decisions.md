# Decisões de rotulagem do conjunto novo

Rótulos escritos por Mariana Moura com `LABELING.md`, em 11 a 13/11/2026, sem ver a saída de nenhum sistema.
Depois da primeira passada, os rótulos foram conferidos contra o guia, também sem rodar nenhum sistema. A autora decidiu cada ponto:

| id | Mensagem | Decisão |
|---|---|---|
| n004 | açaí caprichado no leite em pó | Sem `farto`: "caprichado no X" é acréscimo de ingrediente, que o guia ignora |
| n020 | lanche vegano sem queijo sem maionese | Só `vegano`: o guia manda não duplicar exclusões já cobertas pela restrição |
| n026 | porção de fritas | Pedido vazio: batata frita não tem categoria |
| n038 | risoto sem frutos do mar | Sem categoria: risoto não está no guia (não é `massa`) |
| n042 | feijoada individual | Mantido `people: 1`. A autora entende "individual" como explícito; o guia só cita "só pra mim" |
| n067 | coca zero e batata grande | Só `bebida`: batata frita não tem categoria |
| n077 | o combo serve dois? | Mantido `fora_escopo`: pergunta sobre o rendimento de um item do cardápio, que o assistente não tem como responder |

Casos não cobertos pelo guia e decididos pela autora: batata frita e porções (sem categoria), risoto (sem categoria), "não como porco" (`exclude_ingredients: porco`).
