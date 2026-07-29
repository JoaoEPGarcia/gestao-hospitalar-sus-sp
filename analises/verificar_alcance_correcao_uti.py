# verificar_alcance_correcao_uti.py
# BLOCO A do fechamento — levantamento do alcance ANTES de propor texto.
#
# A correção da Etapa 1 (commit 1c5b35a) criou `ocupacao_uti_valida`, definida
# só onde `uti_sus > 0`. A coluna antiga `ocupacao_uti` traz ZERO ESTRUTURAL
# nas 688 observações sem UTI SUS, que deveriam ser não-aplicável.
#
# Este script mede, célula a célula, o que muda nas tabelas JÁ PUBLICADAS do
# documento se o domínio for corrigido. Ele NÃO altera nada: só produz o
# "antes e depois" para a decisão.

from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent

# ACHADO DE PROCEDIMENTO: `ocupacao_uti_valida` NÃO existe em
# `painel_definitivo.csv` — só em `painel_segmentado.csv`. Ou seja, a base que
# `estimacao.py` e `analise_exploratoria.py` leem não carrega a coluna
# corrigida, e por isso nenhuma tabela publicada pôde tê-la usado.
p = pd.read_csv(RAIZ / "painel_segmentado.csv")
definitivo = pd.read_csv(RAIZ / "painel_definitivo.csv")
assert len(p) == len(definitivo), "os dois painéis divergem em nº de linhas"
assert "ocupacao_uti_valida" not in definitivo.columns, \
    "painel_definitivo passou a ter a coluna corrigida — reveja este script"
print(f"[fonte] painel_segmentado.csv, {len(p)} obs "
      f"(painel_definitivo.csv tem as mesmas {len(definitivo)}, "
      f"sem a coluna corrigida)")

antiga = p["ocupacao_uti"]
nova = p["ocupacao_uti_valida"]

print("=" * 84)
print("DOMÍNIO")
print("=" * 84)
print(f"observações no painel .................. {len(p)}")
print(f"com uti_sus = 0 (zero estrutural) ...... {int((p['uti_sus'] == 0).sum())}")
print(f"não-faltantes em ocupacao_uti .......... {int(antiga.notna().sum())}")
print(f"não-faltantes em ocupacao_uti_valida ... {int(nova.notna().sum())}")

print()
print("=" * 84)
print("TABELA tab:univariada, Seção 2 — linha 'Ocupação UTI (%)'")
print("=" * 84)


def desc(s):
    s = s.dropna()
    return {
        "Média": s.mean(), "DP": s.std(), "Mediana": s.median(),
        "p90": s.quantile(0.90), "Máximo": s.max(),
        "Assimetria": s.skew(),
        "Zeros": 100.0 * (s == 0).mean(),
    }


a, b = desc(antiga), desc(nova)
PUB = {"Média": 59.84, "DP": 44.89, "Mediana": 69.38, "p90": 96.67,
       "Máximo": 875.21, "Assimetria": 2.95, "Zeros": 21.9}
print(f"{'estatística':<13}{'publicado':>11}{'recalc. antigo':>16}"
      f"{'CORRIGIDO':>12}{'muda?':>8}")
print("-" * 84)
for k in PUB:
    muda = "SIM" if abs(a[k] - b[k]) > 0.05 else "não"
    print(f"{k:<13}{PUB[k]:>11.2f}{a[k]:>16.2f}{b[k]:>12.2f}{muda:>8}")

print()
print("=" * 84)
print("TABELA tab:categorias, Seção 4 — coluna 'Ocup. UTI (%)' (MEDIANAS)")
print("=" * 84)

ORDEM = ["Direta", "OSS", "Público Municipal", "Filantrópico", "Privado"]
med_a = p.groupby("modelo_gestao_proxy")["ocupacao_uti"].median()
med_b = p.groupby("modelo_gestao_proxy")["ocupacao_uti_valida"].median()
mea_a = p.groupby("modelo_gestao_proxy")["ocupacao_uti"].mean()
mea_b = p.groupby("modelo_gestao_proxy")["ocupacao_uti_valida"].mean()

print(f"{'categoria':<20}{'mediana pub.':>13}{'mediana corr.':>15}"
      f"{'média pub.':>12}{'média corr.':>13}")
print("-" * 84)
for c in ORDEM:
    print(f"{c:<20}{med_a[c]:>13.1f}{med_b[c]:>15.1f}"
          f"{mea_a[c]:>12.2f}{mea_b[c]:>13.2f}")

print()
print("ORDENAMENTO entre as quatro categorias públicas e filantrópicas")
print("(o Privado nunca é interpretado):")
quatro = [c for c in ORDEM if c != "Privado"]
for rot, sa, sb in (("MEDIANA", med_a, med_b), ("MÉDIA", mea_a, mea_b)):
    oa = sorted(quatro, key=lambda c: -sa[c])
    ob = sorted(quatro, key=lambda c: -sb[c])
    print(f"  {rot:<8} publicado: {' > '.join(oa)}")
    print(f"  {'':<8} CORRIGIDO: {' > '.join(ob)}")
    pa = oa.index("Filantrópico") + 1
    pb = ob.index("Filantrópico") + 1
    print(f"  {'':<8} Filantrópico: {pa}º -> {pb}º de 4")
    print()

print("=" * 84)
print("O QUE A ESTIMAÇÃO USA — estimacao.py")
print("=" * 84)
# o modelo em duas partes de estimacao.py condiciona em ocupacao_uti > 0
pos_antigo = int((p["ocupacao_uti"] > 0).sum())
cap = int((p["uti_sus"] > 0).sum())
cap_sem_uso = int(((p["uti_sus"] > 0) & (p["diarias_uti"] == 0)).sum())
print(f"observações com ocupacao_uti > 0 (parte positiva publicada) . {pos_antigo}")
print(f"observações com uti_sus > 0 (capacidade, domínio correto) ... {cap}")
print(f"diferença: uti_sus > 0 MAS diarias_uti = 0 .................. {cap_sem_uso}")
print()
print("Leitura: a PARTE POSITIVA do modelo publicado já exclui os zeros")
print("estruturais, porque condicionar em ocupacao_uti > 0 os remove junto.")
print("Ela não está contaminada pelo defeito da Etapa 1 — está sujeita ao")
print("defeito 2 de R8, que é condicionar no desfecho e perder as")
print(f"{cap_sem_uso} observações com UTI habilitada e nenhuma diária.")
print()
print("Já a PRIMEIRA parte (uti_ativa = ocupacao_uti > 0) confunde as duas")
print("coisas: hospital SEM UTI e hospital COM UTI e sem uso entram ambos")
print("como zero. É essa parte que a correção do domínio afeta.")

print()
print("=" * 84)
print("OUTRAS CÉLULAS PUBLICADAS QUE DEPENDEM DA COLUNA ANTIGA")
print("=" * 84)
sub = p[["mort_all", "ocupacao_uti", "ocupacao_uti_valida"]].dropna(
    subset=["mort_all"])
r_a = sub[["mort_all", "ocupacao_uti"]].dropna().corr(method="spearman").iloc[0, 1]
r_b = sub[["mort_all", "ocupacao_uti_valida"]].dropna().corr(
    method="spearman").iloc[0, 1]
print(f"Seção 8, correlação mortalidade x ocupação de UTI")
print(f"   publicado 0,36 | recalculado antigo {r_a:.2f} | CORRIGIDO {r_b:.2f}")


def within_pct(col):
    d = p[["cnes", col]].dropna()
    g = d.groupby("cnes")[col]
    dentro = float(((d[col] - g.transform("mean")) ** 2).sum())
    total = float(((d[col] - d[col].mean()) ** 2).sum())
    return 100.0 * dentro / total


print(f"Seção 8, variação within da ocupação de UTI")
print(f"   publicado 38,2% | recalculado antigo {within_pct('ocupacao_uti'):.1f}%"
      f" | CORRIGIDO {within_pct('ocupacao_uti_valida'):.1f}%")
