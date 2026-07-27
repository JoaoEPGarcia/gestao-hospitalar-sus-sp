# -*- coding: utf-8 -*-
"""
ETAPA 1 — Correção do domínio de definição da ocupação de UTI.

CORREÇÃO DE BUG, NÃO ESCOLHA METODOLÓGICA.

O problema
----------
`ocupacao_uti` vale 0 em toda observação com `uti_sus == 0`. Isso não é
ocupação baixa: é indicador não-aplicável. Um hospital sem leito de UTI
habilitado ao SUS não tem taxa de ocupação de UTI SUS — tem denominador
zero, e o zero que aparece na base é artefato de construção da planilha
de origem, não medida.

O viés é diferencial por categoria de gestão: o Filantrópico concentra
os hospitais sem UTI SUS, de modo que a média não-corrigida rebaixa
justamente uma categoria e preserva as outras, invertendo o ordenamento
entre elas.

`ocupacao_internacao` NÃO tem este problema — `leitos_sus` nunca é zero
no painel (verificado: 0 observações). Não se mexe nela.

O contrato deste script
-----------------------
1. `painel_definitivo.csv` é lido e nunca escrito.
2. `ocupacao_uti` NÃO é sobrescrita. A correção entra como coluna nova,
   `ocupacao_uti_valida`, para que o diff fique auditável linha a linha.
3. Nenhuma observação é removida: o painel de saída tem exatamente as
   mesmas 3.179 linhas do de entrada.

Saídas
------
  analises/tabelas/tabSEG_00_impacto_correcao_uti.csv
  analises/figuras_segmentacao/figSEG_00_ocupacao_uti_antes_depois.png
  analises/painel_definitivo_corrigido.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent
PAINEL_IN = RAIZ / "analises" / "painel_definitivo.csv"
PAINEL_OUT = RAIZ / "analises" / "painel_definitivo_corrigido.csv"
PASTA_TAB = RAIZ / "analises" / "tabelas"
PASTA_FIG = RAIZ / "analises" / "figuras_segmentacao"

# Denominador da ocupação de UTI: uti_sus (leitos habilitados ao SUS),
# não uti_total. Verificado empiricamente pelo bloco VERIFICAÇÃO 0.
DIAS_ANO = 365

# Ordem e paleta idênticas às de analise_exploratoria.py, para que as
# figuras SEG possam conviver com as do documento sem ruído visual.
CATEGORIAS = ["Direta", "OSS", "Público Municipal", "Filantrópico", "Privado"]
CORES_CAT = {
    "Direta":            "#0d366b",
    "OSS":               "#0f9b8e",
    "Público Municipal": "#5598e7",
    "Filantrópico":      "#6a51c7",
    "Privado":           "#898781",
}
CORES_CAT_CLARAS = {
    "Direta":            "#9ec5f4",
    "OSS":               "#8fd9cf",
    "Público Municipal": "#c4dcf9",
    "Filantrópico":      "#cfc4f2",
    "Privado":           "#d6d5d1",
}
COR_EVENTO = "#52514e"
COR_GRADE  = "#e1e0d9"
COR_EIXO   = "#c3c2b7"
COR_MUTED  = "#898781"

plt.rcParams.update({
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": COR_EIXO, "axes.labelcolor": "#0b0b0b",
    "axes.grid": True, "grid.color": COR_GRADE, "grid.linewidth": .6,
    "xtick.color": COR_MUTED, "ytick.color": COR_MUTED,
    "font.size": 11.5, "axes.titlesize": 11.5, "figure.titlesize": 11,
})


def _parar(motivo: str) -> None:
    """Aborta sem escrever nada. A realidade do repositório contrariou o
    que esta tarefa pressupõe, e reconciliar por conta própria seria pior
    do que parar."""
    print("\n" + "!" * 78)
    print("PARAR E REPORTAR")
    print(motivo)
    print("Nenhum arquivo foi escrito.")
    print("!" * 78)
    sys.exit(1)


# ---------------------------------------------------------------------------
# LEITURA
# ---------------------------------------------------------------------------
print("=" * 78)
print("ETAPA 1 — domínio de definição da ocupação de UTI")
print("=" * 78)

df = pd.read_csv(PAINEL_IN)
print(f"\nlido: {PAINEL_IN.relative_to(RAIZ)}")
print(f"  {len(df):,} observações | {df['cnes'].nunique():,} CNES | "
      f"{df['ano'].min()}–{df['ano'].max()}")

N_IN = len(df)
COLS_IN = list(df.columns)
if not {"uti_sus", "diarias_uti", "ocupacao_uti", "modelo_gestao_proxy"}.issubset(df.columns):
    _parar("Colunas obrigatórias ausentes no painel definitivo.")


# ---------------------------------------------------------------------------
# VERIFICAÇÃO 0 — a fórmula da ocupação é mesmo diarias_uti / (uti_sus × 365)?
# ---------------------------------------------------------------------------
# O prompt afirma que o denominador é `uti_sus`, verificado empiricamente.
# Reconferir aqui é barato e evita que a correção seja aplicada sobre uma
# premissa que a base já não sustenta — em particular, se 2025 fosse meia
# competência, o denominador anual de 365 dias falharia só naquele ano.
print("\n" + "-" * 78)
print("VERIFICAÇÃO 0 — fórmula da ocupação de UTI")
print("-" * 78)

com_uti = df["uti_sus"] > 0
recalc = 100 * df.loc[com_uti, "diarias_uti"] / (df.loc[com_uti, "uti_sus"] * DIAS_ANO)
obs = df.loc[com_uti, "ocupacao_uti"]
dif = (recalc - obs).abs()

TOL = 0.05  # ponto percentual; a planilha de origem arredonda
adere = (dif <= TOL)
print(f"observações com uti_sus > 0 ......... {com_uti.sum():,}")
print(f"aderência à fórmula (|dif| <= {TOL} pp) . {100 * adere.mean():.2f}%")
print(f"maior desvio absoluto .............. {dif.max():.4f} pp")

print("\naderência por ano:")
por_ano = (pd.DataFrame({"ano": df.loc[com_uti, "ano"], "adere": adere})
             .groupby("ano")["adere"].agg(["mean", "size"]))
for ano, lin in por_ano.iterrows():
    print(f"  {ano}: {100 * lin['mean']:6.2f}%  (n={int(lin['size'])})")

if adere.mean() < 0.99:
    _parar(
        "A identidade ocupacao_uti = 100*diarias_uti/(uti_sus*365) não se\n"
        "sustenta na base atual. O denominador da ocupação mudou, ou algum\n"
        "ano não é competência cheia. A correção do domínio pressupõe esta\n"
        "fórmula e não pode ser aplicada às cegas."
    )
print("\n>>> fórmula confirmada: denominador é uti_sus × 365.")


# ---------------------------------------------------------------------------
# CORREÇÃO
# ---------------------------------------------------------------------------
df["tem_uti_sus"] = df["uti_sus"] > 0
df["ocupacao_uti_valida"] = df["ocupacao_uti"].where(df["tem_uti_sus"])

n_sem = int((~df["tem_uti_sus"]).sum())
# Zeros legítimos: hospital tem leito de UTI SUS habilitado e não registrou
# nenhuma diária no ano. Continuam valendo 0 — o indicador é aplicável.
n_zero_legitimo = int(((df["ocupacao_uti"] == 0) & df["tem_uti_sus"]).sum())

print("\n" + "-" * 78)
print("CORREÇÃO APLICADA")
print("-" * 78)
print(f"obs sem UTI SUS (viram NaN) ................. {n_sem:,} "
      f"({100 * n_sem / len(df):.1f}%)")
print(f"zeros legítimos preservados (uti_sus > 0) ... {n_zero_legitimo:,}")
print(f"obs com ocupacao_uti_valida definida ........ "
      f"{int(df['ocupacao_uti_valida'].notna().sum()):,}")

n_cnes_sem = df.loc[~df["tem_uti_sus"], "cnes"].nunique()
n_cnes_sempre_sem = (df.groupby("cnes")["tem_uti_sus"].sum() == 0).sum()
print(f"CNES que em algum ano não têm UTI SUS ....... {n_cnes_sem:,}")
print(f"CNES sem UTI SUS em nenhum ano do período ... {n_cnes_sempre_sem:,}")


# ---------------------------------------------------------------------------
# tabSEG_00 — impacto da correção
# ---------------------------------------------------------------------------
def _linha(bloco: pd.DataFrame, rotulo: str) -> dict:
    n_obs = len(bloco)
    n_sem = int((~bloco["tem_uti_sus"]).sum())
    todos = bloco["ocupacao_uti"]
    valida = bloco["ocupacao_uti_valida"].dropna()
    media_todos = todos.mean()
    media_valida = valida.mean() if len(valida) else np.nan
    return {
        "modelo_gestao_proxy": rotulo,
        "n_obs": n_obs,
        "n_obs_sem_uti_sus": n_sem,
        "pct_sem_uti_sus": round(100 * n_sem / n_obs, 2),
        "ocup_media_todos": round(media_todos, 2),
        "ocup_media_valida": round(media_valida, 2),
        "ocup_mediana_todos": round(todos.median(), 2),
        "ocup_mediana_valida": round(valida.median(), 2) if len(valida) else np.nan,
        # negativo = a média não-corrigida SUBESTIMA a ocupação verdadeira
        "vies_pp": round(media_todos - media_valida, 2),
    }


linhas = [_linha(df[df["modelo_gestao_proxy"] == cat], cat)
          for cat in CATEGORIAS if (df["modelo_gestao_proxy"] == cat).any()]
linhas.append(_linha(df, "TOTAL"))
tab00 = pd.DataFrame(linhas)

PASTA_TAB.mkdir(parents=True, exist_ok=True)
cam_tab = PASTA_TAB / "tabSEG_00_impacto_correcao_uti.csv"
tab00.to_csv(cam_tab, index=False, encoding="utf-8-sig")

print("\n" + "=" * 78)
print("tabSEG_00_impacto_correcao_uti")
print("=" * 78)
print(tab00.to_string(index=False))
print("\nvies_pp = ocup_media_todos - ocup_media_valida")
print("  negativo => a média sem correção subestima a ocupação verdadeira")

# Ordenamento entre categorias antes e depois: é este o achado que muda.
print("\n" + "-" * 78)
print("ORDENAMENTO ENTRE CATEGORIAS (média)")
print("-" * 78)
so_cat = tab00[tab00["modelo_gestao_proxy"] != "TOTAL"]
antes = so_cat.sort_values("ocup_media_todos", ascending=False)["modelo_gestao_proxy"].tolist()
depois = so_cat.sort_values("ocup_media_valida", ascending=False)["modelo_gestao_proxy"].tolist()
print(f"  antes  : {' > '.join(antes)}")
print(f"  depois : {' > '.join(depois)}")
print(f"  o ordenamento {'MUDA' if antes != depois else 'não muda'} com a correção.")


# ---------------------------------------------------------------------------
# figSEG_00 — barras pareadas
# ---------------------------------------------------------------------------
cats = so_cat["modelo_gestao_proxy"].tolist()
x = np.arange(len(cats))
larg = 0.38

fig, eixos = plt.subplots(1, 2, figsize=(12.5, 5.4))
for ax, (col_a, col_d, titulo) in zip(
    eixos,
    [("ocup_media_todos", "ocup_media_valida", "Média"),
     ("ocup_mediana_todos", "ocup_mediana_valida", "Mediana")],
):
    va = so_cat[col_a].to_numpy(float)
    vd = so_cat[col_d].to_numpy(float)
    ax.bar(x - larg / 2, va, larg, label="sem correção (zeros incluídos)",
           color=[CORES_CAT_CLARAS[c] for c in cats], edgecolor="white", lw=.6)
    ax.bar(x + larg / 2, vd, larg, label="corrigido (uti_sus > 0)",
           color=[CORES_CAT[c] for c in cats], edgecolor="white", lw=.6)
    for xi, v in zip(x - larg / 2, va):
        ax.annotate(f"{v:.1f}", (xi, v), textcoords="offset points",
                    xytext=(0, 3), ha="center", fontsize=9.5, color=COR_EVENTO)
    for xi, v in zip(x + larg / 2, vd):
        ax.annotate(f"{v:.1f}", (xi, v), textcoords="offset points",
                    xytext=(0, 3), ha="center", fontsize=9.5,
                    color="#0b0b0b", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(cats, fontsize=10)
    ax.set_ylabel("Ocupação UTI (%)")
    ax.set_title(titulo)
    ax.set_ylim(0, max(np.nanmax(va), np.nanmax(vd)) * 1.18)

# O % de observações não-aplicáveis é o que explica o tamanho do viés, e
# pertence à barra sem correção — é ela que os zeros contaminam. Vai na
# vertical, dentro da barra (abaixo do eixo, os rótulos das cinco categorias
# colidiam entre si), e só no painel da média: a proporção é atributo da
# categoria, não da estatística, e repeti-la nos dois painéis só polui.
media_todos = so_cat["ocup_media_todos"].to_numpy(float)
for xi, v, p in zip(x - larg / 2, media_todos, so_cat["pct_sem_uti_sus"]):
    # em barra curta o texto passaria por cima do rótulo de valor
    base = 1.5 if v >= 25 else v + 5
    eixos[0].annotate(f"{p:.0f}% sem UTI SUS", (xi, base), rotation=90,
                      ha="center", va="bottom", fontsize=8.5, color=COR_EVENTO)

eixos[0].legend(frameon=False, fontsize=10, loc="upper left")
fig.suptitle("Ocupação de UTI antes e depois da correção do domínio de definição\n"
             "observações com uti_sus = 0 deixam de contar como ocupação zero",
             fontsize=11)
fig.tight_layout()

PASTA_FIG.mkdir(parents=True, exist_ok=True)
cam_fig = PASTA_FIG / "figSEG_00_ocupacao_uti_antes_depois.png"
fig.savefig(cam_fig, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)


# ---------------------------------------------------------------------------
# GRAVAÇÃO — painel corrigido
# ---------------------------------------------------------------------------
# Contrato: nada some, nada muda de valor; só entram duas colunas.
if len(df) != N_IN:
    _parar(f"Observações perdidas: {N_IN:,} -> {len(df):,}.")
if list(df.columns)[:len(COLS_IN)] != COLS_IN:
    _parar("As colunas originais foram alteradas ou reordenadas.")

df.to_csv(PAINEL_OUT, index=False, encoding="utf-8-sig")

# Relê o que foi gravado e confere coluna a coluna contra a entrada. O
# contrato "nada muda de valor" precisa ser verificado, não só afirmado:
# a única diferença tolerada é o ruído de ida e volta em ponto flutuante.
_volta = pd.read_csv(PAINEL_OUT)
_pior_rel, _pior_col = 0.0, None
for col in COLS_IN:
    orig, novo = df[col], _volta[col]
    if orig.dtype.kind in "fi":
        escala = orig.abs().max() or 1.0
        rel = float((orig - novo).abs().max()) / escala
        if rel > _pior_rel:
            _pior_rel, _pior_col = rel, col
    elif (orig.fillna("\x00") != novo.fillna("\x00")).any():
        _parar(f"Coluna de texto '{col}' mudou ao ser gravada.")
if _pior_rel > 1e-9:
    _parar(f"Coluna '{_pior_col}' mudou de valor além do ruído numérico "
           f"(erro relativo {_pior_rel:.2e}).")

print("\n" + "=" * 78)
print("ESCRITO")
print("=" * 78)
for c in (cam_tab, cam_fig, PAINEL_OUT):
    print(f"  {c.relative_to(RAIZ)}")
print(f"\n{PAINEL_IN.relative_to(RAIZ)} NÃO foi modificado.")
print(f"colunas novas: tem_uti_sus, ocupacao_uti_valida "
      f"({len(COLS_IN)} -> {df.shape[1]} colunas)")
print(f"colunas originais conferidas na releitura: {len(COLS_IN)}/{len(COLS_IN)} "
      f"iguais (pior erro relativo {_pior_rel:.1e}, em '{_pior_col}')")
print("\nPONTO DE PARADA — tabSEG_00 vai para a Priscilla antes de qualquer "
      "reestimação.")
