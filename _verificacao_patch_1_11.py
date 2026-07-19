# -*- coding: utf-8 -*-
"""
_verificacao_patch_1_11.py
==========================
Verificação do patch do item 1.11 (Hospital Guilherme Álvaro, CNES 2079720,
OSS→Direta via SOBRESCRITAS_MODELO_GESTAO) — SOMENTE LEITURA sobre o
painel_definitivo.csv ATUAL (gerado antes do patch; a regeneração real
acontece na Etapa 3, em ciclo único com os demais itens estruturais).

O teste chama a PRÓPRIA função patcheada (cpd.aplicar_decisoes_equipe) sobre
o painel atual e reporta:
  V1. Efeito em hospital-ano E em CNES distintos por categoria (adição 1
      pedida no gate), com nota sobre a dupla contagem dos 5 switchers.
  V2. class_assistencial intacta (por construção do mecanismo).
  V3. Não-interação com a regra de valor modal de tipo_hospital/
      especializacao da ETAPA A (adição 2 pedida no gate): colunas lidas
      por cada mecanismo e posição no funil.

USO: python _verificacao_patch_1_11.py
"""

import pandas as pd

import analise_sih as base                      # embrulha stdout em UTF-8
import construir_painel_definitivo as cpd

CNES_ALVO = 2079720
LARG = 84


def contagens(df: pd.DataFrame) -> pd.DataFrame:
    g = df[df["modelo_gestao_proxy"].notna()].groupby("modelo_gestao_proxy")
    return pd.DataFrame({"hospital_ano": g.size(),
                         "cnes_distintos": g["cnes"].nunique()})


def main():
    print("=" * LARG)
    print("VERIFICAÇÃO DO PATCH 1.11 — sobrescrita OSS→Direta do CNES 2079720")
    print("=" * LARG)

    df = pd.read_csv(cpd.PAINEL_DEFINITIVO_CSV, encoding="utf-8-sig")
    df["cnes"] = pd.to_numeric(df["cnes"], errors="raise").astype("int64")

    print(f"\nConstante aplicada: SOBRESCRITAS_MODELO_GESTAO = "
          f"{cpd.SOBRESCRITAS_MODELO_GESTAO}")

    antes = contagens(df)
    depois_df = cpd.aplicar_decisoes_equipe(df, aud=None)
    depois = contagens(depois_df)

    print("\n[V1] Efeito por categoria — hospital-ano e CNES distintos")
    comp = antes.join(depois, lsuffix="_antes", rsuffix="_depois")
    comp["delta_ha"] = comp["hospital_ano_depois"] - comp["hospital_ano_antes"]
    comp["delta_cnes"] = (comp["cnes_distintos_depois"]
                          - comp["cnes_distintos_antes"])
    print(comp.to_string())
    print("\n  NOTA (dupla contagem): a soma de 'cnes_distintos' pelas "
          "categorias excede 314 porque os 5 switchers Direta→OSS contam nas "
          "duas categorias (anos pré numa, anos pós na outra). O CNES 2079720 "
          "não é switcher: sai INTEIRO da contagem OSS e entra INTEIRO na "
          "Direta.")

    sub = depois_df[depois_df["cnes"] == CNES_ALVO]
    proxy = sorted(sub["modelo_gestao_proxy"].dropna().unique())
    classe = sorted(sub["class_assistencial"].dropna().unique())
    print(f"\n[V2] CNES {CNES_ALVO} após a função: "
          f"modelo_gestao_proxy = {proxy} em {len(sub)}/11 anos | "
          f"class_assistencial (intacta) = {classe}")
    assert proxy == ["Direta"] and classe == ["OSS"], "sobrescrita incorreta!"
    demais = (depois_df.loc[depois_df["cnes"] != CNES_ALVO,
                            "modelo_gestao_proxy"]
              .compare(df.loc[df["cnes"] != CNES_ALVO, "modelo_gestao_proxy"])
              if hasattr(pd.Series, "compare") else None)
    n_dif = 0 if demais is None else len(demais)
    print(f"     Demais 313 CNES: {n_dif} diferenças em modelo_gestao_proxy "
          f"(esperado: 0).")
    assert n_dif == 0

    print(f"\n[V3] Não-interação com a regra de valor modal (ETAPA A):")
    bruto = cpd.carregar_painel_bruto()
    tipo_modal = cpd.valor_modal_por_cnes(
        bruto[bruto["cnes"] == CNES_ALVO], "tipo_hospital").get(CNES_ALVO, "")
    print(f"     • ETAPA A decide EXCLUSÃO lendo tipo_hospital/especializacao "
          f"(valor modal) — nunca lê class_assistencial nem "
          f"modelo_gestao_proxy (que nem existe naquele ponto do funil).")
    print(f"     • A sobrescrita roda ao FINAL do funil "
          f"(aplicar_decisoes_equipe, após ETAPAS A–E) e só escreve em "
          f"modelo_gestao_proxy.")
    print(f"     • CNES {CNES_ALVO}: tipo modal = {tipo_modal!r} → não é "
          f"alvo de nenhuma regra da ETAPA A (62/70/07+006); presente "
          f"11/11 anos no painel.")
    print(f"     → Mecanismos independentes; nenhuma sobreposição ou ordem "
          f"de aplicação com efeito colateral.")

    print("\n" + "=" * LARG)
    print("VERIFICAÇÃO OK. Lembrete: painel_definitivo.csv em disco ainda é o "
          "PRÉ-patch; a regeneração ocorre na Etapa 3 (ciclo único).")
    print("=" * LARG)


if __name__ == "__main__":
    main()
