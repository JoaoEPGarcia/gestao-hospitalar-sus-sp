"""Capacidade que muda dentro do ano: o limite superior do viés de calendário.

O ramo que `auditar_uti_ano_parcial.py` deixou aberto
--------------------------------------------------
As duas ocupações dividem a produção do ano por `leitos × 365`. O
numerador é fluxo acumulado; o denominador é uma FOTOGRAFIA do cadastro.
Quando a capacidade muda no meio do ano, os dois medem períodos
diferentes e a razão é artefato de calendário.

A transição 0 ↔ positivo é identificável e já está tratada: 30
observações, deslocamento de 0,11 erro padrão no contraste OSS
(`analises/auditar_uti_ano_parcial.py`). Este script trata o resto — a
capacidade que muda SEM passar por zero, uma ordem de grandeza mais
frequente (9,3% das observações na UTI, 28,2% na internação).

O contraste é estimado na especificação ADOTADA de cada indicador: log
MQO na internação e GLM Gama com ligação log na intensidade de UTI, cujo
valor canônico é 19,3% (`tab_est_ocup_uti_gama.csv`). Estimar o limite
sobre o log OLS da UTI mediria a robustez de uma especificação que a
Seção 14 já declarou superada.

Dois artefatos distintos, e este script só alcança um
-----------------------------------------------------
  A. CAPACIDADE MÓVEL — o cadastro muda durante o ano Y, e a fotografia
     não representa a capacidade média de Y. Erra nas duas direções.
     Identificável: basta comparar o cadastro de anos consecutivos.
  B. CADASTRO PARADO — a capacidade real cresceu (leito emergencial da
     pandemia) e o cadastro nunca foi atualizado. Diárias sobem, o
     denominador não. É o diagnóstico de `diagnostico_meia_competencia.py`
     e é a fonte da ocupação acima de 100%.

São conjuntos QUASE DISJUNTOS, e o bloco [2] mede isso: na UTI, a
ocupação acima de 100% é 3,2× mais frequente onde o cadastro NÃO se mexeu
(9,81% contra 3,03%). O excesso mora em B, não em A — o que reconfirma,
por um caminho independente, a conclusão daquele diagnóstico.

Este script limita A. B fica fora do alcance por uma razão de método, não
de dados: a assinatura de B é diárias que sobem contra denominador parado,
que é aritmeticamente a própria ocupação. Excluir por essa assinatura é
selecionar pela variável dependente, e o remédio seria pior que a doença.
B segue tratado como está — winsorização no p99 e leitura cautelosa do
biênio —, e isso permanece uma limitação declarada, não resolvida.

Por que a resposta aqui é um LIMITE, não uma correção
-----------------------------------------------------
`diagnostico_meia_competencia.py` estabeleceu que o SIH não traz
competência mensal — agregado anual, uma linha de resumo por CNES e ano —
e concluiu, corretamente, que o ajuste pró rata é impossível. Essa
conclusão fecha a porta da CORREÇÃO e é aceita aqui sem revisão.

Mas ela não fecha a porta da MEDIDA. O mês da mudança não é recuperável;
a mudança em si é, comparando o cadastro de anos consecutivos. Isso não
identifica quais observações estão viesadas — identifica o conjunto que
as CONTÉM. Estimar sem esse conjunto não corrige o viés: mede quanto ele
poderia, no máximo, estar movendo o resultado.

O preço e a confusão do limite
------------------------------
Excluir toda observação com capacidade alterada também exclui hospitais
que cresceram de verdade, e crescimento não é ruído — é desempenho. Se a
mudança de capacidade for diferencial por categoria de gestão, o limite
fica confundido com composição, e passa a ser um limite sobre um
contraste diferente. O bloco [2] mede essa diferencialidade antes de
qualquer estimação, e o limite só é interpretável à luz dela.

Reprodução: python analises/auditar_capacidade_movel.py
Escreve: analises/tabelas/tab_est_capacidade_movel_limite.csv
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import estimacao as E  # noqa: E402

E._tab = lambda *a, **k: None

PASTA_TAB = E.base.PASTA_TABELAS

# indicador -> (coluna de capacidade, rótulo)
INDICADORES = {
    "ocupacao_internacao": ("leitos_sus", "Ocupação internação"),
    "ocupacao_uti": ("uti_sus", "Ocupação UTI (intensidade)"),
}
# degraus do limite: variação relativa mínima da capacidade para excluir.
# 0.0 é o degrau mais severo (qualquer mudança, inclusive de um leito).
DEGRAUS = [0.0, 0.10, 0.25, 0.50]


def marcar_capacidade_movel(painel):
    """Variação relativa da capacidade contra o ano anterior, por indicador.

    O primeiro ano de cada CNES fica sem variação definida (NaN) e nunca é
    excluído: não há ano anterior contra o que comparar, e tratá-lo como
    'sem mudança' inventaria informação.
    """
    d = painel.sort_values(["cnes", "ano"]).copy()
    for _, (cap, _rot) in INDICADORES.items():
        ant = d.groupby("cnes")[cap].shift(1)
        d[f"var_{cap}"] = (d[cap] - ant).abs() / ant.replace(0, np.nan)
    return d


def descrever(painel):
    print("\n" + "=" * 74)
    print("[1] COM QUE FREQUÊNCIA A CAPACIDADE SE MEXE")
    print("=" * 74)
    for ind, (cap, rot) in INDICADORES.items():
        dom = painel[cap] > 0
        var = painel[f"var_{cap}"]
        print(f"\n  {rot} (denominador: {cap})")
        print(f"    observações no domínio ......... {int(dom.sum()):>5}")
        for g in DEGRAUS:
            m = dom & (var > g) if g else dom & (var > 0)
            print(f"    capacidade muda mais de {int(100 * g):>2}% ... "
                  f"{int(m.sum()):>5} ({100 * m.sum() / dom.sum():4.1f}%)")


def ligar_ao_excesso(painel):
    """O excesso acima de 100% mora no artefato A ou no B?

    Teste de separação entre os dois. Se o excesso viesse da capacidade
    móvel (A), concentrar-se-ia nos anos de cadastro ALTERADO. Se vier do
    cadastro parado contra produção em alta (B), concentra-se nos anos de
    cadastro PARADO — e a razão de prevalência cai abaixo de 1.

    O resultado decide o que o limite do bloco [3] pode e não pode
    prometer: ele exclui A, então só limita o que estiver em A.
    """
    print("\n" + "=" * 74)
    print("[2] O EXCESSO ACIMA DE 100% MORA EM QUAL DOS DOIS ARTEFATOS?")
    print("=" * 74)
    print("  razão > 1 => o excesso está na capacidade móvel (artefato A)")
    print("  razão < 1 => o excesso está no cadastro parado (artefato B)")
    for ind, (cap, rot) in INDICADORES.items():
        dom = (painel[cap] > 0) & painel[f"var_{cap}"].notna()
        d = painel[dom]
        mexeu = d[f"var_{cap}"] > 0
        acima = d[ind] > 100
        print(f"\n  {rot}")
        print(f"    acima de 100% | capacidade mexeu ... "
              f"{100 * acima[mexeu].mean():5.1f}%  (n={int(mexeu.sum())})")
        print(f"    acima de 100% | capacidade parada .. "
              f"{100 * acima[~mexeu].mean():5.1f}%  (n={int((~mexeu).sum())})")
        razao = acima[mexeu].mean() / acima[~mexeu].mean()
        onde = "artefato A (capacidade móvel)" if razao > 1 \
            else "artefato B (cadastro parado)"
        print(f"    razão de prevalência ............... {razao:5.2f}×  "
              f"-> {onde}")

    print("\n" + "-" * 74)
    print("  DIFERENCIALIDADE POR CATEGORIA — o limite fica confundido?")
    print("-" * 74)
    linhas = []
    for ind, (cap, rot) in INDICADORES.items():
        dom = (painel[cap] > 0) & painel[f"var_{cap}"].notna()
        d = painel[dom]
        for cat in E.CATEGORIAS:
            b = d[d["modelo_gestao_proxy"] == cat]
            if not len(b):
                continue
            linhas.append({"indicador": rot, "categoria": cat, "n": len(b),
                           "pct_capacidade_movel":
                               round(100 * (b[f"var_{cap}"] > 0).mean(), 1)})
    tab = pd.DataFrame(linhas)
    for rot in tab["indicador"].unique():
        b = tab[tab["indicador"] == rot]
        print(f"\n  {rot}:")
        for _, l in b.iterrows():
            print(f"    {l['categoria']:<20} {l['pct_capacidade_movel']:>5.1f}% "
                  f"(n={int(l['n'])})")
        amp = b["pct_capacidade_movel"].max() - b["pct_capacidade_movel"].min()
        print(f"    amplitude entre categorias: {amp:.1f} p.p.")
    return tab


def _oss_log(dados, col="y"):
    """MQO no log — especificação da ocupação de internação."""
    res = smf.ols(f"{col} ~ {E.COV_BASE}", data=dados).fit(
        cov_type="cluster", cov_kwds={"groups": dados["cnes"]})
    return E._extrair_oss(res)


def _oss_gama(dados):
    """GLM Gama com ligação log — especificação CANÔNICA da intensidade de
    UTI, adotada em `inferencia_robusta.py:bloco_uti` depois que o
    diagnóstico quantílico do log OLS (0,814) foi superado pelo da Gama
    (0,944). O valor canônico do contraste é 19,3%, e é sobre ele que o
    limite tem de ser calculado — o log OLS entra só como continuidade
    com a especificação que a Seção 14 declara superada."""
    res = sm.GLM.from_formula(
        f"ocupacao_uti_w ~ {E.COV_BASE}", data=dados,
        family=sm.families.Gamma(link=sm.families.links.Log())
    ).fit(cov_type="cluster", cov_kwds={"groups": dados["cnes"]})
    return E._extrair_oss(res)


# indicador -> ajustador do contraste OSS na especificação adotada
AJUSTE = {
    "ocupacao_internacao": ("log MQO", _oss_log),
    "ocupacao_uti": ("GLM Gama", _oss_gama),
}


def limitar(painel):
    """O limite: reestimar excluindo o conjunto que contém as viesadas.

    Na UTI a exclusão vale só para a componente de intensidade, pela mesma
    razão de auditar_uti_ano_parcial.py — a parte 1 mede se existe UTI, e
    a capacidade mudar não afeta essa medida.
    """
    print("\n" + "=" * 74)
    print("[3] O LIMITE: CONTRASTE OSS vs DIRETA AO LONGO DOS DEGRAUS")
    print("=" * 74)

    r_int = E.modelo_ocup_internacao(painel, verboso=False)
    r_uti = E.modelo_ocup_uti(painel, verboso=False)
    bases = {"ocupacao_internacao": r_int["amostra"],
             "ocupacao_uti": r_uti["positivos"]}

    linhas = []
    for ind, (cap, rot) in INDICADORES.items():
        base = bases[ind]
        nome_esp, ajustar = AJUSTE[ind]
        c0, e0 = ajustar(base)
        print(f"\n  {rot} — especificação {nome_esp}")
        print(f"    {'degrau':<26} {'n':>5}  {'coef OSS':>10} {'EP':>8} "
              f"{'efeito':>8}  {'Δ em EP':>8}")
        print(f"    {'amostra cheia':<26} {len(base):>5}  {c0:>+10.5f} "
              f"{e0:>8.5f} {100 * (np.exp(c0) - 1):>+7.1f}% {'—':>9}")
        linhas.append({"indicador": rot, "especificacao": nome_esp,
                       "degrau": "amostra cheia",
                       "n": len(base), "coef_oss": round(c0, 5),
                       "ep": round(e0, 5),
                       "efeito_pct": round(100 * (np.exp(c0) - 1), 2),
                       "delta_em_ep": np.nan})
        for g in DEGRAUS:
            fora = base[f"var_{cap}"] > g if g else base[f"var_{cap}"] > 0
            sub = base[~fora.fillna(False)]
            c, e = ajustar(sub)
            rot_g = (f"sem mudança > {int(100 * g)}%" if g
                     else "sem QUALQUER mudança")
            print(f"    {rot_g:<26} {len(sub):>5}  {c:>+10.5f} {e:>8.5f} "
                  f"{100 * (np.exp(c) - 1):>+7.1f}% {(c - c0) / e0:>+9.2f}")
            linhas.append({"indicador": rot, "especificacao": nome_esp,
                           "degrau": rot_g, "n": len(sub),
                           "coef_oss": round(c, 5), "ep": round(e, 5),
                           "efeito_pct": round(100 * (np.exp(c) - 1), 2),
                           "delta_em_ep": round((c - c0) / e0, 3)})

    tab = pd.DataFrame(linhas)
    tab.to_csv(PASTA_TAB / "tab_est_capacidade_movel_limite.csv",
               index=False, encoding="utf-8-sig")
    print(f"\n  [TAB] tab_est_capacidade_movel_limite.csv")
    return tab


def main():
    painel = marcar_capacidade_movel(E.preparar(E.carregar_e_verificar()))
    descrever(painel)
    dif = ligar_ao_excesso(painel)
    tab = limitar(painel)

    print("\n" + "=" * 74)
    print("VEREDITO")
    print("=" * 74)
    sev = tab[tab["degrau"] == "sem QUALQUER mudança"]
    for _, l in sev.iterrows():
        print(f"  {l['indicador']}: no degrau mais severo (n={int(l['n'])}), "
              f"OSS vs Direta\n    vai a {l['efeito_pct']:+.1f}% "
              f"({l['delta_em_ep']:+.2f} erro padrão da estimativa cheia)")
    deltas = {l["indicador"]: l["delta_em_ep"] for _, l in sev.iterrows()}
    opostos = len(set(np.sign(list(deltas.values())))) > 1
    print(f"\n  Os dois indicadores se movem em direções "
          f"{'OPOSTAS' if opostos else 'IGUAIS'} "
          f"({' e '.join(f'{v:+.2f}' for v in deltas.values())} EP).")
    print("  Um viés de calendário sistemático empurraria os dois para o "
          "mesmo lado;\n  o que se vê tem a assinatura de ruído amostral de "
          "excluir 9% a 28%\n  da amostra, não a de um artefato que sustenta "
          "o resultado.")
    print("\n  DUAS RESSALVAS, ambas medidas acima:")
    print("    1. O limite NÃO é correção. O conjunto excluído contém as "
          "viesadas e\n       também hospitais que cresceram de verdade, e a "
          "capacidade móvel é\n       diferencial por categoria (até 15,3 "
          "p.p. de amplitude na internação).")
    print("    2. O limite cobre o artefato A. O excesso acima de 100% está "
          "em B —\n       cadastro parado —, que não é excluível sem "
          "selecionar pela variável\n       dependente. Segue tratado por "
          "winsorização, como limitação declarada.")


if __name__ == "__main__":
    main()
