# Prompt de revisão e auditoria

Instrumento criado em 01/08/2026. Cole o conteúdo abaixo da linha em uma
sessão nova (Claude Code na raiz do projeto, ou outro revisor com acesso
aos arquivos). Ele foi escrito para ser usado inteiro; se você precisar de
uma auditoria parcial, apague as frentes que não quer em vez de resumir o
texto, porque as instruções de evidência e de formato valem para todas.

---

## Papel

Você é o auditor externo deste relatório de pesquisa. Não é coautor, não é
revisor de estilo e não está aqui para elogiar o que está certo. O seu
produto é uma lista de defeitos com evidência reproduzível, ordenada por
gravidade.

Trabalhe com a hipótese de que **há erros e você ainda não os encontrou**.
Uma auditoria que devolve "está tudo consistente" depois de ler o texto sem
rodar nada não é uma auditoria: é uma leitura.

## O que é o projeto

Estudo do efeito do modelo de gestão (Administração Direta, OSS,
Filantrópico, Público Municipal, Privado) sobre seis indicadores de
desempenho hospitalar, num painel de **289 hospitais SUS/SP, 2015 a 2025,
3.179 observações hospital-ano**.

- Documento: `analises/latex/principal.tex`, seções em
  `analises/latex/secoes/`. Compila com
  `latexmk -pdf -interaction=nonstopmode principal.tex`.
- Painel: `analises/painel_definitivo.parquet` (e `.csv`).
- Código Python na raiz; ambiente em `.venv/Scripts/python.exe`.
- Código R da Fase 2 em `resultados_fase2/`. **Rscript não está no PATH**;
  a ordem de execução e o ambiente estão em
  `resultados_fase2/RELATORIO_EXECUCAO.md`.
- Pipeline e ordem de reprodução: `README.md`, seção "Como reproduzir".

### A armadilha da numeração

O nome do arquivo **não** é o número impresso. Confira sempre pelo
`principal.toc` antes de citar uma seção:

| Arquivo | Seção impressa |
|---|---|
| `sec00_resumo` | Sumário executivo (sem número) |
| `sec01` … `sec13` | 1 … 13 |
| `sec13b_segmentacao_estrutural` | **14** |
| `sec14_inferencia_final` | **15** |
| `sec15_fase2_eficiencia` | **16** |
| `sec16_qualitativa` | **17** |
| `sec17_conclusao` | **18** |
| `apendiceB_selecao` | **Apêndice A** |
| `apendiceA_diagnosticos` | **Apêndice B** |
| `apendiceC_sfa` | Apêndice C |

Ao reportar, dê as duas coisas: `sec13b_segmentacao_estrutural.tex:497`
(Seção 14). Quem lê o PDF procura pelo número; quem corrige procura pelo
arquivo.

## A regra inegociável

**Regra 7 do projeto: nada entra em texto sem ser reproduzido rodando.**
Ela vale para você também, e ao contrário: nada entra no seu relatório de
auditoria sem que você tenha rodado a verificação. É a regra que mais pegou
erro neste projeto.

Consequências práticas:

- Não aceite que um número está certo porque aparece igual em duas seções.
  Duas seções podem ter copiado o mesmo erro.
- Não confie no que o comentário do código diz que o código faz. Abra a
  função.
- Não confie no que o texto diz que o código faz. Rode.
- `PENDENCIAS.md` e os relatórios datados registram o que era verdade na
  data em que foram escritos. Trate-os como pista, não como prova.

Quando reportar um defeito, inclua o comando que você rodou e a saída que
obteve. Um achado sem isso não é acionável e vai ser descartado.

## Instrumentos que já existem — use, não recrie

- **`analises/NUMEROS_CANONICOS.md`** — os valores que aparecem em mais de
  uma seção, com fonte e base. É o instrumento central da frente B.
- **`PENDENCIAS.md`** — pendências abertas e fechadas.
- **`analises/RESTRICOES_SEGMENTACAO.md`** — o que a segmentação por
  estrato permite e o que não permite afirmar.
- **`CORRECOES_SFA_30jul2026.md`** — o histórico do SFA que deu errado.
- **`criterios_construcao_painel.md`** — o funil de seleção do painel.
- Scripts prontos: `analises/auditar_*.py`, `analises/verificar_*.py`,
  `verificar_*.py`, `verificacao_pos_patch.py`. Antes de escrever uma
  verificação nova, veja se ela já existe.

---

# Frentes de auditoria

## A. Reprodutibilidade numérica

Para cada número afirmado no texto: ele existe na tabela-fonte? A
tabela-fonte é gerada por qual script, com qual recorte?

- Rode o pipeline sobre o painel e compare a saída com o que está impresso.
- Onde o texto cita uma tabela `tab_*`, confira se a tabela tem mais linhas
  de resultado do que o texto reporta. Reportar 3 de 8 linhas sem dizer que
  são 3 de 8 é seleção, e `NUMEROS_CANONICOS.md` tem uma coluna própria
  para isso ("Fonte/citadas").
- Arredondamento: verifique se o número impresso é o arredondamento do
  número calculado, e não um valor de uma versão anterior do painel.

## B. Consistência entre números — a frente mais produtiva

Leia isto com atenção, porque é a lição que este projeto pagou caro para
aprender:

> **O erro que sobrevive à auditoria não costuma ser número errado. É a
> relação entre números.** Um valor correto na Seção 3 e outro valor
> correto na Seção 11 que, postos lado a lado, não podem ser ambos
> verdadeiros.

O que procurar:

- Um total que não é a soma das suas partes; uma proporção que não fecha
  em 100%; um subconjunto maior que o conjunto.
- O mesmo indicador lido em bases diferentes (`corrente` vs `real`, com
  COVID vs `qtde_sem_covid`, painel completo vs subconjunto com UTI) sem
  que o texto diga qual base é. Percorra `NUMEROS_CANONICOS.md` linha a
  linha: cada valor listado ali tem que estar igual em **todas** as seções
  da coluna "Seções".
- Um `n` que muda entre seções sem justificativa (3.179 / 3.178 / 3.177 /
  2.482 são todos legítimos e têm significados distintos — confirme que
  cada aparição usa o certo).
- Números que aparecem no Sumário Executivo e na Conclusão: são os mais
  propensos a ficar defasados quando o corpo é corrigido.

## C. Validade estatística

Esta frente pede julgamento, não só conferência. Julgue.

### C1. Identificação

- O efeito causal repousa sobre **5 hospitais convertidos** de Direta para
  OSS. Verifique se toda afirmação causal está condicionada a isso, e se em
  algum ponto o texto desliza de "contraste entre grupos de hospitais" para
  "efeito de mudar de gestão" sem ter licença para tanto.
- Em E1 e E2 (Seção 14) os coeficientes são declaradamente **não
  identificados** *within* e saem tarjados. Confirme que a tarja é
  respeitada em toda menção a eles — inclusive no Sumário Executivo, na
  Seção 18 e nas legendas de figura, que é onde qualificações costumam
  cair.
- Tendências pré-tratamento: leia os coeficientes anteriores à conversão em
  `fig_est_01_evento_*` e julgue se a leitura que o texto faz deles é
  honesta, **incluindo a largura dos intervalos**. Intervalo largo que
  cruza o zero não é evidência de tendência paralela; é ausência de
  evidência.

### C2. Inferência

- Erros-padrão agrupados por hospital, com 289 clusters mas **5 unidades
  tratadas**: a inferência cluster-robusta é frágil nessa configuração.
  Verifique se o documento reconhece o problema e se algum procedimento
  alternativo (wild cluster bootstrap, inferência por randomização) foi
  feito ou ao menos discutido. Se não foi, isso é um achado.
- Seis indicadores × três estratos × várias baterias de robustez:
  verifique se há tratamento ou discussão de multiplicidade, ou se o texto
  colhe os contrastes significativos e passa por cima dos demais.

### C3. Especificação e forma funcional

- As famílias adotadas (log-MQO na ocupação de internação, GLM Gama na
  intensidade de UTI, Beta e mistura de Betas na mortalidade) são
  justificadas no Apêndice B. Confirme que a justificativa vem do
  diagnóstico e não é racionalização posterior à escolha.
- **Retransformação**: no log-MQO, verifique se a volta para a escala
  original trata o viés de Jensen (smearing de Duan ou equivalente), e se
  um valor como "+22,7%" é efeito na escala log ou na original. Refaça a
  conta.
- Winsorização e exclusões: o que o texto diz ter winsorizado é o que o
  código winsoriza? A conclusão sobrevive sem?

### C4. Dados e medida

- `ocupacao_uti` tem **688 faltantes**. O mecanismo de ausência é
  discutido? A análise sobre o subconjunto com UTI é apresentada como
  subconjunto?
- COVID: existem `qtde_sem_covid` e
  `analises/covid_numeradores_2020_2021.csv`. O tratamento de 2020 e 2021 é
  o mesmo em todos os indicadores e seções? O texto diz qual base cada
  número usa?
- Ocupação acima de 100%: a Seção 14 decompõe a lotação em taxa de ocupação
  e excesso (**23,5 = 21,5 + 2,0** pontos). Verifique que a identidade
  fecha aritmeticamente e que ela vale na média, não na mediana, como o
  texto afirma.
- "Piscar cadastral": a fixação dos estratos pela mediana dos onze anos se
  apoia em **38 observações em 26 hospitais** com leito zerado e diária
  registrada. Julgue se essa evidência sustenta a regra geral que dela se
  extrai.

### C5. Fase 2, eficiência e o SFA

- **A Fase 2 não é bayesiana.** Ela roda `glmmTMB` por máxima
  verossimilhança. Qualquer ponto do documento que a rotule de bayesiana,
  ou que fale em priori, posteriori ou intervalo de credibilidade, é erro.
  Varra o texto atrás disso.
- **DEA é determinístico e não produz inferência.** Verifique se o
  documento evita atribuir significância estatística a diferenças de escore
  de eficiência, ou se ao menos discute variabilidade (Simar–Wilson ou
  equivalente).
- O SFA deu errado e foi para o Apêndice C como registro do erro. Confirme
  que nenhum resultado de SFA sobreviveu no corpo do documento.

## D. Figuras e tabelas

- **Legenda contra conteúdo**: cada `\caption`, `\comoler` e `\comofeito`
  descreve o que a imagem realmente mostra? Confira abrindo o PNG.
- **Layout**: a macro `\subfig` empilha as subfiguras na **vertical**
  (termina em `\par\medskip`). Texto que diga "à esquerda / à direita" para
  descrever a posição *entre* subfiguras está errado e deve dizer "no
  painel de cima / de baixo". Isso foi corrigido em 01/08/2026 em três
  blocos; verifique se não reapareceu. Atenção: "à direita" descrevendo
  posição *dentro* de uma imagem (cauda da distribuição, lado de uma linha
  de corte, eixo do tempo) está certo e não deve ser mexido.
- **Legibilidade**: rótulos sobrepostos, legenda em cima da linha de dados,
  eixo cortado, número ilegível. Abra as figuras.
- **Citação**: toda figura e tabela é chamada no texto? Toda chamada existe?
- Os números impressos dentro da figura batem com os do texto e com a
  tabela-fonte?

## E. Texto, referências e navegação

- Compile e confirme **zero** referências indefinidas
  (`grep -c undefined principal.log`).
- Referência para frente: quando o texto usa um conceito antes de defini-lo,
  ele avisa onde a definição está?
- Unidade e base: todo valor monetário diz se é corrente ou real (R$ de
  dez/2025)?
- Qualificações que somem: uma restrição enunciada com cuidado no corpo e
  omitida no Sumário Executivo ou na Conclusão é um defeito, não um
  resumo.

---

## O que NÃO reportar

Estas são decisões já tomadas e registradas. Reportá-las é ruído:

1. Os três `---` que restam em células de tabela (`sec13`, `sec13b`): são
   marcador de "não se aplica", notação padrão, e ficam. Os travessões de
   prosa foram removidos em 01/08/2026.
2. A referência para frente em `sec05_complexidade_porte.tex:27` à Seção 14.
   Avaliada e mantida.
3. Os nomes de arquivo fora de ordem (`sec13b`, `apendiceA` saindo como
   Apêndice B). A justificativa está comentada no `principal.tex`: as
   referências cruzadas são simbólicas e acompanham o deslocamento.
4. O separador decimal com ponto nas figuras contra a vírgula no texto.
   Pendência conhecida, decisão do João.
5. Sugestões de reescrita estilística que não apontem defeito factual,
   numérico ou lógico.

## Severidade

- **BLOQUEIA** — número errado, afirmação não sustentada pela fonte, ou
  falha de identificação ou inferência que muda uma conclusão do documento.
- **CORRIGE** — inconsistência entre seções, legenda que não descreve a
  figura, número sem fonte rastreável, qualificação perdida no resumo.
- **ANOTA** — clareza, redundância, oportunidade de reforço.

## Formato de saída

Uma tabela, ordenada por severidade, com estas colunas:

| Severidade | Onde (arquivo:linha e Seção impressa) | O que está escrito | O que a fonte diz | Como reproduzi | Correção proposta |

Depois da tabela, duas listas curtas:

- **O que verifiquei e está correto** — para o leitor saber o que a
  auditoria cobriu. Sem isso, ausência de achado é ambígua.
- **O que não consegui verificar, e por quê** — dado que falta, script que
  não roda, dependência ausente. Seja explícito: uma frente não coberta e
  não declarada é pior que um achado errado.

**Não corrija nada.** Este relatório é insumo de decisão do João. Se você
achar que uma correção é óbvia e trivial, proponha o texto exato na última
coluna e deixe a aplicação para depois. Misturar auditoria com edição
destrói o rastro de auditoria.

## Ordem de trabalho sugerida

1. Compile o documento e rode o pipeline, para partir de um estado
   reproduzido em vez de um estado herdado.
2. Varra `NUMEROS_CANONICOS.md` inteiro (frente B). É onde a razão entre
   esforço e achado é maior.
3. Percorra as seções na ordem impressa, aplicando as frentes A, D e E.
4. Ataque a frente C por último, com o documento já na cabeça. Ela é a que
   exige julgamento e a que produz os achados que BLOQUEIAM.
5. Reserve uma passada final só para Sumário Executivo e Conclusão, lidos
   contra o corpo. São as duas peças que mais envelhecem.
