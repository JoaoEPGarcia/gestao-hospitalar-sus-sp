# -*- coding: utf-8 -*-
"""
_investigacao_etapa1_13jul2026_complemento.py
=============================================
Complemento da ETAPA 1 (revisão 13/07/2026) — SOMENTE LEITURA.
Responde às devoluções do gate de aprovação:

  C1 (item 1.8)  Cruzamento de denominadores da ocupação de UTI: mesmo
                 numerador (diárias-UTI do resumo SIH), dois denominadores
                 (leitos-UTI do SIH vs. leitos-UTI da planilha Barcelona).
                 Hipótese: a contagem Barcelona é menor → ocupação maior
                 ("modelo Barcelona" citado por Alberto).
  C2 (item 1.4)  Assinatura de censura/truncamento do TMP em ~30,5 dias:
                 empilhamento no teto, contagens por faixa, reprodutibilidade
                 do teto na base bruta. Subsídio para a pergunta ao Alberto.
  C3 (item 1.10) Efeito da exclusão pediátrica na COMPOSIÇÃO dos grupos de
                 comparação (Direta perde 2 de 32 CNES; Filantrópico perde
                 até 4): medianas antes/depois, sem excluir nada.
  C4 (item 1.3)  Anomalia do grupo Privado na UTI (mediana 3,5%): leitos de
                 UTI totais vs. SUS dos 3 CNES.

USO: python _investigacao_etapa1_13jul2026_complemento.py
"""

import numpy as np
import pandas as pd

import analise_sih as base                      # embrulha stdout em UTF-8
import construir_painel_definitivo as cpd

LARG = 84
PASTA_TAB = base.PASTA_TABELAS

CNES_PED_DIRETA = [2071371, 2088517]            # Darcy Vargas, Cândido Fontoura
CNES_PED_FILANT = [2081482, 2089696, 2076985, 2082454]  # Boldrini, GRAACC, Betinho, Tupã
CNES_PRIVADO    = [2077507, 2708566, 5586348]


def titulo(txt):
    print("\n" + "=" * LARG)
    print(txt)
    print("=" * LARG)


def sub(txt):
    print("\n--- " + txt)


def carregar():
    df = pd.read_csv(cpd.PAINEL_DEFINITIVO_CSV, encoding="utf-8-sig")
    df["cnes"] = pd.to_numeric(df["cnes"], errors="raise").astype("int64")
    df["ano"] = df["ano"].astype(int)
    cl = pd.read_csv(PASTA_TAB / "tab_classificacao_hospitais.csv",
                     encoding="utf-8-sig")
    cl["cnes"] = pd.to_numeric(cl["CNES"], errors="coerce")
    cl = cl.dropna(subset=["cnes"])
    cl["cnes"] = cl["cnes"].astype("int64")
    cl["uti_barcelona"] = pd.to_numeric(cl["UTI"], errors="coerce")
    return df, cl[["cnes", "uti_barcelona"]]


# ══════════════════════════════════════════════════════════════════════════════
# C1 — ITEM 1.8: DOIS DENOMINADORES PARA A MESMA OCUPAÇÃO DE UTI
# ══════════════════════════════════════════════════════════════════════════════

def c1_denominadores_uti(df: pd.DataFrame, cl: pd.DataFrame):
    titulo("C1 (item 1.8) — OCUPAÇÃO DE UTI: leitos SIH × leitos Barcelona")

    d = df.merge(cl, on="cnes", how="left").copy()
    for c in ["uti_total", "uti_sus", "diarias_uti", "ocupacao_uti"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    sub("Passo 1 — qual contagem de leitos reproduz a ocupacao_uti do resumo SIH?")
    for col in ["uti_total", "uti_sus"]:
        den = d[col] * 365
        recalc = np.where(den > 0, 100 * d["diarias_uti"] / den, np.nan)
        ok = np.isfinite(recalc) & d["ocupacao_uti"].notna()
        err = np.abs(recalc[ok] - d.loc[ok, "ocupacao_uti"])
        print(f"  denominador {col:9}: mediana |erro| = {np.median(err):8.3f} p.p. | "
              f"% com |erro| < 0,5 p.p.: {(err < 0.5).mean():6.1%}  (n={ok.sum()})")

    sub("Passo 2 — comparação das contagens de leitos de UTI (por CNES, painel 314)")
    leitos = (d.sort_values("ano").groupby("cnes")
              .agg(uti_total_sih=("uti_total", "median"),
                   uti_sus_sih=("uti_sus", "median"),
                   uti_barcelona=("uti_barcelona", "last")))
    leitos["dif_barc_menos_sus"] = leitos["uti_barcelona"] - leitos["uti_sus_sih"]
    leitos["dif_barc_menos_tot"] = leitos["uti_barcelona"] - leitos["uti_total_sih"]
    print(f"  CNES com leitos Barcelona informados: "
          f"{leitos['uti_barcelona'].notna().sum()}/314")
    print(f"  Barcelona < UTI SUS (SIH):   "
          f"{(leitos['dif_barc_menos_sus'] < 0).mean():.1%} dos CNES")
    print(f"  Barcelona = UTI SUS (SIH):   "
          f"{(leitos['dif_barc_menos_sus'] == 0).mean():.1%}")
    print(f"  Barcelona > UTI SUS (SIH):   "
          f"{(leitos['dif_barc_menos_sus'] > 0).mean():.1%}")
    print(f"  Barcelona < UTI TOTAL (SIH): "
          f"{(leitos['dif_barc_menos_tot'] < 0).mean():.1%} dos CNES")
    print("\n  Distribuição das diferenças (leitos):")
    print(leitos[["uti_total_sih", "uti_sus_sih", "uti_barcelona",
                  "dif_barc_menos_sus", "dif_barc_menos_tot"]]
          .describe(percentiles=[.1, .25, .5, .75, .9]).round(1).to_string())

    sub("Passo 3 — ocupação recalculada com CADA denominador (hospital-ano)")
    d["ocup_uti_sus"] = np.where(d["uti_sus"] > 0,
                                 100 * d["diarias_uti"] / (d["uti_sus"] * 365),
                                 np.nan)
    d["ocup_uti_tot"] = np.where(d["uti_total"] > 0,
                                 100 * d["diarias_uti"] / (d["uti_total"] * 365),
                                 np.nan)
    d["ocup_uti_barc"] = np.where(d["uti_barcelona"] > 0,
                                  100 * d["diarias_uti"] / (d["uti_barcelona"] * 365),
                                  np.nan)
    resumo = pd.DataFrame({
        "ocupacao_uti (resumo SIH)": d["ocupacao_uti"].describe(
            percentiles=[.25, .5, .75]),
        "recalc leitos SUS (SIH)": d["ocup_uti_sus"].describe(
            percentiles=[.25, .5, .75]),
        "recalc leitos TOTAIS (SIH)": d["ocup_uti_tot"].describe(
            percentiles=[.25, .5, .75]),
        "recalc leitos BARCELONA": d["ocup_uti_barc"].describe(
            percentiles=[.25, .5, .75]),
    }).round(1)
    print(resumo.to_string())
    par = d.dropna(subset=["ocup_uti_barc", "ocupacao_uti"])
    dif = par["ocup_uti_barc"] - par["ocupacao_uti"]
    print(f"\n  Diferença (Barcelona − SIH) por hospital-ano: mediana "
          f"{dif.median():+.1f} p.p. | p25 {dif.quantile(.25):+.1f} | "
          f"p75 {dif.quantile(.75):+.1f} | % hospital-ano em que a versão "
          f"Barcelona é MAIOR: {(dif > 0).mean():.1%}")
    print("\n  Medianas anuais das quatro versões:")
    print(d.groupby("ano")[["ocupacao_uti", "ocup_uti_sus", "ocup_uti_tot",
                            "ocup_uti_barc"]].median().round(1).to_string())


# ══════════════════════════════════════════════════════════════════════════════
# C2 — ITEM 1.4: ASSINATURA DE CENSURA DO TMP EM ~30,5 DIAS
# ══════════════════════════════════════════════════════════════════════════════

def c2_censura_tmp(df: pd.DataFrame):
    titulo("C2 (item 1.4) — TMP: empilhamento no teto de ~30,5 dias "
           "(assinatura de censura à direita)")

    bruto = cpd.carregar_painel_bruto()
    bruto_ind = base.calcular_indicadores(bruto)

    for nome, dfx, col in [("PAINEL DEFINITIVO (sem COVID)", df, "tmp"),
                           ("BASE BRUTA (com COVID)", bruto_ind, "tmp")]:
        x = dfx[col].dropna()
        x = x[np.isfinite(x)]
        sub(f"{nome} — n={len(x)}")
        print(f"  máximo = {x.max():.4f} | p99,9 = {x.quantile(.999):.2f} | "
              f"p99 = {x.quantile(.99):.2f}")
        faixas = [(">= 30,45 (no teto)", (x >= 30.45).sum()),
                  ("[30,0 ; 30,45)", ((x >= 30.0) & (x < 30.45)).sum()),
                  ("[29,0 ; 30,0)", ((x >= 29.0) & (x < 30.0)).sum()),
                  ("[25,0 ; 29,0)", ((x >= 25.0) & (x < 29.0)).sum()),
                  ("[20,0 ; 25,0)", ((x >= 20.0) & (x < 25.0)).sum()),
                  ("> 30,5 (acima do teto)", (x > 30.5001).sum())]
        for rot, n in faixas:
            print(f"    {rot:24}: {n:5d} hospital-ano")

    sub("Quem está NO teto no painel definitivo (tmp >= 30,45), por CNES")
    top = df[df["tmp"] >= 30.45]
    cont = (top.groupby("cnes")["ano"].agg(["count", "min", "max"])
            .rename(columns={"count": "anos_no_teto"}))
    mun = (bruto[bruto["municipio"].notna()].sort_values("ano")
           .groupby("cnes")["municipio"].last())
    cont["municipio"] = [mun.get(c, "") for c in cont.index]
    cont["tmp_mediano_serie"] = df.groupby("cnes")["tmp"].median().reindex(cont.index).round(1)
    print(cont.sort_values("anos_no_teto", ascending=False).to_string())

    sub("Contra-exemplo acima do teto na base bruta (quem consegue passar de 30,5?)")
    acima = bruto_ind[bruto_ind["tmp"] > 30.5001][
        ["cnes", "ano", "nome_fantasia", "municipio", "tipo_hospital", "tmp"]]
    print(acima.sort_values("tmp", ascending=False).head(15).to_string(index=False)
          if len(acima) else "  (nenhum)")

    print("\n  LEITURA: se apenas um punhado de estabelecimentos (e de tipo "
          "específico) ultrapassa 30,5 na base inteira, o valor ~30,5 opera "
          "como teto efetivo do TMP por AIH no SIH — censura à direita — e "
          "os perfis de longa permanência do painel ficam empilhados nele. "
          "Pergunta para Alberto: existe regra de faturamento/registro que "
          "limite as diárias por AIH (~30 dias + meia diária)?")


# ══════════════════════════════════════════════════════════════════════════════
# C3 — ITEM 1.10: EFEITO NA COMPOSIÇÃO DOS GRUPOS DE COMPARAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

def c3_composicao_grupos(df: pd.DataFrame):
    titulo("C3 (item 1.10) — Efeito da exclusão pediátrica na composição dos "
           "grupos (prévia; NADA excluído)")

    inds = ["mort_all", "tmp", "custo_saida", "pct_alta_complex",
            "ocupacao_internacao", "ocupacao_uti"]
    cenarios = [
        ("Direta — atual (32 CNES)", df["modelo_gestao_proxy"] == "Direta", None),
        ("Direta — sem Darcy Vargas e Cândido Fontoura (30 CNES)",
         df["modelo_gestao_proxy"] == "Direta", CNES_PED_DIRETA),
        ("Filantrópico — atual (187 CNES)",
         df["modelo_gestao_proxy"] == "Filantrópico", None),
        ("Filantrópico — sem Boldrini/GRAACC/Betinho/Tupã (183 CNES)",
         df["modelo_gestao_proxy"] == "Filantrópico", CNES_PED_FILANT),
    ]
    linhas = []
    for rot, mask, excl in cenarios:
        s = df[mask]
        if excl:
            s = s[~s["cnes"].isin(excl)]
        med = s[inds].median()
        med["n_cnes"] = s["cnes"].nunique()
        med.name = rot
        linhas.append(med)
    tab = pd.DataFrame(linhas)
    print(tab.round(4).to_string())

    sub("Perfil individual dos candidatos Direta (para dimensionar o que sai)")
    for c in CNES_PED_DIRETA:
        s = df[df["cnes"] == c]
        print(f"  CNES {c}: mort_all mediana {s['mort_all'].median():.4f} | "
              f"tmp {s['tmp'].median():.2f} | pct_alta "
              f"{s['pct_alta_complex'].median():.4f} | "
              f"qtde mediana {s['qtde'].median():.0f}")


# ══════════════════════════════════════════════════════════════════════════════
# C4 — ITEM 1.3: ANOMALIA DA UTI DO GRUPO PRIVADO
# ══════════════════════════════════════════════════════════════════════════════

def c4_uti_privado(df: pd.DataFrame):
    titulo("C4 (item 1.3) — Grupo Privado: por que ocupação de UTI ~3,5%?")

    s = df[df["cnes"].isin(CNES_PRIVADO)].copy()
    g = (s.groupby("cnes")
         .agg(uti_total_mediana=("uti_total", "median"),
              uti_sus_mediana=("uti_sus", "median"),
              diarias_uti_mediana=("diarias_uti", "median"),
              ocup_uti_mediana=("ocupacao_uti", "median"),
              ocup_int_mediana=("ocupacao_internacao", "median")))
    print(g.round(2).to_string())
    print("\n  LEITURA: se uti_sus ≈ 0 ou diárias-UTI ≈ 0 (produção SUS de UTI "
          "residual em hospitais privados contratualizados), a taxa de 3,5% é "
          "denominador/numerador residual — reforça a ressalva de "
          "não-interpretação do grupo (n=3) em QUALQUER tabela que circule.")


def main():
    print("=" * LARG)
    print("COMPLEMENTO DA ETAPA 1 — SOMENTE LEITURA (devoluções do gate)")
    print("=" * LARG)
    base.configurar_diretorios()
    df, cl = carregar()
    print(f"[CARGA] definitivo: {df['cnes'].nunique()} CNES / {len(df)} linhas")

    c1_denominadores_uti(df, cl)
    c2_censura_tmp(df)
    c3_composicao_grupos(df)
    c4_uti_privado(df)

    print("\n" + "=" * LARG)
    print("FIM — nenhum arquivo do pipeline foi alterado.")
    print("=" * LARG)


if __name__ == "__main__":
    main()
