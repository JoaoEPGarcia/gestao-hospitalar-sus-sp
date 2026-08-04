# -*- coding: utf-8 -*-
"""
Decomposição da LOTAÇÃO em TAXA DE OCUPAÇÃO e EXCESSO — Seção da segmentação.

Por que este script existe
--------------------------
O documento vinha chamando de "ocupação de internação" uma razão que pode
passar de 100%, e uma taxa de ocupação, por definição, não pode: a fração de
leito-dia efetivamente ocupada está presa ao intervalo [0, 1]. O que a
variável `ocupacao_internacao` mede é a **lotação**, isto é, leito-dia
demandado por leito-dia habilitado, que é um índice sem teto.

Este script formaliza a distinção e mede as três quantidades separadamente:

    lotação            ell   = diarias_internacao / (365 * leitos_sus)
    taxa de ocupação   tau   = min(ell, 1)
    excesso            exc   = max(ell - 1, 0)
    superlotação       sup   = 1{ell > 1}

com a identidade exata  ell = tau + exc,  verificada abaixo (aborta se falhar).

A identidade é aditiva na MÉDIA e não na mediana, e isso é o ponto
metodológico do script: só a média decompõe o contraste entre redes em
"quanto é nível de ocupação" e "quanto é excesso". A mediana bruta apenas
CONFLACIONA as duas coisas, que é a restrição R1/R6 já registrada.

NADA aqui muda um número do documento. `ocupacao_internacao` continua sendo
100*ell, e as três colunas que a Seção já imprimia (mediana bruta, mediana
condicional a <= 100, % de anos > 100) são reproduzidas idênticas antes de
qualquer coisa nova ser calculada — é a trava de reprodução da regra 7.

Restrições herdadas
-------------------
  R1/R6  a mediana bruta conflaciona frequência de superlotação com nível de
         ocupação; as três colunas saem sempre separadas.
  --     o Privado (3 CNES) nunca é interpretado; entra só como registro e
         fica fora das figuras por categoria.
  --     células com menos de 10 hospitais-ano saem marcadas [n<10].

Saídas
------
  analises/tabelas/tabSEG_26_decomposicao_lotacao.csv
  analises/tabelas/tabSEG_27_persistencia_superlotacao.csv
  analises/figuras_segmentacao/figSEG_14_decomposicao_lotacao.png
  analises/figuras_segmentacao/figSEG_15_lotacao_por_ano.png
  analises/figuras_segmentacao/figSEG_16_profundidade_excesso.png
  analises/figuras_segmentacao/figSEG_17_persistencia_superlotacao.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PAINEL_IN = RAIZ / "analises" / "painel_segmentado.csv"
PASTA_TAB = RAIZ / "analises" / "tabelas"
PASTA_FIG = RAIZ / "analises" / "figuras_segmentacao"

ESTRATOS = ["E1", "E2", "E3"]
# ordem fixa de leitura: as duas redes que a pesquisa compara primeiro
CATS = ["Direta", "OSS", "Público Municipal", "Filantrópico"]
PISO_N = 10

# paleta do documento (reproduzida de analise_exploratoria.py para não
# importar aquele script, que roda o pipeline inteiro ao ser carregado)
CORES_CAT = {"Direta": "#0d366b", "OSS": "#0f9b8e",
             "Público Municipal": "#5598e7", "Filantrópico": "#6a51c7",
             "Privado": "#898781"}
MARCADORES = {"Direta": "o", "OSS": "s", "Público Municipal": "^",
              "Filantrópico": "D", "Privado": "X"}
COR_ESTRATO = {"E1": "#5598e7", "E2": "#0f9b8e", "E3": "#0d366b"}
COR_GRADE, COR_EIXO, COR_MUTED = "#e1e0d9", "#c3c2b7", "#898781"
COR_EXCESSO, COR_EVENTO = "#c0562f", "#52514e"

plt.rcParams.update({
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": COR_EIXO, "axes.labelcolor": "#0b0b0b",
    "axes.grid": True, "grid.color": COR_GRADE, "grid.linewidth": .6,
    "xtick.color": COR_MUTED, "ytick.color": COR_MUTED,
    "font.size": 10.5, "axes.titlesize": 11, "figure.titlesize": 11.5,
})


def _titulo(t):
    print("\n" + "=" * 74)
    print(t)
    print("=" * 74)


def _salvar(fig, nome):
    fig.savefig(PASTA_FIG / nome, dpi=150, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print(f"  [FIG] {nome}")


def _tab(df, nome, index=False):
    df.to_csv(PASTA_TAB / nome, index=index, encoding="utf-8-sig")
    print(f"  [TAB] {nome}")


# ══════════════════════════════════════════════════════════════════════════
# 1. As definições, e a trava de reprodução
# ══════════════════════════════════════════════════════════════════════════
def carregar():
    d = pd.read_csv(PAINEL_IN)

    # a identidade declarada no documento, conferida antes de tudo
    calc = 100 * d["diarias_internacao"] / (d["leitos_sus"] * 365)
    desvio = float(np.nanmax(np.abs(calc - d["ocupacao_internacao"])))
    assert desvio < 1e-9, f"ocupacao_internacao não bate com a identidade ({desvio})"

    d["ell"] = d["ocupacao_internacao"] / 100.0        # lotação
    d["tau"] = d["ell"].clip(upper=1.0)                # taxa de ocupação
    d["exc"] = (d["ell"] - 1.0).clip(lower=0.0)        # excesso
    d["sup"] = (d["ell"] > 1.0).astype(int)            # superlotação

    # ell = tau + exc, exata por construção; conferida mesmo assim
    resid = float(np.nanmax(np.abs(d["ell"] - (d["tau"] + d["exc"]))))
    assert resid == 0.0, f"identidade ell = tau + exc violada ({resid})"

    print(f"painel: {len(d)} hospitais-ano, {d.cnes.nunique()} CNES")
    print(f"identidade ocupacao_internacao: desvio máximo {desvio:.2e}")
    print(f"identidade ell = tau + exc:     desvio máximo {resid:.2e}")
    return d


def trava_reproducao(d):
    """As três colunas que a Seção já imprime, recalculadas aqui."""
    _titulo("TRAVA DE REPRODUÇÃO — números já impressos no documento")
    print(f"% do painel acima de 100%: {100 * d.sup.mean():.1f}  (impresso: 15,5)")
    for est in ESTRATOS:
        s = d[d.estrato == est]
        print(f"  {est}: bruta {s.ocupacao_internacao.median():5.1f} | "
              f"cond<=100 {s.loc[s.sup == 0, 'ocupacao_internacao'].median():5.1f} | "
              f"freq {100 * s.sup.mean():4.1f}%")
    print("  (impressos: 41/41/1, 66/63/9, 90/83/28)")
    e3 = d[d.estrato == "E3"]
    print("E3 por categoria — freq | cond<=100 | bruta:")
    for c in CATS:
        s = e3[e3.modelo_gestao_proxy == c]
        print(f"  {c:20s} {100 * s.sup.mean():5.1f} | "
              f"{s.loc[s.sup == 0, 'ocupacao_internacao'].median():5.1f} | "
              f"{s.ocupacao_internacao.median():5.1f}")


# ══════════════════════════════════════════════════════════════════════════
# 2. A decomposição, por estrato e por categoria
# ══════════════════════════════════════════════════════════════════════════
def decomposicao(d):
    _titulo("DECOMPOSIÇÃO  ell = tau + exc  (médias, onde a identidade é aditiva)")
    linhas = []
    for est in ESTRATOS:
        for c in CATS + ["Privado"]:
            s = d[(d.estrato == est) & (d.modelo_gestao_proxy == c)]
            if len(s) == 0:
                continue
            linhas.append(dict(
                estrato=est, categoria=c, n_obs=len(s), n_cnes=s.cnes.nunique(),
                lotacao_media=100 * s.ell.mean(),
                ocupacao_media=100 * s.tau.mean(),
                excesso_medio=100 * s.exc.mean(),
                freq_superlotacao=100 * s.sup.mean(),
                mediana_bruta=s.ocupacao_internacao.median(),
                mediana_cond_ate100=s.loc[s.sup == 0, "ocupacao_internacao"].median(),
                lotacao_mediana_se_superlota=(
                    100 * s.loc[s.sup == 1, "ell"].median() if s.sup.sum() else np.nan),
                tarja=TARJA if len(s) < PISO_N else "",
            ))
    tabela = pd.DataFrame(linhas).round(2)
    _tab(tabela, "tabSEG_26_decomposicao_lotacao.csv")

    e3 = d[d.estrato == "E3"]
    o = e3[e3.modelo_gestao_proxy == "OSS"]
    r = e3[e3.modelo_gestao_proxy == "Direta"]
    g_ell = 100 * (o.ell.mean() - r.ell.mean())
    g_tau = 100 * (o.tau.mean() - r.tau.mean())
    g_exc = 100 * (o.exc.mean() - r.exc.mean())
    print(f"\nE3, OSS menos Direta:")
    print(f"  lotação          {g_ell:6.1f} pontos")
    print(f"  = taxa ocupação  {g_tau:6.1f}  ({100 * g_tau / g_ell:.0f}% do total)")
    print(f"  + excesso        {g_exc:6.1f}  ({100 * g_exc / g_ell:.0f}% do total)")

    # a mesma conta na mediana, que NÃO decompõe: só para mostrar o contraste
    gb = o.ocupacao_internacao.median() - r.ocupacao_internacao.median()
    gc = (o.loc[o.sup == 0, "ocupacao_internacao"].median()
          - r.loc[r.sup == 0, "ocupacao_internacao"].median())
    print(f"  na mediana: bruta {gb:.1f} contra condicional {gc:.1f} "
          f"({100 * (gb - gc) / gb:.0f}% do contraste bruto é conflação)")
    return tabela, dict(g_ell=g_ell, g_tau=g_tau, g_exc=g_exc, gb=gb, gc=gc)


# ══════════════════════════════════════════════════════════════════════════
# 3. Profundidade do excesso e persistência
# ══════════════════════════════════════════════════════════════════════════
def profundidade(d):
    _titulo("PROFUNDIDADE — quão acima de 100 vai, condicional a passar de 100")
    sup = d[d.sup == 1]
    print(f"painel: n={len(sup)}, mediana da lotação {100 * sup.ell.median():.1f}, "
          f"p90 {100 * sup.ell.quantile(.9):.1f}")
    for est in ["E2", "E3"]:
        print(f"-- {est} --")
        for c in CATS:
            s = d[(d.estrato == est) & (d.modelo_gestao_proxy == c) & (d.sup == 1)]
            marca = TARJA if len(s) < PISO_N else ""
            med = 100 * s.ell.median() if len(s) else np.nan
            p90 = 100 * s.ell.quantile(.9) if len(s) else np.nan
            print(f"   {c:20s} n={len(s):4d}  mediana={med:6.1f}  p90={p90:6.1f} {marca}")


def persistencia(d):
    _titulo("PERSISTÊNCIA — quantos anos cada hospital passa acima de 100")
    por_cnes = d.groupby("cnes").agg(
        anos_sup=("sup", "sum"),
        estrato=("estrato", "first"),
        categoria=("modelo_gestao_proxy",
                   lambda x: x.mode().iat[0]),
    ).reset_index()
    _tab(por_cnes, "tabSEG_27_persistencia_superlotacao.csv")

    dist = por_cnes.anos_sup.value_counts().sort_index()
    afetados = int((por_cnes.anos_sup >= 1).sum())
    print(f"CNES com ao menos um ano acima de 100: {afetados} de {len(por_cnes)}")
    print(f"  com 1 ou 2 anos: {int(por_cnes.anos_sup.isin([1, 2]).sum())}")
    print(f"  nos onze anos:   {int((por_cnes.anos_sup == 11).sum())}")
    print(f"  mediana de anos entre os afetados: "
          f"{por_cnes.loc[por_cnes.anos_sup >= 1, 'anos_sup'].median():.1f}")
    print("\npor categoria:")
    for c in CATS:
        s = por_cnes[por_cnes.categoria == c]
        af = s[s.anos_sup >= 1]
        print(f"  {c:20s} {len(af):3d}/{len(s):3d} hospitais "
              f"({100 * len(af) / len(s):4.1f}%)  mediana de anos "
              f"{af.anos_sup.median() if len(af) else np.nan:.1f}")
    return por_cnes, dist


# ══════════════════════════════════════════════════════════════════════════
# 4. As figuras
# ══════════════════════════════════════════════════════════════════════════
def fig14(d, gaps):
    fig, axes = plt.subplots(1, 2, figsize=(13.6, 4.6))

    # (a) a distribuição da lotação, com a linha dos 100%
    ax = axes[0]
    v = 100 * d.ell.dropna()
    corte = 250
    bins = np.arange(0, corte + 5, 5)
    ax.hist(v[v <= 100], bins=bins,
            color=COR_ESTRATO["E2"], alpha=.55, edgecolor="white", lw=.5,
            label="lotação $\\leq$ 100: a taxa de ocupação")
    ax.hist(v[v > 100].clip(upper=corte), bins=bins,
            color=COR_EXCESSO, alpha=.85, edgecolor="white", lw=.5,
            label="lotação > 100: superlotação")
    ax.axvline(100, color=COR_EVENTO, lw=1.4, ls="--")
    ax.annotate(f"{100 * d.sup.mean():.1f}% das observações",
                xy=(104, ax.get_ylim()[1] * .78), fontsize=9.5,
                color=COR_EXCESSO, fontweight="bold")
    ax.set_xlabel("Lotação $\\ell$ (%), aparada em 250 para a vista")
    ax.set_ylabel("Hospitais-ano")
    ax.set_title("(a) A lotação do painel, e onde ela deixa de ser taxa")
    ax.legend(frameon=False, fontsize=9)

    # (b) a identidade, em barras empilhadas, dentro de E3
    ax = axes[1]
    e3 = d[d.estrato == "E3"]
    xs = np.arange(len(CATS))
    tau = [100 * e3[e3.modelo_gestao_proxy == c].tau.mean() for c in CATS]
    exc = [100 * e3[e3.modelo_gestao_proxy == c].exc.mean() for c in CATS]
    frq = [100 * e3[e3.modelo_gestao_proxy == c].sup.mean() for c in CATS]
    ax.bar(xs, tau, .62, color=[CORES_CAT[c] for c in CATS], alpha=.85,
           label="taxa de ocupação $\\bar\\tau$")
    ax.bar(xs, exc, .62, bottom=tau, color=COR_EXCESSO, alpha=.9,
           label="excesso $\\bar e$")
    for x, t, e, f in zip(xs, tau, exc, frq):
        ax.text(x, t + e + 1.6, f"{t + e:.1f}", ha="center", fontsize=9.5,
                fontweight="bold")
        ax.text(x, 4, f"superlota\nem {f:.1f}%\ndos anos", ha="center",
                fontsize=8.2, color="white")
    ax.axhline(100, color=COR_EVENTO, lw=1.2, ls="--")
    ax.set_xticks(xs)
    ax.set_xticklabels([c.replace(" ", "\n") for c in CATS], fontsize=9)
    ax.set_ylabel("Média em E3 (%)")
    ax.set_ylim(0, 118)
    ax.set_title("(b) $\\bar\\ell = \\bar\\tau + \\bar e$, no estrato comparável")
    ax.legend(frameon=False, fontsize=9, loc="upper left")

    fig.suptitle("A lotação separada em taxa de ocupação e excesso", y=1.02)
    _salvar(fig, "figSEG_14_decomposicao_lotacao.png")


def fig15(d):
    e3 = d[d.estrato == "E3"]
    fig, axes = plt.subplots(1, 3, figsize=(14.6, 4.3))
    séries = [("ell", "Lotação média $\\bar\\ell$ (%)", "(a) A lotação, como o painel a mede"),
              ("tau", "Taxa de ocupação média $\\bar\\tau$ (%)", "(b) Só a ocupação, com teto em 100"),
              ("sup", "Anos em superlotação (%)", "(c) Só a frequência de superlotação")]
    for ax, (col, rot, tit) in zip(axes, séries):
        for c in CATS:
            g = (e3[e3.modelo_gestao_proxy == c]
                 .groupby("ano")[col].mean() * 100)
            ax.plot(g.index, g.values, color=CORES_CAT[c], lw=1.8,
                    marker=MARCADORES[c], ms=4.2, label=c)
        ax.axvspan(2019.5, 2021.5, color=COR_GRADE, alpha=.75, lw=0, zorder=0)
        ax.set_xlabel("Ano")
        ax.set_ylabel(rot)
        ax.set_title(tit, fontsize=10.4)
    maneiras, nomes = axes[0].get_legend_handles_labels()
    fig.legend(maneiras, nomes, ncol=4, frameon=False, fontsize=9.4,
               loc="lower center", bbox_to_anchor=(.5, -.08))
    fig.suptitle("As três leituras ano a ano, no estrato E3 "
                 "(faixa cinza: biênio pandêmico)", y=1.03)
    _salvar(fig, "figSEG_15_lotacao_por_ano.png")


def fig16(d):
    fig, axes = plt.subplots(1, 2, figsize=(13.6, 4.6))

    # (a) distribuição da lotação entre quem superlota, em E3
    ax = axes[0]
    dados, rotulos, cores = [], [], []
    for c in CATS:
        s = d[(d.estrato == "E3") & (d.modelo_gestao_proxy == c) & (d.sup == 1)]
        marca = f"\n[n={len(s)}" + (", tarjado]" if len(s) < PISO_N else "]")
        dados.append(100 * s.ell.values)
        rotulos.append(c.replace(" ", "\n") + marca)
        cores.append(CORES_CAT[c])
    bp = ax.boxplot(dados, patch_artist=True, widths=.55, showfliers=True,
                    flierprops=dict(marker=".", ms=3, mfc=COR_MUTED,
                                    mec="none", alpha=.6),
                    medianprops=dict(color="white", lw=1.6))
    for caixa, cor in zip(bp["boxes"], cores):
        caixa.set(facecolor=cor, edgecolor="white", lw=.8, alpha=.9)
    ax.axhline(100, color=COR_EVENTO, lw=1.2, ls="--")
    ax.set_xticklabels(rotulos, fontsize=8.6)
    ax.set_ylabel("Lotação nos anos em que passa de 100 (%)")
    ax.set_title("(a) Quando superlota, quanto superlota (E3)")

    # (b) frequência contra profundidade
    ax = axes[1]
    for est in ["E2", "E3"]:
        for c in CATS:
            s = d[(d.estrato == est) & (d.modelo_gestao_proxy == c)]
            sup = s[s.sup == 1]
            if len(sup) == 0:
                continue
            x, y = 100 * s.sup.mean(), 100 * sup.ell.median()
            ax.scatter(x, y, s=118 if est == "E3" else 62,
                       color=CORES_CAT[c], marker=MARCADORES[c],
                       alpha=.9 if est == "E3" else .45,
                       edgecolor="white", lw=.8, zorder=3)
            if est == "E3":
                ax.annotate(c, (x, y), textcoords="offset points",
                            xytext=(7, 5), fontsize=8.4, color=CORES_CAT[c])
    ax.set_xlim(0, 48)
    ax.set_xlabel("Frequência: % de hospitais-ano acima de 100")
    ax.set_ylabel("Profundidade: lotação mediana quando passa de 100 (%)")
    ax.set_title("(b) Frequência e profundidade são coisas distintas")
    ax.annotate("marca cheia e grande: E3\nmarca clara e pequena: E2",
                xy=(.02, .93), xycoords="axes fraction", fontsize=8.2,
                color=COR_MUTED, va="top")
    fig.suptitle("Superlotar mais vezes não é superlotar mais fundo", y=1.02)
    _salvar(fig, "figSEG_16_profundidade_excesso.png")


def fig17(por_cnes):
    fig, axes = plt.subplots(1, 2, figsize=(13.6, 4.4))

    # (a) quantos anos cada hospital passa acima de 100
    ax = axes[0]
    cont = por_cnes.anos_sup.value_counts().reindex(range(12), fill_value=0)
    cores = [COR_MUTED] + [COR_EXCESSO] * 11
    ax.bar(cont.index, cont.values, .74, color=cores, alpha=.85,
           edgecolor="white", lw=.6)
    for x, y in zip(cont.index, cont.values):
        if y:
            ax.text(x, y + 2.5, str(int(y)), ha="center", fontsize=8.6,
                    color=COR_MUTED)
    ax.set_xticks(range(12))
    ax.set_xlabel("Anos, dos onze, em que o hospital passa de 100")
    ax.set_ylabel("Hospitais (CNES)")
    ax.set_title("(a) A superlotação é episódica na maioria dos hospitais")

    # (b) alcance contra recorrência, por categoria
    ax = axes[1]
    for c in CATS:
        s = por_cnes[por_cnes.categoria == c]
        af = s[s.anos_sup >= 1]
        if len(af) == 0:
            continue
        x, y = 100 * len(af) / len(s), af.anos_sup.median()
        ax.scatter(x, y, s=130, color=CORES_CAT[c], marker=MARCADORES[c],
                   edgecolor="white", lw=.9, zorder=3)
        ax.annotate(f"{c}\n({len(af)} de {len(s)})", (x, y),
                    textcoords="offset points", xytext=(9, -4),
                    fontsize=8.4, color=CORES_CAT[c])
    ax.set_xlim(20, 90)
    ax.set_ylim(0, 7)
    ax.set_xlabel("Alcance: % dos hospitais da rede que superlotam alguma vez")
    ax.set_ylabel("Recorrência: mediana de anos, entre os que superlotam")
    ax.set_title("(b) Nas OSS é recorrente, não episódico")
    fig.suptitle("Quantos hospitais superlotam, e por quantos anos", y=1.03)
    _salvar(fig, "figSEG_17_persistencia_superlotacao.png")


TARJA = "[n<10]"


def main():
    PASTA_TAB.mkdir(parents=True, exist_ok=True)
    PASTA_FIG.mkdir(parents=True, exist_ok=True)
    d = carregar()
    trava_reproducao(d)
    _, gaps = decomposicao(d)
    profundidade(d)
    por_cnes, _ = persistencia(d)
    _titulo("FIGURAS")
    fig14(d, gaps)
    fig15(d)
    fig16(d)
    fig17(por_cnes)
    print("\nconcluído.")


if __name__ == "__main__":
    main()
