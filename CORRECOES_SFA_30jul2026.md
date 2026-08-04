# Correções da SFA no documento — guia de substituição manual

**Data:** 30/07/2026
**Motivo:** a auditoria da §16 do `PENDENCIAS.md` mostrou que a razão principal
hoje impressa para desqualificar a SFA **não se sustenta**, e que a redação
atual diz mais do que a evidência permite.
**Reprodução:** `analises/auditar_sfa_validade.py` e
`resultados_fase2/auditar_fronteira_sem_uti.R`.

---

## O que muda, em uma frase

Sai a tese de que **a fronteira inteira está desqualificada e a Translog não
descreve a produção hospitalar**. Entra a formulação correta e mais modesta:
a SFA é **verificação complementar**, concorda com o DEA na ordem, tem dois
problemas conhecidos que impedem usá-la como magnitude, e por isso **as
conclusões de eficiência do documento vêm do DEA**. Os escores continuam
impressos nas tabelas como registro.

### Por que a redação atual precisa mudar

| Afirmação hoje impressa | Situação |
|---|---|
| Degeneração das OSS (TE constante em 0,9993) | **Confirmada.** Sobrevive a todas as especificações. Mantida. |
| Monotonicidade violada em 94,9% | **Número correto** (reproduzido: 94,93%). |
| "A fronteira não se comporta como função de produção" | **Excessivo.** A violação está confinada a **um** insumo; leitos 99,7% e valor 99,6% respeitam. |
| "A Translog não descreve bem o modo como estes hospitais transformam insumo em produto" | **Refutado.** A violação vem de leito de UTI ser **subconjunto** de leito total (aninhamento em 100% das obs, razão mediana 0,115, corr 0,825). Retirado esse insumo, a violação **desaparece** e nada se move (Spearman 0,986). |
| "Nenhum valor é citável, em nenhuma categoria" | **Escopo herdado da premissa refutada.** A degeneração sozinha alcança as OSS, não as cinco categorias. |

**Consequência prática:** o tom novo é mais defensável, não mais frouxo. Você
deixa de afirmar uma coisa que um parecerista pode derrubar rodando duas
linhas de R, e passa a afirmar só o que os dados sustentam.

---

## Índice das 20 correções

| # | Arquivo | Localizar por |
|---|---|---|
| C1 | `sec00_resumo` | "Nenhum coeficiente da fronteira estocástica é citável" |
| C2–C11 | `sec15_fase2_eficiencia` | ver cada entrada |
| C12–C16 | `sec16_qualitativa` | ver cada entrada |
| C17–C18 | `sec17_conclusao` | ver cada entrada |
| C19–C20 | `apendiceB_selecao` | ver cada entrada |
| C21–C22 | `sec15_fase2_eficiencia` | **acrescentadas em 30/07** — figura da dispersão SFA×DEA, que tinha escapado do índice |

> Fora do escopo da SFA, anotadas no anexo ao fim deste arquivo: **R1**,
> decisão editorial sobre a passagem das cinco famílias em `sec15`; **R2**,
> coluna de efeito na tabela de robustez em `sec13`; **R3**, o `n.a.` da
> tabela de contrastes em `sec11` (**depende do R2**).

> `arquivo/roteiro_entrevistas.tex` **não** entra no PDF (não está em
> `principal.tex`) — ignorar.
> `apendiceA_diagnosticos.tex:60` fala da separação na **parte 1 do modelo de
> UTI**, não da SFA — não mexer.

---

# C1 — Sumário executivo (`sec00_resumo.tex`, ~linha 90)

**Localizar:** *"Nenhum coeficiente da fronteira estocástica é citável"*

### Texto atual
> \item \textbf{Nenhum coeficiente da fronteira estocástica é citável.} A
>   forma Translog estimada tem a monotonicidade violada em \textbf{94,9\%}
>   das observações e não se comporta como função de produção. Ela
>   permanece no documento como diagnóstico dessa inadequação; todas as
>   conclusões de eficiência apoiam-se no DEA (Seção~\ref{sec:fase2}).

### Texto novo
> \item \textbf{As conclusões de eficiência apoiam-se no DEA.} A fronteira
>   estocástica foi estimada como verificação complementar e \textbf{concorda
>   com o DEA na ordem das redes}, mas não é usada para magnitude: a
>   eficiência técnica das OSS degenera numericamente (fica constante em
>   0,9993) e o insumo de leitos de UTI está mal especificado, por ser um
>   subconjunto do total de leitos que também entra na fronteira. Os escores
>   aparecem nas tabelas como registro (Seção~\ref{sec:fase2}).

---

# C2 — `sec15`, \comoler dos violinos (~linha 154–161)

**Localizar:** *"O painel (b) é diagnóstico, não medida"*

### Texto atual (trecho final do \comoler)
> O painel (b) é
> diagnóstico, não medida: pelo motivo estabelecido adiante, nenhum número
> dele é citável. O Privado aparece só como registro.}

### Texto novo
> O painel (b) é
> verificação complementar: pelos motivos estabelecidos adiante, o documento
> não extrai magnitude dele, e o valor das OSS em especial é artefato
> numérico. O Privado aparece só como registro.}

---

# C3 — `sec15`, legenda da Figura dos violinos (~linha 169–178)

**Localizar:** *"é \textbf{diagnóstico e não medida}"*

### Texto atual
> \caption{Eficiência por categoria nos dois métodos. O painel (a), do DEA,
> é a medida em que este documento se apoia. O painel (b), da fronteira
> estocástica, é \textbf{diagnóstico e não medida}: a concentração das OSS
> junto ao valor 1 é uma degeneração numérica do modelo, e a fronteira que
> o gerou tem a monotonicidade violada em 94,9\% das observações, de modo
> que \textbf{nenhum valor do painel (b) é citável, em nenhuma categoria}
> (o texto explica). Como nos violinos da
> Seção~\ref{sec:categorias}, onde a silhueta é mais gorda há mais
> hospitais com aquele valor de eficiência; a largura não é percentual nem
> contagem, e não se compara entre categorias.}

### Texto novo
> \caption{Eficiência por categoria nos dois métodos. O painel (a), do DEA,
> é a medida em que este documento se apoia. O painel (b), da fronteira
> estocástica, entra como \textbf{verificação complementar}: a concentração
> das OSS junto ao valor 1 é uma degeneração numérica do modelo, e a
> fronteira que o gerou tem um insumo mal especificado, de modo que
> \textbf{o documento não retira magnitudes do painel (b)} (o texto
> explica). Os dois painéis concordam na ordem das redes. Como nos violinos
> da Seção~\ref{sec:categorias}, onde a silhueta é mais gorda há mais
> hospitais com aquele valor de eficiência; a largura não é percentual nem
> contagem, e não se compara entre categorias.}

---

# C4 — `sec15`, \comofeito dos violinos (~linha 186–189)

**Localizar:** *"nenhum valor do painel é citável, em nenhuma categoria"*

### Texto atual (trecho final)
> No painel (b) a concentração das OSS
> junto a 1 é uma degeneração numérica do modelo, e nenhum valor do painel
> é citável, em nenhuma categoria, pelo motivo estabelecido no texto.}

### Texto novo
> No painel (b) a concentração das OSS
> junto a 1 é uma degeneração numérica do modelo, e o documento não retira
> magnitudes desse painel, pelos motivos estabelecidos no texto.}

---

# C5 — `sec15`, "A contraparte paramétrica" — abertura (~linha 192–201)

**Localizar:** *"e traz três honestidades a registrar, que juntas retiram dela o estatuto de medida"*

### Texto atual
> põe as OSS na mesma ponta de cima em que o DEA as põe, e traz
> três honestidades a registrar, que juntas retiram dela o estatuto de
> medida:

### Texto novo
> põe as OSS na mesma ponta de cima em que o DEA as põe, e traz
> três honestidades a registrar, que juntas explicam por que este documento
> a usa como verificação de direção e não como medida de magnitude:

---

# C6 — `sec15`, a passagem da monotonicidade de UTI (~linha 214–222)

**Esta é a correção mais importante do conjunto.**

**Localizar:** *"o insumo de UTI é mal comportado na forma Translog"*

### Texto atual
> \textbf{o insumo de UTI é mal
> comportado na forma Translog}, com a monotonicidade violada em
> \textbf{94,9\% das observações} (97,8\% entre as que têm leito de UTI
> habilitado, tenham-no usado ou não no ano; 96,9\% se o corte for ter
> registrado diária de UTI),
> contra 99,7\% de respeito para leitos e 99,6\% para valor: herança
> do logaritmo de um mais UTI com 19\% de zeros e da colinearidade alta
> com leitos totais e valor, e o motivo pelo qual qualquer leitura fina
> de UTI nesta fronteira precisa da sensibilidade que a remove;

### Texto novo
> \textbf{o insumo de leitos de UTI está mal
> especificado}, com a monotonicidade violada em \textbf{94,9\% das
> observações} (97,8\% entre as que têm leito de UTI habilitado, tenham-no
> usado ou não no ano; 96,9\% se o corte for ter registrado diária de UTI),
> contra 99,7\% de respeito para leitos e 99,6\% para valor. A causa é
> conhecida e específica: \textbf{leito de UTI é subconjunto do total de
> leitos} (em 100\% das observações, com razão mediana de 0,115 e
> correlação de 0,82 entre os dois logaritmos), e os dois entram na mesma
> fronteira. Condicionado ao total de leitos, mais UTI não é mais
> capacidade, é composição diferente — e como o produto medido são as
> saídas, que caem quando a permanência sobe, uma elasticidade condicional
> negativa é o resultado esperado. \textbf{O defeito é da escolha de
> insumos, não da forma funcional}: reestimada sem esse insumo, a fronteira
> volta a ser monótona e a ordenação dos hospitais praticamente não se move
> (correlação de ordem de 0,99). Por isso nenhuma leitura fina de UTI é
> feita sobre esta fronteira;

> **Nota:** os dois números novos desta redação (o aninhamento em 100% e a
> correlação de ordem de 0,986, impressa como 0,99) vêm de
> `resultados_fase2/auditar_fronteira_sem_uti.R`. Se preferir não introduzir
> resultado novo no documento, corte da frase *"reestimada sem esse insumo"*
> até *"0,99)"* — o resto da correção continua válido e suficiente.

---

# C7 — `sec15`, "não é corroboração" (~linha 229–232)

**Localizar:** *"um deles, pelo motivo estabelecido adiante, não descreve uma função de produção"*

### Texto atual
> Ela mede quanto os dois procedimentos se
> parecem quando aplicados aos mesmos dados, e \textbf{não é corroboração
> de um pelo outro}: os dois consomem a mesma informação, e um deles, pelo
> motivo estabelecido adiante, não descreve uma função de produção.

### Texto novo
> Ela mede quanto os dois procedimentos se
> parecem quando aplicados aos mesmos dados, e \textbf{não é corroboração
> de um pelo outro}: os dois consomem a mesma informação, de modo que a
> semelhança é esperada e não constitui validação independente.

---

# C8 — `sec15`, título e advertência da equação de ineficiência (~linha 239–267)

**Localizar:** *"e por que nenhum coeficiente dela é citável"*

### Texto atual (três parágrafos: título, advertência e concentração)
> \textbf{A equação de ineficiência, e por que nenhum coeficiente dela é
> citável.} A fronteira estocástica estima, em paralelo à produção, uma
> segunda equação que explica \emph{quanta} ineficiência cada hospital
> carrega. […]
>
> A tabela é reproduzida porque omiti-la seria pior: […] \textbf{A monotonicidade da fronteira que gerou
> estes coeficientes está violada em 94,9\% das observações}, como o
> parágrafo anterior registrou. Uma fronteira violada em quase toda a
> amostra \textbf{não se comporta como função de produção}, e significância
> mede a precisão de uma estimativa, não a validade da estrutura de onde
> ela sai: coeficiente preciso extraído de fronteira mal-comportada é
> preciso sobre um objeto que não é o que o nome diz. Por isso, e não por
> conveniência de resultado, \textbf{nenhum coeficiente desta tabela é
> interpretável como magnitude de ineficiência, e nenhum entra em conclusão
> alguma deste documento}.
>
> A violação também não se concentra em categoria nenhuma, o que impede
> tratá-la como problema de uma linha só: ela vai de 93,6\% no Filantrópico
> a \textbf{99,3\% na administração Direta}, que é justamente a referência
> de todos os contrastes da tabela. Cinco vírgula sete pontos de amplitude
> sobre uma base de 93,6\% é defeito geral da forma funcional. A fronteira
> inteira está desqualificada como medida, não uma parte dela.

### Texto novo
> \textbf{A equação de ineficiência, e por que ela não fornece magnitudes.}
> A fronteira estocástica estima, em paralelo à produção, uma
> segunda equação que explica \emph{quanta} ineficiência cada hospital
> carrega. […mantenha o restante do parágrafo…]
>
> A tabela é reproduzida porque omiti-la seria pior: […mantenha…] Mas ela vem
> com uma advertência que vale para cada uma das suas linhas e que precisa
> ser lida \emph{antes} dos números. \textbf{Estes coeficientes são estimados
> conjuntamente com o termo degenerado das OSS}, numa fronteira em que um dos
> três insumos está mal especificado. Significância mede a precisão de uma
> estimativa, não a validade da estrutura de onde ela sai. Por isso, e não
> por conveniência de resultado, \textbf{este documento não usa nenhum
> coeficiente desta tabela como magnitude de ineficiência, e nenhum entra em
> conclusão alguma}. Eles ficam registrados como leitura de ordem de
> grandeza relativa, a ser confrontada com o DEA.
>
> A má especificação do insumo de UTI, por sua vez, não se concentra em
> categoria nenhuma: a violação vai de 93,6\% no Filantrópico a 99,3\% na
> administração Direta, que é justamente a referência de todos os contrastes
> da tabela. Não é problema de uma linha só, e sim uma característica de como
> a fronteira foi montada — o que é mais uma razão para as magnitudes virem
> do DEA.

---

# C9 — `sec15`, legenda da Tabela da equação de ineficiência (~linha 271–278)

**Localizar:** *"Tabela tarjada"*

### Texto atual
> \textbf{Tabela tarjada: a monotonicidade da fronteira que produziu estes
> coeficientes está violada em 94,9\% das observações, de 93,6\% no
> Filantrópico a 99,3\% na própria Direta. Nenhum valor desta tabela é
> interpretável como magnitude nem entra em conclusão deste documento; ela
> é diagnóstico da inadequação da forma Translog.}}

### Texto novo
> \textbf{Nenhum valor desta tabela é usado como magnitude nem entra em
> conclusão deste documento: os coeficientes são estimados junto com o termo
> degenerado das OSS, numa fronteira cujo insumo de UTI está mal
> especificado. A tabela é registro, e as conclusões de eficiência vêm do
> DEA.}}

---

# C10 — `sec15`, "O que a tabela mostra" (~linha 296 e ~318–322)

**Localizar (a):** *"lida como diagnóstico e não como medida"*

| Atual | Novo |
|---|---|
| \textbf{O que a tabela mostra, lida como diagnóstico e não como medida.} | \textbf{O que a tabela mostra, lida como ordem de grandeza e não como medida.} |

**Localizar (b):** *"Lidos como magnitudes, não dizem"* — atenção, no fonte a
frase quebra entre `dizem` e `nada`, então busque só até `dizem`.

### Texto atual
> Lidos como \emph{ordens de grandeza relativas
> dentro de uma fronteira que se sabe mal especificada}, esses sinais
> sugerem que a estrutura física do hospital move a ineficiência medida
> mais do que a rede que o administra. Lidos como magnitudes, não dizem
> nada, pelo motivo já enunciado.

### Texto novo
> Lidos como \emph{ordens de grandeza relativas
> dentro de uma fronteira que se sabe mal especificada}, esses sinais
> sugerem que a estrutura física do hospital move a ineficiência medida
> mais do que a rede que o administra. Como magnitudes, não são usados neste
> documento, pelo motivo já enunciado.

---

# C11 — `sec15`, "A regra, enunciada uma vez" (~linha 324–331)

**Localizar:** *"A regra, enunciada uma vez para todo o documento"*

### Texto atual
> \textbf{A regra, enunciada uma vez para todo o documento.} Nenhum
> coeficiente e nenhum nível da fronteira estocástica é citável, em nenhuma
> categoria de gestão, nem aqui nem nas seções seguintes. A SFA permanece
> no documento como \textbf{diagnóstico da própria inadequação da forma
> Translog a esta tecnologia de produção}, e a violação em 94,9\% é ela
> mesma um achado: diz que a Translog não descreve bem o modo como estes
> hospitais transformam insumo em produto. \textbf{As conclusões de
> eficiência deste documento apoiam-se no DEA.}

### Texto novo
> \textbf{A regra, enunciada uma vez para todo o documento.} \textbf{As
> conclusões de eficiência deste documento apoiam-se no DEA}, que é o
> instrumento mais confiável para estes dados: ele não exige forma funcional
> e não sofre com a degeneração que atinge as OSS na fronteira paramétrica.
> Nenhuma magnitude da fronteira estocástica é usada como resultado, aqui
> nem nas seções seguintes, e o nível das OSS não é comparável com o das
> demais categorias. A SFA permanece no documento pelo que ela de fato
> oferece: uma \textbf{verificação de direção por um método de natureza
> oposta}, que concorda com o DEA na ordem das redes (correlação de ordem de
> 0,62, e 0,63 excluindo as OSS). Os escores seguem impressos nas tabelas
> como registro de como as análises foram conduzidas.

---

# C12 — `sec16`, \comofeito das seis tabelas (~linha 124–135)

**Localizar:** *"Ressalva que vale para todas as seis tabelas"*

### Texto atual
> \textbf{Ressalva que vale
> para todas as seis tabelas e para todas as suas linhas:} a coluna SFA
> \textbf{não é citável em nenhuma categoria de gestão}. A fronteira que a
> produziu tem a monotonicidade violada em 94,9\% das observações
> (Seção~\ref{sec:fase2}) e não se comporta como função de produção. Nas
> linhas de categoria OSS há ainda um segundo problema, a
> \textbf{degeneração numérica}: a eficiência técnica das OSS na fronteira
> estocástica é praticamente uma constante (0,9993 a 0,9994 em todo o
> painel), não uma medida do hospital. \textbf{Em todas as linhas, portanto,
> vale a coluna DEA}; a coluna SFA fica impressa por transparência sobre
> como a seleção foi conduzida, e não deve ser citada nem comparada entre
> categorias.}

### Texto novo
> \textbf{Ressalva que vale
> para todas as seis tabelas e para todas as suas linhas:} \textbf{a coluna
> que vale é a do DEA}, que é o instrumento em que as conclusões de
> eficiência deste documento se apoiam. A coluna SFA fica impressa por
> transparência sobre como a seleção foi conduzida, mas não fornece
> magnitude: a fronteira que a produziu tem um insumo mal especificado
> (Seção~\ref{sec:fase2}). Nas linhas de categoria OSS há ainda um segundo
> problema, mais grave, a \textbf{degeneração numérica}: a eficiência
> técnica das OSS na fronteira estocástica é praticamente uma constante
> (0,9993 a 0,9994 em todo o painel), não uma medida do hospital, e por isso
> \textbf{não deve ser comparada com a de outras categorias}.}

---

# C13 — `sec16`, \comofeito do bloco b (~linha 166–169)

### Texto atual
> com a mesma ressalva, que vale para todas as linhas: a coluna SFA não é
> citável em categoria nenhuma, e o 0,999 da linha OSS acumula ainda a
> degeneração numérica.}

### Texto novo
> com a mesma ressalva, que vale para todas as linhas: a coluna que vale é a
> do DEA, e o 0,999 da linha OSS é degeneração numérica, não medida.}

---

# C14 — `sec16`, "Nota sobre o critério" (~linha 173–182)

**Localizar:** *"Como nenhum valor da fronteira estocástica é citável"*

### Texto atual
> A
> seleção exigia posição extrema \emph{nos dois} escores, DEA e SFA, e
> desempatava por uma média dos dois percentis. Como nenhum valor da
> fronteira estocástica é citável (Seção~\ref{sec:fase2}), o critério foi
> reexecutado \textbf{sem} a SFA, para saber de quanto a lista depende dela.

### Texto novo
> A
> seleção exigia posição extrema \emph{nos dois} escores, DEA e SFA, e
> desempatava por uma média dos dois percentis. Como o documento apoia suas
> conclusões de eficiência no DEA (Seção~\ref{sec:fase2}), o critério foi
> reexecutado \textbf{sem} a SFA, para saber de quanto a lista depende dela.

---

# C15 — `sec16`, \comofeito do bloco c (~linha 212–214)

### Texto atual
> com
> a mesma ressalva: a coluna SFA não é citável em categoria nenhuma.}

### Texto novo
> com
> a mesma ressalva: a coluna que vale é a do DEA.}

---

# C16 — `sec16`, "Esta lista depende da SFA" (~linha 224–231)

**Localizar:** *"Como \textbf{nenhum valor da fronteira estocástica é citável}"*

### Texto atual
> Como \textbf{nenhum valor da
> fronteira estocástica é citável}, esta seleção não pode ser tratada como
> fechada: ela precisa ser refeita apenas sobre o DEA antes que as
> entrevistas do bloco c sejam agendadas.

### Texto novo
> Como \textbf{o DEA é o instrumento em que este
> documento se apoia}, esta seleção não pode ser tratada como fechada: ela
> precisa ser refeita apenas sobre o DEA antes que as entrevistas do bloco c
> sejam agendadas.

> **Atenção:** o resto do parágrafo (os CNES que mudam) permanece **igual** —
> o achado continua válido, só muda a justificativa.

---

# C17 — `sec17`, eficiência produtiva das OSS (~linha 63–68)

**Localizar:** *"mas \textbf{não conta como confirmação}"*

### Texto atual
> A fronteira estocástica põe as OSS na
> mesma ponta, mas \textbf{não conta como confirmação}: a monotonicidade
> dela está violada em 94,9\% das observações e nenhum coeficiente seu é
> citável, de modo que este achado se apoia no DEA e apenas nele.

### Texto novo
> A fronteira estocástica põe as OSS na
> mesma ponta, mas \textbf{não conta como confirmação independente}: os dois
> métodos consomem a mesma informação, e a fronteira paramétrica ainda
> degenera justamente no contraste das OSS. Este achado apoia-se, portanto,
> no DEA e apenas nele.

---

# C18 — `sec17`, a sexta fronteira (~linha 141–149)

**Localizar:** *"E uma sexta, sobre um dos instrumentos"*

### Texto atual
> E uma sexta, sobre um dos instrumentos: \textbf{nenhum coeficiente e
> nenhum nível da fronteira estocástica é citável}, em nenhuma categoria de
> gestão. A forma Translog estimada tem a monotonicidade violada em 94,9\%
> das observações, de 93,6\% no Filantrópico a 99,3\% na própria
> administração Direta, e uma fronteira violada em quase toda a amostra não
> se comporta como função de produção. A SFA permanece no documento como
> diagnóstico dessa inadequação, que é ela própria um achado sobre a
> tecnologia de produção hospitalar; \textbf{todas as conclusões de
> eficiência apoiam-se no DEA} (Seção~\ref{sec:fase2}).

### Texto novo
> E uma sexta, sobre a escolha de instrumento: \textbf{todas as conclusões de
> eficiência apoiam-se no DEA}, e nenhuma magnitude da fronteira estocástica
> é usada como resultado (Seção~\ref{sec:fase2}). A SFA foi estimada como
> verificação por um método de natureza oposta e \textbf{concorda com o DEA
> na ordem das redes}, mas dois problemas impedem tomá-la como medida: a
> eficiência técnica das OSS degenera numericamente, ficando constante em
> 0,9993, e o insumo de leitos de UTI está mal especificado, por ser um
> subconjunto do total de leitos que também entra na fronteira. O DEA não
> tem nenhum dos dois problemas — não impõe forma funcional e não degenera
> nas OSS —, e é por isso que ele é o instrumento das conclusões.

---

# C19 — `apendiceB`, \comofeito do bloco d (~linha 150–157)

**Localizar:** *"a diferença de SFA entre âncora e par não mede nada"*

### Texto atual
> Vale aqui, com força redobrada, a ressalva do bloco a: o SFA
> de 0,999 das âncoras OSS é degeneração numérica, de modo que \textbf{o
> contraste do par deve ser lido apenas na coluna DEA}, a diferença de
> SFA entre âncora e par não mede nada.}

### Texto novo (pode ficar como está)
> Vale aqui, com força redobrada, a ressalva do bloco a: o SFA
> de 0,999 das âncoras OSS é degeneração numérica, de modo que \textbf{o
> contraste do par deve ser lido apenas na coluna DEA}, a diferença de
> SFA entre âncora e par não mede nada.}

> **Sem alteração necessária.** Esta passagem já está correta e no tom certo:
> ela invoca a degeneração das OSS, que é o defeito real, e não a
> monotonicidade. Listada aqui só para você não procurá-la em vão.

---

# C20 — `apendiceB`, "O que esta divergência mede" (~linha 260–273)

**Localizar:** *"Essa leitura não se sustenta"*

### Texto atual
> \textbf{O que esta divergência mede, e o que ela não mede.} Este bloco é o
> único da seleção construído \emph{inteiramente} sobre a fronteira
> estocástica, e a Seção~\ref{sec:fase2} estabelece que \textbf{nenhum valor
> dela é citável}: a monotonicidade da Translog está violada em 94,9\% das
> observações, de modo que a fronteira não se comporta como função de
> produção. A leitura original deste bloco supunha que a discordância
> apontasse alguma coisa \emph{sobre o hospital}, uma composição de casos
> atípica ou um insumo mal medido. \textbf{Essa leitura não se sustenta.}
> Divergência entre um instrumento válido e um instrumento mal especificado
> é, em primeiro lugar, diagnóstico do segundo, e o candidato mais econômico
> para explicar o afastamento é a própria inadequação da forma funcional a
> hospitais com este perfil de insumo, não um fator omitido na operação
> deles.

### Texto novo
> \textbf{O que esta divergência mede, e o que ela não mede.} Este bloco é o
> único da seleção construído \emph{inteiramente} sobre a fronteira
> estocástica, e a Seção~\ref{sec:fase2} estabelece que \textbf{as conclusões
> de eficiência se apoiam no DEA}, não nela. A leitura original deste bloco
> supunha que a discordância apontasse alguma coisa \emph{sobre o hospital},
> uma composição de casos atípica ou um insumo mal medido. \textbf{Essa
> leitura precisa ser qualificada.} Divergência entre um instrumento em que o
> documento se apoia e outro que tem um insumo mal especificado é, em
> primeiro lugar, candidata a diagnóstico do segundo. Estes hospitais entram
> como \textbf{sugeridos}, e a entrevista deve tratar a divergência como
> pergunta aberta, não como fato estabelecido sobre a operação deles.

---

# C21 — `sec15`, \comoler da dispersão SFA×DEA (~linha 333–339)

**Acrescentada em 30/07/2026.** Esta passagem e a C22 **tinham escapado** do
levantamento original: as duas ficam depois da "regra enunciada uma vez"
(C11) e repetem a formulação que ela abandona. Sem elas, o documento
corrigiria a regra e deixaria a figura seguinte contradizendo-a.

**Localizar:** *"e nenhum valor dele é citável"* (fim do `\comoler`)

### Texto atual (trecho final)
> Semelhança não é confirmação: o eixo vertical vem
> de uma fronteira cuja monotonicidade está violada em 94,9\% das
> observações, e nenhum valor dele é citável.}

### Texto novo
> Semelhança não é confirmação: os dois procedimentos consomem a mesma
> informação, e o eixo vertical vem de uma fronteira com um insumo mal
> especificado, da qual o documento não retira magnitude.}

---

# C22 — `sec15`, legenda da Figura `fig:convergencia` (~linha 344–347)

**Acrescentada em 30/07/2026.**

**Localizar:** *"O eixo vertical é diagnóstico, não medida"*

### Texto atual
> \caption{Semelhança entre os dois procedimentos de eficiência: cada ponto
> é um hospital num ano, posicionado pelo escore DEA (horizontal) e pela
> eficiência SFA (vertical). O eixo vertical é diagnóstico, não medida:
> nenhum valor de SFA é citável.}

### Texto novo
> \caption{Semelhança entre os dois procedimentos de eficiência: cada ponto
> é um hospital num ano, posicionado pelo escore DEA (horizontal) e pela
> eficiência SFA (vertical). Os dois concordam na ordem das redes; o eixo
> vertical entra como verificação de direção, e o documento não retira
> magnitude dele.}

---

# C23 — `apendiceB`, a pergunta de entrevista do bloco d (~linha 274–280)

**Encontrada durante a aplicação, em 30/07/2026**, não no levantamento
original. Fica **imediatamente abaixo** da C20 e sobrevivia a ela: corrigido
o parágrafo da C20, o seguinte ainda mandava o entrevistador perguntar por
que a Translog falha — que é exatamente a tese refutada.

**Localizar:** *"por que a Translog falha aqui"*

### Texto atual
> cuja pergunta de entrevista deixa de ser
> ``o que há neste hospital que os modelos não capturam'' e passa a ser
> ``estes hospitais têm alguma coisa em comum que ajude a entender por que a
> Translog falha aqui''.

### Texto novo
> cuja pergunta de entrevista deixa de ser
> ``o que há neste hospital que os modelos não capturam'' e passa a ser
> ``estes hospitais têm alguma coisa em comum que explique por que os dois
> procedimentos discordam justamente aqui''.

---

## Checklist de execução — **TUDO APLICADO EM 30/07/2026**

- [x] C1 `sec00_resumo`
- [x] C2 C3 C4 `sec15` — figura dos violinos (3 blocos)
- [x] C5 C6 C7 `sec15` — "A contraparte paramétrica" (**C6 é a principal**)
- [x] C8 C9 C10 C11 `sec15` — equação de ineficiência e a regra
- [x] C21 C22 `sec15` — figura da dispersão SFA×DEA (**vêm depois da C11 no fonte**)
- [x] C12 C13 C14 C15 C16 `sec16`
- [x] C17 C18 `sec17`
- [x] C19 (sem alteração) C20 C23 `apendiceB`
- [x] R1 `sec15` — passagem das cinco famílias (**decisão editorial, não é correção de erro**)
- [x] R2 `sec13` — coluna de efeito na tabela de robustez (**dois números novos, já reproduzidos**)
- [x] R3 `sec11` — o `n.a.` da tabela de contrastes (**aplicar junto com R2, mesma origem**)

**Verificação:** `latexmk -pdf principal.tex` → 136 páginas, sem erro, **zero
`Overfull \hbox`** no documento inteiro (a tabela de 7 colunas do R2 coube).
Varredura por `citável`, `Tabela tarjada`, `não se comporta como função de
produção` e `n.a.`: os resíduos que sobraram invocam a **degeneração das
OSS**, que é o defeito confirmado, ou tratam de mortalidade e não da SFA.
Nenhum precisa mudar.

### O que ficou aberto, de propósito

1. **`PENDENCIAS.md` 12.A.11** (bloco c das entrevistas) — **continua
   aberta**. A lista segue provisória e refazê-la só sobre o DEA continua
   sendo a recomendação. Nenhuma destas correções a resolve.
2. **A mortalidade em `sec13`.** Com a coluna de efeito do R2 à frente, fica
   visível que ela tem $z = -1{,}71$ no painel completo e $z = -2{,}01$ sem o
   biênio: cruza o zero com a pandemia dentro, não cruza sem. Isso já estava
   impresso antes, mas agora salta. **Não foi resolvido** — conferir se a
   Seção~11 ou 12 afirma algo em tensão com isso é escopo de outra seção.

### Depois de aplicar

1. **`analises/NUMEROS_CANONICOS.md`** — as linhas de SFA (0,788/0,784 e
   0,62/0,63) continuam válidas; nenhuma mudança de número, só de estatuto.
2. **`PENDENCIAS.md` item 12.A.12** — fechar, registrando qual foi a decisão
   de escopo.
3. **`PENDENCIAS.md` item 12.A.11** (bloco c das entrevistas) — **continua
   aberto**. Nenhuma destas correções o resolve: a lista do bloco c segue
   provisória, e refazê-la só sobre o DEA continua sendo a recomendação.
4. Nenhum `.csv`, `.rds` ou figura precisa ser regerado — **nenhum número
   muda**.

---
---

# Anexo — R1, fora do escopo da SFA

# R1 — `sec15`, a passagem das cinco famílias (~linha 394–449)

**Data:** 30/07/2026. **Natureza:** decisão editorial de registro, **não é
correção de erro**. Nada aqui está errado; o que está desajustado é a
proporção entre prosa estatística e leitura administrativa.

**Localizar:** `\subsubsection*{A escolha de família move mais o número do
que os defeitos}` — vai até o fim do `\comofeito` do critério de informação,
imediatamente antes do `\newpage` de *"O que fica para a leitura do
documento"*.

### O problema

Quatro parágrafos de prosa estatística no corpo do texto, para sustentar um
número: `+30,4%` de intensidade de uso da UTI. Média condicional contra
mediana condicional, erro-padrão 41% maior, 0,0087 em pontos de logaritmo,
critério de informação em escalas diferentes — nada disso é leitura de
gestor, e o documento tem lugar próprio para isso, que é o `\comofeito`.

### Por que **não** excluir

O `+30,4%` é conclusão que o documento carrega até a conclusão (`sec17`).
Retirar a tabela faria o documento afirmar `+30,4%` **sem registrar que uma
das cinco especificações cruza o zero** — que é encontrável por qualquer
parecerista que rode `resultados_fase2/fase2_ocupacao_familias.R`. É a mesma
falha de forma que a auditoria da SFA acabou de obrigar a corrigir em vinte
lugares, invertida de sinal: sairia de *afirmar demais sobre a SFA* para
*afirmar de menos sobre a robustez da UTI*. **A tabela fica inteira.**

### A decisão: reescrever, movendo o aparato para o `\comofeito`

Corpo de quatro parágrafos para dois; todo o detalhe técnico desce. **Nenhum
número sai do documento** — mudam de lugar e de registro.

### Texto novo — título

| Atual | Novo |
|---|---|
| `A escolha de família move mais o número do que os defeitos` | `O resultado da UTI resiste à troca do modelo` |

O título atual descreve a decisão do analista; o novo descreve o que o
leitor leva. "Defeitos" além disso é jargão herdado da discussão da SFA e
não tem antecedente nesta subseção.

### Texto novo — parágrafo de abertura (substitui as linhas 396–399)

> Uma estimativa como esta depende de uma escolha técnica: qual a forma
> matemática suposta para a distribuição da ocupação. Entre todas as decisões
> desta análise, é a que mais desloca o número, mais do que as três decisões
> de amostra e limiar acima. Por isso a conta foi refeita nas
> \textbf{cinco formas plausíveis}, e as cinco estão na tabela.

### Texto novo — legenda da tabela (linhas 403–404)

> \caption{Intensidade de uso da UTI, OSS contra administração Direta,
> refeita sob cinco formas de distribuição. Efeito e intervalo em
> percentual. A tabela em si \textbf{não muda}.}

*(A tabela permanece exatamente como está: mesmas cinco linhas, mesmos
números, mesma coluna "Zero".)*

### Texto novo — parágrafo único de leitura (substitui os três parágrafos das linhas 420–442)

> As cinco apontam na \textbf{mesma direção}, e a distância entre a maior e a
> menor é de \textbf{4,5 pontos percentuais} — menos que a margem de erro de
> qualquer uma delas isolada. Em \textbf{quatro das cinco} a diferença exclui
> o zero. A quinta é a lognormal, e ela precisa ser nomeada, porque
> ``robusto em quatro de cinco'' sem dizer qual é a exceção não é robustez
> reportada. \textbf{Ela não discorda:} o efeito estimado é praticamente o
> mesmo, e o limite inferior fica a três milésimos do zero. O que muda é a
> \textbf{margem de erro}, cerca de 40\% maior — e há uma razão conhecida
> para isso. A lognormal é a única das cinco que mede o \emph{hospital
> típico} em vez da média, e numa distribuição assimétrica como esta a
> medida do típico é sempre mais atenuada e menos precisa. \textbf{A única
> especificação que não atinge significância é também a única que não está
> medindo a mesma coisa que as outras} — e ainda assim chega ao mesmo
> número.

### Texto novo — `\comofeito` (substitui o das linhas 444–449)

> \comofeito{a distância entre a lognormal e as demais é de \textbf{0,0087}
> em pontos de logaritmo, medida contra o Tweedie estimado sobre exatamente a
> mesma amostra — menor que a que separa quaisquer duas das outras famílias.
> O erro-padrão da lognormal é 41\% maior que o do Tweedie e 11\% maior que
> o da Gama: ela perde a significância \textbf{por variância, não por
> deslocamento}. A diferença de quantidade estimada é que as demais modelam
> a \textbf{média condicional} e a lognormal a \textbf{mediana condicional};
> sob assimetria à direita, o efeito sobre a mediana é sistematicamente mais
> atenuado e menos preciso que o efeito sobre a média. É \emph{estimar
> diferente}, não \emph{estimativa discordante}. Um alerta, por fim, sobre a
> coluna de ajuste que não aparece na tabela: o critério de informação da
> lognormal (2.135) é numericamente muito menor que o das demais (entre
> 21.608 e 22.695), e \textbf{isso não significa ajuste melhor} — o da
> lognormal é calculado sobre o logaritmo da resposta e o das outras sobre a
> resposta. O critério é comparável \emph{dentro} de cada escala, nunca entre
> elas.}

### O que se perde, declarado

Sai do corpo do texto a frase *"isso fortalece a leitura de robustez em vez
de qualificá-la"*. Era boa, e o parágrafo novo diz a mesma coisa de forma
mais seca (*"e ainda assim chega ao mesmo número"*). Se você quiser mantê-la,
o lugar é o fim do parágrafo de leitura, não o `\comofeito`.

### Reprodução

`resultados_fase2/fase2_ocupacao_familias.R` e
`resultados_fase2/tabelas/tabE5_sensibilidade_familias.csv`. **Nenhum número
muda; nada precisa ser reexecutado** para aplicar R1.

---
---

# R2 — `sec13`, coluna de efeito na Tabela `tab:sempandemia` (~linha 17–50)

**Data:** 30/07/2026. **Natureza:** acréscimo pedido — a tabela imprime só
coeficientes na escala interna, e o leitor não tem como converter.
**Reprodução:** `analises/auditar_efeitos_robustez.py` (script novo).

## O achado que orientou a solução

Os efeitos **não precisavam ser todos calculados**: cinco dos sete já estavam
gravados em `analises/tabelas/tab_est_robustez_sem_pandemia.csv`, colunas
`efeito_pct_completo` e `efeito_pct_sem_pandemia`, e são os que a prosa da
Seção~13 já cita (os 10,2\%/11,4\% do TMP e os 43,7\%/44,7\% da produção).
Estavam calculados e não estavam sendo impressos.

**Os dois que faltavam faltavam por um motivo, não por esquecimento.**
Mortalidade e fração de alta complexidade estão em **logito Beta**, e nessa
escala `exp(coef) - 1` **não é** variação percentual da média — é razão de
chances. O `estimacao.py` deixa as duas células vazias de propósito. Imprimir
ali um "$-20{,}0\%$" de mortalidade seria erro grosseiro: diria que as OSS
têm mortalidade 20\% menor, quando o que o modelo diz é outra coisa.

A quantidade correta para esses dois é o **efeito marginal médio em pontos
percentuais do desfecho**. Para a mortalidade ele **já existia** no projeto
(`ame_pp` em `tab_est_resumo_oss*.csv`: $-1{,}1614$ e $-1{,}1840$). Para a
alta complexidade não existia, e foi calculado.

| Modelo | Escala | Efeito, painel completo | Efeito, sem 2020 e 2021 | Origem |
|---|---|---|---|---|
| Mortalidade (geral) | logito Beta | **−1,16 p.p.** | **−1,18 p.p.** | já gravado (`ame_pp`), reproduzido |
| Fração alta complexidade | logito Beta | **−1,31 p.p.** | **−1,25 p.p.** | **número novo**, calculado agora |
| Faturamento real por saída | log | −8,3% | −8,0% | já gravado |
| Tempo de permanência | log | −10,2% | −11,4% | já gravado (é o que a prosa cita) |
| Produção (saídas) | log | +43,7% | +44,7% | já gravado (é o que a prosa cita) |
| Ocupação de internação | log | +22,7% | +22,3% | já gravado |
| Ocupação de UTI | log | +22,8% | +24,3% | já gravado |

O script reproduziu o `ame_pp` da mortalidade **exatamente** ($-1{,}1614$ e
$-1{,}1840$, batendo com o gravado), o que valida a fórmula antes de aplicá-la
ao caso novo.

## Ponto de atenção antes de aplicar

A coluna de efeito **torna visível** uma coisa que hoje está diluída na razão
entre `Coef.` e `EP`: a mortalidade tem $z = -1{,}71$ no painel completo e
$z = -2{,}01$ sem o biênio. Ou seja, **ela cruza o zero no painel inteiro e
deixa de cruzar quando a pandemia sai**. Isso não muda com R2 — já está
impresso — mas um leitor com a coluna de efeito à frente vai reparar. Vale
conferir se a Seção~11 ou 12 afirma alguma coisa sobre mortalidade que fique
em tensão com isso. **Não resolvi essa questão aqui**: é escopo de outra
seção e decisão sua.

## O código LaTeX

Substitui as linhas 17–50 inteiras (tabela e `\comofeito`).

```latex
\begin{table}[H]
\centering
\caption{Contraste OSS \emph{versus} Direta estimado no painel completo
e na amostra que exclui 2020 e 2021, nos sete modelos principais. A
coluna de efeito traduz o coeficiente para a escala do indicador; os
erros-padrão são agrupados por hospital e permanecem na escala interna
do modelo. A leitura pretendida é a comparação entre as duas metades da
tabela: quanto mais próximas, menos o resultado depende dos anos de
pandemia.}
\label{tab:sempandemia}
\small
\setlength{\tabcolsep}{4pt}
\begin{tabular}{lrrrrrr}
\toprule
& \multicolumn{3}{c}{Painel completo} & \multicolumn{3}{c}{Sem 2020 e 2021} \\
\cmidrule(lr){2-4}\cmidrule(lr){5-7}
Modelo & Coef. & EP & Efeito & Coef. & EP & Efeito \\
\midrule
\multicolumn{7}{l}{\emph{Em pontos percentuais do desfecho}} \\
Mortalidade (geral)        & $-0{,}2237$ & 0,1311 & $-1{,}16$ & $-0{,}2329$ & 0,1157 & $-1{,}18$ \\
Fração alta complexidade   & $-0{,}2044$ & 0,2348 & $-1{,}31$ & $-0{,}1937$ & 0,2333 & $-1{,}25$ \\
\addlinespace
\multicolumn{7}{l}{\emph{Em variação percentual do indicador}} \\
Faturamento real por saída & $-0{,}0866$ & 0,0948 & $-8{,}3\%$  & $-0{,}0830$ & 0,0978 & $-8{,}0\%$ \\
Tempo de permanência       & $-0{,}1080$ & 0,0468 & $-10{,}2\%$ & $-0{,}1207$ & 0,0527 & $-11{,}4\%$ \\
Produção (saídas)          & $0{,}3629$  & 0,0895 & $+43{,}7\%$ & $0{,}3694$  & 0,0892 & $+44{,}7\%$ \\
Ocupação de internação     & $0{,}2044$  & 0,0779 & $+22{,}7\%$ & $0{,}2015$  & 0,0753 & $+22{,}3\%$ \\
Ocupação de UTI            & $0{,}2058$  & 0,0747 & $+22{,}8\%$ & $0{,}2175$  & 0,0723 & $+24{,}3\%$ \\
\bottomrule
\end{tabular}
\end{table}

\comofeito{cada linha é um dos sete modelos principais. Para cada
amostra, a tabela traz o coeficiente do contraste OSS \emph{versus}
Direta, o seu erro-padrão agrupado por hospital e o \textbf{efeito
traduzido para a escala do indicador}. \textbf{As duas metades da tabela
usam unidades diferentes, e não se comparam entre si.} Nos cinco
modelos em escala logarítmica o efeito é a variação percentual,
$100 \times (e^{\,\beta} - 1)$. Nos dois primeiros, que são modelos Beta
com massa nos extremos, o coeficiente está em \textbf{logito} e a
exponencial dele seria uma razão de chances, não uma variação
percentual: por isso o efeito ali é o \textbf{efeito marginal médio em
pontos percentuais do desfecho}, isto é, de quanto a fração média se
desloca. Uma queda de $1{,}16$ p.p. de mortalidade, sobre uma média
amostral de $5{,}5\%$, é o que o coeficiente de $-0{,}2237$ significa. A
significância continua sendo lida na razão entre coeficiente e
erro-padrão, que não muda. Nenhum coeficiente muda de sinal e nenhum
muda de magnitude de forma relevante entre as duas amostras, que é o
que a figura seguinte mostra em forma gráfica.}
```

### Duas escolhas de formatação, para você reverter se quiser

1. **`\setlength{\tabcolsep}{4pt}`** foi acrescentado porque a tabela passa de
   5 para 7 colunas. Se ainda estourar a margem, troque `\small` por
   `\footnotesize`. Se quiser o espaçamento padrão de volta, apague a linha —
   mas confira a largura no PDF.
2. **As duas linhas de rótulo de escala** (`\multicolumn{7}{l}{\emph{Em
   pontos percentuais…}}`) existem porque a coluna "Efeito" mistura duas
   unidades. Se preferir sem elas, ponha a unidade em cada célula
   (`$-1{,}16$ p.p.`) — fica mais poluído, mas dispensa os rótulos. **O que
   não dá é deixar sem nenhum dos dois:** aí a tabela mente por omissão.

## Reprodução

`python analises/auditar_efeitos_robustez.py` — imprime as quatro linhas em
logito Beta, confere o `ame_pp` da mortalidade contra o gravado no projeto e
relista os cinco efeitos em escala log. O script **não escreve nenhum arquivo
de resultado** (o `_tab` do `estimacao.py` é neutralizado durante a execução),
então rodá-lo não altera nada em `analises/tabelas/`.

**Fórmula usada nos dois modelos Beta**, com $\mu$ a média condicional Beta,
$\pi_0$ a probabilidade de zero e $\pi_1$ a de um:

- mortalidade (inflação em zero): $\text{AME} = \overline{\mu(1-\mu)} \cdot
  \beta_{\text{OSS}} \cdot (1 - \bar{\pi_0}) \cdot 100$ — é literalmente a
  linha 444 do `estimacao.py`, reproduzida;
- alta complexidade (ZOIB): $\text{AME} = \overline{\mu(1-\mu)} \cdot
  \beta_{\text{OSS}} \cdot (1 - \bar{\pi_0} - \bar{\pi_1}) \cdot 100$ — mesma
  construção, com a massa em um entrando no fator de escala.

## Se aplicar R2

Acrescentar em **`analises/NUMEROS_CANONICOS.md`** os dois números novos da
alta complexidade ($-1{,}31$ e $-1{,}25$ p.p.), com a fonte
`auditar_efeitos_robustez.py`. Os outros cinco já estão canônicos. **Nenhuma
figura precisa ser regerada**: a `fig_est_05_robustez_sem_pandemia.png` já
plota os efeitos percentuais dos cinco modelos em escala log, e continua
válida.

---
---

# R3 — `sec11`, o `n.a.` da Tabela `tab:contrasteoss` (~linha 67–108)

**Data:** 30/07/2026. **Depende do R2** — mesmo número, mesma origem, mesma
reprodução (`analises/auditar_efeitos_robustez.py`). Aplicar os dois juntos.

**Localizar:** `sec11_resultados_indicadores.tex:88`, a célula `n.a.`

## Por que o `n.a.` está lá

A fração de alta complexidade é ZOIB, e o coeficiente $-0{,}2044$ está em
**logito**. Nessa escala $e^{-0{,}2044} - 1 = -18{,}5\%$ é uma **razão de
chances**, não variação percentual da média — imprimir isso ao lado do
$-8{,}3\%$ do faturamento, que é variação percentual de verdade, faria o
leitor comparar coisas diferentes. Não traduzir foi a decisão certa **na
época**.

A mortalidade escapou do `n.a.` porque tinha efeito marginal médio computado
(`estimacao.py:444`). A alta complexidade não tinha. **O `n.a.` não significa
"não se aplica": significa "não foi computado".** Agora foi.

## A correção

| Linha 88, atual | Linha 88, novo |
|---|---|
| `Fração alta complexidade     & $-0{,}2044$ & 0,2348 & $-0{,}87$ & n.a. \\` | `Fração alta complexidade     & $-0{,}2044$ & 0,2348 & $-0{,}87$ & $-1{,}31$ p.p. \\` |

O `-1,31` é o AME do painel completo calculado no R2 ($-1{,}3091$),
diretamente aplicável: mesmo modelo, mesma amostra, mesmo coeficiente.

**Ressalva de leitura, importante:** o $z$ continua $-0{,}87$. Preencher a
célula **não** transforma a alta complexidade em achado — ela segue sem
diferença estatisticamente firme, e a coluna $z$ ao lado diz isso. O ganho é
a tabela deixar de ter um buraco que parece arbitrário.

## Dois ajustes de texto que vêm junto

Sem eles a tabela fica preenchida e a legenda continua explicando por que não
está.

**(a) Legenda, ~linha 77–80.** Localizar: *"quando essa tradução faz
sentido"*.

### Texto atual
> O \textbf{erro-padrão} é
> agrupado por hospital; o \textbf{efeito} traduz o coeficiente para
> variação percentual, quando essa tradução faz sentido. Na mortalidade,
> a coluna final traz o efeito marginal médio em pontos percentuais, que
> é a forma interpretável naquele modelo.}

### Texto novo
> O \textbf{erro-padrão} é
> agrupado por hospital; o \textbf{efeito} traduz o coeficiente para a
> escala do indicador. Nos dois modelos de proporção — mortalidade e fração
> de alta complexidade — a tradução é o \textbf{efeito marginal médio em
> pontos percentuais}, que é a forma interpretável neles; nos demais, a
> variação percentual.}

**(b) `\comofeito`, ~linha 105–106.** Localizar: *"(ou, na mortalidade, para
pontos percentuais)"*.

| Atual | Novo |
|---|---|
| `\textbf{Efeito} é a tradução para variação percentual (ou, na mortalidade, para pontos percentuais).` | `\textbf{Efeito} é a tradução para variação percentual (ou, nos dois modelos de proporção, para pontos percentuais do próprio indicador).` |

## Atenção à linha da UTI, que **não** muda

`sec11` traz a ocupação de UTI com coeficiente $0{,}1769$ e efeito
$+19{,}3\%$; o R2, em `sec13`, traz $0{,}2058$ e $+22{,}8\%$. **Os dois estão
certos e não se contradizem:** a linha de `sec11` já é a reestimação pela
família Gama da Seção~15, como o próprio `\comofeito` declara, e a de `sec13`
é o modelo da bateria de robustez. Não uniformizar.
