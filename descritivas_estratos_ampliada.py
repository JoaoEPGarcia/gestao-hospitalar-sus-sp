# -*- coding: utf-8 -*-
"""
Descritiva AMPLIADA por estrato estrutural (E1, E2, E3).

O que este script acrescenta ao `descritivas_segmentadas.py`
------------------------------------------------------------
Aquele script descreve SEIS indicadores dentro de cada estrato, e é a fonte
da tabela do gradiente da Seção da segmentação. Este aqui cruza os estratos
com TODAS as variáveis do painel que admitem leitura descritiva --- estrutura
instalada, produção, casemix, financeiro, uso da capacidade e complexidade,
mais nove métricas derivadas ---, e acrescenta a pergunta que a tabela de
medianas não responde: *quanto* do que separa dois hospitais quaisquer é
explicado por estarem em estratos diferentes.

DECISÃO DE UNIDADE DE ANÁLISE, que é o ponto metodológico deste script
----------------------------------------------------------------------
O estrato é FIXO por CNES (verificado abaixo, aborta se não for). Logo, para
COMPARAR estratos a unidade é o **hospital**, não o hospital-ano: as onze
observações de um hospital são o mesmo hospital medido onze vezes, e tratá-las
como independentes infla qualquer teste por um fator próximo de onze.

Este script, portanto, reporta as duas coisas e não as mistura:

  - DESCRITIVA em hospital-ano (`tabSEG_21`), que é a unidade da tabela já
    publicada e serve de continuidade com ela;
  - TESTE E TAMANHO DE EFEITO em CNES (`tabSEG_22` e `tabSEG_23`), com uma
    linha por hospital (mediana dos onze anos), que é a unidade em que a
    hipótese "os estratos diferem" pode ser testada sem inflar o n.

RESTRIÇÕES HERDADAS, todas respeitadas e impressas nas tabelas
---------------------------------------------------------------
  R1/R6  `ocupacao_internacao` mediana CONFLACIONA frequência de superlotação
         com nível de ocupação. A tabela traz as três colunas separadas:
         mediana bruta, mediana condicional a <= 100 e % de anos > 100.
  R2     o par de mortalidade OSS x Direta dentro de E3 NÃO é citável. O
         cruzamento estrato x categoria (`tabSEG_25`) marca essa célula.
  R7     E1 é definido por MEDIANA de uti_sus igual a zero, não por ausência
         de UTI em todos os anos: 18 CNES de E1 registram UTI SUS em algum
         ano (piscar cadastral). A ocupação de UTI existe para eles e a
         tabela a reporta, tarjada, em vez de imprimir travessão.
  R9/R11 nada aqui é coeficiente de fronteira nem de modelo: é descritiva.
  --     `complexidade_pond_mort` entra TARJADA: é construída usando
         mortalidade, e cruzá-la com mortalidade é circular.
  --     o Privado (3 CNES) nunca é interpretado; aparece só como registro.

Saídas
------
  analises/tabelas/tabSEG_20_dicionario_variaveis.csv
  analises/tabelas/tabSEG_21_estratos_hospital_ano.csv
  analises/tabelas/tabSEG_22_estratos_cnes.csv
  analises/tabelas/tabSEG_23_teste_estratos.csv
  analises/tabelas/tabSEG_24_estratos_por_ano.csv
  analises/tabelas/tabSEG_25_estratos_x_categoria.csv
  analises/figuras_segmentacao/figSEG_10_perfil_estratos.png
  analises/figuras_segmentacao/figSEG_11_eta2_ranking.png
  analises/figuras_segmentacao/figSEG_12_estrutura_uso.png
  analises/figuras_segmentacao/figSEG_12_escala.png
  analises/figuras_segmentacao/figSEG_12_duas_perguntas.png
  analises/figuras_segmentacao/figSEG_12_giro.png
  analises/figuras_segmentacao/figSEG_13_estratos_por_ano.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parent
PAINEL_IN = RAIZ / "analises" / "painel_segmentado.csv"
PASTA_TAB = RAIZ / "analises" / "tabelas"
PASTA_FIG = RAIZ / "analises" / "figuras_segmentacao"

ESTRATOS = ["E1", "E2", "E3"]
ROTULO_ESTRATO = {"E1": "E1 sem UTI SUS",
                  "E2": "E2 com UTI, baixa complexidade",
                  "E3": "E3 com UTI, alta complexidade"}
CATEGORIAS = ["Direta", "OSS", "Público Municipal", "Filantrópico", "Privado"]
PISO_CNES = 10
TARJA_N = "[n<10]"

# IPCA anual (dez/dez, IBGE), reproduzido de analise_exploratoria.py para não
# importar aquele script, que roda o pipeline inteiro ao ser carregado.
IPCA_ANUAL = {2015: 10.67, 2016: 6.29, 2017: 2.95, 2018: 3.75, 2019: 4.31,
              2020: 4.52, 2021: 10.06, 2022: 5.79, 2023: 4.62, 2024: 4.83,
              2025: 4.26}

COR_ESTRATO = {"E1": "#5598e7", "E2": "#0f9b8e", "E3": "#0d366b"}
COR_SERIE, COR_GRADE, COR_EIXO, COR_MUTED = "#2a78d6", "#e1e0d9", "#c3c2b7", "#898781"
MARCADOR = {"E1": "o", "E2": "s", "E3": "D"}

plt.rcParams.update({
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": COR_EIXO, "axes.labelcolor": "#0b0b0b",
    "axes.grid": True, "grid.color": COR_GRADE, "grid.linewidth": .6,
    "xtick.color": COR_MUTED, "ytick.color": COR_MUTED,
    "font.size": 10.5, "axes.titlesize": 11, "figure.titlesize": 11.5,
})

# ══════════════════════════════════════════════════════════════════════════
# As variáveis, por família. (rótulo, família, formato, tarja)
# ══════════════════════════════════════════════════════════════════════════
VARIAVEIS = {
    # --- estrutura instalada -------------------------------------------
    "total_leitos":        ("Leitos totais", "Estrutura", "int", ""),
    "leitos_sus":          ("Leitos SUS", "Estrutura", "int", ""),
    "leitos_internacao":   ("Leitos de internação", "Estrutura", "int", ""),
    "uti_total":           ("Leitos de UTI (todos)", "Estrutura", "int", ""),
    "uti_sus":             ("Leitos de UTI SUS", "Estrutura", "int", ""),
    "share_uti":           ("UTI como % dos leitos", "Estrutura", "pct1", ""),
    "share_sus":           ("Leitos SUS como % do total", "Estrutura", "pct1", ""),
    # --- produção e casemix --------------------------------------------
    "qtde":                ("Saídas hospitalares", "Produção", "int", ""),
    "qtde_sem_covid":      ("Saídas, excluindo COVID", "Produção", "int", ""),
    "diarias_internacao":  ("Diárias de internação", "Produção", "int", ""),
    "diarias_uti":         ("Diárias de UTI", "Produção", "int", ""),
    "qtde_alta_complex":   ("Saídas de alta complexidade", "Produção", "int", ""),
    "pct_alta_complex":    ("Fração de alta complexidade", "Produção", "prop", ""),
    "saidas_por_leito":    ("Saídas por leito SUS", "Produção", "f1", ""),
    # --- desfecho assistencial -----------------------------------------
    "mort_all":            ("Mortalidade geral", "Desfecho", "prop", ""),
    "tmp":                 ("TMP (dias)", "Desfecho", "f2", ""),
    # --- financeiro ------------------------------------------------------
    "custo_real":          ("Faturamento real por saída (R$)", "Financeiro", "int", ""),
    "valor_real_total":    ("Faturamento real total (R$ mil)", "Financeiro", "int", ""),
    "valor_por_leito":     ("Faturamento real por leito SUS (R$)", "Financeiro", "int", ""),
    # --- uso da capacidade ------------------------------------------------
    "ocupacao_internacao": ("Ocupação de internação (%)", "Uso", "f1",
                            "conflaciona nível e superlotação (R1/R6)"),
    "ocup_int_ate100":     ("Ocupação de internação <= 100 (%)", "Uso", "f1", ""),
    "pct_anos_superlot":   ("% de anos em superlotação", "Uso", "f1", ""),
    "ocupacao_uti_valida": ("Ocupação de UTI (%)", "Uso", "f1",
                            "indefinida onde uti_sus = 0; em E1 só o piscar (R7)"),
    # --- complexidade -----------------------------------------------------
    "complexidade_estrutural": ("Complexidade Barcelona (escore)", "Complexidade", "f1", ""),
    "faixa_barcelona":     ("Faixa Barcelona", "Complexidade", "f1", ""),
    "complexidade_pond_mort": ("Complexidade ponderada por mortalidade",
                               "Complexidade", "f1",
                               "TARJADA: construída com mortalidade, circular"),
    # --- pandemia ----------------------------------------------------------
    "pct_covid":           ("% de saídas por COVID (2020-21)", "Pandemia", "f1", ""),
}

# O corte em E1/E2/E3 é construído a partir da MEDIANA de `uti_sus` e da
# `faixa_barcelona`. Um eta² alto nessas variáveis, e nas que são consequência
# aritmética direta delas, NÃO é achado: é a definição do corte reaparecendo.
# Marcá-las é o que separa o ranking de um argumento circular.
DEFINICIONAL = {
    "faixa_barcelona":         "define o corte (E3 é faixa >= 4)",
    "complexidade_estrutural": "define o corte (a faixa é o seu binning)",
    "uti_sus":                 "define o corte (E1 é mediana zero)",
    "uti_total":               "consequência direta do corte de UTI",
    "share_uti":               "consequência direta do corte de UTI",
    "diarias_uti":             "consequência direta do corte de UTI",
    "ocupacao_uti_valida":     "só existe onde o corte já separou",
}

EXCLUIDAS = {
    "mort_sem_excl": "mortalidade ajustada, retirada do documento em A1 "
                     "(Spearman 1,000 com a mortalidade geral)",
    "pont_barcelona": "idêntica a complexidade_estrutural (conferido: iguais)",
    "dias_perm": "idêntica a diarias_internacao (conferido: iguais)",
    "*_com_covid": "o documento usa sempre as versões que excluem COVID",
    "n_linhas_*": "contadores de linha da extração, não medem hospital",
    "cnes / ano / municipio / cod_ibge / nome_fantasia": "identificadores",
    "estrato* / faixa_mediana / uti_sus_mediana": "definem o próprio corte",
    "class_assistencial / modelo_gestao_proxy / porte_hospital": "categóricas, "
        "entram como eixo de cruzamento e não como métrica",
}


def cab(t):
    print("\n" + "=" * 74)
    print(t)
    print("=" * 74)


def _tab(df, nome, index=True):
    df.to_csv(PASTA_TAB / nome, index=index, encoding="utf-8-sig")
    print(f"  [TAB] {nome}")


def _salvar(fig, nome):
    fig.savefig(PASTA_FIG / nome, dpi=150, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print(f"  [FIG] {nome}")


def _fatores_ipca():
    anos, acum, indice = sorted(IPCA_ANUAL), 1.0, {}
    for a in anos:
        acum *= 1 + IPCA_ANUAL[a] / 100
        indice[a] = acum
    return {a: indice[anos[-1]] / indice[a] for a in anos}


# ══════════════════════════════════════════════════════════════════════════
# 1. CARGA E DERIVADAS
# ══════════════════════════════════════════════════════════════════════════

def carregar():
    p = pd.read_csv(PAINEL_IN, encoding="utf-8-sig")
    assert len(p) == 3179 and p["cnes"].nunique() == 289, "painel inesperado"
    fixo = p.groupby("cnes")["estrato"].nunique()
    assert (fixo == 1).all(), "o estrato NÃO é fixo por CNES; o teste em CNES cai"

    fator = _fatores_ipca()
    p["custo_real"] = p["custo_saida"] * p["ano"].map(fator)
    p["valor_real_total"] = p["valor_sem_covid"] * p["ano"].map(fator) / 1000

    leitos = p["leitos_sus"].replace(0, np.nan)
    p["saidas_por_leito"] = p["qtde_sem_covid"] / leitos
    p["valor_por_leito"] = p["valor_real_total"] * 1000 / leitos
    tot = p["total_leitos"].replace(0, np.nan)
    p["share_uti"] = 100 * p["uti_total"] / tot
    p["share_sus"] = 100 * p["leitos_sus"] / tot

    # R1/R6: as duas metades da ocupação de internação, separadas
    p["ocup_int_ate100"] = p["ocupacao_internacao"].where(
        p["ocupacao_internacao"] <= 100)
    p["superlotado"] = (p["ocupacao_internacao"] > 100).astype(float)
    p["pct_anos_superlot"] = 100 * p["superlotado"]

    p["pct_covid"] = np.where(p["ano"].isin([2020, 2021]),
                              100 * p["qtde_covid"] / p["qtde"].replace(0, np.nan),
                              np.nan)

    print(f"painel: {len(p)} obs, {p['cnes'].nunique()} CNES, "
          f"anos {p['ano'].min()}-{p['ano'].max()}")
    print("CNES por estrato: "
          + ", ".join(f"{e} {(p.drop_duplicates('cnes')['estrato'] == e).sum()}"
                      for e in ESTRATOS))
    return p


def resumo_cnes(p):
    """Uma linha por hospital: mediana dos onze anos de cada variável.
    É a unidade em que o estrato é definido e em que ele pode ser testado."""
    cols = [c for c in VARIAVEIS if c in p.columns]
    g = p.groupby("cnes")[cols].median()
    g["estrato"] = p.drop_duplicates("cnes").set_index("cnes")["estrato"]
    g["categoria"] = (p.groupby("cnes")["modelo_gestao_proxy"]
                      .agg(lambda s: s.mode().iloc[0]))
    return g


# ══════════════════════════════════════════════════════════════════════════
# 2. TABELAS
# ══════════════════════════════════════════════════════════════════════════

def dicionario():
    cab("0. Dicionário: o que entrou e o que ficou de fora, com o motivo")
    linhas = [{"variavel": v, "rotulo": r, "familia": f,
               "situacao": ("incluída, DEFINICIONAL" if v in DEFINICIONAL
                            else "incluída"),
               "observacao": DEFINICIONAL.get(v) or t}
              for v, (r, f, _, t) in VARIAVEIS.items()]
    linhas += [{"variavel": v, "rotulo": "", "familia": "",
                "situacao": "excluída", "observacao": m}
               for v, m in EXCLUIDAS.items()]
    tab = pd.DataFrame(linhas)
    _tab(tab, "tabSEG_20_dicionario_variaveis.csv", index=False)
    print(f"  {len(VARIAVEIS)} variáveis incluídas, {len(EXCLUIDAS)} grupos "
          f"excluídos com motivo registrado")
    return tab


def por_estrato(dados, unidade, nome_arq):
    """Descritiva de cada variável dentro de cada estrato."""
    linhas = []
    for v, (rot, fam, _, tarja) in VARIAVEIS.items():
        if v not in dados.columns:
            continue
        for e in ESTRATOS:
            x = dados.loc[dados["estrato"] == e, v].dropna()
            n_c = (dados.loc[dados["estrato"] == e, v].notna()
                   .groupby(dados["cnes"] if "cnes" in dados else dados.index)
                   .any().sum()) if unidade == "hospital-ano" else len(x)
            linhas.append({
                "familia": fam, "variavel": v, "rotulo": rot, "estrato": e,
                "n": len(x), "n_cnes": int(n_c),
                "media": x.mean() if len(x) else np.nan,
                "dp": x.std() if len(x) else np.nan,
                "p25": x.quantile(.25) if len(x) else np.nan,
                "mediana": x.median() if len(x) else np.nan,
                "p75": x.quantile(.75) if len(x) else np.nan,
                "tarja": (TARJA_N if n_c < PISO_CNES else "") + (
                    (" " + tarja) if tarja else ""),
            })
    tab = pd.DataFrame(linhas).round(4)
    _tab(tab, nome_arq, index=False)
    return tab


def testar(cnes_df):
    """Kruskal-Wallis entre os três estratos e eta² (parcela da variância
    entre hospitais explicada pelo estrato). Unidade: CNES."""
    cab("3. O estrato explica quanto? Teste e tamanho de efeito, em CNES")
    linhas = []
    for v, (rot, fam, _, tarja) in VARIAVEIS.items():
        if v not in cnes_df.columns:
            continue
        grupos = [cnes_df.loc[cnes_df["estrato"] == e, v].dropna().to_numpy()
                  for e in ESTRATOS]
        n_ok = [g for g in grupos if len(g) >= 3]
        if len(n_ok) < 2:
            continue
        H, p = stats.kruskal(*n_ok)
        todos = np.concatenate(n_ok)
        # eta²: variância entre médias de estrato / variância total
        gm = todos.mean()
        ss_b = sum(len(g) * (g.mean() - gm) ** 2 for g in n_ok)
        ss_t = ((todos - gm) ** 2).sum()
        eta2 = ss_b / ss_t if ss_t > 0 else np.nan
        med = {e: (cnes_df.loc[cnes_df["estrato"] == e, v].median())
               for e in ESTRATOS}
        vals = [med[e] for e in ESTRATOS if pd.notna(med[e])]
        mono = ("crescente" if vals == sorted(vals)
                else "decrescente" if vals == sorted(vals, reverse=True)
                else "não ordena")
        # pares, com correção de Holm sobre os três
        pares, ps = [], []
        for a, b in (("E1", "E2"), ("E2", "E3"), ("E1", "E3")):
            xa = cnes_df.loc[cnes_df["estrato"] == a, v].dropna()
            xb = cnes_df.loc[cnes_df["estrato"] == b, v].dropna()
            if len(xa) >= 3 and len(xb) >= 3:
                pares.append(f"{a}x{b}")
                ps.append(stats.mannwhitneyu(xa, xb).pvalue)
        holm = {}
        if ps:
            ordem = np.argsort(ps)
            ajust = np.empty(len(ps))
            corrente = 0.0
            for i, k in enumerate(ordem):
                corrente = max(corrente, min(1.0, ps[k] * (len(ps) - i)))
                ajust[k] = corrente
            holm = dict(zip(pares, ajust))
        linhas.append({
            "familia": fam, "variavel": v, "rotulo": rot,
            "n_cnes": int(sum(len(g) for g in n_ok)),
            "mediana_E1": med["E1"], "mediana_E2": med["E2"],
            "mediana_E3": med["E3"], "ordena": mono,
            "kruskal_H": H, "kruskal_p": p, "eta2": eta2,
            "p_E1xE2": holm.get("E1xE2", np.nan),
            "p_E2xE3": holm.get("E2xE3", np.nan),
            "p_E1xE3": holm.get("E1xE3", np.nan),
            "definicional": DEFINICIONAL.get(v, ""),
            "tarja": tarja,
        })
    tab = pd.DataFrame(linhas).sort_values("eta2", ascending=False).round(6)
    _tab(tab, "tabSEG_23_teste_estratos.csv", index=False)
    print(f"\n  {'variável':<40} {'eta2':>7} {'ordena':<12} {'p (KW)':>10}  def.")
    for _, r in tab.iterrows():
        print(f"  {r['rotulo'][:39]:<40} {r['eta2']:>7.3f} "
              f"{r['ordena']:<12} {r['kruskal_p']:>10.2e}  "
              f"{'DEF' if r['definicional'] else ''}")
    n_def = (tab['definicional'] != '').sum()
    print(f"\n  {n_def} das {len(tab)} variáveis são definicionais e ficam "
          f"fora de qualquer leitura de achado.")
    return tab


def por_ano(p):
    cab("4. Estrato por ano: as trajetórias se aproximam ou se afastam?")
    chave = ["mort_all", "tmp", "custo_real", "ocupacao_internacao",
             "saidas_por_leito", "pct_alta_complex"]
    g = (p.groupby(["ano", "estrato"])[chave].median().round(4)
         .reset_index())
    _tab(g, "tabSEG_24_estratos_por_ano.csv", index=False)
    return g


def por_categoria(p):
    """Estrato x categoria de gestão, com a tarja de R2 na célula proibida."""
    cab("5. Estrato x categoria de gestão")
    chave = ["mort_all", "tmp", "custo_real", "ocupacao_internacao",
             "saidas_por_leito", "pct_alta_complex", "ocupacao_uti_valida"]
    linhas = []
    for e in ESTRATOS:
        for cat in CATEGORIAS:
            sub = p[(p["estrato"] == e) & (p["modelo_gestao_proxy"] == cat)]
            n_c = sub["cnes"].nunique()
            for v in chave:
                x = sub[v].dropna()
                t = TARJA_N if n_c < PISO_CNES else ""
                if e == "E3" and v == "mort_all" and cat in ("OSS", "Direta"):
                    t = (t + " R2: par OSS x Direta NÃO citável").strip()
                linhas.append({
                    "estrato": e, "categoria": cat, "variavel": v,
                    "n_cnes": n_c, "n_hospital_ano": len(x),
                    "mediana": x.median() if len(x) else np.nan,
                    "p25": x.quantile(.25) if len(x) else np.nan,
                    "p75": x.quantile(.75) if len(x) else np.nan,
                    "tarja": t})
    tab = pd.DataFrame(linhas).round(4)
    _tab(tab, "tabSEG_25_estratos_x_categoria.csv", index=False)
    return tab


# ══════════════════════════════════════════════════════════════════════════
# 3. FIGURAS
# ══════════════════════════════════════════════════════════════════════════

def fig_eta2(teste):
    t = teste.dropna(subset=["eta2"]).sort_values("eta2")
    ehdef = t["definicional"] != ""
    fig, ax = plt.subplots(figsize=(8.6, 8.6))
    cores = ["#e1e0d9" if d else
             "#0d366b" if p < .001 else "#5598e7" if p < .05 else "#c3c2b7"
             for p, d in zip(t["kruskal_p"], ehdef)]
    rotulos = [f"{r} ▸" if d else r for r, d in zip(t["rotulo"], ehdef)]
    barras = ax.barh(rotulos, t["eta2"] * 100, color=cores,
                     edgecolor="white", lw=.5,
                     hatch=["///" if d else "" for d in ehdef])
    ax.bar_label(barras, labels=[f"{v * 100:.0f}%" for v in t["eta2"]],
                 fontsize=9.5, padding=3, color="#52514e")
    for rot, d in zip(ax.get_yticklabels(), ehdef):
        if d:
            rot.set_color(COR_MUTED)
            rot.set_style("italic")
    ax.set_xlabel("Variância entre hospitais explicada pelo estrato (%)")
    ax.set_title("O que o perfil de complexidade explica, e o que não explica\n"
                 "(um ponto por hospital, mediana dos onze anos)",
                 fontsize=11.5)
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, min(100, t["eta2"].max() * 100 * 1.20))
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(facecolor="#e1e0d9", hatch="///", edgecolor="white",
              label="▸ definicional: o corte é feito com ela"),
        Patch(color="#0d366b", label="p < 0,001"),
        Patch(color="#5598e7", label="p < 0,05"),
        Patch(color="#c3c2b7", label="não distingue os estratos")],
        fontsize=9.2, loc="lower right", frameon=False)
    fig.tight_layout()
    _salvar(fig, "figSEG_11_eta2_ranking.png")


def fig_perfil(cnes_df, teste):
    """Os doze contrastes NÃO DEFINICIONAIS de maior eta², um painel cada.
    As variáveis que constroem o corte ficam de fora: mostrá-las aqui seria
    ilustrar a definição e chamar isso de achado."""
    top = (teste.dropna(subset=["eta2"])
           .loc[teste["definicional"] == ""].head(12))
    fig, axes = plt.subplots(3, 4, figsize=(15, 9.6))
    for ax, (_, r) in zip(axes.ravel(), top.iterrows()):
        v = r["variavel"]
        dados = [cnes_df.loc[cnes_df["estrato"] == e, v].dropna()
                 for e in ESTRATOS]
        bp = ax.boxplot(dados, patch_artist=True,
                        widths=.6, showfliers=False,
                        medianprops=dict(color="white", lw=1.6))
        ax.set_xticks(range(1, len(ESTRATOS) + 1), ESTRATOS)
        for caixa, e in zip(bp["boxes"], ESTRATOS):
            caixa.set(facecolor=COR_ESTRATO[e], edgecolor="white", lw=.8)
        for i, d in enumerate(dados, start=1):
            if len(d):
                ax.scatter(np.random.default_rng(20260729 + i).normal(i, .05, len(d)),
                           d, s=4, color="#52514e", alpha=.28, zorder=3)
        marca = "  ⚑ tarjada" if r["tarja"] else ""
        ax.set_title(f"{r['rotulo'][:42]}{marca}\n$\\eta^2$ = {r['eta2']:.2f}",
                     fontsize=10,
                     color=COR_MUTED if r["tarja"] else "#0b0b0b")
        ax.grid(axis="x", visible=False)
    for ax in axes.ravel()[len(top):]:
        ax.axis("off")
    fig.suptitle("Perfil dos três estratos nas doze variáveis que eles mais "
                 "separam (um ponto por hospital)", fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, .965))
    _salvar(fig, "figSEG_10_perfil_estratos.png")


def fig_estrutura_uso(cnes_df, p):
    """Três leituras do mesmo corte, na tira de três painéis e uma a uma.

    Os três painéis respondem perguntas independentes e sempre foram lidos um
    de cada vez; juntos numa tira de 14 polegadas, reduzida à largura da
    mancha, cada um sobrava com pouco mais de cinco centímetros e os rótulos
    dos eixos ficavam ilegíveis. Desde 01/08/2026 a mesma função de desenho
    alimenta as duas versões: a tira, que continua servindo à visão de
    conjunto, e um arquivo por painel, que é o que o relatório publica.
    """
    def _escala(ax):
        for e in ESTRATOS:
            d = cnes_df[cnes_df["estrato"] == e]
            ax.scatter(d["total_leitos"], d["share_uti"], s=26,
                       color=COR_ESTRATO[e], alpha=.75, marker=MARCADOR[e],
                       edgecolor="white", lw=.4, label=e)
        ax.set_xscale("log")
        ax.set_xlabel("Leitos totais (escala log)")
        ax.set_ylabel("UTI como % dos leitos")
        ax.set_title("Escala e intensidade tecnológica")
        ax.legend(fontsize=9.5, frameon=False)

    def _duas_perguntas(ax):
        larg, pos = .26, np.arange(3)
        freq = [100 * p.loc[p["estrato"] == e, "superlotado"].mean()
                for e in ESTRATOS]
        nivel = [p.loc[p["estrato"] == e, "ocup_int_ate100"].median()
                 for e in ESTRATOS]
        bruta = [p.loc[p["estrato"] == e, "ocupacao_internacao"].median()
                 for e in ESTRATOS]
        for i, (serie, rot, cor) in enumerate([
                (bruta, "mediana bruta (conflaciona)", "#c3c2b7"),
                (nivel, "mediana com ocupação <= 100", "#0f9b8e"),
                (freq, "% de anos em superlotação", "#0d366b")]):
            b = ax.bar(pos + (i - 1) * larg, serie, larg, color=cor,
                       edgecolor="white", lw=.5, label=rot)
            ax.bar_label(b, labels=[f"{v:.0f}" for v in serie], fontsize=9,
                         padding=2, color="#52514e")
        ax.set_xticks(pos, ESTRATOS)
        ax.set_title("A ocupação de internação são duas perguntas")
        ax.legend(fontsize=8.8, frameon=False, loc="upper left")
        ax.grid(axis="x", visible=False)

    def _giro(ax):
        for e in ESTRATOS:
            d = cnes_df[cnes_df["estrato"] == e]
            ax.scatter(d["saidas_por_leito"], d["tmp"], s=26,
                       color=COR_ESTRATO[e], alpha=.75, marker=MARCADOR[e],
                       edgecolor="white", lw=.4, label=e)
        ax.set_xlabel("Saídas por leito SUS")
        ax.set_ylabel("TMP (dias)")
        ax.set_title("Giro contra permanência")
        ax.legend(fontsize=9.5, frameon=False)

    paineis = [("escala", _escala), ("duas_perguntas", _duas_perguntas),
               ("giro", _giro)]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))
    for ax, (_, desenhar) in zip(axes, paineis):
        desenhar(ax)
    fig.tight_layout()
    _salvar(fig, "figSEG_12_estrutura_uso.png")

    for nome, desenhar in paineis:
        fig, ax = plt.subplots(figsize=(8.6, 5.4))
        desenhar(ax)
        ax.title.set_fontsize(13)
        fig.tight_layout()
        _salvar(fig, f"figSEG_12_{nome}.png")


def fig_por_ano(g):
    chave = [("mort_all", "Mortalidade geral"), ("tmp", "TMP (dias)"),
             ("custo_real", "Faturamento real por saída (R$)"),
             ("ocupacao_internacao", "Ocupação de internação (%)"),
             ("saidas_por_leito", "Saídas por leito SUS"),
             ("pct_alta_complex", "Fração de alta complexidade")]
    fig, axes = plt.subplots(2, 3, figsize=(14.5, 7.2))
    for ax, (v, rot) in zip(axes.ravel(), chave):
        for e in ESTRATOS:
            d = g[g["estrato"] == e]
            ax.plot(d["ano"], d[v], marker=MARCADOR[e], ms=4, lw=1.7,
                    color=COR_ESTRATO[e], label=e)
        ax.axvspan(2019.5, 2021.5, color="#f0efec", zorder=0)
        ax.set_title(rot, fontsize=10.5)
        ax.set_xticks([2015, 2018, 2021, 2025])
    axes.ravel()[0].legend(fontsize=9.5, frameon=False)
    fig.suptitle("Os três estratos ano a ano (medianas; faixa cinza é o "
                 "biênio pandêmico)", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, .955))
    _salvar(fig, "figSEG_13_estratos_por_ano.png")


# ══════════════════════════════════════════════════════════════════════════
def main():
    PASTA_FIG.mkdir(parents=True, exist_ok=True)
    p = carregar()
    dicionario()

    cab("1. Descritiva em hospital-ano (continuidade com a tabela publicada)")
    por_estrato(p, "hospital-ano", "tabSEG_21_estratos_hospital_ano.csv")

    cab("2. Descritiva em CNES (unidade em que o estrato é definido)")
    cnes_df = resumo_cnes(p).reset_index()
    por_estrato(cnes_df, "cnes", "tabSEG_22_estratos_cnes.csv")

    teste = testar(cnes_df)
    g_ano = por_ano(p)
    por_categoria(p)

    cab("6. Figuras")
    fig_eta2(teste)
    fig_perfil(cnes_df, teste)
    fig_estrutura_uso(cnes_df, p)
    fig_por_ano(g_ano)

    cab("CONCLUÍDO")
    print("Tabelas tabSEG_20 a tabSEG_25 em analises/tabelas;")
    print("figuras figSEG_10 a figSEG_13 em analises/figuras_segmentacao.")


if __name__ == "__main__":
    main()
