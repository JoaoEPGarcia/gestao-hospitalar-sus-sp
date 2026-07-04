"""
estimacao.py
============
Fase de estimação do painel analítico de hospitais SUS/SP (314 hospitais,
2015 a 2025, 3.454 observações de hospital e ano), honrando integralmente
as decisões da Análise Exploratória (analises/analise_exploratoria.md e
tabelas tab_ae_*). Erros padrão agrupados por CNES em todos os modelos.

Blocos (iterativos; rodar um por vez ou todos):
  prep        0. Verificação do painel (aborta se não conferir) e
              1. Preparo: custo real (IPCA a preços de 2025), porte fixo,
                 flag de denominador frágil, dummy de longa permanência,
                 winsorização das ocupações no p99, dummies de ano
  principais  2. Modelos principais por indicador, nas famílias decididas:
                 mortalidade em Beta com inflação em zero (Mundlak),
                 fração de alta complexidade em ZOIB completo,
                 log do custo real e log do TMP em efeitos fixos,
                 produção em Binomial Negativa,
                 ocupação de internação no log, UTI em duas partes
  gestao      3. Efeito de gestão OSS vs Direta: estudo de eventos com
                 efeitos fixos (5 conversores, leads e lags, teste de
                 tendências paralelas) e amostra de suporte comum
  robustez    4. Reestimação sem 2020 e 2021, mortalidade ajustada como
                 checagem, resíduos quantílicos dos modelos ajustados

SALVAGUARDA DE CIRCULARIDADE: toda equação de mortalidade usa
complexidade_estrutural, nunca complexidade_pond_mort.
RESSALVA PERMANENTE: a categoria Privado tem 3 CNES e entra apenas como
dummy de absorção; nenhum coeficiente dela é interpretado.

Saídas: figuras em analises/figuras_estimacao (pasta exclusiva desta fase),
tabelas tab_est_* em analises/tabelas.

USO: python estimacao.py [prep|principais|gestao|robustez|todos]
"""

import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.othermod.betareg import BetaModel

import analise_sih as base                      # embrulha stdout no encoding do terminal

# ══════════════════════════════════════════════════════════════════════════════
# A. CONSTANTES E ESTILO (paleta fria da Análise Exploratória)
# ══════════════════════════════════════════════════════════════════════════════

PASTA_FIG_EST = base.PASTA_ANALISES / "figuras_estimacao"

CATEGORIAS = ["Direta", "OSS", "Público Municipal", "Filantrópico", "Privado"]
CORES_CAT = {
    "Direta":            "#0d366b",
    "OSS":               "#0f9b8e",
    "Público Municipal": "#5598e7",
    "Filantrópico":      "#6a51c7",
    "Privado":           "#898781",
}
MARCADORES = {
    "Direta":            "o",
    "OSS":               "s",
    "Público Municipal": "^",
    "Filantrópico":      "D",
    "Privado":           "X",
}
COR_SERIE  = "#2a78d6"
COR_APOIO  = "#0d366b"
COR_EVENTO = "#52514e"
COR_GRADE  = "#e1e0d9"
COR_EIXO   = "#c3c2b7"
COR_MUTED  = "#898781"
COR_BANDA  = "#f0efec"

ROT = {
    "mort_all":            "Mortalidade geral",
    "mort_sem_excl":       "Mortalidade ajustada",
    "tmp":                 "TMP (dias)",
    "custo_saida":         "Custo por saída (R$)",
    "custo_real":          "Custo por saída (R$ de 2025)",
    "pct_alta_complex":    "Fração alta complexidade",
    "qtde":                "Saídas hospitalares (produção)",
    "ocupacao_internacao": "Ocupação internação (%)",
    "ocupacao_uti":        "Ocupação UTI (%)",
}

CONVERSOES = {2081695: 2019, 2078287: 2023, 2082225: 2025,
              2091755: 2025, 2750511: 2025}

# preenchido em preparar(): nome fantasia por CNES no painel completo
NOMES_CNES = {}

# denominador frágil documentado na Análise Exploratória: único CNES com
# menos de 30 saídas sem COVID no biênio, com tmp igual a zero em 2021
CNES_FRAGIL = 2097613
ANOS_FRAGIL = (2020, 2021)

# IPCA anual (variação % dez/dez, IBGE); 2025 fechado em 4,26%
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


def _fatores_ipca_2025() -> dict:
    """Fator multiplicativo que leva valores do ano de referência a preços
    de 2025 (índice acumulado dez/dez até o fim de cada ano)."""
    anos = sorted(IPCA_ANUAL)
    indice, acum = {}, 1.0
    for a in anos:
        acum *= 1 + IPCA_ANUAL[a] / 100
        indice[a] = acum
    return {a: indice[anos[-1]] / indice[a] for a in anos}


def _salvar(fig, nome: str):
    caminho = PASTA_FIG_EST / nome
    fig.savefig(caminho, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [FIG] {nome}")


def _tab(df: pd.DataFrame, nome: str, index=True):
    df.to_csv(base.PASTA_TABELAS / nome, index=index, encoding="utf-8-sig")
    print(f"  [TAB] {nome}")


def _fmt_val(v) -> str:
    """Número legível para anotações: milhar com ponto, sem notação
    científica."""
    if abs(v) >= 100:
        return f"{v:,.0f}".replace(",", ".")
    return f"{v:.3g}"


def _renomear(nome: str) -> str:
    """Nomes de parâmetro legíveis nas tabelas."""
    trocas = {
        "C(modelo_gestao_proxy, Treatment('Direta'))[T.": "",
        "C(porte_fixo, Treatment('Médio Porte'))[T.": "porte ",
        "C(cat_zero, Treatment('Pública'))[T.": "",
        "C(ano)[T.": "ano ",
        "Intercept": "constante",
        "complexidade_estrutural": "complexidade estrutural",
        "longa_perm": "longa permanência",
        "media_oss": "média OSS (Mundlak)",
        "log_leitos": "log leitos",
    }
    for antes, depois in trocas.items():
        nome = nome.replace(antes, depois)
    return nome.rstrip("]")


def ep_cluster_mv(modelo, params, grupos) -> np.ndarray:
    """Erros padrão agrupados (sanduíche) para modelos de máxima
    verossimilhança sem suporte nativo a cov_type, caso do BetaModel:
    V = H^{-1} (soma dos escores por grupo) H^{-1}, com correção G/(G menos 1)."""
    s = modelo.score_obs(params)
    H = modelo.hessian(params)
    Hinv = np.linalg.inv(H)
    df_s = pd.DataFrame(s)
    df_s["_g"] = np.asarray(grupos)
    S = df_s.groupby("_g").sum().to_numpy()
    G = S.shape[0]
    meat = S.T @ S
    V = Hinv @ meat @ Hinv * G / (G - 1)
    return np.sqrt(np.diag(V))


def tabela_mv(nomes, params, ep, nome_arq, extra=None):
    """Tabela padronizada de um modelo: coeficiente, EP agrupado, z, p."""
    z = params / ep
    p = 2 * stats.norm.sf(np.abs(z))
    tab = pd.DataFrame({"coeficiente": params, "ep_cluster": ep,
                        "z": z, "p_valor": p},
                       index=[_renomear(n) for n in nomes]).round(5)
    if extra:
        for k, v in extra.items():
            tab.loc[k] = [v, np.nan, np.nan, np.nan]
    _tab(tab, nome_arq)
    return tab


# ══════════════════════════════════════════════════════════════════════════════
# 0. CARGA E VERIFICAÇÃO (aborta se o painel não conferir)
# ══════════════════════════════════════════════════════════════════════════════

def carregar_e_verificar() -> pd.DataFrame:
    painel = pd.read_csv(base.PASTA_ANALISES / "painel_definitivo.csv",
                         encoding="utf-8-sig")
    n_cnes = painel["cnes"].nunique()
    n_obs = len(painel)
    anos_cnes = painel.groupby("cnes")["ano"].nunique()
    nan_mod = painel["modelo_gestao_proxy"].isna().sum()
    nan_cpx = painel["complexidade_estrutural"].isna().sum()
    print(f"[0] Painel carregado: {n_cnes} CNES, {n_obs} linhas, "
          f"anos por CNES min {anos_cnes.min()} max {anos_cnes.max()}, "
          f"NaN modelo_gestao_proxy {nan_mod}, "
          f"NaN complexidade_estrutural {nan_cpx}")
    ok = (n_cnes == 314 and n_obs == 3454 and (anos_cnes == 11).all()
          and nan_mod == 0 and nan_cpx == 0)
    if not ok:
        raise SystemExit("[0] PAINEL NÃO CONFERE COM O ESPERADO. PARANDO.")
    print("[0] Verificação OK: 314 CNES, 3.454 observações, painel balanceado.")
    return painel


# ══════════════════════════════════════════════════════════════════════════════
# 1. PREPARO
# ══════════════════════════════════════════════════════════════════════════════

def preparar(painel: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "=" * 70)
    print("[1] PREPARO: custo real, porte fixo, frágeis, longa permanência, "
          "winsorização")
    print("=" * 70)

    # 1a. custo deflacionado pelo IPCA para preços de 2025
    fatores = _fatores_ipca_2025()
    painel["custo_real"] = painel["custo_saida"] * painel["ano"].map(fatores)
    med15 = painel.loc[painel["ano"] == 2015, "custo_real"].median()
    med25 = painel.loc[painel["ano"] == 2025, "custo_real"].median()
    print(f"  Custo real (R$ de 2025): mediana 2015 R$ {med15:,.0f}, "
          f"mediana 2025 R$ {med25:,.0f} "
          f"(fator de 2015: {fatores[2015]:.4f})")

    # 1b. porte fixo pela mediana de leitos (cortes oficiais 50/150/500)
    med_leitos = painel.groupby("cnes")["total_leitos"].median()

    def _porte(leitos):
        if leitos <= 50:
            return "HPP"
        if leitos <= 150:
            return "Médio Porte"
        if leitos <= 500:
            return "Grande Porte"
        return "Especial"

    painel["porte_fixo"] = painel["cnes"].map(med_leitos.apply(_porte))
    contagem = (painel.groupby("cnes")["porte_fixo"].first()
                .value_counts().to_dict())
    print(f"  Porte fixo por CNES: {contagem}")

    # 1c. flag de denominador frágil (2 observações do CNES 2097613)
    painel["flag_fragil"] = ((painel["cnes"] == CNES_FRAGIL)
                             & painel["ano"].isin(ANOS_FRAGIL)).astype(int)
    n_fragil = int(painel["flag_fragil"].sum())
    print(f"  Observações de denominador frágil (excluídas dos desfechos): "
          f"{n_fragil} (CNES {CNES_FRAGIL}, anos {ANOS_FRAGIL})")

    # 1d. dummy de longa permanência: CNES com TMP mediano acima de 20 dias
    tmp_med = painel.groupby("cnes")["tmp"].median()
    cnes_lp = set(tmp_med[tmp_med > 20].index)
    painel["longa_perm"] = painel["cnes"].isin(cnes_lp).astype(int)
    print(f"  Longa permanência: {len(cnes_lp)} CNES, "
          f"{int(painel['longa_perm'].sum())} observações")

    # 1e. winsorização das ocupações no percentil 99 (sem truncar em 100)
    limites = {}
    for c in ["ocupacao_internacao", "ocupacao_uti"]:
        p99 = float(np.percentile(painel[c], 99))
        limites[c] = p99
        painel[c + "_w"] = painel[c].clip(upper=p99)
        n_w = int((painel[c] > p99).sum())
        print(f"  {c}: p99 = {p99:.1f}%, {n_w} observações winsorizadas")

    # 1f. auxiliares: log de leitos (escala na produção), termo de Mundlak
    # (média da dummy OSS por CNES; complexidade e porte são fixos no tempo,
    # logo apenas a categoria varia dentro de hospital, e somente de Direta
    # para OSS nos 5 conversores)
    painel["log_leitos"] = np.log(painel["total_leitos"])
    painel["d_oss"] = (painel["modelo_gestao_proxy"] == "OSS").astype(int)
    painel["media_oss"] = painel.groupby("cnes")["d_oss"].transform("mean")
    n_sw = painel.loc[painel["media_oss"].between(0.001, 0.999),
                      "cnes"].nunique()
    print(f"  Termo de Mundlak media_oss: {n_sw} CNES com valor "
          f"intermediário (os conversores)")

    # 1g. categoria agrupada para o componente logístico da mortalidade:
    # OSS e Público Municipal não registram nenhum óbito zero (separação
    # perfeita), então o logito usa Filantrópico e Privado contra a base
    # agregada das três categorias públicas
    painel["cat_zero"] = painel["modelo_gestao_proxy"].where(
        painel["modelo_gestao_proxy"].isin(["Filantrópico", "Privado"]),
        "Pública")
    zeros_cat = (painel[painel["mort_all"] == 0]
                 .groupby("modelo_gestao_proxy").size().to_dict())
    print(f"  Zeros de mortalidade por categoria: {zeros_cat} "
          f"(OSS e Municipal sem zeros: separação, base agregada no logito)")

    # nomes fantasia fixados no painel completo (o cadastro só traz o nome
    # em parte dos anos, concentrados em 2020 e 2021)
    global NOMES_CNES
    NOMES_CNES = painel.groupby("cnes")["nome_fantasia"].agg(
        lambda s: s.dropna().iloc[-1] if s.notna().any() else "").to_dict()

    # tabela de preparo para o relatório
    nomes = painel.groupby("cnes")["nome_fantasia"].last()
    linhas = [{"item": "fator IPCA para 2025", "detalhe": str(a),
               "valor": round(fatores[a], 4)} for a in sorted(fatores)]
    linhas += [{"item": "p99 winsorização", "detalhe": c,
                "valor": round(limites[c], 1)} for c in limites]
    linhas += [{"item": "denominador frágil", "detalhe":
                f"CNES {CNES_FRAGIL} ({nomes.get(CNES_FRAGIL)}) {a}",
                "valor": 1} for a in ANOS_FRAGIL]
    linhas += [{"item": "longa permanência",
                "detalhe": f"CNES {c} ({nomes.get(c)})",
                "valor": round(tmp_med[c], 1)} for c in sorted(cnes_lp)]
    _tab(pd.DataFrame(linhas), "tab_est_preparo.csv", index=False)

    return painel


# ══════════════════════════════════════════════════════════════════════════════
# AMOSTRAS
# ══════════════════════════════════════════════════════════════════════════════

def amostra_desfecho(painel: pd.DataFrame) -> pd.DataFrame:
    """Exclui as 2 observações de denominador frágil de toda equação."""
    return painel[painel["flag_fragil"] == 0].copy()


def amostra_suporte(painel: pd.DataFrame) -> pd.DataFrame:
    """Suporte comum do efeito de gestão: faixas 3 e 4, portes médio e
    grande (leitura recomendada pela Análise Exploratória)."""
    sup = painel[painel["faixa_barcelona"].isin([3, 4])
                 & painel["porte_fixo"].isin(["Médio Porte", "Grande Porte"])]
    return sup.copy()


# ══════════════════════════════════════════════════════════════════════════════
# 2. MODELOS PRINCIPAIS POR INDICADOR
# ══════════════════════════════════════════════════════════════════════════════

CAT   = "C(modelo_gestao_proxy, Treatment('Direta'))"
PORTE = "C(porte_fixo, Treatment('Médio Porte'))"
COV_BASE = f"{CAT} + complexidade_estrutural + {PORTE} + longa_perm + C(ano)"


def _ajustar_logit(formula, dados, rotulo, tentar_sem_ano=True):
    """Logit com erros padrão agrupados por CNES; se houver separação com
    as dummies de ano (coeficiente divergindo), reajusta sem elas e avisa."""
    grupos = dados["cnes"]
    mod = smf.logit(formula, data=dados)
    res = mod.fit(disp=0, maxiter=200, method="bfgs",
                  cov_type="cluster", cov_kwds={"groups": grupos})
    if np.abs(res.params).max() > 15 and tentar_sem_ano:
        print(f"    [{rotulo}] separação com dummies de ano "
              f"(|coef| máximo {np.abs(res.params).max():.0f}); "
              f"reajustando sem C(ano)")
        formula2 = formula.replace(" + C(ano)", "")
        mod = smf.logit(formula2, data=dados)
        res = mod.fit(disp=0, maxiter=200, method="bfgs",
                      cov_type="cluster", cov_kwds={"groups": grupos})
    if not res.mle_retvals.get("converged", True):
        print(f"    [{rotulo}] ATENÇÃO: logit não convergiu")
    return res


def _extrair_oss(res, escala="log"):
    """Coeficiente OSS vs Direta e erro padrão agrupado de um resultado."""
    alvo = [n for n in res.params.index if "[T.OSS]" in n]
    if not alvo:
        return np.nan, np.nan
    c, e = res.params[alvo[0]], res.bse[alvo[0]]
    return float(c), float(e)


def modelo_mortalidade(painel, col="mort_all", sufixo="", verboso=True):
    """Beta com inflação em zero: logito dos zeros (complexidade, porte e
    categoria agrupada por separação) e média condicional Beta com Mundlak
    (média da dummy OSS por hospital), dada a variância within de 13,9%."""
    d = amostra_desfecho(painel)
    if verboso:
        print(f"\n  MORTALIDADE ({col}): Beta com inflação em zero, "
              f"Mundlak, n = {len(d)}")

    # componente logístico dos zeros
    d["y_zero"] = (d[col] == 0).astype(int)
    f_zero = ("y_zero ~ C(cat_zero, Treatment('Pública')) "
              "+ complexidade_estrutural + " + PORTE + " + C(ano)")
    res_zero = _ajustar_logit(f_zero, d, f"mortalidade zeros{sufixo}")

    # componente Beta no interior, com Mundlak
    interior = d[(d[col] > 0) & (d[col] < 1)].copy()
    f_media = (f"{col} ~ {CAT} + complexidade_estrutural + {PORTE} "
               "+ longa_perm + media_oss + C(ano)")
    y, X = patsy.dmatrices(f_media, data=interior, return_type="dataframe")
    mod_beta = BetaModel(np.asarray(y).ravel(), X)
    res_beta = mod_beta.fit(maxiter=500, disp=0)
    params_b = np.asarray(res_beta.params)
    nomes = list(X.columns) + ["ln precisão"]
    ep = ep_cluster_mv(mod_beta, params_b, interior["cnes"])

    # tabela única com os dois componentes
    tab_z = pd.DataFrame({"coeficiente": res_zero.params,
                          "ep_cluster": res_zero.bse})
    tab_z.index = [_renomear(n) for n in tab_z.index]
    tab_z["componente"] = "logito do zero"
    tab_b = pd.DataFrame({"coeficiente": params_b, "ep_cluster": ep},
                         index=[_renomear(n) for n in nomes])
    tab_b["componente"] = "média Beta"
    tab = pd.concat([tab_b, tab_z])
    tab["z"] = tab["coeficiente"] / tab["ep_cluster"]
    tab["p_valor"] = 2 * stats.norm.sf(np.abs(tab["z"]))
    _tab(tab.round(5)[["componente", "coeficiente", "ep_cluster", "z",
                       "p_valor"]], f"tab_est_mort_zib{sufixo}.csv")

    # efeito marginal médio do contraste OSS vs Direta em pontos percentuais
    i_oss = [i for i, n in enumerate(X.columns) if "[T.OSS]" in n][0]
    k_media = X.shape[1]
    mu = mod_beta.predict(params_b, exog=np.asarray(X))
    pi = res_zero.predict(d)
    b_oss = params_b[i_oss]
    ep_oss = ep[i_oss]
    ame_pp = float(np.mean(mu * (1 - mu)) * b_oss * (1 - pi.mean()) * 100)
    llf = float(res_beta.llf + res_zero.llf)
    if verboso:
        print(f"    zeros: {int(d['y_zero'].sum())} de {len(d)}; interior "
              f"n = {len(interior)}; log verossimilhança total {llf:,.0f}")
        print(f"    OSS vs Direta (média Beta, within Mundlak): "
              f"coef {b_oss:+.4f} (EP {ep_oss:.4f}), "
              f"efeito marginal médio {ame_pp:+.3f} p.p.")
        print(f"    média OSS (Mundlak, between): coef "
              f"{params_b[list(X.columns).index('media_oss')]:+.4f}")
    return {"rotulo": f"Mortalidade ({'geral' if col == 'mort_all' else 'ajustada'})",
            "oss": b_oss, "ep": ep_oss, "escala": "logito Beta",
            "ame_pp": ame_pp, "res_zero": res_zero, "mod_beta": mod_beta,
            "res_beta": res_beta, "interior": interior, "amostra": d,
            "col": col, "X": X, "k_media": k_media}


def modelo_pct_alta(painel, sufixo="", verboso=True):
    """ZOIB completo para a fração de alta complexidade: logito do zero,
    logito do um (11 casos, 10 deles Privados: só dummy Privado) e Beta."""
    d = amostra_desfecho(painel)
    col = "pct_alta_complex"
    if verboso:
        print(f"\n  ALTA COMPLEXIDADE ({col}): ZOIB completo, n = {len(d)}")

    d["y_zero"] = (d[col] == 0).astype(int)
    d["y_um"] = (d[col] == 1).astype(int)
    d["d_privado"] = (d["modelo_gestao_proxy"] == "Privado").astype(int)

    f_zero = f"y_zero ~ {CAT} + complexidade_estrutural + {PORTE} + C(ano)"
    res_zero = _ajustar_logit(f_zero, d, f"pct alta zeros{sufixo}")
    res_um = _ajustar_logit("y_um ~ d_privado", d, f"pct alta uns{sufixo}",
                            tentar_sem_ano=False)

    interior = d[(d[col] > 0) & (d[col] < 1)].copy()
    f_media = (f"{col} ~ {CAT} + complexidade_estrutural + {PORTE} "
               "+ longa_perm + C(ano)")
    y, X = patsy.dmatrices(f_media, data=interior, return_type="dataframe")
    mod_beta = BetaModel(np.asarray(y).ravel(), X)
    res_beta = mod_beta.fit(maxiter=500, disp=0)
    params_b = np.asarray(res_beta.params)
    nomes = list(X.columns) + ["ln precisão"]
    ep = ep_cluster_mv(mod_beta, params_b, interior["cnes"])

    partes = []
    for rotulo, params, eps in [
            ("média Beta", pd.Series(params_b,
                                     index=[_renomear(n) for n in nomes]),
             pd.Series(ep, index=[_renomear(n) for n in nomes])),
            ("logito do zero", res_zero.params.rename(_renomear),
             res_zero.bse.rename(_renomear)),
            ("logito do um", res_um.params.rename(_renomear),
             res_um.bse.rename(_renomear))]:
        t = pd.DataFrame({"coeficiente": params, "ep_cluster": eps})
        t["componente"] = rotulo
        partes.append(t)
    tab = pd.concat(partes)
    tab["z"] = tab["coeficiente"] / tab["ep_cluster"]
    tab["p_valor"] = 2 * stats.norm.sf(np.abs(tab["z"]))
    _tab(tab.round(5)[["componente", "coeficiente", "ep_cluster", "z",
                       "p_valor"]], f"tab_est_pct_alta_zoib{sufixo}.csv")

    i_oss = [i for i, n in enumerate(X.columns) if "[T.OSS]" in n][0]
    b_oss, ep_oss = params_b[i_oss], ep[i_oss]
    alvo_z = [n for n in res_zero.params.index if "[T.OSS]" in n][0]
    if verboso:
        print(f"    zeros {int(d['y_zero'].sum())}, uns "
              f"{int(d['y_um'].sum())}, interior {len(interior)}")
        print(f"    OSS vs Direta: média Beta {b_oss:+.4f} (EP {ep_oss:.4f}); "
              f"logito do zero {res_zero.params[alvo_z]:+.3f} "
              f"(EP {res_zero.bse[alvo_z]:.3f})")
    return {"rotulo": "Fração alta complexidade", "oss": b_oss,
            "ep": ep_oss, "escala": "logito Beta", "res_zero": res_zero,
            "res_um": res_um, "mod_beta": mod_beta, "res_beta": res_beta,
            "interior": interior, "amostra": d, "col": col, "X": X}


def _modelo_fe(painel, col, transform, nome_tab, rotulo, excluir_lp=False,
               verboso=True):
    """Efeitos fixos de hospital e ano por MQO com dummies de CNES; erros
    padrão agrupados por CNES; identificação da categoria pelos conversores."""
    d = amostra_desfecho(painel)
    if excluir_lp:
        d = d[d["longa_perm"] == 0]
    d["y"] = transform(d[col])
    f = f"y ~ {CAT} + C(ano) + C(cnes)"
    res = smf.ols(f, data=d).fit(cov_type="cluster",
                                 cov_kwds={"groups": d["cnes"]})
    tab = pd.DataFrame({"coeficiente": res.params, "ep_cluster": res.bse,
                        "z": res.tvalues, "p_valor": res.pvalues})
    tab = tab[~tab.index.str.startswith("C(cnes)")]
    tab.index = [_renomear(n) for n in tab.index]
    tab.loc["R2"] = [res.rsquared, np.nan, np.nan, np.nan]
    tab.loc["N"] = [res.nobs, np.nan, np.nan, np.nan]
    _tab(tab.round(5), nome_tab)
    c, e = _extrair_oss(res)
    if verboso:
        print(f"\n  {rotulo}: efeitos fixos de hospital e ano, "
              f"n = {int(res.nobs)}, R2 = {res.rsquared:.3f}")
        print(f"    OSS vs Direta (conversores): {c:+.4f} log pontos "
              f"(EP {e:.4f}), efeito de {100 * (np.exp(c) - 1):+.1f}%")
    return {"rotulo": rotulo, "oss": c, "ep": e, "escala": "log",
            "res": res, "amostra": d, "col": col}


def modelo_producao(painel, sufixo="", verboso=True):
    """Produção (saídas) em Binomial Negativa com controle de escala por
    log de leitos; alfa de dispersão perfilado por máxima verossimilhança
    e coeficientes via GLM (a rota direta da BN não converge com a escala
    das saídas); erros padrão agrupados por CNES, condicionais ao alfa."""
    d = amostra_desfecho(painel)
    f = f"qtde ~ {COV_BASE} + log_leitos"

    def negll(a):
        fam = sm.families.NegativeBinomial(alpha=a)
        return -sm.GLM.from_formula(f, data=d, family=fam).fit().llf

    from scipy.optimize import minimize_scalar
    ot = minimize_scalar(negll, bounds=(0.01, 5), method="bounded",
                         options={"xatol": 1e-5})
    alpha = float(ot.x)
    res = sm.GLM.from_formula(
        f, data=d, family=sm.families.NegativeBinomial(alpha=alpha)
    ).fit(cov_type="cluster", cov_kwds={"groups": d["cnes"]})
    tab = pd.DataFrame({"coeficiente": res.params, "ep_cluster": res.bse,
                        "z": res.tvalues, "p_valor": res.pvalues})
    tab.index = [_renomear(n) for n in tab.index]
    tab.loc["alfa (perfilado)"] = [alpha, np.nan, np.nan, np.nan]
    tab.loc["N"] = [res.nobs, np.nan, np.nan, np.nan]
    _tab(tab.round(5), f"tab_est_producao_bn{sufixo}.csv")
    c, e = _extrair_oss(res)
    if verboso:
        print(f"\n  PRODUÇÃO (qtde): Binomial Negativa (GLM, alfa "
              f"perfilado), n = {int(res.nobs)}, alfa = {alpha:.4f}, "
              f"llf = {res.llf:,.0f}")
        print(f"    OSS vs Direta: {c:+.4f} (EP {e:.4f}), "
              f"efeito de {100 * (np.exp(c) - 1):+.1f}% nas saídas")
    return {"rotulo": "Produção (saídas)", "oss": c, "ep": e,
            "escala": "log", "res": res, "amostra": d, "col": "qtde",
            "alpha": alpha}


def modelo_ocup_internacao(painel, sufixo="", verboso=True):
    """Ocupação de internação no log (winsorizada no p99, sem truncar em
    100), MQO com erros padrão agrupados."""
    d = amostra_desfecho(painel)
    d["y"] = np.log(d["ocupacao_internacao_w"])
    f = f"y ~ {COV_BASE}"
    res = smf.ols(f, data=d).fit(cov_type="cluster",
                                 cov_kwds={"groups": d["cnes"]})
    tab = pd.DataFrame({"coeficiente": res.params, "ep_cluster": res.bse,
                        "z": res.tvalues, "p_valor": res.pvalues})
    tab.index = [_renomear(n) for n in tab.index]
    tab.loc["R2"] = [res.rsquared, np.nan, np.nan, np.nan]
    tab.loc["N"] = [res.nobs, np.nan, np.nan, np.nan]
    _tab(tab.round(5), f"tab_est_ocup_internacao{sufixo}.csv")
    c, e = _extrair_oss(res)
    if verboso:
        print(f"\n  OCUPAÇÃO INTERNAÇÃO: log da razão winsorizada, "
              f"n = {int(res.nobs)}, R2 = {res.rsquared:.3f}")
        print(f"    OSS vs Direta: {c:+.4f} (EP {e:.4f}), "
              f"efeito de {100 * (np.exp(c) - 1):+.1f}%")
    return {"rotulo": "Ocupação internação", "oss": c, "ep": e,
            "escala": "log", "res": res, "amostra": d,
            "col": "ocupacao_internacao_w"}


def modelo_ocup_uti(painel, sufixo="", verboso=True):
    """Ocupação de UTI em duas partes: logito de UTI ativa e log da
    intensidade entre os positivos (winsorizada no p99)."""
    d = amostra_desfecho(painel)
    d["uti_ativa"] = (d["ocupacao_uti"] > 0).astype(int)
    f1 = f"uti_ativa ~ {CAT} + complexidade_estrutural + {PORTE} + C(ano)"
    res1 = _ajustar_logit(f1, d, f"UTI ativa{sufixo}")

    pos = d[d["ocupacao_uti"] > 0].copy()
    pos["y"] = np.log(pos["ocupacao_uti_w"])
    f2 = f"y ~ {COV_BASE}"
    res2 = smf.ols(f2, data=pos).fit(cov_type="cluster",
                                     cov_kwds={"groups": pos["cnes"]})
    partes = []
    for rotulo, r in [("logito UTI ativa", res1), ("log intensidade", res2)]:
        t = pd.DataFrame({"coeficiente": r.params, "ep_cluster": r.bse,
                          "z": r.tvalues, "p_valor": r.pvalues})
        t.index = [_renomear(n) for n in t.index]
        t["componente"] = rotulo
        partes.append(t)
    tab = pd.concat(partes)
    _tab(tab.round(5)[["componente", "coeficiente", "ep_cluster", "z",
                       "p_valor"]], f"tab_est_ocup_uti_2partes{sufixo}.csv")
    c1, e1 = _extrair_oss(res1)
    c2, e2 = _extrair_oss(res2)
    if verboso:
        print(f"\n  OCUPAÇÃO UTI: duas partes; UTI ativa em "
              f"{int(d['uti_ativa'].sum())} de {len(d)} observações")
        print(f"    OSS vs Direta: logito UTI ativa {c1:+.3f} (EP {e1:.3f}); "
              f"log intensidade {c2:+.4f} (EP {e2:.4f}), "
              f"efeito de {100 * (np.exp(c2) - 1):+.1f}%")
    return {"rotulo": "Ocupação UTI (intensidade)", "oss": c2, "ep": e2,
            "escala": "log", "res1": res1, "res2": res2, "amostra": d,
            "positivos": pos, "col": "ocupacao_uti_w"}


def modelos_principais(painel, sufixo="", verboso=True):
    if verboso:
        print("\n" + "=" * 70)
        print("[2] MODELOS PRINCIPAIS POR INDICADOR (EP agrupados por CNES)")
        print("=" * 70)
    resultados = {}
    resultados["mortalidade"] = modelo_mortalidade(painel, sufixo=sufixo,
                                                   verboso=verboso)
    resultados["pct_alta"] = modelo_pct_alta(painel, sufixo=sufixo,
                                             verboso=verboso)
    resultados["custo"] = _modelo_fe(
        painel, "custo_real", np.log, f"tab_est_custo_fe{sufixo}.csv",
        "Custo real por saída (log)", verboso=verboso)
    resultados["tmp"] = _modelo_fe(
        painel, "tmp", np.log, f"tab_est_tmp_fe{sufixo}.csv",
        "TMP (log, sem longa perm.)", excluir_lp=True, verboso=verboso)
    resultados["producao"] = modelo_producao(painel, sufixo=sufixo,
                                             verboso=verboso)
    resultados["ocup_int"] = modelo_ocup_internacao(painel, sufixo=sufixo,
                                                    verboso=verboso)
    resultados["ocup_uti"] = modelo_ocup_uti(painel, sufixo=sufixo,
                                             verboso=verboso)

    # resumo do contraste OSS vs Direta
    linhas = []
    for chave, r in resultados.items():
        efeito_pct = (100 * (np.exp(r["oss"]) - 1)
                      if r["escala"] == "log" else np.nan)
        linhas.append({"modelo": r["rotulo"], "coef_oss": r["oss"],
                       "ep_cluster": r["ep"],
                       "z": r["oss"] / r["ep"] if r["ep"] else np.nan,
                       "efeito_pct": efeito_pct,
                       "ame_pp": r.get("ame_pp", np.nan)})
    resumo = pd.DataFrame(linhas).round(4)
    _tab(resumo, f"tab_est_resumo_oss{sufixo}.csv", index=False)
    if verboso:
        print("\n  RESUMO OSS vs Direta:")
        print(resumo.to_string(index=False))
    return resultados


# ══════════════════════════════════════════════════════════════════════════════
# 3. EFEITO DE GESTÃO: ESTUDO DE EVENTOS E CONTRASTE OSS VS DIRETA
# ══════════════════════════════════════════════════════════════════════════════

# janelas relativas ao ano de conversão; a referência é o ano anterior
# (tempo igual a menos 1); pontas agrupadas em "menos 5 ou antes" e
# "mais 3 ou depois" pela cobertura dos 5 conversores
BINS_EVENTO = [("ev_m5", -np.inf, -5), ("ev_m4", -4, -4), ("ev_m3", -3, -3),
               ("ev_m2", -2, -2), ("ev_0", 0, 0), ("ev_1", 1, 1),
               ("ev_2", 2, 2), ("ev_3p", 3, np.inf)]
POS_EVENTO = {"ev_m5": -5, "ev_m4": -4, "ev_m3": -3, "ev_m2": -2,
              "ev_0": 0, "ev_1": 1, "ev_2": 2, "ev_3p": 3}
ROT_EVENTO = {"ev_m5": "-5 ou antes", "ev_m4": "-4", "ev_m3": "-3",
              "ev_m2": "-2", "ev_0": "0", "ev_1": "+1", "ev_2": "+2",
              "ev_3p": "+3 ou depois"}

ALVOS_EVENTO = [
    ("mort_all", "pp", "Mortalidade geral", "p.p."),
    ("tmp", "log", "TMP", "log pontos"),
    ("custo_real", "log", "Custo real por saída", "log pontos"),
    ("pct_alta_complex", "pp", "Fração alta complexidade", "p.p."),
    ("ocupacao_internacao_w", "log", "Ocupação internação", "log pontos"),
]


def _montar_evento(d: pd.DataFrame) -> tuple:
    """Cria as dummies de tempo relativo à conversão; devolve o quadro e a
    lista de dummies com suporte na amostra."""
    d = d.copy()
    d["tempo_ev"] = np.nan
    for cnes, ano_conv in CONVERSOES.items():
        m = d["cnes"] == cnes
        d.loc[m, "tempo_ev"] = d.loc[m, "ano"] - ano_conv
    usadas = []
    for nome, lo, hi in BINS_EVENTO:
        d[nome] = ((d["tempo_ev"] >= lo) & (d["tempo_ev"] <= hi)).astype(int)
        if d[nome].sum() > 0:
            usadas.append(nome)
    return d, usadas


def _fig_evento(coefs, nome_arq, titulo, unidade, subtitulo):
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    xs = [POS_EVENTO[t] for t in coefs.index]
    ax.axhline(0, color=COR_EIXO, lw=1)
    ax.axvline(-0.5, color=COR_EVENTO, lw=1.2, ls="dashed")
    ax.errorbar(xs, coefs["coef"], yerr=1.96 * coefs["ep"], fmt="o",
                color=COR_SERIE, ecolor=COR_SERIE, elinewidth=1.4,
                capsize=3, ms=6, zorder=3)
    ax.plot([-1], [0], marker="D", color=COR_EVENTO, ms=6, zorder=3)
    for t in ["ev_0", "ev_3p"]:
        if t in coefs.index:
            v = coefs.loc[t, "coef"]
            ax.annotate(_fmt_val(v), (POS_EVENTO[t], v),
                        textcoords="offset points", xytext=(8, 6),
                        fontsize=9.5, color=COR_APOIO)
    rot_pos = {-5: "-5 ou antes", -4: "-4", -3: "-3", -2: "-2",
               -1: "-1 (ref.)", 0: "0", 1: "+1", 2: "+2",
               3: "+3 ou depois"}
    posicoes = sorted(set(xs + [-1]))
    ax.set_xticks(posicoes)
    ax.set_xticklabels([rot_pos[p] for p in posicoes], fontsize=9.5)
    ax.set_xlabel("Anos desde a conversão para OSS")
    ax.set_ylabel(f"Efeito estimado ({unidade})")
    ax.set_title(f"{titulo}\n{subtitulo}", fontsize=11)
    fig.tight_layout()
    _salvar(fig, nome_arq)


def estudo_eventos(painel, sufixo="", fazer_figuras=True):
    """Estudo de eventos com efeitos fixos de hospital e ano em torno da
    conversão para OSS dos 5 conversores; teste de tendências paralelas
    pelos leads; amostra completa e amostra de suporte comum."""
    print("\n" + "=" * 70)
    print(f"[3] EFEITO DE GESTÃO: estudo de eventos{sufixo} "
          "(EP agrupados por CNES)")
    print("=" * 70)
    nomes_fantasia = NOMES_CNES

    amostras = [("completa", "01", amostra_desfecho(painel))]
    if not sufixo:
        sup = amostra_suporte(amostra_desfecho(painel))
        amostras.append(("suporte comum", "02", sup))
    linhas, linhas_pt = [], []
    for rotulo_am, num_fig, d0 in amostras:
        conv_na_amostra = [c for c in CONVERSOES if c in
                           set(d0["cnes"].unique())]
        print(f"\n  Amostra {rotulo_am}: {d0['cnes'].nunique()} CNES, "
              f"{len(d0)} obs; conversores presentes: "
              + ", ".join(f"{c} ({nomes_fantasia.get(c)})"
                          for c in conv_na_amostra))
        for col, escala, rotulo, unidade in ALVOS_EVENTO:
            d = d0.copy()
            if col == "tmp":
                d = d[d["longa_perm"] == 0]
            d, usadas = _montar_evento(d)
            if escala == "pp":
                d["y"] = d[col] * 100
            else:
                d["y"] = np.log(d[col])
            f = "y ~ " + " + ".join(usadas) + " + C(ano) + C(cnes)"
            res = smf.ols(f, data=d).fit(cov_type="cluster",
                                         cov_kwds={"groups": d["cnes"]})
            coefs = pd.DataFrame({"coef": res.params[usadas],
                                  "ep": res.bse[usadas],
                                  "p_valor": res.pvalues[usadas]})
            for t in usadas:
                linhas.append({"amostra": rotulo_am, "indicador": rotulo,
                               "unidade": unidade, "termo": ROT_EVENTO[t],
                               "coef": coefs.loc[t, "coef"],
                               "ep_cluster": coefs.loc[t, "ep"],
                               "p_valor": coefs.loc[t, "p_valor"]})
            # tendências paralelas: leads conjuntamente nulos
            leads = [t for t in usadas if t.startswith("ev_m")]
            wt = res.wald_test(", ".join(f"{t} = 0" for t in leads),
                               use_f=True, scalar=True)
            p_leads = float(wt.pvalue)
            linhas_pt.append({"amostra": rotulo_am, "indicador": rotulo,
                              "estatistica_F": float(wt.statistic),
                              "gl": str(wt.df_denom),
                              "p_valor": p_leads})
            pos_chave = coefs.loc["ev_0", "coef"] if "ev_0" in usadas else np.nan
            print(f"    {rotulo:<28} efeito em t0 {pos_chave:+.3f} {unidade}; "
                  f"leads conjuntos p = {p_leads:.3f}")
            if fazer_figuras:
                sub = ("Conversores Direta para OSS, efeitos fixos de "
                       f"hospital e ano, amostra {rotulo_am}")
                _fig_evento(coefs, f"fig_est_{num_fig}_evento"
                            f"{'_suporte' if num_fig == '02' else ''}_{col}.png",
                            f"Estudo de eventos: {rotulo}", unidade, sub)
    _tab(pd.DataFrame(linhas).round(5), f"tab_est_evento{sufixo}.csv",
         index=False)
    _tab(pd.DataFrame(linhas_pt).round(5),
         f"tab_est_tendencias_paralelas{sufixo}.csv", index=False)
    print("\n  Ressalva registrada: Sorocaba tem pico de mortalidade "
          "imediatamente antes da conversão (reversão à média possível) e "
          "o Pérola Byington melhora já em 2021 e 2022, antes da mudança "
          "formal; os leads acima quantificam essas dinâmicas.")


def figura_contraste_oss(resultados):
    """Painel de contraste OSS vs Direta nos modelos em escala log
    (efeito percentual com IC de 95%); mortalidade anotada em p.p."""
    modelos = [(ch, r) for ch, r in resultados.items()
               if r["escala"] == "log"]
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    ys = np.arange(len(modelos))[::-1]
    ax.axvline(0, color=COR_EIXO, lw=1)
    for y, (ch, r) in zip(ys, modelos):
        c, e = r["oss"], r["ep"]
        lo, hi = 100 * (np.exp(c - 1.96 * e) - 1), 100 * (np.exp(c + 1.96 * e) - 1)
        pc = 100 * (np.exp(c) - 1)
        ax.plot([lo, hi], [y, y], color=CORES_CAT["OSS"], lw=2)
        ax.plot([pc], [y], marker=MARCADORES["OSS"], color=CORES_CAT["OSS"],
                ms=7)
        ax.annotate(f"{pc:+.1f}%", (pc, y), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=10,
                    color=COR_APOIO)
    ax.set_yticks(ys)
    ax.set_yticklabels([r["rotulo"] for _, r in modelos], fontsize=10.5)
    ax.set_xlabel("Efeito OSS vs Direta (%)")
    ame = resultados["mortalidade"].get("ame_pp", np.nan)
    ax.set_title("Contraste OSS vs Direta nos modelos principais\n"
                 f"(mortalidade: efeito marginal médio de {ame:+.2f} p.p., "
                 "Beta inflada com Mundlak)", fontsize=11)
    fig.tight_layout()
    _salvar(fig, "fig_est_03_contraste_oss_direta.png")


# ══════════════════════════════════════════════════════════════════════════════
# 4. ROBUSTEZ E DIAGNÓSTICO
# ══════════════════════════════════════════════════════════════════════════════

def _beta_mu_phi(mod_beta, res_beta, X):
    params = np.asarray(res_beta.params)
    mu = mod_beta.predict(params, exog=np.asarray(X))
    phi = np.exp(params[-1])
    return mu, phi


def _r_qq(x):
    x = np.sort(np.asarray(x))
    q = stats.norm.ppf((np.arange(1, len(x) + 1) - .5) / len(x))
    return float(np.corrcoef(q, x)[0, 1]), q, x


def _fig_qq_resid(resid, nome_arq, titulo):
    r, q, x = _r_qq(resid)
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    ax.plot(q, x, ".", color=COR_SERIE, ms=3.5, alpha=.7)
    lim = [min(q.min(), x.min()), max(q.max(), x.max())]
    ax.plot(lim, lim, color=COR_EVENTO, lw=1.2, ls="dashed")
    ax.annotate(f"r = {r:.4f}\nn = {len(x):,}".replace(",", "."),
                xy=(.04, .96), xycoords="axes fraction", va="top",
                fontsize=10, color=COR_APOIO)
    ax.set_xlabel("Quantis teóricos da Normal")
    ax.set_ylabel("Resíduos quantílicos ordenados")
    ax.set_title(titulo, fontsize=11)
    fig.tight_layout()
    _salvar(fig, nome_arq)
    return r


def residuos_quantilicos(resultados):
    """Resíduos quantílicos aleatorizados dos modelos ajustados: a
    validação distribucional decisiva prometida na Análise Exploratória."""
    print("\n  RESÍDUOS QUANTÍLICOS DOS MODELOS AJUSTADOS")
    rng = np.random.default_rng(20260704)
    diag = []

    def registrar(slug, titulo, resid):
        resid = np.asarray(resid)
        resid = resid[np.isfinite(resid)]
        r = _fig_qq_resid(resid, f"fig_est_04_qq_{slug}.png",
                          f"Resíduos quantílicos: {titulo}")
        diag.append({"modelo": titulo, "r_qq": r,
                     "assimetria": float(stats.skew(resid)),
                     "curtose_excesso": float(stats.kurtosis(resid)),
                     "n": len(resid)})
        print(f"    {titulo:<42} r do QQ = {r:.4f}")

    # mortalidade (ZIB): massa em zero aleatorizada + Beta no interior
    for chave, titulo in [("mortalidade", "Mortalidade geral (ZIB)"),
                          ("mort_ajustada", "Mortalidade ajustada (ZIB)")]:
        if chave not in resultados:
            continue
        r0 = resultados[chave]
        d, col = r0["amostra"], r0["col"]
        pi = np.asarray(r0["res_zero"].predict(d))
        mu, phi = _beta_mu_phi(r0["mod_beta"], r0["res_beta"], r0["X"])
        u = np.empty(len(d))
        y = d[col].to_numpy()
        eh_zero = y == 0
        u[eh_zero] = rng.uniform(0, pi[eh_zero])
        F = stats.beta.cdf(y[~eh_zero], mu * phi, (1 - mu) * phi)
        u[~eh_zero] = pi[~eh_zero] + (1 - pi[~eh_zero]) * F
        registrar("mort_zib" if chave == "mortalidade" else "mort_ajustada_zib",
                  titulo, stats.norm.ppf(np.clip(u, 1e-7, 1 - 1e-7)))

    # fração de alta complexidade (ZOIB): massas em zero e um + Beta
    r0 = resultados["pct_alta"]
    d, col = r0["amostra"], r0["col"]
    p0 = np.asarray(r0["res_zero"].predict(d))
    p1 = np.asarray(r0["res_um"].predict(d))
    mu, phi = _beta_mu_phi(r0["mod_beta"], r0["res_beta"], r0["X"])
    y = d[col].to_numpy()
    u = np.empty(len(d))
    eh_zero, eh_um = y == 0, y == 1
    interior = ~(eh_zero | eh_um)
    u[eh_zero] = rng.uniform(0, p0[eh_zero])
    u[eh_um] = rng.uniform(1 - p1[eh_um], 1)
    F = stats.beta.cdf(y[interior], mu * phi, (1 - mu) * phi)
    u[interior] = (p0[interior]
                   + (1 - p0[interior] - p1[interior]) * F)
    registrar("pct_alta_zoib", "Fração alta complexidade (ZOIB)",
              stats.norm.ppf(np.clip(u, 1e-7, 1 - 1e-7)))

    # produção (Binomial Negativa): PIT aleatorizado da discreta
    r0 = resultados["producao"]
    res, d = r0["res"], r0["amostra"]
    mu = np.asarray(res.predict(d))
    alpha = float(r0["alpha"])
    size = 1 / alpha
    prob = size / (size + mu)
    y = d["qtde"].to_numpy()
    Fy = stats.nbinom.cdf(y, size, prob)
    Fy1 = stats.nbinom.cdf(y - 1, size, prob)
    u = rng.uniform(Fy1, Fy)
    registrar("producao_bn", "Produção (Binomial Negativa)",
              stats.norm.ppf(np.clip(u, 1e-7, 1 - 1e-7)))

    # modelos gaussianos no log: resíduos padronizados
    for chave, slug, titulo in [
            ("custo", "custo_fe", "Custo real (log, efeitos fixos)"),
            ("tmp", "tmp_fe", "TMP (log, efeitos fixos)"),
            ("ocup_int", "ocup_internacao", "Ocupação internação (log)")]:
        res = resultados[chave]["res"]
        registrar(slug, titulo, res.resid / np.std(res.resid, ddof=1))
    res2 = resultados["ocup_uti"]["res2"]
    registrar("ocup_uti_pos", "Ocupação UTI (log, positivos)",
              res2.resid / np.std(res2.resid, ddof=1))

    _tab(pd.DataFrame(diag).round(4), "tab_est_residuos_quantilicos.csv",
         index=False)


def robustez(painel, resultados):
    print("\n" + "=" * 70)
    print("[4] ROBUSTEZ: sem o biênio 2020 e 2021, mortalidade ajustada, "
          "resíduos quantílicos")
    print("=" * 70)

    # 4a. reestimação sem 2020 e 2021
    sem = painel[~painel["ano"].isin([2020, 2021])].copy()
    print(f"\n  Amostra sem 2020 e 2021: {len(sem)} observações")
    res_sem = modelos_principais(sem, sufixo="_sem_pandemia", verboso=False)
    estudo_eventos(sem, sufixo="_sem_pandemia", fazer_figuras=False)

    comp = []
    for ch in resultados:
        rc, rs = resultados[ch], res_sem[ch]
        comp.append({
            "modelo": rc["rotulo"], "escala": rc["escala"],
            "coef_oss_completo": rc["oss"], "ep_completo": rc["ep"],
            "coef_oss_sem_pandemia": rs["oss"], "ep_sem_pandemia": rs["ep"],
            "efeito_pct_completo": 100 * (np.exp(rc["oss"]) - 1)
                if rc["escala"] == "log" else np.nan,
            "efeito_pct_sem_pandemia": 100 * (np.exp(rs["oss"]) - 1)
                if rs["escala"] == "log" else np.nan})
    tab_comp = pd.DataFrame(comp).round(4)
    _tab(tab_comp, "tab_est_robustez_sem_pandemia.csv", index=False)
    print("\n  OSS vs Direta, painel completo vs sem 2020 e 2021:")
    print(tab_comp[["modelo", "coef_oss_completo",
                    "coef_oss_sem_pandemia"]].to_string(index=False))

    # figura comparativa (modelos em log, efeito percentual)
    em_log = tab_comp[tab_comp["escala"] == "log"]
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    ys = np.arange(len(em_log))[::-1]
    ax.axvline(0, color=COR_EIXO, lw=1)
    for y, (_, ln) in zip(ys, em_log.iterrows()):
        ax.plot([ln["efeito_pct_completo"]], [y], marker="o",
                color=COR_APOIO, ms=7,
                label="Painel completo" if y == ys[0] else None)
        ax.plot([ln["efeito_pct_sem_pandemia"]], [y], marker="s",
                color=CORES_CAT["OSS"], ms=7,
                label="Sem 2020 e 2021" if y == ys[0] else None)
        ax.plot([ln["efeito_pct_completo"], ln["efeito_pct_sem_pandemia"]],
                [y, y], color=COR_GRADE, lw=1.6, zorder=1)
    ax.set_yticks(ys)
    ax.set_yticklabels(em_log["modelo"], fontsize=10.5)
    ax.set_xlabel("Efeito OSS vs Direta (%)")
    ax.set_title("Robustez: contraste OSS vs Direta com e sem o biênio "
                 "pandêmico", fontsize=11)
    ax.legend(fontsize=9.5, loc="lower right")
    fig.tight_layout()
    _salvar(fig, "fig_est_05_robustez_sem_pandemia.png")

    # 4b. mortalidade ajustada como checagem
    print("\n  CHECAGEM: mortalidade ajustada (sem óbitos fetais, maternos "
          "e neonatais)")
    resultados["mort_ajustada"] = modelo_mortalidade(
        painel, col="mort_sem_excl", sufixo="_ajustada", verboso=True)

    # 4c. resíduos quantílicos dos modelos ajustados
    residuos_quantilicos(resultados)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    bloco = sys.argv[1] if len(sys.argv) > 1 else "todos"
    PASTA_FIG_EST.mkdir(parents=True, exist_ok=True)

    painel = carregar_e_verificar()
    painel = preparar(painel)
    if bloco == "prep":
        print("\n[prep] Concluído. Próximo passo: python estimacao.py "
              "principais")
        return

    if bloco in ("principais", "todos"):
        resultados = modelos_principais(painel)
    if bloco == "principais":
        print("\n[principais] Concluído. Próximo passo: python estimacao.py "
              "gestao")
        return

    if bloco in ("gestao", "todos"):
        if bloco == "gestao":
            resultados = modelos_principais(painel, verboso=False)
        figura_contraste_oss(resultados)
        estudo_eventos(painel)
    if bloco == "gestao":
        print("\n[gestao] Concluído. Próximo passo: python estimacao.py "
              "robustez")
        return

    if bloco in ("robustez", "todos"):
        if bloco == "robustez":
            resultados = modelos_principais(painel, verboso=False)
        robustez(painel, resultados)
        print("\n[robustez] Concluído. Entregáveis: relatório e LaTeX.")


if __name__ == "__main__":
    main()
