"""
A2 --- nomenclatura unica de complexidade: "complexidade Barcelona".

O documento vinha usando dois nomes para a mesma covariavel: "escore
estrutural" / "complexidade estrutural" no corpo e nas legendas, e "faixa
Barcelona" para a versao em faixas. Havia ainda uma nota de rodape em
sec01 explicando que existia um segundo escore, ponderado pela mortalidade
relativa, e justificando a escolha pela salvaguarda de circularidade.

A decisao editorial (Bloco A, item A2) e usar UM nome so --- "complexidade
Barcelona" --- e nao expor ao leitor administrador que houve duas versoes,
nem a correlacao entre elas, nem o debate de circularidade. O escore em
faixas continua a se chamar "faixa Barcelona", que ja e consistente com o
nome novo.

Este script faz apenas a substituicao mecanica de nome nos .tex. A remocao
da nota de rodape de sec01 e feita a mao, porque e supressao de conteudo e
nao renomeacao.

Uso:
    python analises/renomear_complexidade_barcelona.py            # aplica
    python analises/renomear_complexidade_barcelona.py --dry-run  # so lista
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
LATEX = RAIZ / "latex"

# Ordem importa: as formas mais longas primeiro, para que "complexidade
# estrutural" nao seja parcialmente substituida antes de "Complexidade
# estrutural media".
SUBSTITUICOES: list[tuple[str, str]] = [
    ("Complexidade estrutural", "Complexidade Barcelona"),
    ("complexidade estrutural", "complexidade Barcelona"),
    ("complexidade\nestrutural", "complexidade\nBarcelona"),
    ("Complexidade\nestrutural", "Complexidade\nBarcelona"),
]

# Arquivos-alvo: principal.tex e todas as secoes/apendices.
def alvos() -> list[Path]:
    arquivos = [LATEX / "principal.tex"]
    arquivos += sorted((LATEX / "secoes").glob("*.tex"))
    return [a for a in arquivos if a.exists()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    total = 0
    for caminho in alvos():
        texto = caminho.read_text(encoding="utf-8")
        original = texto
        contagem_arquivo = 0
        for antigo, novo in SUBSTITUICOES:
            n = texto.count(antigo)
            if n:
                texto = texto.replace(antigo, novo)
                contagem_arquivo += n
        if contagem_arquivo:
            total += contagem_arquivo
            print(f"  {caminho.name}: {contagem_arquivo}")
            if not args.dry_run and texto != original:
                caminho.write_text(texto, encoding="utf-8")

    verbo = "encontradas" if args.dry_run else "substituidas"
    print(f"\n{total} ocorrencias {verbo}.")

    # Guarda: nenhuma forma antiga pode sobreviver depois da aplicacao.
    if not args.dry_run:
        resto = []
        for caminho in alvos():
            texto = caminho.read_text(encoding="utf-8")
            for antigo, _ in SUBSTITUICOES:
                if antigo in texto:
                    resto.append(f"{caminho.name}: {antigo!r}")
        if resto:
            print("\nFALHA --- formas antigas sobreviveram:")
            for r in resto:
                print(f"  {r}")
            return 1
        print("Guarda: nenhuma forma antiga sobrevive nos .tex.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
