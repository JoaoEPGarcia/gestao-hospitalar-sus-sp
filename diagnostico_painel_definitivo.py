# -*- coding: utf-8 -*-
"""
diagnostico_painel_definitivo.py
================================
Diagnóstico exploratório do PAINEL ANALÍTICO DEFINITIVO (314 hospitais ×
11 anos = 3.454 observações), gerado por construir_painel_definitivo.py. Reaproveita a
infraestrutura de analise_sih.py (rotulagem, figuras, descritivas).

Blocos:
  1. Descritivas dos indicadores oficiais (versões SEM covid) — geral e por ano
  2. Distribuições: boxplots por ano, histogramas, séries temporais
  3. Corte por modelo_gestao_proxy — DEFINIÇÃO ADOTADA de modelo de gestão,
     ressalva estampada em figura e tabela; usa modelo_gestao_proxy (NUNCA
     class_assistencial); HU-UFSCar agrupado em Privado por decisão da equipe
  4. Comparação ANTES/DEPOIS dos filtros: painel bruto (com covid) ×
     definitivo (com covid) × definitivo (sem covid) — separa o efeito da
     seleção de hospitais do efeito da remoção do código 999
  5. Complexidade: faixas Barcelona no painel final e comparação entre as
     duas versões do escore (estrutural × ponderado por mortalidade)

LIMITAÇÃO DE DESENHO (destacar no relatório): 3 dos 5 switchers Direta→OSS
(CNES 2082225, 2091755, 2750511) só viram OSS em 2025 — 1 ano de
pós-tratamento. Impressa ao final e registrada no LEIAME do painel.

USO: python diagnostico_painel_definitivo.py
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import analise_sih as base                      # também embrulha stdout em UTF-8
import construir_painel_definitivo as cpd

INDICADORES = base.INDICADORES                  # 5 indicadores oficiais
ROTULOS     = base.ROTULOS

TAB_DESC_GERAL   = base.PASTA_TABELAS / "tab_def_descritiva_geral.csv"
TAB_DESC_ANO     = base.PASTA_TABELAS / "tab_def_descritiva_por_ano.csv"
TAB_MODELO       = base.PASTA_TABELAS / "tab_def_por_modelo_gestao.csv"
TAB_ANTES_DEPOIS = base.PASTA_TABELAS / "tab_def_antes_depois.csv"

NOTA_PROXY_FIG = ("Modelo de gestão: categorias de class_assistencial (SIH) "
                  "como definição operacional adotada; PPP/Autarquia não "
                  "desmembrados; Público Municipal como dummy única. Categoria "
                  "Privado (n=3) inclui o HU UFSCar, hospital público federal "
                  "(Ebserh) agrupado por conveniência estatística; "
                  "coeficientes de n=3 não são interpretáveis como efeito "
                  "médio do modelo.")

LIMITACAO_SWITCHERS = (
    "LIMITAÇÃO DE DESENHO — SWITCHERS DIRETA→OSS: dos 5 hospitais com "
    "transição documentada, 3 (CNES 2082225, 2091755, 2750511) só aparecem "
    "como OSS em 2025, oferecendo APENAS 1 ANO de pós-tratamento no painel; "
    "2078287 vira em 2023 (3 anos pós) e 2081695 em 2019 (7 anos pós). Isso "
    "limita o poder de identificação within-hospital e deve constar na seção "
    "de limitações do documento.")


def carregar():
    painel_def = pd.read_csv(cpd.PAINEL_DEFINITIVO_CSV, encoding="utf-8-sig")
    painel_bruto = cpd.carregar_painel_bruto()
    # indicadores do bruto = versões COM covid (base histórica, sem filtros)
    bruto_ind = base.calcular_indicadores(painel_bruto)
    return painel_def, bruto_ind


# ══════════════════════════════════════════════════════════════════════════════
# 1. DESCRITIVAS
# ══════════════════════════════════════════════════════════════════════════════

def descritivas(painel: pd.DataFrame):
    cols = INDICADORES + ["ocupacao_internacao", "ocupacao_uti"]
    cols = [c for c in cols if c in painel.columns]

    geral = (painel[cols].describe(percentiles=[.10, .25, .5, .75, .90])
             .T.round(4))
    geral.index.name = "indicador"
    geral.to_csv(TAB_DESC_GERAL, encoding="utf-8-sig")
    print("\n[1] DESCRITIVA GERAL — indicadores oficiais (SEM covid), "
          "314 hospitais × 11 anos = 3.454 hospital-ano")
    print(geral.to_string())

    por_ano = (painel.groupby("ano")[cols]
               .describe(percentiles=[.25, .5, .75]).round(4))
    por_ano.to_csv(TAB_DESC_ANO, encoding="utf-8-sig")
    print(f"\n[1] Descritiva por ano → {TAB_DESC_ANO.name}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. DISTRIBUIÇÕES
# ══════════════════════════════════════════════════════════════════════════════

def figuras_distribuicao(painel: pd.DataFrame):
    anos = sorted(painel["ano"].unique())
    n = len(INDICADORES)

    # figD01 — boxplots por ano
    fig, axes = plt.subplots(n, 1, figsize=(14, 4 * n))
    for ax, ind in zip(axes, INDICADORES):
        dados = [painel.loc[painel["ano"] == a, ind].dropna() for a in anos]
        ax.boxplot(dados, labels=[str(a) for a in anos],
                   patch_artist=True, flierprops={"markersize": 2})
        ax.set_title(ROTULOS[ind], fontsize=9)
    fig.suptitle("Painel definitivo — distribuição dos indicadores por ano "
                 "(versões sem COVID)", y=1.005)
    fig.tight_layout()
    base._salvar_fig(fig, "figD01_boxplots_por_ano.png")

    # figD02 — séries temporais mediana ± IQR
    grp = painel.groupby("ano")[INDICADORES]
    med, q25, q75 = grp.median(), grp.quantile(.25), grp.quantile(.75)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4))
    for ax, ind in zip(axes, INDICADORES):
        ax.plot(med.index, med[ind], "o-", color="#4e79a7", lw=1.8, ms=5)
        ax.fill_between(med.index, q25[ind], q75[ind], alpha=.2, color="#4e79a7")
        ax.set_title(ROTULOS[ind], fontsize=8)
        ax.tick_params(axis="x", rotation=45)
    fig.suptitle("Painel definitivo — mediana ± IQR por ano (sem COVID)")
    fig.tight_layout()
    base._salvar_fig(fig, "figD02_series_temporais.png")

    # figD03 — histogramas gerais
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4))
    for ax, ind in zip(axes, INDICADORES):
        ax.hist(painel[ind].dropna(), bins=50, color="#4e79a7",
                edgecolor="white", lw=.3)
        ax.set_title(ROTULOS[ind], fontsize=8)
        ax.set_ylabel("Nº hospitais-ano")
    fig.suptitle("Painel definitivo — histogramas (todos os anos)")
    fig.tight_layout()
    base._salvar_fig(fig, "figD03_histogramas.png")


# ══════════════════════════════════════════════════════════════════════════════
# 3. CORTE POR MODELO DE GESTÃO (DEFINIÇÃO ADOTADA — ver nota)
# ══════════════════════════════════════════════════════════════════════════════

def corte_modelo_gestao(painel: pd.DataFrame):
    col = "modelo_gestao_proxy"
    assert col in painel.columns, (
        "Coluna modelo_gestao_proxy ausente — regenerar o painel com "
        "construir_painel_definitivo.py")
    sub = painel[painel[col].notna()]
    cats = sorted(sub[col].unique())

    print(f"\n[3] CORTE POR MODELO DE GESTÃO — {NOTA_PROXY_FIG}")
    contagem = (sub.groupby(col)["cnes"]
                .agg(hospital_ano="size", cnes_distintos="nunique"))
    print(contagem.to_string())

    # tabela de medianas por categoria × indicador (todos os anos)
    tab = sub.groupby(col)[INDICADORES].median().round(4)
    tab.insert(0, "n_hospital_ano", sub.groupby(col).size())
    tab.index.name = "modelo_gestao_proxy (definição adotada — ver nota)"
    tab.to_csv(TAB_MODELO, encoding="utf-8-sig")
    print(f"\nMedianas por categoria (todos os anos) → {TAB_MODELO.name}")
    print(tab.to_string())

    # figD04 — boxplots por categoria, aviso estampado
    n = len(INDICADORES)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 6))
    for ax, ind in zip(axes, INDICADORES):
        vals = [sub.loc[sub[col] == c, ind].dropna() for c in cats]
        ax.boxplot(vals, labels=[str(c) for c in cats],
                   patch_artist=True, flierprops={"markersize": 2})
        ax.set_title(ROTULOS[ind], fontsize=8)
        ax.tick_params(axis="x", rotation=55, labelsize=7)
    fig.suptitle("Painel definitivo — indicadores por modelo de gestão "
                 "(definição adotada — ver nota)")
    fig.text(.5, .01, NOTA_PROXY_FIG, ha="center", fontsize=7,
             style="italic", wrap=True,
             bbox={"facecolor": "#fff3cd", "edgecolor": "#e0a800", "pad": 4})
    fig.tight_layout(rect=[0, .04, 1, 1])
    base._salvar_fig(fig, "figD04_por_modelo_gestao_proxy.png")


# ══════════════════════════════════════════════════════════════════════════════
# 4. ANTES / DEPOIS DOS FILTROS
# ══════════════════════════════════════════════════════════════════════════════

def antes_depois(painel_def: pd.DataFrame, bruto_ind: pd.DataFrame):
    """
    Três séries de medianas anuais por indicador:
      bruto_com_covid       — painel original, sem filtros (830 CNES)
      definitivo_com_covid  — só o efeito da SELEÇÃO de hospitais
      definitivo_sem_covid  — seleção + remoção do código 999 (oficial)
    A distância bruto→def_com isola o efeito dos filtros A-B-C1-D; a
    distância def_com→def_sem isola o efeito da etapa C2.
    """
    series = {
        "bruto_com_covid": (bruto_ind, INDICADORES),
        "definitivo_com_covid": (painel_def,
                                 [f"{i}_com_covid" for i in INDICADORES]),
        "definitivo_sem_covid": (painel_def, INDICADORES),
    }
    linhas = []
    for versao, (df, cols) in series.items():
        med = df.groupby("ano")[cols].median()
        med.columns = INDICADORES          # nomes canônicos p/ empilhar
        med["n_hospitais"] = df[df["qtde"] > 0].groupby("ano")["cnes"].nunique()
        med["versao"] = versao
        linhas.append(med.reset_index())
    tab = pd.concat(linhas, ignore_index=True).round(4)
    tab.to_csv(TAB_ANTES_DEPOIS, index=False, encoding="utf-8-sig")
    print(f"\n[4] Antes/depois dos filtros → {TAB_ANTES_DEPOIS.name}")

    resumo = tab.groupby("versao")[INDICADORES].median().round(4)
    print("Mediana das medianas anuais, por versão do painel:")
    print(resumo.to_string())

    # figD05 — séries sobrepostas
    n = len(INDICADORES)
    cores = {"bruto_com_covid": "#bab0ac",
             "definitivo_com_covid": "#e15759",
             "definitivo_sem_covid": "#4e79a7"}
    rotulos_v = {"bruto_com_covid": "Bruto (830 CNES, com COVID)",
                 "definitivo_com_covid": "Definitivo (314 CNES, com COVID)",
                 "definitivo_sem_covid": "Definitivo (314 CNES, sem COVID)"}
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4))
    for ax, ind in zip(axes, INDICADORES):
        for versao, cor in cores.items():
            s = tab[tab["versao"] == versao]
            ax.plot(s["ano"], s[ind], "o-", color=cor, lw=1.6, ms=4,
                    label=rotulos_v[versao])
        ax.set_title(ROTULOS[ind], fontsize=8)
        ax.tick_params(axis="x", rotation=45)
    axes[0].legend(fontsize=6)
    fig.suptitle("Efeito dos filtros: medianas anuais antes/depois "
                 "(seleção de hospitais × remoção do código 999)")
    fig.tight_layout()
    base._salvar_fig(fig, "figD05_antes_depois_filtros.png")


# ══════════════════════════════════════════════════════════════════════════════
# 5. COMPLEXIDADE — FAIXAS E AS DUAS VERSÕES DO ESCORE
# ══════════════════════════════════════════════════════════════════════════════

def complexidade(painel: pd.DataFrame):
    print("\n[5] COMPLEXIDADE — faixas Barcelona no painel definitivo:")
    print(painel.groupby("faixa_barcelona")["cnes"].nunique()
          .rename("n_cnes").to_string())

    # figD06 — escore estrutural × ponderado por mortalidade
    sub = painel.dropna(subset=["complexidade_estrutural",
                                "complexidade_pond_mort"])
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(sub["complexidade_estrutural"], sub["complexidade_pond_mort"],
               s=8, alpha=.3, color="#4e79a7")
    lim = [0, max(sub["complexidade_pond_mort"].max(),
                  sub["complexidade_estrutural"].max()) * 1.02]
    ax.plot(lim, lim, "--", color="#e15759", lw=1, label="identidade (peso nulo)")
    ax.set_xlabel("complexidade_estrutural (Barcelona pura)")
    ax.set_ylabel("complexidade_pond_mort (fórmula provisória)")
    ax.legend(fontsize=8)
    ax.set_title("Duas versões do escore de complexidade (hospital-ano)\n"
                 "Modelos de MORTALIDADE devem usar SOMENTE a versão "
                 "estrutural (salvaguarda de circularidade, critérios §4)",
                 fontsize=9)
    fig.tight_layout()
    base._salvar_fig(fig, "figD06_complexidade_duas_versoes.png")

    corr = sub[["complexidade_estrutural", "complexidade_pond_mort"]].corr(
        method="spearman").iloc[0, 1]
    print(f"Correlação de Spearman entre as duas versões: {corr:.3f}")


def main():
    print("=" * 70)
    print("DIAGNÓSTICO EXPLORATÓRIO — PAINEL ANALÍTICO DEFINITIVO")
    print("=" * 70)
    print(f"\n{cpd.AVISO_PROXY}\n")

    base.configurar_diretorios()
    painel_def, bruto_ind = carregar()
    print(f"[CARGA] definitivo: {painel_def['cnes'].nunique()} CNES × "
          f"{painel_def['ano'].nunique()} anos = {len(painel_def)} hospital-ano | "
          f"bruto: {bruto_ind['cnes'].nunique()} CNES, {len(bruto_ind)} hospital-ano")

    descritivas(painel_def)
    figuras_distribuicao(painel_def)
    corte_modelo_gestao(painel_def)
    antes_depois(painel_def, bruto_ind)
    complexidade(painel_def)

    print("\n" + "!" * 70)
    print(LIMITACAO_SWITCHERS)
    print("!" * 70)
    print("\nCONCLUÍDO. Figuras figD01-figD06 em analises/figuras; tabelas "
          "tab_def_* em analises/tabelas.")


if __name__ == "__main__":
    main()
