# -*- coding: utf-8 -*-
"""
ETAPA 4 — Reestimação segmentada por estrato estrutural (CRE/Mundlak).

Modos
-----
    python estimacao_segmentada.py --piloto     # só tmp em E3, e para
    python estimacao_segmentada.py --completo   # cinco indicadores × estratos

O piloto foi o ponto de parada obrigatório da Etapa 4 e foi aprovado em
28/07/2026; o escopo completo ficou liberado a partir daí.

CINCO INDICADORES
-----------------
`mort_all`, `tmp`, `custo_real` (deflacionado por fator IPCA anual),
`ocupacao_uti_valida` (winsorizada, limiar único) e `ocupacao_internacao`
(duas partes, R6).

Forma funcional de cada um, e por que:

  mort_all      logito fracionário (GLM Binomial, quasi-verossimilhança).
                Diverge do Beta com inflação em zero de `estimacao.py`: dentro
                de estrato o componente de inflação fica inestimável por
                separação (E3 não tem NENHUM zero; E1 tem 3). O logito
                fracionário acomoda zeros sem componente extra e é consistente
                sob má-especificação da variância. Divergência registrada.
  tmp           log, MQO.
  custo_real    log, MQO.
  ocup. UTI     log da winsorizada, MQO, na subamostra VÁLIDA (`uti_sus > 0`).
                NÃO condiciona em `ocupacao_uti > 0` — isso seria condicionar
                no desfecho, que é o defeito 2 de R8.
  ocup. intern. parte A logito do binário; parte B log da contínua ≤ 100.

SENSIBILIDADES PRÉ-ESPECIFICADAS (R4)
-------------------------------------
  R4.1  E2+E3 agrupados, SOMENTE mortalidade. Motivo: `mort_all` mediana
        empata entre E2 e E3 — a mortalidade separa "sem UTI" do resto, não
        baixa de alta complexidade. Nos outros indicadores os estratos ordenam
        monotonicamente e agrupar destruiria informação.
  R4.2  Excluir o Hospital Gilson de Cássia (7711980), único CNES instável
        alocado em E3, mantido no principal pela regra da mediana.

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

Saídas do escopo completo
-------------------------
  analises/tabelas/tabSEG_10_cre_mundlak_por_estrato.csv
  analises/tabelas/tabSEG_13_winsorizacao_uti.csv
  analises/tabelas/tabSEG_14_sobrecarga_binario.csv
  analises/tabelas/tabSEG_15_ocupacao_condicional.csv
  analises/figuras_segmentacao/figSEG_04_coef_oss_por_estrato.png
  analises/figuras_segmentacao/figSEG_05_sobrecarga_por_categoria.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
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
                log: bool = False, binario: bool = False,
                fracionario: bool = False, ppml: bool = False) -> dict:
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

    if log and (d[col] <= 0).any():
        return {"erro": f"{int((d[col] <= 0).sum())} zeros em {col} — log "
                        "indefinido; use ppml em vez de descartar (R8-2)"}
    d["y"] = np.log(d[col]) if log else d[col]

    # porte e categoria só entram com variação; em estrato pequeno podem
    # colapsar em nível único e tornar a coluna singular no patsy
    termos = [CAT, "complexidade_estrutural", "C(ano)", "media_oss"]
    if d["porte_fixo"].nunique() > 1:
        termos.insert(2, PORTE)
    else:
        print(f"    [{estrato}] porte_fixo sem variação "
              f"({d['porte_fixo'].iloc[0]}) — termo excluído")
    # O termo de Mundlak só é estimável se houver SWITCHER na subamostra.
    # Sem conversor, media_oss ∈ {0, 1} é perfeitamente colinear com a própria
    # dummy de categoria OSS (matriz singular): não há between a separar do
    # within porque não há within nenhum.
    tem_switcher = bool(d["media_oss"].between(0.001, 0.999).any())
    if not tem_switcher:
        termos.remove("media_oss")
        print(f"    [{estrato}] sem conversor na subamostra — media_oss "
              f"colinear com a dummy OSS; Mundlak removido, SEM within")

    f = "y ~ " + " + ".join(termos)
    try:
        if binario:
            res = smf.logit(f, data=d).fit(
                disp=0, maxiter=200, method="bfgs",
                cov_type="cluster", cov_kwds={"groups": d["cnes"]})
            conv = res.mle_retvals.get("converged", True)
            # separação: coeficientes divergem sem que a verossimilhança
            # tenha máximo interior. Tenta sem as dummies de ano, como em
            # estimacao.py; se persistir, NÃO reporta o número.
            if np.abs(res.params).max() > 15 and "C(ano)" in termos:
                print(f"    [{estrato}] separação com dummies de ano "
                      f"(|coef| máx {np.abs(res.params).max():.0f}) — "
                      f"reajustando sem C(ano)")
                f = f.replace(" + C(ano)", "")
                res = smf.logit(f, data=d).fit(
                    disp=0, maxiter=200, method="bfgs",
                    cov_type="cluster", cov_kwds={"groups": d["cnes"]})
                conv = res.mle_retvals.get("converged", True)
            if np.abs(res.params).max() > 15:
                return {"erro": "SEPARAÇÃO — logito não identificado "
                                f"(|coef| máx {np.abs(res.params).max():.0f}); "
                                "coeficiente não reportado"}
        elif ppml:
            # Poisson de pseudo-máxima verossimilhança, link log. Escolhido
            # porque PRESERVA OS ZEROS: descartá-los seria condicionar no
            # desfecho, que é exatamente o defeito 2 de R8. Consistente para
            # a média condicional sob má-especificação da variância; o
            # coeficiente lê-se como efeito proporcional, igual ao log-MQO.
            res = smf.glm(f, data=d, family=sm.families.Poisson()).fit(
                cov_type="cluster", cov_kwds={"groups": d["cnes"]})
            conv = bool(getattr(res, "converged", True))
        elif fracionario:
            # logito fracionário: GLM Binomial em resposta contínua em [0,1].
            # Consistente sob má-especificação da variância; acomoda os zeros
            # sem componente de inflação, que é inestimável dentro de estrato.
            res = smf.glm(f, data=d,
                          family=sm.families.Binomial()).fit(
                cov_type="cluster", cov_kwds={"groups": d["cnes"]})
            conv = bool(getattr(res, "converged", True))
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
            "convergiu": conv, "log": log or ppml,
            "binario": binario or fracionario,
            "escala": ("logito" if (binario or fracionario)
                       else "log (PPML)" if ppml else "log" if log
                       else "nível"),
            "identificacao": identificacao(estrato, d),
            "n_cnes_oss": int(d.loc[d["modelo_gestao_proxy"] == "OSS",
                                    "cnes"].nunique()),
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
    esc = r["escala"]
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


# ══════════════════════════════════════════════════════════════════════
# ESCOPO COMPLETO
# ══════════════════════════════════════════════════════════════════════

# (rótulo, coluna, kwargs do estimador, só_em_estratos_com_uti)
INDICADORES = [
    ("Mortalidade geral",        "mort_all",            {"fracionario": True}, False),
    ("TMP (dias)",               "tmp",                 {"log": True},         False),
    ("Faturamento real/saída",   "custo_real",          {"log": True},         False),
    ("Ocupação UTI (winsor.)",   "ocup_uti_w",          {"ppml": True},        True),
    ("Superlot. internação (A)", "sobrecarga",          {"binario": True},     False),
    ("Ocupação intern. ≤100 (B)", "ocup_int_cond",      {"log": True},         False),
]


def linha_tabela(r: dict, indicador: str, estrato: str,
                 recorte: str = "principal") -> dict:
    """Uma linha de tabSEG_10, com tarja e rótulo de identificação."""
    base = {"indicador": indicador, "estrato": estrato, "recorte": recorte}
    if "erro" in r:
        return {**base, "situacao": f"FALHOU: {r['erro']}"}
    pct = (100 * (np.exp(r["coef_oss"]) - 1)) if r["log"] else np.nan
    return {**base,
            "situacao": "estimado" if r["convergiu"] else "NÃO CONVERGIU",
            "n_obs": r["n_obs"], "n_cnes": r["n_cnes"],
            "n_cnes_oss": r["n_cnes_oss"], "tarja": r["tarja"],
            "identificacao": r["identificacao"], "escala": r["escala"],
            "coef_oss": round(r["coef_oss"], 5),
            "ep_cluster": round(r["ep_oss"], 5),
            "ic95_lo": round(r["ic_baixo"], 5),
            "ic95_hi": round(r["ic_alto"], 5),
            "z": round(r["z"], 3), "p_valor": round(r["p"], 5),
            "efeito_pct": round(pct, 2) if np.isfinite(pct) else np.nan}


def escopo_completo(p: pd.DataFrame) -> None:
    d = amostra_desfecho(p)
    linhas: list[dict] = []

    print("\n" + "=" * 72)
    print("ESCOPO COMPLETO — CRE/Mundlak, cinco indicadores × três estratos")
    print("=" * 72)

    for estrato in ("E1", "E2", "E3"):
        sub = d[d["estrato"] == estrato]
        print(f"\n{'─' * 72}\n{estrato} — {sub['estrato_rotulo'].iloc[0]}: "
              f"{len(sub)} obs, {sub['cnes'].nunique()} CNES")
        print(f"  identificação: {identificacao(estrato, sub)}")
        print("─" * 72)

        for rotulo, col, kw, exige_uti in INDICADORES:
            if exige_uti and estrato == "E1":
                print(f"\n  {rotulo} — NÃO-APLICÁVEL em E1")
                print("    E1 é 'sem UTI SUS' pela mediana. As 71 observações "
                      "com UTI ativa\n    são piscar cadastral (R7); estimar "
                      "aqui seria rodar sobre o artefato.")
                linhas.append({"indicador": rotulo, "estrato": estrato,
                               "recorte": "principal",
                               "situacao": "NÃO-APLICÁVEL (E1 sem UTI SUS)"})
                continue
            r = cre_mundlak(sub, col, estrato, **kw)
            imprimir(r, f"{rotulo} — {estrato}")
            linhas.append(linha_tabela(r, rotulo, estrato))

    # ── R4.1: E2+E3 agrupados, SOMENTE mortalidade ────────────────────
    print(f"\n{'=' * 72}")
    print("SENSIBILIDADE R4.1 — E2+E3 agrupados, SOMENTE mortalidade")
    print("Motivo pré-especificado: mort_all empata entre E2 e E3; a "
          "mortalidade\nsepara 'sem UTI' do resto, não baixa de alta "
          "complexidade.")
    print("=" * 72)
    e23 = d[d["estrato"].isin(["E2", "E3"])]
    med = e23.groupby("estrato")["mort_all"].median()
    print(f"  mediana mort_all: E2 {med.get('E2', np.nan):.4f}, "
          f"E3 {med.get('E3', np.nan):.4f}  (o empate que motiva o "
          f"agrupamento)")
    print(f"  CNES: OSS {e23.loc[e23['modelo_gestao_proxy'] == 'OSS', 'cnes'].nunique()}, "
          f"Direta {e23.loc[e23['modelo_gestao_proxy'] == 'Direta', 'cnes'].nunique()}")
    r = cre_mundlak(e23, "mort_all", "E2+E3", fracionario=True)
    imprimir(r, "Mortalidade geral — E2+E3")
    linhas.append(linha_tabela(r, "Mortalidade geral", "E2+E3",
                               "sensib. R4.1 (agrupado)"))

    # ── R4.2: excluir o Gilson de Cássia (7711980) ────────────────────
    print(f"\n{'=' * 72}")
    print("SENSIBILIDADE R4.2 — excluir Hospital Gilson de Cássia (7711980)")
    print("Único CNES instável alocado em E3, mantido no principal pela "
          "regra da mediana.")
    print("=" * 72)
    e3_sem = d[(d["estrato"] == "E3") & (d["cnes"] != 7711980)]
    presente = 7711980 in set(d.loc[d["estrato"] == "E3", "cnes"])
    print(f"  CNES 7711980 presente em E3: {'sim' if presente else 'NÃO'}"
          f" — E3 vai de {d[d['estrato'] == 'E3']['cnes'].nunique()} para "
          f"{e3_sem['cnes'].nunique()} CNES")
    for rotulo, col, kw, exige_uti in INDICADORES:
        r = cre_mundlak(e3_sem, col, "E3", **kw)
        imprimir(r, f"{rotulo} — E3 sem 7711980")
        linhas.append(linha_tabela(r, rotulo, "E3", "sensib. R4.2 (sem 7711980)"))

    # ── tabSEG_10 ─────────────────────────────────────────────────────
    tab = pd.DataFrame(linhas)
    _grava(tab, "tabSEG_10_cre_mundlak_por_estrato.csv")

    tabelas_ocupacao(d)
    figuras(d, tab)


def tabelas_ocupacao(d: pd.DataFrame) -> None:
    """tabSEG_13 (winsorização UTI), tabSEG_14 (binário) e tabSEG_15 (contínua)."""
    # tabSEG_13 — winsorização da UTI, limiar único
    valida = d[d["ocupacao_uti_valida"].notna()]
    p99 = float(np.percentile(valida["ocupacao_uti_valida"], 99))
    l13 = []
    for est in sorted(valida["estrato"].unique()):
        s = valida[valida["estrato"] == est]
        for cat in sorted(s["modelo_gestao_proxy"].unique()):
            sc = s[s["modelo_gestao_proxy"] == cat]
            n_w = int((sc["ocupacao_uti_valida"] > p99).sum())
            l13.append({
                "estrato": est, "categoria": cat, "n_obs": len(sc),
                "n_cnes": sc["cnes"].nunique(), "tarja": tarja(sc["cnes"].nunique()),
                "limiar_unico": round(p99, 2), "n_winsorizadas": n_w,
                "pct_winsorizadas": round(100 * n_w / len(sc), 2),
                "p99_do_estrato_NAO_USADO": round(
                    float(np.percentile(s["ocupacao_uti_valida"], 99)), 2),
                "mediana": round(float(sc["ocupacao_uti_valida"].median()), 2)})
    _grava(pd.DataFrame(l13), "tabSEG_13_winsorizacao_uti.csv")

    # tabSEG_14 — parte A, binário de superlotação
    l14 = []
    for est in ("E1", "E2", "E3"):
        s = d[d["estrato"] == est]
        for cat in sorted(s["modelo_gestao_proxy"].unique()):
            sc = s[s["modelo_gestao_proxy"] == cat]
            nc = sc["cnes"].nunique()
            within = int(sc.groupby("cnes")["sobrecarga"].nunique().gt(1).sum())
            l14.append({
                "estrato": est, "categoria": cat, "n_obs": len(sc),
                "n_cnes": nc, "tarja": tarja(nc),
                "n_acima_100": int(sc["sobrecarga"].sum()),
                "pct_superlotacao": round(100 * sc["sobrecarga"].mean(), 2),
                "cnes_com_variacao_within": within,
                "pct_cnes_com_within": round(100 * within / nc, 1) if nc else np.nan})
    _grava(pd.DataFrame(l14), "tabSEG_14_sobrecarga_binario.csv")

    # tabSEG_15 — parte B, contínua condicional a <= 100
    l15 = []
    for est in ("E1", "E2", "E3"):
        s = d[(d["estrato"] == est) & d["ocup_int_cond"].notna()]
        bruto = d[d["estrato"] == est]
        for cat in sorted(s["modelo_gestao_proxy"].unique()):
            sc = s[s["modelo_gestao_proxy"] == cat]
            bc = bruto[bruto["modelo_gestao_proxy"] == cat]
            l15.append({
                "estrato": est, "categoria": cat,
                "n_obs_condicional": len(sc), "n_obs_bruto": len(bc),
                "n_cnes": sc["cnes"].nunique(),
                "tarja": tarja(sc["cnes"].nunique()),
                "mediana_condicional": round(float(sc["ocup_int_cond"].median()), 2),
                "media_condicional": round(float(sc["ocup_int_cond"].mean()), 2),
                "mediana_bruta_conflaciona": round(
                    float(bc["ocupacao_internacao"].median()), 2)})
    t15 = pd.DataFrame(l15)
    _grava(t15, "tabSEG_15_ocupacao_condicional.csv")

    # decomposição do gap em E3, para o registro
    e3 = d[d["estrato"] == "E3"]
    gb = e3.groupby("modelo_gestao_proxy")["ocupacao_internacao"].median()
    gc = (e3[e3["ocup_int_cond"].notna()]
          .groupby("modelo_gestao_proxy")["ocup_int_cond"].median())
    gap_b = float(gb["OSS"] - gb["Direta"])
    gap_c = float(gc["OSS"] - gc["Direta"])
    print(f"\n  Decomposição do gap OSS−Direta em E3 (mediana):")
    print(f"    bruto {gap_b:+.1f} | contínua {gap_c:+.1f} | "
          f"frequência de superlotação responde por "
          f"{100 * (1 - gap_c / gap_b):.0f}% do gap")


def _grava(df: pd.DataFrame, nome: str) -> None:
    caminho = RAIZ / "analises" / "tabelas" / nome
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False, encoding="utf-8-sig")
    print(f"  [TAB] {nome}  ({len(df)} linhas)")


def figuras(d: pd.DataFrame, tab: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pasta = RAIZ / "analises" / "figuras_segmentacao"
    pasta.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
                         "font.size": 10.5, "axes.grid": True,
                         "grid.color": "#e9e7e4", "grid.linewidth": .6})

    # ── figSEG_04 — coeficiente de OSS por estrato ────────────────────
    pr = tab[(tab["recorte"] == "principal")
             & (tab["situacao"] == "estimado")].copy()
    inds = [i for i in pr["indicador"].unique()]
    fig, axes = plt.subplots(1, len(inds), figsize=(3.1 * len(inds), 4.6),
                             sharey=False)
    if len(inds) == 1:
        axes = [axes]
    for ax, ind in zip(axes, inds):
        s = pr[pr["indicador"] == ind].set_index("estrato").reindex(
            ["E1", "E2", "E3"]).dropna(subset=["coef_oss"])
        y = np.arange(len(s))
        # E3 é o único com identificação within: cor cheia; os demais, apagados
        cores = ["#0f9b8e" if e == "E3" else "#c9c7c4" for e in s.index]
        # ecolor não aceita lista: uma barra por ponto, para colorir por estrato
        for yi, (_, row), cor in zip(y, s.iterrows(), cores):
            ax.errorbar(row["coef_oss"], yi,
                        xerr=[[row["coef_oss"] - row["ic95_lo"]],
                              [row["ic95_hi"] - row["coef_oss"]]],
                        fmt="none", ecolor=cor, elinewidth=2.2, capsize=3)
        ax.scatter(s["coef_oss"], y, color=cores, s=46, zorder=3)
        ax.axvline(0, color="#0b0b0b", lw=.9, ls="--")
        ax.set_yticks(y)
        ax.set_yticklabels(s.index)
        ax.set_title(ind, fontsize=9.5)
        ax.set_xlabel(s["escala"].iloc[0] if len(s) else "")
        ax.invert_yaxis()
    fig.suptitle("Efeito OSS vs Direta por estrato — CRE/Mundlak, "
                 "IC95% com EP agrupado por CNES", fontsize=11)
    fig.text(.5, .005,
             "Somente E3 tem identificação within (4 conversores). E1 e E2 "
             "em cinza: comparação entre grupos, NÃO efeito causal.",
             ha="center", fontsize=8.5, color="#898781")
    fig.tight_layout(rect=(0, .035, 1, .96))
    fig.savefig(pasta / "figSEG_04_coef_oss_por_estrato.png", dpi=150,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  [FIG] figSEG_04_coef_oss_por_estrato.png")

    # ── figSEG_05 — superlotação por categoria e estrato ──────────────
    cores_cat = {"Direta": "#0d366b", "OSS": "#0f9b8e",
                 "Público Municipal": "#5598e7", "Filantrópico": "#6a51c7",
                 "Privado": "#898781"}
    fig, ax = plt.subplots(figsize=(9.4, 4.8))
    ordem = [c for c in cores_cat if c in set(d["modelo_gestao_proxy"])]
    larg, ests = .26, ["E1", "E2", "E3"]
    for i, est in enumerate(ests):
        s = d[d["estrato"] == est]
        for j, cat in enumerate(ordem):
            sc = s[s["modelo_gestao_proxy"] == cat]
            if sc.empty:
                continue
            pct = 100 * sc["sobrecarga"].mean()
            x = j + (i - 1) * larg
            ax.bar(x, pct, larg * .92, color=cores_cat[cat],
                   alpha=[.38, .66, 1.0][i],
                   edgecolor="white", linewidth=.6)
            if sc["cnes"].nunique() < PISO_CNES:
                ax.text(x, pct + 1, "n<10", ha="center", fontsize=6.5,
                        color="#898781")
    ax.set_xticks(range(len(ordem)))
    ax.set_xticklabels(ordem, fontsize=9)
    ax.set_ylabel("% das observações com ocupação > 100%")
    ax.set_title("Superlotação de internação por categoria e estrato\n"
                 "(parte A do modelo em duas partes — R6)", fontsize=11)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor="#5a5a5a", alpha=a, label=e)
                       for a, e in zip([.38, .66, 1.0], ests)],
              title="estrato", frameon=False, fontsize=9)
    fig.text(.5, .002, "Ocupação > 100% é a assinatura aritmética da "
             "superlotação: o SIH fatura leito extra, o CNES não o cadastra "
             "(R1 v4).", ha="center", fontsize=8.5, color="#898781")
    fig.tight_layout(rect=(0, .04, 1, 1))
    fig.savefig(pasta / "figSEG_05_sobrecarga_por_categoria.png", dpi=150,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  [FIG] figSEG_05_sobrecarga_por_categoria.png")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--piloto", action="store_true",
                    help="roda somente tmp em E3 e para")
    ap.add_argument("--completo", action="store_true",
                    help="cinco indicadores × três estratos + sensibilidades")
    args = ap.parse_args()

    p = preparar()
    if args.piloto:
        piloto(p)
    elif args.completo:
        escopo_completo(p)
    else:
        sys.exit("informe --piloto ou --completo")


if __name__ == "__main__":
    main()
