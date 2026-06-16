# Transcricao - Reuniao com a gestora (Doces Vo Nena)

- Gerado em: 14/06/2026 15:40
- Modelo: faster-whisper `medium` (idioma: pt)
- Participantes: **Gestora** (apoia o dono na gestao) e **Leo**

> Locutores **inferidos pelos trechos** (Gestora / Leo) na *Leitura organizada*
> abaixo; a transcrição crua com tempos [mm:ss] vem logo depois para conferência.
> Correções do Whisper: "CIG/CMTJ/CPT" = **SIGE** · "cocava/focada" = **cocada** ·
> "Streamlight" = **Streamlit** · "rasterabilidade" = **rastreabilidade**.

## Leitura organizada — quem fala + termos corrigidos

> Síntese legível por tema. Atribuição de locutor é uma **inferência** a partir do
> conteúdo (não há marcação de canais no áudio); confira pelos tempos na crua.

**1. Rotina do Leo na fábrica + o TCC** _[~00:00–00:48]_
- **Leo:** todo dia define o que a equipe **corta** (bandeja), **produz** e **embala**;
  de tarde desenvolve o sistema, que é o **TCC**. Grava as conversas e transcreve
  para registrar tudo.

**2. Como o SIGE fecha o ciclo de materiais** _[~00:49–02:34]_
- **Leo:** pede para a Gestora repetir a ligação entre o **SIGE** e o **XML**.
- **Gestora:** a **NF-e entra por XML e abastece o estoque automaticamente**
  (ex.: nota de 10 kg de coco). A Fazenda gera o XML; o SIGE puxa as notas; você
  **confere os itens e dá entrada**. Ao **gerar a ordem de produção, o SIGE baixa o
  estoque sozinho** → fecha o ciclo **sem preencher nada manual**.

**3. Rendimento como sinal de problema** _[~04:01–05:06]_
- **Gestora:** cada receita rende **~7 kg de cocada**; se fizeram **10** e deviam
  render **70** mas **rendeu 60**, há um erro — leite com mais água, não chegou no
  ponto, alguém demorou (mais tempo = mais água evapora) e a cocada fica mais dura.
  O **rendimento baixo dispara a investigação** e o controle por etapa.

**4. O sistema / TCC do Leo** _[~05:24–12:50]_
- **Leo:** começou só para **passar a folha de produção pro computador** (tela de
  Lançamento); hoje extrai **Curva ABC**, **média móvel**, **parâmetros por dia**
  (ex.: 5.200 cocada tradicional na segunda, metade disso de leite condensado) e
  gráficos de cortados. Hospeda no **Streamlit**; comentou o **Power BI** (acha caro
  e que expõe dados publicamente).
- **Nota de privacidade (Leo):** em dashboard público, **não colocar logo /
  identificação** da empresa — quem acessa o link só **visualiza**, não sabe de quem
  é nem altera nada.

**5. Explorar o módulo de produção do SIGE** _[~12:54–14:42]_
- **Gestora:** pede para o Leo **mexer no PCP do SIGE** e avaliar se funciona.
- **Leo:** primeira impressão — está **vazio** (sem dados, sem produção, sem
  cadastro de produto; controle manual).

**6. O fluxo da Ordem de Produção** _[áudio curto, ~00:01–00:50]_
- **Gestora:** **imputa as fichas técnicas no SIGE**; ao **gerar a OP** (ex.: 10
  receitas de cocada tradicional) o SIGE **separa coco/leite e pré-reserva no
  estoque** (some da necessidade de compra); o **estoquista dá baixa confirmando os
  lotes** (**rastreabilidade**); ao **finalizar a OP, registra o rendimento** das
  receitas.

---

## Audio longo (~15 min) - `audio_limpo.mp3`

- **[00:00]** É muito bom que a gente entenda com a população, mas ao mesmo tempo a gente passa a ter mais um funcionário aqui dentro, que o plano fala, tá apertado aqui, faz aqui, me ajuda aqui, e aí você acaba fazendo essas coisas.
- **[00:14]** É que eu fico fazendo, isso é o que eu faço todo dia, que é definir o que eles têm que cortar de bandeja, o que eles têm que produzir, o que eles têm que embalar de calcado, e é isso que eu faço mais.
- **[00:27]** E aí à tarde eu fico desenvolvendo esse sistema, que na verdade é pro meu TCC, que eu ainda não sou formado, sabe? Eu não sou formado.
- **[00:35]** Aí é meio que isso que eu faço, mas eu quero, é entender, por isso que eu fico gravando tudo aí. Eu gravo a minha conversa, aí eu transcrevo tudo utilizando a inteligência artificial, e eu vou colocar.
- **[00:49]** Tu falou, repete só o que tu falou, das ligações entre o CIG, XML, o que tu falou agora antes?
- **[00:57]** É a entrada de nota fiscal, que entra e entra direto no sistema. E aí ele já abastece um estoque, certo?
- **[01:08]** Entra uma nota fiscal com uma quantidade de 10 quilos de coco, e ele já entra pelo XML. O XML é aquele...
- **[01:17]** Do Excel?
- **[01:19]** Sim.
- **[01:21]** Isso daqui.
- **[01:23]** Esse aqui é o XML. Tem uma numeração.
- **[01:27]** Aqui.
- **[01:29]** Ele tem uma numeração, e esse é o XML. E aí quando você acessa esse XML, a fazenda, quando ele emite a nota, ela gera esse XML.
- **[01:40]** Então o sistema, tudo que foi emitido nesse CMTJ fica lá na fazenda. E aí o CIG já puxa de lá.
- **[01:49]** Então fica lá. Todas as notas ele tem lá no relator. E você vai dando o OK se realmente essas notas são suas.
- **[01:57]** Deu o OK nessa nota, por exemplo, da rocha-pã. OK, essa nota é nossa. Você abre essa nota para conferir os itens.
- **[02:06]** Você só vai dando o OK nesses itens e dá a entrada de nota fiscal.
- **[02:10]** Quando você deu entrada, ele abasteceu no stock.
- **[02:14]** E aí quando você gera a hora de produção, ele vai dando abaixo, automaticamente, nesse stock.
- **[02:20]** Por isso que a gente consegue fechar a cadeira.
- **[02:24]** Fechar o ciclo.
- **[02:26]** Exatamente. Sem ter que fazer as partes manuais.
- **[02:31]** Manuais preenchendo lá tudo isso.
- **[02:34]** Beleza.
- **[02:53]** Sim, pronto. Eu vou dar uma focada agora. Sempre para tentar fechar isso. Beleza.
- **[03:07]** Sim.
- **[03:16]** Fique mais claro. Já tem ali os números.
- **[03:19]** Isso. Quanto mais automatizado, melhor.
- **[03:36]** Quando vê que não tem mais nada sendo acompanhado, o tanto que você fez se perdeu ali no meio.
- **[03:42]** Aí no final das contas vai diminuir os custos também, assim, desperdício também.
- **[03:47]** Isso.
- **[03:48]** Vai, vai. Os custos de... É o desperdício.
- **[03:54]** Porque os números ficam todos ali. E dá para acompanhar tudo certinho.
- **[03:59]** Pronto, fechou.
- **[04:01]** Aqui tem que ser 10, 10... Uma receita, uma...
- **[04:05]** Uma taxa de focada rendem 7 quilos de focada, por exemplo.
- **[04:11]** 7 quilos de focada.
- **[04:13]** E aí nós fizemos 10 e rendeu 60.
- **[04:17]** Tinha que render 70.
- **[04:19]** Aí você já sabe que ali tem um erro. O que aconteceu?
- **[04:23]** Foi o leite que tinha mais água.
- **[04:26]** Aí não chegou no ponto.
- **[04:29]** Alguém foi almoçar e esqueceu.
- **[04:31]** Esqueceu, né?
- **[04:32]** Tem muito tempo.
- **[04:33]** Quanto mais tempo fica mais água evapora.
- **[04:36]** O que aconteceu é que a gente tem perdido tanto.
- **[04:39]** Aí você já sabe que tem alguma coisa errada ali.
- **[04:42]** Porque na hora que você vai almoçar o rendimento, você fala, opa.
- **[04:45]** Já foi errado aqui. Chega o rendimento e você tem que render 60.
- **[04:49]** Já volta com o processo porque provavelmente essa focada vai ficar mais dura.
- **[04:54]** Provavelmente essa focada já tem que ser experimentada pra ver se ela tá no padrão.
- **[04:59]** Sim, sim.
- **[05:00]** Se realmente foram botar todos os ingredientes.
- **[05:03]** Se não esqueceram nada ou ela botada.
- **[05:06]** E aí a gente começa a entender a cada etapa usando...
- **[05:11]** Ah...
- **[05:16]** Fechou.
- **[05:20]** Eu vou entender, eu vou entender.
- **[05:22]** Eu vou entender melhor.
- **[05:24]** Não, porque o que eu tô fazendo aqui é meu TCC.
- **[05:27]** O sistema que eu tô fazendo é meu TCC.
- **[05:31]** De início o que eu queria é o quê?
- **[05:33]** Passar a folha de produção pro computador.
- **[05:36]** Só colocar a folha de produção pro computador.
- **[05:39]** E aí todo dia eu coloco aqui a folha de produção.
- **[05:42]** Tipo aqui em lançamento.
- **[05:44]** Eu coloco a folha de produção.
- **[05:46]** Isso aqui é do meu TCC.
- **[05:48]** E aí eu consigo aqui...
- **[05:53]** Eu extraí a curva BC que isso não é muito...
- **[05:57]** Cadê?
- **[05:59]** Eu extraí a curva BC do sistema.
- **[06:03]** Aqui.
- **[06:05]** Isso.
- **[06:09]** E aí aqui eu tenho a curva BC do...
- **[06:12]** E aqui tem a média móvel também.
- **[06:16]** Tipo, ele tem uns parâmetros de...
- **[06:20]** Do que ele tem que ter de produtos todo dia.
- **[06:22]** Por exemplo, na segunda-feira
- **[06:24]** ele precisa ter 5.200 calcadas tradicionais na empresa.
- **[06:27]** Contando o produto acabado e inacabado.
- **[06:29]** E aí a metade disso, lente condensada, 2.600.
- **[06:34]** Então existem parâmetros assim.
- **[06:36]** Que ele tem que...
- **[06:38]** E aí quando falta eu mando produzir.
- **[06:41]** Quando tá legal, não precisa produzir.
- **[06:44]** Eu coloco a pessoa pra ir pra outro lugar.
- **[06:46]** Fazer outra coisa.
- **[06:48]** Isso.
- **[06:50]** Essa meta, realidade.
- **[06:53]** Isso aqui é mais pra ajeitar mesmo esses parâmetros.
- **[06:56]** Então é mais isso.
- **[06:58]** Então é muita coisa.
- **[07:00]** E aí eu extraio também da folha de produção, dos números.
- **[07:04]** Construo alguns gráficos aqui de cortados.
- **[07:07]** E é mais isso meu TCC, sabe?
- **[07:10]** Eu demorei muito tempo desenvolvendo um código, sabe?
- **[07:13]** Em programas de análise de dados.
- **[07:15]** Eu fiquei muito tempo nisso aqui pra chegar nesse site aqui, sabe?
- **[07:18]** Porque se tu vê aqui no meu VS Code, tem muito...
- **[07:21]** Acacetada de coisa aqui que eu fiquei fazendo, fazendo, fazendo, fazendo.
- **[07:25]** E algumas coisas eu ainda utilizei a IA pra me ajudar.
- **[07:27]** A IA ajuda.
- **[07:29]** E eu uso muito.
- **[07:31]** Eu uso muito.
- **[07:33]** Não. É, eu uso muito.
- **[07:35]** Não precisa ficar mais codando na mão, né?
- **[07:37]** Não dá na mão.
- **[07:38]** Mas eu uso o Cloud Code aqui.
- **[07:40]** O Cloud Code é muito bom.
- **[07:42]** O Cloud Code é muito bom.
- **[07:44]** Aí eu uso direto aqui. Fiquei.
- **[07:46]** Você joga o Black Box?
- **[07:48]** Black Box? Não.
- **[07:50]** Black Box é muito legal.
- **[07:52]** Você tá gostado desse desenvolvimento de sistema?
- **[07:55]** É muito legal.
- **[07:57]** Muito legal.
- **[07:59]** Mas o Cloud Code tem me ajudado muito.
- **[08:01]** Tipo, ele...
- **[08:03]** Ou ele...
- **[08:05]** O problema é que a CPT, se você treinar...
- **[08:07]** A CPT também.
- **[08:09]** Mas esse Cloud...
- **[08:11]** Você joga todo o seu sistema lá.
- **[08:13]** Eu copio e coloco todo o seu código lá.
- **[08:15]** E ele pede pra ele analisar.
- **[08:17]** E aí ele fala o que você quer.
- **[08:19]** Meu, ele já vai fazer isso.
- **[08:21]** Ele faz tudo aqui também.
- **[08:23]** Eu não gosto de programação.
- **[08:25]** Mas assim, depois que a IA apareceu...
- **[08:28]** A minha base também de programação na universidade é pouca.
- **[08:31]** Porque a gente... Engenharia de produção.
- **[08:33]** Quem tem uma base forte de programação
- **[08:35]** é o cintos da computação.
- **[08:37]** A gente faz cintos da computação.
- **[08:39]** Mas lá na minha universidade...
- **[08:42]** Tinha uns cintos de análises de dados
- **[08:44]** que a gente via de parte.
- **[08:46]** Mas era meio que raso, sabe?
- **[08:48]** Aí eu...
- **[08:50]** Eu sei algumas coisas, porém o Cloud Code me ajuda muito.
- **[08:52]** Ele...
- **[08:54]** Os desenvolvedores dele...
- **[08:56]** Estudaram o chat IPT.
- **[08:58]** Só que eles abandonaram o chat IPT
- **[09:00]** porque eles não tinham liberdade
- **[09:02]** de implementar algum assunto de criação.
- **[09:04]** Aí eles fizeram a própria deles.
- **[09:06]** E essa IA era muito avançada.
- **[09:08]** E aí eu uso ela.
- **[09:10]** E assim eu fiquei...
- **[09:12]** Um tempão pra desenvolver esse...
- **[09:14]** Se ela te ajuda e você acostumou
- **[09:16]** usar ela, sabe usar ela bem, né?
- **[09:18]** Segue nela.
- **[09:20]** E aí eu tô tentando colocar aqui agora
- **[09:22]** um assistente de inteligência artificial
- **[09:24]** dentro dele.
- **[09:26]** E aí...
- **[09:28]** Enfim.
- **[09:30]** Tudo aqui que eu uso.
- **[09:34]** Isso aqui é uma...
- **[09:36]** É...
- **[09:38]** O que eu posso dizer?
- **[09:43]** Pra que a IA...
- **[09:52]** A IA ela lê as folhas de produção
- **[09:54]** e faz um...
- **[09:56]** Um briefing.
- **[09:58]** Briefing, eu acho que é isso que fala.
- **[10:00]** Pra IA fazer isso
- **[10:02]** eu tenho que ligar o Cloud Code
- **[10:04]** nesse...
- **[10:06]** Nesse sistema aqui.
- **[10:08]** No meu.
- **[10:12]** Mas eu posso ligar...
- **[10:14]** É isso que eu tô na península de fazer.
- **[10:16]** Eu posso ligar através de um API.
- **[10:18]** Uma chave de API.
- **[10:20]** O SIG com o meu aqui.
- **[10:22]** Mas...
- **[10:24]** Mas...
- **[10:26]** Não, eu consegui a chave com ela.
- **[10:28]** Só que aí eu lembro que deu algum errinho,
- **[10:30]** mas aí...
- **[10:32]** Se por acaso der um erro de chave,
- **[10:34]** eu consigo uma outra chave com ela.
- **[10:36]** Aí ela escolhe a chave e me gera uma nova.
- **[10:38]** Eu já conversei com a assistente.
- **[10:40]** Se eu tiver algum erro, eu vou pedir pra ela uma nova chave.
- **[10:42]** Daquele que ela dá.
- **[10:44]** Eu já conversei com a assistente.
- **[10:46]** Ah, maravilha.
- **[10:48]** É. E...
- **[10:50]** Esse Streamlight...
- **[10:52]** Streamlight é o nome desse...
- **[10:54]** É o nome desse local aqui.
- **[10:59]** Onde eu hospedei o meu sistema.
- **[11:03]** Ele é muito bom, velho.
- **[11:05]** Porque...
- **[11:07]** O interessante é quando eu consegui
- **[11:09]** gerar dashboards com ele.
- **[11:11]** E ligar...
- **[11:13]** No Power BI também.
- **[11:15]** É muita coisa pra fazer.
- **[11:17]** E aí...
- **[11:19]** O problema que eu vejo no Power BI
- **[11:21]** é que...
- **[11:23]** Ele é muito caro.
- **[11:25]** É.
- **[11:27]** Ele é muito caro.
- **[11:29]** Eu sei muito pouco dele.
- **[11:31]** Mas eu sei...
- **[11:33]** Os dados ficam...
- **[11:35]** Eles ficam públicos, né?
- **[11:37]** Esse que é o problema.
- **[11:39]** E aí qualquer pessoa que entrar,
- **[11:41]** que tiver
- **[11:43]** o link do...
- **[11:45]** Do...
- **[11:47]** Da planilha do dashboard
- **[11:49]** que você tiver movendo,
- **[11:51]** ela abre.
- **[11:53]** Abre e encontra todos os dados ali.
- **[11:55]** Então...
- **[11:57]** Ah, isso, né? Não sei.
- **[11:59]** Só apagando mesmo, né?
- **[12:01]** Só apagando.
- **[12:03]** Ou então você não coloca
- **[12:05]** nome.
- **[12:08]** Por exemplo,
- **[12:10]** logo da panela.
- **[12:12]** Não coloca nada disso.
- **[12:14]** Então você não deixa por ali.
- **[12:16]** Você deve ir lá financeiro
- **[12:18]** ou alguma coisa assim.
- **[12:20]** E aí quem acessar
- **[12:22]** de onde é não sabe de onde é.
- **[12:24]** Entendeu? Por mais que ela tenha acesso
- **[12:26]** ao link desse site,
- **[12:28]** ela não sabe de onde é.
- **[12:30]** E quando é por meio de link,
- **[12:32]** ela também não consegue fazer nenhuma operação.
- **[12:34]** Ela consegue visualizar só.
- **[12:36]** Mas nada.
- **[12:38]** O que ela pode fazer é roubar um layout,
- **[12:40]** achar legal.
- **[12:42]** Ou assim também.
- **[12:44]** Só não colocar logo, não identificar
- **[12:46]** a panela no dashboard.
- **[12:48]** E aí está tudo certo.
- **[12:50]** Beleza.
- **[12:54]** No mais é isso.
- **[12:56]** Legal. E aí num tempinho que você
- **[12:58]** tivesse você poder mexer
- **[13:00]** no PCP do CIG para ver como entende,
- **[13:02]** como você entende,
- **[13:04]** se realmente ele funciona
- **[13:06]** ou não?
- **[13:08]** Sim.
- **[13:16]** Ah, isso.
- **[13:23]** A primeira impressão que eu tive quando eu entrei,
- **[13:28]** eu achei ele meio vazio, mas eu vou
- **[13:30]** vazio assim, sabe?
- **[13:32]** A parte de dados.
- **[13:34]** Porque não tinha nada lá.
- **[13:36]** Não tinha nada.
- **[13:38]** Mas eu vou...
- **[13:40]** Mas eu coloco também.
- **[13:42]** Tudo isso.
- **[13:44]** Não tem nada de
- **[13:48]** produção
- **[13:50]** de só.
- **[13:54]** Cadastro de produtos.
- **[13:56]** Controle de só.
- **[13:58]** Manual.
- **[14:00]** Controle de base.
- **[14:02]** Ace.
- **[14:28]** Ace não tem nada.
- **[14:30]** Mas...
- **[14:42]** Fechou.

## Audio curto (~1 min) - `audio2_limpo.mp3`

- **[00:01]** Então, a lógica é a seguinte, a gente imputa as fichas técnicas dentro do CIG,
- **[00:10]** aí quando a gente fizer, gerar a ordem de produção, por exemplo, 10 receitas de cocava tradicional,
- **[00:19]** então ele vai separar a quantidade de coco, a quantidade de leite, tudo certinho,
- **[00:24]** já deixar pré-reservado no estoque, do estoque, para não aparecer para compras mais,
- **[00:32]** e aí quando o estoquista faz a retirada, ele só da abaixo, só confirma abaixo daqueles lotes,
- **[00:38]** daqueles produtos, para que a gente também consiga acompanhar a rasterabilidade desse produto,
- **[00:44]** e aí finalizou a produção, a gente só finaliza essa ordem de produção do CIG,
- **[00:50]** com o rendimento dessas receitas.

---

> Detalhamento completo em `docs/ARQUITETURA_SIGE.md` e `docs/requisitos_gestora_sige.md`.
> (Correções de transcrição: "CIG/CMTJ/CPT" = **SIGE**; "cocava/focada" = **cocada**;
> "Streamlight" = **Streamlit**; "rasterabilidade" = **rastreabilidade**.)

## O que a gestora pediu

- Fechar o ciclo de materiais **sem trabalho manual**: NF-e por XML abastece o estoque; a OP explode a ficha técnica, pré-reserva e baixa os insumos; a finalização registra o rendimento.
- **Acompanhar tudo por números** (reduzir desperdício; o que não é acompanhado "se perde no meio").
- Usar o **rendimento** como sinal de problema (planejou 70, rendeu 60 → investigar).
- **Rastreabilidade por lote** na baixa.
- Que o Leonardo **explore o módulo de produção do SIGE** (hoje vazio) e avalie se serve.
- Manter a **decisão de produção com as pessoas** (Gestão + planejamento), não com o sistema.

## Requisitos da integracao com o SIGE Cloud

- **Somente leitura** no SIGE (nosso PCP lê, não altera o ERP).
- A **OP é o ponto de ligação**: decisão humana → OP no SIGE → SIGE roda o ciclo → nosso PCP lê de volta (OPs, reservas, baixas, lotes, rendimento, estoque) para planejar, analisar e **reconciliar**.
- Reconciliar **estoque teórico do SIGE × contagem física** → divergência vira ajuste.
- Ramo de **escrita da OP isolado e desligado** até a decisão da Gestão.

## Perguntas em aberto / a confirmar com ela

- **(a)** A OP entra **manual** (uma pessoa lança) ou **via API** (nosso sistema escreve — único ponto de escrita)?
- **(b)** As **fichas técnicas** passam a ser **fonte única no SIGE** com a gente só lendo?
- **(c)** Quando começam a **lançar OPs no SIGE** (módulo hoje vazio)? Podemos fazer uma **OP de teste** pra validar os campos de rendimento? (Obs. técnica: a API **não** expõe histórico de movimentações; lotes vêm dentro da OP.)
- **(d)** **Onde** a contagem física é registrada e **quem lança o ajuste** da reconciliação (nosso PCP × SIGE)?
- **(extra)** Qual **depósito** do SIGE é o da fábrica/matéria-prima (provável "FABRICA" / PEQUENAS MORDIDAS)?
