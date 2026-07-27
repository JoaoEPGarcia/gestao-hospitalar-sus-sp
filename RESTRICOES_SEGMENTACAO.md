# Restrições e pré-especificações da segmentação por estratos estruturais

Aberto em 27/07/2026, na Etapa 3b, antes da reestimação segmentada.

Este documento registra o que **não** pode ser feito com as saídas `SEG`, e o
que foi **pré-especificado antes de ver resultado**. Ele existe porque três
das quatro decisões abaixo são do tipo que, se não ficar escrito antes,
vira racionalização depois.

Estado das etapas: 1, 2, 3 e 3b concluídas e commitadas em `master`. A
Etapa 4 (reestimação) foi aprovada em 27/07/2026 com recorte — quatro
indicadores, sem ocupação de internação — e sai em branch próprio.

---

## R1 — Ocupação de internação: denominador validado, natureza do excesso em aberto

**Status: FORA DA ESTIMAÇÃO NA ETAPA 4, mantido como descritiva tarjada.
Pergunta aberta com o Alberto. Ver PENDENCIAS.md §9.**

> **Revisão de 27/07/2026, no mesmo dia da abertura.** Este item foi aberto
> como "subdeclaração de `leitos_sus`" e **essa hipótese foi refutada** por
> teste contra fonte independente, algumas horas depois. O registro do
> diagnóstico refutado fica preservado abaixo, porque o caminho importa: a
> hipótese motivou uma recomendação de bloquear o indicador, e bloquear com
> base em diagnóstico refutado seria pior que o problema original.

### O que foi verificado e continua valendo

`ocupacao_internacao = 100 × diarias_internacao / (leitos_sus × 365)`,
aderência exata verificada nos onze anos. Ocupação acima de 100% é
fisicamente impossível **frente à capacidade cadastrada** e ocorre em
**15,5% das observações do painel definitivo**, com incidência fortemente
diferencial por categoria de gestão:

| categoria | % obs > 100% | média | mediana | máximo |
|---|---|---|---|---|
| OSS | 29,3 | 87,0 | 92,6 | 119,5 |
| Público Municipal | 26,0 | 82,4 | 86,9 | 209,2 |
| Filantrópico | 11,3 | 65,2 | 65,5 | 236,6 |
| Direta | 3,9 | 65,2 | 64,1 | 110,0 |
| Privado | 3,0 | 48,1 | 40,5 | 114,5 |

Dentro de E3 o desequilíbrio é maior: **OSS 35,5% contra Direta 2,9%**.

### A hipótese de subdeclaração foi REFUTADA

A leitura inicial foi que `leitos_sus` estaria subdeclarado frente ao leito
efetivamente operado, com subdeclaração maior em OSS e Público Municipal —
a mesma classe de erro corrigida na Etapa 1 para a UTI, com o sinal
invertido. **Não é isso.**

Teste contra fonte independente de contagem de leitos: a coluna `Leitos` do
arquivo de classificação Barcelona (`20260303 - Classificação
Hospitais.xlsx`, do Alberto), que não deriva do SIH. Todos os 289 CNES do
painel têm correspondência.

| categoria | `leitos_sus` / `Leitos` Barcelona | % > 100% com denominador Barcelona | % > 100% original |
|---|---|---|---|
| OSS | 1,00 | 24,4 | 29,3 |
| Público Municipal | 0,98 | 19,6 | 26,0 |
| Filantrópico | 1,00 | 9,4 | 11,3 |
| Direta | 1,00 | 1,8 | 3,9 |
| Privado | 1,00 | 0,0 | 3,0 |

Três fontes independentes de leito concordam — `leitos_sus`,
`leitos_internacao` e o cadastro Barcelona dão razão 1,00 nas categorias
onde o excesso se concentra. E trocando o denominador para a contagem
Barcelona, **o excesso do OSS sobrevive quase inteiro**: 24,4% contra 1,8%
da Direta, diferencial ainda mais nítido que o original. Dentro de E3: OSS
30,1% contra Direta 2,4%.

**O denominador está certo. Não é subdeclaração de leito.**

Limite desta validação, que precisa ficar dito: o arquivo Barcelona é um
retrato único (março de 2026), enquanto o painel tem onze anos de contagens
que variam. A concordância observação a observação é de apenas 24% a 40%.
A validação estabelece que **não há subdeclaração diferencial por categoria
de gestão** — que é a hipótese que estava em teste — mas não valida a
contagem de um ano específico.

### O que a refutação implica

Se o denominador está certo, o excesso está no **numerador**
(`diarias_internacao`) ou é **real**. E "real" aqui tem significado
substantivo: hospital operando acima da capacidade nominal cadastrada, com
leito extra, maca em corredor ou leito de observação contabilizado como
diária. É o que se espera de hospital de porta aberta em região de alta
demanda.

O teste de persistência abaixo, levantado como agravante, aponta na mesma
direção: subdeclaração cadastral seria **estável** — leito subdeclarado fica
subdeclarado. O padrão encontrado é o oposto, e é assinatura de **pico de
demanda**, não de erro de cadastro.

### As três variantes: nenhuma responde à pergunta que restou

Estão no painel como colunas paralelas (`ocup_int_censura100`,
`ocup_int_missing100`, `ocup_int_leitos_int`). **Nenhuma foi escolhida, e
com a refutação nenhuma deve ser.** As três tratam sintoma: foram desenhadas
para corrigir um erro de denominador que não existe. Se o excesso for
sobrecarga real, censurar em 100 ou marcar como missing apagaria justamente
o achado.

O diagnóstico de cada uma fica registrado porque continua informativo sobre
a estrutura dos dados:

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

### O excesso é episódico

**123 dos 289 CNES** têm ao menos um ano acima de 100%, mas apenas **3 estão
acima nos onze anos**, **57 estão acima em só um ou dois**, e a mediana entre
os afetados é de **3 anos**. Apenas 19 dos 289 CNES têm `leitos_sus`
constante na série.

Por categoria, entre os afetados: OSS 23 CNES com mediana de 4 anos acima,
Público Municipal 39 com 3, Filantrópico 55 com 2, Direta 5 com 1.

Este padrão foi lido primeiro como agravante — o efeito fixo de CNES não
absorveria um artefato que varia dentro do hospital. Com a refutação da
subdeclaração, ele vira **evidência a favor da interpretação substantiva**:
é assinatura de pico de demanda. As duas leituras têm a mesma consequência
operacional, por caminhos opostos: não se estima sobre o indicador antes de
saber o que ele mede.

### Situação na Etapa 4

O modelo de ocupação de internação **fica fora da estimação**, e o indicador
**não é bloqueado**: sai como descritiva tarjada, com nota de que o
denominador foi validado contra fonte independente e a interpretação do
excesso está pendente. Os outros indicadores não dependem disto.

A pergunta que decide não é estatística e não é da equipe de análise —
é do Alberto, e está em `PENDENCIAS.md` §9:

1. As diárias do SIH incluem permanência em leito extra ou de observação
   não cadastrado?
2. O cadastro CNES de leitos SUS exclui leito extra operado?

**Se ambas forem sim, ocupação acima de 100% é medida válida de sobrecarga
assistencial e vira achado, não bug** — e possivelmente um dos mais
interessantes do trabalho, porque separa OSS e Público Municipal de Direta e
Filantrópico numa dimensão de pressão sobre a qual o projeto ainda não disse
nada.

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

## Nota de método — a ordem em que R1 foi levantada

Registrada por decisão de João, 27/07/2026.

R1 foi aberta com uma hipótese — subdeclaração de leito — e uma recomendação
forte apoiada nela: não aprovar a Etapa 4. A hipótese não sobreviveu ao
primeiro teste contra fonte independente, feito horas depois. **A checagem
contra o arquivo do Alberto deveria ter vindo antes da recomendação, não
depois.**

O que funcionou, e vale como procedimento: o diagnóstico das variantes
recusou-se a escolher uma e devolveu a decisão à equipe. Foi essa recusa que
deixou a refutação barata — nenhuma variante tinha sido aplicada ao painel,
nenhum resultado dependia dela, e reverter custou uma reescrita de registro
em vez de uma reestimação.

Vale também para R2: a formulação original do mecanismo ("os hospitais de
complexidade máxima de E3 são todos Direta") estava errada e foi corrigida
por conferência na tabela de composição. A restrição de citação sobreviveu;
o motivo dela, não.

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
