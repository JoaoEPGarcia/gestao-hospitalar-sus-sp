# -*- coding: utf-8 -*-
"""
_investigacao_blocos34_6_14jul2026.py
=====================================
Investigação SOMENTE-LEITURA dos Blocos 3, 4 e 6 do prompt de 14/07/2026.
Nenhum arquivo do pipeline é alterado; nenhum CNES é excluído.

  B3. Ampliação do item 1.10: candidatos de perfil PSIQUIÁTRICO no painel
      definitivo que escaparam do filtro tipo 07 + espec. 006 (por nome,
      por especialização em anos isolados, ou pela planilha Barcelona).
  B4. Os ~18 CNES de longa permanência (TMP mediano > 20 dias, empilhados
      no teto de censura ~30,5): classificação caso a caso em
      (a) ligado a critério de exclusão já adotado (psiquiátrico/pediátrico),
      (b) causa identificada fora dos critérios (longa permanência legítima
          — mantém com ressalva de censura),
      (c) causa não identificada (decisão manual).
  B6. Item 1.13 — viabilidade de mortalidade estratificada por complexidade
      (mort_alta_complex / mort_baixa_complex): o que os dados atuais
      permitem, o que exige re-stream, e estimativa de denominadores
      pequenos/instáveis.

USO: python _investigacao_blocos34_6_14jul2026.py
"""

import re

import numpy as np
import pandas as pd

import analise_sih as base                      # embrulha stdout em UTF-8
import construir_painel_definitivo as cpd

LARG = 84
PASTA_TAB = base.PASTA_TABELAS

CNES_PED_INEQUIVOCOS = {2071371, 2078325, 2080427, 2088517, 2081482, 2089696}
CNES_CASAS_CRIANCA   = {2076985, 2082454}       # decisão 14/07/2026: excluir
SWITCHERS            = {2078287, 2081695, 2082225, 2091755, 2750511}

PAT_PSIQ  = re.compile(r"PSIQUIATR|SAUDE MENTAL|MANICOM")
PAT_PED   = re.compile(r"INFANTIL|PEDIATR|CRIANCA")
PAT_LONGA = re.compile(r"REABILIT|CRONIC|PALIATIV|LONGA PERMAN|RETAGUARDA|"
                       r"\bLAR\b|CASAS ANDRE|CASA DE DAVID|CRUZ VERDE|"
                       r"ANOMALIA|DEFICIEN")


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


def _sinais_por_cnes(bruto, cl):
    """Texto agregado por CNES (nomes + especializações de todos os anos +
    Instituição Barcelona), normalizado, para busca de padrões."""
    nm = bruto[["cnes", "nome_fantasia"]].dropna()
    nm["t"] = nm["nome_fantasia"].map(cpd.normalizar_texto)
    es = bruto[["cnes", "especializacao"]].dropna()
    es["t"] = es["especializacao"].map(cpd.normalizar_texto)
    ins = cl[["cnes", "Instituição"]].dropna()
    ins["t"] = ins["Instituição"].map(cpd.normalizar_texto)
    tudo = pd.concat([nm[["cnes", "t"]], es[["cnes", "t"]], ins[["cnes", "t"]]])
    return tudo.groupby("cnes")["t"].apply(lambda s: " | ".join(sorted(set(s))))


# ══════════════════════════════════════════════════════════════════════════════
# B3 — PERFIL PSIQUIÁTRICO NÃO CAPTURADO PELO FILTRO 07+006
# ══════════════════════════════════════════════════════════════════════════════

def bloco3_psiquiatricos(bruto, df, cl, sinais):
    titulo("B3 — CANDIDATOS DE PERFIL PSIQUIÁTRICO NO PAINEL DEFINITIVO "
           "(escaparam do filtro tipo 07 + espec. 006)")

    def_cnes = set(df["cnes"].unique())

    sub("Checagem 1 — especializacao 006/psiquiatria em QUALQUER ano (bruto), "
        "para CNES do painel definitivo")
    es = bruto[bruto["cnes"].isin(def_cnes)][["cnes", "ano", "especializacao"]]
    es = es.dropna(subset=["especializacao"]).copy()
    es["norm"] = es["especializacao"].map(cpd.normalizar_texto)
    hit006 = es[es["norm"].str.contains(r"006|PSIQUIATR", regex=True)]
    if len(hit006):
        print(hit006.to_string(index=False))
    else:
        print("  (nenhum CNES do painel definitivo declarou especialização "
              "psiquiátrica em nenhum ano)")

    sub("Checagem 2 — nome/Instituição com PSIQUIATR / SAUDE MENTAL / MANICOM")
    cand = {c for c in def_cnes if PAT_PSIQ.search(sinais.get(c, ""))}
    if not cand:
        print("  (nenhum)")
        return set()
    nomes = cpd.nome_referencia_por_cnes(bruto)
    inst = cl.set_index("cnes")["Instituição"]
    tmp_med = df[df["tmp"] > 0].groupby("cnes")["tmp"].median()
    proxy = df.sort_values("ano").groupby("cnes")["modelo_gestao_proxy"].last()
    tipo_modal = cpd.valor_modal_por_cnes(bruto, "tipo_hospital")
    espec_modal = cpd.valor_modal_por_cnes(bruto, "especializacao")
    for c in sorted(cand):
        print(f"  CNES {c}: {nomes.get(c) or inst.get(c, '')} | "
              f"tipo modal {tipo_modal.get(c, '?')!r} | "
              f"espec modal {espec_modal.get(c, '(vazia)')!r} | "
              f"gestão {proxy.get(c, '?')} | tmp mediano "
              f"{tmp_med.get(c, float('nan')):.1f} dias")
    print("\n  → Escaparam do filtro 07+006 porque a ESPECIALIZAÇÃO modal não "
          "é 006 (vazia ou '-') — o filtro atual exige tipo 07 E espec 006.")
    print("  >>> NADA excluído: lista de candidatos para validação.")
    return cand


# ══════════════════════════════════════════════════════════════════════════════
# B4 — OS 18 CNES DE LONGA PERMANÊNCIA, CASO A CASO
# ══════════════════════════════════════════════════════════════════════════════

def bloco4_longa_permanencia(bruto, df, cl, sinais, cand_psiq):
    titulo("B4 — CNES DE LONGA PERMANÊNCIA (TMP mediano > 20 dias): "
           "classificação caso a caso — NADA é excluído")

    tmp_med = df[df["tmp"] > 0].groupby("cnes")["tmp"].median()
    grupo = tmp_med[tmp_med > 20].sort_values(ascending=False)

    nomes = cpd.nome_referencia_por_cnes(bruto)
    inst = cl.set_index("cnes")["Instituição"]
    mun = (bruto[bruto["municipio"].notna()].sort_values("ano")
           .groupby("cnes")["municipio"].last())
    tipo_modal = cpd.valor_modal_por_cnes(bruto, "tipo_hospital")
    espec_modal = cpd.valor_modal_por_cnes(bruto, "especializacao")
    proxy = df.sort_values("ano").groupby("cnes")["modelo_gestao_proxy"].last()
    porte = df.sort_values("ano").groupby("cnes")["porte_hospital"].last()
    faixa = df.groupby("cnes")["faixa_barcelona"].first()
    mort_med = df.groupby("cnes")["mort_all"].median()
    no_teto = df[df["tmp"] >= 30.0].groupby("cnes")["ano"].nunique()

    linhas = []
    for c, tmp_v in grupo.items():
        s = sinais.get(c, "")
        f_psiq = bool(PAT_PSIQ.search(s)) or c in cand_psiq
        f_ped = bool(PAT_PED.search(s)) or c in CNES_PED_INEQUIVOCOS \
            or c in CNES_CASAS_CRIANCA
        f_longa = bool(PAT_LONGA.search(s))
        if c in CNES_CASAS_CRIANCA:
            classe = "(a) EXCLUIR — pediátrico (decisão 14/07 já tomada)"
        elif f_psiq:
            classe = "(a) candidato a exclusão — perfil psiquiátrico"
        elif f_ped:
            classe = "(a) candidato a exclusão — perfil pediátrico"
        elif f_longa:
            classe = "(b) mantém — longa permanência fora dos critérios; " \
                     "ressalva de censura 30,5d"
        else:
            classe = "(c) causa não identificada — decisão manual"
        linhas.append({
            "cnes": c,
            "nome": (nomes.get(c) or inst.get(c, ""))[:44],
            "municipio": str(mun.get(c, ""))[:18],
            "gestao": proxy.get(c, ""),
            "porte": porte.get(c, ""),
            "faixa_b": faixa.get(c, ""),
            "tipo_modal": str(tipo_modal.get(c, ""))[:26],
            "espec_modal": str(espec_modal.get(c, "(vazia)"))[:16],
            "tmp_med": round(tmp_v, 1),
            "anos_tmp>=30": int(no_teto.get(c, 0)),
            "mort_med": round(mort_med.get(c, float("nan")), 3),
            "classificacao": classe,
        })
    t = pd.DataFrame(linhas)
    with pd.option_context("display.width", 400, "display.max_columns", 20,
                           "display.max_rows", 100,
                           "display.max_colwidth", 70):
        print(t.to_string(index=False))

    sub("Resumo da classificação")
    resumo = t["classificacao"].str.slice(0, 3).value_counts()
    print(resumo.to_string())
    switch_priv = t[(t["cnes"].isin(SWITCHERS)) | (t["gestao"] == "Privado")]
    print(f"\n  Switchers ou Privado no grupo: "
          f"{'NENHUM' if switch_priv.empty else switch_priv['cnes'].tolist()}")
    print("  >>> NADA excluído — alimenta o dossiê do item 1.10 e a decisão "
          "de Priscilla (memorando, pergunta 3).")
    return t


# ══════════════════════════════════════════════════════════════════════════════
# B6 — VIABILIDADE: MORTALIDADE ESTRATIFICADA POR COMPLEXIDADE (item 1.13)
# ══════════════════════════════════════════════════════════════════════════════

def bloco6_viabilidade(df):
    titulo("B6 (item 1.13) — VIABILIDADE de mort_alta_complex / "
           "mort_baixa_complex (somente análise; nada implementado)")

    print("""\
[Viabilidade estrutural — leitura de analise_sih.py]
  • Cada linha de PRODUÇÃO do SIH carrega, na MESMA linha: QTDE, DESFECHO
    (usado em eh_obito/eh_obito_versao_b), COMPLEX (usado em
    qtde_alta_complex) e Cód Grupo/Subgrupo (usado em eh_covid).
  • Logo, o cruzamento óbito × alta complexidade É VIÁVEL no nível de
    linha: basta acumular qtde_obito_alta_complex (e a variante versão B)
    quando eh_obito(desfecho) E complex == 'Alta complexidade'.
  • O painel em CACHE (painel_hospital_ano) NÃO guarda esse cruzamento —
    só os totais marginais. Portanto EXIGE reprocessamento dos 11 arquivos
    brutos (83–108 MB cada), por um de dois caminhos:
      (i) estender _prod0()/processar_arquivo_sih() em analise_sih.py com
          os novos acumuladores e reconstruir o cache completo (apagar
          painel_hospital_ano.*) — 1 rodada completa de streaming; ou
      (ii) re-stream dedicado no molde de restream_numeradores_covid()
          (construir_painel_definitivo.py), acumulando apenas os novos
          numeradores — mesmo custo de leitura, sem tocar no cache.
    Custo: 1 leitura integral dos 11 xlsx (ordem de grandeza da construção
    original do painel). Recomendação: caminho (i), porque a Etapa 3 já
    prevê reexecução completa com cache invalidado.
  • Versões com/sem COVID: VIÁVEL — eh_covid é decidido na mesma linha;
    basta acumular também os numeradores/denominadores condicionais a
    COVID em 2020-2021 (mesma lógica já usada para mort_all).

[Variáveis propostas — mesma lógica de mort_all; NÃO implementadas]
  mort_alta_complex  = (obitos em internações de alta complexidade −
                        idem COVID) ÷ (qtde_alta_complex − idem COVID)
  mort_baixa_complex = (demais óbitos − idem COVID) ÷
                        (qtde − qtde_alta_complex − idem COVID)
""")

    sub("Estimativa de denominadores pequenos em mort_alta_complex "
        "(a partir do painel definitivo atual — qtde_alta_complex sem COVID)")
    d = df.copy()
    d["alta_sem_covid"] = (d["qtde_alta_complex"]
                           - d["qtde_alta_complex_covid"].fillna(0))
    d["baixa_sem_covid"] = d["qtde_sem_covid"] - d["alta_sem_covid"]
    faixas = [("= 0 (mort_alta indefinida)", d["alta_sem_covid"] <= 0),
              ("1–19 (muito instável)", (d["alta_sem_covid"] > 0)
               & (d["alta_sem_covid"] < 20)),
              ("20–49 (instável)", (d["alta_sem_covid"] >= 20)
               & (d["alta_sem_covid"] < 50)),
              ("50–99", (d["alta_sem_covid"] >= 50)
               & (d["alta_sem_covid"] < 100)),
              (">= 100 (estável)", d["alta_sem_covid"] >= 100)]
    print(f"{'faixa do denominador':32}{'hosp-ano':>9}{'% de 3.454':>12}")
    for rot, m in faixas:
        print(f"{rot:32}{int(m.sum()):>9}{100 * m.mean():>11.1f}%")

    sub("Por categoria: % de hospital-ano com denominador < 20")
    inst = d.groupby("modelo_gestao_proxy").apply(
        lambda g: pd.Series({
            "pct_denom_zero": 100 * (g["alta_sem_covid"] <= 0).mean(),
            "pct_denom_<20": 100 * (g["alta_sem_covid"] < 20).mean(),
            "mediana_denom": g["alta_sem_covid"].median(),
        }), include_groups=False).round(1)
    print(inst.to_string())

    sub("Atenção simétrica: denominador da mort_baixa_complex no grupo Privado")
    priv = d[d["modelo_gestao_proxy"] == "Privado"]
    print(f"  Privado (pct_alta ~98%): mediana de internações NÃO-alta por "
          f"hospital-ano = {priv['baixa_sem_covid'].median():.0f} "
          f"(p25 = {priv['baixa_sem_covid'].quantile(.25):.0f}) — "
          f"mort_baixa_complex será instável para os 3 CNES privados.")

    n_cnes_zero = (d.groupby("cnes")["alta_sem_covid"].sum() <= 0).sum()
    print(f"\n  CNES com ZERO alta complexidade em TODOS os anos: "
          f"{n_cnes_zero} de 314 → mort_alta_complex permanentemente "
          f"indefinida para eles.")
    print("\n  LEITURA: o cruzamento é viável e barato de especificar, mas "
          "mort_alta_complex nasce indefinida ou muito instável em cerca de "
          "metade do painel (concentrada em Filantrópico pequeno e Público "
          "Municipal). Qualquer uso em modelo precisará de regra explícita "
          "de denominador mínimo — reportar isso no memorando antes do envio.")


def main():
    print("=" * LARG)
    print("INVESTIGAÇÃO BLOCOS 3, 4 e 6 (14/07/2026) — SOMENTE LEITURA")
    print("=" * LARG)
    base.configurar_diretorios()
    bruto, df, cl = carregar()
    print(f"[CARGA] bruto {bruto['cnes'].nunique()} CNES | definitivo "
          f"{df['cnes'].nunique()} CNES / {len(df)} linhas")
    sinais = _sinais_por_cnes(bruto, cl)

    cand_psiq = bloco3_psiquiatricos(bruto, df, cl, sinais)
    bloco4_longa_permanencia(bruto, df, cl, sinais, cand_psiq)
    bloco6_viabilidade(df)

    print("\n" + "=" * LARG)
    print("FIM — nenhum arquivo do pipeline foi alterado; nenhum CNES excluído.")
    print("=" * LARG)


if __name__ == "__main__":
    main()
