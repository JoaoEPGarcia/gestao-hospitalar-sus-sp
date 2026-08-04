# -*- coding: utf-8 -*-
"""
ETAPA 3 — Descritivas segmentadas por estrato estrutural.

Lê painel_segmentado.csv (ETAPA 2) e descreve os seis indicadores dentro de
cada estrato, para dimensionar quanto a média agregada por categoria de
gestão estava misturando tecnologias de produção distintas.

Regra de reporte
----------------
Célula com menos de 10 CNES recebe a marca [n<10] na coluna `tarja`. A linha
NÃO é suprimida: o funil precisa ficar auditável, e uma célula pequena
omitida é indistinguível de uma célula que não existe.

RESTRIÇÃO DE CITAÇÃO — par de mortalidade de E3 (R2, 27/07/2026)
----------------------------------------------------------------
Este script produz, dentro de E3, `mort_all` mediana Direta 0,0698 contra
OSS 0,0536. ESSE PAR NÃO É CITÁVEL COMO ACHADO DESCRITIVO em nenhum texto:
está em parte comprado por composição de casemix dentro do próprio estrato.
A Direta tem 22 hospital-ano em faixa 6 e o OSS tem zero — assimetria de
cauda, vinda de 2 CNES, com escore Barcelona médio praticamente idêntico
entre as duas categorias (455,9 contra 455,6).

A restrição vale para o par OSS × Direta. Não vale dizer que os hospitais de
complexidade máxima de E3 são todos Direta: o Filantrópico tem 8 CNES em
faixa 6, quatro vezes os 2 da Direta.

Não invalida a estratificação — é por isso que complexidade_estrutural
permanece como covariável dentro do estrato. Ver RESTRICOES_SEGMENTACAO.md
e tabSEG_05d_composicao_faixa_e3.csv.

NOTA sobre ocupacao_internacao (R1 v4, 28/07/2026 — ITEM RESOLVIDO)
--------------------------------------------------------------------
15,5% das observações têm ocupação acima de 100%, com incidência fortemente
diferencial por categoria — 29,3% no OSS contra 3,9% na Direta. A natureza
do excesso ESTÁ ESTABELECIDA e não é erro de nenhum dos dois sistemas:

  - o CNES registra estritamente capacidade instalada e HABILITADA, e exclui
    por definição qualquer leito extra efetivamente operado;
  - o SIH fatura diária e gera AIH primária para maca e leito de observação
    quando a permanência ultrapassa 24 horas (a "regra das 24 horas"), o que
    configura leito extra por superlotação.

Ocupação acima de 100% é a ASSINATURA ARITMÉTICA DA SUPERLOTAÇÃO: o
numerador conta permanência em leito extra, o denominador exclui leito extra.
Os dois campos estão corretos segundo as próprias definições.

Consequência para esta tabela: o indicador NÃO é descritiva tarjada. Ele
entra na estimação da Etapa 4 em MODELO DE DUAS PARTES (R6) — binário de
superlotação (>100) e contínua condicional (<=100) —, nunca como contínua
winsorizada, que apagaria o sinal. A média bruta desta tabela CONFLACIONA as
duas partes e não deve ser lida como "quão cheio o hospital opera": parte da
diferença entre categorias é frequência de superlotação, não nível de
ocupação. Ver RESTRICOES_SEGMENTACAO.md (R1, R6).

NOTA sobre uti_sus == 0 (R7, 28/07/2026)
-----------------------------------------
As observações com uti_sus == 0 NÃO são todas ausência de UTI. Das 688 do
painel definitivo, 650 são ausência real (76 CNES) e 38 são PISCAR CADASTRAL
com operação ativa (26 CNES): uti_sus zerado e diarias_uti > 0. É suspensão e
limpeza de cadastro — por exemplo inativação temporária por falta de
intensivista —, não demolição de ala.

Isso reforça a estratificação fixa por mediana: a capacidade subjacente é
estável e o cadastro é que pisca, de modo que a mediana dos onze anos é o
estimador certo. Não muda a ETAPA 1 — a razão segue indefinida com
denominador zero e essas 38 observações saem do modelo de qualquer forma,
via ocupacao_uti_valida. Muda o motivo registrado. Ver
verificar_piscar_cadastral.py e tabSEG_09_piscar_cadastral.csv.

Faturamento
-----------
`custo_saida` está em base NOMINAL no painel. A descritiva usa `custo_real`
= custo_saida × fator IPCA (preços de dez/2025), a mesma construção de
analise_exploratoria.py (item 1.5, decisão de 14/07/2026), reproduzida aqui
para não importar aquele script — que roda o pipeline inteiro ao ser
carregado.

Saídas
------
  analises/tabelas/tabSEG_04_indicadores_por_estrato.csv
  analises/tabelas/tabSEG_05_antes_depois_segmentacao.csv
  analises/figuras_segmentacao/figSEG_01_boxplots_por_estrato.png
  analises/figuras_segmentacao/figSEG_02_series_por_estrato.png
  analises/figuras_segmentacao/figSEG_01_box_<indicador>.png       (6 arquivos)
  analises/figuras_segmentacao/figSEG_02_serie_<indicador>.png     (6 arquivos)

As duas últimas famílias são os painéis das duas figuras acima, um por
indicador, para que cada gráfico possa ocupar a largura inteira da página do
relatório em vez de um sexto dela.
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
PAINEL_IN = RAIZ / "analises" / "painel_segmentado.csv"
PASTA_TAB = RAIZ / "analises" / "tabelas"
PASTA_FIG = RAIZ / "analises" / "figuras_segmentacao"

PISO_CNES = 10          # abaixo disto a célula é tarjada
TARJA = "[n<10]"

CATEGORIAS = ["Direta", "OSS", "Público Municipal", "Filantrópico", "Privado"]
ESTRATOS = ["E1", "E2", "E3"]
ROTULOS = {"E1": "sem_uti_sus", "E2": "uti_baixa_complex", "E3": "uti_alta_complex"}

INDICADORES = ["mort_all", "tmp", "custo_real", "ocupacao_uti_valida",
               "pct_alta_complex", "ocupacao_internacao"]
ROT = {
    "mort_all":            "Mortalidade geral",
    "tmp":                 "TMP (dias)",
    "custo_real":          "Faturamento real por saída (R$ dez/2025)",
    "ocupacao_uti_valida": "Ocupação UTI (%) — só uti_sus > 0",
    "pct_alta_complex":    "Fração alta complexidade",
    "ocupacao_internacao": "Ocupação internação (%)",
}
LOG_Y = {"custo_real"}   # Privado fica três ordens de grandeza acima

# Paleta e estilo idênticos aos de analise_exploratoria.py.
CORES_CAT = {
    "Direta":            "#0d366b",
    "OSS":               "#0f9b8e",
    "Público Municipal": "#5598e7",
    "Filantrópico":      "#6a51c7",
    "Privado":           "#898781",
}
MARCADORES = {"E1": "o", "E2": "s", "E3": "D"}
# Estratos ganham rampa própria: confundi-los com as cores de categoria
# seria ler estrutura como gestão, que é justamente o que se quer separar.
CORES_ESTRATO = {"E1": "#86b6ef", "E2": "#2a78d6", "E3": "#0d366b"}
COR_EVENTO = "#52514e"
COR_GRADE  = "#e1e0d9"
COR_EIXO   = "#c3c2b7"
COR_MUTED  = "#898781"
COR_BANDA  = "#f0efec"

IPCA_ANUAL = {2015: 10.67, 2016: 6.29, 2017: 2.95, 2018: 3.75, 2019: 4.31,
              2020: 4.52, 2021: 10.06, 2022: 5.79, 2023: 4.62, 2024: 4.83,
              2025: 4.26}

plt.rcParams.update({
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": COR_EIXO, "axes.labelcolor": "#0b0b0b",
    "axes.grid": True, "grid.color": COR_GRADE, "grid.linewidth": .6,
    "xtick.color": COR_MUTED, "ytick.color": COR_MUTED,
    "font.size": 11.5, "axes.titlesize": 11.5, "figure.titlesize": 11,
})


def _parar(motivo: str) -> None:
    print("\n" + "!" * 78)
    print("PARAR E REPORTAR")
    print(motivo)
    print("Nenhum arquivo foi escrito.")
    print("!" * 78)
    sys.exit(1)


def _fatores_ipca_2025() -> dict:
    """Fator multiplicativo que leva valores do ano de referência a preços de
    2025 (índice acumulado dez/dez até o fim de cada ano)."""
    anos = sorted(IPCA_ANUAL)
    indice, acum = {}, 1.0
    for a in anos:
        acum *= 1 + IPCA_ANUAL[a] / 100
        indice[a] = acum
    return {a: indice[anos[-1]] / indice[a] for a in anos}


# ---------------------------------------------------------------------------
# LEITURA
# ---------------------------------------------------------------------------
print("=" * 78)
print("ETAPA 3 — descritivas segmentadas")
print("=" * 78)

if not PAINEL_IN.exists():
    _parar(f"{PAINEL_IN.name} não existe. Rodar antes a ETAPA 2.")

df = pd.read_csv(PAINEL_IN)
if "estrato" not in df.columns or "ocupacao_uti_valida" not in df.columns:
    _parar("O painel de entrada não traz estrato/ocupacao_uti_valida.")

fatores = _fatores_ipca_2025()
# O fator de 2015 é o deflator ratificado do projeto; se ele não bater, a
# tabela de IPCA aqui divergiu da que o resto do documento usa.
if round(fatores[2015], 4) != 1.6479:
    _parar(f"Fator IPCA de 2015 = {fatores[2015]:.4f}, esperado 1.6479. "
           "A série de IPCA deste script divergiu da do projeto.")
df["custo_real"] = df["custo_saida"] * df["ano"].map(fatores)

print(f"\nlido: {PAINEL_IN.relative_to(RAIZ)}")
print(f"  {len(df):,} observações | {df['cnes'].nunique():,} CNES")
print(f"  deflator IPCA dez/2025: 2015 = {fatores[2015]:.4f}, "
      f"2025 = {fatores[2025]:.4f}")

cats = [c for c in CATEGORIAS if (df["modelo_gestao_proxy"] == c).any()]


# ---------------------------------------------------------------------------
# tabSEG_04 — indicadores por estrato × categoria
# ---------------------------------------------------------------------------
def _celula(bloco: pd.DataFrame, ind: str) -> dict:
    """Estatísticas de um indicador numa célula, sobre as observações em que
    ele está definido. Em ocupacao_uti_valida isso importa: o indicador é
    ausente onde não há leito de UTI SUS, e contar essas linhas no n daria
    uma célula maior do que a que sustenta a estatística."""
    val = bloco[ind].dropna()
    n_cnes = bloco.loc[bloco[ind].notna(), "cnes"].nunique()
    return {
        "n_cnes": n_cnes,
        "n_hospital_ano": len(val),
        "media": round(val.mean(), 4) if len(val) else np.nan,
        "p25": round(val.quantile(.25), 4) if len(val) else np.nan,
        "mediana": round(val.median(), 4) if len(val) else np.nan,
        "p75": round(val.quantile(.75), 4) if len(val) else np.nan,
        "tarja": TARJA if n_cnes < PISO_CNES else "",
    }


linhas = []
for e in ESTRATOS:
    bloco_e = df[df["estrato"] == e]
    for c in cats + ["TODAS"]:
        bloco = bloco_e if c == "TODAS" else bloco_e[bloco_e["modelo_gestao_proxy"] == c]
        for ind in INDICADORES:
            linhas.append({"estrato": e, "estrato_rotulo": ROTULOS[e],
                           "modelo_gestao_proxy": c, "indicador": ind,
                           **_celula(bloco, ind)})
tab04 = pd.DataFrame(linhas)

PASTA_TAB.mkdir(parents=True, exist_ok=True)
tab04.to_csv(PASTA_TAB / "tabSEG_04_indicadores_por_estrato.csv",
             index=False, encoding="utf-8-sig")

print("\n" + "=" * 78)
print("tabSEG_04 — medianas por estrato × categoria")
print("=" * 78)
for ind in INDICADORES:
    sub = tab04[tab04["indicador"] == ind]
    piv = sub.pivot(index="modelo_gestao_proxy", columns="estrato",
                    values="mediana").reindex(cats + ["TODAS"])[ESTRATOS]
    ntag = sub.pivot(index="modelo_gestao_proxy", columns="estrato",
                     values="tarja").reindex(cats + ["TODAS"])[ESTRATOS]
    ncn = sub.pivot(index="modelo_gestao_proxy", columns="estrato",
                    values="n_cnes").reindex(cats + ["TODAS"])[ESTRATOS]
    print(f"\n{ROT[ind]}  [{ind}]")
    for cat in piv.index:
        partes = []
        for e in ESTRATOS:
            v, t, n = piv.loc[cat, e], ntag.loc[cat, e], ncn.loc[cat, e]
            txt = "     --     " if pd.isna(v) else f"{v:>9.4g} (n={int(n)})"
            partes.append(f"{txt}{t}")
        print(f"  {cat:<18} " + " | ".join(f"{p:<22}" for p in partes))

n_tarjadas = int((tab04["tarja"] == TARJA).sum())
print(f"\ncélulas tarjadas [n<10]: {n_tarjadas} de {len(tab04)}")


# ---------------------------------------------------------------------------
# tabSEG_05 — antes e depois da segmentação
# ---------------------------------------------------------------------------
# O ponto da tabela: quanto a estatística agregada por categoria de gestão se
# afasta da estatística dentro de cada estrato. Diferença grande significa
# que o número agregado descrevia a composição da carteira de hospitais, não
# o desempenho da gestão.
linhas5 = []
for ind in INDICADORES:
    for c in cats + ["TODAS"]:
        bloco_c = df if c == "TODAS" else df[df["modelo_gestao_proxy"] == c]
        agr = _celula(bloco_c, ind)
        base_med = agr["mediana"]
        linhas5.append({"indicador": ind, "modelo_gestao_proxy": c,
                        "escopo": "agregado", "estrato_rotulo": "todos",
                        **agr, "dif_mediana_vs_agregado": 0.0,
                        "dif_pct_vs_agregado": 0.0})
        for e in ESTRATOS:
            cel = _celula(bloco_c[bloco_c["estrato"] == e], ind)
            dif = (np.nan if pd.isna(cel["mediana"]) or pd.isna(base_med)
                   else round(cel["mediana"] - base_med, 4))
            dpc = (np.nan if pd.isna(dif) or not base_med
                   else round(100 * dif / base_med, 2))
            linhas5.append({"indicador": ind, "modelo_gestao_proxy": c,
                            "escopo": e, "estrato_rotulo": ROTULOS[e],
                            **cel, "dif_mediana_vs_agregado": dif,
                            "dif_pct_vs_agregado": dpc})
tab05 = pd.DataFrame(linhas5)
tab05.to_csv(PASTA_TAB / "tabSEG_05_antes_depois_segmentacao.csv",
             index=False, encoding="utf-8-sig")

print("\n" + "=" * 78)
print("tabSEG_05 — agregado vs. dentro do estrato (mediana, todas as categorias)")
print("=" * 78)
sub = tab05[tab05["modelo_gestao_proxy"] == "TODAS"]
print(f"{'indicador':<22} {'agregado':>12} {'E1':>12} {'E2':>12} {'E3':>12} "
      f"{'amplitude':>12}")
for ind in INDICADORES:
    s = sub[sub["indicador"] == ind].set_index("escopo")
    vals = [s.loc[e, "mediana"] if e in s.index else np.nan
            for e in ["agregado"] + ESTRATOS]
    amp = np.nanmax(vals[1:]) - np.nanmin(vals[1:])
    print(f"{ind:<22} " + " ".join(f"{v:>12.4g}" for v in vals) +
          f" {amp:>12.4g}")

# A amplitude entre estratos, comparada ao próprio nível agregado, mede o
# tamanho do que a agregação escondia.
print("\namplitude entre estratos como % do nível agregado:")
for ind in INDICADORES:
    s = sub[sub["indicador"] == ind].set_index("escopo")
    base_med = s.loc["agregado", "mediana"]
    vals = [s.loc[e, "mediana"] for e in ESTRATOS if e in s.index]
    amp = np.nanmax(vals) - np.nanmin(vals)
    print(f"  {ind:<22} {100 * amp / base_med:>6.1f}%")


# ---------------------------------------------------------------------------
# figSEG_01 — boxplots por estrato × categoria
#
# As duas figuras deste bloco saem em DUAS VERSÕES (decisão de 01/08/2026): a
# grade de seis painéis, que serve à leitura de conjunto, e um arquivo por
# indicador, que é o que entra no relatório. O painel de seis, reduzido à
# largura da mancha de uma folha A4, deixava rótulo de eixo e asterisco de
# célula tarjada em corpo ilegível; separado, cada gráfico ocupa a página
# inteira. O desenho de cada painel é o mesmo nos dois casos, porque é a
# mesma função que o produz: nada diverge entre a versão de conjunto e a
# individual.
# ---------------------------------------------------------------------------
def _painel_boxplot(ax, ind, fonte_x=9.5):
    """Desenha, num eixo, os boxplots de um indicador por estrato e categoria."""
    pos, dados, cores, rotulos_x, centros, marcados = [], [], [], [], [], []
    passo = len(cats) + 1.4
    for i, e in enumerate(ESTRATOS):
        base_x = i * passo
        usados = []
        for j, c in enumerate(cats):
            val = df.loc[(df["estrato"] == e) &
                         (df["modelo_gestao_proxy"] == c), ind].dropna()
            if not len(val):                       # célula vazia: Privado em E3
                continue
            x = base_x + j
            pos.append(x)
            dados.append(val.to_numpy())
            cores.append(CORES_CAT[c])
            n_cnes = df.loc[(df["estrato"] == e) &
                            (df["modelo_gestao_proxy"] == c) &
                            df[ind].notna(), "cnes"].nunique()
            if n_cnes < PISO_CNES:
                marcados.append(x)
            usados.append(x)
        centros.append(np.mean(usados) if usados else base_x)
        rotulos_x.append(f"{e}\n{ROTULOS[e]}")

    bp = ax.boxplot(dados, positions=pos, widths=.78, patch_artist=True,
                    showfliers=False, medianprops=dict(color="white", lw=1.6),
                    whiskerprops=dict(color=COR_MUTED, lw=.9),
                    capprops=dict(color=COR_MUTED, lw=.9))
    for caixa, cor in zip(bp["boxes"], cores):
        caixa.set(facecolor=cor, edgecolor="white", lw=.6)

    topo = ax.get_ylim()[1]
    for x in marcados:
        ax.annotate("*", (x, topo), textcoords="offset points", xytext=(0, -12),
                    ha="center", fontsize=13, color=COR_EVENTO)

    if ind in LOG_Y:
        ax.set_yscale("log")
    ax.set_xticks(centros)
    ax.set_xticklabels(rotulos_x, fontsize=fonte_x)
    ax.set_title(ROT[ind], fontsize=11)
    ax.grid(axis="x", visible=False)


maneiras = [plt.Rectangle((0, 0), 1, 1, facecolor=CORES_CAT[c]) for c in cats]
PASTA_FIG.mkdir(parents=True, exist_ok=True)

fig, eixos = plt.subplots(2, 3, figsize=(17.5, 10.5))
for ax, ind in zip(eixos.ravel(), INDICADORES):
    _painel_boxplot(ax, ind)
fig.legend(maneiras, cats, ncol=len(cats), frameon=False, fontsize=10.5,
           loc="lower center", bbox_to_anchor=(.5, -.005))
fig.suptitle("Indicadores por estrato estrutural e categoria de gestão\n"
             "caixas sem outliers; * marca célula com menos de "
             f"{PISO_CNES} CNES; faturamento em escala logarítmica",
             fontsize=11.5)
fig.tight_layout(rect=[0, .035, 1, .97])
fig.savefig(PASTA_FIG / "figSEG_01_boxplots_por_estrato.png", dpi=150,
            bbox_inches="tight", facecolor="white")
plt.close(fig)

for ind in INDICADORES:
    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    _painel_boxplot(ax, ind, fonte_x=11)
    ax.set_title(f"{ROT[ind]} por estrato estrutural e categoria de gestão\n"
                 f"caixas sem outliers; * marca célula com menos de "
                 f"{PISO_CNES} CNES"
                 + ("; escala logarítmica" if ind in LOG_Y else ""),
                 fontsize=12.5)
    fig.legend(maneiras, cats, ncol=len(cats), frameon=False, fontsize=10.5,
               loc="lower center", bbox_to_anchor=(.5, -.01))
    fig.tight_layout(rect=[0, .06, 1, 1])
    fig.savefig(PASTA_FIG / f"figSEG_01_box_{ind}.png", dpi=150,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# figSEG_02 — séries temporais por estrato
# ---------------------------------------------------------------------------
anos = sorted(df["ano"].unique())


def _painel_serie(ax, ind):
    """Desenha, num eixo, a mediana anual do indicador nos três estratos."""
    ax.axvspan(2020, 2021, color=COR_BANDA, zorder=0)
    for e in ESTRATOS:
        serie = (df[df["estrato"] == e].groupby("ano")[ind]
                 .median().reindex(anos))
        # Em E1 a ocupação de UTI existe só nos anos avulsos em que os CNES
        # instáveis tiveram leito habilitado: linha tracejada para não sugerir
        # que o estrato tem série comparável às demais.
        precario = (ind == "ocupacao_uti_valida" and e == "E1")
        ax.plot(anos, serie, marker=MARCADORES[e], ms=4.5, lw=1.7,
                ls="dashed" if precario else "solid",
                color=CORES_ESTRATO[e],
                label=f"{e} {ROTULOS[e]}" + (" (esparso)" if precario else ""))
    if ind in LOG_Y:
        ax.set_yscale("log")
    ax.set_title(ROT[ind], fontsize=11)
    ax.set_xticks(anos[::2])
    ax.legend(frameon=False, fontsize=9)


fig, eixos = plt.subplots(2, 3, figsize=(17.5, 9.5))
for ax, ind in zip(eixos.ravel(), INDICADORES):
    _painel_serie(ax, ind)
fig.suptitle("Mediana anual por estrato estrutural, 2015–2025\n"
             "faixa cinza: 2020 e 2021", fontsize=11.5)
fig.tight_layout(rect=[0, 0, 1, .955])
fig.savefig(PASTA_FIG / "figSEG_02_series_por_estrato.png", dpi=150,
            bbox_inches="tight", facecolor="white")
plt.close(fig)

for ind in INDICADORES:
    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    _painel_serie(ax, ind)
    ax.set_title(f"{ROT[ind]}: mediana anual por estrato estrutural, "
                 f"2015 a 2025\nfaixa cinza: 2020 e 2021", fontsize=12.5)
    ax.set_xticks(anos)
    ax.legend(frameon=False, fontsize=10.5)
    fig.tight_layout()
    fig.savefig(PASTA_FIG / f"figSEG_02_serie_{ind}.png", dpi=150,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)


print("\n" + "=" * 78)
print("ESCRITO")
print("=" * 78)
for nome in ("tabelas/tabSEG_04_indicadores_por_estrato.csv",
             "tabelas/tabSEG_05_antes_depois_segmentacao.csv",
             "figuras_segmentacao/figSEG_01_boxplots_por_estrato.png",
             "figuras_segmentacao/figSEG_02_series_por_estrato.png"):
    print(f"  analises/{nome}")
print(f"  analises/figuras_segmentacao/figSEG_01_box_*.png "
      f"({len(INDICADORES)} arquivos, um por indicador)")
print(f"  analises/figuras_segmentacao/figSEG_02_serie_*.png "
      f"({len(INDICADORES)} arquivos, um por indicador)")
