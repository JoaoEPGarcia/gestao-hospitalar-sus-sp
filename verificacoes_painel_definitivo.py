# -*- coding: utf-8 -*-
"""
verificacoes_painel_definitivo.py
=================================
Bateria de verificações pós-construção sobre analises/painel_definitivo.csv.
NÃO altera o painel — apenas investiga e tabula. Quatro checagens:

  V1. Sobrevivência dos switchers Direta→OSS (5 CNES nominados) e busca por
      identificação formal de PPP nas fontes disponíveis
  V2. Os hospital-ano rotulados "Privado" no painel final: histórico completo
      de class_assistencial por ano, para detectar rotulagem pontual errada
  V3. Os CNES removidos APENAS pelo balanceamento (ETAPA D): anos presentes,
      anos faltantes, ordenados dos "quase completos" para os esparsos
  V4. Candidatos de revisão manual (ETAPA C1) em formato legível, com coluna
      vazia `decisao_manual` para preenchimento da equipe

Saídas (analises/tabelas/):
  tab_verif_switchers.csv, tab_verif_privado.csv,
  tab_verif_etapa_d.csv,  tab_revisao_manual_para_decisao.csv

USO: python verificacoes_painel_definitivo.py
"""

import pandas as pd

# Reutiliza caminhos e o wrapper UTF-8 de stdout (feito no import)
import analise_sih as base
import construir_painel_definitivo as cpd

CNES_SWITCHERS = [2078287, 2081695, 2082225, 2091755, 2750511]

TAB_SWITCHERS = base.PASTA_TABELAS / "tab_verif_switchers.csv"
TAB_PRIVADO   = base.PASTA_TABELAS / "tab_verif_privado.csv"
TAB_ETAPA_D   = base.PASTA_TABELAS / "tab_verif_etapa_d.csv"
TAB_REVISAO   = base.PASTA_TABELAS / "tab_revisao_manual_para_decisao.csv"


def carregar_bases():
    painel_def = pd.read_csv(cpd.PAINEL_DEFINITIVO_CSV, encoding="utf-8-sig")
    painel_bruto = cpd.carregar_painel_bruto()
    aud_rem = pd.read_csv(cpd.TAB_AUD_REMOVIDOS, encoding="utf-8-sig")
    aud_rev = pd.read_csv(cpd.TAB_AUD_REVISAO, encoding="utf-8-sig")
    nomes = cpd.nome_referencia_por_cnes(painel_bruto)
    # município de referência: o mais recente informado por CNES
    mun = (painel_bruto[painel_bruto["municipio"].notna()]
           .sort_values("ano").groupby("cnes")["municipio"].last())
    return painel_def, painel_bruto, aud_rem, aud_rev, nomes, mun


def _anos_producao(painel_bruto: pd.DataFrame, cnes: int) -> list[int]:
    sub = painel_bruto[(painel_bruto["cnes"] == cnes) & (painel_bruto["qtde"] > 0)]
    return sorted(sub["ano"].astype(int).unique())


# ══════════════════════════════════════════════════════════════════════════════
# V1 — SWITCHERS E PPP
# ══════════════════════════════════════════════════════════════════════════════

def v1_switchers_ppp(painel_def, painel_bruto, aud_rem, nomes, mun):
    print("\n" + "=" * 70)
    print("V1. SOBREVIVÊNCIA DOS SWITCHERS DIRETA→OSS E GRUPO PPP")
    print("=" * 70)

    anos_totais = painel_bruto["ano"].nunique()
    linhas = []
    for cnes in CNES_SWITCHERS:
        no_final = painel_def[painel_def["cnes"] == cnes]
        anos_prod = _anos_producao(painel_bruto, cnes)
        # histórico do rótulo, para confirmar a transição Direta→OSS
        hist = (painel_bruto[painel_bruto["cnes"] == cnes]
                .sort_values("ano")[["ano", "class_assistencial"]])
        hist_txt = "; ".join(f"{int(a)}={c}" for a, c in
                             zip(hist["ano"], hist["class_assistencial"].fillna("?")))
        if len(no_final):
            status, etapa_queda, motivo = "PRESENTE no painel final", "", ""
        else:
            queda = aud_rem[aud_rem["cnes"] == cnes]
            if len(queda):
                etapa_queda = queda["etapa"].iloc[0]
                motivo = queda["motivo"].iloc[0]
                status = f"REMOVIDO ({etapa_queda})"
            elif cnes not in set(painel_bruto["cnes"]):
                status, etapa_queda, motivo = (
                    "AUSENTE da própria base bruta (nunca entrou no painel)",
                    "-", "CNES sem qualquer linha no SIH 2015-2025")
            else:
                status, etapa_queda, motivo = "?", "?", "?"
        linhas.append({
            "cnes": cnes,
            "nome_referencia": nomes.get(cnes, ""),
            "municipio": mun.get(cnes, ""),
            "status": status,
            "etapa_queda": etapa_queda,
            "motivo": motivo,
            "anos_no_painel_final": len(no_final),
            "anos_com_producao_base_bruta": f"{len(anos_prod)}/{anos_totais}",
            "historico_class_assistencial": hist_txt,
        })
    df = pd.DataFrame(linhas)
    df.to_csv(TAB_SWITCHERS, index=False, encoding="utf-8-sig")
    with pd.option_context("display.max_colwidth", 200, "display.width", 250):
        print(df.drop(columns=["historico_class_assistencial"]).to_string(index=False))
        print("\nHistórico do rótulo class_assistencial (confirmação da transição):")
        for _, r in df.iterrows():
            print(f"  {r['cnes']}: {r['historico_class_assistencial']}")

    # ── PPP: existe identificação formal em alguma fonte? ────────────────────
    print("\n--- Identificação de PPP nas fontes disponíveis ---")
    vals_sih = sorted(painel_bruto["class_assistencial"].dropna().unique())
    ppp_sih = [v for v in vals_sih if "PPP" in v.upper() or "PARCERIA" in v.upper()]
    print(f"Valores de class_assistencial no SIH: {vals_sih}")
    print(f"Valores contendo PPP/Parceria: {ppp_sih if ppp_sih else 'NENHUM'}")

    _, path_classif, _ = base.localizar_arquivos(base.PASTA_DADOS)
    df_classif = base.carregar_classificacao(path_classif)
    print(f"Colunas da classificação Barcelona: {list(df_classif.columns)}")
    tem_gestao = [c for c in df_classif.columns
                  if any(t in str(c).upper() for t in
                         ["GEST", "PPP", "PARCERIA", "ADMINISTRA", "NATUREZA"])]
    print(f"Colunas com cara de modelo de gestão: {tem_gestao if tem_gestao else 'NENHUMA'}")


# ══════════════════════════════════════════════════════════════════════════════
# V2 — HOSPITAL-ANO "PRIVADO" NO PAINEL FINAL
# ══════════════════════════════════════════════════════════════════════════════

def v2_privado(painel_def, nomes, mun):
    print("\n" + "=" * 70)
    print("V2. HOSPITAL-ANO ROTULADOS 'PRIVADO' NO PAINEL FINAL")
    print("=" * 70)

    priv = painel_def[painel_def["class_assistencial"] == "Privado"]
    cnes_priv = sorted(priv["cnes"].unique())
    print(f"{len(priv)} hospital-ano 'Privado', {len(cnes_priv)} CNES distintos: "
          f"{cnes_priv}")

    # timeline do rótulo por CNES (todas as 11 colunas de ano)
    linhas = []
    for cnes in cnes_priv:
        sub = painel_def[painel_def["cnes"] == cnes].sort_values("ano")
        rotulos = dict(zip(sub["ano"].astype(int),
                           sub["class_assistencial"].fillna("?")))
        outros = sorted(set(rotulos.values()) - {"Privado"})
        linhas.append({
            "cnes": cnes,
            "nome_referencia": nomes.get(cnes, ""),
            "municipio": mun.get(cnes, ""),
            "anos_como_Privado": sum(v == "Privado" for v in rotulos.values()),
            "outros_rotulos_no_periodo": "; ".join(outros) if outros else "(nenhum — sempre Privado)",
            **{f"a{ano}": rot for ano, rot in rotulos.items()},
        })
    df = pd.DataFrame(linhas)
    df.to_csv(TAB_PRIVADO, index=False, encoding="utf-8-sig")
    with pd.option_context("display.max_colwidth", 60, "display.width", 300,
                           "display.max_columns", 50):
        print(df.to_string(index=False))
    n_mistos = (df["outros_rotulos_no_periodo"] != "(nenhum — sempre Privado)").sum()
    print(f"\nCNES com rótulo misto (indício de erro pontual de rotulagem): "
          f"{n_mistos}/{len(df)}")


# ══════════════════════════════════════════════════════════════════════════════
# V3 — REMOVIDOS APENAS PELO BALANCEAMENTO (ETAPA D)
# ══════════════════════════════════════════════════════════════════════════════

def v3_etapa_d(painel_bruto, aud_rem, nomes, mun):
    print("\n" + "=" * 70)
    print("V3. CNES REMOVIDOS APENAS PELO BALANCEAMENTO (ETAPA D)")
    print("=" * 70)

    anos_todos = sorted(painel_bruto["ano"].astype(int).unique())
    rem_d = aud_rem[aud_rem["etapa"] == "ETAPA D"]["cnes"].astype(int).tolist()
    print(f"{len(rem_d)} CNES removidos na ETAPA D (esperado: 82)")

    linhas = []
    for cnes in rem_d:
        anos_prod = _anos_producao(painel_bruto, cnes)
        faltam = sorted(set(anos_todos) - set(anos_prod))
        linhas.append({
            "cnes": cnes,
            "nome_referencia": nomes.get(cnes, ""),
            "municipio": mun.get(cnes, ""),
            "anos_presentes": len(anos_prod),
            "de_possiveis": len(anos_todos),
            "anos_faltantes": ", ".join(str(a) for a in faltam),
        })
    df = (pd.DataFrame(linhas)
          .sort_values(["anos_presentes", "cnes"], ascending=[False, True])
          .reset_index(drop=True))
    df.to_csv(TAB_ETAPA_D, index=False, encoding="utf-8-sig")

    print("\nDistribuição por nº de anos presentes:")
    print(df["anos_presentes"].value_counts().sort_index(ascending=False)
          .rename_axis("anos_presentes").rename("n_cnes").to_string())
    print("\nLista completa (do mais completo para o mais esparso):")
    with pd.option_context("display.max_colwidth", 55, "display.width", 250,
                           "display.max_rows", 200):
        print(df.to_string(index=False))


# ══════════════════════════════════════════════════════════════════════════════
# V4 — REVISÃO MANUAL EM FORMATO PARA DECISÃO
# ══════════════════════════════════════════════════════════════════════════════

def v4_revisao_manual(painel_bruto, aud_rev, nomes, mun):
    print("\n" + "=" * 70)
    print("V4. CANDIDATOS DE REVISÃO MANUAL (ETAPA C1) — PARA DECISÃO DA EQUIPE")
    print("=" * 70)

    rev = aud_rev[aud_rev["etapa"] == "ETAPA C1"].copy()
    linhas = []
    for _, r in rev.iterrows():
        cnes = int(r["cnes"])
        anos_prod = _anos_producao(painel_bruto, cnes)
        linhas.append({
            "cnes": cnes,
            "nome_referencia": nomes.get(cnes, ""),
            "municipio": mun.get(cnes, ""),
            "anos_com_producao": ", ".join(str(a) for a in anos_prod),
            "n_anos": len(anos_prod),
            "situacao_no_funil": r["questao"],
            "decisao_manual": "",          # ← preencher pela equipe
        })
    df = pd.DataFrame(linhas).sort_values("cnes").reset_index(drop=True)
    df.to_csv(TAB_REVISAO, index=False, encoding="utf-8-sig")
    with pd.option_context("display.max_colwidth", 70, "display.width", 300):
        print(df.drop(columns=["situacao_no_funil"]).to_string(index=False))
    print(f"\nTabela completa (com a coluna 'decisao_manual' vazia) → {TAB_REVISAO}")


def main():
    painel_def, painel_bruto, aud_rem, aud_rev, nomes, mun = carregar_bases()
    v1_switchers_ppp(painel_def, painel_bruto, aud_rem, nomes, mun)
    v2_privado(painel_def, nomes, mun)
    v3_etapa_d(painel_bruto, aud_rem, nomes, mun)
    v4_revisao_manual(painel_bruto, aud_rev, nomes, mun)
    print("\nVerificações concluídas. Nenhuma alteração feita no painel.")


if __name__ == "__main__":
    main()
