"""
A selecao dos blocos b e c muda se o criterio deixar de usar a SFA?

Motivo da pergunta: R11 estabelece que nenhum coeficiente nem nivel da
fronteira estocastica e citavel. O criterio de `_selecionar_extremos` em
`selecao_entrevistas.py` usa a SFA duas vezes: no filtro (quartil em DEA
*E* em SFA) e no desempate (`pct_comb`, que e a media dos percentis de DEA
e de SFA). Se a lista de entrevistados mudar ao remover a SFA, a tarja nao
se resolve por redacao e a selecao precisa ser refeita.

Este script NAO altera nada e NAO regera nenhuma tabela. Ele reconstroi o
mesmo `eleg` de `selecao_entrevistas.py` a partir das fontes e roda o
criterio nas duas versoes, lado a lado.

Regra 7 do projeto: nenhum numero entra em relatorio sem ser reproduzido.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
F2 = RAIZ / "resultados_fase2"

# as constantes geograficas e a tolerancia de empate vem do proprio script de
# selecao, para que o desempate seja o mesmo e nao uma copia que envelhece.
# selecao_entrevistas.py tem guarda __main__, entao importa-lo nao executa nada.
sys.path.insert(0, str(RAIZ))
import selecao_entrevistas as sel  # noqa: E402

CONVERSORES = [2081695, 2078287, 2082225, 2091755, 2750511]
CNES_FRAGIL = 2097613
ANOS_FRAGIL = (2020, 2021)
CATEGORIAS_BC = ["OSS", "Direta", "Público Municipal", "Filantrópico"]

# o que o documento publica hoje nos blocos b e c (sec16 e apendice de
# selecao), para conferir se esta reproducao bate antes de acreditar nela
PUBLICADOS = {
    "b": {"OSS": 7573162, "Direta": 6164366,
          "Público Municipal": 5718368, "Filantrópico": 2076896},
    "c": {"OSS": None, "Direta": 2028840,
          "Público Municipal": 2698471, "Filantrópico": 2078465},
}


def cab(t):
    print("\n" + "=" * 74)
    print(t)
    print("=" * 74)


# ---------------------------------------------------------------- fontes
painel = pd.read_csv(RAIZ / "analises" / "painel_definitivo.csv")
painel["flag_fragil"] = ((painel["cnes"] == CNES_FRAGIL)
                         & painel["ano"].isin(ANOS_FRAGIL)).astype(int)

# longa permanencia, como estimacao.py a define: CNES com TMP mediano > 20 d.
_tmp_med = painel.groupby("cnes")["tmp"].median()
painel["longa_perm"] = painel["cnes"].isin(
    set(_tmp_med[_tmp_med > 20].index)).astype(int)
print(f"longa permanencia: {int(painel['longa_perm'].sum())} obs em "
      f"{painel.loc[painel['longa_perm'] == 1, 'cnes'].nunique()} CNES")

dea = pd.read_csv(F2 / "dea" / "dea_escores_principal.csv")[
    ["cnes", "ano", "te_bcc_vc"]]
sfa = pd.read_csv(F2 / "sfa" / "sfa_eficiencias.csv")[["cnes", "ano", "te_sfa"]]

p = painel.merge(dea, on=["cnes", "ano"], how="left") \
          .merge(sfa, on=["cnes", "ano"], how="left")
print(f"painel {len(painel)} obs; te_bcc_vc {p['te_bcc_vc'].notna().sum()}; "
      f"te_sfa {p['te_sfa'].notna().sum()}")

# porte fixo pela mediana de leitos dos onze anos, como o projeto define
med_leitos = painel.groupby("cnes")["total_leitos"].median()
porte = med_leitos.map(lambda x: "Médio Porte" if x <= 150
                       else ("Grande Porte" if x <= 500 else "Especial"))

ok = p[p["flag_fragil"] == 0]
resumo = ok.groupby("cnes").agg(
    faixa_barcelona=("faixa_barcelona", lambda s: int(s.mode().iloc[0])),
    longa_perm=("longa_perm", "max"),
    te_dea_med=("te_bcc_vc", "median"),
    te_sfa_med=("te_sfa", "median"),
)
resumo["porte_fixo"] = porte
resumo["geografia"] = painel.groupby("cnes")["cod_ibge"].agg(
    lambda s: s.dropna().iloc[-1]).map(sel._estrato_geografico)
resumo["categoria"] = painel.groupby("cnes")["modelo_gestao_proxy"].agg(
    lambda s: s.mode().iloc[0])
resumo.loc[[c for c in CONVERSORES if c in resumo.index],
           "categoria"] = "OSS (conversor)"

eleg = resumo[(~resumo["categoria"].isin(["Privado", "OSS (conversor)"]))
              & (resumo.index != CNES_FRAGIL)].copy()
eleg["pct_dea"] = eleg["te_dea_med"].rank(pct=True)
eleg["pct_sfa"] = eleg["te_sfa_med"].rank(pct=True)
eleg["pct_comb"] = (eleg["pct_dea"] + eleg["pct_sfa"]) / 2
print(f"rede elegivel: {len(eleg)} CNES")

pool = eleg[eleg["faixa_barcelona"].isin([3, 4])
            & eleg["porte_fixo"].isin(["Médio Porte", "Grande Porte"])
            & (eleg["longa_perm"] == 0)].copy()
print(f"suporte comum sem longa permanencia: {len(pool)} CNES")


def escolher(superior: bool, usar_sfa: bool):
    """Reproduz _selecionar_extremos; usar_sfa=False remove a SFA do filtro
    e troca o desempate de pct_comb por pct_dea."""
    q_dea = pool["te_dea_med"].quantile(.75 if superior else .25)
    q_sfa = pool["te_sfa_med"].quantile(.75 if superior else .25)
    med_sfa = pool["te_sfa_med"].median()
    chave = "pct_comb" if usar_sfa else "pct_dea"
    out, geografias = {}, []
    for cat in CATEGORIAS_BC:
        base = pool[pool["categoria"] == cat]
        if superior:
            cand = base[base["te_dea_med"] >= q_dea]
            if usar_sfa:
                cand = cand[cand["te_sfa_med"] >= q_sfa]
        else:
            cand = base[base["te_dea_med"] <= q_dea]
            if usar_sfa:
                cand = cand[cand["te_sfa_med"] <= q_sfa]
        relax = False
        if cand.empty and usar_sfa:
            cand = base[(base["te_dea_med"] >= q_dea)
                        & (base["te_sfa_med"] >= med_sfa)] if superior else \
                   base[(base["te_dea_med"] <= q_dea)
                        & (base["te_sfa_med"] <= med_sfa)]
            relax = True
        if cand.empty:
            out[cat] = (None, relax, 0)
            continue
        cand = cand.sort_values(chave, ascending=not superior)
        melhor = cand.iloc[0]
        # mesmo desempate geografico do script de selecao, sobre a mesma chave
        quase = cand[(cand[chave] - melhor[chave]).abs() < sel.TOL_EMPATE]
        if len(quase) > 1 and geografias:
            disponiveis = list(dict.fromkeys(quase["geografia"]))
            falta = min(disponiveis, key=geografias.count)
            alt = quase[quase["geografia"] == falta]
            if not alt.empty:
                melhor = alt.iloc[0]
        geografias.append(melhor["geografia"])
        out[cat] = (int(melhor.name), relax, len(cand))
    return out


for superior, rot in ((True, "b: DESVIANTES POSITIVOS (quartil superior)"),
                      (False, "c: DESVIANTES NEGATIVOS (quartil inferior)")):
    cab(rot)
    com = escolher(superior, usar_sfa=True)
    sem = escolher(superior, usar_sfa=False)
    print(f"  {'categoria':<20} {'COM SFA':>10} {'SEM SFA':>10}  "
          f"{'cands':>11}  muda?")
    for cat in CATEGORIAS_BC:
        c_id, c_rx, c_n = com[cat]
        s_id, s_rx, s_n = sem[cat]
        muda = "MUDA" if c_id != s_id else "igual"
        pub = PUBLICADOS[rot[0]].get(cat)
        bate = "confere" if pub == c_id else f"NAO BATE (publicado {pub})"
        print(f"  {cat:<20} {str(c_id):>10} {str(s_id):>10}  "
              f"{c_n:>4} -> {s_n:<4}  {muda:<6} reproducao: {bate}"
              + ("   [relaxado]" if c_rx else ""))

cab("leitura")
print("Se alguma linha diz MUDA, a tarja da SFA nao se resolve por redacao")
print("nos blocos b e c: a lista de entrevistados depende da fronteira")
print("paramétrica e precisa ser refeita so com o DEA.")
