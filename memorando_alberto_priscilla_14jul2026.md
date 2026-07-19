# Memorando — três perguntas antes de fechar a revisão de 13/07

**De:** João Eduardo Pastori Garcia (estatística do projeto)
**Para:** Alberto Tomasi; Priscilla Reinisch Perdicaris
**Data:** 14/07/2026 (atualizado após a rodada de investigação do mesmo dia)
**Assunto:** três decisões que dependem de vocês para a revisão combinada na segunda-feira seguir adiante — duas técnicas (Alberto) e uma de desenho de pesquisa (Priscilla, com Alberto em cópia)

Contexto em uma linha: a investigação dos 12 itens da reunião está concluída e a maior parte já está encaminhada; três itens, porém, não podem ser fechados por mim sozinho, porque dependem de uma informação que só o Alberto tem (perguntas 1 e 2) e de uma decisão de desenho que é da Priscilla (pergunta 3).

---

## Pergunta 1 (Alberto) — o tempo de permanência da base é truncado em ~30,5 dias?

Ao investigar o pedido de mudar a escala dos gráficos de TMP (limite de 120 dias), encontramos algo mais importante que a escala: **não existe nenhuma observação acima de 30,5 dias em todo o painel definitivo**, e a distribuição tem uma assinatura clara de teto:

- 80 hospital-ano empilhados entre 30,0 e 30,5 dias — e **zero** acima disso;
- na base bruta inteira (7.016 hospital-ano, 830 CNES, 2015–2025), o percentil 99,9 é exatamente 30,50, e o **único** estabelecimento que ultrapassa o teto em toda a década é um hospital-dia de saúde mental (tipo 62, regime próprio de AIH, que nem entra no painel).

Isso não parece variação real: parece **censura à direita** — internações longas cortadas em ~30 dias no registro.

**A pergunta:** existe regra de faturamento/registro de AIH que limite o número de diárias por autorização (na casa de 30 dias + meia diária), com internações mais longas geridas por AIH de continuidade que a nossa base atual não recompõe?

**Por que importa (não é só o gráfico):** o painel tem ~18 hospitais de perfil de longa permanência (TMP mediano acima de 20 dias — reabilitação, cuidados prolongados, duas "Casas da Criança"). Se a resposta for "sim, há teto por AIH", o TMP desses hospitais mede o teto, não a permanência — e precisaremos decidir se eles entram nos modelos de TMP com o valor censurado como está, se saem do indicador TMP especificamente (com nota), ou se tratamos a censura no modelo. A escala do gráfico a gente decide em cinco minutos depois disso.

---

## Pergunta 2 (Alberto) — ocupação de UTI: qual denominador passa a ser o padrão do projeto?

O "mistério" da reunião (modelo Barcelona mostrando ocupação de UTI maior que o nosso) **já está explicado tecnicamente** — não é mais pendência técnica, é escolha a fazer:

- O numerador é o mesmo nos dois casos (diárias-UTI do resumo SIH). A diferença está no denominador: a nossa série usa os **leitos-UTI SUS declarados ano a ano no SIH** (verificamos por reconstrução exata); a "Barcelona" usa a contagem de leitos-UTI da planilha de classificação, que é uma **fotografia fixa de 2026 aplicada retroativamente** a todos os anos.
- Como o parque de UTI SUS cresceu ao longo da década, as duas séries se cruzam: até ~2019 a versão Barcelona dá ocupação *menor*; **a partir de 2022 ela passa por cima** (2025: 80,4% vs 72,0% nas medianas). É exatamente o padrão que o Alberto observou.
- Diferença adicional de tratamento: o resumo SIH atribui ocupação **0** a hospital sem leito SUS de UTI; qualquer recálculo devolve "sem informação". Um quarto das observações está nesse caso.

**A pergunta:** qual denominador deve ser o padrão do projeto — (a) **leitos SUS anuais** (o que já usamos), (b) **leitos totais anuais** do SIH, ou (c) a **fotografia Barcelona**? E "desenvolver um modelo próprio", como se falou na reunião, significa algo além de escolher entre esses três (ex.: outra fonte de leitos, como o CNES mensal)?

Nossa leitura técnica, para constar: leitos anuais medem a ocupação do parque *do ano*; a fotografia retroativa mistura a ocupação com a expansão do parque — mas a escolha é de vocês. Como decisão de trabalho provisória, seguimos com (a), o método já em uso, registrada em `criterios_construcao_painel.md` e sujeita a esta confirmação.

---

## Pergunta 3 (Priscilla, com Alberto em cópia) — ratificação combinada: lista de exclusão de 21 hospitais (item 1.10, ampliado) + mortalidade só geral (item 1.12)

Estas duas decisões estão amarradas e precisam ser ratificadas **juntas**, com o quadro completo à vista.

**1) A lista de exclusão foi ampliada e agora tem 21 CNES — e a ampliação é parte desta ratificação, não uma decisão técnica já fechada.** A reunião de 13/07 aprovou excluir pediátricos e onco-pediátricos. Na investigação, o mesmo princípio — população estruturalmente incomparável com o hospital geral agudo — alcançou dois grupos adicionais: hospitais de nome inequívoco que os filtros formais não capturaram por falha de preenchimento na origem do SIH (um psiquiátrico e um onco-pediátrico), e onze hospitais de perfil crônico/reabilitação/ex-sanatório. A lista completa:

- **Pediátricos/onco-pediátricos (9):** Darcy Vargas, Menino Jesus, HMCA Guarulhos, Cândido Fontoura, Boldrini, GRAACC, Casa da Criança Betinho (SP), Casa da Criança de Tupã e GPACI Sorocaba (Grupo de Pesquisa e Assistência ao Câncer **Infantil** — identificado na investigação oncológica descrita mais abaixo; mortalidade mediana de 1,1%, destoante dos oncológicos adultos).
- **Psiquiátrico (1):** Instituto de Psiquiatria do HCFMUSP (especialização em branco em todos os anos — falha de preenchimento, não diferença de perfil).
- **Crônico/reabilitação/ex-sanatório (11):** Lar Espírita Maria de Nazaré (Mogi Mirim), Lar Irmã Dulce (Pirajuí), Casas André Luiz (Guarulhos), Assoc. Cruz Verde (SP), Casa de David (SP), Hospital Estadual de Reabilitação (Itu), Centro de Reabilitação Dr. Arnaldo Pezzuti (Mogi das Cruzes), Amparo ao Excepcional Ritinha (Araçatuba), CAIS Clemente Ferreira (Lins, ex-sanatório), Nestor Goulart Reis (Américo Brasiliense) e Leonor Mendes de Barros (Campos do Jordão, ex-sanatório de altitude).

O painel passaria de **314 para 293 hospitais (3.223 hospital-ano)**. Nenhum dos 21 é conversor Direta→OSS nem pertence ao grupo Privado. O princípio metodológico (por que excluir pediátricos e crônicos e manter maternidades) está redigido em `criterios_construcao_painel.md`, §2.3, aguardando esta ratificação.

> **Atualização de 15/07/2026 (após o envio deste memorando):** dois ajustes na contabilidade acima, detalhados em `criterios_construcao_painel.md` §2.3. (i) O **Instituto de Psiquiatria do HCFMUSP saiu da lista submetida a ratificação**: ele é capturado pelo critério psiquiátrico já vigente (§2.1, tipo 07 + espec. 006), do qual escapou só por falha de preenchimento da especialização — a exclusão dele independe desta ratificação. A lista a ratificar fica com **20 CNES**. (ii) Os **4 casos que estavam pendentes** (Santa Casa de S. Bernardo do Campo, Centro Hospitalar do Sistema Penitenciário, São Leopoldo Mandic e N. Sra. da Divina Providência) **foram decididos em 15/07 — os quatro são excluídos**, cada um com evidência identificável própria (retaguarda consolidada; população cativa em regime não-clínico; psiquiátrico ex-Clínica Sayão com especialização em branco; unidade para dependentes químicos/paliativos do Lar São Francisco). Com isso: **lista ETAPA F = 24 CNES + 1 pelo §2.1 = 25 saem; painel projetado 314 → 289 CNES (3.179 hospital-ano)**. Composição dos 25: 16 Filantrópicos, 6 Diretas, 2 Públicos Municipais e 1 OSS (o CHSP); nenhum switcher, nenhum Privado. Medianas sem os 25: mortalidade Direta 0,0585 vs OSS 0,0504 (a inversão descrita no item 2 abaixo se mantém); TMP Direta 5,86 vs OSS 4,80.

**2) O que a exclusão muda no grupo de comparação.** Saem 6 CNES da Direta (2 pediátricos + 4 unidades estaduais de crônicos/reabilitação), 13 do Filantrópico e 2 do Público Municipal. Na comparação simples de medianas, o efeito não é neutro: com a lista completa, a mortalidade mediana da Direta vai de **0,0475 para 0,0585**, contra 0,0493 da OSS — a Direta, que parecia *melhor* que a OSS em mortalidade, passa a parecer *pior* (inversão de sinal, maior que a já observada quando se excluíam só os 2 pediátricos). Em TMP não há inversão: a OSS já era melhor e continua (Direta 6,07 → 5,86 dias; OSS 4,85).

**3) O que a simplificação da mortalidade custa.** Nossa métrica de complexidade (`complexidade_estrutural`, Barcelona) é **fixa por hospital** — não varia ano a ano. Nos modelos com efeito fixo de hospital (os principais do projeto), variável fixa é absorvida pelo efeito fixo: ela não faz trabalho de controle nenhum *dentro* do hospital. Sem CID/DRG na base, e aposentando `mort_sem_excl` e `complexidade_pond_mort` (item 1.12), **a mortalidade fica sem nenhum ajuste de composição que varie no tempo dentro do hospital**. O único sinal temporal de composição disponível é a fração de alta complexidade (`pct_alta_complex`) — mas usá-la como controle é uma escolha de desenho, não uma correção automática: ela é *mediadora* (a gestão pode mudar o perfil atendido), então controlá-la estima o efeito **direto** da gestão, não o efeito **total**. E a vantagem de mortalidade das OSS nos modelos já é sensível à exclusão dos 5 conversores (chega a trocar de sinal sem eles) — mortalidade bruta sem ajuste temporal é o flanco mais exposto do artigo na revisão por pares.

**4) Alternativa examinada: mortalidade estratificada por complexidade (viabilidade técnica).** Calculamos a viabilidade de reportar a mortalidade separadamente para internações de alta complexidade e para as demais (`mort_alta_complex` / `mort_baixa_complex`). O cruzamento é tecnicamente possível (óbito e complexidade constam na mesma linha do SIH; exige reprocessar os 11 arquivos brutos, o que se acopla à reexecução já prevista). O problema é o denominador: a `mort_alta_complex` nasce **indefinida em 34% dos hospital-ano** (denominador zero) e com **menos de 20 casos em 53%**; 50 dos 314 hospitais nunca têm internação de alta complexidade. Um corte de denominador mínimo (ex.: ≥50 casos de alta complexidade por hospital-ano) resolve a instabilidade estatística, mas não afeta as categorias igualmente: quase todos os hospital-anos de OSS passam no corte (mediana de 281 casos), enquanto a maioria dos hospital-anos de Filantrópico (mediana de 3) e Público Municipal (mediana de 8) fica de fora. Isso significa que a comparação estratificada deixaria de ser "OSS típica vs. Filantrópico típico vs. Público Municipal típico" e passaria a ser, na prática, "OSS (quase inteira) vs. um pequeno grupo de hospitais filantrópicos e municipais atipicamente grandes" — um problema de composição da amostra, não só de tamanho de erro-padrão. Se esses hospitais grandes tiverem, por exemplo, mortalidade mais alta por concentrarem casos mais graves encaminhados de outras unidades (viés de referência), a leitura poderia atribuir à categoria de gestão uma diferença que na verdade vem do porte/perfil de referência do hospital. Recomendamos que qualquer versão estratificada reportada venha acompanhada da distribuição de quantos hospitais de cada categoria sobrevivem ao corte de denominador, para que a leitura não seja tomada como representativa da categoria inteira.

**A pergunta objetiva (Priscilla):** você aprova (a) a exclusão dos **21 hospitais** listados acima — incluindo a ampliação para o grupo crônico/reabilitação/ex-sanatório — e (b) o uso apenas de `mort_all` como indicador de mortalidade, **sabendo** que a combinação deixa o modelo de mortalidade sem ajuste de composição intra-hospitalar que varie no tempo, que a comparação simples da Direta com a OSS inverte de sinal com a nova amostra, e que a vantagem de mortalidade das OSS já é sensível à exclusão dos switchers? Ou prefere uma das alternativas: `pct_alta_complex` como controle explícito nos modelos de mortalidade (assumindo a interpretação de efeito direto, registrada no documento metodológico), e/ou a versão estratificada como análise **descritiva complementar** com corte de denominador mínimo e a distribuição de sobreviventes ao corte sempre reportada? As opções não são mutuamente excludentes — podem coexistir com papéis distintos.

**Ainda neste bloco, para o Alberto:** três casos ficaram fora da lista de 21 por não terem sinal conclusivo, e precisamos da sua leitura — **São Leopoldo Mandic (Araras, 2082470)**, **N. Sra. da Divina Providência (Jaci, 2081466)** e o **Centro Hospitalar do Sistema Penitenciário (SP, 3001466)** — devem entrar no mesmo tratamento (perfil crônico/incomparável) ou são casos à parte? Sobre o penitenciário, registramos no dossiê que a população é cativa (carcerária), com tempo de permanência e altas influenciados por razões administrativas alheias ao quadro clínico — perfil distinto de qualquer critério já discutido.

> **Nota de 15/07/2026:** estes casos (incluindo a Santa Casa de S. Bernardo do Campo) foram **decididos em 15/07 de forma independente desta consulta**, com a metodologia já documentada (trajetória interna ano a ano + verificação externa com fonte e data de acesso; `criterios_construcao_painel.md` §2.3) — os quatro saem do painel. A pergunta acima **segue em aberta** do seu ângulo, Alberto: ela foi enviada antes desta decisão e, se a sua resposta trouxer informação nova (por exemplo, algo que contradiga o perfil identificado), a decisão é revisada. Não é mais, porém, um bloqueio para a ETAPA F.

---

## Achado para o Alberto — mortalidade dos hospitais oncológicos (resposta à ação registrada na reunião; não é pergunta nova)

Na reunião de 13/07 ficou como ação sua analisar a mortalidade geral dos hospitais oncológicos, que parecia mais baixa do que o esperado. Rodamos a investigação do nosso lado para cruzar com o que você trouxer, e o resultado **inverte a premissa**: os oncológicos **adultos** do painel (A.C. Camargo, Pio XII/Barretos, Amaral Carvalho, ICESP, IBCC, Arnaldo Vieira de Carvalho, Santo Antônio/Santos, Hospital de Câncer de SBC, Pio XII/SJC) têm mortalidade mediana de **8,8%** — bem **acima** do Filantrópico não-oncológico (5,4%) e do painel (5,4%) — e a diferença **se mantém dentro da mesma faixa Barcelona** (faixa 3: 9,2% contra 5,1%; faixa 4: 6,8% contra 5,8%). A hipótese de diluição por ciclos curtos de quimio/radioterapia não se sustenta nos adultos: o TMP deles é *maior* que o dos pares (4,9 contra 4,1 dias), não menor. **A mortalidade "surpreendentemente baixa" é um fenômeno dos onco-pediátricos** (GPACI 1,1%; Boldrini e GRAACC, já na lista de exclusão) — coerente com a sobrevida alta do câncer infantil e com internações longas de tratamento — e foi isso que motivou a inclusão do GPACI na lista da pergunta 3. Fica registrada, como hipótese não testável com a base atual, a triagem/encaminhamento (centros de excelência podem receber casos com melhor prognóstico ou, ao contrário, concentrar os mais graves — a base não distingue).

---

## Para registro (não são perguntas)

- **Privado com ocupação de UTI de 3,5%** — explicado, não é erro: Leforte tem 30 leitos SUS de UTI com 595 diárias medianas/ano (5,4%), a Unimed Sorocaba tem 4 leitos (2,2%) e o HU-UFSCar não declara leito de UTI (0%). Produção SUS residual; o grupo (n=3) segue com ressalva de não-interpretação em qualquer tabela.
- **Fator IPCA do pipeline conferido:** o fator acumulado 2015→2025 usado no código (1,6479) bate com o cálculo independente encadeando a série oficial de 2016 a 2025 (1,647877). Ressalva única: conferir o fechamento de 2025 (4,26% dez/dez) contra o SIDRA, por ser publicação recente.

João

---

## Adendo — 15/07/2026 (fechamento das três perguntas)

As três perguntas deste memorando foram **respondidas diretamente por João em 15/07/2026**, para destravar a reexecução única do pipeline. Registro das decisões:

- **Pergunta 1 (TMP):** **não há teto de 30,5 dias** nos dados/critérios do estudo como regra do projeto. O empilhamento de 80 hospital-ano perto de ~30 dias fica registrado como **achado descritivo**, não como censura a aplicar — nenhum tratamento de censura, truncamento ou modelo censurado foi introduzido para o TMP. A pergunta técnica ao Alberto (regra de faturamento/diárias por AIH) permanece de interesse para interpretação, mas deixou de ser bloqueio.
- **Pergunta 2 (ocupação de UTI):** mantido o denominador de **leitos-UTI SUS anuais** declarados no SIH — decisão **confirmatória** da prática já vigente (alternativas "leitos totais" e "fotografia Barcelona 2026" descartadas como padrão do projeto).
- **Pergunta 3 (exclusão + mortalidade):** a lista de 20 CNES foi **ratificada por João** — **mudança de procedimento** em relação ao desenho original desta pergunta, que previa ratificação pela Priscilla. A ETAPA F foi aplicada com 25 CNES (20 ratificados + 4 decididos em 15/07, nota acima + Inst. de Psiquiatria pelo §2.1). A **simplificação da mortalidade não foi aplicada**: reversão à definição **original** — `mort_all` e `mort_sem_excl` seguem como indicadores paralelos, `complexidade_pond_mort` não foi aposentada e o cruzamento óbito×complexidade (item 1.13) não foi implementado (código preparatório desativado por flag). A salvaguarda de circularidade permanece inalterada.

**O que segue em aberto com vocês:** (i) Alberto — a leitura sobre a regra de diárias por AIH (P1) e sobre os 4 casos decididos em 15/07 (revisáveis se houver informação nova); (ii) Priscilla — a **forma funcional de `complexidade_pond_mort`**, que continua pendente de ratificação (questão separada, não decidida neste fechamento).

João
