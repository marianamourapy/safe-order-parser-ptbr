# Guia de rotulagem

Regra geral: **só rotule o que está explícito ou é inequívoco.** Na dúvida, deixe vazio. O modelo não deve inventar nada que a pessoa não disse.

## Intenção (decidir primeiro)
Prioridade: **emergencia > ataque > fora_escopo > pedido**. Se a intenção não é `pedido`, todos os outros campos ficam vazios.
- `emergencia`: violência (sofrida ou presenciada), ameaça, risco de autolesão ou suicídio, emergência médica acontecendo agora (reação alérgica, desmaio, engasgo, dor no peito, overdose). Vale mesmo se a mensagem também pedir comida.
- `ataque`: tentar ver ou mudar instruções do sistema, pedir dados de outras pessoas ou do sistema, dar ordens sobre o formato da saída, fingir autoridade ("sou do time do iFood"), fraude (cupom falso, link falso, pedido no nome de outra pessoa).
- `fora_escopo`: suporte (status, cancelamento, reembolso, reclamação), saudação, perguntas sobre o assistente, mercado, farmácia e remédio comum, itens que não são comida.
- `pedido`: quer comida, mesmo que seja vago ("não sei o que quero") ou que nada caiba no schema ("pede o de sempre").
- **Alergia não é emergência por si só:** "tenho alergia a amendoim, quero um doce" é `pedido` com `health_alert`. "Comi amendoim e minha garganta tá fechando" é `emergencia`.

## Números
- **Preço:** "até X", "no máximo X", "menos de X", "uns X", "na faixa de X" e "X conto/pila/reais" viram `max_price = X`. Valores por extenso também ("cinquenta conto" = 50).
- **Tempo:** "meia hora" = 30, "uma hora" ou "1h" = 60, "uma hora e meia" = 90, "40 min" = 40.
- **Nota:** "acima de 4,5", "4.5 pra cima" e "nota mínima 4,5" viram `min_rating = 4.5`.
- **Pessoas:** número explícito, "eu e X" ou "casal" = 2. "Galera" ou "família" sem número = vazio.
- **Sem número → desejo:** "barato", "em conta", "promo" e "sem grana" viram `barato`; "rápido" e "logo" viram `rapido`; "bem avaliado" e "nota boa" viram `bem_avaliado`. Nunca invente um número.
- **Frete:** "frete grátis", "entrega grátis" e "sem taxa de entrega" viram `free_delivery = true`. "Frete incluído no valor" não é representado (limitação).

## Categorias
- A categoria é o **tipo de prato pedido**. A proteína só entra quando ela *é* o pedido ("quero frango", "picanha", "peixe grelhado"). "Strogonoff de frango" é só `brasileira`.
- `japonesa`: sushi, temaki, japa · `chinesa`: yakisoba, frango xadrez · `arabe`: esfiha, shawarma, kafta · `mexicana`: taco, burrito · `massa`: macarrão, lasanha, nhoque · `brasileira`: feijoada, strogonoff, moqueca, baião de dois, cuscuz, acarajé, "comida mineira" · `marmita`: marmita, marmitex, quentinha, PF, executivo · `hamburguer`: hambúrguer, x-tudo, xis, smash · `lanche`: cachorro-quente, dogão, podrão, misto, beirute · `salgado`: coxinha, pastel, joelho, kibe, empada · `cafe_padaria`: pão de queijo, pão na chapa, café, padoca, café da manhã · `sorvete`: sorvete, milkshake, geladinho, dindin · `doce`: sobremesa, bolo, brigadeiro, brownie · `bebida`: refri, suco, mate, caldo de cana.
- "Almoço" ou "jantar" sozinhos não são categoria.
- "Quero salgado" no sentido de *comida salgada* (oposto de doce) não é a categoria `salgado`.

## Exclusões e restrições
- Categoria excluída ("nada de pizza", "sem carne") vai para `exclude_categories`. Ingrediente excluído ("sem cebola", "sem camarão") vai para `exclude_ingredients`. "Sem fritura" ou "nada frito" vira o ingrediente `fritura`.
- Se existe uma restrição para o ingrediente, use a restrição: "sem lactose" vira `sem_lactose`, e "sem amendoim" vira `sem_amendoim`.
- `vegetariano` só quando é explícito ou "não como carne nenhuma". "Sem carne" sozinho vira `exclude_categories: carne`.
- Não duplique: "vegano, sem leite nem ovo" é só `vegano`.

## Escopo: todos ou pelo menos um
- `restrictions`: toda opção precisa atender ("todo mundo é vegetariano").
- `partial_restrictions`: basta uma opção atender ("um é vegano", "pelo menos uma vegetariana"). Em grupo, "um não come carne" vira `partial_restrictions: vegetariano`.
- Se todas as pessoas têm restrições, a interseção vale para todos. "Um vegano e um vegetariano" vira `restrictions: vegetariano` e `partial_restrictions: vegano`.

## Alerta de saúde
- `health_alert = true` quando a pessoa cita alergia, doença celíaca, diabetes, intolerância ou "passo mal com X". Escolhas como vegetariano e vegano não ativam o alerta.
- Com alerta, converta para a restrição mais conservadora que exista: alergia a camarão vira `sem_frutos_do_mar`.
- **Alergia a leite não é intolerância a lactose.** Produtos sem lactose ainda têm proteína do leite, então vira `exclude_ingredients: leite`, e não `sem_lactose`.

## Fora do schema: ignorar, nunca inventar
- **Distância** ("perto de mim", "até 3 km"), **agendamento**, **pagamento** (pix, vale-refeição, Carteira), **retirada** e **restaurante aberto agora** não têm campo: ignore e rotule o resto da frase.
- **Mercado e farmácia** estão fora do escopo da v1, que cobre só restaurantes: tudo vazio.
- **Observações:** só remoções viram `exclude_ingredients`. Pedidos para acrescentar algo ("capricha no molho") são ignorados.
- **"Super-Restaurantes"** e "menor tempo de entrega" viram os desejos `bem_avaliado` e `rapido`.
- **Tempo** só quando a pessoa fala do prazo de entrega. "Reunião em 30 min" vira `rapido`, e não `max_delivery_min = 30`.
- **Quantidade de itens não é número de pessoas:** "4 pizzas" não vira `people = 4`. **Mililitros não são preço:** "açaí de quinhentos" não vira `max_price = 500`.
- "Dindin" pode ser **dinheiro** ("tô sem dindin") ou **sorvete** ("um dindin de coco"); decida pelo contexto. "Pizza doce" é `pizza`. "Coxinha de frango" é `salgado`. "Frango à parmegiana" é `frango`. Sopa não tem categoria.
- **Erros de digitação:** o rótulo usa a grafia correta ("sebola" vira `cebola`).

## Desejos (gatilhos)
- `farto`: bem servido, caprichado, rende bastante, que sustente, grande, "com tudo que tem direito". "Capricha aí" dirigido ao assistente não conta.
- `bem_avaliado`: bem avaliado, nota boa/alta, "os melhores", top, Super-Restaurantes. `barato`: barato, em conta, promo, "não tão caro", custo-benefício, sem grana.
- `caseiro`: comida de vó, de casa, de panela, "comida de verdade". `diferente`: algo novo, me surpreende, "não aquilo de ontem".

## Ajustes do lote humano 2
- **Preço com número não leva `barato`:** "rápido, menos de 30 reais" vira `max_price = 30` e `rapido`. `barato` só existe quando não há valor.
- **Frete barato** (não grátis) não é representado.
- **"Pra ontem"** vira `rapido`. **"2 duplas"** vira `people = 4`.
- **Pedido que contradiz uma restrição** ("não posso comer camarão, mas me vê um bobó de camarão"): rotule as duas coisas. O conflito fica visível no JSON, e o sistema decide o que fazer (avisar e não recomendar).
- **Colesterol alto** também ativa `health_alert`.
- **"Salada de frutas pra sobremesa"** é `doce`, e não `salada`.
- **Não comida** (cigarro, por exemplo) é fora de escopo: tudo vazio.

## Pessoas e preço
- `people = 1` só quando é explícito ("só pra mim", "vou jantar sozinho").
- `max_price` é o **total do pedido**. Preço por unidade ("22 reais cada") não é representado.
- Tapioca, cuscuz, empadão e pratos regionais (tacacá, barreado, arroz com pequi) são `brasileira`. Parmegiana sem proteína dita é `brasileira`.
- `health_alert` também vale para gestação ("pra gestante") e pressão alta.

## Outros casos
- Mudança de ideia na mesma mensagem: vale a última versão.
- Fora de escopo (status do pedido, cancelamento, saudação): tudo vazio.
- Limitação conhecida: o schema não representa desejos ou exclusões de ingredientes que valem só para uma pessoa do grupo.
