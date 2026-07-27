# Arquivo — documentos aposentados

## `roteiro_entrevistas.tex`

**Aposentado em 27/07/2026. Não compilar, não editar, não distribuir.**

Este arquivo era um documento LaTeX autônomo (12 páginas) com a seleção
de entrevistados e o roteiro da fase qualitativa. Todo o seu conteúdo
vive hoje na **Seção 16 do `principal.tex`** e no **Apêndice B**, e é lá
que deve ser mantido.

### Por que foi aposentado

A duplicação foi a **origem direta** do defeito mais grave encontrado na
auditoria de julho de 2026: as duas cópias liam colunas diferentes da
base para o mesmo indicador. O `roteiro_entrevistas.tex` (e a Seção 16,
gerada a partir do mesmo script) lia `custo_real`, deflacionado; a Seção
7 do `principal.tex` lia `custo_saida`, nominal. Nenhuma das duas
declarava a base. O resultado é que o Conjunto Hospitalar de Sorocaba
aparecia com faturamento **19,3% maior** numa página e **12,2% menor**
noutra, a 34 páginas de distância, dentro do mesmo documento impresso.

Manter dois artefatos com o mesmo conteúdo e ciclos de correção
independentes garante que a divergência se reintroduza. Por isso o
standalone sai de circulação em vez de ser mantido em sincronia.

### Se a fase qualitativa precisar de um documento próprio

Não recupere este arquivo. Gere um novo extrato a partir da Seção 16 e
do Apêndice B do `principal.tex`, que são a fonte única. O script
`selecao_entrevistas.py` continua sendo o gerador das tabelas e figuras
de seleção.

### Nota sobre o preâmbulo

As restrições registradas no cabeçalho deste arquivo — sem babel
português, `\sloppy`, `\emergencystretch`, microtype sem expansão —
**valiam para ele, não para o `principal.tex`**. O `principal.tex`
carrega `\usepackage[brazilian]{babel}` desde sempre, com hifenização
portuguesa funcionando, e não usa `\sloppy` nem microtype. Confundir os
dois preâmbulos já custou uma rodada de trabalho; ver `PENDENCIAS.md`.
