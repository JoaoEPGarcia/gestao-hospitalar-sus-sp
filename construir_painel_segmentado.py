# -*- coding: utf-8 -*-
"""
ETAPA 2 — Construção do painel segmentado por estrato estrutural.

Derivado de construir_painel_definitivo.py, que NÃO é editado. Este script
não reconstrói o painel: parte do painel definitivo já corrigido (ETAPA 1)
e apenas acrescenta a classificação em estratos.

Por que estratificar
--------------------
Comparar um hospital sem UTI SUS com um terciário de alta complexidade não
é comparar gestões: é comparar tecnologias de produção distintas. A média
agregada por categoria de gestão mistura as duas coisas, e o que sai dali
não separa efeito de gestão de composição da carteira de hospitais.

Definição dos estratos
----------------------
Classificação POR CNES, FIXA no período inteiro (não varia por ano), sobre
a MEDIANA das onze observações. A mediana de série de 11 pontos é sempre um
valor observado — não há empate em .5 a desempatar.

    E1  sem_uti_sus         mediana uti_sus == 0
    E2  uti_baixa_complex   mediana uti_sus > 0  e  mediana faixa_barcelona <= 3
    E3  uti_alta_complex    mediana uti_sus > 0  e  mediana faixa_barcelona >= 4

CNES que não caia em exatamente um estrato recebe rótulo REVISAR e o script
PARA. Não há regra de desempate improvisada.

A classificação é fixa, mas alguns CNES oscilam entre ter e não ter UTI SUS
ao longo da série. A mediana decide a alocação; a flag `estrato_instavel`
preserva a auditoria de quem oscilou.

Saídas
------
  analises/tabelas/tabSEG_01_funil_estratos.csv
  analises/tabelas/tabSEG_02_switchers_estrato.csv
  analises/tabelas/tabSEG_03_instaveis.csv
  analises/painel_segmentado.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent
PAINEL_IN = RAIZ / "analises" / "painel_definitivo_corrigido.csv"
PAINEL_OUT = RAIZ / "analises" / "painel_segmentado.csv"
PASTA_TAB = RAIZ / "analises" / "tabelas"

CATEGORIAS = ["Direta", "OSS", "Público Municipal", "Filantrópico", "Privado"]
ESTRATOS = ["E1", "E2", "E3"]
ROTULOS = {"E1": "sem_uti_sus", "E2": "uti_baixa_complex", "E3": "uti_alta_complex"}

# Os cinco switchers Direta->OSS, com o ano da virada (mesma lista de
# CONVERSOES em analise_exploratoria.py). São eles que sustentam a
# identificação within-hospital do efeito OSS; saber em que estrato cada um
# caiu determina onde essa identificação continua existindo.
SWITCHERS = {
    2081695: ("Sorocaba", 2019),
    2078287: ("Pérola", 2023),
    2082225: ("Taipas", 2025),
    2091755: ("Vila Penteado", 2025),
    2750511: ("Odilo Antunes", 2025),
}
# Referência da versão de 314 CNES: ordem de grandeza esperada, não valor a
# reproduzir. Divergência aqui significa que a base mudou sob os pés desta
# tarefa, e isso se reporta — não se reconcilia sozinho.
SWITCHERS_ESPERADO = {2081695: "E3", 2078287: "E3", 2082225: "E3",
                      2091755: "E3", 2750511: "E2"}


def _parar(motivo: str) -> None:
    """Aborta sem escrever nada."""
    print("\n" + "!" * 78)
    print("PARAR E REPORTAR")
    print(motivo)
    print("Nenhum arquivo foi escrito.")
    print("!" * 78)
    sys.exit(1)


# ---------------------------------------------------------------------------
# LEITURA
# ---------------------------------------------------------------------------
print("=" * 78)
print("ETAPA 2 — painel segmentado por estrato estrutural")
print("=" * 78)

if not PAINEL_IN.exists():
    _parar(f"{PAINEL_IN.name} não existe. Rodar antes a ETAPA 1 "
           "(corrigir_dominio_ocupacao_uti.py).")

df = pd.read_csv(PAINEL_IN)
N_IN, COLS_IN = len(df), list(df.columns)

if "ocupacao_uti_valida" not in df.columns or "tem_uti_sus" not in df.columns:
    _parar("O painel de entrada não traz ocupacao_uti_valida/tem_uti_sus. "
           "A ETAPA 1 não foi aplicada a este arquivo.")

print(f"\nlido: {PAINEL_IN.relative_to(RAIZ)}")
print(f"  {len(df):,} observações | {df['cnes'].nunique():,} CNES | "
      f"{df['ano'].min()}–{df['ano'].max()}")

anos_por_cnes = df.groupby("cnes")["ano"].nunique()
if anos_por_cnes.nunique() != 1:
    _parar("Painel desbalanceado: os CNES não têm todos o mesmo número de "
           "anos. A mediana de 11 pontos pressupõe painel balanceado.")
print(f"  painel balanceado: {anos_por_cnes.iloc[0]} anos por CNES")


# ---------------------------------------------------------------------------
# CLASSIFICAÇÃO POR CNES
# ---------------------------------------------------------------------------
print("\n" + "-" * 78)
print("CLASSIFICAÇÃO — medianas por CNES ao longo dos 11 anos")
print("-" * 78)

por_cnes = df.groupby("cnes").agg(
    uti_sus_mediana=("uti_sus", "median"),
    faixa_mediana=("faixa_barcelona", "median"),
    uti_sus_min=("uti_sus", "min"),
    uti_sus_max=("uti_sus", "max"),
    anos_com_uti=("tem_uti_sus", "sum"),
    faixa_n_valores=("faixa_barcelona", "nunique"),
    nome_fantasia=("nome_fantasia", "last"),
    municipio=("municipio", "last"),
    modelo_gestao_proxy=("modelo_gestao_proxy", "last"),
)

# faixa_barcelona é fixa por CNES na construção do painel (pontuação
# Barcelona, atributo estrutural). Se variasse, a mediana estaria escondendo
# uma mudança de complexidade e a premissa da estratificação fixa cairia.
n_faixa_varia = int((por_cnes["faixa_n_valores"] > 1).sum())
print(f"CNES com faixa_barcelona variando no período: {n_faixa_varia}")
if n_faixa_varia:
    print("  !! a faixa não é fixa por CNES; a mediana está agregando variação")

if por_cnes[["uti_sus_mediana", "faixa_mediana"]].isna().any().any():
    _parar("Há CNES com mediana de uti_sus ou faixa_barcelona indefinida.")

# As três regras, avaliadas em paralelo para poder exigir exclusividade
# mútua em vez de assumi-la por ordem de if/elif.
regras = pd.DataFrame({
    "E1": por_cnes["uti_sus_mediana"] == 0,
    "E2": (por_cnes["uti_sus_mediana"] > 0) & (por_cnes["faixa_mediana"] <= 3),
    "E3": (por_cnes["uti_sus_mediana"] > 0) & (por_cnes["faixa_mediana"] >= 4),
})
n_regras = regras.sum(axis=1)
por_cnes["estrato"] = regras.idxmax(axis=1).where(n_regras == 1, "REVISAR")

n_revisar = int((por_cnes["estrato"] == "REVISAR").sum())
if n_revisar:
    print("\nCNES que não caem em exatamente um estrato:")
    print(por_cnes.loc[por_cnes["estrato"] == "REVISAR",
                       ["uti_sus_mediana", "faixa_mediana", "nome_fantasia"]].to_string())
    _parar(f"{n_revisar} CNES com rótulo REVISAR. Não há regra de desempate "
           "prevista, e improvisar uma aqui seria decisão metodológica "
           "tomada no lugar da equipe.")

por_cnes["estrato_rotulo"] = por_cnes["estrato"].map(ROTULOS)

# Oscilação entre ter e não ter UTI SUS ao longo da série.
n_anos = int(anos_por_cnes.iloc[0])
por_cnes["estrato_instavel"] = por_cnes["anos_com_uti"].between(1, n_anos - 1)

print("\ndistribuição dos estratos:")
for e in ESTRATOS:
    n = int((por_cnes["estrato"] == e).sum())
    print(f"  {e} {ROTULOS[e]:<20} {n:>4} CNES")
print(f"  {'TOTAL':<24} {len(por_cnes):>4} CNES")

n_inst = int(por_cnes["estrato_instavel"].sum())
print(f"\nCNES com UTI SUS oscilante (estrato_instavel) ... {n_inst}")
print(f"CNES sem UTI SUS em nenhum ano .................. "
      f"{int((por_cnes['anos_com_uti'] == 0).sum())}")
print(f"CNES com UTI SUS em todos os anos ............... "
      f"{int((por_cnes['anos_com_uti'] == n_anos).sum())}")


# ---------------------------------------------------------------------------
# VERIFICAÇÃO — alocação dos switchers
# ---------------------------------------------------------------------------
print("\n" + "-" * 78)
print("VERIFICAÇÃO — alocação dos cinco switchers Direta->OSS")
print("-" * 78)

faltantes = [c for c in SWITCHERS if c not in por_cnes.index]
if faltantes:
    _parar(f"Switchers ausentes do painel: {faltantes}.")

linhas_sw = []
for cnes, (nome, ano_virada) in SWITCHERS.items():
    lin = por_cnes.loc[cnes]
    linhas_sw.append({
        "cnes": cnes,
        "nome_curto": nome,
        "nome_fantasia": lin["nome_fantasia"],
        "municipio": lin["municipio"],
        "ano_conversao": ano_virada,
        "modelo_gestao_proxy": lin["modelo_gestao_proxy"],
        "uti_sus_mediana": lin["uti_sus_mediana"],
        "uti_sus_min": lin["uti_sus_min"],
        "uti_sus_max": lin["uti_sus_max"],
        "faixa_mediana": lin["faixa_mediana"],
        "estrato": lin["estrato"],
        "estrato_rotulo": lin["estrato_rotulo"],
        "estrato_esperado": SWITCHERS_ESPERADO[cnes],
        "confere": lin["estrato"] == SWITCHERS_ESPERADO[cnes],
        "estrato_instavel": lin["estrato_instavel"],
    })
tab02 = pd.DataFrame(linhas_sw)
print(tab02[["cnes", "nome_curto", "ano_conversao", "uti_sus_mediana",
             "faixa_mediana", "estrato", "estrato_esperado", "confere"]]
      .to_string(index=False))

if not tab02["confere"].all():
    divergem = tab02.loc[~tab02["confere"], ["cnes", "nome_curto", "estrato",
                                             "estrato_esperado"]]
    _parar("A alocação dos switchers divergiu da referência:\n"
           f"{divergem.to_string(index=False)}\n"
           "É sinal de que a base mudou. A identificação within do efeito OSS "
           "depende de onde estes hospitais caem.")
print("\n>>> alocação confere com a referência (4 em E3, Odilo em E2).")


# ---------------------------------------------------------------------------
# MERGE NO PAINEL
# ---------------------------------------------------------------------------
novas = ["estrato", "estrato_rotulo", "uti_sus_mediana", "faixa_mediana",
         "estrato_instavel"]
df = df.merge(por_cnes[novas], left_on="cnes", right_index=True, how="left")

if len(df) != N_IN:
    _parar(f"O merge alterou o número de observações: {N_IN:,} -> {len(df):,}.")
if df["estrato"].isna().any():
    _parar("Há observações sem estrato após o merge.")


# ---------------------------------------------------------------------------
# tabSEG_01 — funil dos estratos
# ---------------------------------------------------------------------------
cats = [c for c in CATEGORIAS if (df["modelo_gestao_proxy"] == c).any()]
linhas_funil = []
for e in ESTRATOS + ["TOTAL"]:
    bloco_e = df if e == "TOTAL" else df[df["estrato"] == e]
    for c in cats + ["TOTAL"]:
        bloco = bloco_e if c == "TOTAL" else bloco_e[bloco_e["modelo_gestao_proxy"] == c]
        linhas_funil.append({
            "estrato": e,
            "estrato_rotulo": ROTULOS.get(e, "todos"),
            "modelo_gestao_proxy": c,
            "n_cnes": bloco["cnes"].nunique(),
            "n_hospital_ano": len(bloco),
        })
tab01 = pd.DataFrame(linhas_funil)

PASTA_TAB.mkdir(parents=True, exist_ok=True)
tab01.to_csv(PASTA_TAB / "tabSEG_01_funil_estratos.csv",
             index=False, encoding="utf-8-sig")

print("\n" + "=" * 78)
print("tabSEG_01_funil_estratos — n de CNES")
print("=" * 78)
piv_cnes = tab01.pivot(index="estrato", columns="modelo_gestao_proxy",
                       values="n_cnes").reindex(ESTRATOS + ["TOTAL"])[cats + ["TOTAL"]]
print(piv_cnes.to_string())
print("\ntabSEG_01_funil_estratos — n de hospital-ano")
piv_obs = tab01.pivot(index="estrato", columns="modelo_gestao_proxy",
                      values="n_hospital_ano").reindex(ESTRATOS + ["TOTAL"])[cats + ["TOTAL"]]
print(piv_obs.to_string())

# Onde a comparação OSS vs. Direta tem lastro suficiente para ser lida.
print("\ncélulas OSS/Direta por estrato (piso de 10 CNES):")
for e in ESTRATOS:
    n_oss = int(piv_cnes.loc[e, "OSS"]) if "OSS" in piv_cnes.columns else 0
    n_dir = int(piv_cnes.loc[e, "Direta"]) if "Direta" in piv_cnes.columns else 0
    marca = "viável" if min(n_oss, n_dir) >= 10 else "abaixo do piso"
    print(f"  {e}: OSS {n_oss:>3} | Direta {n_dir:>3}  -> {marca}")

# E1 é o estrato "sem UTI SUS" pela MEDIANA, não pela série inteira: os CNES
# instáveis alocados nele têm anos isolados com leito habilitado. Quantificar
# esse resíduo importa para a ETAPA 4, onde o modelo de ocupação de UTI é
# declarado não-aplicável em E1 — a declaração precisa ser decisão informada,
# não suposição de que o estrato não tem nenhuma observação válida.
print("\nobservações com UTI SUS dentro de cada estrato:")
for e in ESTRATOS:
    bloco = df[df["estrato"] == e]
    n_val = int(bloco["tem_uti_sus"].sum())
    n_cnes_val = bloco.loc[bloco["tem_uti_sus"], "cnes"].nunique()
    print(f"  {e}: {n_val:>4} de {len(bloco):>4} hospital-ano "
          f"({100 * n_val / len(bloco):5.1f}%), em {n_cnes_val:>3} CNES")


# ---------------------------------------------------------------------------
# tabSEG_02 / tabSEG_03
# ---------------------------------------------------------------------------
tab02.to_csv(PASTA_TAB / "tabSEG_02_switchers_estrato.csv",
             index=False, encoding="utf-8-sig")

tab03 = (por_cnes.loc[por_cnes["estrato_instavel"],
                      ["nome_fantasia", "municipio", "modelo_gestao_proxy",
                       "anos_com_uti", "uti_sus_min", "uti_sus_max",
                       "uti_sus_mediana", "faixa_mediana", "estrato",
                       "estrato_rotulo"]]
         .reset_index()
         .sort_values(["estrato", "anos_com_uti", "cnes"]))
tab03.insert(tab03.columns.get_loc("anos_com_uti") + 1, "anos_sem_uti",
             n_anos - tab03["anos_com_uti"])
tab03.to_csv(PASTA_TAB / "tabSEG_03_instaveis.csv",
             index=False, encoding="utf-8-sig")

print("\n" + "=" * 78)
print(f"tabSEG_03_instaveis — {len(tab03)} CNES oscilam entre ter e não ter UTI SUS")
print("=" * 78)
if len(tab03):
    print(tab03[["cnes", "nome_fantasia", "modelo_gestao_proxy", "anos_com_uti",
                 "uti_sus_min", "uti_sus_max", "uti_sus_mediana", "estrato"]]
          .to_string(index=False))
    print("\ninstáveis por estrato:")
    print(tab03.groupby("estrato").size().to_string())


# ---------------------------------------------------------------------------
# VERIFICAÇÕES FINAIS E GRAVAÇÃO
# ---------------------------------------------------------------------------
print("\n" + "-" * 78)
print("VERIFICAÇÕES OBRIGATÓRIAS")
print("-" * 78)

soma_estratos = sum(int((por_cnes["estrato"] == e).sum()) for e in ESTRATOS)
if soma_estratos != df["cnes"].nunique():
    _parar(f"Soma dos estratos ({soma_estratos}) != total de CNES "
           f"({df['cnes'].nunique()}).")
print(f"  soma dos estratos == total de CNES ....... {soma_estratos} OK")

if len(df) != N_IN:
    _parar(f"Observações perdidas: {N_IN:,} -> {len(df):,}.")
print(f"  nenhuma observação perdida ............... {len(df):,} OK")

if list(df.columns)[:len(COLS_IN)] != COLS_IN:
    _parar("As colunas do painel de entrada foram alteradas ou reordenadas.")
print(f"  colunas de entrada preservadas ........... {len(COLS_IN)} OK")

df.to_csv(PAINEL_OUT, index=False, encoding="utf-8-sig")

print("\n" + "=" * 78)
print("ESCRITO")
print("=" * 78)
for nome in ("tabSEG_01_funil_estratos.csv", "tabSEG_02_switchers_estrato.csv",
             "tabSEG_03_instaveis.csv"):
    print(f"  analises/tabelas/{nome}")
print(f"  {PAINEL_OUT.relative_to(RAIZ)}")
print(f"\ncolunas novas: {', '.join(novas)} "
      f"({len(COLS_IN)} -> {df.shape[1]} colunas)")
