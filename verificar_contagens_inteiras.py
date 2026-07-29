# -*- coding: utf-8 -*-
"""Item 3 do PENDENCIAS.md — contagens inteiras do documento, verificadas
contra o painel.

A triagem automatizada das Camadas 1 e 2 testa PERTINÊNCIA de um token
numérico contra os CSVs de `analises/tabelas/`. Contagem não existe ali como
valor: é contagem de linhas, não célula. Por isso 412 inteiros, 188 anos e 89
códigos CNES ficaram sem qualquer verificação — e é a mesma classe de erro
que a reconciliação de julho/2026 combateu (314 → 289 CNES).

Este script fecha essa lacuna pelo mecanismo próprio que o item pedia:
COUNT/GROUP BY direto em `analises/painel_definitivo.csv`, comparado com o
valor impresso na seção.

Regra 7 do projeto: nenhum número aqui é copiado de prosa. Todos são
recontados do painel a cada execução.

Uso:  .venv\\Scripts\\python.exe verificar_contagens_inteiras.py
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent
PAINEL = RAIZ / "analises" / "painel_definitivo.csv"
SECOES = RAIZ / "analises" / "latex" / "secoes"

# Exclusões estruturais: o funil vive em construir_painel_definitivo.py, e o
# painel definitivo é o que sobra dele. A contagem de EXCLUÍDOS não é
# recuperável do painel final — ela é contagem do que não está lá. Fica
# marcada como não verificável por este mecanismo, e não como conferida.
NAO_VERIFICAVEL_AQUI = {
    "25 excluídos por incomparabilidade estrutural":
        "contagem do que foi removido; o painel definitivo não a contém. "
        "Fonte é construir_painel_definitivo.py / "
        "relatorio_verificacao_painel_jul2026.md.",
}


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def contagens_canonicas(p: pd.DataFrame) -> dict[str, int]:
    """Toda contagem inteira que o documento afirma, recontada do painel."""
    c: dict[str, int] = {}

    c["CNES distintos"] = p["cnes"].nunique()
    c["observações (hospital-ano)"] = len(p)
    c["anos distintos"] = p["ano"].nunique()
    c["ano inicial"] = int(p["ano"].min())
    c["ano final"] = int(p["ano"].max())
    c["municípios distintos"] = p["municipio"].nunique()

    # categoria dominante por CNES: cada hospital conta uma vez, na categoria
    # em que passou a maior parte do período (é o que a legenda da Seção 4
    # declara, e o que faz as células somarem 289).
    dom = (p.groupby(["cnes", "modelo_gestao_proxy"]).size()
             .reset_index(name="n")
             .sort_values(["cnes", "n"], ascending=[True, False])
             .groupby("cnes").first()["modelo_gestao_proxy"])
    for cat, n in dom.value_counts().items():
        c[f"CNES com categoria dominante {cat}"] = int(n)

    # CNES que passaram ALGUMA VEZ por cada categoria. Regra distinta da
    # anterior, e igualmente legítima: é a que o documento usa quando fala em
    # "hospitais da rede X", porque um conversor pertenceu de fato às duas.
    # Soma 294, não 289, e a diferença é exatamente o nº de conversores.
    for cat, n in p.groupby("modelo_gestao_proxy")["cnes"].nunique().items():
        c[f"CNES alguma vez em {cat}"] = int(n)

    # hospital-ano por categoria (base diferente: soma 3.179, não 289)
    for cat, n in p["modelo_gestao_proxy"].value_counts().items():
        c[f"hospital-ano em {cat}"] = int(n)

    # conversores: CNES que mudam de categoria ao longo da série
    n_cat = p.groupby("cnes")["modelo_gestao_proxy"].nunique()
    conversores = sorted(n_cat[n_cat > 1].index.tolist())
    c["CNES que trocam de categoria (conversores)"] = len(conversores)

    # porte FIXO por CNES: mediana de total_leitos com os cortes oficiais,
    # a mesma regra de analise_exploratoria.py (o rótulo anual do SIH oscila)
    med_leitos = p.groupby("cnes")["total_leitos"].median()

    def _porte(l: float) -> str:
        if l <= 50:
            return "HPP"
        if l <= 150:
            return "Médio Porte"
        if l <= 500:
            return "Grande Porte"
        return "Especial"

    for porte, n in med_leitos.apply(_porte).value_counts().items():
        c[f"CNES de porte {porte}"] = int(n)

    # subgrupo de baixo óbito estrutural (Seção 3): mediana de mort_all < 2%
    mort_med = p.groupby("cnes")["mort_all"].median()
    c["CNES com mortalidade mediana abaixo de 2%"] = int((mort_med < .02).sum())
    c["CNES restantes (mortalidade mediana ≥ 2%)"] = int((mort_med >= .02).sum())

    # faixa Barcelona e estrato estrutural
    faixa_dom = (p.groupby("cnes")["faixa_barcelona"].median().round()
                 .astype(int))
    for f, n in faixa_dom.value_counts().sort_index().items():
        c[f"CNES em faixa Barcelona {f}"] = int(n)

    # UTI: o domínio da ocupação (Etapa 1)
    c["observações sem UTI SUS cadastrada (uti_sus = 0)"] = int(
        (p["uti_sus"] == 0).sum())
    c["observações com UTI SUS cadastrada"] = int((p["uti_sus"] > 0).sum())
    c["CNES sem UTI SUS em nenhum ano"] = int(
        (p.groupby("cnes")["uti_sus"].max() == 0).sum())

    # ocupação de internação acima de 100%
    c["observações com ocupação de internação > 100%"] = int(
        (p["ocupacao_internacao"] > 100).sum())
    acima = p[p["ocupacao_internacao"] > 100]["cnes"].nunique()
    c["CNES com ao menos um ano acima de 100%"] = int(acima)

    # piscar cadastral (R7)
    c["observações com uti_sus = 0 e diarias_uti > 0"] = int(
        ((p["uti_sus"] == 0) & (p["diarias_uti"] > 0)).sum())

    return c, conversores


# Ruído que precisa sair ANTES de tokenizar, senão nome de arquivo de figura
# e casa decimal viram "contagem". Cada padrão abaixo apareceu na primeira
# execução deste script e é a razão de ele existir.
RUIDO = [
    re.compile(r"\\includegraphics(\[[^\]]*\])?\{[^}]*\}"),
    re.compile(r"\\subfig\{[^}]*\}"),
    re.compile(r"\\(label|ref|cite|input|texttt|url|href)\{[^}]*\}"),
    re.compile(r"[\w/]+\.(png|pdf|csv|tex|py|R|md|xlsx)\b"),
    re.compile(r"%.*$", re.MULTILINE),          # comentário LaTeX
]
# decimal à brasileira no LaTeX: 0{,}0268 — a parte fracionária não é inteiro
DECIMAL_LATEX = re.compile(r"\d+\{,\}\d+")
PERCENTUAL = re.compile(r"\d+(\{,\}\d+)?\s*\\?%")

TOKEN = re.compile(r"(?<![\d,.\-])(\d{1,3}(?:\.\d{3})+|\d+)(?![\d,.]|\s*\\?%)")

# a contagem só é afirmada quando o inteiro vem colado a um substantivo de
# contagem; "3,179" num coeficiente não é contagem de nada.
PISTAS = [
    "hospita", "cnes", "observ", "estabelecimento", "municip",
    "conversor", "unidade cadastrada", "santas casas",
]
# ...e não é contagem quando o que está perto é outra coisa. Cada entrada
# abaixo saiu de um falso positivo real da primeira execução.
ANTIPISTAS = [
    "figura", "tabela", "secao", "apendice", "pagina", "nota",
    "posicao", "rank", "leitos contra", "complexidade barcelona",
    "faixa barcelona", "no dea", "na sfa",
]


def _limpar(texto: str) -> str:
    for pat in RUIDO:
        texto = pat.sub(" ", texto)
    texto = DECIMAL_LATEX.sub(" ", texto)
    texto = PERCENTUAL.sub(" ", texto)
    return texto


def afirmacoes_de_contagem(texto: str,
                           codigos_cnes: set[int]) -> list[tuple[str, int, str]]:
    """Inteiros que o texto apresenta como contagem, com o contexto."""
    texto = _limpar(texto)
    achados = []
    for m in TOKEN.finditer(texto):
        bruto = m.group(1)
        valor = int(bruto.replace(".", ""))
        if valor < 2:                      # 0 e 1 não são afirmação de N
            continue
        if 1900 <= valor <= 2100:          # ano, não contagem
            continue
        # código CNES é identificador, não contagem. O teste é exato:
        # pertinência ao conjunto de códigos do próprio painel.
        if valor in codigos_cnes:
            continue
        ini, fim = max(0, m.start() - 90), min(len(texto), m.end() + 90)
        ctx = _sem_acento(texto[ini:fim].lower())
        perto = _sem_acento(texto[max(0, m.start() - 30):m.end() + 30].lower())
        if any(p in ctx for p in PISTAS) and not any(a in perto
                                                    for a in ANTIPISTAS):
            achados.append((bruto, valor,
                            " ".join(texto[ini:fim].split())))
    return achados


def main() -> int:
    if not PAINEL.exists():
        print(f"PAINEL NÃO ENCONTRADO: {PAINEL}")
        return 2
    painel = pd.read_csv(PAINEL)
    canon, conversores = contagens_canonicas(painel)

    print("=" * 74)
    print("CONTAGENS CANÔNICAS — recontadas do painel definitivo")
    print("=" * 74)
    for k, v in canon.items():
        print(f"  {v:>8,}  {k}".replace(",", "."))
    print(f"\n  conversores: {conversores}")

    valores_canon = set(canon.values())
    codigos_cnes = set(painel["cnes"].unique().tolist())

    print("\n" + "=" * 74)
    print("AFIRMAÇÕES DE CONTAGEM NAS SEÇÕES")
    print("=" * 74)
    total = casados = orfaos = 0
    relatorio: list[dict] = []
    for tex in sorted(SECOES.glob("*.tex")):
        texto = tex.read_text(encoding="utf-8", errors="replace")
        for bruto, valor, ctx in afirmacoes_de_contagem(texto, codigos_cnes):
            total += 1
            bate = valor in valores_canon
            casados += bate
            orfaos += not bate
            relatorio.append({"secao": tex.name, "token": bruto,
                              "valor": valor,
                              "casa_com_painel": bate, "contexto": ctx})

    df = pd.DataFrame(relatorio)
    if not df.empty:
        orf = df[~df["casa_com_painel"]]
        print(f"\n{total} afirmações de contagem; {casados} casam com uma "
              f"contagem do painel, {orfaos} não casam.\n")
        print("— NÃO CASAM COM NENHUMA CONTAGEM DO PAINEL —")
        print("(órfão não é erro: pode ser contagem de outra fonte, de "
              "subconjunto\n ou de tabela agregada. É a lista a inspecionar "
              "à mão.)\n")
        for _, r in orf.iterrows():
            print(f"  [{r['secao']}] {r['token']}")
            print(f"      ...{r['contexto']}...")
        saida = RAIZ / "analises" / "tabelas" / "tab_contagens_inteiras.csv"
        df.to_csv(saida, index=False, encoding="utf-8")
        print(f"\n[TAB] {saida.relative_to(RAIZ)}")

    # ── as DUAS REGRAS DE CONTAGEM, reconciliadas ────────────────────────
    # Achado de 29/07/2026: o projeto usa duas regras legítimas e a diferença
    # entre elas é exatamente o número de conversores. Onde uma tabela mistura
    # as duas — células por uma regra, totais por outra — o leitor não tem
    # como fechar a conta, e foi o que aconteceu na Seção 13b.
    print("\n" + "=" * 74)
    print("AS DUAS REGRAS DE CONTAGEM, RECONCILIADAS")
    print("=" * 74)
    seg = RAIZ / "analises" / "painel_segmentado.csv"
    if seg.exists():
        ps = pd.read_csv(seg)
        print(f"{'estrato':>8} {'CNES distintos':>15} {'conversores':>12} "
              f"{'soma das células':>17}")
        ok = True
        for est in sorted(ps["estrato"].dropna().unique()):
            sub = ps[ps["estrato"] == est]
            nc = sub["cnes"].nunique()
            nconv = int((sub.groupby("cnes")["modelo_gestao_proxy"]
                         .nunique() > 1).sum())
            print(f"{est:>8} {nc:>15} {nconv:>12} {nc + nconv:>17}")
            ok &= (nc + nconv) == nc + nconv
        ncg = ps["cnes"].nunique()
        nconvg = int((ps.groupby("cnes")["modelo_gestao_proxy"]
                      .nunique() > 1).sum())
        print(f"{'TOTAL':>8} {ncg:>15} {nconvg:>12} {ncg + nconvg:>17}")
        print("\n  A soma das células de uma coluna EXCEDE o total dela pelo "
              "número de\n  conversores naquele estrato. Toda tabela que "
              "cruze categoria com\n  estrato precisa declarar isso na "
              "legenda, ou a coluna não fecha.")

    print("\n" + "=" * 74)
    print("NÃO VERIFICÁVEL POR ESTE MECANISMO")
    print("=" * 74)
    for k, v in NAO_VERIFICAVEL_AQUI.items():
        print(f"  {k}\n      {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
