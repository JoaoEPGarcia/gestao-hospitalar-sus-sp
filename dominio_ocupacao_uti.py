# dominio_ocupacao_uti.py
# Domínio de definição da ocupação de UTI. Uma função, e a trava que a mantém
# única.
#
# POR QUE ESTE MÓDULO EXISTE
# --------------------------
# `ocupacao_uti = 100 × diarias_uti / (uti_sus × 365)` é INDEFINIDA quando
# `uti_sus = 0`. No painel essas 688 observações entraram como ZERO ESTRUTURAL
# em vez de não-aplicável, o que é o defeito corrigido na Etapa 1: um hospital
# SEM UTI SUS passava a contar como hospital com UTI 0% ocupada, puxando a
# média da sua categoria para baixo na proporção em que ela concentra
# hospitais sem UTI.
#
# A correção existia até 29/07/2026 apenas como COLUNA de
# `painel_segmentado.csv` (`ocupacao_uti_valida`), e não em
# `painel_definitivo.csv`, que é a base lida por `analise_exploratoria.py` e
# `estimacao.py`. Havia portanto duas bases com DOMÍNIOS DIFERENTES para o
# mesmo indicador, e a publicada era a do domínio errado.
#
# `ocupacao_uti_valida` não é dado: é restrição de domínio, função
# determinística de duas colunas que `painel_definitivo.csv` já contém. Dado
# congelado guarda medição; definição mora em código. Por isso ela passa a
# viver aqui, e não num painel.
#
# NENHUM ARQUIVO PROTEGIDO É TOCADO: `painel_definitivo.csv`,
# `construir_painel_definitivo.py` e `analise_sih.py` seguem intactos.
#
# A TRAVA
# -------
# `verificar_equivalencia()` confere, célula a célula nas 3.179 observações,
# que esta função reproduz exatamente a coluna do `painel_segmentado.csv`, e
# aborta se divergir. É o que impede as duas definições de andarem separadas
# de novo — se alguém mudar uma, a checagem quebra.

from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent
PAINEL_SEGMENTADO = RAIZ / "analises" / "painel_segmentado.csv"

COL = "ocupacao_uti_valida"


def ocupacao_uti_valida(painel: pd.DataFrame) -> pd.Series:
    """Ocupação de UTI restrita ao domínio em que ela é definida.

    Devolve `ocupacao_uti` onde há capacidade de UTI SUS cadastrada
    (`uti_sus > 0`) e `NaN` — não-aplicável — onde não há.

    O critério é a CAPACIDADE, nunca o desfecho: um hospital com UTI
    habilitada e nenhuma diária no ano permanece na amostra, com ocupação 0.
    Excluí-lo seria condicionar na variável dependente, que é o defeito 2 de
    R8, cometido em outro ponto do projeto e não repetido aqui.
    """
    for c in ("uti_sus", "ocupacao_uti"):
        if c not in painel.columns:
            raise KeyError(f"coluna ausente no painel: {c}")
    return painel["ocupacao_uti"].where(painel["uti_sus"] > 0, np.nan)


def verificar_equivalencia(painel: pd.DataFrame, verboso: bool = True) -> None:
    """Aborta se esta função divergir da coluna do painel_segmentado.csv.

    Comparação célula a célula, com os NaN tratados como iguais entre si.
    """
    if not PAINEL_SEGMENTADO.exists():
        raise SystemExit(
            f"[dominio-uti] referência ausente: {PAINEL_SEGMENTADO}. "
            "A trava de equivalência não pode ser dispensada em silêncio.")

    ref = pd.read_csv(PAINEL_SEGMENTADO)
    if COL not in ref.columns:
        raise SystemExit(
            f"[dominio-uti] {PAINEL_SEGMENTADO.name} não tem a coluna {COL}.")
    if len(ref) != len(painel):
        raise SystemExit(
            f"[dominio-uti] painéis de tamanhos diferentes: "
            f"{len(painel)} contra {len(ref)} na referência.")

    # o pareamento é por (cnes, ano), não por posição de linha
    chave = ["cnes", "ano"]
    esq = painel[chave].copy()
    esq["calculado"] = ocupacao_uti_valida(painel).to_numpy()
    dir_ = ref[chave + [COL]].rename(columns={COL: "referencia"})
    j = esq.merge(dir_, on=chave, how="outer", validate="one_to_one")

    if len(j) != len(painel):
        raise SystemExit(
            f"[dominio-uti] pareamento por (cnes, ano) falhou: "
            f"{len(j)} linhas contra {len(painel)}.")

    a, b = j["calculado"], j["referencia"]
    ambos_nan = a.isna() & b.isna()
    iguais = np.isclose(a, b, rtol=0, atol=1e-9, equal_nan=True) | ambos_nan
    n_div = int((~iguais).sum())

    if n_div:
        ex = j[~iguais].head(5)
        raise SystemExit(
            f"[dominio-uti] DIVERGÊNCIA em {n_div} de {len(j)} células "
            f"entre esta função e {PAINEL_SEGMENTADO.name}.\n"
            f"As duas definições andaram separadas — resolva antes de "
            f"publicar qualquer número.\n{ex.to_string(index=False)}")

    if verboso:
        n_val = int(a.notna().sum())
        print(f"[dominio-uti] equivalência conferida célula a célula: "
              f"{len(j)} observações, {n_val} no domínio válido, "
              f"{len(j) - n_val} não-aplicáveis. Zero divergências.")


if __name__ == "__main__":
    d = pd.read_csv(RAIZ / "analises" / "painel_definitivo.csv",
                    encoding="utf-8-sig")
    verificar_equivalencia(d)
    s = ocupacao_uti_valida(d)
    print(f"[dominio-uti] média {s.mean():.2f} | mediana {s.median():.2f} | "
          f"n {int(s.notna().sum())}")
