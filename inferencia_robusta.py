"""
inferencia_robusta.py
=====================
Fechamento inferencial da fase de estimação do painel de hospitais
SUS/SP (314 CNES, 2015 a 2025). Reforça a leitura do efeito de gestão,
que repousa em apenas 5 hospitais convertidos de Direta para OSS, com
métodos adequados a poucos tratados, e fecha a limitação distribucional
da ocupação de UTI registrada em analises/estimacao.md.

Blocos (iterativos; rodar um por vez ou todos):
  bootstrap   1a. Bootstrap selvagem por cluster (Rademacher, hipótese
                  nula imposta) para o efeito OSS nos modelos de efeitos
                  fixos de log custo real e log TMP
  permutacao  1b. Teste de permutação: 5 conversores falsos sorteados
                  entre os nunca tratados, com os anos reais de conversão
  cs          2a. Callaway e Sant'Anna com controles nunca tratados:
                  ATT por coorte e ano e agregação por tempo de evento,
                  comparados aos coeficientes do estudo TWFE
  sintetico   2b. Controle sintético de Sorocaba e do Pérola Byington
                  (pesos não negativos somando um, ajustados no período
                  anterior à conversão) com placebos em espaço
  uti         3.  Intensidade de UTI reestimada em GLM Gama com ligação
                  log e variante com corte mínimo de atividade, com
                  resíduos quantílicos comparados ao log OLS original

Reaproveita preparo, amostras e estilo de estimacao.py; erros padrão
agrupados por CNES onde há modelo paramétrico. Figuras novas continuam
em analises/figuras_estimacao (fig_est_06 a 08) e tabelas em
analises/tabelas (prefixo tab_est_).

USO: python inferencia_robusta.py [bootstrap|permutacao|cs|sintetico|uti|todos]
"""

import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from scipy.optimize import nnls

import estimacao as est

SEMENTE = 20260704
B_BOOT = 1999
B_PERM = 1999

ROT_VAR_SINT = {"mort_pp": ("Mortalidade geral (%)", "%"),
                "tmp": ("TMP (dias)", "dias"),
                "custo_real": ("Custo real por saída (R$ de 2025)", "R$")}


# ══════════════════════════════════════════════════════════════════════════════
# FERRAMENTAS: DEMEANING DUPLO E FWL COM CLUSTER
# ══════════════════════════════════════════════════════════════════════════════

def _demean_2w(x, c1, c2, tol=1e-10, itmax=300):
    """Remove alternadamente as médias dos dois grupos (efeitos fixos de
    hospital e de ano via projeção iterativa)."""
    x = np.asarray(x, dtype=float).copy()
    n1, n2 = np.bincount(c1), np.bincount(c2)
    for _ in range(itmax):
        m1 = np.bincount(c1, x) / n1
        x -= m1[c1]
        m2 = np.bincount(c2, x) / n2
        x -= m2[c2]
        if max(np.abs(m1).max(), np.abs(m2).max()) < tol:
            break
    return x


def _beta_t_cluster(ytil, dtil, cg):
    """Coeficiente FWL e estatística t com erros agrupados."""
    sdd = float(dtil @ dtil)
    beta = float(dtil @ ytil) / sdd
    u = ytil - beta * dtil
    S = np.bincount(cg, dtil * u)
    G = len(S)
    var = G / (G - 1) * float(S @ S) / sdd ** 2
    return beta, beta / np.sqrt(var), np.sqrt(var)


def _preparar_fwl(painel, alvo):
    """Amostra, códigos de grupo e vetores demeaned do desfecho e da
    dummy OSS para os dois modelos de efeitos fixos."""
    d = est.amostra_desfecho(painel)
    if alvo == "tmp":
        d = d[d["longa_perm"] == 0]
        y = np.log(d["tmp"].to_numpy())
    else:
        y = np.log(d["custo_real"].to_numpy())
    c1 = pd.factorize(d["cnes"])[0]
    c2 = pd.factorize(d["ano"])[0]
    ytil = _demean_2w(y, c1, c2)
    dtil = _demean_2w(d["d_oss"].to_numpy(), c1, c2)
    return d, c1, c2, ytil, dtil


# ══════════════════════════════════════════════════════════════════════════════
# 1a. BOOTSTRAP SELVAGEM POR CLUSTER
# ══════════════════════════════════════════════════════════════════════════════

def bloco_bootstrap(painel):
    print("\n" + "=" * 70)
    print(f"[1a] BOOTSTRAP SELVAGEM POR CLUSTER (Rademacher, B = {B_BOOT}, "
          "nula imposta)")
    print("=" * 70)
    rng = np.random.default_rng(SEMENTE)
    linhas = []
    for alvo, rotulo in [("custo_real", "Custo real por saída (log, EF)"),
                         ("tmp", "TMP (log, EF, sem longa permanência)")]:
        d, c1, c2, ytil, dtil = _preparar_fwl(painel, alvo)
        beta, t_obs, ep = _beta_t_cluster(ytil, dtil, c1)
        G = c1.max() + 1
        cont = 0
        for _ in range(B_BOOT):
            w = rng.choice([-1.0, 1.0], size=G)
            estrela = _demean_2w(w[c1] * ytil, c1, c2)
            _, t_b, _ = _beta_t_cluster(estrela, dtil, c1)
            cont += abs(t_b) >= abs(t_obs)
        p_boot = (1 + cont) / (B_BOOT + 1)
        p_normal = 2 * stats.norm.sf(abs(t_obs))
        print(f"  {rotulo}")
        print(f"    beta OSS {beta:+.4f} (EP cluster {ep:.4f}, "
              f"t = {t_obs:+.3f}); p normal {p_normal:.4f} vs "
              f"p bootstrap {p_boot:.4f}")
        linhas.append({"modelo": rotulo, "coef_oss": beta, "ep_cluster": ep,
                       "t": t_obs, "p_normal": p_normal,
                       "p_wild_bootstrap": p_boot, "B": B_BOOT})
    est._tab(pd.DataFrame(linhas).round(5),
             "tab_est_wild_bootstrap.csv", index=False)


# ══════════════════════════════════════════════════════════════════════════════
# 1b. TESTE DE PERMUTAÇÃO (CONVERSORES FALSOS)
# ══════════════════════════════════════════════════════════════════════════════

def bloco_permutacao(painel):
    print("\n" + "=" * 70)
    print(f"[1b] PERMUTAÇÃO: 5 conversores falsos, B = {B_PERM}")
    print("=" * 70)
    rng = np.random.default_rng(SEMENTE)
    anos_conv = np.array(sorted(est.CONVERSOES.values()))
    linhas = []
    for alvo, rotulo in [("custo_real", "Custo real por saída (log, EF)"),
                         ("tmp", "TMP (log, EF, sem longa permanência)")]:
        d, c1, c2, ytil, dtil = _preparar_fwl(painel, alvo)
        sdd = float(dtil @ dtil)
        beta = float(dtil @ ytil) / sdd
        cnes_cod = pd.factorize(d["cnes"])[0]
        cnes_vals = d["cnes"].to_numpy()
        ano_vals = d["ano"].to_numpy()
        pool = np.array(sorted(set(d["cnes"].unique())
                               - set(est.CONVERSOES)))
        betas_p = np.empty(B_PERM)
        for b in range(B_PERM):
            falsos = rng.choice(pool, size=5, replace=False)
            anos_b = rng.permutation(anos_conv)
            d_falso = np.zeros(len(d))
            for cn, ac in zip(falsos, anos_b):
                d_falso[(cnes_vals == cn) & (ano_vals >= ac)] = 1.0
            dtil_b = _demean_2w(d_falso, c1, c2)
            betas_p[b] = float(dtil_b @ ytil) / float(dtil_b @ dtil_b)
        p_perm = (1 + np.sum(np.abs(betas_p) >= abs(beta))) / (B_PERM + 1)
        print(f"  {rotulo}")
        print(f"    beta OSS real {beta:+.4f}; distribuição placebo com "
              f"desvio {betas_p.std():.4f}; p permutação {p_perm:.4f}")
        linhas.append({"modelo": rotulo, "coef_oss_real": beta,
                       "dp_placebos": betas_p.std(),
                       "p_permutacao": p_perm, "B": B_PERM})
    est._tab(pd.DataFrame(linhas).round(5),
             "tab_est_permutacao.csv", index=False)


# ══════════════════════════════════════════════════════════════════════════════
# 2a. CALLAWAY E SANT'ANNA COM CONTROLES NUNCA TRATADOS
# ══════════════════════════════════════════════════════════════════════════════

ALVOS_CS = [("mort_all", "pp", "Mortalidade geral", "p.p."),
            ("tmp", "log", "TMP", "log pontos"),
            ("custo_real", "log", "Custo real por saída", "log pontos"),
            ("pct_alta_complex", "pp", "Fração alta complexidade", "p.p."),
            ("ocupacao_internacao_w", "log", "Ocupação internação",
             "log pontos")]


def bloco_cs(painel):
    print("\n" + "=" * 70)
    print("[2a] CALLAWAY E SANT'ANNA: ATT(g,t) com nunca tratados e "
          "agregação por tempo de evento")
    print("=" * 70)
    coortes = {}
    for cn, ac in est.CONVERSOES.items():
        coortes.setdefault(ac, []).append(cn)
    twfe = pd.read_csv(est.base.PASTA_TABELAS / "tab_est_evento.csv",
                       encoding="utf-8-sig")
    twfe = twfe[twfe["amostra"] == "completa"]
    rot_bin = {0: "0", 1: "+1", 2: "+2", 3: "+3 ou depois"}

    linhas_att, linhas_agg = [], []
    series_fig = {}
    for col, escala, rotulo, unidade in ALVOS_CS:
        d = est.amostra_desfecho(painel)
        if col == "tmp":
            d = d[d["longa_perm"] == 0]
        d = d.copy()
        d["y"] = (d[col] * 100 if escala == "pp"
                  else np.log(d[col]))
        nunca = d[~d["cnes"].isin(est.CONVERSOES)]
        med_ctrl = nunca.groupby("ano")["y"].mean()

        att_por_evento = {}
        for g, membros in sorted(coortes.items()):
            base_t = g - 1
            trat = d[d["cnes"].isin(membros)]
            y_base = trat[trat["ano"] == base_t]["y"].mean()
            for t in range(g, 2026):
                y_t = trat[trat["ano"] == t]["y"].mean()
                if np.isnan(y_t) or t > d["ano"].max():
                    continue
                att = ((y_t - y_base)
                       - (med_ctrl[t] - med_ctrl[base_t]))
                e = t - g
                att_por_evento.setdefault(e, []).append((len(membros), att))
                linhas_att.append({"indicador": rotulo, "coorte": g,
                                   "ano": t, "evento": e,
                                   "n_tratados": len(membros),
                                   "att": att})
        # agregação por tempo de evento com pesos pelo tamanho da coorte
        thetas = {}
        for e, pares in sorted(att_por_evento.items()):
            ns = np.array([p[0] for p in pares], dtype=float)
            atts = np.array([p[1] for p in pares])
            thetas[e] = float((ns * atts).sum() / ns.sum())
        # espelha os bins do TWFE: 0, +1, +2 e média de 3 ou mais
        agreg = {0: thetas.get(0), 1: thetas.get(1), 2: thetas.get(2)}
        e3 = [v for e, v in thetas.items() if e >= 3]
        agreg[3] = float(np.mean(e3)) if e3 else np.nan
        for e, v in agreg.items():
            tw = twfe[(twfe["indicador"] == rotulo)
                      & (twfe["termo"] == rot_bin[e])]
            tw_c = float(tw["coef"].iloc[0]) if len(tw) else np.nan
            tw_ep = float(tw["ep_cluster"].iloc[0]) if len(tw) else np.nan
            linhas_agg.append({"indicador": rotulo, "unidade": unidade,
                               "evento": rot_bin[e], "att_cs": v,
                               "coef_twfe": tw_c, "ep_twfe": tw_ep})
        series_fig[rotulo] = (agreg, unidade)
        print(f"  {rotulo:<28} CS em t0 "
              f"{agreg[0]:+.3f} {unidade} (TWFE "
              f"{float(twfe[(twfe['indicador'] == rotulo) & (twfe['termo'] == '0')]['coef'].iloc[0]):+.3f})")

    est._tab(pd.DataFrame(linhas_att).round(5), "tab_est_cs_att.csv",
             index=False)
    est._tab(pd.DataFrame(linhas_agg).round(5), "tab_est_cs_evento.csv",
             index=False)

    # figuras de comparação CS vs TWFE para mortalidade e TMP
    for rotulo, slug in [("Mortalidade geral", "mort"), ("TMP", "tmp")]:
        agreg, unidade = series_fig[rotulo]
        tw = twfe[twfe["indicador"] == rotulo].set_index("termo")
        fig, ax = plt.subplots(figsize=(7.4, 4.4))
        xs = [0, 1, 2, 3]
        ax.axhline(0, color=est.COR_EIXO, lw=1)
        tw_c = [tw.loc[rot_bin[e], "coef"] for e in xs]
        tw_e = [tw.loc[rot_bin[e], "ep_cluster"] for e in xs]
        ax.errorbar([x - .06 for x in xs], tw_c,
                    yerr=[1.96 * v for v in tw_e], fmt="o",
                    color=est.COR_APOIO, capsize=3, ms=6,
                    label="TWFE (com IC de 95%)")
        cs_c = [agreg[e] for e in xs]
        ax.plot([x + .06 for x in xs], cs_c, "s", ms=7,
                color=est.CORES_CAT["OSS"], label="Callaway e Sant'Anna")
        for x, v in zip(xs, cs_c):
            if np.isfinite(v):
                ax.annotate(est._fmt_val(v), (x + .06, v),
                            textcoords="offset points", xytext=(8, 4),
                            fontsize=9.5, color=est.CORES_CAT["OSS"])
        ax.set_xticks(xs)
        ax.set_xticklabels(["0", "+1", "+2", "+3 ou depois"])
        ax.set_xlabel("Anos desde a conversão para OSS")
        ax.set_ylabel(f"Efeito estimado ({unidade})")
        ax.set_title(f"Estudo de eventos, TWFE vs Callaway e Sant'Anna: "
                     f"{rotulo}", fontsize=11)
        ax.legend(fontsize=9.5)
        fig.tight_layout()
        est._salvar(fig, f"fig_est_07_cs_twfe_{slug}.png")


# ══════════════════════════════════════════════════════════════════════════════
# 2b. CONTROLE SINTÉTICO COM PLACEBOS EM ESPAÇO
# ══════════════════════════════════════════════════════════════════════════════

def _pesos_sinteticos(X0, x1):
    """Pesos não negativos que somam um, por mínimos quadrados com a
    restrição de soma imposta por linha de penalidade."""
    pen = 1e6
    A = np.vstack([X0, pen * np.ones(X0.shape[1])])
    b = np.append(x1, pen)
    w, _ = nnls(A, b)
    s = w.sum()
    return w / s if s > 0 else w


def _ajuste_sintetico(tab, alvo_cnes, ano_conv, anos):
    """Ajusta o sintético de um CNES; devolve trajetórias e razão RMSPE."""
    pre = [a for a in anos if a < ano_conv]
    pos = [a for a in anos if a >= ano_conv]
    doadores = [c for c in tab.columns if c != alvo_cnes]
    X0 = tab.loc[pre, doadores].to_numpy()
    x1 = tab.loc[pre, alvo_cnes].to_numpy()
    w = _pesos_sinteticos(X0, x1)
    sint = tab[doadores].to_numpy() @ w
    real = tab[alvo_cnes].to_numpy()
    lacuna = real - sint
    i_pre = [anos.index(a) for a in pre]
    i_pos = [anos.index(a) for a in pos]
    rmspe_pre = float(np.sqrt(np.mean(lacuna[i_pre] ** 2)))
    rmspe_pos = float(np.sqrt(np.mean(lacuna[i_pos] ** 2)))
    return {"w": w, "doadores": doadores, "sint": sint, "real": real,
            "lacuna_pos": float(np.mean(lacuna[i_pos])),
            "rmspe_pre": rmspe_pre, "rmspe_pos": rmspe_pos,
            "razao": rmspe_pos / rmspe_pre if rmspe_pre > 0 else np.inf}


def bloco_sintetico(painel):
    print("\n" + "=" * 70)
    print("[2b] CONTROLE SINTÉTICO: Sorocaba e Pérola Byington, placebos "
          "em espaço")
    print("=" * 70)
    anos = sorted(painel["ano"].unique())
    casos = [(2081695, 2019), (2078287, 2023)]
    linhas = []
    for alvo_cnes, ano_conv in casos:
        nome = est.NOMES_CNES.get(alvo_cnes, str(alvo_cnes))
        for var in ["mort_pp", "tmp", "custo_real"]:
            d = painel.copy()
            d["mort_pp"] = d["mort_all"] * 100
            # doadores: nunca tratados, sem o CNES frágil; sem longa
            # permanência quando o desfecho é TMP
            excluir = set(est.CONVERSOES) | {est.CNES_FRAGIL}
            if var == "tmp":
                excluir |= set(d.loc[d["longa_perm"] == 1, "cnes"])
            excluir.discard(alvo_cnes)
            d = d[~d["cnes"].isin(excluir)]
            tab = d.pivot(index="ano", columns="cnes", values=var)
            aj = _ajuste_sintetico(tab, alvo_cnes, ano_conv, anos)

            # placebos: cada doador tratado de mentira no mesmo ano.
            # Com centenas de doadores e poucos anos anteriores, o ajuste
            # pré é interpolação exata (RMSPE pré perto de zero) e a razão
            # RMSPE degenera; a estatística do placebo passa a ser a
            # lacuna média pós conversão em valor absoluto.
            lacunas = []
            for cn in aj["doadores"]:
                pl = _ajuste_sintetico(tab.drop(columns=[alvo_cnes]),
                                       cn, ano_conv, anos)
                lacunas.append(pl["lacuna_pos"])
            lacunas = np.array(lacunas)
            p_lac = ((1 + np.sum(np.abs(lacunas) >= abs(aj["lacuna_pos"])))
                     / (len(lacunas) + 1))
            rotulo, unidade = ROT_VAR_SINT[var]
            print(f"  {nome} | {rotulo}")
            print(f"    lacuna média pós {aj['lacuna_pos']:+.3f} {unidade}; "
                  f"RMSPE pré {aj['rmspe_pre']:.4f}; "
                  f"p placebo (lacuna) {p_lac:.4f} "
                  f"({len(lacunas)} doadores)")
            linhas.append({"cnes": alvo_cnes, "hospital": nome,
                           "indicador": rotulo,
                           "lacuna_media_pos": aj["lacuna_pos"],
                           "rmspe_pre": aj["rmspe_pre"],
                           "p_placebo_lacuna": p_lac,
                           "n_doadores": len(lacunas)})

            fig, ax = plt.subplots(figsize=(7.4, 4.4))
            ax.plot(anos, aj["real"], "o", ls="solid", color="#0b0b0b",
                    lw=1.7, ms=4, label="hospital")
            ax.plot(anos, aj["sint"], marker="s", ls="dashed",
                    color=est.COR_SERIE, lw=1.5, ms=4,
                    label="controle sintético")
            ax.axvline(ano_conv - .5, color=est.COR_EVENTO, lw=1.3,
                       ls="dashed")
            pos_anos = [a for a in anos if a >= ano_conv]
            ax.annotate(f"lacuna média pós: {aj['lacuna_pos']:+.2f}",
                        xy=(.98, .04), xycoords="axes fraction",
                        ha="right", fontsize=9.5, color=est.COR_APOIO)
            ax.set_xlabel("Ano")
            ax.set_ylabel(rotulo)
            ax.set_title(f"{nome} (CNES {alvo_cnes}) vs sintético\n"
                         f"{rotulo} (conversão em {ano_conv}, "
                         f"p placebo {p_lac:.3f})", fontsize=11)
            ax.tick_params(axis="x", rotation=45)
            ax.legend(fontsize=9.5)
            fig.tight_layout()
            est._salvar(fig, f"fig_est_06_sintetico_{alvo_cnes}_{var}.png")
    est._tab(pd.DataFrame(linhas).round(4), "tab_est_sintetico.csv",
             index=False)


# ══════════════════════════════════════════════════════════════════════════════
# 3. INTENSIDADE DE UTI: GAMA E CORTE MÍNIMO
# ══════════════════════════════════════════════════════════════════════════════

def bloco_uti(painel):
    print("\n" + "=" * 70)
    print("[3] INTENSIDADE DE UTI: GLM Gama (ligação log) e corte mínimo")
    print("=" * 70)
    rng = np.random.default_rng(SEMENTE)
    d = est.amostra_desfecho(painel)
    pos = d[d["ocupacao_uti"] > 0].copy()
    f = f"ocupacao_uti_w ~ {est.COV_BASE}"
    linhas = []

    # referência: log OLS original (mesmos números de estimacao.py)
    pos["y_log"] = np.log(pos["ocupacao_uti_w"])
    res_log = smf.ols(f"y_log ~ {est.COV_BASE}", data=pos).fit(
        cov_type="cluster", cov_kwds={"groups": pos["cnes"]})
    c0, e0 = est._extrair_oss(res_log)
    r0 = est._r_qq(res_log.resid / np.std(res_log.resid, ddof=1))[0]
    linhas.append({"modelo": "log OLS (original)", "n": int(res_log.nobs),
                   "coef_oss": c0, "ep_cluster": e0,
                   "efeito_pct": 100 * (np.exp(c0) - 1), "r_qq": r0})

    # GLM Gama com ligação log na razão winsorizada
    res_gama = sm.GLM.from_formula(
        f, data=pos, family=sm.families.Gamma(link=sm.families.links.Log())
    ).fit(cov_type="cluster", cov_kwds={"groups": pos["cnes"]})
    phi = float(res_gama.scale)
    mu = np.asarray(res_gama.predict(pos))
    y = pos["ocupacao_uti_w"].to_numpy()
    u = stats.gamma.cdf(y, a=1 / phi, scale=mu * phi)
    resid_q = stats.norm.ppf(np.clip(u, 1e-7, 1 - 1e-7))
    r_gama = est._fig_qq_resid(resid_q, "fig_est_08_qq_uti_gama.png",
                               "Resíduos quantílicos: Ocupação UTI "
                               "(Gama, positivos)")
    c1, e1 = est._extrair_oss(res_gama)
    tab_g = pd.DataFrame({"coeficiente": res_gama.params,
                          "ep_cluster": res_gama.bse,
                          "z": res_gama.tvalues,
                          "p_valor": res_gama.pvalues})
    tab_g.index = [est._renomear(n) for n in tab_g.index]
    tab_g.loc["dispersão (Pearson)"] = [phi, np.nan, np.nan, np.nan]
    est._tab(tab_g.round(5), "tab_est_ocup_uti_gama.csv")
    linhas.append({"modelo": "GLM Gama ligação log", "n": int(res_gama.nobs),
                   "coef_oss": c1, "ep_cluster": e1,
                   "efeito_pct": 100 * (np.exp(c1) - 1), "r_qq": r_gama})

    # variante com corte mínimo de atividade (ocupação de ao menos 5%)
    corte = 5.0
    pos5 = pos[pos["ocupacao_uti"] >= corte].copy()
    pos5["y_log"] = np.log(pos5["ocupacao_uti_w"])
    res_c = smf.ols(f"y_log ~ {est.COV_BASE}", data=pos5).fit(
        cov_type="cluster", cov_kwds={"groups": pos5["cnes"]})
    c2, e2 = est._extrair_oss(res_c)
    r_c = est._r_qq(res_c.resid / np.std(res_c.resid, ddof=1))[0]
    n_removidas = len(pos) - len(pos5)
    linhas.append({"modelo": f"log OLS com corte de {corte:.0f}%",
                   "n": int(res_c.nobs), "coef_oss": c2, "ep_cluster": e2,
                   "efeito_pct": 100 * (np.exp(c2) - 1), "r_qq": r_c})

    tab = pd.DataFrame(linhas).round(4)
    est._tab(tab, "tab_est_uti_alternativas.csv", index=False)
    print(f"  Observações entre 0% e {corte:.0f}%: {n_removidas}")
    print(tab.to_string(index=False))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    bloco = sys.argv[1] if len(sys.argv) > 1 else "todos"
    est.PASTA_FIG_EST.mkdir(parents=True, exist_ok=True)
    painel = est.carregar_e_verificar()
    painel = est.preparar(painel)

    if bloco in ("bootstrap", "todos"):
        bloco_bootstrap(painel)
    if bloco in ("permutacao", "todos"):
        bloco_permutacao(painel)
    if bloco in ("cs", "todos"):
        bloco_cs(painel)
    if bloco in ("sintetico", "todos"):
        bloco_sintetico(painel)
    if bloco in ("uti", "todos"):
        bloco_uti(painel)
    print("\n[inferencia_robusta] Bloco(s) concluído(s).")


if __name__ == "__main__":
    main()
