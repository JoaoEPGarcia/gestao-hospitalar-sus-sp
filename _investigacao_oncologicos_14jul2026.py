# -*- coding: utf-8 -*-
"""
_investigacao_oncologicos_14jul2026.py
======================================
Passo 6 do prompt consolidado de 14/07/2026 — SOMENTE LEITURA.

  P6.  Por que a mortalidade dos hospitais ONCOLÓGICOS (adultos) aparece
       mais baixa que o esperado? Identificação, comparação com pares e
       teste das hipóteses testáveis com o painel atual.
  P4b. Complemento da checagem da Santa Casa de S. Bernardo do Campo
       (3223728): trajetória ano a ano (mort_all, tmp) para distinguir
       padrão consistente de ano-anomalia.
  P5b. Medianas de grupo (Direta/OSS/Filantrópico) SEM os 20 CNES da lista
       de exclusão proposta — números para o memorando (a citação anterior
       cobria só os 2 pediátricos da Direta).

Nada é alterado; nenhuma variável nova é criada no painel.
"""

import re

import numpy as np
import pandas as pd

import analise_sih as base                      # embrulha stdout em UTF-8
import construir_painel_definitivo as cpd

LARG = 84
PASTA_TAB = base.PASTA_TABELAS

# Onco-pediátricos (já na lista de exclusão do item 1.10) — fora deste grupo
CNES_ONCO_PED = {2081482, 2089696}

# Lista de exclusão proposta (20 CNES) — Passos 2 e 3 de 14/07/2026
LISTA_20 = {2071371, 2078325, 2080427, 2088517, 2081482, 2089696,   # pediátricos
            2076985, 2082454,                                       # Casas da Criança
            2812703,                                                # psiquiátrico
            2079208, 2790998, 2082276, 2089572, 2688522, 2080192,   # crônicos
            2084236, 2082675, 2081725, 2079194, 3753433}

PAT_ONCO = re.compile(r"ONCOLOG|CANCER|TUMOR|\bPIO XII\b")


def titulo(txt):
    print("\n" + "=" * LARG)
    print(txt)
    print("=" * LARG)


def sub(txt):
    print("\n--- " + txt)


def carregar():
    bruto = cpd.carregar_painel_bruto()
    df = pd.read_csv(cpd.PAINEL_DEFINITIVO_CSV, encoding="utf-8-sig")
    df["cnes"] = pd.to_numeric(df["cnes"], errors="raise").astype("int64")
    df["ano"] = df["ano"].astype(int)
    cl = pd.read_csv(PASTA_TAB / "tab_classificacao_hospitais.csv",
                     encoding="utf-8-sig")
    cl["cnes"] = pd.to_numeric(cl["CNES"], errors="coerce")
    cl = cl.dropna(subset=["cnes"])
    cl["cnes"] = cl["cnes"].astype("int64")
    return bruto, df, cl


def identificar_oncologicos(bruto, df, cl):
    titulo("P6.1 — HOSPITAIS ONCOLÓGICOS (ADULTOS) NO PAINEL DEFINITIVO")

    def_cnes = set(df["cnes"].unique())
    # Sinal 1: especializacao 004 ONCOLOGIA em qualquer ano
    es = bruto[bruto["cnes"].isin(def_cnes)][["cnes", "especializacao"]].dropna()
    es["norm"] = es["especializacao"].map(cpd.normalizar_texto)
    c_esp = set(es[es["norm"].str.contains("ONCOLOG")]["cnes"])
    # Sinal 2: nome_fantasia / Instituição
    nm = bruto[["cnes", "nome_fantasia"]].dropna()
    nm["norm"] = nm["nome_fantasia"].map(cpd.normalizar_texto)
    c_nome = set(nm[nm["norm"].str.contains(PAT_ONCO)]["cnes"]) & def_cnes
    cli = cl.copy()
    cli["norm"] = cli["Instituição"].map(cpd.normalizar_texto)
    c_inst = set(cli[cli["norm"].str.contains(PAT_ONCO)]["cnes"]) & def_cnes

    onco = sorted((c_esp | c_nome | c_inst) - CNES_ONCO_PED)
    nomes = cpd.nome_referencia_por_cnes(bruto)
    inst = cli.set_index("cnes")["Instituição"]
    proxy = df.sort_values("ano").groupby("cnes")["modelo_gestao_proxy"].last()
    porte = df.sort_values("ano").groupby("cnes")["porte_hospital"].last()
    faixa = df.groupby("cnes")["faixa_barcelona"].first()
    med = df.groupby("cnes")[["mort_all", "tmp", "pct_alta_complex",
                              "qtde_sem_covid"]].median()

    linhas = []
    for c in onco:
        vias = []
        if c in c_esp:  vias.append("espec004")
        if c in c_nome: vias.append("nome")
        if c in c_inst: vias.append("instituicao")
        linhas.append({
            "cnes": c,
            "nome": (nomes.get(c) or inst.get(c, ""))[:46],
            "gestao": proxy.get(c, ""),
            "porte": porte.get(c, ""),
            "faixa_b": faixa.get(c, ""),
            "mort_med": round(med.loc[c, "mort_all"], 4),
            "tmp_med": round(med.loc[c, "tmp"], 2),
            "pct_alta_med": round(med.loc[c, "pct_alta_complex"], 3),
            "qtde_med": int(med.loc[c, "qtde_sem_covid"]),
            "via": "+".join(vias),
        })
    t = pd.DataFrame(linhas)
    with pd.option_context("display.width", 400, "display.max_columns", 20):
        print(t.to_string(index=False))
    print("\n  NOTA: GRAACC e Boldrini (onco-pediátricos) excluídos deste "
          "grupo por já estarem na lista do item 1.10. ATENÇÃO ao GPACI "
          "(2079321): a sigla significa 'Grupo de Pesquisa e Assistência ao "
          "Câncer INFANTIL' — possível onco-pediátrico não capturado; "
          "confirmar com Alberto se deve migrar para a lista de exclusão.")
    return t


def comparar_mortalidade(df, onco_tab):
    titulo("P6.2 — MORTALIDADE DOS ONCOLÓGICOS × PARES")

    onco = set(onco_tab["cnes"])
    d = df.copy()
    d["grupo"] = np.where(d["cnes"].isin(onco), "Oncológico (adulto)", "resto")

    sub("Medianas de mort_all (hospital-ano)")
    m_onco = d.loc[d["grupo"] == "Oncológico (adulto)", "mort_all"].median()
    fil = d[d["modelo_gestao_proxy"] == "Filantrópico"]
    m_fil_sem = fil.loc[~fil["cnes"].isin(onco), "mort_all"].median()
    m_painel = d["mort_all"].median()
    print(f"  Oncológicos (adultos):            {m_onco:.4f}")
    print(f"  Filantrópico SEM os oncológicos:  {m_fil_sem:.4f}")
    print(f"  Painel completo:                  {m_painel:.4f}")

    sub("Comparação dentro da MESMA faixa Barcelona (mediana de mort_all)")
    for fx in sorted(d.loc[d["cnes"].isin(onco), "faixa_barcelona"].unique()):
        df_fx = d[d["faixa_barcelona"] == fx]
        o = df_fx[df_fx["cnes"].isin(onco)]
        r = df_fx[~df_fx["cnes"].isin(onco)]
        print(f"  faixa {fx}: oncológicos {o['mort_all'].median():.4f} "
              f"({o['cnes'].nunique()} CNES) | demais da faixa "
              f"{r['mort_all'].median():.4f} ({r['cnes'].nunique()} CNES) | "
              f"tmp onc {o['tmp'].median():.2f} vs demais {r['tmp'].median():.2f}")

    sub("Hipótese de composição: TMP e fração de alta complexidade")
    g = (d.groupby("grupo")[["tmp", "pct_alta_complex", "mort_all", "qtde"]]
         .median().round(4))
    print(g.to_string())
    fil_n_onco = fil[~fil["cnes"].isin(onco)]
    print(f"\n  TMP mediano: oncológicos "
          f"{d.loc[d['grupo'] == 'Oncológico (adulto)', 'tmp'].median():.2f} "
          f"dias vs Filantrópico não-oncológico "
          f"{fil_n_onco['tmp'].median():.2f} dias")

    sub("Presença em extremos_mort_all_bottom10.csv (base bruta, menores "
        "mortalidades)")
    ext = pd.read_csv(PASTA_TAB / "extremos_mort_all_bottom10.csv",
                      encoding="utf-8-sig")
    hit = ext[ext["cnes"].isin(onco)]
    print(hit.to_string(index=False) if len(hit) else
          "  (nenhum oncológico adulto entre os bottom-10 de mortalidade — "
          "os extremos de mortalidade zero são outros perfis)")


def p4b_santa_casa_sbc(df):
    titulo("P4b — SANTA CASA DE S. BERNARDO DO CAMPO (3223728): "
           "trajetória ano a ano")
    t = (df[df["cnes"] == 3223728]
         [["ano", "mort_all", "tmp", "qtde_sem_covid", "ocupacao_internacao"]]
         .sort_values("ano"))
    t["mort_all"] = (100 * t["mort_all"]).round(1)
    print(t.round(2).to_string(index=False))
    print("  (leitura: se mort_all fica alta em todos ou quase todos os anos, "
          "o padrão é consistente — perfil de retaguarda —, não ano-anomalia; "
          "ela não aparece em nenhuma tabela de extremos hospital-ano.)")


def p5b_medianas_sem_20(df):
    titulo("P5b — MEDIANAS DE GRUPO SEM OS 20 CNES DA LISTA DE EXCLUSÃO "
           "(números para o memorando)")
    inds = ["mort_all", "tmp", "custo_saida", "pct_alta_complex"]
    for rot, dfx in [("Painel atual (314)", df),
                     ("Sem os 20 CNES (294)", df[~df["cnes"].isin(LISTA_20)])]:
        g = dfx.groupby("modelo_gestao_proxy")[inds].median().round(4)
        g.insert(0, "n_cnes", dfx.groupby("modelo_gestao_proxy")["cnes"]
                 .nunique())
        print(f"\n  {rot}:")
        print(g.to_string())


def main():
    print("=" * LARG)
    print("PASSO 6 (+P4b, P5b) — 14/07/2026 — SOMENTE LEITURA")
    print("=" * LARG)
    base.configurar_diretorios()
    bruto, df, cl = carregar()
    print(f"[CARGA] definitivo {df['cnes'].nunique()} CNES / {len(df)} linhas")

    onco_tab = identificar_oncologicos(bruto, df, cl)
    comparar_mortalidade(df, onco_tab)
    p4b_santa_casa_sbc(df)
    p5b_medianas_sem_20(df)

    print("\n" + "=" * LARG)
    print("FIM — nenhum arquivo do pipeline foi alterado.")
    print("=" * LARG)


if __name__ == "__main__":
    main()
