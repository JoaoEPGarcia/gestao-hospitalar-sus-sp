# Restrições e pré-especificações da segmentação por estratos estruturais

Aberto em 27/07/2026, na Etapa 3b, antes da reestimação segmentada.

Este documento registra o que **não** pode ser feito com as saídas `SEG`, e o
que foi **pré-especificado antes de ver resultado**. Ele existe porque três
das quatro decisões abaixo são do tipo que, se não ficar escrito antes,
vira racionalização depois.

Estado das etapas: 1, 2, 3 e 3b concluídas e commitadas em `master`. A
Etapa 4 (reestimação) ainda não começou e sai em branch próprio.

---

## R1 — Ocupação de internação: decisão em aberto, indicador bloqueado

**Status: PENDENTE DE RATIFICAÇÃO DA EQUIPE. Bloqueia a Etapa 4.**

`ocupacao_internacao = 100 × diarias_internacao / (leitos_sus × 365)`,
aderência exata verificada nos onze anos. Ocupação acima de 100% é
fisicamente impossível — mais diárias do que leito-dia disponível — e
ocorre em **15,5% das observações do painel definitivo**, com incidência
fortemente diferencial por categoria de gestão:

| categoria | % obs > 100% | média | mediana | máximo |
|---|---|---|---|---|
| OSS | 29,3 | 87,0 | 92,6 | 119,5 |
| Público Municipal | 26,0 | 82,4 | 86,9 | 209,2 |
| Filantrópico | 11,3 | 65,2 | 65,5 | 236,6 |
| Direta | 3,9 | 65,2 | 64,1 | 110,0 |
| Privado | 3,0 | 48,1 | 40,5 | 114,5 |

Dentro de E3 o desequilíbrio é maior: **OSS 35,5% contra Direta 2,9%**.

Não é OSS operando mais cheio. É `leitos_sus` subdeclarado frente ao leito
efetivamente operado, e a subdeclaração é sistematicamente maior em OSS e
Público Municipal. É a mesma classe de erro corrigida na Etapa 1 para a UTI
— denominador estrutural mal especificado com viés diferencial por categoria
— com o sinal invertido: na UTI o artefato **deprimia** o Filantrópico;
aqui **infla** o OSS.

### As três variantes, e por que nenhuma resolve

Estão no painel como colunas paralelas (`ocup_int_censura100`,
`ocup_int_missing100`, `ocup_int_leitos_int`). **Nenhuma foi escolhida.**
O diagnóstico de cada uma:

- **V1 censura em 100.** Preserva o n, mas não move nenhuma mediana — todas
  estão abaixo de 100 — e atua só na cauda. Atenua o viés em média e em
  regressão; não o remove.

- **V2 missing acima de 100.** Perde observação de forma diferencial, na
  proporção exata da incidência: OSS −29,3%, Público Municipal −26,0%,
  Filantrópico −11,3%, Direta −3,9%. Transporta o viés do valor para a
  amostra.

- **V3 denominador `leitos_internacao`.** Muda a definição do indicador — passa
  a medir ocupação da capacidade instalada total, não da contratada ao SUS —
  e **agrava o problema em vez de corrigi-lo**. A mediana de
  `leitos_sus / leitos_internacao` é 1,00 em Direta, OSS e Público Municipal
  nos três estratos (64% a 88% das observações têm todo leito de internação
  já SUS), de modo que V3 não muda nada nas categorias afetadas; e é 0,65 a
  0,75 no Filantrópico, que ela derruba. O gap OSS−Direta em E3 **aumenta**
  de 27,4 para 28,4 pontos. Além disso, 8,7% das observações continuam acima
  de 100% sob V3.

Gap OSS−Direta em E3 (mediana, descritivo bruto, sem controles):
V0 27,4 | V1 27,4 | V2 21,1 | V3 28,4.

### O efeito fixo não salva

A subdeclaração é **episódica, não traço estável de hospital**: 123 dos 289
CNES têm ao menos um ano acima de 100%, mas apenas 3 estão acima nos onze
anos, 57 estão acima em só um ou dois, e a mediana entre os afetados é de 3
anos. Apenas 19 dos 289 CNES têm `leitos_sus` constante na série.

Consequência: o efeito fixo de CNES **não absorve** o artefato. Ele
contamina também o estimador within, não apenas a comparação entre grupos.
Esta é a razão pela qual a decisão da equipe é carregada e não pode ser
substituída por escolha de especificação.

### Enquanto R1 estiver aberta

O modelo de ocupação de internação **não roda** na Etapa 4. Os outros cinco
indicadores não dependem desta decisão e seguem normalmente.

---

## R2 — O par de mortalidade de E3 não é citável como achado descritivo

**Status: RESTRIÇÃO PERMANENTE DE REDAÇÃO.**

A Etapa 3 produziu, dentro de E3: `mort_all` mediana **Direta 0,0698** contra
**OSS 0,0536**. Esse par **não pode ser citado como achado descritivo em
nenhum texto** — nem no `principal.tex`, nem em relatório, nem em
apresentação — porque está em parte comprado por composição de casemix
dentro do próprio estrato.

Evidência, em `tabSEG_05d_composicao_faixa_e3.csv`:

| categoria em E3 | faixa 4 | faixa 5 | faixa 6 | faixa média | Barcelona médio |
|---|---|---|---|---|---|
| Direta | 182 | 4 | **22** | 4,23 | 455,9 |
| OSS | 236 | 40 | **0** | 4,14 | 455,6 |
| Público Municipal | 286 | 55 | 0 | 4,16 | 410,8 |
| Filantrópico | 407 | 55 | 88 | 4,42 | 550,8 |

(hospital-ano; em CNES: Direta 17/1/2, OSS 24/4/0, Filantrópico 37/5/8)

Duas precisões sobre o mecanismo, porque a formulação importa quando isto
virar texto:

1. A assimetria OSS × Direta é real e é de **cauda, não de nível**: a Direta
   tem 22 hospital-ano em faixa 6 e o OSS tem zero, mas o escore Barcelona
   médio das duas categorias é praticamente idêntico (455,9 contra 455,6).
   O que difere é o extremo, e ele vem de **2 CNES**.

2. Não é verdade que os hospitais de complexidade máxima de E3 sejam todos
   Direta. O **Filantrópico tem 8 CNES em faixa 6, quatro vezes os 2 da
   Direta**, e o maior escore Barcelona médio do estrato. A restrição vale
   especificamente para o par OSS × Direta.

Isto **não invalida a estratificação**. É exatamente por isso que
`complexidade_estrutural` (escore contínuo) permanece como covariável dentro
do estrato: o estrato é grosseiro e o escore varia largamente dentro dele.
O que a restrição proíbe é citar a diferença bruta como se fosse achado.

---

## R3 — Redação factual sobre as habilitações de UTI em E1

**Status: CORREÇÃO DE REDAÇÃO, registrada antes de gerar texto.**

E1 é "sem UTI SUS" pela **mediana**, não pela série inteira: 71 dos seus 737
hospital-ano têm leito habilitado, em 18 CNES.

Redação **correta**, a ser usada em qualquer texto:

> As observações de E1 com leito de UTI SUS concentram-se a partir de 2021:
> nenhuma até 2020, uma em 2021 e dezesseis dos dezoito CNES entrando
> simultaneamente em 2022. A simultaneidade indica evento administrativo de
> habilitação, cuja causa não foi determinada.

Redação **incorreta**, a evitar: descrever essas entradas como "habilitações
transitórias da pandemia". São **posteriores** à fase aguda, provavelmente
permanentes, e podem ser mudança de registro em vez de habilitação nova. A
conclusão prática não muda — o modelo de ocupação de UTI segue não-aplicável
em E1 — mas a causa não está estabelecida e não se deve afirmá-la.

Hospitais envolvidos: predominantemente Santas Casas do interior (Guaíra,
Pederneiras, Capão Bonito, Capivari, São Pedro, Novo Horizonte, Atibaia,
Registro) e hospitais municipais, quase todos com 6 a 10 leitos.

---

## R4 — Pré-especificações registradas antes de ver resultado

**Status: PRÉ-ESPECIFICADO EM 27/07/2026, ANTES DA ETAPA 4.**

Registradas agora justamente para que não sejam post-hoc depois de a Etapa 4
rodar.

### R4.1 — Sensibilidade com E2 e E3 agrupados, só para mortalidade

Motivo, observado na Etapa 3: `mort_all` mediana é **0,0585 em E2 e 0,0587 em
E3** — empate. A mortalidade separa "sem UTI" de "com UTI", mas não distingue
baixa de alta complexidade. Agrupar E2+E3 daria **OSS 35 e Direta 26 CNES**,
com mais potência.

Vale **apenas para mortalidade**. Nos outros indicadores os estratos ordenam
monotonicamente e o agrupamento destruiria informação.

### R4.2 — Sensibilidade excluindo o Hospital Gilson de Cássia (7711980)

Único CNES instável alocado em E3, com 7 dos 11 anos com UTI e `uti_sus`
variando de 0 a 40 (mediana 20). **Mantido em E3 pela regra da mediana**, com
sensibilidade que o exclui.

---

## Nota de procedimento — base dos números

O diagnóstico original de R1 foi levantado sobre `painel_definitivo_ANTES.csv`
(317 CNES, 3.487 obs), o que explica a pequena diferença frente aos números
deste documento: ali OSS 27,6% / média 85,7 / mediana 91,6, contra 29,3% /
87,0 / 92,6 no painel definitivo. **Todas as tabelas `SEG` usam o painel
definitivo de 289 CNES**, e nele o achado é mais forte, não mais fraco.

---

## Pendências que esta tarefa não resolve

Registradas, não executadas:

- Propagação da correção da ocupação de UTI (Etapa 1) para as seções já
  escritas do `principal.tex` — depende de leitura da Priscilla, pois inverte
  um achado publicado.
- Reclassificação geográfica (Santos, Cotia, Guarulhos) — aguarda Priscilla e
  Alberto.
- Forma funcional de `complexidade_pond_mort` — aguarda Priscilla.
