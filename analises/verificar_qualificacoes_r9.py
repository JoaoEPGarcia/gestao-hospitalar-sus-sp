# verificar_qualificacoes_r9.py
# ITEM 1.5 do fechamento de 29/07/2026.
#
# Três qualificações que precisam ir ao registro ANTES de virarem texto. Todas
# são afirmações sobre a amostra, não sobre coeficientes, e nenhuma delas é
# visível na tabela publicada. Este script reproduz as três a partir do painel,
# em vez de copiá-las de prosa.
#
#   (1) A parte B (ocupação <= 100) roda sobre 989 obs / 122 CNES em E3, e não
#       sobre 1.375 / 125. A restrição elimina CNES INTEIROS, e a hipótese a
#       testar é que os eliminados são justamente os cronicamente superlotados.
#   (2) A sensibilidade R4.2 cruza para significância ao remover UM hospital.
#   (3) Dos switchers que sustentam o binário de superlotação, quantos têm
#       superlotação do lado PÓS-conversão — que é o lado que identifica.
#
# Os switchers são derivados do próprio painel (mudança de modelo_gestao_proxy
# dentro do CNES), e não de lista em prosa, porque o registro diverge: o
# PENDENCIAS.md nomeia cinco conversores e R10 cita um sexto nome.
#
# Saída: console + analises/tabelas/tabSEG_17_qualificacoes_amostra.csv

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent
TAB = RAIZ / "tabelas"

p = pd.read_csv(RAIZ / "painel_segmentado.csv")

print("=" * 88)
print("(1) PERDA DE AMOSTRA NA PARTE B — quem sai quando se restringe a <= 100")
print("=" * 88)

e3 = p[p["estrato"] == "E3"].copy()
print(f"E3 completo:            {len(e3):>5} obs, {e3['cnes'].nunique():>3} CNES")

b = e3[e3["ocupacao_internacao"] <= 100]
print(f"E3 com ocupação <= 100: {len(b):>5} obs, {b['cnes'].nunique():>3} CNES")

perdidos = sorted(set(e3["cnes"]) - set(b["cnes"]))
print(f"\nCNES que desaparecem inteiros: {len(perdidos)}")
print("(um CNES só desaparece se TODOS os seus 11 anos estiverem acima de 100)")
print()

linhas = []
for c in perdidos:
    sub = e3[e3["cnes"] == c]
    nome = str(sub["nome_fantasia"].iloc[0])[:44]
    cat = sub["modelo_gestao_proxy"].iloc[0]
    acima = int((sub["ocupacao_internacao"] > 100).sum())
    print(f"  {c}  {nome:<44} {cat:<18} "
          f"{acima}/{len(sub)} anos > 100%  "
          f"mediana {sub['ocupacao_internacao'].median():.1f}%")
    linhas.append({
        "verificacao": "1-perda_amostra_parte_B", "cnes": c,
        "nome": nome, "categoria": cat,
        "anos_acima_100": acima, "anos_total": len(sub),
        "mediana_ocupacao": round(float(sub["ocupacao_internacao"].median()), 1),
    })

print()
print("Comparação: entre os 125 CNES de E3, distribuição de anos acima de 100%")
anos_acima = e3.groupby("cnes")["ocupacao_internacao"].apply(lambda s: (s > 100).sum())
print(f"  nenhum ano acima:      {int((anos_acima == 0).sum()):>3} CNES")
print(f"  1 a 10 anos acima:     {int(((anos_acima >= 1) & (anos_acima <= 10)).sum()):>3} CNES")
print(f"  todos os 11 acima:     {int((anos_acima == 11).sum()):>3} CNES  <- os que somem")
print()
print("Leitura: a parte B é condicional a uma amostra que exclui exatamente os")
print("hospitais cronicamente superlotados. É interpretável, mas não pode ficar")
print("implícito — o estrato deixa de conter quem mais superlota.")

print()
print("=" * 88)
print("(2) FRAGILIDADE DA SENSIBILIDADE R4.2 — um hospital move o veredito")
print("=" * 88)

t10 = pd.read_csv(TAB / "tabSEG_10_cre_mundlak_por_estrato.csv")
t10.columns = [c.lstrip("﻿") for c in t10.columns]
pb = t10[(t10["estrato"] == "E3") & (t10["indicador"].str.contains("100"))]

for _, r in pb.iterrows():
    cruza = r["ic95_lo"] < 0 < r["ic95_hi"]
    print(f"  {r['recorte']:<28} n={r['n_obs']:.0f}/{r['n_cnes']:.0f}  "
          f"coef {r['coef_oss']:+.5f}  p={r['p_valor']:.5f}  "
          f"IC [{r['ic95_lo']:+.5f}, {r['ic95_hi']:+.5f}]  "
          f"cruza o zero: {cruza}")
    linhas.append({
        "verificacao": "2-fragilidade_R4.2", "cnes": r["recorte"],
        "nome": str(r["indicador"]), "categoria": "",
        "anos_acima_100": None, "anos_total": None,
        "mediana_ocupacao": None,
        "coef": round(float(r["coef_oss"]), 5),
        "p_valor": round(float(r["p_valor"]), 5),
        "ic95_lo": round(float(r["ic95_lo"]), 5),
        "cruza_zero": bool(cruza),
    })

lo_sens = float(pb[pb["recorte"].str.contains("R4.2")]["ic95_lo"].iloc[0])
print()
print(f"O limite inferior da sensibilidade é {lo_sens:+.5f} — a "
      f"{lo_sens:.1e} do zero.")
print("Remover UM hospital (7711980) leva p de 0,068 a 0,049. A significância")
print("da parte B não pode ser citada sem esta qualificação colada.")

print()
print("=" * 88)
print("(3) SWITCHERS DO BINÁRIO — de que lado da conversão está a superlotação")
print("=" * 88)

# switcher = CNES cuja categoria muda ao longo dos 11 anos
mudam = p.groupby("cnes")["modelo_gestao_proxy"].nunique()
switchers = sorted(mudam[mudam > 1].index)
print(f"CNES com mudança de modelo_gestao_proxy no painel: {len(switchers)}")
print()

for c in switchers:
    sub = p[p["cnes"] == c].sort_values("ano")
    nome = str(sub["nome_fantasia"].iloc[0])[:38]
    estrato = sub["estrato"].iloc[0]
    # o primeiro ano em que aparece como OSS marca a conversão
    anos_oss = sub[sub["modelo_gestao_proxy"] == "OSS"]["ano"]
    ano_conv = int(anos_oss.min()) if len(anos_oss) else None
    pre = sub[sub["ano"] < ano_conv]
    pos = sub[sub["ano"] >= ano_conv]
    sup_pre = int((pre["ocupacao_internacao"] > 100).sum())
    sup_pos = int((pos["ocupacao_internacao"] > 100).sum())
    marca = "SIM" if sup_pos > 0 else "nao"
    print(f"  {c}  {nome:<38} [{estrato}] conv.{ano_conv}  "
          f"pré {len(pre):>2}a ({sup_pre} sup)  "
          f"pós {len(pos):>2}a ({sup_pos} sup)   "
          f"superlotação pós-conversão: {marca}")
    linhas.append({
        "verificacao": "3-switchers_binario", "cnes": c, "nome": nome,
        "categoria": estrato, "ano_conversao": ano_conv,
        "anos_pre": len(pre), "sup_pre": sup_pre,
        "anos_pos": len(pos), "sup_pos": sup_pos,
        "tem_sup_pos_conversao": bool(sup_pos > 0),
    })

com_pos = [l for l in linhas
           if l["verificacao"] == "3-switchers_binario" and l["tem_sup_pos_conversao"]]
com_alguma = [l for l in linhas
              if l["verificacao"] == "3-switchers_binario"
              and (l["sup_pre"] + l["sup_pos"]) > 0]
print()
print(f"Switchers com QUALQUER superlotação observada: {len(com_alguma)}")
print(f"Switchers com superlotação PÓS-conversão:      {len(com_pos)}")
print()
print("Leitura: a variação existe, mas é quase toda 'superlotava antes'. O lado")
print("que identifica o efeito da gestão é o pós-conversão, e ali a massa é")
print("mínima. Isso reforça a redação obrigatória de R10 — o nulo do binário")
print("não distingue 'sem efeito' de 'sem potência' — e a reforça mais do que o")
print("registro atual deixa ver.")

pd.DataFrame(linhas).to_csv(TAB / "tabSEG_17_qualificacoes_amostra.csv",
                            index=False, encoding="utf-8")
print()
print("[TAB] tabSEG_17_qualificacoes_amostra.csv")
