"""Efeitos interpretáveis da tabela de robustez sem o biênio pandêmico.

Motivo: a Tabela `tab:sempandemia` da Seção 13 imprime só coeficientes na
escala interna de cada modelo. Cinco dos sete modelos já têm o efeito em
variação percentual gravado em `tab_est_robustez_sem_pandemia.csv`
(colunas `efeito_pct_*`), calculado como 100*(exp(coef)-1) porque a escala
é log. Os outros dois, mortalidade e fração de alta complexidade, estão em
logito Beta: ali exp(coef)-1 NÃO é variação percentual da média, e as
colunas de efeito estão vazias.

Este script calcula, para esses dois modelos e nas duas amostras, o
EFEITO MARGINAL MÉDIO em pontos percentuais do desfecho, que é a
quantidade interpretável correta.

Mortalidade (Beta com inflação em zero), E[y] = (1 - pi0) * mu:
    AME = media(mu * (1 - mu)) * b_oss * (1 - media(pi0)) * 100
que é exatamente a fórmula já usada em estimacao.py:444 — reproduzida aqui
para conferência e estendida à amostra sem pandemia.

Alta complexidade (ZOIB), E[y] = pi1 + (1 - pi0 - pi1) * mu:
    AME = media(mu * (1 - mu)) * b_oss * (1 - media(pi0) - media(pi1)) * 100
mesma construção, com a massa em um entrando no fator de escala.

O erro-padrão do AME usa a aproximação de fator de escala fixo
(EP_ame = fator * EP_oss), coerente com o ponto: propaga só a incerteza do
coeficiente OSS da componente Beta, tratando mu e as probabilidades das
massas como dadas. Não é delta method completo, e está declarado como tal.

Reprodução: python analises/auditar_efeitos_robustez.py
Não escreve nenhum arquivo de resultado do projeto (o _tab é neutralizado).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import estimacao as E  # noqa: E402

# não sobrescrever nenhuma tabela do projeto durante a auditoria
E._tab = lambda *a, **k: None


def ame_mortalidade(r):
    """AME em p.p. do contraste OSS vs Direta, Beta com inflação em zero."""
    X = r["X"]
    params = np.asarray(r["res_beta"].params)
    i_oss = [i for i, n in enumerate(X.columns) if "[T.OSS]" in n][0]
    mu = r["mod_beta"].predict(params, exog=np.asarray(X))
    pi0 = r["res_zero"].predict(r["amostra"])
    fator = float(np.mean(mu * (1 - mu)) * (1 - pi0.mean()) * 100)
    return fator * r["oss"], fator * r["ep"], fator


def ame_pct_alta(r):
    """AME em p.p. do contraste OSS vs Direta, ZOIB (zero e um inflados)."""
    X = r["X"]
    params = np.asarray(r["res_beta"].params)
    i_oss = [i for i, n in enumerate(X.columns) if "[T.OSS]" in n][0]
    mu = r["mod_beta"].predict(params, exog=np.asarray(X))
    pi0 = r["res_zero"].predict(r["amostra"])
    pi1 = r["res_um"].predict(r["amostra"])
    fator = float(np.mean(mu * (1 - mu))
                  * (1 - pi0.mean() - pi1.mean()) * 100)
    return fator * r["oss"], fator * r["ep"], fator


def main():
    painel = E.preparar(E.carregar_e_verificar())
    sem = painel[~painel["ano"].isin([2020, 2021])].copy()

    linhas = []
    for rotulo_am, dados in [("painel completo", painel),
                             ("sem 2020 e 2021", sem)]:
        rm = E.modelo_mortalidade(dados, verboso=False)
        rp = E.modelo_pct_alta(dados, verboso=False)
        for nome, r, fn in [("Mortalidade (geral)", rm, ame_mortalidade),
                            ("Fração alta complexidade", rp, ame_pct_alta)]:
            ame, ep_ame, fator = fn(r)
            linhas.append({
                "amostra": rotulo_am, "modelo": nome,
                "coef": r["oss"], "ep": r["ep"],
                "razao_chances": np.exp(r["oss"]),
                "ame_pp": ame, "ep_ame_pp": ep_ame,
                "ic_baixo_pp": ame - 1.96 * ep_ame,
                "ic_alto_pp": ame + 1.96 * ep_ame,
                "fator_escala": fator,
                "media_desfecho": float(dados[r["col"]].dropna().mean()) * 100,
            })

    tab = pd.DataFrame(linhas)
    pd.set_option("display.width", 200)
    print("\n" + "=" * 78)
    print("EFEITOS MARGINAIS MEDIOS — modelos em logito Beta")
    print("=" * 78)
    print(tab.round(4).to_string(index=False))

    print("\n" + "-" * 78)
    print("Confere contra o que ja esta gravado no projeto:")
    for nome, arq in [("painel completo", "tab_est_resumo_oss.csv"),
                      ("sem 2020 e 2021",
                       "tab_est_resumo_oss_sem_pandemia.csv")]:
        g = pd.read_csv(RAIZ / "analises" / "tabelas" / arq)
        v = g.loc[g["modelo"] == "Mortalidade (geral)", "ame_pp"].iloc[0]
        n = tab.loc[(tab["amostra"] == nome)
                    & (tab["modelo"] == "Mortalidade (geral)"),
                    "ame_pp"].iloc[0]
        print(f"  mortalidade {nome:<16} gravado {v:+.4f} | "
              f"recalculado {n:+.4f} | bate: {abs(v - n) < 1e-3}")

    print("\n" + "-" * 78)
    print("Efeitos em escala log ja gravados (conferencia):")
    rob = pd.read_csv(RAIZ / "analises" / "tabelas"
                      / "tab_est_robustez_sem_pandemia.csv")
    print(rob[["modelo", "escala", "coef_oss_completo",
               "efeito_pct_completo", "coef_oss_sem_pandemia",
               "efeito_pct_sem_pandemia"]].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
