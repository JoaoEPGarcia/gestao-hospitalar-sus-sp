# -*- coding: utf-8 -*-
"""
verificacao_pos_patch.py
========================
Verificação pós-patch (jul/2026) do PAINEL ANALÍTICO DEFINITIVO, após:
  CHANGE 1 — analise_sih.py: coluna correta de "Classificação assistencial"
             no arquivo 2025 (posição ~38; preferir_ultima).
  CHANGE 2 — construir_painel_definitivo.py: ETAPA E — exclusão dos CNES
             sem pontuação de Barcelona (2042894, 2078031, 2082209).

Compara analises/painel_definitivo.csv (DEPOIS) com
analises/painel_definitivo_ANTES.csv (cópia pré-patch) e imprime TODOS os
números com PASS/FALHA quando há valor esperado. NÃO altera nenhum arquivo
do pipeline.

USO: python -u verificacao_pos_patch.py
"""

import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PASTA          = Path(__file__).parent
PASTA_ANALISES = PASTA / "analises"
PASTA_TABELAS  = PASTA_ANALISES / "tabelas"

ARQ_DEPOIS   = PASTA_ANALISES / "painel_definitivo.csv"
ARQ_ANTES    = PASTA_ANALISES / "painel_definitivo_ANTES.csv"
ARQ_BRUTO_PQ = PASTA_ANALISES / "painel_hospital_ano.parquet"
ARQ_BRUTO_CSV= PASTA_ANALISES / "painel_hospital_ano.csv"
ARQ_FILTROS  = PASTA_TABELAS  / "tab_auditoria_filtros.csv"
ARQ_REMOVIDOS= PASTA_TABELAS  / "tab_auditoria_cnes_removidos.csv"

SWITCHERS = {
    # cnes: (ano-proxy da virada Direta→OSS, data de contrato)
    2081695: (2019, "OSS desde nov/2018"),
    2078287: (2023, "OSS desde set/2022"),
    2082225: (2025, "OSS desde 01/09/2024"),
    2091755: (2025, "OSS desde 01/09/2024"),
    2750511: (2025, "OSS desde jan/2025"),
}
CNES_EXCLUIDOS_E = [2042894, 2078031, 2082209]
INDICADORES = ["mort_all", "mort_sem_excl", "tmp", "custo_saida", "pct_alta_complex"]

# Item 1.5 (14/07/2026): a tabela de medianas pós-patch ganha também o
# faturamento REAL (R$ de 2025). As CHECAGENS numéricas de referência
# permanecem sobre custo_saida (valores esperados inalterados). Série IPCA
# idêntica à canônica de estimacao.py (dez/dez IBGE; 2025 = 4,26%).
IPCA_ANUAL = {2015: 10.67, 2016: 6.29, 2017: 2.95, 2018: 3.75, 2019: 4.31,
              2020: 4.52, 2021: 10.06, 2022: 5.79, 2023: 4.62, 2024: 4.83,
              2025: 4.26}


def _fatores_ipca_2025() -> dict:
    anos = sorted(IPCA_ANUAL)
    acum_ate, acum = {}, 1.0
    for a in anos:
        acum *= 1 + IPCA_ANUAL[a] / 100
        acum_ate[a] = acum
    total = acum_ate[anos[-1]]
    return {a: total / acum_ate[a] for a in anos}

# Referências do painel de 317 (pré-patch) — diferenças pequenas esperadas
REFERENCIAS = {
    "mort_all":         0.0535,
    "mort_sem_excl":    0.0534,
    "tmp":              4.42,
    "custo_saida":      1064.68,
    "pct_alta_complex": 0.0017,
}
FAIXAS_ESPERADAS = {2: 49, 3: 134, 4: 106, 5: 15, 6: 10}   # nº de CNES por faixa

_resultados: list[tuple[str, bool]] = []


def check(nome: str, ok: bool, obtido, esperado) -> None:
    status = "PASS " if ok else "FALHA"
    print(f"  [{status}] {nome}: obtido={obtido}  esperado={esperado}")
    _resultados.append((nome, bool(ok)))


def titulo(txt: str) -> None:
    print("\n" + "=" * 78)
    print(txt)
    print("=" * 78)


def carregar():
    depois = pd.read_csv(ARQ_DEPOIS, encoding="utf-8-sig")
    antes  = pd.read_csv(ARQ_ANTES,  encoding="utf-8-sig")
    if ARQ_BRUTO_PQ.exists():
        bruto = pd.read_parquet(ARQ_BRUTO_PQ)
    else:
        bruto = pd.read_csv(ARQ_BRUTO_CSV, encoding="utf-8-sig")
    bruto["cnes"] = pd.to_numeric(bruto["cnes"], errors="raise").astype(np.int64)
    bruto["ano"]  = bruto["ano"].astype(int)
    filtros   = pd.read_csv(ARQ_FILTROS,   encoding="utf-8-sig")
    removidos = pd.read_csv(ARQ_REMOVIDOS, encoding="utf-8-sig")
    return depois, antes, bruto, filtros, removidos


# ══════════════════════════════════════════════════════════════════════════════
# 1. CORREÇÃO DE 2025
# ══════════════════════════════════════════════════════════════════════════════

def item1_correcao_2025(depois, antes):
    titulo("1. CORREÇÃO DA CLASSIFICAÇÃO ASSISTENCIAL DE 2025 (CHANGE 1)")

    for rotulo, df in [("ANTES", antes), ("DEPOIS", depois)]:
        sub = df[df["ano"] == 2025]["class_assistencial"]
        vc = sub.value_counts(dropna=False)
        print(f"\n  class_assistencial em 2025 — painel {rotulo} "
              f"({sub.notna().sum()} não-nulos de {len(sub)} linhas):")
        print("    valores distintos (não-nulos):", sub.dropna().nunique())
        print("    " + vc.to_string().replace("\n", "\n    "))

    n_antes  = antes.loc[antes["ano"] == 2025, "class_assistencial"].dropna().nunique()
    n_depois = depois.loc[depois["ano"] == 2025, "class_assistencial"].dropna().nunique()
    if n_antes <= 1:
        print(f"\n  >> O painel ANTES era DEGENERADO em 2025 "
              f"({n_antes} valor distinto) — artefato entregue corrompido.")
    else:
        print(f"\n  >> O painel ANTES NÃO era degenerado em 2025 "
              f"({n_antes} valores distintos) — o artefato entregue já trazia "
              f"rótulos variando por CNES.")
    n_nan_2025 = int(depois.loc[depois["ano"] == 2025,
                                "class_assistencial"].isna().sum())
    check("2025 DEPOIS não-degenerado (>= 2 categorias) e sem NaN",
          (n_depois >= 2) and (n_nan_2025 == 0),
          f"{n_depois} categorias, {n_nan_2025} NaN", ">= 2 categorias, 0 NaN")

    # Comparação rótulo a rótulo (CNES comuns) — mede o efeito real do patch
    m = antes.loc[antes["ano"] == 2025, ["cnes", "class_assistencial"]].merge(
        depois.loc[depois["ano"] == 2025, ["cnes", "class_assistencial"]],
        on="cnes", suffixes=("_antes", "_depois"))
    dif = m[m["class_assistencial_antes"].fillna("~")
            != m["class_assistencial_depois"].fillna("~")]
    print(f"\n  Comparação por CNES (2025): {len(m)} CNES comuns; rótulo "
          f"divergente ANTES×DEPOIS em {len(dif)} CNES.")
    if len(dif):
        print("    " + dif.to_string(index=False).replace("\n", "\n    "))

    # Tabela ANTES × DEPOIS para os 5 switchers (rótulo de 2025)
    print("\n  Rótulo de 2025 dos 5 switchers — ANTES × DEPOIS:")
    print(f"    {'CNES':>8}  {'ANTES':<22}  {'DEPOIS':<22}")
    for cnes in SWITCHERS:
        a = antes.loc [(antes["cnes"] == cnes)  & (antes["ano"] == 2025),
                       "class_assistencial"]
        d = depois.loc[(depois["cnes"] == cnes) & (depois["ano"] == 2025),
                       "class_assistencial"]
        va = a.iloc[0] if len(a) else "(ausente)"
        vd = d.iloc[0] if len(d) else "(ausente)"
        print(f"    {cnes:>8}  {str(va):<22}  {str(vd):<22}")

    # Histórico completo e coerência com as datas de contrato
    print("\n  Histórico 2015-2025 de class_assistencial (painel DEPOIS) e "
          "coerência com o ano-proxy da virada:")
    anos = sorted(depois["ano"].unique())
    for cnes, (ano_proxy, contrato) in SWITCHERS.items():
        sub = (depois[depois["cnes"] == cnes]
               .sort_values("ano")[["ano", "class_assistencial"]])
        hist = {int(a): str(c) for a, c in
                zip(sub["ano"], sub["class_assistencial"].fillna("?"))}
        print(f"\n    CNES {cnes} ({contrato}; proxy {ano_proxy}):")
        print("      " + "; ".join(f"{a}={hist.get(a, '(ausente)')}" for a in anos))
        pos = [hist.get(a, "") for a in anos if a >= ano_proxy]
        pre = [hist.get(a, "") for a in anos if a <  ano_proxy]
        ok_pos = all(v == "OSS" for v in pos)
        ok_pre = all(v != "OSS" for v in pre)
        check(f"{cnes}: OSS em todos os anos >= {ano_proxy}", ok_pos,
              f"{pos}", "todos 'OSS'")
        check(f"{cnes}: sem OSS antes de {ano_proxy}", ok_pre,
              f"{pre}", "nenhum 'OSS'")


# ══════════════════════════════════════════════════════════════════════════════
# 2. DIMENSÕES DO PAINEL
# ══════════════════════════════════════════════════════════════════════════════

def item2_dimensoes(depois, antes, filtros):
    titulo("2. DIMENSÕES DO PAINEL E FUNIL DE AUDITORIA")

    n_cnes, n_obs = depois["cnes"].nunique(), len(depois)
    check("nº de hospitais (nunique cnes)", n_cnes == 314, n_cnes, 314)
    check("nº de observações (linhas)",     n_obs == 3454, n_obs, 3454)

    anos_por_cnes = depois.groupby("cnes")["ano"].nunique()
    n_incompletos = int((anos_por_cnes != 11).sum())
    check("balanceamento: todo CNES com exatamente 11 anos",
          n_incompletos == 0, f"{n_incompletos} CNES fora do padrão", "0")

    print("\n  Funil de auditoria (tab_auditoria_filtros.csv):")
    with pd.option_context("display.width", 250, "display.max_colwidth", 80):
        print("    " + filtros.to_string(index=False).replace("\n", "\n    "))

    et_e = filtros[filtros["etapa"] == "ETAPA E"]
    if len(et_e) == 1:
        r = et_e.iloc[0]
        check("ETAPA E: CNES removidos",        r["cnes_removidos"] == 3,
              int(r["cnes_removidos"]), 3)
        check("ETAPA E: hospital-ano removidos", r["hospital_ano_removidos"] == 33,
              int(r["hospital_ano_removidos"]), 33)
        check("ETAPA E: CNES restantes",         r["cnes_restantes"] == 314,
              int(r["cnes_restantes"]), 314)
        check("ETAPA E: hospital-ano restantes", r["hospital_ano_restantes"] == 3454,
              int(r["hospital_ano_restantes"]), 3454)
    else:
        check("linha ETAPA E presente no funil", False, len(et_e), 1)

    # Presença e categoria modal dos 3 CNES excluídos
    print("\n  Os 3 CNES da ETAPA E — presença e categoria modal "
          "(class_assistencial, painel ANTES):")
    for cnes in CNES_EXCLUIDOS_E:
        no_depois = int((depois["cnes"] == cnes).sum())
        sub = antes.loc[antes["cnes"] == cnes, "class_assistencial"].dropna()
        modal = sub.mode().iloc[0] if len(sub) else "(sem rótulo)"
        print(f"    CNES {cnes}: modal ANTES = {modal!r} "
              f"({sub.value_counts().to_dict()}); linhas no DEPOIS = {no_depois}")
        check(f"{cnes} ausente do painel DEPOIS", no_depois == 0, no_depois, 0)


# ══════════════════════════════════════════════════════════════════════════════
# 3. DISTRIBUIÇÃO POR MODELO_GESTAO_PROXY
# ══════════════════════════════════════════════════════════════════════════════

def item3_modelo_gestao(depois):
    titulo("3. DISTRIBUIÇÃO POR modelo_gestao_proxy (PAINEL DE 314, 2025 CORRIGIDO)")

    col = "modelo_gestao_proxy"
    sub = depois[depois[col].notna()]
    cont = (sub.groupby(col)["cnes"]
            .agg(n_cnes="nunique", n_hospital_ano="size")
            .sort_values("n_hospital_ano", ascending=False))
    print("\n  Contagem por categoria (um CNES pode aparecer em mais de uma "
          "categoria se o rótulo variou entre anos):")
    print("    " + cont.to_string().replace("\n", "\n    "))
    print(f"\n    Total hospital-ano com rótulo: {len(sub)} "
          f"(NaN: {depois[col].isna().sum()})")

    sub = sub.copy()
    sub["custo_real"] = (sub["custo_saida"]
                         * sub["ano"].map(_fatores_ipca_2025()))
    med = sub.groupby(col)[INDICADORES + ["custo_real"]].median().round(6)
    print("\n  Mediana dos indicadores por categoria (custo_real = "
          "faturamento em R$ de 2025, item 1.5):")
    with pd.option_context("display.width", 200):
        print("    " + med.to_string().replace("\n", "\n    "))
    med.to_csv(PASTA_TABELAS / "tab_pospatch_medianas_por_modelo.csv",
               encoding="utf-8-sig")
    cont.to_csv(PASTA_TABELAS / "tab_pospatch_contagem_por_modelo.csv",
                encoding="utf-8-sig")
    print("\n  [SAÍDA] tab_pospatch_contagem_por_modelo.csv e "
          "tab_pospatch_medianas_por_modelo.csv gravadas em analises/tabelas.")


# ══════════════════════════════════════════════════════════════════════════════
# 4. COMPLEXIDADE
# ══════════════════════════════════════════════════════════════════════════════

def item4_complexidade(depois):
    titulo("4. COMPLEXIDADE (BARCELONA)")

    n_nan = int(depois["complexidade_estrutural"].isna().sum())
    check("NaN em complexidade_estrutural", n_nan == 0, n_nan, 0)

    ok = depois[["complexidade_estrutural", "complexidade_pond_mort"]].dropna()
    rho = ok["complexidade_estrutural"].corr(ok["complexidade_pond_mort"],
                                             method="spearman")
    check("Spearman(estrutural, pond_mort) próximo de 0,926",
          abs(rho - 0.926) <= 0.02, f"{rho:.4f}", "~0.926 (tol. ±0.02)")

    print("\n  Distribuição de CNES por faixa_barcelona:")
    faixas = depois.groupby("faixa_barcelona")["cnes"].nunique()
    print("    " + faixas.to_string().replace("\n", "\n    "))
    obtido = {}
    for rotulo, n in faixas.items():
        dig = "".join(ch for ch in str(rotulo) if ch.isdigit())
        if dig:
            obtido[int(dig)] = int(n)
    check("faixas 2-6 = 49/134/106/15/10", obtido == FAIXAS_ESPERADAS,
          obtido, FAIXAS_ESPERADAS)
    check("soma das faixas = 314", int(faixas.sum()) == 314, int(faixas.sum()), 314)


# ══════════════════════════════════════════════════════════════════════════════
# 5. OCUPAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

def item5_ocupacao(depois):
    titulo("5. OCUPAÇÃO — ESCALA, FRONTEIRAS E RECOMENDAÇÃO DE DISTRIBUIÇÃO")

    resultado = {}
    for col in ["ocupacao_internacao", "ocupacao_uti"]:
        s = pd.to_numeric(depois[col], errors="coerce").dropna()
        p50, p90, p95, p99 = s.quantile([.50, .90, .95, .99])
        escala = "percentual [0,100]" if p50 > 2 else "fração [0,1]"
        lim = 100.0 if p50 > 2 else 1.0
        frac_acima = float((s > lim).mean())
        resultado[col] = frac_acima
        print(f"\n  {col}  (n={len(s)}, NaN={depois[col].isna().sum()})")
        print(f"    escala detectada : {escala} (p50={p50:.4f})")
        print(f"    p50={p50:.4f}  p90={p90:.4f}  p95={p95:.4f}  "
              f"p99={p99:.4f}  máx={s.max():.4f}")
        print(f"    obs. acima de 100%: {int((s > lim).sum())} "
              f"({100 * frac_acima:.2f}% das não-nulas)")

    pior = max(resultado.values())
    if pior < 0.005:
        rec = ("Beta — a fração de observações acima de 100% é desprezível "
               f"(máx. {100 * pior:.2f}%); tratar pontuais >1 por winsorização "
               "ou exclusão justificada.")
    else:
        rec = ("Gamma ou LogNormal sobre a razão de ocupação — a fração acima "
               f"de 100% NÃO é desprezível (máx. {100 * pior:.2f}%), o que "
               "viola o suporte (0,1) da Beta.")
    print(f"\n  RECOMENDAÇÃO EMPÍRICA: {rec}")


# ══════════════════════════════════════════════════════════════════════════════
# 6. DESCRITIVAS GERAIS × REFERÊNCIAS
# ══════════════════════════════════════════════════════════════════════════════

def item6_descritivas(depois, antes):
    titulo("6. DESCRITIVAS GERAIS (314 HOSPITAIS) × REFERÊNCIAS DO PAINEL DE 317")

    print(f"\n  {'indicador':<18} {'mediana':>12} {'q25':>12} {'q75':>12} "
          f"{'med.ANTES':>12} {'referência':>12} {'dif.rel.%':>10}")
    for ind in INDICADORES:
        s = pd.to_numeric(depois[ind], errors="coerce").dropna()
        med, q25, q75 = s.median(), s.quantile(.25), s.quantile(.75)
        med_antes = pd.to_numeric(antes[ind], errors="coerce").median()
        ref = REFERENCIAS[ind]
        dif = 100 * (med - ref) / ref if ref else np.nan
        alerta = "  << DIVERGÊNCIA GRANDE" if abs(dif) > 5 else ""
        print(f"  {ind:<18} {med:>12.4f} {q25:>12.4f} {q75:>12.4f} "
              f"{med_antes:>12.4f} {ref:>12.4f} {dif:>+10.2f}{alerta}")
        check(f"mediana de {ind} próxima da referência (±5%)",
              abs(dif) <= 5, f"{med:.4f} ({dif:+.2f}%)",
              f"~{ref} (mediana ANTES: {med_antes:.4f})")


# ══════════════════════════════════════════════════════════════════════════════
# 7. INTEGRIDADE
# ══════════════════════════════════════════════════════════════════════════════

def item7_integridade(depois, antes):
    titulo("7. INTEGRIDADE")

    n_dup = int(depois.duplicated(subset=["cnes", "ano"]).sum())
    check("duplicatas de (cnes, ano)", n_dup == 0, n_dup, 0)

    regras = {
        "mort_all":         lambda s: (s < 0) | (s > 1),
        "mort_sem_excl":    lambda s: (s < 0) | (s > 1),
        "tmp":              lambda s: s <= 0,
        "custo_saida":      lambda s: s <= 0,
        "pct_alta_complex": lambda s: (s < 0) | (s > 1),
    }
    descricao = {
        "mort_all": "[0,1]", "mort_sem_excl": "[0,1]",
        "tmp": "> 0", "custo_saida": "> 0", "pct_alta_complex": "[0,1]",
    }
    for ind, regra in regras.items():
        s = pd.to_numeric(depois[ind], errors="coerce").dropna()
        n_viol = int(regra(s).sum())
        check(f"{ind} dentro de {descricao[ind]}", n_viol == 0,
              f"{n_viol} violações", "0")
        if n_viol:
            v = depois.loc[regra(pd.to_numeric(depois[ind], errors="coerce"))
                           .fillna(False),
                           ["cnes", "ano", ind, "qtde_sem_covid",
                            "dias_sem_covid", "valor_sem_covid"]]
            print("      linhas violadoras:")
            print("      " + v.to_string(index=False).replace("\n", "\n      "))
            for _, r in v.iterrows():
                ja_antes = pd.to_numeric(
                    antes.loc[(antes["cnes"] == r["cnes"])
                              & (antes["ano"] == r["ano"]), ind],
                    errors="coerce")
                val = float(ja_antes.iloc[0]) if len(ja_antes) else np.nan
                print(f"      (cnes={int(r['cnes'])}, ano={int(r['ano'])}) "
                      f"no painel ANTES: {ind}={val} — "
                      f"{'JÁ EXISTIA antes do patch' if not np.isnan(val) and regra(pd.Series([val])).iloc[0] else 'não violava/ausente no ANTES'}")

    print("\n  NaN por coluna (indicadores + colunas críticas):")
    for col in INDICADORES + ["modelo_gestao_proxy", "complexidade_estrutural",
                              "faixa_barcelona"]:
        print(f"    {col:<24}: {int(depois[col].isna().sum())} NaN")


# ══════════════════════════════════════════════════════════════════════════════
# 8. COVID
# ══════════════════════════════════════════════════════════════════════════════

def item8_covid(bruto, removidos):
    titulo("8. COVID — PESO DO CÓDIGO 999 (2020-2021) E HOSPITAIS DE CAMPANHA")

    for anos, rotulo in [([2020], "2020"), ([2021], "2021"),
                         ([2020, 2021], "biênio 2020-2021")]:
        sub = bruto[bruto["ano"].isin(anos)]
        fq = sub["qtde_covid"].sum()  / sub["qtde"].sum()
        fv = sub["valor_covid"].sum() / sub["valor"].sum()
        print(f"  {rotulo:<18}: {100 * fq:6.2f}% da qtde | "
              f"{100 * fv:6.2f}% do valor "
              f"(qtde_covid={sub['qtde_covid'].sum():,.0f} de "
              f"{sub['qtde'].sum():,.0f})")

    camp = removidos[removidos["etapa"] == "ETAPA C1"]
    print(f"\n  Hospitais de campanha excluídos (ETAPA C1): {len(camp)} CNES")
    for _, r in camp.iterrows():
        print(f"    {int(r['cnes'])}: {r['nome_referencia']} — {r['motivo']}")


# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("VERIFICAÇÃO PÓS-PATCH DO PAINEL DEFINITIVO — jul/2026")
    depois, antes, bruto, filtros, removidos = carregar()
    print(f"[CARGA] DEPOIS: {depois['cnes'].nunique()} CNES × "
          f"{depois['ano'].nunique()} anos = {len(depois)} linhas | "
          f"ANTES: {antes['cnes'].nunique()} CNES, {len(antes)} linhas | "
          f"bruto: {bruto['cnes'].nunique()} CNES, {len(bruto)} linhas")

    item1_correcao_2025(depois, antes)
    item2_dimensoes(depois, antes, filtros)
    item3_modelo_gestao(depois)
    item4_complexidade(depois)
    item5_ocupacao(depois)
    item6_descritivas(depois, antes)
    item7_integridade(depois, antes)
    item8_covid(bruto, removidos)

    titulo("RESUMO DOS CHECKS")
    n_falhas = sum(1 for _, ok in _resultados if not ok)
    for nome, ok in _resultados:
        if not ok:
            print(f"  [FALHA] {nome}")
    print(f"\n  {len(_resultados)} checks executados — "
          f"{len(_resultados) - n_falhas} PASS, {n_falhas} FALHA.")


if __name__ == "__main__":
    main()
