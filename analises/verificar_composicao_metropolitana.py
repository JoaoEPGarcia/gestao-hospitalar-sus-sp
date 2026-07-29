# verificar_composicao_metropolitana.py
# BLOCO 3 do fechamento de 29/07/2026 — ponto de verificação, antes de decidir.
#
# Confere a classificação geográfica implementada em `selecao_entrevistas.py`
# contra a composição oficial das duas regiões metropolitanas, e mede quantos
# hospitais do painel caem em cada estrato sob os dois esquemas possíveis.
#
# FONTES OFICIAIS conferidas em 29/07/2026:
#   RMSP  — Lei Complementar estadual nº 1.139, de 16/06/2011, art. 4º:
#           39 municípios em cinco sub-regiões. Guarulhos é sub-região LESTE,
#           Cotia é sub-região SUDOESTE, e Santos NÃO consta.
#   RMBS  — Lei Complementar estadual nº 815, de 30/07/1996: nove municípios,
#           Bertioga, Cubatão, Guarujá, Itanhaém, Mongaguá, Peruíbe, Praia
#           Grande, SANTOS e São Vicente.
#
# Este script NÃO regenera a seleção e NÃO altera nenhum estrato. Ele existe
# para que a decisão sobre o esquema de agregação seja tomada com o número na
# mesa, e não com a estimativa de memória.

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ.parent))

from selecao_entrevistas import (  # noqa: E402
    COD_IBGE_BAIXADA_SANTISTA, COD_IBGE_CAPITAL, COD_IBGE_RMSP,
)

PISO_ESTRATO = 15  # piso de hospitais por estrato de amostragem, pré-fixado

# ── as listas oficiais, para conferência nome a nome ─────────────────
RMSP_OFICIAL = {
    "Norte": ["Caieiras", "Cajamar", "Francisco Morato", "Franco da Rocha",
              "Mairiporã"],
    "Leste": ["Arujá", "Biritiba-Mirim", "Ferraz de Vasconcelos", "Guararema",
              "Guarulhos", "Itaquaquecetuba", "Mogi das Cruzes", "Poá",
              "Salesópolis", "Santa Isabel", "Suzano"],
    "Sudeste": ["Diadema", "Mauá", "Ribeirão Pires", "Rio Grande da Serra",
                "Santo André", "São Bernardo do Campo", "São Caetano do Sul"],
    "Sudoeste": ["Cotia", "Embu", "Embu-Guaçu", "Itapecerica da Serra",
                 "Juquitiba", "São Lourenço da Serra", "Taboão da Serra",
                 "Vargem Grande Paulista"],
    "Oeste": ["Barueri", "Carapicuíba", "Itapevi", "Jandira", "Osasco",
              "Pirapora do Bom Jesus", "Santana de Parnaíba"],
}
RMBS_OFICIAL = ["Bertioga", "Cubatão", "Guarujá", "Itanhaém", "Mongaguá",
                "Peruíbe", "Praia Grande", "Santos", "São Vicente"]

print("=" * 78)
print("1. COMPOSIÇÃO OFICIAL contra o que está implementado")
print("=" * 78)

n_of = sum(len(v) for v in RMSP_OFICIAL.values())
print(f"RMSP, LC 1.139/2011: {n_of} municípios além da capital "
      f"(+ São Paulo = {n_of + 1})")
for sub, muns in RMSP_OFICIAL.items():
    print(f"   {sub:<9} {len(muns):>2}: {', '.join(muns)}")
print(f"\nimplementado em COD_IBGE_RMSP: {len(COD_IBGE_RMSP)} códigos")
print(f"  confere em contagem: {len(COD_IBGE_RMSP) == n_of}")

print(f"\nRMBS, LC 815/1996: {len(RMBS_OFICIAL)} municípios")
print(f"   {', '.join(RMBS_OFICIAL)}")
print(f"implementado em COD_IBGE_BAIXADA_SANTISTA: "
      f"{len(COD_IBGE_BAIXADA_SANTISTA)} códigos")
print(f"  confere em contagem: "
      f"{len(COD_IBGE_BAIXADA_SANTISTA) == len(RMBS_OFICIAL)}")

print()
print("Os três casos que motivaram a revisão:")
CASOS = {"Guarulhos": 351880, "Cotia": 351300, "Santos": 354850}
for nome, cod in CASOS.items():
    onde = ("RMSP" if cod in COD_IBGE_RMSP else
            "Baixada Santista" if cod in COD_IBGE_BAIXADA_SANTISTA else
            "capital" if cod == COD_IBGE_CAPITAL else "INTERIOR")
    print(f"   {nome:<11} cod {cod} -> {onde}")

print()
print("=" * 78)
print("2. QUANTOS HOSPITAIS DO PAINEL CAEM EM CADA ESTRATO")
print("=" * 78)

p = pd.read_csv(RAIZ / "painel_definitivo.csv")
h = p.groupby("cnes").agg(
    cod_ibge=("cod_ibge", lambda s: s.dropna().iloc[-1]),
    municipio=("municipio", lambda s: s.dropna().iloc[-1] if s.notna().any()
               else ""),
).reset_index()
print(f"hospitais únicos no painel: {len(h)}")


def quatro(cod):
    if pd.isna(cod):
        return "Interior"
    cod = int(cod)
    if cod == COD_IBGE_CAPITAL:
        return "Capital"
    if cod in COD_IBGE_RMSP:
        return "RMSP"
    if cod in COD_IBGE_BAIXADA_SANTISTA:
        return "Baixada Santista"
    return "Interior"


h["quatro"] = h["cod_ibge"].map(quatro)
h["tres"] = h["quatro"].replace({"RMSP": "Outras regiões metropolitanas",
                                 "Baixada Santista":
                                     "Outras regiões metropolitanas"})

print()
print("ESQUEMA IMPLEMENTADO — três estratos (o que está em master):")
for k, v in h["tres"].value_counts().items():
    marca = "" if v >= PISO_ESTRATO else f"  << ABAIXO DO PISO DE {PISO_ESTRATO}"
    print(f"   {k:<32} {v:>4}{marca}")

print()
print("ESQUEMA PEDIDO — quatro estratos, separando a Baixada:")
for k, v in h["quatro"].value_counts().items():
    marca = "" if v >= PISO_ESTRATO else f"  << ABAIXO DO PISO DE {PISO_ESTRATO}"
    print(f"   {k:<32} {v:>4}{marca}")

nb = int((h["quatro"] == "Baixada Santista").sum())
print()
print(f"A Baixada Santista sozinha tem {nb} hospitais, contra um piso "
      f"pré-fixado de {PISO_ESTRATO}.")
print(f"Faltam {PISO_ESTRATO - nb} para que ela sustente estrato próprio.")

print()
print("Hospitais da Baixada Santista, por município:")
b = h[h["quatro"] == "Baixada Santista"]
for m, n in b["municipio"].value_counts().items():
    print(f"   {m:<24} {n}")
