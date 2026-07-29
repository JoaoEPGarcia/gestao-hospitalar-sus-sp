# `uti_parte1` removida de `tabB_modelos_hierarquicos.csv`

**Removida em:** 28/07/2026, na Etapa 5.
**Motivo:** separação. Não é estimativa.

## O que estava publicado

```
modelo,coef,ep,lo,hi,efeito_pct
uti_parte1,-58.958032,,,,
```

Coeficiente de −58,96 no logito com **erro-padrão vazio**. Um logito de −58,96
corresponde a uma probabilidade da ordem de 10⁻²⁶: o otimizador foi para o
infinito porque o preditor separa perfeitamente os desfechos. O erro-padrão
ausente é a assinatura disso — sem máximo interior, não há curvatura para
inverter.

## Por que sai da tabela e não fica com tarja

É da **mesma classe do termo `d_oss` da SFA**, já documentado no projeto como
não citável por degeneração. Recebe o mesmo tratamento, pela mesma razão: um
número degenerado numa tabela publicada é lido como estimativa por quem não
leu a nota de rodapé, e a tarja não impede a citação — só a desculpa depois.
A documentação preserva o valor; a tabela não o exibe.

Isto **não é decisão de estilo editorial**. A tabela afirma quantidades
estimadas, e esta não foi estimada.

## A pergunta não é estimável com estes dados

A quantidade que `uti_parte1` tentava medir era "o hospital tem UTI ativa?",
mas o modelo original a rodava sobre o **painel inteiro**, onde ela confunde
duas coisas: *ter UTI cadastrada* e *usar a UTI que tem*. Como 688 das 3.179
observações não têm UTI SUS cadastrada, a categoria de gestão prediz o
desfecho quase perfeitamente e o logito diverge.

A versão **corrigida** da mesma pergunta — "opera, **dado que** tem
capacidade?", rodada sobre a subamostra de capacidade (`uti_sus > 0`) — é
conceitualmente a pergunta certa, e **também não converge**: na subamostra de
capacidade sobram apenas 7 observações com desfecho zero. Está reportada como
falha explícita em `tabE5_ocupacao_antes_depois.csv`.

Ou seja: a pergunta não é estimável nem na forma defeituosa nem na corrigida.
O que muda é que agora se sabe **por quê**.

## Atenção a quem reexecutar

`fase2_hierarquico.R` **não foi alterado** — os resultados publicados continuam
reproduzíveis a partir do arquivo que os produziu. Consequência: reexecutar
`fase2_hierarquico.R` regenera `tabB_modelos_hierarquicos.csv` **com a linha
`uti_parte1` de volta**. Quem reexecutar precisa remover a linha de novo e
manter este arquivo ao lado.

Ver `RESTRICOES_SEGMENTACAO.md`, R10.
