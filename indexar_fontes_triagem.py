# -*- coding: utf-8 -*-
"""Item 1 e 3 do PENDENCIAS.md — o índice de fontes da triagem de consistência.

## Por que este arquivo existe

A triagem das Camadas 1 e 2 (26/07/2026) rodou **em sessão** e nunca foi
versionada: só os resultados ficaram no `PENDENCIAS.md`. Isso é a mesma
classe de problema que a §13 descreve para os documentos de controle — um
mecanismo cujo comportamento ninguém consegue reproduzir não é mecanismo, é
lembrança. Este script materializa a parte que os itens 1 e 3 nomeiam como
**pré-requisito comum**: o índice.

## O que o índice cobre

A triagem antiga indexava **apenas** `analises/tabelas/`, e por isso 62,5%
dos seus candidatos eram falso positivo: os 12 indeterminados e boa parte
dos 20 falsos positivos vinham de estatísticas calculadas direto do painel e
dos escores por observação, fontes que nenhuma tabela agregada reproduz.

São indexadas cinco famílias:

  1. `analises/tabelas/*.csv`            — o que a triagem antiga via
  2. `resultados_fase2/tabelas/*.csv`    — onde vivia o gamma de 95,5%
  3. `analises/painel_definitivo.csv`    — estatísticas calculadas direto
  4. `resultados_fase2/dea/*.csv`        — escores por observação
  5. `resultados_fase2/sfa/*.csv`        — idem
  6. os relatórios em **markdown**       — lição de método do §0: resultado
                                            documentado em prosa continua
                                            sendo resultado documentado

## O que ele NÃO faz

Não decide se um número está certo. Pertinência é teste **necessário e não
suficiente**: um token que casa pode casar por coincidência, e um token que
não casa pode ser conta legítima feita no texto. O script separa o que
merece olho humano do que não merece, e informa **qual fonte** resolveu cada
token — que é como se mede se acrescentar uma fonte valeu a pena.

## O resultado que este script produziu sobre si mesmo (29/07/2026)

A **calibração nula** abaixo compara a taxa de acerto dos tokens reais com a
de valores sorteados na mesma faixa. Ela **refuta a previsão do §1**, que
dizia que indexar as três fontes "derrubaria a taxa de falso positivo de
62,5% para perto de zero":

- os candidatos caem de 13 para 0, mas
- a taxa de acerto do **placebo** vai a 100% em uma casa decimal e 94% em
  quatro.

Ou seja: a queda de candidatos não é o documento ficando limpo, é o índice
ficando **denso demais para discriminar**. Os escores do DEA cobrem o
intervalo [0,1] com milhares de valores de quatro casas; depois de
indexá-los, qualquer número de quatro casas naquele intervalo "pertence".

**A conclusão prática, que vale mais que o índice:** pertinência sozinha não
sustenta a Camada 1. Os quatro erros encontrados em 29/07/2026 saíram de
**recontagem própria** (`verificar_contagens_inteiras.py`) e de **leitura de
figura** (Camada 3) — **nenhum** saiu de pertinência. O índice serve para
localizar a fonte de um número e para dar o crédito por fonte; não serve de
teste de correção.

Uso:  .venv\\Scripts\\python.exe indexar_fontes_triagem.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent
SECOES = RAIZ / "analises" / "latex" / "secoes"

# (rótulo, caminhos, era_indexada_antes)
FONTES: list[tuple[str, list[Path], bool]] = [
    ("analises/tabelas", sorted((RAIZ / "analises" / "tabelas").glob("*.csv")),
     True),
    ("fase2/tabelas",
     sorted((RAIZ / "resultados_fase2" / "tabelas").glob("*.csv")), False),
    ("painel_definitivo", [RAIZ / "analises" / "painel_definitivo.csv"], False),
    ("fase2/dea", sorted((RAIZ / "resultados_fase2" / "dea").glob("*.csv")),
     False),
    ("fase2/sfa", sorted((RAIZ / "resultados_fase2" / "sfa").glob("*.csv")),
     False),
    ("relatorios_md", [RAIZ / "resultados_fase2" / "RELATORIO_EXECUCAO.md",
                       RAIZ / "analises" / "NUMEROS_CANONICOS.md"], False),
]

NUM_MD = re.compile(r"-?\d[\d.]*(?:,\d+)?")


def _valores_de_csv(p: Path) -> set[float]:
    """Todo valor numérico de um CSV, mais os derivados que o texto imprime."""
    try:
        df = pd.read_csv(p, low_memory=False)
    except Exception:
        return set()
    vals: set[float] = set()
    for col in df.columns:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if s.empty:
            continue
        arr = np.asarray(s, dtype=float)
        arr = arr[np.isfinite(arr)]
        if arr.size == 0:
            continue
        vals.update(float(x) for x in np.unique(arr))
        # o texto raramente imprime a célula bruta de uma coluna longa; ele
        # imprime a estatística. Sem isto, painel e escores não resolveriam
        # quase nada — que é exatamente por que a triagem antiga falhava.
        if arr.size > 30:
            vals.update(float(x) for x in
                        np.quantile(arr, [0, .10, .25, .50, .75, .90, 1]))
            vals.update({float(arr.mean()), float(arr.std(ddof=1)),
                         float(arr.sum()), float(arr.size)})
            vals.add(float((arr > 100).sum()))
            vals.add(float((arr == 0).mean() * 100))
    return vals


def _valores_de_md(p: Path) -> set[float]:
    if not p.exists():
        return set()
    txt = p.read_text(encoding="utf-8", errors="replace")
    vals: set[float] = set()
    for m in NUM_MD.finditer(txt):
        bruto = m.group(0)
        try:
            vals.add(float(bruto.replace(".", "").replace(",", ".")))
        except ValueError:
            pass
        try:                      # ler também como número "à americana"
            vals.add(float(bruto.replace(",", "")))
        except ValueError:
            pass
    return vals


def construir_indice() -> dict[str, set[float]]:
    indice: dict[str, set[float]] = {}
    for rotulo, caminhos, _ in FONTES:
        vals: set[float] = set()
        for p in caminhos:
            if not p.exists():
                continue
            vals |= (_valores_de_md(p) if p.suffix == ".md"
                     else _valores_de_csv(p))
        indice[rotulo] = vals
    return indice


# ── tokens do documento ──────────────────────────────────────────────────
LIMPAR = [
    re.compile(r"\\includegraphics(\[[^\]]*\])?\{[^}]*\}"),
    re.compile(r"\\(label|ref|cite|input|url|href|subfig)\{[^}]*\}"),
    re.compile(r"[\w/]+\.(png|pdf|csv|tex|py|R|md|xlsx)\b"),
    re.compile(r"%.*$", re.MULTILINE),
]
TOKEN_TEX = re.compile(r"(?<![\w])(\d{1,3}(?:\.\d{3})*(?:\{,\}\d+)?)(?![\w])")


def tokens_do_documento() -> list[dict]:
    achados = []
    for tex in sorted(SECOES.glob("*.tex")):
        txt = tex.read_text(encoding="utf-8", errors="replace")
        for pat in LIMPAR:
            txt = pat.sub(" ", txt)
        for m in TOKEN_TEX.finditer(txt):
            bruto = m.group(1)
            if "{,}" not in bruto and "." not in bruto:
                if len(bruto) > 4:            # código CNES e afins
                    continue
            try:
                val = float(bruto.replace(".", "").replace("{,}", "."))
            except ValueError:
                continue
            if 1900 <= val <= 2100 and "{,}" not in bruto:
                continue                      # ano
            dec = len(bruto.split("{,}")[1]) if "{,}" in bruto else 0
            achados.append({"secao": tex.name, "token": bruto,
                            "valor": val, "decimais": dec})
    return achados


def resolve(val: float, dec: int, vals: set[float]) -> bool:
    """O token casa com algum valor da fonte NA PRECISÃO EM QUE FOI IMPRESSO."""
    if not vals:
        return False
    tol = 0.5 * (10 ** -dec)
    arr = np.fromiter(vals, dtype=float)
    return bool(np.any(np.abs(arr - val) < tol))


def main() -> int:
    print("=" * 74)
    print("ÍNDICE DE FONTES DA TRIAGEM")
    print("=" * 74)
    indice = construir_indice()
    antes: set[float] = set()
    depois: set[float] = set()
    for rotulo, caminhos, era_antiga in FONTES:
        n_arq = sum(1 for p in caminhos if p.exists())
        marca = "[já indexada]" if era_antiga else "[NOVA]"
        linha = (f"  {rotulo:<20} {n_arq:>3} arquivos  "
                 f"{len(indice[rotulo]):>9,} valores   {marca}")
        print(linha.replace(",", "."))
        depois |= indice[rotulo]
        if era_antiga:
            antes |= indice[rotulo]

    toks = tokens_do_documento()
    print(f"\n{len(toks)} tokens numéricos nas seções.\n")

    print("=" * 74)
    print("O QUE AS TRÊS FONTES NOVAS ACRESCENTAM")
    print("=" * 74)
    nao_antes = [t for t in toks if not resolve(t["valor"], t["decimais"], antes)]
    nao_depois = [t for t in toks
                  if not resolve(t["valor"], t["decimais"], depois)]
    print(f"  candidatos com o índice ANTIGO (só analises/tabelas): "
          f"{len(nao_antes)}")
    print(f"  candidatos com o índice COMPLETO                    : "
          f"{len(nao_depois)}")
    if nao_antes:
        queda = 100 * (1 - len(nao_depois) / len(nao_antes))
        print(f"  redução                                            : "
              f"{queda:.1f}%")

    # qual fonte resolve o quê — é assim que se mede se vale manter uma fonte
    print("\n  primeira fonte que resolve cada token:")
    credito = {r: 0 for r, _, _ in FONTES}
    credito["NENHUMA"] = 0
    for t in toks:
        for rotulo, _, _ in FONTES:
            if resolve(t["valor"], t["decimais"], indice[rotulo]):
                credito[rotulo] += 1
                break
        else:
            credito["NENHUMA"] += 1
    for k, v in credito.items():
        print(f"    {k:<20} {v:>5}")

    # ── calibração nula: o teste discrimina alguma coisa? ────────────────
    # Sem isto o número acima não significa nada. Um índice com dezenas de
    # milhares de valores e tolerância de meia unidade casa quase qualquer
    # inteiro por acaso, e "97% dos tokens conferem" viraria a mesma
    # armadilha de R1 v2: concordância lida como validação sem que se tenha
    # perguntado com o que ela NÃO concordaria.
    print("\n" + "=" * 74)
    print("CALIBRAÇÃO NULA — a taxa de acerto ao acaso, por precisão")
    print("=" * 74)
    rng = np.random.default_rng(20260729)
    print(f"  {'decimais':>9} {'tokens reais':>13} {'casam':>7} "
          f"{'placebo':>9} {'casam':>7}")
    for dec in (0, 1, 2, 3, 4):
        reais = [t for t in toks if t["decimais"] == dec]
        if not reais:
            continue
        casam = sum(resolve(t["valor"], dec, depois) for t in reais)
        # placebo: mesma faixa de grandeza, valor sorteado
        lo, hi = min(t["valor"] for t in reais), max(t["valor"] for t in reais)
        placebo = rng.uniform(lo, hi, size=max(400, len(reais)))
        placebo = np.round(placebo, dec)
        casam_p = sum(resolve(float(v), dec, depois) for v in placebo)
        print(f"  {dec:>9} {len(reais):>13} {100*casam/len(reais):>6.1f}% "
              f"{len(placebo):>9} {100*casam_p/len(placebo):>6.1f}%")
    print("\n  Onde as duas colunas de porcentagem se encostam, o teste de\n"
          "  pertinência NÃO está discriminando: ali ele só confirma que o\n"
          "  número cabe na faixa, e a conferência tem de ser humana ou por\n"
          "  mecanismo próprio (ver verificar_contagens_inteiras.py).")
    print("\n  LEIA A TABELA ACIMA ANTES DE CELEBRAR A REDUÇÃO DE CANDIDATOS.\n"
          "  Indexar mais fontes derruba o número de candidatos, mas parte\n"
          "  dessa queda é o índice ficando DENSO demais para discriminar —\n"
          "  os escores do DEA cobrem [0,1] com milhares de valores de quatro\n"
          "  casas, e depois disso qualquer número de quatro casas naquele\n"
          "  intervalo 'pertence'. Zero candidatos não é um documento limpo:\n"
          "  é um teste que parou de testar.")

    saida = RAIZ / "analises" / "tabelas" / "tab_triagem_candidatos.csv"
    pd.DataFrame(nao_depois).to_csv(saida, index=False, encoding="utf-8")
    print(f"\n[TAB] {saida.relative_to(RAIZ)} — {len(nao_depois)} candidatos "
          "para inspeção humana")
    print("\nPertinência é necessária e NÃO suficiente: casar não prova que o "
          "número\nestá certo, e não casar não prova que está errado. O "
          "índice separa o que\nmerece olho humano do que não merece.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
