# Restrições e pré-especificações da segmentação por estratos estruturais

Aberto em 27/07/2026, na Etapa 3b, antes da reestimação segmentada.

Este documento registra o que **não** pode ser feito com as saídas `SEG`, e o
que foi **pré-especificado antes de ver resultado**. Ele existe porque três
das quatro decisões abaixo são do tipo que, se não ficar escrito antes,
vira racionalização depois.

Estado das etapas: 1, 2, 3 e 3b concluídas e commitadas em `master`. A
Etapa 4 (reestimação) foi executada em 28/07/2026 no branch
`feat/etapa4-reestimacao-segmentada`, com **cinco indicadores** e as três
famílias previstas — CRE/Mundlak, DEA e hierárquico. Resultados e restrições
de leitura em **R9**. A Etapa 5 (refazer os modelos de ocupação da Fase 2
pelos defeitos de R8) foi executada no mesmo dia, em
`feat/etapa5-ocupacao-fase2`: o achado publicado sobrevive atenuado, e o que
muda é registrado em **R10**.

## Ratificação de escopo da Etapa 4

Ratificado por **João Eduardo Pastori Garcia** em **27/07/2026**, no exercício
da sua responsabilidade como estatístico do projeto e com a confiança expressa
da PI. Registrado aqui porque o protocolo do projeto nomeia a **PI (Priscilla)**
para decisões de escopo, e a trilha de auditoria precisa dizer de quem partiu
cada decisão. Isto é registro factual, não objeção.

As três decisões ratificadas:

1. **Ocupação de internação permanece entre os indicadores estimados**, em
   nova forma funcional — modelo em duas partes, ver R6. Não é rebaixada a
   descritiva. Isto reverte o recorte de quatro indicadores registrado na
   versão anterior deste documento, e o motivo da reversão é R1 v4: o
   mecanismo do excesso foi esclarecido.
2. `complexidade_pond_mort` fica **fora**; `complexidade_estrutural` é a única
   covariável de complexidade em todos os modelos, inclusive TMP e custo.
3. **Operacionalização dos estratos aprovada** — mediana de `uti_sus`, faixa
   Barcelona ≥ 4, classificação fixa no período — com ciência de que 48 das
   108 células ficam tarjadas por n < 10, o Privado desaparece de E3, e E3 é
   o único estrato com comparação viável.

---

## R1 — Ocupação de internação: RESOLVIDA em mecanismo

**Status: DENTRO DA ESTIMAÇÃO NA ETAPA 4, em modelo de duas partes (R6).
Quarta versão do item, 28/07/2026.**

> **Item revisado três vezes em 27/07/2026 e resolvido em 28/07/2026.** As
> três versões anteriores ficam registradas abaixo, rotuladas, porque o
> caminho importa — e porque as duas primeiras estavam erradas. Esta quarta
> versão é a única que identifica o mecanismo, e ela **inverte a decisão
> operacional** que havia sobrevivido às três anteriores: o indicador volta
> para dentro da estimação.

### O mecanismo: os dois sistemas estão certos

O excesso acima de 100% **não é erro de nenhum dos dois sistemas**. É o que se
obtém quando se divide um numerador e um denominador que respondem a
definições diferentes de "leito":

- O **CNES registra estritamente capacidade instalada e habilitada**, e
  exclui por definição qualquer leito extra efetivamente operado.
- O **SIH fatura diária e gera AIH primária** para maca e leito de observação
  quando a permanência ultrapassa 24 horas — a **regra das 24 horas** —, o que
  configura leito extra por superlotação.

Ocupação acima de 100% é, portanto, a **assinatura aritmética da
superlotação**: o numerador conta permanência em leito extra, o denominador
exclui leito extra. Os dois campos estão corretos segundo as próprias
definições, e é o quociente entre eles que carrega a informação.

O leito pactuado nos contratos SES-SP com as OSS é sistematicamente **maior**
que o registrado no CNES, e seria melhor denominador de capacidade
*operacional*. Isso **não torna o CNES errado**: contrato estipula capacidade
operacional, CNES registra capacidade habilitada. São conceitos distintos, não
medidas discordantes.

### O critério de decisão pré-especificado FALHOU — registro obrigatório

O critério registrado na terceira versão dizia, textualmente: *"Se o
contratualizado estiver sistematicamente acima, é sub-registro."*

**O contratualizado está acima, e a conclusão correta é a oposta.**

O critério montava uma **dicotomia falsa** entre "cadastro errado" e
"sobrecarga real", quando o mecanismo verdadeiro é que o cadastro está certo
*e é exatamente por isso* que o excesso mede sobrecarga. Um critério
pré-especificado sobre a dicotomia errada não protege contra nada: ele apenas
compromete de antemão com a leitura errada dos dois desfechos possíveis.

O critério falho fica preservado aqui, sem correção retroativa. Pré-especificar
disciplina a análise; não a torna correta.

### Calibragem de confiança — o que é medido e o que é asserção

As duas linhas de apoio deste item **não têm o mesmo estatuto**, e ficam
separadas de propósito:

| Afirmação | Estatuto | Situação |
|---|---|---|
| Contratos CGCSS/SES-SP acima de `leitos_sus` | **Asserção do Alberto**, não medida nestes dados | O portal não está no painel. Pendência verificável, não perseguida agora. |
| Coluna `Leitos` do arquivo Barcelona derivar do `ST_LEITO` | **Asserção**, verificável cruzando com o histórico DataSUS | Não verificada. |

A **linhagem CNES do arquivo Barcelona já está estabelecida por evidência
própria**, independentemente da asserção sobre o `ST_LEITO`: o teste do
Privado, a assinatura repetida na coluna `UTI` e a deriva de concordância de
9,3% em 2015 para 69,6% em 2025. As duas linhas de apoio ficam distintas
porque uma se sustenta sozinha e a outra não.

### Consequência para a Etapa 4

O indicador **volta para dentro da estimação**, em modelo de duas partes
(R6) — e não como contínua winsorizada, que destruiria justamente o sinal.
Os três defeitos dos modelos de ocupação já rodados na Fase 2 ficam em R8,
como escopo da Etapa 5.

---

### Versões anteriores, preservadas

**v1 (27/07/2026) — "É sub-registro de `leitos_sus`."** Hipótese apresentada
como diagnóstico, com recomendação de bloquear a Etapa 4, antes de qualquer
teste contra fonte externa.

**v2 (27/07/2026) — "O denominador está validado contra fonte independente."**
A fonte não era independente. O sinal estava na própria saída que a produziu
(Privado com `bc/total_leitos` = 0,08) e foi lido como corroboração em vez de
como assinatura de linhagem comum.

**v3 (27/07/2026) — "Não se sabe, e estes dados não distinguem."** Correta no
que negava, e é o corpo do texto que segue abaixo. Errada no critério de
decisão que propôs, e incompleta: tratava como indeterminado um mecanismo que
as definições dos dois sistemas já determinavam. Faltava perguntar o que cada
sistema define como leito, não qual dos dois estava errado.

O texto de v3 segue integralmente abaixo, porque a evidência de linhagem que
ele levanta continua válida e é ela que sustenta a calibragem acima.

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

### A hipótese de sub-registro NÃO FOI REFUTADA — ficou NÃO TESTADA

A leitura inicial foi que `leitos_sus` estaria sub-registrado frente ao leito
efetivamente operado, com sub-registro maior em OSS e Público Municipal — a
mesma classe de erro corrigida na Etapa 1 para a UTI, com o sinal invertido.

Essa hipótese foi dada por refutada com base na contagem de leitos do arquivo
de classificação Barcelona (`20260303 - Classificação Hospitais.xlsx`), que
concorda com `leitos_sus` e sob a qual o excesso sobrevive: OSS 24,4% contra
Direta 1,8%. **A refutação não se sustenta, porque a contagem Barcelona não é
fonte independente.**

Quatro testes de linhagem, todos na mesma direção:

**1. O Privado é decisivo.** Ali `leitos_sus` é 6,7% de `total_leitos`. Uma
contagem independente de leito *hospitalar* daria razão ~15 contra
`leitos_sus` e ~1 contra `total_leitos`. Os valores observados:

| categoria | Barcelona / `leitos_sus` | `leitos_sus` / `total_leitos` |
|---|---|---|
| Direta | 1,000 | 0,845 |
| OSS | 1,000 | 0,853 |
| Público Municipal | 1,023 | 0,836 |
| Filantrópico | 1,000 | 0,632 |
| **Privado** | **1,000** | **0,067** |

**2. Distância absoluta.** Nas 3.040 observações em que `leitos_sus` difere de
`total_leitos`: |Barcelona − `leitos_sus`| tem mediana de **6** leitos;
contra `leitos_internacao`, 22; contra `total_leitos`, **38**.

**3. A coluna `UTI` do mesmo arquivo repete a assinatura.** `bc_uti/uti_sus`
= 1,000 nas cinco categorias, inclusive no Privado, onde `uti_sus/uti_total`
= 0,625 e `bc_uti/uti_total` = 0,312. Duas colunas, mesma linhagem.

**4. A concordância cresce monotonicamente com o ano**, de 9,3% em 2015 a
**69,6% em 2025** — perfil de retrato do campo CNES tomado perto do fim do
período (o arquivo é de março de 2026). Isto também explica a concordância
observação a observação de 24% a 40% registrada antes: era deriva temporal,
não discordância de medida.

**A coluna `Leitos` do arquivo Barcelona é, ou deriva de, o mesmo campo de
leitos SUS do CNES que alimenta `leitos_sus`.** Não são três fontes
independentes: é uma fonte contada de três maneiras. Um CNES que sub-registra
leito SUS sub-registra nos três campos ao mesmo tempo, e a concordância entre
eles não constitui validação externa.

### Posição de v3 — SUPERADA pelo mecanismo, preservada

*Correta na negação, incompleta na pergunta. Ver o mecanismo no topo do item.*

**Não se sabe se o excesso é sobrecarga real ou sub-registro, e os dados
disponíveis não conseguem distinguir.** Todos os campos de leito do projeto
— `leitos_sus`, `leitos_internacao`, `total_leitos`, contagem Barcelona —
são de linhagem CNES.

Se o denominador estiver certo, o excesso está no **numerador**
(`diarias_internacao`) ou é **real** — hospital operando acima da capacidade
cadastrada, com leito extra, maca em corredor ou leito de observação
contabilizado como diária, o que se espera de hospital de porta aberta em
região de alta demanda. Mas isso é a hipótese alternativa, não a conclusão.

Sobra **um** argumento que não depende do CNES: o padrão episódico registrado
abaixo. Sub-registro cadastral estável produziria excesso persistente, e o
observado é mediana de 3 anos em 11. O argumento favorece a leitura de pico
de demanda **sem estabelecê-la** — um hospital pode sub-registrar leito
justamente nos anos em que expande.

### Uma fonte genuinamente independente existe — e o critério que ela alimentava falhou

Os contratos de gestão no portal **CGCSS/SES-SP** estipulam número de leitos
contratualizados, e isso não vem do CNES. Cobre apenas OSS — que é
exatamente onde o excesso se concentra.

O critério pré-especificado em v3 era:

- Se o leito contratualizado bater com `leitos_sus`, a leitura de sobrecarga
  real ganha muita força.
- Se estiver sistematicamente acima, o sub-registro ganha.

**Este critério falhou.** O contratualizado está acima — asserção do Alberto,
não medida nestes dados — e a conclusão correta é a oposta da que o critério
previa, pelo motivo registrado no topo do item: contrato e CNES medem
conceitos diferentes de capacidade, e a diferença entre eles não é erro de
nenhum dos dois. Preservado sem correção retroativa.

### As três variantes: PERMANECEM INERTES, e agora sabe-se por quê

Estão no painel como colunas paralelas (`ocup_int_censura100`,
`ocup_int_missing100`, `ocup_int_leitos_int`). **Nenhuma foi escolhida e
nenhuma será aplicada.** As três foram desenhadas contra um erro que não
existe: pressupõem que o excesso é artefato a corrigir, quando ele é o sinal.
Censurar em 100 ou marcar como missing apagaria exatamente o achado.

Foi mantê-las sem aplicar que tornou baratas duas reversões de diagnóstico —
nenhuma tinha tocado o painel, nenhum resultado dependia delas, e reverter
custou reescrita de registro em vez de reestimação. Continuam no painel pelo
mesmo motivo: como registro do que foi considerado e recusado.

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
absorveria um artefato que varia dentro do hospital. Na segunda revisão virou
a única evidência não dependente do CNES, favorecendo pico de demanda sem
estabelecê-lo.

Sob o mecanismo de v4 ele deixa de ser evidência disputada e passa a ser
**descrição do fenômeno**: superlotação é episódica por natureza. Um hospital
opera acima da capacidade habilitada nos anos em que a demanda excede a
oferta, não em todos. A mediana de 3 anos em 11 é o que se espera de pressão
assistencial intermitente — e é o que dá variação *within* suficiente para o
binário de superlotação ser estimável com efeito fixo de CNES (ver R6).

### Situação na Etapa 4

O modelo de ocupação de internação **entra na estimação**, em duas partes
(R6). Não é descritiva tarjada e não é contínua winsorizada.

As perguntas 1 e 2 abaixo, que estavam com o Alberto, estão **respondidas
pelas definições dos dois sistemas** e é isso que constitui o mecanismo de
v4. As perguntas 3 e 4 permanecem abertas, agora como **asserções não
medidas** e não como critério de decisão — ver a calibragem de confiança no
topo do item, e `PENDENCIAS.md` §9.

1. **RESPONDIDA — sim.** As diárias do SIH incluem permanência em leito extra
   ou de observação não cadastrado: o SIH fatura diária e gera AIH primária
   quando a permanência ultrapassa 24 horas.
2. **RESPONDIDA — sim.** O cadastro CNES de leitos SUS registra estritamente
   capacidade instalada e habilitada, e exclui leito extra operado.
3. **ABERTA, como asserção.** O leito contratualizado no CGCSS/SES-SP está
   acima de `leitos_sus` segundo o Alberto. Não medido nestes dados — o
   portal não está no painel. Isto **não** decide entre sobrecarga e
   sub-registro, porque contrato e CNES medem conceitos distintos.
4. **ABERTA, como asserção.** A coluna `Leitos` do arquivo Barcelona derivar
   do `ST_LEITO` é verificável contra o histórico DataSUS, e não foi
   verificada. A linhagem CNES do arquivo já está estabelecida por evidência
   própria, independentemente disto.

**Ocupação acima de 100% é medida válida de sobrecarga assistencial e é
achado, não bug** — e possivelmente um dos mais interessantes do trabalho,
porque separa OSS e Público Municipal de Direta e Filantrópico numa dimensão
de pressão sobre a qual o projeto ainda não disse nada.

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

Redação **correta**, a ser usada em qualquer texto (revisada em 28/07/2026,
quando a causa foi estabelecida):

> As observações de E1 com leito de UTI SUS concentram-se a partir de 2021:
> nenhuma até 2020, uma em 2021 e dezesseis dos dezoito CNES entrando
> simultaneamente em 2022. A simultaneidade é efeito direto de política
> pública: a conversão em bloco de leitos emergenciais de UTI COVID em leitos
> definitivos de UTI Adulto SUS, que atingiu especialmente Santas Casas e
> hospitais municipais.

Duas precisões que a redação precisa preservar:

- A conversão é **relacionada à pandemia, mas permanente**. Não é habilitação
  transitória, e por isso a entrada em 2022 é posterior à fase aguda: é a
  consolidação do leito emergencial, não a resposta a ela.
- Redação **incorreta**, a evitar: "habilitações transitórias da pandemia".
  Erra nos dois termos — não são transitórias e não são da fase aguda.

A conclusão prática não muda: o modelo de ocupação de UTI segue não-aplicável
em E1, porque a classificação é por mediana dos onze anos e três anos de UTI
no fim da série não movem a mediana.

*Versão anterior deste item, preservada:* a redação dizia "evento
administrativo de habilitação, cuja causa não foi determinada", e advertia
que podia ser mudança de registro em vez de habilitação nova. A cautela era
correta enquanto a causa não estava estabelecida; agora está.

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

## R5 — Pressão assistencial como mediador: hipótese guardada, com trava

**Status: HIPÓTESE REGISTRADA. NÃO IMPLEMENTAR sem desenho próprio.
A TRAVA FICA MAIS IMPORTANTE, NÃO MENOS, DEPOIS DE R1 v4.**

A condição desta hipótese era: *"se a resposta a R1 for que o excesso de
ocupação mede sobrecarga real"*. **Ela foi satisfeita em 28/07/2026.** O
excesso mede sobrecarga assistencial, e pressão assistencial deixa de ser
problema de indicador e passa a ser mecanismo candidato entre modelo de
gestão e desfecho — por que uma OSS teria mortalidade ou TMP diferente.

É justamente por isso que a trava abaixo precisa ser lida agora com mais
atenção do que quando foi escrita. Enquanto o indicador estava sob suspeita,
ninguém seria tentado a colocá-lo como covariável; agora que ele é achado
legítimo, a tentação existe — e é exatamente aí que ela é errada.

**A trava, que vai colada à hipótese:** pressão assistencial, se for real, é
**variável pós-tratamento** — causada pelo modelo de gestão e causadora do
desfecho. Incluí-la como covariável nos modelos de mortalidade ou de TMP
**bloquearia justamente o canal causal que se quer medir**. É o mesmo erro de
*bad control* que descartou `pct_alta_complex` como candidato a estrato no
início do desenho.

Só entra como mediador em **análise de mediação formal, com desenho próprio**
— e mesmo assim frágil, porque a identificação repousa sobre cinco switchers,
dos quais apenas dois têm pós-tratamento de mais de um ano.

Ninguém deve implementar isto a partir da hipótese sozinha.

---

## R6 — Ocupação de internação em duas partes: IMPLEMENTADA na Etapa 4

**Status: IMPLEMENTADA. Pré-especificada em 28/07/2026, antes de ver
coeficiente.**

*Nota de registro:* este item **não existia neste documento** antes de
28/07/2026 — o documento ia de R1 a R5. Ele entra já no estado "implementada".
A instrução de trabalho o descrevia como promoção de uma proposta anteriormente
marcada "não implementar"; esse estado anterior não consta deste arquivo nem
de nenhum outro do repositório, e por isso não é afirmado aqui. O que se
registra é o que se pode verificar: a forma em duas partes entra agora, e o
motivo é R1 v4.

### A forma funcional

A ocupação de internação entra em **duas partes**, nunca como contínua
winsorizada:

- **Parte A — binário de superlotação.** `sobrecarga = 1` se
  `ocupacao_internacao > 100`. Modelo logístico com estrutura CRE/Mundlak,
  erros-padrão clusterizados por CNES.
- **Parte B — contínua condicional.** `ocupacao_internacao` restrita a
  `≤ 100`. Mesmo conjunto de covariáveis. **Não há winsorização na parte B**:
  o teto é 100 por construção.

As duas são reportadas e interpretadas **conjuntamente**. Não se somam e não
se colapsam em índice único — são duas perguntas distintas: *com que
frequência o hospital entra em superlotação* e *quão cheio ele opera quando
não está superlotado*.

### Por que não a contínua winsorizada

Porque ela **destrói justamente o sinal**. Winsorizar o excesso acima de 100%
trata como ruído de cauda aquilo que R1 v4 identificou como a assinatura
aritmética da superlotação. O indicador contínuo bruto, por sua vez,
**conflaciona** as duas perguntas numa média só.

O tamanho da conflação, **medido no painel definitivo em 28/07/2026** (medianas
em E3, descritivo bruto sem controles): gap bruto OSS−Direta de **+27,4
pontos**, gap da parte contínua de **+21,1 pontos**. Ou seja, **cerca de 23%
da diferença que aparecia como "OSS mais cheio" era OSS mais frequentemente em
superlotação**, misturado na mesma média.

*Divergência frente à referência, registrada:* a instrução de trabalho previa
~16,6 pontos na parte contínua e cerca de 40% de conflação, a partir da base
de 314 CNES. O gap bruto reproduz exatamente (27,4), mas a parte contínua não:
o observado é 21,1, e a conflação é **23%, não 40%**. O valor de 21,1 é
coerente com o registro já existente da variante V2 no diagnóstico de R1
(V0 27,4 | V1 27,4 | V2 21,1 | V3 28,4) — restringir a ≤ 100 é, em mediana, a
mesma operação de V2. Prevalece o observado.

A conclusão qualitativa não se move: a maior parte do gap é nível, uma parte
material é frequência, e a média bruta não distingue as duas. Verificação em
`verificar_prespecificacoes_etapa4.py`.

### Assimetria com a UTI — registrada antes de rodar

Ocupação de **UTI continua contínua**, winsorizada em p99 da subamostra
válida, com **limiar único para o painel inteiro**. A justificativa da
assimetria é empírica e verificável: em internação o excesso acima de 100% é
fortemente **diferencial** entre as categorias do contraste principal; em UTI
ele é **não-diferencial**, praticamente idêntico entre OSS e Direta. Se o
diferencial aparecer em UTI no painel definitivo, a justificativa cai e a
assimetria precisa ser reaberta.

---

## R7 — Piscar cadastral de UTI

**Status: NOVA, verificada no painel definitivo em 28/07/2026.
Ver `verificar_piscar_cadastral.py` e `tabSEG_09_piscar_cadastral.csv`.**

A oscilação de `uti_sus` entre anos é **suspensão e limpeza cadastral** — por
exemplo inativação temporária por falta de intensivista — e **não** construção
ou demolição de ala. A capacidade subjacente é estável; o cadastro é que
pisca.

### Isto REFORÇA a estratificação fixa

O estrato é atribuído por CNES, pela mediana de `uti_sus` nos onze anos, e
fica fixo no período. Se as oscilações fossem obra física, a classificação
fixa apagaria mudança real de tecnologia de produção. Sendo piscar cadastral,
a mediana é o estimador **certo** da capacidade subjacente: ignora os anos em
que o registro caiu sem que a ala fechasse.

### Consequência verificável, e verificada

Se o cadastro pisca enquanto a ala opera, devem existir observações com
`uti_sus = 0` **e produção de UTI ativa**. Existem, e o controle da internação
sai limpo:

| medida | referência (314 CNES) | painel definitivo (289 CNES) |
|---|---|---|
| observações com `uti_sus = 0` e `diarias_uti > 0` | 39 | **38** |
| CNES envolvidos | 27 | **26** |
| mediana de diárias no Filantrópico | 775 | **763** |
| anos de concentração | 2017, 2020, 2021, 2025 | **2017, 2020, 2021, 2025** |
| casos análogos em internação | 0 | **0** |

Distribuição no painel definitivo: 2021 com 23 casos, 2020 com 13, 2017 e
2025 com 1 cada — a concentração em 2020–2021 é coerente com sobrecarga e
remanejamento cadastral no período pandêmico. Por categoria: Filantrópico 28
observações em 19 CNES, Público Municipal 6 em 4, Privado 2 em 1, Direta e
OSS 1 cada. Por estrato: 36 em E1 e 2 em E2.

**29 CNES** têm `uti_sus` ora zero ora positivo; destes, **19** têm produção
ativa em ano zerado. O controle da internação — `leitos_sus = 0` com
`diarias_internacao > 0` — dá **zero casos**, como esperado: leito de
internação não é habilitação que se suspenda do mesmo modo.

### O que isto NÃO muda

**A Etapa 1 continua válida.** A razão segue indefinida com denominador zero,
e essas 38 observações saem do modelo de qualquer forma — é para isso que
existe `ocupacao_uti_valida`, definida apenas onde `uti_sus > 0`.

O que muda é o **motivo registrado**. Das 688 observações com `uti_sus = 0`,
**650 são ausência real** de UTI (76 CNES) e **38 são piscar cadastral com
operação ativa** (26 CNES). As duas ficam distinguidas no registro e no
cabeçalho de `descritivas_segmentadas.py`, em vez de somadas sob o rótulo
único de "sem UTI".

---

## R8 — Três defeitos nos modelos de ocupação da Fase 2 já rodada

**Status: EXECUTADA NA ETAPA 5, em 28/07/2026. Os três defeitos foram
corrigidos e reestimados. A consequência prevista abaixo — "o achado não
sobrevive como está" — NÃO se confirmou: ele sobrevive, atenuado. Ver R10.**

Os modelos de ocupação em `fase2_bayes.R` e `fase2_robustez.R` têm três
defeitos **independentes** entre si:

1. **Winsorização contaminada.** `preparo_fase2.R` winsoriza ambas as
   ocupações no p99 do **painel completo**, incluindo os zeros estruturais.
   Para `ocupacao_uti` isso dá limiar de ~164 contra ~179 sobre a subamostra
   válida — ou seja, **o limiar é ele próprio artefato do bug corrigido na
   Etapa 1**.

2. **Condicionamento no desfecho.** `fase2_bayes.R` restringe o modelo de UTI
   a `ocupacao_uti > 0`, o que condiciona **no desfecho** e não na capacidade.
   Exclui hospitais com UTI habilitada e zero diárias no ano — seleção pela
   variável dependente. É problema **distinto** do corrigido na Etapa 1, e
   ainda não corrigido.

3. **Sinal apagado por winsorização.** O modelo de internação winsoriza o
   excesso acima de 100% como ruído, quando ele é a assinatura da
   superlotação (R1 v4, R6). Apaga o achado.

**Consequência prevista em 28/07/2026, ANTES de reestimar:** "o achado de
ocupação que está no `principal.tex` não sobrevive como está". A Etapa 5
refará esses modelos já na forma correta.

> **A previsão acima é preservada, e o veredito é por defeito, não em bloco.**
> A Etapa 5 rodou no mesmo dia. O achado sobrevive, atenuado: intensidade de
> UTI de +30,4% para +26,7%, ainda excluindo o zero; ocupação de internação
> de +12,5% para +11,5%, ainda cruzando o zero.
>
> - **Defeito 1 — previsão errada.** Corrigir o limiar move +0,0005.
> - **Defeito 2 — errada quanto ao coeficiente, certa quanto ao princípio.**
>   As 7 observações movem −0,0026 diretamente, mas a correção força a troca
>   de família (a Gama não admite zero), e a troca move −0,0268. Age por um
>   canal que a previsão não antecipou.
> - **Defeito 3 — previsão CERTA.** Winsorizar destruía mesmo o sinal de
>   sobrecarga, e a resposta nunca foi um coeficiente que muda: é o modelo em
>   duas partes, que mostrou que o número publicado misturava frequência de
>   superlotação com intensidade de ocupação. Isto é o defeito se
>   confirmando.
>
> Ver R10 para a decomposição completa.

---

## R9 — Resultados da Etapa 4: o que pode e o que não pode ser dito

**Status: REGISTRADO EM 28/07/2026, depois de rodar as três famílias.**

Registrado aqui porque a tabela sozinha convida a leituras que os dados não
sustentam. Saídas em `tabSEG_10` a `tabSEG_15`, `figSEG_04` e `figSEG_05`.

### O que está estimado

Três famílias, cinco indicadores, três estratos. CRE/Mundlak
(`estimacao_segmentada.py`), DEA com fronteira por estrato
(`etapa4_dea_segmentado.R`) e hierárquico glmmTMB
(`etapa4_bayes_segmentado.R`).

Em **E3**, o único estrato com identificação within (coeficiente de OSS contra
Direta, CRE/Mundlak, EP agrupado por CNES):

| indicador | efeito | IC95% | p |
|---|---|---|---|
| Mortalidade geral | −0,281 (logito) | [−0,442, −0,121] | 0,001 |
| TMP | **−11,8%** | [−17,6%, −5,6%] | 0,000 |
| Faturamento real/saída | −9,2% | [−25,2%, +10,4%] | 0,332 |
| Ocupação de UTI (PPML) | +25,5% | [−18,4%, +93,0%] | 0,300 |
| Superlotação (parte A) | +0,74 (logito) | [−1,17, +2,64] | 0,448 |
| Ocupação ≤100 (parte B) | +27,0% | [−1,8%, +64,3%] | 0,068 |

O **hierárquico concorda onde ambos estimam**, e a concordância é estreita:
TMP −0,1254 no CRE/Mundlak contra −0,1255 no hierárquico; mortalidade −0,281
contra −0,258; ocupação de UTI +0,227 contra +0,231. Isso é consistência
entre estimadores, **não** evidência independente: os dois usam os mesmos
dados e a mesma identificação.

O **DEA** em E3 põe o OSS acima da Direta em eficiência técnica corrigida de
viés (0,747 contra 0,687), e a segunda etapa truncada dá coeficiente de OSS
de −0,601, IC95% [−1,065, −0,169] — negativo é mais eficiente. Escores de
estratos diferentes **não são comparáveis entre si**: cada fronteira é a do
próprio estrato.

### O que NÃO pode ser dito

**1. Nada causal fora de E3.** E1 não tem nenhum conversor: ali o termo de
Mundlak é colinear com a própria dummy de categoria e foi removido, o que a
saída anuncia. E2 tem um só. Os coeficientes de E1 e E2 são comparação entre
grupos e saem tarjados; em `figSEG_04` estão em cinza por isso. O
−72,9% de TMP em E1 é o contraste de **2 CNES OSS contra 1 CNES Direta** e
não é achado.

**2. O within de E3 é mais fino do que o IC sugere.** A identificação vem de
quatro hospitais, e **dois deles contribuem um único ano**: Taipas e Vila
Penteado convertem em 2025. Pérola tem 3 anos, Sorocaba tem 7. Na prática
Sorocaba domina, e é o caso com endogeneidade de conversão documentada. O
IC de Wald não sabe disso. Nenhum efeito de E3 deve ser citado sem a
qualificação de que repousa sobre Sorocaba e Pérola.

**3. A mortalidade de E3 pede cuidado extra, por R2.** O coeficiente
modelado **não** é o par descritivo proibido — controla
`complexidade_estrutural` contínua, que é justamente a razão pela qual R2 diz
que a estratificação não fica invalidada. Mas o mecanismo de R2 continua
presente nos dados: a assimetria de cauda de 2 CNES em faixa 6. O
coeficiente é citável **com** o controle explicitado; o par bruto, não.

**4. O Privado não é interpretado em nenhum estrato**, inclusive no DEA, onde
aparece com 1 a 2 CNES por estrato e escore de 0,257 em E2.

**5. O IC do OSS no DEA de E1 repousa sobre 490 das 1.000 réplicas.** Com 2
CNES OSS, mais da metade das reamostragens por hospital não sorteia nenhum.
A tabela traz réplicas válidas por termo para que isso não passe.

### Onde a estimação falhou, e por quê

Falha reportada é resultado, não lacuna a preencher depois:

- **Superlotação (parte A) em E1 e E2: separação.** O logito não é
  identificado — em E1 o coeficiente diverge mesmo sem dummies de ano. O
  número **não é reportado**. O hierárquico recusa as mesmas duas células,
  por matriz singular. Duas rotas independentes, mesmo diagnóstico.
- **Ocupação de UTI em E1: NÃO-APLICÁVEL.** E1 é "sem UTI SUS" pela mediana;
  as 71 observações com UTI ativa são piscar cadastral (R7). Estimar ali
  seria rodar sobre o artefato.

### Divergência entre famílias que fica registrada

Ocupação de UTI em **E2**: o CRE/Mundlak em PPML dá +61,9% com IC que exclui
zero; o hierárquico em Tweedie dá +39,2% com IC que o inclui. Mesmo sinal,
conclusões diferentes sobre significância. A diferença é de família e de
efeito aleatório, não de dados. **Em E2 não há identificação causal de todo
modo**, então isto não muda conclusão nenhuma — mas não deve ser apresentado
como se as duas famílias concordassem.

### Três decisões de forma funcional tomadas na execução

Registradas porque divergem de convenções anteriores do projeto:

1. **Mortalidade em logito fracionário**, não no Beta com inflação em zero de
   `estimacao.py`. Dentro de estrato o componente de inflação é inestimável
   por separação: E3 não tem nenhum zero, E1 tem três.
2. **Ocupação de UTI em PPML** (e Tweedie no hierárquico), não em log-MQO. A
   subamostra válida tem 7 zeros — UTI habilitada com zero diárias no ano.
   Descartá-los para tomar o log seria condicionar no desfecho, que é o
   defeito 2 de R8. Não se corrige um defeito num script e se reproduz o
   mesmo defeito no outro.
3. **Guarda de separação no binário**: coeficiente acima de 15 em módulo
   dispara reajuste sem dummies de ano e, persistindo, o número não é
   reportado.

---

## R10 — Etapa 5: o achado de ocupação SOBREVIVE, atenuado

**Status: EXECUTADA EM 28/07/2026. R8 FECHADA quanto à correção; a
consequência que ela previu não se confirmou na forma prevista.**

Saídas em `tabE5_ocupacao_antes_depois.csv` e `tabE5_ocupacao_variantes.csv`.
Scripts: `preparo_fase2_corrigido.R` e `fase2_ocupacao_corrigido.R`. Os
originais não foram tocados.

### A trava de reprodução veio antes da conclusão

Antes de corrigir qualquer coisa, o script reestima as especificações
**originais, com os defeitos**, e aborta se não casar com o publicado. Casou
na quinta casa em todas as oito células — as duas do modelo principal
(`+0,11802` e `+0,26514`) e as seis de variante de
`tabR_frente1_variantes.csv`. Sem isso, qualquer diferença observada depois
poderia ser do pipeline e não da correção.

### O veredito

| quantidade | publicado | corrigido | conclusão |
|---|---|---|---|
| Intensidade de UTI | +30,4% \[+5,6%, +60,8%\] | **+30,4%** \[+5,6%, +60,8%\] (hurdle) | **sobrevive intacto** |
| Ocupação de internação | +12,5%, cruza o zero | **+11,5%**, cruza o zero | **sobrevive**, inalterado |
| Sem conversores, internação | 0,118 → 0,235, passa a excluir o zero | 0,108 → **0,218**, passa a excluir o zero | **sobrevive** |

Nenhuma conclusão publicada inverte ou cai. A frase da Seção 15 — a ocupação
aponta na mesma direção com magnitude menor, com intervalo que cruza o zero
na especificação hierárquica — continua correta com os números corrigidos.

**A frase que vai ao texto sobre a intensidade de UTI:** corrigir o
condicionamento no desfecho, com especificação que preserva a função de
variância, **deixa o achado publicado intacto** (+30,4%). Sob famílias
alternativas o efeito varia entre +25,9% e +30,4%, mantendo direção nas cinco
e significância em quatro — a família é a sensibilidade principal, e a
amplitude de 4,5 pontos é menor que a largura do próprio intervalo de
confiança.

### Efeito ISOLADO de cada defeito — e a atribuição correta da atenuação

Ver `tabE5_decomposicao_defeitos.csv` e `fase2_ocupacao_decomposicao.R`. A
UTI foi decomposta em fatorial 2×2 (limiar × amostra) com a **família mantida
fixa** em Tweedie, porque a Gama do original não admite zero: trocar a
amostra para capacidade obrigaria a trocar de família junto, e o efeito do
defeito 2 ficaria confundido com o da família.

| fonte | obs tocadas | Δ coeficiente (log) |
|---|---|---|
| R8-1 limiar da UTI (171,3 → 180,5) | 32 mudam de valor, 7 deixam de ser aparadas | **+0,0005** |
| R8-2 amostra da UTI (desfecho → capacidade) | 7 entram | **−0,0026** |
| R8-3a tirar a winsorização da internação | 32 aparadas | **−0,0002** |
| R8-3b mudar para a forma em duas partes | reorganiza as 492 acima de 100 | **−0,0093** |
| **Gama → Tweedie (família)** | — | **−0,0268** |

Dentro de família fixa, os defeitos movem a terceira e a quarta casa decimal.
A atenuação passa pela troca de família. Isso levantou a pergunta seguinte, e
a resposta dela **derrubou a leitura intermediária deste item**.

### A família NÃO é forçada — e o achado publicado sobrevive intacto

Ver `tabE5_sensibilidade_familias.csv` e `fase2_ocupacao_familias.R`.

Chegou-se a registrar aqui que a troca de família era **consequência forçada**
de corrigir R8-2 — "manter os zeros exige família que os admita, e a Gama não
admite". A primeira metade é verdadeira; a conclusão não segue. **Existe
família que admite zero e preserva a função de variância da Gama: o hurdle.**

| especificação | n | efeito | IC95% |
|---|---|---|---|
| Gama, sem os zeros (**publicada**) | 2.482 | **+30,4%** | \[+5,6%, +60,8%\] |
| **ziGamma / hurdle, com os zeros** | 2.489 | **+30,4%** | \[+5,6%, +60,8%\] |
| Tweedie, sem os zeros | 2.482 | +27,0% | \[+7,6%, +49,8%\] |
| Tweedie, com os zeros | 2.489 | +26,7% | \[+6,7%, +50,4%\] |
| lognormal, sem os zeros | 2.482 | +25,9% | \[−0,3%, +59,0%\] |

**O hurdle corrige R8-2 integralmente — os 7 zeros ficam na amostra, não há
condicionamento no desfecho — e devolve +30,4%, idêntico ao publicado até a
quarta casa decimal.** Logo: corrigir o defeito 2 **não** atenua o achado. O
+26,7% foi consequência de escolher Tweedie, que é decisão de modelagem
independente, não imposição do defeito.

### O teste decisivo: os zeros ou a função de variância?

A massa em zero é de **7 observações em 2.489 — 0,281% da amostra**. São
hospitais com UTI habilitada e nenhuma diária no ano (o CNES 7580770, da
Direta, em dois anos seguidos; dois OSS; três Filantrópicos).

Rodando Tweedie sobre **exatamente a mesma amostra da Gama publicada**, a
única diferença entre as duas passa a ser a função de variância:

| decomposição da atenuação | Δ (log) | participação |
|---|---|---|
| efeito dos **zeros** (Tweedie com − Tweedie sem) | −0,00265 | **9%** |
| efeito da **função de variância** (Tweedie sem − Gama sem) | −0,02649 | **91%** |

Confirma a suspeita que motivou o teste: **sete observações não movem o
número; a função de variância move.** `V(μ) = μ²` na Gama contra `V(μ) = μᵖ`
na Tweedie repondera as 2.489 inteiras. Deixar 0,281% da amostra escolher a
família para os outros 99,7% seria inverter a ordem de importância.

### A família é a sensibilidade principal, e o achado é robusto a ela

Amplitude entre as cinco especificações: **+25,9% a +30,4%, 4,5 pontos
percentuais**. Quatro das cinco excluem o zero no IC95%. A exceção é a
lognormal, cujo limite inferior é −0,0035 em pontos de log — cruza o zero por
uma margem que não é distinguível de tocá-lo.

**Direção idêntica nas cinco, significância em quatro, magnitude entre 26% e
30%: isto é resultado robusto e reportável.** A família é a decisão de
modelagem que mais move o número, e por isso a amplitude deve acompanhar o
achado sempre que ele for citado — não como ressalva defensiva, mas porque
4,5 pontos é a incerteza real de especificação, e ela é menor que a largura
do próprio IC.

### Sobre o modelo em duas partes aqui

Avaliado, não implementado como principal. **Não dispensa a escolha de
família: relocaliza-a, e nesse caso específico é o bastante.**

A forma em duas partes tira do conjunto de famílias a exigência "precisa
admitir zero", porque a massa em zero vai para um componente binário próprio.
Isso libera a Gama para a parte contínua — que é exatamente o que o hurdle
faz, e por isso ele recupera o +30,4%. Mas a escolha **entre** famílias para
a parte positiva permanece inteira, e é ali que vivem os 4,5 pontos de
amplitude. Resolve o problema dos zeros; não resolve o da função de
variância.

Há ainda um limite prático: a **primeira parte não é estimável** com
covariáveis. Sete zeros não sustentam um binômio, e ele não converge — o
mesmo motivo pelo qual `uti_parte1` é degenerada. A versão com intercepto
apenas converge, e é precisamente o ziGamma da tabela acima. Ou seja, o
modelo em duas partes viável aqui **já está reportado**; o que não existe é
uma primeira parte com conteúdo substantivo.

### O que R8 previu certo e o que previu errado — por defeito

R8 dizia, em bloco, que "o achado não sobrevive como está". Avaliada por
defeito, a previsão se divide:

- **R8-1 (winsorização contaminada): previsão ERRADA.** O defeito é real — o
  limiar antigo era mesmo artefato do bug da Etapa 1 — mas corrigi-lo move
  +0,0005. Nada depende disso.
- **R8-2 (condicionamento no desfecho): previsão ERRADA quanto ao
  coeficiente, CERTA quanto ao princípio.** As 7 observações movem −0,0026, e
  corrigido pelo hurdle — que preserva a função de variância — o coeficiente
  volta a +30,4%, o publicado. O defeito é real e a correção é obrigatória
  por princípio: condicionar no desfecho está errado mesmo quando não muda
  nada. Mas ele **não atenua o achado**. Chegou-se a registrar que forçava a
  troca de família; não força — ver a seção da família acima.
- **R8-3 (sinal apagado por winsorização): previsão CERTA.** E é a única que
  se confirma na forma em que foi feita. A resposta a este defeito nunca foi
  um coeficiente que muda — tirar o corte mantendo o modelo único move
  −0,0002, praticamente nada. A resposta é o **modelo em duas partes**, que
  mostrou que o número publicado misturava *frequência de superlotação* com
  *intensidade de ocupação*. O modelo antigo não tinha como responder à
  primeira pergunta; o novo tem, e é a parte A. Isso é o defeito 3 se
  confirmando, não se refutando.

**A lição, que é a de R1 v2 com o sinal trocado:** diagnosticar corretamente
um defeito não permite prever a magnitude do seu efeito, **nem o canal por
onde ele age**. R8-2 agiu por um canal que ninguém antecipou (a família), e
R8-3 agiu não sobre o valor do coeficiente mas sobre a pergunta que o modelo
consegue responder. Declarar o achado morto a partir do diagnóstico teria
sido tão errado quanto declará-lo salvo sem reestimar.

### O que MUDA de verdade, e não é o que R8 previa

**1. A parte que a winsorização escondia não é magnitude, é uma pergunta
separada.** O modelo publicado tem UM coeficiente de ocupação de internação,
que mistura *com que frequência o hospital entra em superlotação* com *quão
cheio opera quando não está*. Separadas (R6), as duas partes dizem coisas
diferentes:

- **Parte B** (contínua ≤ 100): +11,5%, cruza o zero. É o que o número
  publicado essencialmente já media.
- **Parte A** (binário de superlotação): +3,27 no logito **sem conversores**,
  IC \[+1,39, +5,16\] — e −0,25 com IC \[−2,36, +1,86\] no principal.

Essa inversão não é instabilidade: é a diferença entre **between e within**.
No principal, o termo de Mundlak absorve o contraste entre redes e a
identificação de `d_oss` passa a vir só dos hospitais que **trocam de
categoria**. Sem conversores, o Mundlak sai e o coeficiente passa a ser o
contraste bruto entre redes, que é enorme porque o excesso é de 29,3% no OSS
contra 3,9% na Direta.

**Quantos hospitais sustentam cada estimativa within** — informação que
precisa acompanhar todo coeficiente within deste projeto:

| estimativa | switchers que a sustentam |
|---|---|
| contínuas (intensidade, TMP, custo, mortalidade) | **5 de 5** — todos variam |
| **binário de superlotação, painel inteiro** | **4 de 5** — Taipas nunca entra em superlotação |
| binário de superlotação, dentro de E3 (Etapa 4) | **3 de 4** — Odilo Antunes está em E2 |

E o quanto cada um contribui é desigual: Sorocaba tem 7 anos como OSS e 3 em
superlotação; Pérola 3 e 1; Vila Penteado 1 e 1; Odilo Antunes 1 e 4; Taipas
1 e nenhum.

**Redação obrigatória para o binário — o nulo não é evidência de ausência.**
A formulação anterior deste item dizia que o gap "não é efeito causal de
gestão", o que atribui ao nulo mais força do que ele tem. A redação correta,
que é a mesma já usada para o coeficiente de mortalidade:

> O gap de superlotação entre as redes é grande e bem medido. A estimativa
> within é nula, mas repousa sobre 4 hospitais e **não distingue "sem efeito"
> de "sem potência"**. O erro-padrão de 1,08 no logito é a medida honesta de
> quão pouco os conversores informam sobre esta quantidade: o intervalo
> \[−2,36, +1,86\] cobre desde uma redução enorme até um aumento enorme.

Não se deve escrever que a gestão não afeta a superlotação, nem que afeta.
Estes dados não decidem. O que se pode dizer é que o **contraste descritivo
entre redes é grande**, e que a evidência causal disponível é insuficiente
para atribuí-lo à gestão em qualquer direção.

Isto é coerente com a Etapa 4, onde o mesmo binário em E3 deu +0,74 com EP
0,97 — outro intervalo que cobre tudo.

**2. `uti_parte1` publicado é um número degenerado — REMOVIDO da tabela.** Em
`tabB_modelos_hierarquicos.csv` estava `-58,958032` com erro-padrão **NaN**:
separação, não estimativa. É da **mesma classe do termo `d_oss` da SFA**, já
documentado no projeto como não citável, e recebe o mesmo tratamento — sai da
tabela publicada, permanece na documentação com o motivo. Não é decisão de
estilo. A versão corrigida da mesma quantidade (opera, dado que tem
capacidade) **também não converge**: na subamostra de capacidade sobram só 7
zeros. A pergunta não é estimável com estes dados, nem antes nem depois da
correção.

**3. A frase do Apêndice A era enganosa e ficou pior — CORRIGIDA.** Ela dizia
que a ocupação de internação é "modelada no logaritmo **sem truncar em
100%**". Literalmente verdadeira e materialmente enganosa: não trunca em 100,
mas **winsoriza em 125,1**. Depois desta etapa a gravidade aumenta, porque
125,1 é precisamente onde começa a cauda de superlotação que agora se sabe
carregar sinal próprio — a frase sugeria preservação do excesso justamente
onde ele era aparado. A redação nova declara o limiar efetivo e o que ele
remove.

### Pendências que a Etapa 5 abre

- Se a parte A da internação entrar no texto, ela entra com a redação
  obrigatória acima: **contraste descritivo entre redes**, com a nulidade
  within declarada como falta de potência e não como ausência de efeito.
- Reexecutar `fase2_bayes.R` regeneraria `tabB_modelos_hierarquicos.csv` com
  a linha `uti_parte1` de volta. A remoção está registrada em
  `tabB_uti_parte1_removida.md`, ao lado da tabela, para que quem reexecutar
  saiba o que refazer.

Nada disto exige reestimar mais nada. A propagação ao `principal.tex`
continua dependendo de leitura da Priscilla, como já registrado.

---

## Nota de método — a ordem em que R1 foi levantada

Registrada por decisão de João, 27/07/2026. Ampliada em 28/07/2026, quando a
quarta versão fechou o item.

R1 foi reescrita duas vezes no dia em que foi aberta, e uma quarta vez no dia
seguinte. As três primeiras versões afirmaram estrutura com confiança, a
partir de checagem correlacional em dados de **linhagem única**, e as duas
primeiras estavam erradas:

1. **"É sub-registro de leito"** — hipótese apresentada como diagnóstico,
   com recomendação de bloquear a Etapa 4, antes de qualquer teste contra
   fonte externa.
2. **"O denominador está validado contra fonte independente"** — a fonte não
   era independente. O sinal estava na própria saída que a produziu (Privado
   com `bc/total_leitos` = 0,08), e foi lido como corroboração em vez de
   como assinatura de linhagem comum.
3. **"Não se sabe, e estes dados não distinguem"** — correta no que negava,
   e a evidência de linhagem que ela levantou continua de pé.
4. **"Os dois sistemas estão certos, e o excesso é a assinatura da
   superlotação"** — a versão que fecha o item, 28/07/2026.

**A quarta versão inverteu a decisão operacional.** As três primeiras
mantinham o indicador fora da estimação, por justificativas diferentes; a
quarta o traz de volta, em forma nova. Isto desfaz a leitura tranquilizadora
que a nota original registrava — a de que a decisão operacional tinha
sobrevivido a todas as reversões de diagnóstico. Ela sobreviveu a três e caiu
na quarta. Uma decisão que resiste a várias mudanças de justificativa não
está por isso validada: pode estar apenas sendo reencontrada por caminhos
igualmente errados.

**A lição específica da quarta versão:** as três primeiras discutiam *qual dos
dois sistemas estava errado*, e a pergunta certa era *o que cada sistema
define como leito*. A dicotomia estava embutida no critério pré-especificado
de v3, que por isso comprometia com a leitura errada em qualquer um dos dois
desfechos possíveis — ver o registro do critério falho em R1. Pré-especificar
não protege contra a pergunta errada; só contra a resposta oportunista.

Três lições, em ordem de importância:

- **Concordância entre campos da mesma fonte não é validação.** Foi o erro
  central da segunda versão, e a checagem que o teria evitado é barata: pedir
  a uma fonte candidata que discorde de outra coluna onde as duas deveriam
  divergir. O Privado era esse teste e estava disponível desde o início.
- **A checagem contra fonte externa precede a recomendação**, não a segue.
- **Errar junto não dilui.** A conta do arquivo Barcelona foi reproduzida
  fielmente e o detalhe do Filantrópico foi reportado com precisão; a
  inferência errada a partir dele foi de ambos os lados. Reprodução fiel de
  um cálculo não é verificação da inferência que se tira dele.

O que funcionou, e vale como procedimento: o diagnóstico das variantes
recusou-se a escolher uma e devolveu a decisão à equipe. Foi essa recusa que
deixou as duas reversões baratas — nenhuma variante tinha sido aplicada ao
painel, nenhum resultado dependia delas, e reverter custou reescrita de
registro em vez de reestimação. Esse procedimento se pagou uma terceira vez
na quarta versão, que **inverteu** a decisão operacional: se alguma variante
tivesse sido aplicada, a inversão exigiria reconstruir o painel, e o sinal de
superlotação já teria sido apagado do arquivo.

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

- ~~**Etapa 5 — refazer os modelos de ocupação da Fase 2**~~ — **feita em
  28/07/2026**. Ver R10. Deixou três pendências menores: ajustar a frase do
  Apêndice A sobre truncamento, decidir o destino editorial do `uti_parte1`
  degenerado em `tabB_modelos_hierarquicos.csv`, e a regra de que a parte A
  da internação só entra no texto como descritivo entre redes.
- Propagação da correção da ocupação de UTI (Etapa 1) para as seções já
  escritas do `principal.tex` — depende de leitura da Priscilla, pois inverte
  um achado publicado e faz o Filantrópico passar de último a primeiro.
- Verificação da coluna `Leitos` do arquivo Barcelona contra o histórico
  `ST_LEITO` do DataSUS — asserção registrada em R1, não perseguida.
- Comparação do leito contratualizado CGCSS/SES-SP com `leitos_sus` —
  asserção registrada em R1, não medida.
- Números e datas exatas de contrato dos cinco switchers, para citação formal.
- Reclassificação geográfica (Santos, Cotia, Guarulhos) — aguarda Priscilla e
  Alberto; bloqueia o algoritmo de seleção do bloco de entrevistas.
- Forma funcional de `complexidade_pond_mort` — aguarda Priscilla.
- Figuras `fig_ae_09` em valores reais, conversão monetária das Seções 2 e 9,
  regeneração dos eixos de densidade.
- Leitura humana do PDF compilado, para coerência de prosa entre seções.
