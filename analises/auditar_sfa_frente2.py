"""
Frente 2 da auditoria editorial --- as medidas que a frente exige.

Nao altera nada. Reporta.

1. O DEA ordena o Publico Municipal acima da Direta? Em qual escore, em qual
   estatistica, e em qual estrato.
2. A violacao de monotonicidade da Translog e uniforme entre categorias ou se
   concentra em alguma?
3. Onde estao, no .tex, o coeficiente de -5,454 e a violacao de 94,9%, e a
   que distancia um do outro.

Regra 7 do projeto: nenhum numero entra em relatorio sem ser reproduzido
rodando. Este script e a reproducao.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
F2 = RAIZ / "resultados_fase2"
SEC = RAIZ / "analises" / "latex" / "secoes"

ESCORES = ["te_bcc", "te_bcc_vc", "te_ccr", "ef_escala"]
PAR = ["Público Municipal", "Direta"]


def cabecalho(t):
    print("\n" + "=" * 74)
    print(t)
    print("=" * 74)


def confronto(df, rot, escores=ESCORES):
    """Imprime o par PM x Direta em media e mediana, para cada escore."""
    if not set(PAR) <= set(df["categoria"].unique()):
        print(f"  [{rot}] uma das duas categorias nao esta presente")
        return
    print(f"\n  {rot}")
    print(f"    {'escore':<12} {'estat':<9} {'Pub.Mun.':>9} {'Direta':>9} "
          f"{'dif':>9}  veredito")
    for esc in escores:
        if esc not in df.columns:
            continue
        for est in ("mean", "median"):
            g = df.groupby("categoria")[esc].agg(est)
            pm, dr = g.get(PAR[0]), g.get(PAR[1])
            if pd.isna(pm) or pd.isna(dr):
                continue
            v = "PM ACIMA" if pm > dr else "PM ABAIXO"
            print(f"    {esc:<12} {est:<9} {pm:>9.4f} {dr:>9.4f} "
                  f"{pm - dr:>+9.4f}  {v}")


# ----------------------------------------------------------------------
cabecalho("1. O DEA ordena o Publico Municipal acima da Direta?")

dea = pd.read_csv(F2 / "dea" / "dea_escores_principal.csv")
print(f"dea_escores_principal.csv: {len(dea)} obs, "
      f"{dea['cnes'].nunique()} CNES, anos {dea['ano'].min()}-{dea['ano'].max()}")
print("\nordenamento completo por categoria (media de cada escore):")
print(dea.groupby("categoria")[ESCORES].mean().round(4)
      .sort_values("te_bcc_vc", ascending=False).to_string())

confronto(dea, "painel inteiro, todos os estratos")

# --- por estrato, que e onde a comparacao e honesta ---
seg = pd.read_csv(RAIZ / "analises" / "painel_segmentado.csv")
col_e = next((c for c in seg.columns if "estrato" in c.lower()), None)
print(f"\ncoluna de estrato em painel_segmentado.csv: {col_e!r}")
if col_e:
    mapa = seg.drop_duplicates("cnes").set_index("cnes")[col_e]
    dea["estrato"] = dea["cnes"].map(mapa)
    print("obs do DEA por estrato:")
    print(dea["estrato"].value_counts(dropna=False).to_string())
    for e in sorted(x for x in dea["estrato"].dropna().unique()):
        confronto(dea[dea["estrato"] == e], f"estrato {e}")

# --- ano a ano, no escore corrigido de vies ---
cabecalho("1b. Ano a ano, no escore corrigido de vies (te_bcc_vc)")
tabE = pd.read_csv(F2 / "tabelas" / "tabE_eficiencia_categoria_ano.csv")
piv = tabE.pivot(index="ano", columns="categoria", values="te_bcc_vc")
if set(PAR) <= set(piv.columns):
    piv = piv[PAR].copy()
    piv["dif"] = piv[PAR[0]] - piv[PAR[1]]
    piv["PM acima?"] = piv["dif"] > 0
    print(piv.round(4).to_string())
    n = int(piv["PM acima?"].sum())
    print(f"\n  o Publico Municipal fica acima da Direta em {n} dos "
          f"{len(piv)} anos (te_bcc_vc)")

print("\nmesma contagem, escore a escore:")
for esc in ESCORES:
    p = tabE.pivot(index="ano", columns="categoria", values=esc)
    if set(PAR) <= set(p.columns):
        n = int((p[PAR[0]] > p[PAR[1]]).sum())
        print(f"  {esc:<12}: PM acima em {n}/{len(p)} anos")

# ----------------------------------------------------------------------
cabecalho("2. Monotonicidade: os coeficientes da Translog estao em .rds")
for p in sorted((F2 / "sfa").glob("*")):
    print(f"  {p.name}  ({p.stat().st_size} bytes)")
print("\nA verificacao de monotonicidade precisa dos coeficientes do")
print("modS_translog.rds e do painel de insumos --- exige R. Ver a secao 2")
print("do relatorio: se o Rscript nao rodar, o 94,9% NAO e reproduzido aqui")
print("e a pergunta de concentracao por categoria fica sem resposta.")

# ----------------------------------------------------------------------
cabecalho("3. Distancia no .tex entre o coeficiente e a violacao")

linhas = (SEC / "sec15_fase2_eficiencia.tex").read_text(
    encoding="utf-8").splitlines()


def achar(padrao, rot):
    hits = [(i + 1, l.strip()) for i, l in enumerate(linhas)
            if re.search(padrao, l)]
    print(f"\n{rot}: {len(hits)} ocorrencia(s)")
    for n, l in hits:
        print(f"  linha {n}: {l[:105]}")
    return [n for n, _ in hits]


l_coef = achar(r"5\{,\}454|5,454", "coeficiente -5,454 (Publico Municipal)")
l_mono = achar(r"94\{,\}9|94,9", "violacao de monotonicidade em 94,9%")
# a regex antiga era so `nao e citavel` e devolvia zero depois que a correcao
# de 29/07/2026 passou a escrever "nenhum coeficiente ... e citavel", que e a
# forma mais forte. Instrumento que nao enxerga a correcao mede o proprio
# vocabulario, nao o documento.
achar(r"n[aã]o (?:é|e|s[aã]o) cit[aá]ve|nenhum[a]?\s+\w+(?:\s+\w+){0,6}\s+"
      r"[eé]\s+cit[aá]ve|nem\s+.{0,40}cit[aá]ve",
      "declaracao de nao-citabilidade (qualquer forma)")

if l_coef and l_mono:
    d = min(abs(a - b) for a in l_coef for b in l_mono)
    print(f"\n  DISTANCIA coeficiente <-> violacao: {d} linhas de fonte")

marcos = [(i + 1, l.strip()) for i, l in enumerate(linhas)
          if re.match(r"\\(sub)*section|\\begin\{table\}|\\end\{table\}", l)]
print("\nmarcos estruturais, para saber se estao na mesma unidade de texto:")
for n, l in marcos:
    print(f"  {n}: {l[:75]}")
