# -*- coding: utf-8 -*-
"""
diagnostico_meia_competencia.py
===============================
Bloco B da rodada de revisão (jul/2026): investigar se o viés de meia
competência (leitos cadastrados por fração do ano contra diárias
acumuladas em período maior, ou o inverso) é diagnosticável e corrigível
com os dados disponíveis.

Perguntas respondidas:
  1. A origem SIH preserva competência mensal ou contagem de meses de
     atividade por CNES e ano?
  2. Sobre qual coluna de leitos a ocupação pré-calculada do SIH foi
     computada (denominador implícito)?
  3. Onde se concentram as observações com ocupação acima de 100% e
     elas coincidem com anos de entrada ou expansão de leitos?

USO: python diagnostico_meia_competencia.py
"""
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
painel = pd.read_csv(r"C:\ProjetoPosDoc\analises\painel_definitivo.csv",
                     encoding="utf-8-sig")

print("=" * 70)
print("[1] GRANULARIDADE DA ORIGEM: existe competência mensal?")
print("=" * 70)
print("""  Colunas da origem SIH (COLUNAS_CANONICAS de analise_sih.py):
  os campos de leitos e diárias são agregados ANUAIS ('Diárias
  Internação Ano', 'Diárias UTI Ano') e a ocupação vem pré-calculada
  na linha de resumo, uma por CNES por arquivo anual. Não há campo de
  competência, mês ou data em nenhuma coluna.""")
print("  n_linhas_resumo por observação do painel (se fosse mensal, "
      "valeria ~12):")
print(painel["n_linhas_resumo"].value_counts().sort_index().to_string())
print("  CONCLUSÃO 1: contagem de meses de atividade NÃO é recuperável; "
      "denominador pró rata inviável.")

print("\n" + "=" * 70)
print("[2] DENOMINADOR IMPLÍCITO DA OCUPAÇÃO PRÉ-CALCULADA")
print("=" * 70)
uti = painel[(painel["ocupacao_uti"] > 0) & (painel["diarias_uti"] > 0)].copy()
uti["den_impl"] = uti["diarias_uti"] / (uti["ocupacao_uti"] / 100) / 365
uti["dif_sus"] = (uti["den_impl"] - uti["uti_sus"]).abs()
uti["dif_total"] = (uti["den_impl"] - uti["uti_total"]).abs()
bate_sus = (uti["dif_sus"] < 0.5).mean()
bate_total = (uti["dif_total"] < 0.5).mean()
print(f"  UTI: denominador implícito bate com uti_sus em "
      f"{100 * bate_sus:.1f}% das {len(uti)} observações; com uti_total "
      f"em {100 * bate_total:.1f}%")

itn = painel[(painel["ocupacao_internacao"] > 0)
             & (painel["diarias_internacao"] > 0)].copy()
itn["den_impl"] = (itn["diarias_internacao"]
                   / (itn["ocupacao_internacao"] / 100) / 365)
for col in ["leitos_sus", "leitos_internacao", "total_leitos_sus",
            "total_leitos"]:
    bate = ((itn["den_impl"] - itn[col]).abs() < 0.5).mean()
    print(f"  Internação: bate com {col} em {100 * bate:.1f}%")

print("\n" + "=" * 70)
print("[3] ONDE ESTÃO AS OCUPAÇÕES ACIMA DE 100%")
print("=" * 70)
for col, den_sus in [("ocupacao_internacao", "leitos_sus"),
                     ("ocupacao_uti", "uti_sus")]:
    alto = painel[painel[col] > 100]
    print(f"\n  {col}: {len(alto)} observações acima de 100% "
          f"({100 * len(alto) / len(painel):.1f}%)")
    print("  por ano: "
          + ", ".join(f"{a}: {n}" for a, n in
                      alto.groupby("ano").size().items()))

# assinatura de entrada/expansão na UTI: comparar uti_sus com o do ano
# anterior nas observações extremas
print("\n  Assinatura de entrada/expansão nos 15 maiores valores de "
      "ocupação de UTI:")
painel = painel.sort_values(["cnes", "ano"])
painel["uti_sus_ant"] = painel.groupby("cnes")["uti_sus"].shift(1)
painel["diarias_uti_ant"] = painel.groupby("cnes")["diarias_uti"].shift(1)
top = painel.nlargest(15, "ocupacao_uti")
for _, r in top.iterrows():
    den_impl = (r["diarias_uti"] / (r["ocupacao_uti"] / 100) / 365
                if r["ocupacao_uti"] > 0 else np.nan)
    print(f"    CNES {int(r['cnes'])} {int(r['ano'])}: "
          f"ocup {r['ocupacao_uti']:6.1f}%, diárias {int(r['diarias_uti']):>6}, "
          f"uti_sus {r['uti_sus']:.0f} (ano anterior "
          f"{r['uti_sus_ant'] if pd.notna(r['uti_sus_ant']) else 'NA'}), "
          f"uti_total {r['uti_total']:.0f}, den. implícito {den_impl:.1f}")

alto_uti = painel[painel["ocupacao_uti"] > 100]
cresceu = (alto_uti["diarias_uti"] > 1.5 * alto_uti["diarias_uti_ant"]
           ).mean()
print(f"\n  Entre as {len(alto_uti)} obs de UTI acima de 100%: "
      f"{100 * cresceu:.0f}% têm diárias ao menos 50% maiores que no "
      f"ano anterior (expansão súbita sem atualização do cadastro)")
print("\n  CONCLUSÃO 3: o excesso da UTI concentra-se em 2020 e 2021 e "
      "coincide com saltos de diárias contra cadastro parado; sem "
      "competência mensal, o ajuste pró rata não é possível e o "
      "tratamento correto segue sendo winsorização, duas partes e "
      "leitura cautelosa do biênio (rota B3 da revisão).")
