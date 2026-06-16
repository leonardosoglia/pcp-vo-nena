# Catálogo de produtos — cruzamento foto × nossos dados (15/06/2026)

> Resultado da leitura de todas as fotos do banco (`entrevistas/fotos_produtos/`)
> cruzada com os dados do sistema. As 38 fichas `descricao.md` foram preenchidas.
> Aqui ficam só as **inconsistências / pontos a confirmar com a fábrica**,
> priorizados. "A foto manda" quando o rótulo impresso diverge do nosso dado.

## ✅ Respostas da fábrica (Leonardo, 15/06) — RESOLVIDO

- **PET Tradicional = 150 g** (mudou recentemente; o rótulo de 160 g estava
  desatualizado). Demais PET = 160 g, Zero = 100 g.
- **Pão de Mel = 1 sabor só (Doce de Leite).** A arte da caixa cita outros sabores,
  mas só Doce de Leite é produzido. Não desdobrar.
- **Palha tablete = 50 g** (a que circula). As cintas de 45 g eram exceção/antigas.
- **Cinta "Copa do Mundo" da cocada 45 g = sabor Tradicional** (cinta sazonal
  especial pro mais vendido, durante a Copa). Não é produto novo.
- **"Doce de Leite Cubos" = 40 g por cubo, produto DIFERENTE** da "Cocada Cubos
  160 g" (esta ≈ a PET, na linguagem da produção). Receita do Doce de Leite Cubos
  e da Cocada Assada: **Leonardo vai pegar.**
- **"Bala" = doce em formato de paralelepípedo (bloco de 400 g)**, não balinhas
  soltas. Custo segue igual (R$ 6,47/bloco, 30/tacho).
- ⚠️ **REGRA DE OURO (grave):** a linguagem do dia a dia da produção pode divergir
  do que está no SIGE — sempre confirmar o de-para antes de afirmar número.
- Pontos 6 (Pé de Moça amendoim/validade), 7 (Café kcal) e Brigadeiro: Leonardo
  vai mandar mais detalhes/fotos.

## 🔴 Impactam o cadastro / os números — resolver primeiro

1. **PET Tradicional = 160 g (foto), não 150 g.** O rótulo do Pet Tradicional diz
   "Peso Líq. 160 g". Eu havia anotado 150 g (você me passou). Qual é o oficial?
   (O cálculo de custo lê o peso do nome no SIGE, então não quebra — mas a
   divergência de cadastro precisa ser resolvida.)

2. **Palha tablete: 45 g vs 50 g circulando.** As cintas de Chocolate e Leite em Pó
   dizem **45 g**; a de Churros diz **50 g**; o display diz "10 de 50 g = 500 g".
   Nosso cadastro usa 50 g. Qual o peso oficial do tablete de palha?

3. **Pão de Mel tem 3 sabores** (Doce de Leite, Cocada, Ganache) — a caixa de
   varejo lista os três. Hoje modelamos PM como um produto único de 60 g, sem
   sabor. Falta desdobrar.

4. **Produtos vendidos mas NÃO modelados:** Cocada Assada na Cumbuca 145 g (leva
   **gema de ovo** — receita diferente da cocada de tacho) e Doce de Leite Cubos
   (lidera receita no SIGE). Atenção: pode haver **confusão de nome** entre
   "Cocada Cubos" (cocada) e "Doce de Leite Cubos" (revenda) — confirmar que não
   estão misturados no de-para.

## 🟡 Operacional / rótulo — levar à fábrica

5. **Pé de Moça contém AMENDOIM** (rótulo: "contém leite e amendoim") e validade
   **~40 dias** (vs ~2 meses dos outros sabores). Controle de alérgenos + validade.

6. **Café: 244 kcal por 45 g** no rótulo, contra 110–175 kcal dos demais sabores.
   Possível **erro de impressão** do rótulo.

7. **Cinta da Tradicional 45 g é promocional** (tema Copa do Mundo) e estampa só
   "Cocada Caseira 45 g", **sem o nome do sabor**. Edição limitada ou padrão?

8. **Nomes comerciais ≠ internos:** Tradicional = "Chocolate" (palha/cocada);
   Leite em Pó = "Ninho"/"Leitinho"; Cookies = "Cookie e Cream". Alinhar o de-para
   de venda com os nomes que aparecem no SIGE.

## 🟢 Arrumação do banco de fotos

9. **Pastas sem foto:** Palha Pet Churros, Doce de Leite Cubos, Doce de Leite Barra
   (fichas preenchidas só com nossos dados).
10. **Fotos fora do lugar nos terceirizados:** a pasta Goiabada_Cascão tem fotos de
    Doce de Leite de corte; há duas goiabadas (Doce de Goiabada 500 g e Goiabada
    Cascão sem peso no rótulo) — confirmar se são SKUs distintos.
11. **Bala:** o pacote de 400 g = **20 balinhas de ~20 g** (tabela nutricional).
    Confirma nosso custo (a "bala" comercial = pacote de 400 g; 30 pacotes/tacho).
12. **Bala de Coco (100 g)** é terceirizado e **diferente** da Bala de Doce de Leite
    (400 g) — não confundir.
