# -*- coding: utf-8 -*-
"""
ETAPA 4 — Reestimação segmentada por estrato estrutural (CRE/Mundlak).

Modo piloto
-----------
    python estimacao_segmentada.py --piloto

Roda SOMENTE `tmp` em E3, imprime a saída e PARA. É o ponto de parada
obrigatório da Etapa 4: o escopo completo não roda sem aval explícito.

RESTRIÇÕES DE INTERPRETAÇÃO — leia antes de citar qualquer coeficiente
======================================================================

1. FORA DE E3 NÃO HÁ IDENTIFICAÇÃO WITHIN. Quatro dos cinco switchers
   Direta→OSS estão em E3 (Sorocaba 2081695, Pérola 2078287, Taipas 2082225,
   Vila Penteado 2091755); Odilo Antunes 2750511 está em E2. Coeficiente de
   OSS em E1 ou E2 é COMPARAÇÃO ENTRE GRUPOS, não efeito causal, e sai
   marcado como tal na coluna `identificacao`.

2. A identificação causal do efeito OSS repousa sobre SORORABA e PÉROLA, os
   únicos com pós-tratamento longo, ambos com confundidores documentados:
   endogeneidade da conversão em Sorocaba, mudança de prédio em Pérola, e o
   mesmo operador nos cinco. Não é um desenho limpo; é o desenho disponível.

3. O PAR DESCRITIVO DE MORTALIDADE DE E3 (Direta ≈ 0,0698, OSS ≈ 0,0536) NÃO
   É CITÁVEL COMO ACHADO. É assimetria de cauda vinda de 2 CNES em faixa 6
   num grupo de 20 — não casemix médio mais pesado; o escore Barcelona médio
   das duas categorias é praticamente idêntico (455,9 contra 455,6). Ver R2.

4. O GRUPO PRIVADO NÃO É INTERPRETADO em nenhum estrato (n = 3 CNES, e
   desaparece de E3).

5. EM E1 O MODELO DE OCUPAÇÃO DE UTI NÃO EXISTE. E1 é "sem UTI SUS" pela
   mediana; reportado como NÃO-APLICÁVEL, nunca rodado com zeros.

SALVAGUARDA DE CIRCULARIDADE
----------------------------
`complexidade_pond_mort` JAMAIS entra como regressor, em nenhum modelo, e em
particular não nos de mortalidade: é construída a partir do próprio desfecho.
A única covariável de complexidade é `complexidade_estrutural`, que PERMANECE
dentro do estrato porque o estrato tem 3 níveis e o escore varia de 18 a 2336
dentro dele.

FORMA FUNCIONAL DA OCUPAÇÃO DE INTERNAÇÃO (R6) — duas partes
-------------------------------------------------------------
Parte A: binário `sobrecarga = ocupacao_internacao > 100`, logístico.
Parte B: contínua restrita a ≤ 100, SEM winsorização (o teto é 100 por
construção). As duas são reportadas e interpretadas conjuntamente; não se
somam nem se colapsam em índice único.

Motivo: ocupação acima de 100% é a assinatura aritmética da superlotação — o
CNES registra capacidade habilitada e exclui leito extra, o SIH fatura diária
para maca e leito de observação acima de 24 horas. Winsorizar apagaria o
sinal; a contínua bruta conflacionaria frequência de superlotação com nível de
ocupação. No painel definitivo essa conflação é de 23% do gap OSS−Direta em
E3 (bruto +27,4 pontos, contínua +21,1). Ver R1 v4 e R6.

OCUPAÇÃO DE UTI — contínua, limiar ÚNICO
-----------------------------------------
`ocupacao_uti_valida` (definida onde `uti_sus > 0`), winsorizada no p99 da
SUBAMOSTRA VÁLIDA, com limiar ÚNICO para o painel inteiro: 180,5. Nunca por
estrato — daria 234,0 em E2 contra 152,7 em E3, e limiares diferentes tornam o
desfecho incomparável entre estratos.

Divergimos deliberadamente de `preparo_fase2.R`, que winsoriza no p99 do
painel completo, contaminado pelos zeros estruturais (171,2). Aquele limiar é
ele próprio artefato do bug corrigido na Etapa 1. Ver R8.

A assimetria com a internação é empírica e foi verificada: o excesso acima de
100% é fortemente diferencial em internação (OSS 29,3% contra Direta 3,9%,
razão 7,6) e não-diferencial em UTI (4,7% contra 5,2%, razão 0,9).

PISO DE REPORTE
---------------
Célula com menos de 10 CNES recebe a tarja `[n<10]`. NÃO é suprimida: o funil
precisa ficar auditável, e célula pequena omitida é indistinguível de célula
que não existe.

Ver `verificar_prespecificacoes_etapa4.py` (premissas) e
`RESTRICOES_SEGMENTACAO.md` (R1 a R8).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

RAIZ = Path(__file__).resolve().parent
PAINEL = RAIZ / "analises" / "painel_segmentado.csv"

# IPCA anual (variação % dez/dez, IBGE); 2025 fechado em 4,26%.
# Mesma tabela de estimacao.py — reproduzida para não importar aquele script,
# que roda o pipeline inteiro ao ser carregado.
IPCA_ANUAL = {2015: 10.67, 2016: 6.29, 2017: 2.95, 2018: 3.75, 2019: 4.31,
              2020: 4.52, 2021: 10.06, 2022: 5.79, 2023: 4.62, 2024: 4.83,
              2025: 4.26}

CNES_FRAGIL = 2097613
ANOS_FRAGIL = (2020, 2021)

SWITCHERS = {2081695: "Sorocaba", 2078287: "Pérola", 2082225: "Taipas",
             2091755: "Vila Penteado", 2750511: "Odilo Antunes"}
SWITCHERS_E3 = {2081695, 2078287, 2082225, 2091755}

CAT = "C(modelo_gestao_proxy, Treatment('Direta'))"
PORTE = "C(porte_fixo, Treatment('Médio Porte'))"

PISO_CNES = 10


def _fatores_ipca_2025() -> dict:
    anos = sorted(IPCA_ANUAL)
    indice, acum = {}, 1.0
    for a in anos:
        acum *= 1 + IPCA_ANUAL[a] / 100
        indice[a] = acum
    return {a: indice[anos[-1]] / indice[a] for a in anos}


def preparar() -> pd.DataFrame:
    """Replica as regras vigentes do projeto sobre o painel segmentado."""
    if not PAINEL.exists():
        sys.exit(f"painel não encontrado: {PAINEL}")
    p = pd.read_csv(PAINEL)
    n_cnes, n_anos = p["cnes"].nunique(), p["ano"].nunique()
    if len(p) != n_cnes * n_anos:
        sys.exit("painel não balanceado — abortando")
    print(f"painel: {len(p)} obs, {n_cnes} CNES, {n_anos} anos")

    # faturamento real a preços de 2025, fator IPCA POR ANO
    p["custo_real"] = p["custo_saida"] * p["ano"].map(_fatores_ipca_2025())

    # porte fixo por CNES, pela mediana de leitos (cortes oficiais 50/150/500)
    def _porte(l):
        return ("HPP" if l <= 50 else "Médio Porte" if l <= 150
                else "Grande Porte" if l <= 500 else "Especial")
    p["porte_fixo"] = p["cnes"].map(
        p.groupby("cnes")["total_leitos"].median().apply(_porte))

    # denominador frágil documentado (2 obs do CNES 2097613)
    p["flag_fragil"] = ((p["cnes"] == CNES_FRAGIL)
                        & p["ano"].isin(ANOS_FRAGIL)).astype(int)

    # termo de Mundlak: média da dummy OSS por hospital. É o único regressor
    # com variação within (os 5 conversores); a média por CNES separa o
    # componente between do within, que é o efeito causal de interesse.
    p["d_oss"] = (p["modelo_gestao_proxy"] == "OSS").astype(int)
    p["media_oss"] = p.groupby("cnes")["d_oss"].transform("mean")
    n_sw = p.loc[p["media_oss"].between(0.001, 0.999), "cnes"].nunique()
    print(f"  Mundlak (media_oss): {n_sw} CNES com valor intermediário "
          f"— os conversores")

    # duas partes da ocupação de internação (R6)
    p["sobrecarga"] = (p["ocupacao_internacao"] > 100).astype(int)
    p["ocup_int_cond"] = p["ocupacao_internacao"].where(
        p["ocupacao_internacao"] <= 100)

    # ocupação de UTI winsorizada: p99 da SUBAMOSTRA VÁLIDA, limiar único
    valida = p["ocupacao_uti_valida"].dropna()
    p99 = float(np.percentile(valida, 99))
    p["ocup_uti_w"] = p["ocupacao_uti_valida"].clip(upper=p99)
    n_w = int((p["ocupacao_uti_valida"] > p99).sum())
    print(f"  Winsorização UTI: limiar único {p99:.1f} (p99 da subamostra "
          f"válida, n={len(valida)}); {n_w} obs winsorizadas")

    return p


def amostra_desfecho(p: pd.DataFrame) -> pd.DataFrame:
    return p[p["flag_fragil"] == 0]


def tarja(n_cnes: int) -> str:
    return "[n<10]" if n_cnes < PISO_CNES else ""


def identificacao(estrato: str, d: pd.DataFrame) -> str:
    """Rótulo honesto sobre o que o coeficiente de OSS significa ali."""
    sw = set(d.loc[d["media_oss"].between(0.001, 0.999), "cnes"])
    if estrato == "E3" and sw:
        return f"within ({len(sw)} conversores)"
    if sw:
        return (f"within FRACA ({len(sw)} conversor) — "
                f"NÃO INTERPRETAR COMO CAUSAL")
    return "ENTRE GRUPOS — NÃO É EFEITO CAUSAL"


def cre_mundlak(d: pd.DataFrame, col: str, estrato: str, *,
                log: bool = False, binario: bool = False) -> dict:
    """CRE/Mundlak dentro de um estrato, EP agrupados por CNES.

    Fórmula: y ~ categoria + complexidade_estrutural + porte + C(ano)
                 + media_oss

    `complexidade_pond_mort` NUNCA entra (salvaguarda de circularidade).
    O termo de Mundlak `media_oss` separa between de within: com ele, o
    coeficiente da dummy OSS é o efeito within, identificado pelos
    conversores.
    """
    d = d.dropna(subset=[col]).copy()
    if d.empty:
        return {"erro": "amostra vazia"}

    d["y"] = np.log(d[col]) if log else d[col]

    # porte e categoria só entram com variação; em estrato pequeno podem
    # colapsar em nível único e tornar a coluna singular no patsy
    termos = [CAT, "complexidade_estrutural", "C(ano)", "media_oss"]
    if d["porte_fixo"].nunique() > 1:
        termos.insert(2, PORTE)
    else:
        print(f"    [{estrato}] porte_fixo sem variação "
              f"({d['porte_fixo'].iloc[0]}) — termo excluído")
    if d["media_oss"].nunique() == 1:
        termos.remove("media_oss")
        print(f"    [{estrato}] media_oss sem variação — Mundlak inestimável; "
              f"SEM identificação within")

    f = "y ~ " + " + ".join(termos)
    try:
        if binario:
            res = smf.logit(f, data=d).fit(
                disp=0, maxiter=200, method="bfgs",
                cov_type="cluster", cov_kwds={"groups": d["cnes"]})
            conv = res.mle_retvals.get("converged", True)
        else:
            res = smf.ols(f, data=d).fit(
                cov_type="cluster", cov_kwds={"groups": d["cnes"]})
            conv = True
    except Exception as e:                     # noqa: BLE001
        return {"erro": f"{type(e).__name__}: {e}"}

    alvo = [n for n in res.params.index if "T.OSS" in n]
    if not alvo:
        return {"erro": "dummy OSS ausente da matriz de desenho"}
    coef, ep = float(res.params[alvo[0]]), float(res.bse[alvo[0]])

    return {"formula": f, "res": res, "n_obs": len(d),
            "n_cnes": d["cnes"].nunique(), "coef_oss": coef, "ep_oss": ep,
            "z": coef / ep, "p": float(res.pvalues[alvo[0]]),
            "ic_baixo": coef - 1.96 * ep, "ic_alto": coef + 1.96 * ep,
            "convergiu": conv, "log": log, "binario": binario,
            "identificacao": identificacao(estrato, d),
            "tarja": tarja(int(d.loc[d["modelo_gestao_proxy"] == "OSS",
                                     "cnes"].nunique()))}


def imprimir(r: dict, rotulo: str) -> None:
    if "erro" in r:
        print(f"\n  {rotulo}: FALHOU — {r['erro']}")
        return
    print(f"\n  {rotulo}")
    print(f"    fórmula: {r['formula']}")
    print(f"    n = {r['n_obs']} obs, {r['n_cnes']} CNES  {r['tarja']}")
    print(f"    identificação: {r['identificacao']}")
    if not r["convergiu"]:
        print("    ATENÇÃO: o modelo NÃO convergiu")
    esc = "log" if r["log"] else ("logito" if r["binario"] else "nível")
    print(f"    OSS vs Direta: {r['coef_oss']:+.4f} ({esc}), "
          f"EP agrupado {r['ep_oss']:.4f}")
    print(f"    IC95%: [{r['ic_baixo']:+.4f}, {r['ic_alto']:+.4f}]   "
          f"z = {r['z']:+.2f}   p = {r['p']:.3f}")
    if r["log"]:
        pct = 100 * (np.exp(r["coef_oss"]) - 1)
        lo = 100 * (np.exp(r["ic_baixo"]) - 1)
        hi = 100 * (np.exp(r["ic_alto"]) - 1)
        print(f"    efeito: {pct:+.1f}%  IC95% [{lo:+.1f}%, {hi:+.1f}%]")


def piloto(p: pd.DataFrame) -> None:
    print("\n" + "=" * 72)
    print("PILOTO — tmp em E3, CRE/Mundlak. Nada além disto roda.")
    print("=" * 72)

    d = amostra_desfecho(p)
    e3 = d[d["estrato"] == "E3"]
    print(f"\n  E3: {len(e3)} obs, {e3['cnes'].nunique()} CNES")
    print("  CNES por categoria:")
    for cat, n in e3.groupby("modelo_gestao_proxy")["cnes"].nunique().items():
        print(f"    {cat:<20} {n:>3} {tarja(int(n))}")

    sw = sorted(set(e3["cnes"]) & SWITCHERS_E3)
    print(f"\n  Conversores presentes em E3: {len(sw)} — "
          + ", ".join(SWITCHERS[c] for c in sw))
    for c in sw:
        s = e3[e3["cnes"] == c]
        anos_oss = sorted(s.loc[s["d_oss"] == 1, "ano"])
        print(f"    {c} {SWITCHERS[c]:<15} anos como OSS: "
              f"{anos_oss[0] if anos_oss else '—'}–{anos_oss[-1] if anos_oss else '—'}"
              f" ({len(anos_oss)} de {len(s)})")

    print(f"\n  tmp em E3: mediana por categoria")
    print(e3.groupby("modelo_gestao_proxy")["tmp"]
          .agg(n="size", mediana="median", media="mean").round(2).to_string())

    r = cre_mundlak(e3, "tmp", "E3", log=True)
    imprimir(r, "TMP (log) — E3 — CRE/Mundlak")

    if "erro" not in r:
        print("\n  Coeficientes completos (sem as dummies de ano):")
        t = pd.DataFrame({"coef": r["res"].params, "ep_cluster": r["res"].bse,
                          "z": r["res"].tvalues, "p": r["res"].pvalues})
        print(t[~t.index.str.startswith("C(ano)")].round(4).to_string())

    print("\n" + "=" * 72)
    print("PILOTO CONCLUÍDO. PARADA OBRIGATÓRIA.")
    print("O escopo completo (cinco indicadores × três famílias) NÃO roda")
    print("sem aval explícito sobre esta saída.")
    print("=" * 72)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--piloto", action="store_true",
                    help="roda somente tmp em E3 e para")
    args = ap.parse_args()

    p = preparar()
    if args.piloto:
        piloto(p)
        return
    sys.exit("escopo completo ainda não liberado — rode com --piloto")


if __name__ == "__main__":
    main()
