"""
analise_exploratoria.py
=======================
Análise Exploratória do painel analítico de hospitais SUS/SP (289 hospitais,
2015 a 2025, 3.179 observações de hospital e ano, painel pós-ETAPA F de
15/07/2026), gerado por
construir_painel_definitivo.py. Prepara a fase de estimação: caracteriza os
dados, perfila as categorias institucionais, visualiza as conversões de
gestão e decide empiricamente as famílias de distribuição.

Blocos:
  0. Verificação do painel (aborta se não conferir)
  1. Univariada dos 5 indicadores oficiais e das 2 ocupações
  2. Diagnóstico distribucional (Beta/ZOIB, LogNormal vs Gama, Poisson vs BN)
  3. Corte por categoria institucional (modelo_gestao_proxy)
  4. Corte por complexidade (faixa_barcelona) e por porte
  5. Tendência temporal (geral e por categoria; destaque 2020 e 2021)
  6. Estudo de eventos dos 5 conversores de Direta para OSS
  7. Correlações de Spearman
  8. Qualidade de dados e decisões para a modelagem

SALVAGUARDA DE CIRCULARIDADE: toda análise que envolve mortalidade usa
complexidade_estrutural, nunca complexidade_pond_mort.

Saídas: figuras em analises/figuras_analise_exploratoria (pasta exclusiva),
tabelas tab_ae_* em analises/tabelas.

USO: python analise_exploratoria.py
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter
from scipy import stats
from scipy.optimize import minimize

import analise_sih as base                      # embrulha stdout no encoding do terminal
import dominio_ocupacao_uti                     # domínio da ocupação de UTI (Etapa 1)

# ══════════════════════════════════════════════════════════════════════════════
# A. CONSTANTES E ESTILO
# ══════════════════════════════════════════════════════════════════════════════

PASTA_FIG_AE = base.PASTA_ANALISES / "figuras_analise_exploratoria"

# A1 (decisão de 29/07/2026): a MORTALIDADE AJUSTADA (`mort_sem_excl`, que
# exclui óbitos fetais, maternos e neonatais) saiu do documento inteiro. Ela
# correlaciona 1,000 em Spearman com a mortalidade geral e nunca sustentou
# achado próprio: mantê-la duplicava uma linha em toda tabela e uma barra em
# toda figura, sem acrescentar informação.
#
# A remoção é feita AQUI e não em `analise_sih.py`, que define a lista
# original, porque aquele arquivo está na lista de protegidos do protocolo de
# trabalho (regra 4), ao lado de `painel_definitivo.csv` e
# `construir_painel_definitivo.py`. A lista de lá permanece intacta; esta
# camada descritiva filtra ao consumi-la.
MORT_AJUSTADA = "mort_sem_excl"
INDICADORES = [c for c in base.INDICADORES if c != MORT_AJUSTADA]  # 4 oficiais
OCUPACOES   = ["ocupacao_internacao", "ocupacao_uti"]
IND7        = INDICADORES + OCUPACOES           # 6 indicadores descritivos

# Item 1.5 (decisão de 14/07/2026): a camada descritiva usa o faturamento
# REAL (custo_real = custo_saida × fator IPCA, preços de 2025). Nas FIGURAS
# o real SUBSTITUI o nominal (a comparação nominal×real segue na fig_ae_07
# dedicada); nas TABELAS o real entra AO LADO do nominal.
IND7_FIG = [("custo_real" if c == "custo_saida" else c) for c in IND7]
IND8_TAB = IND7 + ["custo_real"]

# Item 1 (decisão de 27/07/2026): o faturamento passa a aparecer em valores
# REAIS também na univariada, no inventário de outliers e no estudo de eventos
# dos conversores. O documento não imprime mais valor monetário em base
# nominal; a única exceção é a figura fig_ae_07 e a tabela da Seção 6, cujo
# assunto é justamente a comparação entre as duas bases.
IND5_FIG = [("custo_real" if c == "custo_saida" else c) for c in INDICADORES]

# ── Legibilidade dos histogramas da univariada (31/07/2026) ────────────────
# Três indicadores tinham cauda tão longa que o eixo horizontal ficava sem
# resolução onde mora a massa: o faturamento ia até R$ 42.000 com metade dos
# hospitais abaixo de R$ 1.328, e a ocupação de UTI ia até 875% com a mediana
# em 76,5%. O gestor lia um eixo de 0 a 42.000 com marca a cada 10.000 e não
# conseguia situar o próprio hospital.
#
# A correção é ZOOM COM PRESTAÇÃO DE CONTAS, não corte: o histograma é
# desenhado dentro da janela, e o que fica fora vira uma barra hachurada
# própria, rotulada com quantas observações são e qual é o máximo. Nada
# desaparece do gráfico; o que muda é que a cauda passa a ocupar o espaço
# proporcional à sua massa, e não à sua amplitude.
#   indicador: (limite da janela, passo dos ticks)
JANELA_HIST = {
    "custo_real":   (6000, 500),    # deixa 79 obs (2,5%) fora, máx 41.997
    "ocupacao_uti": (200, 25),      # deixa 20 obs (0,8%) fora, máx 875
}

# ── Legibilidade dos VIOLINOS por categoria (01/08/2026) ───────────────────
# Mesmo defeito dos histogramas, e pelo mesmo motivo: o eixo vertical é
# esticado por um punhado de observações extremas e a silhueta, que é a
# informação do gráfico, encolhe até virar um traço. Na ocupação de UTI o
# eixo ia a 875% para acomodar UM hospital-ano, e os cinco violinos ficavam
# comprimidos no primeiro sexto da altura: o gestor não conseguia comparar
# categoria nenhuma.
#
# A correção é a mesma dos histogramas, JANELA COM PRESTAÇÃO DE CONTAS. O
# violino continua sendo estimado sobre TODOS os dados (a silhueta desenhada
# não muda de forma); o que muda é o trecho do eixo que a página mostra, e
# o gráfico declara em rodapé quantas observações ficaram acima da janela e
# qual é o máximo real. Nada é descartado do cálculo.
# A janela substitui também o teto fixo de 35 dias do TMP (item 1.4 de
# 13-14/07/2026): a decisão daquele item era manter o TMP em escala LINEAR,
# e ela permanece; o que muda é só o valor do teto, que estava em 35 dias
# para um indicador cujo máximo é 24,8 e cuja massa acaba em 12. Um terço da
# altura do gráfico era branco.
#   indicador: (limite superior da janela, obs fora, máximo real)
JANELA_VIOL = {
    "ocupacao_uti":        200,     # deixa 20 obs (0,80%) fora, máx 875
    "ocupacao_internacao": 160,     # deixa  7 obs (0,22%) fora, máx 237
    "mort_all":            0.16,    # deixa 21 obs (0,66%) fora, máx 0,260
    "tmp":                 16,      # deixa  6 obs (0,19%) fora, máx 24,8
}

# A massa exatamente em zero vira barra DESTACADA a partir desta fração.
# Motivo (31/07/2026): na fração de alta complexidade os 31,3% de zeros
# caíam no mesmo primeiro bin dos positivos pequenos, e a barra resultante
# subia a 58,5%. Quem batia o olho lia "58% não fazem alta complexidade",
# que é falso: 31,3% não fazem, e os outros 27% fazem pouco. Separar as duas
# coisas é a única leitura honesta de uma distribuição inflada em zero.
PISO_MASSA_ZERO = 0.05

# Indicadores cuja massa em zero vira barra própria INDEPENDENTEMENTE do piso
# acima (04/08/2026, a pedido de João). Na mortalidade os zeros são 0,9% e não
# alcançariam o piso, mas eles não são resíduo: são o extremo da corcova
# esquerda de maternidades e especializados que a Seção 3 identifica, e o
# gestor precisa lê-los como barra no eixo, e não como nota escrita no canto
# do gráfico. A barra é a mesma construção da alta complexidade; o que muda é
# só o gatilho.
ZERO_SEMPRE_DESTACADO = {"mort_all"}

ROT = {
    "mort_all":            "Mortalidade geral",
    "mort_sem_excl":       "Mortalidade ajustada",
    "tmp":                 "TMP (dias)",
    "custo_saida":         "Faturamento por saída (SIH, R$)",
    "custo_real":          "Faturamento real por saída (R$ de dez/2025)",
    "pct_alta_complex":    "Fração alta complexidade",
    "ocupacao_internacao": "Ocupação internação (%)",
    "ocupacao_uti":        "Ocupação UTI (%)",
    "complexidade_estrutural": "Complexidade Barcelona",
}
# mort_sem_excl exclui óbitos fetais, maternos e neonatais; o rótulo
# "Mortalidade ajustada" foi adotado por ser mais intuitivo nas figuras

# paleta fria com matizes distinguíveis (azul marinho, verde água, azul
# claro, violeta; cinza neutro só para Privado), ordem fixa por categoria,
# reforçada por um marcador próprio para cada categoria
CATEGORIAS = ["Direta", "OSS", "Público Municipal", "Filantrópico", "Privado"]
CORES_CAT = {
    "Direta":            "#0d366b",
    "OSS":               "#0f9b8e",
    "Público Municipal": "#5598e7",
    "Filantrópico":      "#6a51c7",
    "Privado":           "#898781",
}
MARCADORES = {
    "Direta":            "o",
    "OSS":               "s",
    "Público Municipal": "^",
    "Filantrópico":      "D",
    "Privado":           "X",
}
# versão clara da paleta, para preenchimentos com números por cima
# (violinos): mesmos matizes, tons claros que não escondem o texto
CORES_CAT_CLARAS = {
    "Direta":            "#9ec5f4",
    "OSS":               "#8fd9cf",
    "Público Municipal": "#c4dcf9",
    "Filantrópico":      "#cfc4f2",
    "Privado":           "#d6d5d1",
}
COR_SERIE  = "#2a78d6"                          # séries únicas
COR_APOIO  = "#0d366b"                          # curvas de ajuste e comparação
COR_EVENTO = "#52514e"                          # linhas de evento e referência
RAMPA_5    = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]
RAMPA_4    = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
COR_GRADE  = "#e1e0d9"
COR_EIXO   = "#c3c2b7"
COR_MUTED  = "#898781"
COR_BANDA  = "#f0efec"                          # faixa 2020 e 2021
COR_ALERTA = "#c0562f"                          # subconjunto que é artefato

CONVERSOES = {2081695: 2019, 2078287: 2023, 2082225: 2025,
              2091755: 2025, 2750511: 2025}

# IPCA anual (variação % dez/dez, IBGE); 2025 fechado em 4,26%
# (Agência IBGE de Notícias, jan/2026)
IPCA_ANUAL = {2015: 10.67, 2016: 6.29, 2017: 2.95, 2018: 3.75, 2019: 4.31,
              2020: 4.52, 2021: 10.06, 2022: 5.79, 2023: 4.62, 2024: 4.83,
              2025: 4.26}


def _fatores_ipca_2025() -> dict:
    """Fator multiplicativo que leva valores do ano de referência a preços
    de 2025 (índice acumulado dez/dez até o fim de cada ano)."""
    anos = sorted(IPCA_ANUAL)
    indice, acum = {}, 1.0
    for a in anos:
        acum *= 1 + IPCA_ANUAL[a] / 100
        indice[a] = acum
    return {a: indice[anos[-1]] / indice[a] for a in anos}

plt.rcParams.update({
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": COR_EIXO, "axes.labelcolor": "#0b0b0b",
    "axes.grid": True, "grid.color": COR_GRADE, "grid.linewidth": .6,
    "xtick.color": COR_MUTED, "ytick.color": COR_MUTED,
    "font.size": 11.5, "axes.titlesize": 11.5, "figure.titlesize": 11,
})


# Item 5 (27/07/2026): nenhuma figura deste documento imprime "Densidade" no
# eixo vertical. O público inclui gestores não estatísticos, que leem
# densidade como percentual — e ela não é percentual nem contagem. Todos os
# histogramas passam a contar observações de hospital e ano.
#
# Revisão de 29/07/2026: o eixo vertical dos histogramas deixa de ser a
# CONTAGEM de hospitais-ano e passa a ser o PERCENTUAL do total da amostra
# daquela figura. O motivo é de leitura, não de estatística: "400
# hospitais-ano" só significa algo para quem carrega o denominador na cabeça
# (3.179, ou 2.491 na ocupação de UTI, ou o interior de (0,1) nos ajustes
# Beta), enquanto "12,6% do total" é auto-suficiente e comparável entre
# figuras com denominadores diferentes. A forma das barras é idêntica: a
# conversão é uma divisão pelo n da amostra, que não reordena nem reescala
# relativamente nada.
ROT_PERCENTUAL = "% do total de hospitais-ano"


def _rotular_mediana(ax, valor, *, dx=6, fmt=None):
    """Escreve o valor da mediana ao lado da sua linha vertical.

    A linha sozinha não diz quanto vale; o gestor precisa ler o número sem
    ter de cruzar com o eixo horizontal.
    """
    txt = fmt if fmt is not None else _fmt_val(valor)
    ax.annotate(f"mediana {txt}", (valor, 1), xycoords=("data", "axes fraction"),
                textcoords="offset points", xytext=(dx, -12),
                fontsize=10, color=COR_EVENTO, fontweight="bold")


def _pesos_pct(x):
    """Pesos que fazem cada barra do histograma valer o seu % do total.

    Cada observação entra com peso 100/n, de modo que a soma das barras é
    100% e a altura lida no eixo é a fatia da amostra que cai naquela faixa.
    """
    x = np.asarray(x)
    return np.full(x.shape[0], 100.0 / x.shape[0])


def _escala_percentual(pdf_vals, largura_bin):
    """Converte uma densidade ajustada para a escala percentual do histograma.

    Uma densidade integra 1; multiplicá-la pela largura do bin e por 100 põe a
    curva na mesma altura das barras em % do total. O n da amostra não entra:
    ele cancela entre a contagem esperada (pdf x n x largura) e o denominador
    da conversão para percentual — por isso a curva não precisa saber o
    tamanho da amostra, ao contrário do que ocorria na escala de contagem.
    """
    return np.asarray(pdf_vals) * largura_bin * 100.0


def _eixo_pct(ax):
    """Escreve o sinal de % nos rótulos do eixo vertical, com vírgula
    decimal, para a leitura não depender do rótulo do eixo."""
    ax.yaxis.set_major_formatter(FuncFormatter(
        lambda v, _p: (f"{v:.0f}%" if v >= 1 or v == 0
                       else f"{v:g}%".replace(".", ","))))


def _salvar(fig, nome: str):
    """Salva figura na pasta exclusiva da análise exploratória e fecha."""
    caminho = PASTA_FIG_AE / nome
    fig.savefig(caminho, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [FIG] {nome}")


def _tab(df: pd.DataFrame, nome: str, index=True):
    df.to_csv(base.PASTA_TABELAS / nome, index=index, encoding="utf-8-sig")
    print(f"  [TAB] {nome}")


def _fmt_val(v) -> str:
    """Número legível para anotações: milhar com ponto, sem notação
    científica."""
    if abs(v) >= 100:
        return f"{v:,.0f}".replace(",", ".")
    return f"{v:.3g}"


# ══════════════════════════════════════════════════════════════════════════════
# 0. CARGA E VERIFICAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

def carregar_e_verificar() -> pd.DataFrame:
    painel = pd.read_csv(base.PASTA_ANALISES / "painel_definitivo.csv",
                         encoding="utf-8-sig")
    n_cnes = painel["cnes"].nunique()
    n_obs = len(painel)
    anos_cnes = painel.groupby("cnes")["ano"].nunique()
    nan_mod = painel["modelo_gestao_proxy"].isna().sum()
    nan_cpx = painel["complexidade_estrutural"].isna().sum()
    print(f"[0] Painel carregado: {n_cnes} CNES, {n_obs} linhas, "
          f"anos por CNES min {anos_cnes.min()} max {anos_cnes.max()}, "
          f"NaN modelo_gestao_proxy {nan_mod}, "
          f"NaN complexidade_estrutural {nan_cpx}")
    # 289/3.179 desde a ETAPA F de 15/07/2026 (era 314/3.454)
    ok = (n_cnes == 289 and n_obs == 3179 and (anos_cnes == 11).all()
          and nan_mod == 0 and nan_cpx == 0)
    if not ok:
        raise SystemExit("[0] PAINEL NÃO CONFERE COM O ESPERADO. PARANDO.")
    print("[0] Verificação OK: 289 CNES, 3.179 observações, painel balanceado.")

    # Domínio da ocupação de UTI (Etapa 1, propagado ao documento em
    # 29/07/2026). A razão é INDEFINIDA onde `uti_sus = 0`, e no painel essas
    # 688 observações estavam como zero estrutural em vez de não-aplicável.
    # Hospital SEM UTI SUS contava como hospital com UTI 0% ocupada, e a
    # penalização era proporcional à fração de hospitais sem UTI de cada
    # categoria — daí a inversão do ordenamento entre categorias.
    #
    # A restrição vem de `dominio_ocupacao_uti.py`, não de coluna de painel:
    # é definição, não medição. `verificar_equivalencia` aborta se a função
    # divergir de `ocupacao_uti_valida` do `painel_segmentado.csv`, para que
    # as duas definições não voltem a andar separadas.
    dominio_ocupacao_uti.verificar_equivalencia(painel)
    painel["ocupacao_uti"] = dominio_ocupacao_uti.ocupacao_uti_valida(painel)
    print(f"[0] Domínio da ocupação de UTI aplicado: "
          f"{int(painel['ocupacao_uti'].notna().sum())} observações válidas, "
          f"{int(painel['ocupacao_uti'].isna().sum())} não-aplicáveis "
          f"(sem UTI SUS cadastrada).")

    # Ano parcial de UTI (31/07/2026). A ocupação da base é
    # `100 * diarias_uti / (uti_sus * 365)`: o denominador é o ano CHEIO e o
    # numerador, o que o hospital de fato gerou. Quando a UTI SUS abre (ou
    # fecha) no meio do ano, o numerador cobre meio ano contra um ano inteiro
    # de capacidade, e a ocupação medida é artefato de calendário. O painel é
    # balanceado no HOSPITAL, o que fecha o caso análogo do hospital que abriu
    # em julho; não é balanceado na UTI, e 29 CNES oscilam entre ter e não ter.
    #
    # A definição canônica é `estimacao.marcar_uti_ano_parcial`, com a
    # auditoria em `analises/auditar_uti_ano_parcial.py`. Reproduzida aqui em
    # quatro linhas, e não importada, para não fazer a camada exploratória
    # depender da camada de estimação, que vem depois dela no pipeline; a
    # equivalência entre as duas foi conferida observação a observação.
    d = painel.sort_values(["cnes", "ano"])
    tem_uti = d["uti_sus"].fillna(0) > 0
    ant = tem_uti.groupby(d["cnes"]).shift(1)
    prox = tem_uti.groupby(d["cnes"]).shift(-1)
    painel["uti_ano_parcial"] = ((tem_uti & (ant == False))       # noqa: E712
                                 | (tem_uti & (prox == False))    # noqa: E712
                                 ).reindex(painel.index)
    n_parcial = int(painel.loc[painel["ocupacao_uti"].notna(),
                               "uti_ano_parcial"].sum())
    print(f"[0] Ano parcial de UTI marcado: {n_parcial} observações de "
          f"abertura ou encerramento, entre as válidas.")

    # porte FIXO por CNES: mediana de total_leitos com os cortes oficiais
    # (até 50 HPP; 51 a 150 médio; 151 a 500 grande; acima de 500 especial).
    # O rótulo anual porte_hospital oscila com o cadastro do SIH (68
    # observações de hospitais médios apareciam como HPP em anos isolados)
    # e por isso não é usado nos cortes desta análise.
    med_leitos = painel.groupby("cnes")["total_leitos"].median()

    def _porte(leitos):
        if leitos <= 50:
            return "HPP"
        if leitos <= 150:
            return "Médio Porte"
        if leitos <= 500:
            return "Grande Porte"
        return "Especial"

    painel["porte_fixo"] = painel["cnes"].map(med_leitos.apply(_porte))
    contagem_porte = (painel.groupby("cnes")["porte_fixo"].first()
                      .value_counts().to_dict())
    print(f"[0] Porte fixo por CNES (mediana de leitos, cortes 50/150/500): "
          f"{contagem_porte}")
    return painel


# ══════════════════════════════════════════════════════════════════════════════
# 1. UNIVARIADA
# ══════════════════════════════════════════════════════════════════════════════

def univariada(painel: pd.DataFrame):
    print("\n" + "=" * 70)
    print("[1] UNIVARIADA: 5 indicadores oficiais e 2 ocupações")
    print("=" * 70)

    linhas = []
    for c in IND7_FIG:
        x = painel[c].dropna()
        linha = {
            "indicador": c, "n": len(x), "media": x.mean(), "dp": x.std(),
            "min": x.min(), "p10": x.quantile(.10), "p25": x.quantile(.25),
            "p50": x.quantile(.50), "p75": x.quantile(.75),
            "p90": x.quantile(.90), "max": x.max(),
            "assimetria": x.skew(), "curtose": x.kurt(),
            "frac_zero": (x == 0).mean(),
        }
        if c in OCUPACOES:
            linha["frac_acima_100"] = (x > 100).mean()
        linhas.append(linha)
    tab = pd.DataFrame(linhas).set_index("indicador").round(4)
    _tab(tab, "tab_ae_univariada.csv")
    print(tab.to_string())

    for c in IND7_FIG:
        x = painel[c].dropna()
        _hist_univariada(c, x)


def _hist_univariada(c, x):
    """Histograma de um indicador, com janela de zoom e massa em zero
    destacada quando cada um dos dois faz diferença de leitura.

    O eixo vertical é o PERCENTUAL do total de hospitais-ano (Item 5 de
    27/07/2026, revisto em 29/07/2026; era contagem). A densidade saiu antes
    porque era lida como percentual pelo público gestor sem o ser; agora o
    eixo é percentual de verdade, com soma 100%. A curva KDE não voltou:
    ela vive na escala de densidade.

    O peso de cada observação é sempre 100/n sobre o total do indicador,
    inclusive quando os zeros saem para uma barra própria e quando a cauda
    sai para a barra de transbordo. Isso mantém a soma das barras em 100% e
    a altura de cada uma legível como fatia da amostra inteira.
    """
    fig, ax = plt.subplots(figsize=(7, 4.5))
    n_total = len(x)
    peso_un = 100.0 / n_total

    frac_zero = (x == 0).mean()
    destacar_zero = frac_zero > 0 and (frac_zero >= PISO_MASSA_ZERO
                                       or c in ZERO_SEMPRE_DESTACADO)
    corpo = x[x > 0] if destacar_zero else x

    limite, passo = JANELA_HIST.get(c, (None, None))
    if limite is None:
        limite = float(corpo.max())
    dentro = corpo[corpo <= limite]
    fora = corpo[corpo > limite]

    bordas = np.linspace(0, limite, 61)
    largura = bordas[1] - bordas[0]
    ax.hist(dentro, bins=bordas, color=COR_SERIE, edgecolor="white", lw=.3,
            weights=np.full(len(dentro), peso_un))

    # barra da massa em zero, destacada à esquerda do eixo contínuo
    esq = 0.0
    centro_zero = -3.4 * largura
    if destacar_zero:
        # A barra ALTA leva o rótulo deitado por dentro e cabe na margem
        # estreita. A barra BAIXA leva o rótulo por cima, e aí o texto é bem
        # mais largo que a barra: sem margem própria ele avança sobre as
        # primeiras barras do histograma, como avançou na mortalidade, cujos
        # zeros são 0,9%. Por isso a barra baixa desliza para a esquerda e a
        # margem se abre para caber o rótulo inteiro.
        rotulo_dentro = frac_zero * 100 >= 12
        centro_zero = (-3.4 if rotulo_dentro else -4.6) * largura
        esq = (-5.0 if rotulo_dentro else -7.5) * largura
        ax.bar(centro_zero, frac_zero * 100, width=1.9 * largura,
               color=COR_EVENTO, edgecolor="white", lw=.5, align="center")
        # o rótulo vai DENTRO da barra quando ela é alta: acima dela ele
        # disputaria espaço com o rótulo da mediana, que numa distribuição
        # inflada em zero cai sempre a poucos pixels da barra de zeros.
        if rotulo_dentro:
            ax.text(centro_zero, frac_zero * 50,
                    f"exatamente zero: {frac_zero:.1%}", rotation=90,
                    ha="center", va="center", fontsize=10, color="white",
                    fontweight="bold")
        else:
            ax.annotate(f"exatamente\nzero: {frac_zero:.1%}",
                        (centro_zero, frac_zero * 100),
                        textcoords="offset points", xytext=(0, 6),
                        ha="center", fontsize=9.5, color=COR_EVENTO,
                        fontweight="bold")
        ax.axvline(-1.4 * largura, color=COR_EIXO, lw=1.1, ls=(0, (2, 3)))

    # barra de transbordo, com o que a janela deixou de fora
    dir_ = limite
    if len(fora):
        dir_ = limite + 2.6 * largura
        ax.bar(limite + 1.4 * largura, len(fora) * peso_un,
               width=1.6 * largura, color=COR_SERIE, alpha=.55,
               edgecolor=COR_APOIO, lw=.7, hatch="//", align="center")
        ax.axvline(limite + .5 * largura, color=COR_EIXO, lw=1,
                   ls=(0, (2, 3)))
        ax.annotate(f"acima de {_fmt_val(limite)}\n{len(fora)} obs "
                    f"({len(fora) / n_total:.1%})\nmáx {_fmt_val(x.max())}",
                    (limite + 1.4 * largura, len(fora) * peso_un),
                    textcoords="offset points", xytext=(0, 6),
                    ha="center", fontsize=9, color=COR_APOIO)
    else:
        ax.annotate(f"máx {_fmt_val(x.max())}", (x.max(), 0),
                    textcoords="offset points", xytext=(-4, 8),
                    ha="right", fontsize=10, color="#52514e")

    med_v, media_v = x.median(), x.mean()
    for valor, cor, estilo, lw in ((med_v, COR_EVENTO, "dashed", 1.4),
                                   (media_v, COR_APOIO, "dotted", 1.0)):
        if valor <= limite:
            ax.axvline(valor, color=cor, lw=lw, ls=estilo)
    if med_v <= limite:
        _rotular_mediana(ax, med_v)
    if c in OCUPACOES and limite >= 100:
        ax.axvline(100, color=COR_EVENTO, lw=1, ls=":")

    linhas_nota = [(f"média {_fmt_val(media_v)} (pontilhada)", COR_APOIO)]
    if frac_zero > 0 and not destacar_zero:
        linhas_nota.append((f"massa em zero: {frac_zero:.1%}", "#52514e"))
    if c in OCUPACOES:
        linhas_nota.append((f"acima de 100%: {(x > 100).mean():.1%}",
                            "#52514e"))
    # O destaque alaranjado dos anos de abertura e encerramento de UTI saiu
    # daqui em 04/08/2026, a pedido de João. Eram 30 observações (1,2%)
    # ocupando uma linha de legenda e uma cor extra na figura mais lida da
    # Seção 2, para um efeito que a Seção 13 mede em 0,06 erro-padrão: o
    # gasto de atenção do leitor não pagava o que a marcação informava. A
    # marcação em si continua sendo calculada em `carregar_e_verificar`, sai
    # no log da execução e é reestimada por inteiro na bateria de calendário
    # da Seção 13, que é onde quem audita vai procurá-la.
    for i, (txt, cor) in enumerate(linhas_nota):
        ax.text(.97, .95 - .07 * i, txt, transform=ax.transAxes,
                ha="right", va="top", fontsize=10.5, color=cor)

    ax.set_xlim(esq, dir_ + (0 if len(fora) else largura * .5))
    # folga no topo para os rótulos das barras destacadas não baterem no título
    ax.margins(y=.18)
    ax.set_ylim(bottom=0)
    if passo is not None:
        marcas = np.arange(0, limite + passo * .5, passo)
        ax.set_xticks(marcas)
        ax.set_xticklabels([_fmt_val(v) for v in marcas], fontsize=9)
    elif destacar_zero:
        marcas = [t for t in ax.get_xticks() if 0 < t <= limite]
        ax.set_xticks([centro_zero] + list(marcas))
        ax.set_xticklabels(["0"] + [_fmt_val(v) for v in marcas], fontsize=9.5)
    ax.set_title(f"{ROT[c]}: distribuição (289 hospitais, 2015 a 2025)")
    ax.set_ylabel(ROT_PERCENTUAL)
    _eixo_pct(ax)
    fig.tight_layout()
    _salvar(fig, f"fig_ae_01_hist_{c}.png")


# ══════════════════════════════════════════════════════════════════════════════
# 2. DIAGNÓSTICO DISTRIBUCIONAL
# ══════════════════════════════════════════════════════════════════════════════

def distribucional_taxas(painel: pd.DataFrame):
    print("\n[2a] TAXAS: adequação de Beta/ZOIB (inflação em zero e em um)")
    taxas = ["mort_all", "pct_alta_complex"]        # A1: sem a ajustada
    linhas = []
    for c in taxas:
        x = painel[c].dropna()
        p0, p1 = (x == 0).mean(), (x >= 1).mean()
        interior = x[(x > 0) & (x < 1)]
        a, b, _, _ = stats.beta.fit(interior, floc=0, fscale=1)
        ll = np.sum(stats.beta.logpdf(interior, a, b))
        aic_beta = 4 - 2 * ll
        linhas.append({"indicador": c, "n": len(x),
                       "frac_zero": p0, "frac_um": p1,
                       "n_interior": len(interior),
                       "beta_a": a, "beta_b": b, "aic_beta_interior": aic_beta})
        # figura apenas para a alta complexidade: para as mortalidades a
        # comparação informativa (Beta única vs mistura) está na fig_ae_12
        if c == "pct_alta_complex":
            fig, ax = plt.subplots(figsize=(7, 4.5))
            cont, bordas, _ = ax.hist(interior, bins=60, color=COR_SERIE,
                                      edgecolor="white", lw=.3,
                                      label="dados em (0, 1)",
                                      weights=_pesos_pct(interior))
            larg = bordas[1] - bordas[0]
            grade = np.linspace(interior.min(), interior.quantile(.999), 400)
            # a Beta é uma densidade: reescalada para a altura das barras,
            # para o eixo continuar em % do total de hospitais-ano. O total,
            # aqui, é o interior de (0, 1) — os hospitais que fazem alguma
            # alta complexidade —, não as 3.179 observações do painel.
            ax.plot(grade,
                    _escala_percentual(stats.beta.pdf(grade, a, b), larg),
                    color=COR_APOIO,
                    lw=1.6, label=f"Beta({a:.2f}, {b:.1f})")
            med_int = interior.median()
            ax.axvline(med_int, color=COR_EVENTO, lw=1.4, ls="dashed")
            _rotular_mediana(ax, med_int, fmt=f"{med_int:.3f}")
            ax.set_yscale("log")
            # o teto do eixo é 100%: a curva Beta diverge perto de zero (o
            # expoente a é menor que 1) e, na escala percentual, subiria
            # acima de 100% do total, que é um número sem sentido de leitura.
            # Ela sai do gráfico pelo alto, o que já diz que continua subindo.
            ax.set_ylim(top=100)
            for txt, i in [(f"mediana do interior "
                            f"{interior.median():.3f}", 0),
                           (f"p90 do interior "
                            f"{interior.quantile(.9):.3f}", 1),
                           (f"zeros: {p0:.1%}   uns: {p1:.2%}", 2)]:
                ax.text(.97, .95 - .07 * i, txt, transform=ax.transAxes,
                        ha="right", va="top", fontsize=10.5, color="#52514e")
            ax.set_title(f"{ROT[c]}: ajuste Beta no interior, percentual "
                         f"em escala log", fontsize=11.5)
            ax.set_ylabel(f"{ROT_PERCENTUAL} (escala log)")
            _eixo_pct(ax)
            ax.legend(fontsize=10.5, loc="lower left")
            fig.tight_layout()
            _salvar(fig, f"fig_ae_02_beta_{c}.png")

    tab = pd.DataFrame(linhas).set_index("indicador").round(4)
    _tab(tab, "tab_ae_inflacao_taxas.csv")
    print(tab.to_string())


def _ajustar_mistura_beta(x, a1=1.2, b1=200.0, a2=3.0, b2=50.0, w=0.15):
    """Mistura de 2 Betas por máxima verossimilhança. Parâmetros em log e
    peso em logito, para otimizar sem restrições."""
    def nll(theta):
        la1, lb1, la2, lb2, lw = theta
        pa1, pb1, pa2, pb2 = np.exp([la1, lb1, la2, lb2])
        pw = 1 / (1 + np.exp(-lw))
        dens = (pw * stats.beta.pdf(x, pa1, pb1)
                + (1 - pw) * stats.beta.pdf(x, pa2, pb2))
        return -np.sum(np.log(np.clip(dens, 1e-300, None)))
    theta0 = np.array([np.log(a1), np.log(b1), np.log(a2), np.log(b2),
                       np.log(w / (1 - w))])
    res = minimize(nll, theta0, method="Nelder-Mead",
                   options={"maxiter": 20000, "xatol": 1e-8, "fatol": 1e-8})
    la1, lb1, la2, lb2, lw = res.x
    return (dict(a1=np.exp(la1), b1=np.exp(lb1), a2=np.exp(la2),
                 b2=np.exp(lb2), w=1 / (1 + np.exp(-lw))),
            -res.fun, res.success)


def distribucional_mistura_mortalidade(painel: pd.DataFrame):
    """Remodela a mortalidade: a Beta única subestima o pico perto de zero
    porque o painel mistura duas subpopulações. Ajusta mistura de 2 Betas
    e mostra que as componentes correspondem a hospitais reais de baixo
    óbito estrutural (maternidades e especializados) versus os demais."""
    print("\n[2a bis] MORTALIDADE REMODELADA: mistura de 2 Betas e "
          "decomposição por subpopulação real")

    linhas, ajustes = [], {}
    for c in ["mort_all"]:                          # A1: sem a ajustada
        x = painel[c][(painel[c] > 0) & (painel[c] < 1)].to_numpy()
        a, b, _, _ = stats.beta.fit(x, floc=0, fscale=1)
        aic1 = 4 - 2 * np.sum(stats.beta.logpdf(x, a, b))
        par, ll2, ok = _ajustar_mistura_beta(x)
        aic2 = 10 - 2 * ll2
        m1 = par["a1"] / (par["a1"] + par["b1"])
        m2 = par["a2"] / (par["a2"] + par["b2"])
        linhas.append({"indicador": c, "n_interior": len(x),
                       "beta_unica_a": a, "beta_unica_b": b,
                       "aic_beta_unica": aic1, "convergiu": ok,
                       "w_comp1": par["w"], "a1": par["a1"], "b1": par["b1"],
                       "media_comp1": m1, "a2": par["a2"], "b2": par["b2"],
                       "media_comp2": m2, "aic_mistura": aic2,
                       "ganho_aic": aic1 - aic2})
        ajustes[c] = (x, (a, b), par)
        print(f"  {c}: Beta única AIC {aic1:,.0f}; mistura com peso "
              f"{par['w']:.3f} (média {m1:.4f}) e {1 - par['w']:.3f} "
              f"(média {m2:.4f}), AIC {aic2:,.0f}, ganho "
              f"{aic1 - aic2:,.0f}")

    med = painel.groupby("cnes")["mort_all"].median()
    baixo = med[med < 0.02].index
    sub_b = painel[painel["cnes"].isin(baixo)]
    print(f"  Subpopulação de baixo óbito estrutural (mediana do CNES < 2%): "
          f"{len(baixo)} CNES, {len(sub_b)} observações")
    tipos = (sub_b.groupby("cnes")["tipo_hospital"]
             .agg(lambda s: s.mode().iloc[0]).value_counts())
    print("  Composição por tipo_hospital: "
          + "; ".join(f"{t}: {n}" for t, n in tipos.items()))

    grupos = {}
    for nome, mascara in [("baixo óbito", painel["cnes"].isin(baixo)),
                          ("demais", ~painel["cnes"].isin(baixo))]:
        xg = painel.loc[mascara, "mort_all"]
        xg = xg[(xg > 0) & (xg < 1)].to_numpy()
        ag, bg, _, _ = stats.beta.fit(xg, floc=0, fscale=1)
        grupos[nome] = (xg, ag, bg)
        print(f"  Beta do grupo {nome}: Beta({ag:.2f}, {bg:.1f}), média "
              f"{ag / (ag + bg):.4f}, n={len(xg)}")

    tab = pd.DataFrame(linhas).set_index("indicador").round(4)
    _tab(tab, "tab_ae_mistura_mortalidade.csv")

    rotulos_pan = {c: ROT[c] for c in ["mort_all"]}   # A1: sem a ajustada
    for c in ["mort_all"]:
        x, (a, b), par = ajustes[c]
        fig, ax = plt.subplots(figsize=(7, 4.5))
        cont, bordas, _ = ax.hist(x, bins=60, color=COR_SERIE,
                                  edgecolor="white", lw=.3,
                                  label="dados em (0, 1)",
                                  weights=_pesos_pct(x))
        larg = bordas[1] - bordas[0]
        grade = np.linspace(1e-4, np.quantile(x, .999), 400)
        # as duas curvas são densidades, reescaladas para a altura das barras
        ax.plot(grade,
                _escala_percentual(stats.beta.pdf(grade, a, b), larg),
                color=COR_MUTED,
                lw=1.3, ls="dashed", label=f"Beta única ({a:.2f}, {b:.1f})")
        mist = (par["w"] * stats.beta.pdf(grade, par["a1"], par["b1"])
                + (1 - par["w"]) * stats.beta.pdf(grade, par["a2"],
                                                  par["b2"]))
        ax.plot(grade, _escala_percentual(mist, larg),
                color=COR_APOIO, lw=1.9,
                label=f"mistura de 2 Betas (w={par['w']:.2f})")
        med_x = float(np.median(x))
        ax.axvline(med_x, color=COR_EVENTO, lw=1.4, ls="dashed")
        _rotular_mediana(ax, med_x, fmt=f"{med_x:.4f}")
        ax.set_title(f"{rotulos_pan[c]}: Beta única vs mistura de 2 Betas")
        ax.set_ylabel(ROT_PERCENTUAL)
        _eixo_pct(ax)
        ax.legend(fontsize=10.5)
        fig.tight_layout()
        _salvar(fig, f"fig_ae_12_mistura_{c}.png")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    x_all = ajustes["mort_all"][0]
    cont, bordas, _ = ax.hist(x_all, bins=60, color=COR_SERIE,
                              edgecolor="white", lw=.3,
                              label="dados em (0, 1)",
                              weights=_pesos_pct(x_all))
    larg = bordas[1] - bordas[0]
    grade = np.linspace(1e-4, np.quantile(x_all, .999), 400)
    n_tot = len(x_all)
    soma = np.zeros_like(grade)
    cores_g = {"baixo óbito": "#86b6ef", "demais": "#0d366b"}
    for nome, (xg, ag, bg) in grupos.items():
        # o peso do grupo continua sendo a sua fatia do total: na escala
        # percentual ele passa a ser lido direto na altura da curva, que é a
        # fatia da amostra inteira explicada por aquele grupo em cada faixa
        peso = len(xg) / n_tot
        comp = peso * stats.beta.pdf(grade, ag, bg)
        soma += comp
        ax.plot(grade, _escala_percentual(comp, larg),
                color=cores_g[nome], lw=1.6, ls="dashed",
                label=f"{nome} ({len(xg)} obs, média "
                      f"{ag / (ag + bg):.3f})")
    ax.plot(grade, _escala_percentual(soma, larg),
            color="#0b0b0b", lw=1.9, label="soma dos grupos")
    med_all = float(np.median(x_all))
    ax.axvline(med_all, color=COR_EVENTO, lw=1.4, ls="dashed")
    _rotular_mediana(ax, med_all, fmt=f"{med_all:.4f}")
    ax.set_title(f"Mortalidade geral: decomposição observável "
                 f"({len(baixo)} CNES de baixo óbito)")
    ax.set_ylabel(ROT_PERCENTUAL)
    _eixo_pct(ax)
    ax.legend(fontsize=10.5)
    fig.tight_layout()
    _salvar(fig, "fig_ae_12_decomposicao_mort_all.png")


CANDIDATAS_POS = [
    ("lognormal", "LogNormal", stats.lognorm),
    ("gama", "Gama", stats.gamma),
    ("fisk", "Log logística (Fisk)", stats.fisk),
    ("weibull", "Weibull", stats.weibull_min),
    ("gauss_inv", "Gaussiana inversa", stats.invgauss),
]


def _avaliar_candidatas(x):
    """AIC e r do QQ de cada família candidata (locação fixada em zero)."""
    res = {}
    for slug, nome, dist in CANDIDATAS_POS:
        params = dist.fit(x, floc=0)
        ll = np.sum(dist.logpdf(x, *params))
        _, (_, _, r) = stats.probplot(x, dist=dist, sparams=(params[0],))
        res[slug] = {"nome": nome, "aic": 4 - 2 * ll, "r_qq": r,
                     "shape": params[0]}
    return res


def _fig_qq(x, dist, shape, titulo, nome_arq, nota=None):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    stats.probplot(x, dist=dist, sparams=(shape,), plot=ax)
    ax.get_lines()[0].set(color=COR_SERIE, ms=2.5)
    ax.get_lines()[1].set(color=COR_APOIO, lw=1.3)
    ax.set_title(titulo, fontsize=11.5)
    ax.set_xlabel("Quantis teóricos")
    ax.set_ylabel("Valores ordenados")
    if nota:
        ax.text(.03, .97, nota, transform=ax.transAxes, ha="left",
                va="top", fontsize=10, color="#52514e")
    fig.tight_layout()
    _salvar(fig, nome_arq)


def distribucional_continuas(painel: pd.DataFrame):
    print("\n[2b] FATURAMENTO POR SAÍDA (SIH) E TMP: cinco famílias candidatas por "
          "AIC e QQ (locação em zero)")
    med_cnes = painel[painel["tmp"] > 0].groupby("cnes")["tmp"].median()
    longa = med_cnes[med_cnes > 20].index

    amostras = {
        # Item 1 (27/07/2026): o diagnóstico distribucional do faturamento
        # passa a usar a série REAL, para que o eixo em R$ do gráfico não
        # contradiga o resto do documento, que só imprime valores reais.
        "custo_real": painel.loc[painel["custo_real"] > 0, "custo_real"],
        "tmp": painel.loc[painel["tmp"] > 0, "tmp"],
        "tmp_sem_longa_perm": painel.loc[
            (painel["tmp"] > 0) & ~painel["cnes"].isin(longa), "tmp"],
    }
    linhas, aval = [], {}
    for var, x in amostras.items():
        aval[var] = _avaliar_candidatas(x.to_numpy())
        melhor = min(aval[var], key=lambda s: aval[var][s]["aic"])
        for slug, d in aval[var].items():
            linhas.append({"variavel": var, "familia": d["nome"],
                           "n": len(x), "aic": d["aic"], "r_qq": d["r_qq"],
                           "melhor_aic": slug == melhor})
    tab = pd.DataFrame(linhas).round(4)
    _tab(tab, "tab_ae_ajuste_continuas.csv", index=False)
    print(tab.to_string(index=False))
    print("  A log logística (Fisk) vence por AIC nas três amostras; no TMP "
          "sem a longa permanência o QQ dela fica quase perfeito.")

    dists = dict(lognormal=stats.lognorm, fisk=stats.fisk)
    NOTA_TETO = ("Achatamento no alto: teto de 30,5 dias\n"
                 "(longa permanência). Ver o QQ sem\n"
                 "longa permanência.")
    for var in ["custo_real", "tmp"]:
        x = amostras[var]
        fig, ax = plt.subplots(figsize=(7, 4.5))
        if var == "tmp":
            # Decisão 13-14/07/2026 (item 1.4): TMP em escala LINEAR com teto
            # fixo de 35 dias (a base trunca em ~30,5 — censura à direita
            # documentada no dossiê do item 1.4; 120 comprimiria o gráfico).
            # Nome do arquivo (hist_log) mantido por estabilidade das
            # referências no LaTeX; renomeação avaliada na Etapa 4.
            bins = np.linspace(0, 35, 60)
            ax.hist(x, bins=bins, color=COR_SERIE,
                    edgecolor="white", lw=.3, weights=_pesos_pct(x))
            ax.set_xlim(0, 35)
            ax.set_title(f"{ROT[var]}: distribuição em escala linear "
                         f"(teto fixo do eixo em 35 dias)", fontsize=11.5)
        else:
            bins = np.logspace(np.log10(x.min()), np.log10(x.max()), 60)
            ax.hist(x, bins=bins, color=COR_SERIE,
                    edgecolor="white", lw=.3, weights=_pesos_pct(x))
            ax.set_xscale("log")
            ax.xaxis.set_major_formatter(
                FuncFormatter(lambda v, _p: _fmt_val(v)))
            ax.set_title(f"{ROT[var]}: distribuição em eixo logarítmico "
                         f"(rótulos na unidade original)", fontsize=11.5)
        med_v = float(np.median(x))
        ax.axvline(med_v, color=COR_EVENTO, lw=1.4, ls="dashed")
        _rotular_mediana(ax, med_v)
        ax.set_ylabel(ROT_PERCENTUAL)
        _eixo_pct(ax)
        fig.tight_layout()
        _salvar(fig, f"fig_ae_03_hist_log_{var}.png")
        for slug in ["lognormal", "fisk"]:
            d = aval[var][slug]
            _fig_qq(x, dists[slug], d["shape"],
                    f"{ROT[var]}: QQ plot {d['nome']} "
                    f"(AIC {d['aic']:,.0f}, r={d['r_qq']:.4f})",
                    f"fig_ae_03_qq_{slug}_{var}.png",
                    nota=NOTA_TETO if var == "tmp" else None)
    d = aval["tmp_sem_longa_perm"]["fisk"]
    _fig_qq(amostras["tmp_sem_longa_perm"], stats.fisk, d["shape"],
            f"TMP sem longa permanência: QQ plot {d['nome']} "
            f"(r={d['r_qq']:.4f})",
            "fig_ae_03_qq_fisk_tmp_sem_longa_perm.png")


def distribucional_contagem(painel: pd.DataFrame):
    print("\n[2c] PRODUÇÃO (qtde): Poisson vs Binomial Negativa")
    linhas = []
    for c in ["qtde", "qtde_sem_covid"]:
        x = painel[c].dropna()
        razao_pool = x.var() / x.mean()
        por_ano = painel.groupby("ano")[c].agg(["mean", "var"])
        razao_ano = (por_ano["var"] / por_ano["mean"])
        intra = painel.groupby("cnes")[c].agg(["mean", "var"])
        razao_intra = (intra["var"] / intra["mean"]).median()
        linhas.append({"variavel": c, "media": x.mean(), "variancia": x.var(),
                       "razao_var_media_pool": razao_pool,
                       "razao_var_media_ano_min": razao_ano.min(),
                       "razao_var_media_ano_max": razao_ano.max(),
                       "razao_var_media_intra_cnes_mediana": razao_intra})
    tab = pd.DataFrame(linhas).set_index("variavel").round(2)
    _tab(tab, "tab_ae_sobredispersao_qtde.csv")
    print(tab.to_string())
    print("  Razão variância/média muito acima de 1 indica sobredispersão "
          "forte: Binomial Negativa, nunca Poisson.")


def _r_qq(x):
    """r do QQ normal da variável padronizada, com assimetria e curtose."""
    x = np.asarray(x, dtype=float)
    x = (x - x.mean()) / x.std()
    _, (_, _, r) = stats.probplot(x, dist="norm")
    return r, stats.skew(x), stats.kurtosis(x), x


def distribucional_condicional(painel: pd.DataFrame):
    """O QQ marginal mistura 289 hospitais heterogêneos; a estimação assume
    a distribuição CONDICIONAL (dadas as covariáveis e o efeito do hospital).
    Este bloco refaz os QQ sobre resíduos condicionais e quantifica a
    diferença, inclusive isolando a subpopulação de longa permanência."""
    print("\n[2d] AJUSTE MARGINAL vs CONDICIONAL (resíduos após covariáveis "
          "e efeitos fixos)")

    covs = ("C(ano) + C(faixa_barcelona) + C(porte_fixo) "
            "+ C(modelo_gestao_proxy)")
    casos, linhas = [], []

    def registrar(rotulo, valores, r2=np.nan, slug=None):
        r, ass, cur, z = _r_qq(valores)
        linhas.append({"caso": rotulo, "n": len(z), "r_qq": r,
                       "assimetria": ass, "curtose": cur, "r2_modelo": r2})
        if slug:
            casos.append((slug, rotulo, z, r))

    d = painel.copy()
    d["y"] = np.log(d["custo_saida"])
    registrar("custo: log marginal", d["y"], slug="custo_marginal")
    m = smf.ols(f"y ~ {covs}", data=d).fit()
    registrar("custo: resíduo covariáveis", m.resid, m.rsquared)
    m = smf.ols("y ~ C(cnes) + C(ano)", data=d).fit()
    registrar("custo: resíduo EF hospital e ano", m.resid, m.rsquared,
              slug="custo_residuo_ef")

    t = painel[painel["tmp"] > 0].copy()
    t["y"] = np.log(t["tmp"])
    med_cnes = t.groupby("cnes")["tmp"].median()
    longa = med_cnes[med_cnes > 20].index
    n_obs_longa = int(t["cnes"].isin(longa).sum())
    print(f"  Subpopulação de longa permanência (TMP mediano > 20 dias): "
          f"{len(longa)} CNES, {n_obs_longa} observações")
    registrar("tmp: log marginal, painel completo", t["y"],
              slug="tmp_marginal")
    ag = t[~t["cnes"].isin(longa)]
    registrar(f"tmp: log marginal sem longa permanência "
              f"({ag['cnes'].nunique()} CNES)", ag["y"],
              slug="tmp_marginal_sem_longa_perm")
    m = smf.ols(f"y ~ {covs}", data=ag).fit()
    registrar("tmp: resíduo covariáveis, sem longa perm.", m.resid,
              m.rsquared)
    m = smf.ols("y ~ C(cnes) + C(ano)", data=ag).fit()
    registrar("tmp: resíduo EF, sem longa perm.", m.resid, m.rsquared,
              slug="tmp_residuo_ef")

    mo = painel[(painel["mort_all"] > 0) & (painel["mort_all"] < 1)].copy()
    mo["y"] = np.log(mo["mort_all"] / (1 - mo["mort_all"]))
    registrar("mortalidade: logito marginal", mo["y"],
              slug="mort_logito_marginal")
    m = smf.ols("y ~ C(cnes) + C(ano)", data=mo).fit()
    registrar("mortalidade: resíduo logito EF", m.resid, m.rsquared,
              slug="mort_logito_residuo_ef")

    tab = pd.DataFrame(linhas).set_index("caso").round(4)
    _tab(tab, "tab_ae_qq_condicional.csv")
    print(tab.to_string())
    print("  Leitura: o desajuste dos QQ é da marginal (mistura de "
          "hospitais), não da família condicional que a estimação assume.")

    for slug, rotulo, z, r in casos:
        fig, ax = plt.subplots(figsize=(7, 4.5))
        stats.probplot(z, dist="norm", plot=ax)
        ax.get_lines()[0].set(color=COR_SERIE, ms=2.5)
        ax.get_lines()[1].set(color=COR_APOIO, lw=1.3)
        ax.set_title(f"QQ normal, {rotulo} (r={r:.4f})", fontsize=11.5)
        ax.set_xlabel("Quantis teóricos")
        ax.set_ylabel("Valores ordenados")
        fig.tight_layout()
        _salvar(fig, f"fig_ae_11_qq_{slug}.png")


# ══════════════════════════════════════════════════════════════════════════════
# 3. POR CATEGORIA INSTITUCIONAL
# ══════════════════════════════════════════════════════════════════════════════

def _janela_violino(ax, serie: pd.Series, teto: float):
    """Recorta o eixo vertical do violino e presta contas do que ficou fora.

    O violino já foi estimado sobre a série inteira: esta função não descarta
    observação nenhuma nem redesenha a silhueta, apenas escolhe o trecho do
    eixo que a página mostra. O que fica acima do teto vira uma nota no
    canto superior direito, com quantas observações são, que fatia do total
    representam e qual é o máximo real, para que o recorte seja auditável a
    olho e ninguém leia a janela como se fosse o alcance dos dados.
    """
    fora = int((serie > teto).sum())
    ax.set_ylim(0, teto)
    if not fora:
        return
    pct = 100 * fora / len(serie)
    ax.annotate(f"↑ {fora} obs ({pct:.1f}%) acima de {_fmt_val(teto)}; "
                f"máx {_fmt_val(serie.max())}",
                xy=(.995, .985), xycoords="axes fraction",
                ha="right", va="top", fontsize=8.5, color=COR_ALERTA,
                path_effects=[pe.withStroke(linewidth=2.4, foreground="white")])


def por_categoria(painel: pd.DataFrame):
    print("\n" + "=" * 70)
    print("[3] POR CATEGORIA INSTITUCIONAL (modelo_gestao_proxy)")
    print("=" * 70)
    col = "modelo_gestao_proxy"

    contagem = painel.groupby(col)["cnes"].agg(
        hospital_ano="size", cnes_distintos="nunique").reindex(CATEGORIAS)
    print(contagem.to_string())
    print("  RESSALVA: Privado tem só 3 CNES; não é interpretável como "
          "efeito médio da categoria.")

    blocos = []
    for c in IND8_TAB:
        g = painel.groupby(col)[c]
        bloco = pd.DataFrame({
            ("n", c): g.count(), ("p25", c): g.quantile(.25),
            ("mediana", c): g.median(), ("p75", c): g.quantile(.75),
            ("iiq", c): g.quantile(.75) - g.quantile(.25),
            # A MÉDIA entra na tabela em 01/08/2026. A mediana descreve o
            # hospital típico da categoria, e é a medida certa para isso; mas
            # em indicadores inflados em zero, como a fração de alta
            # complexidade, ela descreve mal a CATEGORIA. O Filantrópico tem
            # mediana 0,0018 e média 0,0831: a mediana é o hospital do meio
            # de um grupo de 171 hospitais em que 37% não fazem alta
            # complexidade nenhuma, e a média é o que a rede faz. As duas
            # juntas são a informação; qualquer uma sozinha engana.
            ("media", c): g.mean(),
        })
        blocos.append(bloco)
    tab = pd.concat(blocos, axis=1).reindex(CATEGORIAS).round(4)
    tab.columns = [f"{c}_{e}" for e, c in tab.columns]
    _tab(tab, "tab_ae_por_categoria.csv")
    medianas = tab[[f"{c}_mediana" for c in IND8_TAB]]
    medianas.columns = IND8_TAB
    print("\nMedianas por categoria (todos os anos):")
    print(medianas.to_string())
    medias = tab[[f"{c}_media" for c in IND8_TAB]]
    medias.columns = IND8_TAB
    print("\nMédias por categoria (todos os anos):")
    print(medias.to_string())

    # AGREGADO da categoria: soma dos numeradores sobre soma dos
    # denominadores, que é a taxa da REDE e não a média das taxas dos seus
    # hospitais. É a leitura que responde "quanto desta rede é alta
    # complexidade", em que a Santa Casa de 60 leitos e o hospital de
    # referência de 800 pesam pelo que produzem, e não um voto cada.
    # Numeradores na base SEM COVID, a mesma dos indicadores oficiais, e o
    # faturamento deflacionado antes de somar (senão o agregado misturaria
    # reais de 2015 com reais de 2025).
    ac = painel["qtde_alta_complex"] - painel["qtde_alta_complex_covid"]
    ob = painel["qtde_obito_all"] - painel["qtde_obito_all_covid"]
    vl = painel["valor_sem_covid"] * painel["ano"].map(_fatores_ipca_2025())
    aux = painel[[col, "qtde_sem_covid", "dias_sem_covid",
                  "diarias_internacao", "diarias_uti", "leitos_sus",
                  "uti_sus"]].assign(_ac=ac, _ob=ob, _vl=vl)
    ag = aux.groupby(col)
    agregado = pd.DataFrame({
        "mort_all": ag["_ob"].sum() / ag["qtde_sem_covid"].sum(),
        "tmp": ag["dias_sem_covid"].sum() / ag["qtde_sem_covid"].sum(),
        "custo_real": ag["_vl"].sum() / ag["qtde_sem_covid"].sum(),
        "pct_alta_complex": ag["_ac"].sum() / ag["qtde_sem_covid"].sum(),
        "ocupacao_internacao": (100 * ag["diarias_internacao"].sum()
                                / (ag["leitos_sus"].sum() * 365)),
        "ocupacao_uti": (100 * ag["diarias_uti"].sum()
                         / (ag["uti_sus"].sum() * 365)),
        "share_alta_complex_rede": ag["_ac"].sum() / ac.sum(),
        "share_saidas_rede": (ag["qtde_sem_covid"].sum()
                              / painel["qtde_sem_covid"].sum()),
        "share_leitos_uti_rede": ag["uti_sus"].sum() / painel["uti_sus"].sum(),
    }).reindex(CATEGORIAS).round(4)
    _tab(agregado, "tab_ae_por_categoria_agregado.csv")
    print("\nAgregado da categoria (soma dos numeradores / soma dos "
          "denominadores):")
    print(agregado.to_string())

    # O PRIVADO SAI DOS VIOLINOS (04/08/2026, a pedido de João). São 3 CNES, e
    # o violino é uma estimativa de densidade: com três hospitais ela não
    # descreve grupo nenhum, e desenhá-la ao lado de quatro categorias de
    # dezenas a centenas de hospitais convida à comparação que a própria
    # legenda pedia para não fazer. Pior que isso, ela ESTICAVA O EIXO: no
    # faturamento a mediana do Privado é R$ 16.262 contra R$ 1.293 a R$ 1.438
    # das outras quatro, e as silhuetas que interessam ficavam achatadas
    # contra a base do gráfico.
    #
    # O Privado NÃO sai da análise: continua no painel, continua nas tabelas
    # por categoria e continua entrando em todos os modelos como controle de
    # absorção. O que sai é a figura, onde ele custa a leitura das outras
    # quatro e não entrega leitura própria. O texto da Seção 4 declara isso.
    cats_violino = [c for c in CATEGORIAS if c != "Privado"]

    for c in IND7_FIG:
        dados = painel.loc[painel[col].isin(cats_violino), [col, c]].dropna()
        if c in ("custo_saida", "custo_real"):
            dados = dados[dados[c] > 0]
        fig, ax = plt.subplots(figsize=(7.5, 4.8))
        # Paleta cheia (31/07/2026). Os violinos usavam a versão clara da
        # paleta só para o número da mediana, escrito por cima, não sumir no
        # preenchimento. O contraste agora vem de um contorno branco no texto
        # e das linhas de quartil em branco, o que libera o matiz saturado:
        # a silhueta ganha presença sem custar legibilidade ao número.
        sns.violinplot(data=dados, x=col, y=c, order=cats_violino,
                       hue=col, palette=CORES_CAT, legend=False,
                       cut=0, inner="quartile", linewidth=.9,
                       inner_kws=dict(color="white", linewidth=1.1),
                       density_norm="width", ax=ax)
        for corpo in ax.collections:
            corpo.set_edgecolor("white")
            corpo.set_linewidth(.9)
        if c in ("custo_saida", "custo_real"):
            # A escala log fica mesmo sem o Privado: quem estica o eixo aqui
            # não é a categoria, é a cauda de dentro de cada uma. O máximo do
            # painel é R$ 41.997 contra medianas na casa de R$ 1.300, e em
            # escala linear as quatro silhuetas viram um traço na base.
            ax.set_yscale("log")
        elif c in JANELA_VIOL:
            # Item 1.4 (13-14/07/2026) para o TMP: escala LINEAR, mantida.
            # Janela de leitura (01/08/2026) para os quatro indicadores em que
            # a cauda esticava o eixo e encolhia a silhueta.
            _janela_violino(ax, dados[c], JANELA_VIOL[c])
        medianas_cat = dados.groupby(col)[c].median().reindex(cats_violino)
        for i, v in enumerate(medianas_cat):
            if pd.notna(v):
                ax.annotate(_fmt_val(v), (i, v),
                            textcoords="offset points", xytext=(0, 6),
                            ha="center", fontsize=10, color="#0b0b0b",
                            fontweight="bold", zorder=6,
                            path_effects=[pe.withStroke(linewidth=2.6,
                                                        foreground="white")])
        ax.set_title(f"{ROT[c]} por categoria institucional", fontsize=11.5)
        ax.set_xlabel("")
        ax.set_ylabel(ROT[c], fontsize=10.5)
        ax.tick_params(axis="x", rotation=20, labelsize=10.5)
        fig.tight_layout()
        _salvar(fig, f"fig_ae_04_violino_{c}.png")

    _composicao_estrutural(painel, col)


def _composicao_estrutural(painel, col):
    """Do que é feito o hospital-ano típico de cada rede: UTI e alta
    complexidade, combinadas.

    Pedido de João em 04/08/2026. O documento comparava as redes indicador a
    indicador, e nunca dizia com que MATERIAL cada uma opera. A pergunta do
    gestor é anterior à do desempenho: quando alguém diz "OSS", está falando
    de que tipo de hospital?

    As duas perguntas são combinadas de propósito, e não postas lado a lado
    em dois gráficos. Ter UTI e fazer alta complexidade andam juntas — a UTI é
    retaguarda do procedimento complexo —, e é a COMBINAÇÃO que descreve o
    hospital: quem tem as duas é hospital de referência; quem não tem nenhuma
    das duas vive inteiramente de produção de não alta complexidade, e é o
    grupo em que a comparação entre redes praticamente não existe. Os quatro
    grupos são mutuamente exclusivos e somam 100% em cada rede, de modo que a
    barra inteira é a composição da categoria.

    A unidade é o HOSPITAL-ANO, e não o hospital: um hospital que habilita UTI
    no meio do período conta nos dois grupos, cada ano no seu, que é o retrato
    fiel de uma rede que se move.
    """
    d = painel.assign(
        _uti=painel["uti_sus"].fillna(0) > 0,
        _ac=painel["pct_alta_complex"].fillna(0) > 0)
    GRUPOS = [
        ("UTI e alta complexidade",  True,  True,  "#0d366b"),
        ("UTI, sem alta complexidade", True,  False, "#2a78d6"),
        ("Alta complexidade, sem UTI", False, True,  "#86b6ef"),
        ("Sem UTI e sem alta complexidade", False, False, "#d9d8d1"),
    ]
    comp = pd.DataFrame(
        {rot: (d[col][(d["_uti"] == u) & (d["_ac"] == a)]
               .value_counts().reindex(CATEGORIAS).fillna(0))
         for rot, u, a, _ in GRUPOS})
    n_cat = d[col].value_counts().reindex(CATEGORIAS)
    pct = (100 * comp.div(n_cat, axis=0)).round(1)
    _tab(pct.assign(n_hospital_ano=n_cat), "tab_ae_composicao_estrutural.csv")
    print("\nComposição estrutural do hospital-ano, por rede (% da rede):")
    print(pct.to_string())

    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    base = np.zeros(len(CATEGORIAS))
    for rot, _, _, cor in GRUPOS:
        v = pct[rot].values
        ax.barh(CATEGORIAS, v, left=base, color=cor, edgecolor="white",
                lw=.8, label=rot)
        for i, (largura, esq) in enumerate(zip(v, base)):
            # rótulo só onde a fatia comporta o número sem encavalar na vizinha
            if largura >= 7:
                ax.text(esq + largura / 2, i, f"{largura:.0f}%".replace(".", ","),
                        ha="center", va="center", fontsize=10,
                        fontweight="bold",
                        color="white" if cor != "#d9d8d1" else "#3a3936")
        base = base + v

    for i, cat in enumerate(CATEGORIAS):
        ax.text(101, i, f"n = {int(n_cat[cat]):,}".replace(",", "."),
                va="center", fontsize=9.5, color=COR_MUTED)
    ax.set_xlim(0, 118)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0", "25%", "50%", "75%", "100%"])
    ax.invert_yaxis()
    ax.set_xlabel("% dos hospitais-ano da rede")
    ax.set_title("Do que cada rede é feita: UTI e alta complexidade nos "
                 "hospitais-ano de 2015 a 2025", fontsize=11.5)
    ax.grid(axis="y", visible=False)
    ax.legend(frameon=False, fontsize=9.3, ncol=2,
              loc="upper center", bbox_to_anchor=(.5, -.13))
    fig.tight_layout()
    _salvar(fig, "fig_ae_04b_composicao_estrutural.png")


# ══════════════════════════════════════════════════════════════════════════════
# 4. POR COMPLEXIDADE E POR PORTE
# ══════════════════════════════════════════════════════════════════════════════

def _rotular_mediana_e_media(ax, medianas, medias):
    """Imprime o valor da mediana e o da média sem que os dois se sobreponham.

    O desenho antigo (até 31/07/2026) punha a mediana logo acima do topo da
    barra e a média ao lado do losango. Onde as duas quase coincidem, e é o
    caso na maior parte das faixas, os dois números caíam praticamente no
    mesmo ponto e ficavam ilegíveis. Aqui a mediana passa a ser impressa
    DENTRO da barra, o que desocupa a faixa acima do topo para o losango, e
    o rótulo da média é deslocado para o primeiro vão livre acima ou abaixo
    dele. A escolha é feita em pontos de tela, e não em unidades do
    indicador, porque é na tela que a colisão acontece: assim ela vale
    igual para o faturamento (centenas) e para a mortalidade (centésimos).
    """
    y0, y1 = ax.get_ylim()
    alcance = y1 - y0

    def _pontos(dy_dados):
        """Converte uma distância vertical em unidades dos dados para pontos."""
        base = ax.transData.transform((0, y0))[1]
        return ((ax.transData.transform((0, y0 + dy_dados))[1] - base)
                * 72 / ax.figure.dpi)

    # Alturas aproximadas, em pontos de tela. ALTURA é a caixa de um rótulo de
    # uma linha; RAIO é o meio-tamanho do losango da média, marcador de 54
    # pontos quadrados de área.
    ALTURA, RAIO = 11.0, 6.0

    for i, (med, media) in enumerate(zip(medianas, medias)):
        # a mediana só cabe dentro da barra se a barra for alta o bastante
        dentro = pd.notna(med) and (med - y0) > .14 * alcance
        # distância entre média e mediana convertida para pontos de tela
        sep = (_pontos(media - med)
               if (pd.notna(med) and pd.notna(media)) else None)

        # Onde o rótulo da mediana entra, em pontos abaixo do topo da barra.
        # O padrão é 15, e ele DESCE quando o losango da média cai justamente
        # nessa faixa (04/08/2026). Antes disso o número da mediana era
        # escrito em posição fixa, e na ocupação de UTI por porte a média
        # (75,6) fica dois pontos abaixo da mediana (77,6 no Grande Porte,
        # 78,8 no Especial): o losango pousava exatamente sobre o número.
        dy_med = -15.0
        if dentro and sep is not None:
            colide = (sep - RAIO < dy_med + ALTURA / 2
                      and sep + RAIO > dy_med - ALTURA / 2)
            if colide:
                dy_med = sep - RAIO - ALTURA / 2 - 2

        if pd.notna(med):
            if dentro:
                ax.annotate(_fmt_val(med), (i, med), textcoords="offset points",
                            xytext=(0, dy_med), ha="center", va="center",
                            fontsize=10.5, color="white", fontweight="bold",
                            zorder=5)
            else:
                ax.annotate(_fmt_val(med), (i, med), textcoords="offset points",
                            xytext=(0, 4), ha="center", va="bottom",
                            fontsize=10.5, color="#52514e", zorder=5)
        if pd.isna(media):
            continue
        # faixa (em pontos, relativa ao topo da barra) já tomada pela mediana
        faixa = ((dy_med - ALTURA / 2, dy_med + ALTURA / 2) if dentro
                 else (3, 16))
        if sep is None:
            sep = 0.0
        # A ordem dos candidatos segue a direção que AFASTA o rótulo da média
        # do da mediana. A ordem fixa anterior tentava sempre subir primeiro;
        # quando a média está logo ABAIXO da mediana numa barra alta, subir é
        # caminhar justamente para cima do número da mediana.
        lado = (1, -1) if (pd.isna(med) or media >= med) else (-1, 1)
        for dy in [s * d for d in (9, 21, 33) for s in lado]:
            # é a BANDA que o rótulo ocupa, e não o seu ponto de ancoragem,
            # que precisa ficar fora da faixa já tomada pela mediana
            topo = sep + dy + (ALTURA if dy > 0 else 0)
            base = sep + dy - (ALTURA if dy < 0 else 0)
            if base > faixa[1] + 3 or topo < faixa[0] - 3:
                break
        else:
            dy = faixa[1] + ALTURA + 12 - sep
        ax.annotate(_fmt_val(media), (i, media), textcoords="offset points",
                    xytext=(0, dy), ha="center",
                    va="bottom" if dy > 0 else "top",
                    fontsize=9.5, color=COR_ALERTA, zorder=6,
                    path_effects=[pe.withStroke(linewidth=2.4,
                                                foreground="white")])


def _painel_medianas_grupo(painel, col, ordem, rampa, prefixo_fig, nome_tab,
                           rotulo_grupo):
    g = painel.groupby(col)[IND8_TAB].median().reindex(ordem).round(4)
    med_grupo = painel.groupby(col)[IND8_TAB].mean().reindex(ordem).round(4)
    g.insert(0, "n_cnes", painel.groupby(col)["cnes"].nunique().reindex(ordem))
    _tab(g.join(med_grupo, rsuffix="_media"), nome_tab)
    print(f"\nMedianas por {col}:")
    print(g.to_string())
    print(f"\nMédias por {col}:")
    print(med_grupo.to_string())

    for c in IND7_FIG:
        fig, ax = plt.subplots(figsize=(7, 4.8))
        ax.bar([str(o) for o in ordem], g[c],
               color=rampa[:len(ordem)], edgecolor="white", lw=.5,
               label="mediana")
        # A média entra sobreposta (31/07/2026). Numa distribuição inflada em
        # zero, a mediana de um grupo pode ser zero enquanto boa parte dele é
        # positiva, e a barra sozinha é lida como "este grupo não faz". Onde
        # média e mediana se afastam, a distância é a própria informação:
        # ela mede a assimetria do grupo.
        ax.scatter(range(len(ordem)), med_grupo[c], marker="D", s=54,
                   color=COR_ALERTA, edgecolor="white", lw=.8, zorder=3,
                   label="média")
        ax.set_title(f"{ROT[c]}: mediana e média por {rotulo_grupo}")
        ax.set_ylabel("Mediana (barra) e média (losango)")
        ax.tick_params(axis="x", rotation=15, labelsize=10.5)
        ax.grid(axis="x", visible=False)
        # A legenda também sai da área de dados: no canto superior esquerdo
        # ela encostava no rótulo da média da primeira barra sempre que essa
        # barra era alta (caso da ocupação, em que todas são).
        ax.legend(frameon=False, fontsize=9.5, ncol=2,
                  loc="upper center", bbox_to_anchor=(.5, -.14))
        ax.margins(y=.20)
        _rotular_mediana_e_media(ax, g[c], med_grupo[c])
        fig.tight_layout()
        _salvar(fig, f"{prefixo_fig}_{c}.png")


def por_complexidade_e_porte(painel: pd.DataFrame):
    print("\n" + "=" * 70)
    print("[4] POR COMPLEXIDADE (faixa_barcelona) E POR PORTE")
    print("=" * 70)
    faixas = sorted(painel["faixa_barcelona"].unique())
    _painel_medianas_grupo(
        painel, "faixa_barcelona", faixas, RAMPA_5,
        "fig_ae_05_faixa", "tab_ae_por_faixa_barcelona.csv",
        "faixa Barcelona")
    ordem_porte = [p for p in ["Médio Porte", "Grande Porte", "Especial"]
                   if p in painel["porte_fixo"].unique()]
    print("  Porte: classificação FIXA por CNES (mediana de leitos, cortes "
          "50/150/500); o rótulo anual do SIH não é usado.")
    _painel_medianas_grupo(
        painel, "porte_fixo", ordem_porte, RAMPA_4[1:],
        "fig_ae_06_porte", "tab_ae_por_porte.csv",
        "porte hospitalar (classificação fixa)")
    _alcance_alta_complexidade(painel, ordem_porte)
    _media_complexidade(painel, ordem_porte)


def _alcance_alta_complexidade(painel, ordem_porte):
    """Três leituras da alta complexidade por porte, porque a mediana sozinha
    mente sobre o Médio Porte.

    A mediana da fração de alta complexidade no Médio Porte é ZERO, e a barra
    zerada é lida como "hospital de médio porte não faz alta complexidade".
    É falso, e por larga margem: 126 dos 159 hospitais médios do painel fazem
    alta complexidade em algum ano, e juntos somam 220 mil saídas de alta
    complexidade no período. O que a mediana diz é outra coisa, e bem mais
    modesta: que o hospital médio TÍPICO faz pouca, em muitos anos nenhuma.

    A distinção importa para gestor: "não faz" e "faz pouco" levam a decisões
    de rede opostas. As três leituras aqui separam alcance (quem faz),
    intensidade (quanto faz quem faz) e volume (quanto sai no agregado).
    """
    col, ind = "porte_fixo", "pct_alta_complex"
    linhas = []
    for p in ordem_porte:
        s = painel[painel[col] == p]
        faz = s[s[ind] > 0]
        linhas.append(dict(
            porte=p,
            n_cnes=s["cnes"].nunique(),
            n_obs=len(s),
            pct_cnes_que_faz=100 * faz["cnes"].nunique() / s["cnes"].nunique(),
            pct_obs_que_faz=100 * len(faz) / len(s),
            mediana_geral=s[ind].median(),
            media_geral=s[ind].mean(),
            mediana_entre_os_que_fazem=faz[ind].median(),
            saidas_alta_complex=int(s["qtde_alta_complex"].sum()),
        ))
    tab = pd.DataFrame(linhas).round(4)
    _tab(tab, "tab_ae_alcance_alta_complex.csv", index=False)
    print("\nAlcance da alta complexidade por porte:")
    print(tab.to_string(index=False))

    xs = np.arange(len(ordem_porte))
    cores = RAMPA_4[1:][:len(ordem_porte)]

    # (a) alcance: quem faz alguma vez, em hospitais e em hospitais-ano
    def _alcance(ax, corpo=10.8):
        b1 = ax.bar(xs - .19, tab["pct_cnes_que_faz"], .36, color=cores,
                    edgecolor="white", lw=.5, label="hospitais (algum ano)")
        b2 = ax.bar(xs + .19, tab["pct_obs_que_faz"], .36, color=cores,
                    alpha=.45, edgecolor="white", lw=.5, hatch="//",
                    label="hospitais-ano")
        for barras in (b1, b2):
            ax.bar_label(barras, fmt="%.1f%%", fontsize=9, padding=2,
                         color="#52514e")
        ax.set_xticks(xs)
        ax.set_xticklabels(ordem_porte, fontsize=10)
        ax.set_ylabel("% que faz alguma alta complexidade")
        ax.set_ylim(0, 132)
        ax.set_title("(a) Alcance: quem faz", fontsize=corpo)
        ax.legend(frameon=False, fontsize=8.8, loc="upper left")
        ax.grid(axis="x", visible=False)

    # (b) intensidade ENTRE os que fazem
    def _intensidade(ax, corpo=10.8):
        dados = [painel[(painel[col] == p) & (painel[ind] > 0)][ind].values
                 for p in ordem_porte]
        bp = ax.boxplot(dados, patch_artist=True, widths=.55, showfliers=True,
                        flierprops=dict(marker=".", ms=3, mfc=COR_MUTED,
                                        mec="none", alpha=.5),
                        medianprops=dict(color="white", lw=1.6))
        for caixa, cor in zip(bp["boxes"], cores):
            caixa.set(facecolor=cor, edgecolor="white", lw=.8)
        ax.set_xticklabels(ordem_porte, fontsize=10)
        ax.set_ylabel("Fração de alta complexidade")
        ax.set_title("(b) Intensidade: quanto faz quem faz", fontsize=corpo)
        ax.grid(axis="x", visible=False)

    # (c) volume absoluto no período
    def _volume(ax, corpo=10.8):
        barras = ax.bar(xs, tab["saidas_alta_complex"] / 1000, .62, color=cores,
                        edgecolor="white", lw=.5)
        ax.bar_label(barras,
                     labels=[f"{v/1000:,.0f} mil".replace(",", ".")
                             for v in tab["saidas_alta_complex"]],
                     fontsize=9.5, padding=2, color="#52514e")
        ax.set_xticks(xs)
        ax.set_xticklabels(ordem_porte, fontsize=10)
        ax.set_ylabel("Saídas de alta complexidade (mil)")
        ax.set_title("(c) Volume: quanto sai no agregado", fontsize=corpo)
        ax.margins(y=.16)
        ax.grid(axis="x", visible=False)

    TITULO = ("Alta complexidade por porte: a mediana zero do Médio Porte "
              "é 'faz pouco', não 'não faz'")
    paineis = [("a_alcance", _alcance), ("b_intensidade", _intensidade),
               ("c_volume", _volume)]

    fig, axes = plt.subplots(1, 3, figsize=(14.4, 4.5))
    for ax, (_, desenhar) in zip(axes, paineis):
        desenhar(ax)
    fig.suptitle(TITULO, y=1.02)
    fig.tight_layout()
    _salvar(fig, "fig_ae_06b_alcance_alta_complex.png")

    # Os três painéis também saem em arquivos próprios (01/08/2026). A tira
    # de três serve para ver o argumento inteiro de uma vez; publicada na
    # largura da mancha, porém, cada painel fica com um terço dela, e é nesse
    # tamanho que o rótulo de porcentagem em cima das barras deixa de ser
    # legível. O desenho é o mesmo: as duas versões chamam a mesma função.
    for nome, desenhar in paineis:
        fig, ax = plt.subplots(figsize=(8.2, 5.2))
        desenhar(ax, corpo=13)
        ax.set_title(f"{ax.get_title()}\n{TITULO}", fontsize=13)
        fig.tight_layout()
        _salvar(fig, f"fig_ae_06b_{nome}.png")


def _media_complexidade(painel, ordem_porte):
    """A outra ponta da complexidade: os 90% da produção que não são altos.

    Pedido de João em 01/08/2026. O documento descrevia em detalhe a alta
    complexidade, que é 9,9% das internações do painel, e não dizia nada
    sobre os outros 90,1%, que são o trabalho corrente da rede.

    O QUE O PAINEL PERMITE, E O QUE NÃO PERMITE. O painel guarda
    `qtde_alta_complex` e `qtde`; a diferença entre as duas é tudo o que não
    é alta complexidade. O campo COMPLEX do SIH, na origem, distingue "Alta
    complexidade" de "Média complexidade" e da atenção básica, mas o
    construtor do painel só acumulou a primeira. Separar a média da atenção
    básica exigiria reagregar as planilhas anuais brutas do SIH, que não
    estão no repositório. Por isso tudo aqui é rotulado como NÃO ALTA, e
    nunca como "média complexidade": seria afirmar uma separação que este
    dado não sustenta.

    A figura espelho da alta complexidade seria degenerada: 100% dos
    hospitais fazem produção não alta, em todo ano. As três leituras aqui
    são as que de fato informam: quanto cada porte DEPENDE da produção não
    alta, quantos hospitais vivem SÓ dela, e o volume que ela move.
    """
    col = "porte_fixo"
    ac = painel["qtde_alta_complex"] - painel["qtde_alta_complex_covid"]
    p = painel.assign(_ac=ac, _nao=painel["qtde_sem_covid"] - ac)

    linhas = []
    for porte in ordem_porte:
        s = p[p[col] == porte]
        por_h = s.groupby("cnes")["_ac"].max()
        linhas.append(dict(
            porte=porte,
            n_cnes=s["cnes"].nunique(),
            n_obs=len(s),
            pct_producao_nao_alta=100 * s["_nao"].sum() / s["qtde_sem_covid"].sum(),
            pct_cnes_so_nao_alta=100 * por_h.eq(0).mean(),
            n_cnes_so_nao_alta=int(por_h.eq(0).sum()),
            saidas_nao_alta=int(s["_nao"].sum()),
            fatia_da_nao_alta_do_painel=100 * s["_nao"].sum() / p["_nao"].sum(),
        ))
    tab = pd.DataFrame(linhas).round(4)
    _tab(tab, "tab_ae_media_complexidade.csv", index=False)
    print("\nProdução NÃO ALTA por porte (a outra ponta da complexidade):")
    print(tab.to_string(index=False))

    # perfil dos hospitais que nunca registram alta complexidade
    por_h_geral = p.groupby("cnes")["_ac"].max()
    so_nao = por_h_geral[por_h_geral.eq(0)].index
    perfil = p.assign(_so=p["cnes"].isin(so_nao)).groupby("_so").agg(
        n_cnes=("cnes", "nunique"), n_obs=("cnes", "size"),
        leitos=("leitos_sus", "median"), saidas=("qtde_sem_covid", "median"),
        tmp=("tmp", "median"), mort=("mort_all", "median"),
        custo=("custo_real", "median"), ocup=("ocupacao_internacao", "median"))
    perfil.index = ["faz alta em algum ano", "nunca faz alta"]
    _tab(perfil.round(4), "tab_ae_perfil_so_nao_alta.csv")
    print("\nPerfil de quem nunca registra alta complexidade:")
    print(perfil.round(3).to_string())

    xs = np.arange(len(ordem_porte))
    cores = RAMPA_4[1:][:len(ordem_porte)]
    # O subtítulo comum aos três painéis ("A produção que não é alta
    # complexidade: 90,1% das internações do painel") saiu em 04/08/2026, a
    # pedido de João: repetia em cada figura publicada isolada um número que o
    # texto da seção já traz, e roubava uma linha do título de cada uma. A
    # tira de três painéis continua com um título só, agora escrito direto no
    # suptitle e sem duplicar nos arquivos individuais.
    TIRA = ("A produção que não é alta complexidade: 90,1% das internações "
            "do painel")

    def _dependencia(ax, corpo=10.8):
        barras = ax.bar(xs, tab["pct_producao_nao_alta"], .62, color=cores,
                        edgecolor="white", lw=.5)
        ax.bar_label(barras, fmt="%.1f%%", fontsize=9.5, padding=2,
                     color="#52514e")
        ax.set_xticks(xs)
        ax.set_xticklabels(ordem_porte, fontsize=10)
        ax.set_ylabel("% da produção que não é alta complexidade")
        ax.set_ylim(0, 108)
        ax.set_title("(a) Dependência: quanto do porte é a produção de não "
                     "alta complexidade", fontsize=corpo)
        ax.grid(axis="x", visible=False)

    def _exclusividade(ax, corpo=10.8):
        barras = ax.bar(xs, tab["pct_cnes_so_nao_alta"], .62, color=cores,
                        edgecolor="white", lw=.5)
        ax.bar_label(barras,
                     labels=[f"{v:.1f}%\n({n} hosp.)" for v, n in
                             zip(tab["pct_cnes_so_nao_alta"],
                                 tab["n_cnes_so_nao_alta"])],
                     fontsize=9.5, padding=2, color="#52514e")
        ax.set_xticks(xs)
        ax.set_xticklabels(ordem_porte, fontsize=10)
        ax.set_ylabel("% dos hospitais que nunca fazem alta complexidade")
        ax.set_title("(b) Exclusividade: quem vive só de produção de não "
                     "alta complexidade", fontsize=corpo)
        ax.margins(y=.22)
        ax.grid(axis="x", visible=False)

    def _volume(ax, corpo=10.8):
        barras = ax.bar(xs, tab["saidas_nao_alta"] / 1e6, .62, color=cores,
                        edgecolor="white", lw=.5)
        ax.bar_label(barras,
                     labels=[f"{v/1e6:,.1f} mi".replace(".", ",")
                             for v in tab["saidas_nao_alta"]],
                     fontsize=9.5, padding=2, color="#52514e")
        ax.set_xticks(xs)
        ax.set_xticklabels(ordem_porte, fontsize=10)
        ax.set_ylabel("Internações não alta complexidade (milhões)")
        ax.set_title("(c) Volume: quanto isso move em onze anos",
                     fontsize=corpo)
        ax.margins(y=.18)
        ax.grid(axis="x", visible=False)

    paineis = [("a_dependencia", _dependencia),
               ("b_exclusividade", _exclusividade), ("c_volume", _volume)]

    fig, axes = plt.subplots(1, 3, figsize=(14.4, 4.5))
    for ax, (_, desenhar) in zip(axes, paineis):
        desenhar(ax)
    fig.suptitle(TIRA, y=1.02)
    fig.tight_layout()
    _salvar(fig, "fig_ae_06c_media_complexidade.png")

    for nome, desenhar in paineis:
        fig, ax = plt.subplots(figsize=(8.2, 5.2))
        desenhar(ax, corpo=13)
        fig.tight_layout()
        _salvar(fig, f"fig_ae_06c_{nome}.png")


# ══════════════════════════════════════════════════════════════════════════════
# 5. TENDÊNCIA TEMPORAL
# ══════════════════════════════════════════════════════════════════════════════

def _banda_covid(ax):
    ax.axvspan(2019.5, 2021.5, color=COR_BANDA, zorder=0)


def tendencia_temporal(painel: pd.DataFrame):
    print("\n" + "=" * 70)
    print("[5] TENDÊNCIA TEMPORAL (medianas por ano; faixa cinza em 2020 e 2021)")
    print("=" * 70)
    anos = sorted(painel["ano"].unique())

    grp = painel.groupby("ano")[IND8_TAB]
    med, q25, q75 = grp.median(), grp.quantile(.25), grp.quantile(.75)
    _tab(med.round(4), "tab_ae_mediana_ano.csv")
    print(med.round(4).to_string())

    for c in IND7_FIG:
        fig, ax = plt.subplots(figsize=(7, 4.5))
        _banda_covid(ax)
        ax.plot(anos, med[c], "o", ls="solid", color=COR_SERIE, lw=1.8, ms=4)
        ax.fill_between(anos, q25[c], q75[c], alpha=.18, color=COR_SERIE)
        s = med[c]
        ax.annotate(_fmt_val(s.max()), (s.idxmax(), s.max()),
                    textcoords="offset points", xytext=(0, 8), ha="center",
                    fontsize=10, color=COR_APOIO, fontweight="bold")
        ax.annotate(_fmt_val(s.min()), (s.idxmin(), s.min()),
                    textcoords="offset points", xytext=(0, -12), ha="center",
                    fontsize=10, color=COR_APOIO, fontweight="bold")
        if s.idxmax() != anos[-1] and s.idxmin() != anos[-1]:
            ax.annotate(_fmt_val(s.iloc[-1]), (anos[-1], s.iloc[-1]),
                        textcoords="offset points", xytext=(6, 0),
                        fontsize=10, color="#52514e")
        ax.set_title(f"{ROT[c]}: mediana e IIQ por ano "
                     f"(faixa cinza: 2020 e 2021)", fontsize=11.5)
        ax.set_xlabel("Ano")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        _salvar(fig, f"fig_ae_07_tendencia_{c}.png")

    med_cat = (painel.groupby(["ano", "modelo_gestao_proxy"])[IND8_TAB]
               .median().round(4))
    _tab(med_cat, "tab_ae_mediana_ano_categoria.csv")

    SEM_PRIVADO = ("custo_saida", "custo_real", "pct_alta_complex")
    for c in IND7_FIG:
        fig, ax = plt.subplots(figsize=(7.5, 4.8))
        _banda_covid(ax)
        cats_plot = [cat for cat in CATEGORIAS
                     if not (c in SEM_PRIVADO and cat == "Privado")]
        for cat in cats_plot:
            s = med_cat.xs(cat, level=1)[c]
            estilo = {"lw": 1, "ls": "dotted"} if cat == "Privado" \
                else {"lw": 1.7, "ls": "solid"}
            ax.plot(s.index, s.values, marker=MARCADORES[cat], ms=4.5,
                    color=CORES_CAT[cat], label=cat, **estilo)
        extra = ("; Privado omitido por escala, ver tabela"
                 if c in SEM_PRIVADO else "")
        ax.set_title(f"{ROT[c]}: mediana anual por categoria "
                     f"(faixa cinza: 2020 e 2021{extra})", fontsize=11.5)
        ax.set_xlabel("Ano")
        ax.tick_params(axis="x", rotation=45)
        titulo_leg = (None if c in SEM_PRIVADO
                      else "Privado: n=3, pontilhado")
        ax.legend(fontsize=9.5, title=titulo_leg, title_fontsize=9.5)
        fig.tight_layout()
        _salvar(fig, f"fig_ae_08_categoria_{c}.png")


def comparativo_atendimento_conversores(painel: pd.DataFrame):
    """
    Item 1.6 (decisão de 14/07/2026): "comparativo de atendimento" definido
    como PERFIL DE COMPLEXIDADE ATENDIDA (pct_alta_complex) ano a ano, lado a
    lado com mortalidade geral, TMP e faturamento real, para o Conjunto
    Hospitalar Sorocaba (2081695, conversão 2019) e, como contraste, o
    Pérola Byington (2078287, conversão 2023). complexidade_estrutural e
    faixa_barcelona são FIXAS por CNES — por construção não medem mudança de
    composição; o único sinal temporal disponível é pct_alta_complex.
    """
    ALVOS = {2081695: "Conjunto Hospitalar Sorocaba (conversão 2019)",
             2078287: "Pérola Byington (conversão 2023)"}
    COLS = ["pct_alta_complex", "mort_all", "tmp", "custo_real"]

    sub = painel[painel["cnes"].isin(ALVOS)].sort_values(["cnes", "ano"])
    tab = sub[["cnes", "ano"] + COLS + ["qtde_sem_covid"]].round(4)
    _tab(tab, "tab_ae_comparativo_atendimento.csv", index=False)
    print("\n[6b] Comparativo de atendimento (item 1.6) — perfil de "
          "complexidade ao lado dos desfechos:")
    print(tab.to_string(index=False))

    fig, axes = plt.subplots(len(COLS), 2, figsize=(12, 3.1 * len(COLS)),
                             sharex=True)
    for j, (cnes, nome) in enumerate(ALVOS.items()):
        d = sub[sub["cnes"] == cnes]
        for i, c in enumerate(COLS):
            ax = axes[i, j]
            _banda_covid(ax)
            ax.plot(d["ano"], d[c], marker="o", ms=4, lw=1.7, color=COR_SERIE)
            ax.axvline(CONVERSOES[cnes] - .5, color=COR_EVENTO, lw=1.2,
                       ls="dashed")
            if i == 0:
                ax.set_title(nome, fontsize=11)
            ax.set_ylabel(ROT[c], fontsize=9)
            ax.tick_params(labelsize=9)
    axes[-1, 0].set_xlabel("Ano")
    axes[-1, 1].set_xlabel("Ano")
    fig.suptitle("Comparativo de atendimento dos conversores: o perfil de "
                 "complexidade (1ª linha) mudou junto com os desfechos?\n"
                 "Linha tracejada: entrada na gestão OSS; faixa cinza: "
                 "2020 e 2021", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, .94])
    _salvar(fig, "fig_ae_17_comparativo_atendimento_conversores.png")


# ══════════════════════════════════════════════════════════════════════════════
# 6. ESTUDO DE EVENTOS DOS CONVERSORES
# ══════════════════════════════════════════════════════════════════════════════

def estudo_eventos(painel: pd.DataFrame):
    print("\n" + "=" * 70)
    print("[6] ESTUDO DE EVENTOS: 5 conversores de Direta para OSS")
    print("=" * 70)
    anos = sorted(painel["ano"].unique())
    med_cat = painel.groupby(["ano", "modelo_gestao_proxy"])[IND5_FIG].median()

    nomes = {}
    for cnes in CONVERSOES:
        sub = painel[painel["cnes"] == cnes]
        nome = sub["nome_fantasia"].dropna()
        nomes[cnes] = nome.iloc[-1] if len(nome) else str(cnes)
        municipio = sub["municipio"].dropna().iloc[-1]
        print(f"  CNES {cnes} ({nomes[cnes]}, {municipio}): conversão "
              f"proxy em {CONVERSOES[cnes]}; categorias por ano: "
              + ", ".join(f"{a}={m}" for a, m in
                          zip(sub['ano'], sub['modelo_gestao_proxy'])))

    linhas_pp = []
    for cnes, ano_conv in CONVERSOES.items():
        sub = painel[painel["cnes"] == cnes].set_index("ano")
        for c in IND5_FIG:
            fig, ax = plt.subplots(figsize=(7, 4.6))
            for cat in ["Direta", "OSS"]:
                s = med_cat.xs(cat, level=1)[c]
                ax.plot(s.index, s.values, ls="dashed", lw=1.1,
                        marker=MARCADORES[cat], ms=3.5,
                        color=CORES_CAT[cat], alpha=.75,
                        label=f"mediana {cat}")
            ax.plot(anos, sub[c].reindex(anos), "o", ls="solid",
                    color="#0b0b0b", lw=1.7, ms=4, label="hospital")
            ax.axvline(ano_conv - .5, color=COR_EVENTO, lw=1.3, ls="dashed")
            ax.set_title(f"{nomes[cnes]} (CNES {cnes})\n{ROT[c]} "
                         f"(entrada na gestão OSS em {ano_conv})",
                         fontsize=11)
            ax.set_xlabel("Ano")
            ax.tick_params(axis="x", rotation=45)
            # A legenda sai de dentro da área de dados (01/08/2026). Com
            # loc="best" ela ia parar sobre o traço do próprio hospital, que
            # é a linha que a figura existe para mostrar; abaixo do eixo,
            # numa única fileira, ela não tem como cobrir nada.
            ax.legend(fontsize=9.5, ncol=3, frameon=False,
                      loc="upper center", bbox_to_anchor=(.5, -.22))
            fig.tight_layout()
            _salvar(fig, f"fig_ae_09_conversor_{cnes}_{c}.png")
            pre = sub.loc[sub.index < ano_conv, c].median()
            pos = sub.loc[sub.index >= ano_conv, c].median()
            linhas_pp.append({"cnes": cnes, "hospital": nomes[cnes],
                              "ano_conversao": ano_conv, "indicador": c,
                              "mediana_pre": pre, "mediana_pos": pos,
                              "variacao_relativa":
                                  (pos / pre - 1) if pre else np.nan})

    tab = pd.DataFrame(linhas_pp).round(4)
    _tab(tab, "tab_ae_conversores_pre_pos.csv", index=False)
    print("\nComparação antes vs depois (medianas por hospital):")
    for cnes in [2081695, 2078287]:
        print(f"\n  CNES {cnes} ({nomes[cnes]}), conversão {CONVERSOES[cnes]}:")
        t = tab[tab["cnes"] == cnes][["indicador", "mediana_pre",
                                      "mediana_pos", "variacao_relativa"]]
        print(t.to_string(index=False))
    print("\n  Conversores de 2025 (2082225, 2091755, 2750511): apenas 1 ano "
          "de janela pós, sem leitura de tendência.")


# ══════════════════════════════════════════════════════════════════════════════
# 7. CORRELAÇÕES
# ══════════════════════════════════════════════════════════════════════════════

def correlacoes(painel: pd.DataFrame):
    print("\n" + "=" * 70)
    print("[7] CORRELAÇÕES DE SPEARMAN (complexidade: versão estrutural, "
          "salvaguarda de circularidade)")
    print("=" * 70)
    # a exclusão da mortalidade ajustada já vem de IND7 desde A1 (29/07/2026);
    # este mapa a omitia sozinho desde antes, pelo motivo abaixo, que continua
    # sendo a razão de ela ter saído do documento inteiro.
    cols = list(IND7) + ["complexidade_estrutural"]
    print("  Mortalidade ajustada fora do documento (A1): correlações "
          "idênticas às da mortalidade geral (Spearman de 1,000 entre as "
          "duas).")
    corr = painel[cols].corr(method="spearman").round(3)
    _tab(corr, "tab_ae_correlacao_spearman.csv")
    print(corr.to_string())

    cmap = LinearSegmentedColormap.from_list(
        "azul_seq", ["#ffffff", "#cde2fb", "#5598e7", "#0d366b"])
    fig, ax = plt.subplots(figsize=(9, 7.5))
    rotulos = [ROT[c] for c in cols]
    im = ax.imshow(corr.values, cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks(range(len(cols)), rotulos, rotation=40, ha="right",
                  fontsize=10.5)
    ax.set_yticks(range(len(cols)), rotulos, fontsize=10.5)
    for a in range(len(cols)):
        for b in range(len(cols)):
            v = corr.values[a, b]
            ax.text(b, a, f"{v:.2f}", ha="center", va="center", fontsize=10,
                    color="white" if v > .6 else "#0b0b0b")
    ax.grid(visible=False)
    fig.colorbar(im, ax=ax, shrink=.8, label="Spearman")
    ax.set_title("Análise Exploratória: correlações de Spearman "
                 "(observações de hospital e ano)")
    fig.tight_layout()
    _salvar(fig, "fig_ae_10_correlacao_spearman.png")


# ══════════════════════════════════════════════════════════════════════════════
# 8. QUALIDADE DE DADOS
# ══════════════════════════════════════════════════════════════════════════════

def qualidade_dados(painel: pd.DataFrame):
    print("\n" + "=" * 70)
    print("[8] QUALIDADE DE DADOS E DECISÕES PARA A MODELAGEM")
    print("=" * 70)

    print("\n[8a] OCUPAÇÃO (escala percentual)")
    for c in OCUPACOES:
        x = painel[c].dropna()
        print(f"  {c}: n={len(x)}, acima de 100%: {(x > 100).mean():.1%} "
              f"({(x > 100).sum()} casos), zeros: {(x == 0).mean():.1%} "
              f"({(x == 0).sum()} casos), máximo: {x.max():.1f}%")
    cols_diag = ["cnes", "ano", "municipio", "ocupacao_uti", "diarias_uti",
                 "uti_total", "total_leitos"]
    extremos = painel.nlargest(15, "ocupacao_uti")[cols_diag].round(1)
    _tab(extremos, "tab_ae_ocupacao_uti_extremos.csv", index=False)
    print("\n  15 maiores extremos de ocupacao_uti (diagnóstico de "
          "denominador):")
    print(extremos.to_string(index=False))
    print("\n  RECOMENDAÇÃO: modelar a razão com Gama ou LogNormal; UTI com "
          "componente para zeros (modelo em duas partes) ou amostra restrita "
          "a hospitais com UTI; winsorizar a cauda superior.")

    print("\n[8b] DENOMINADORES FRÁGEIS EM 2020 E 2021 (qtde_sem_covid < 30)")
    frag = painel[(painel["ano"].isin([2020, 2021]))
                  & (painel["qtde_sem_covid"] < 30)]
    cols_f = ["cnes", "ano", "municipio", "qtde", "qtde_covid",
              "qtde_sem_covid", "mort_all", "tmp", "custo_saida"]
    frag_tab = frag[cols_f].sort_values(["qtde_sem_covid", "cnes"]).round(4)
    _tab(frag_tab, "tab_ae_frageis_2020_2021.csv", index=False)
    print(f"  {len(frag)} observações de hospital e ano no biênio com "
          f"qtde_sem_covid < 30:")
    print(frag_tab.to_string(index=False))
    caso_tmp0 = painel[(painel["tmp"] == 0) & painel["tmp"].notna()]
    print(f"\n  Casos com tmp igual a zero: "
          f"{list(zip(caso_tmp0['cnes'], caso_tmp0['ano']))}")

    print("\n[8c] INVENTÁRIO DE OUTLIERS E DE FALTANTES")
    linhas = []
    for c in IND7_FIG:
        x = painel[c].dropna()
        q1, q3 = x.quantile(.25), x.quantile(.75)
        iiq = q3 - q1
        lim_sup, lim_inf = q3 + 3 * iiq, q1 - 3 * iiq
        linhas.append({"indicador": c, "lim_sup_3iiq": lim_sup,
                       "n_acima": (x > lim_sup).sum(),
                       "n_abaixo": (x < max(lim_inf, 0)).sum(),
                       "p99": x.quantile(.99), "max": x.max()})
    out = pd.DataFrame(linhas).set_index("indicador").round(4)
    _tab(out, "tab_ae_outliers.csv")
    print(out.to_string())

    falt = painel.isna().sum()
    falt = falt[falt > 0].sort_values(ascending=False).rename("n_faltantes")
    _tab(falt.to_frame(), "tab_ae_faltantes.csv")
    print("\n  Faltantes por coluna (apenas colunas com algum NaN):")
    print(falt.to_string())


# ══════════════════════════════════════════════════════════════════════════════
# 9. COMPLEMENTOS PARA A ESTIMAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

def composicao_suporte(painel: pd.DataFrame):
    """Composição cruzada categoria × faixa Barcelona e categoria × porte,
    em nível de CNES, para checar o suporte comum das comparações."""
    print("\n[3b] COMPOSIÇÃO E SUPORTE COMUM (nível de CNES; conversores "
          "contados na categoria modal)")
    base_cnes = painel.groupby("cnes").agg(
        categoria=("modelo_gestao_proxy", lambda s: s.mode().iloc[0]),
        faixa=("faixa_barcelona", "first"),
        porte=("porte_fixo", "first"))

    ordem_porte = [p for p in ["HPP", "Médio Porte", "Grande Porte",
                               "Especial"] if p in base_cnes["porte"].unique()]
    dimensoes = [
        ("faixa", sorted(base_cnes["faixa"].unique()), "faixa Barcelona",
         "fig_ae_13_composicao_categoria_faixa.png",
         "tab_ae_composicao_categoria_faixa.csv"),
        ("porte", ordem_porte, "porte hospitalar",
         "fig_ae_13_composicao_categoria_porte.png",
         "tab_ae_composicao_categoria_porte.csv"),
    ]
    cmap = LinearSegmentedColormap.from_list(
        "azul_seq", ["#ffffff", "#cde2fb", "#5598e7", "#0d366b"])
    for dim, ordem, rotulo, nome_fig, nome_tab in dimensoes:
        ct = (pd.crosstab(base_cnes["categoria"], base_cnes[dim])
              .reindex(index=CATEGORIAS, columns=ordem).fillna(0).astype(int))
        _tab(ct, nome_tab)
        print(f"\nCNES por categoria × {rotulo}:")
        print(ct.to_string())
        vazias = [(cat, col) for cat in ct.index for col in ct.columns
                  if ct.loc[cat, col] == 0]
        print(f"  Células vazias (sem suporte): {vazias if vazias else 'nenhuma'}")

        fig, ax = plt.subplots(figsize=(7, 4.8))
        im = ax.imshow(ct.values, cmap=cmap, vmin=0)
        ax.set_xticks(range(len(ct.columns)), [str(c) for c in ct.columns],
                      fontsize=10.5)
        ax.set_yticks(range(len(ct.index)), ct.index, fontsize=10.5)
        vmax = ct.values.max()
        for a in range(ct.shape[0]):
            for b in range(ct.shape[1]):
                v = ct.values[a, b]
                ax.text(b, a, str(v), ha="center", va="center", fontsize=11.5,
                        fontweight="bold" if v == 0 else "normal",
                        color="white" if v > .6 * vmax else "#0b0b0b")
        ax.grid(visible=False)
        fig.colorbar(im, ax=ax, shrink=.8, label="Nº de CNES")
        ax.set_title(f"Composição: CNES por categoria × {rotulo}", fontsize=11.5)
        fig.tight_layout()
        _salvar(fig, nome_fig)


def anatomia_zeros(painel: pd.DataFrame):
    """Fração de zeros por grupo: prepara o componente logístico do ZOIB."""
    print("\n[2e] ANATOMIA DOS ZEROS (insumo do componente inflacionado "
          "do ZOIB)")
    faixas = sorted(painel["faixa_barcelona"].unique())
    ordem_porte = [p for p in ["Médio Porte", "Grande Porte", "Especial"]
                   if p in painel["porte_fixo"].unique()]
    dimensoes = [("modelo_gestao_proxy", CATEGORIAS, "categoria"),
                 ("faixa_barcelona", faixas, "faixa Barcelona"),
                 ("porte_fixo", ordem_porte, "porte")]
    linhas = []
    for var in ["pct_alta_complex", "mort_all"]:
        for col, ordem, rotulo in dimensoes:
            g = painel.groupby(col)[var]
            fz = g.apply(lambda s: (s == 0).mean()).reindex(ordem)
            for grupo, v in fz.items():
                linhas.append({"variavel": var, "dimensao": rotulo,
                               "grupo": grupo, "frac_zero": v,
                               "n": int(g.count().reindex(ordem)[grupo])})
    tab = pd.DataFrame(linhas).round(4)
    _tab(tab, "tab_ae_zeros_por_grupo.csv", index=False)
    print(tab.to_string(index=False))

    graficos = [
        ("pct_alta_complex", "modelo_gestao_proxy", CATEGORIAS,
         "categoria", "fig_ae_15_zeros_pct_alta_categoria.png"),
        ("pct_alta_complex", "faixa_barcelona", faixas,
         "faixa Barcelona", "fig_ae_15_zeros_pct_alta_faixa.png"),
        ("mort_all", "modelo_gestao_proxy", CATEGORIAS,
         "categoria", "fig_ae_15_zeros_mort_categoria.png"),
    ]
    for var, col, ordem, rotulo, nome_fig in graficos:
        fz = (painel.groupby(col)[var]
              .apply(lambda s: (s == 0).mean()).reindex(ordem))
        fig, ax = plt.subplots(figsize=(7, 4.5))
        barras = ax.bar([str(o) for o in ordem], fz.values * 100,
                        color=RAMPA_5[:len(ordem)], edgecolor="white", lw=.5)
        ax.bar_label(barras, labels=[f"{v * 100:.1f}%" for v in fz.values],
                     fontsize=10.5, padding=2, color="#52514e")
        ax.set_title(f"{ROT[var]}: fração de zeros por {rotulo}", fontsize=11.5)
        ax.set_ylabel("Observações iguais a zero (%)")
        ax.tick_params(axis="x", rotation=15, labelsize=10.5)
        ax.grid(axis="x", visible=False)
        fig.tight_layout()
        _salvar(fig, nome_fig)


def custo_real(painel: pd.DataFrame):
    """Série do faturamento por saída corrigida pelo IPCA para preços de 2025."""
    print("\n[5b] FATURAMENTO POR SAÍDA (SIH) EM PREÇOS DE 2025 (IPCA dez/dez, IBGE)")
    fat = _fatores_ipca_2025()
    sub = painel.copy()
    sub["custo_real_2025"] = sub["custo_saida"] * sub["ano"].map(fat)
    med = (sub.groupby("ano")[["custo_saida", "custo_real_2025"]]
           .median().round(2))
    med["fator_ipca"] = pd.Series(fat).round(4)
    _tab(med, "tab_ae_custo_real_ano.csv")
    print(med.to_string())

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    _banda_covid(ax)
    ax.plot(med.index, med["custo_saida"], marker="o", ms=4, ls="dashed",
            lw=1.4, color="#5598e7", label="Nominal")
    ax.plot(med.index, med["custo_real_2025"], marker="s", ms=4, ls="solid",
            lw=1.8, color="#0d366b", label="Preços de 2025 (IPCA)")
    for serie in ["custo_saida", "custo_real_2025"]:
        ax.annotate(_fmt_val(med[serie].iloc[0]),
                    (med.index[0], med[serie].iloc[0]),
                    textcoords="offset points", xytext=(-2, 8), ha="left",
                    fontsize=10, color="#52514e")
        ax.annotate(_fmt_val(med[serie].iloc[-1]),
                    (med.index[-1], med[serie].iloc[-1]),
                    textcoords="offset points", xytext=(4, 0),
                    fontsize=10, color="#52514e")
    ax.set_title("Faturamento por saída: mediana anual nominal vs corrigida "
                 "pelo IPCA (faixa cinza: 2020 e 2021)", fontsize=11.5)
    ax.set_xlabel("Ano")
    ax.set_ylabel("R$ por saída")
    ax.legend(fontsize=10.5)
    fig.tight_layout()
    _salvar(fig, "fig_ae_07_tendencia_custo_saida_real.png")


def variancia_within_between(painel: pd.DataFrame):
    """Decomposição da variância em entre e dentro de hospitais: quanta
    variação resta para os efeitos fixos identificarem."""
    print("\n[7b] VARIÂNCIA ENTRE vs DENTRO DE HOSPITAIS (relevância para "
          "efeitos fixos)")
    linhas = []
    for c in IND7:
        sub = painel[["cnes", c]].dropna()
        desvio = sub[c] - sub.groupby("cnes")[c].transform("mean")
        var_within = desvio.var()
        var_between = sub.groupby("cnes")[c].mean().var()
        total = var_within + var_between
        linhas.append({"indicador": c, "var_between": var_between,
                       "var_within": var_within,
                       "pct_within": var_within / total,
                       "icc_between": var_between / total})
    tab = pd.DataFrame(linhas).set_index("indicador").round(4)
    _tab(tab, "tab_ae_variancia_within_between.csv")
    print(tab.to_string())

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ordenado = tab.sort_values("pct_within")
    barras = ax.barh([ROT[c] for c in ordenado.index],
                     ordenado["pct_within"] * 100, color=COR_SERIE,
                     edgecolor="white", lw=.5)
    ax.bar_label(barras, labels=[f"{v * 100:.0f}%"
                                 for v in ordenado["pct_within"]],
                 fontsize=10.5, padding=3, color="#52514e")
    ax.set_title("Parcela da variância que ocorre dentro do hospital "
                 "ao longo do tempo", fontsize=11.5)
    ax.set_xlabel("Variância dentro do hospital (%)")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    _salvar(fig, "fig_ae_14_variancia_within.png")


def funnel_mortalidade(painel: pd.DataFrame):
    """Funil da mortalidade contra o volume de saídas: separa ruído
    binomial de hospital pequeno de sinal real."""
    print("\n[8d] FUNIL DA MORTALIDADE vs VOLUME (limites binomiais)")
    sub = painel[(painel["qtde_sem_covid"] > 0)
                 & painel["mort_all"].notna()].copy()
    obitos = sub["mort_all"] * sub["qtde_sem_covid"]
    p = obitos.sum() / sub["qtde_sem_covid"].sum()
    n_grade = np.logspace(np.log10(sub["qtde_sem_covid"].min()),
                          np.log10(sub["qtde_sem_covid"].max()), 300)
    ep = np.sqrt(p * (1 - p) / n_grade)

    ep_obs = np.sqrt(p * (1 - p) / sub["qtde_sem_covid"])
    sub["z"] = (sub["mort_all"] - p) / ep_obs
    fora_sup = sub[sub["z"] > 3.09]
    fora_inf = sub[sub["z"] < -3.09]
    print(f"  Mortalidade agregada (ponderada): {p:.4f}")
    print(f"  Fora do limite de 99,8%: {len(fora_sup)} acima "
          f"({fora_sup['cnes'].nunique()} CNES) e {len(fora_inf)} abaixo "
          f"({fora_inf['cnes'].nunique()} CNES), de {len(sub)} observações")
    extremos = (pd.concat([fora_sup.nlargest(10, "z"),
                           fora_inf.nsmallest(10, "z")])
                [["cnes", "ano", "municipio", "qtde_sem_covid", "mort_all",
                  "z"]].round(4))
    _tab(extremos, "tab_ae_funnel_extremos.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.scatter(sub["qtde_sem_covid"], sub["mort_all"], s=8, alpha=.25,
               color=COR_SERIE, edgecolors="none")
    ax.axhline(p, color=COR_APOIO, lw=1.4,
               label=f"média ponderada {p:.3f}")
    for z_lim, ls, rotulo in [(1.96, "dashed", "limites de 95%"),
                              (3.09, "dotted", "limites de 99,8%")]:
        ax.plot(n_grade, p + z_lim * ep, ls=ls, lw=1.1, color=COR_EVENTO,
                label=rotulo)
        ax.plot(n_grade, np.clip(p - z_lim * ep, 0, None), ls=ls, lw=1.1,
                color=COR_EVENTO)
    ax.set_xscale("log")
    ax.set_title("Funil: mortalidade geral vs volume de saídas "
                 "(observações de hospital e ano)", fontsize=11.5)
    ax.set_xlabel("Saídas no ano (escala log)")
    ax.set_ylabel("Mortalidade geral")
    ax.legend(fontsize=9.5)
    fig.tight_layout()
    _salvar(fig, "fig_ae_16_funnel_mortalidade.png")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("ANÁLISE EXPLORATÓRIA: PAINEL DE HOSPITAIS SUS/SP, 2015 A 2025")
    print("=" * 70)
    base.configurar_diretorios()
    PASTA_FIG_AE.mkdir(parents=True, exist_ok=True)
    print(f"[DIR] Figuras desta etapa em: {PASTA_FIG_AE}")

    painel = carregar_e_verificar()
    # Item 1.5: coluna de APRESENTAÇÃO em preços de 2025 (não altera modelos)
    painel["custo_real"] = (painel["custo_saida"]
                            * painel["ano"].map(_fatores_ipca_2025()))

    univariada(painel)
    print("\n" + "=" * 70)
    print("[2] DIAGNÓSTICO DISTRIBUCIONAL PARA A ESCOLHA DE FAMÍLIA")
    print("=" * 70)
    distribucional_taxas(painel)
    distribucional_mistura_mortalidade(painel)
    distribucional_continuas(painel)
    distribucional_contagem(painel)
    distribucional_condicional(painel)
    anatomia_zeros(painel)
    por_categoria(painel)
    composicao_suporte(painel)
    por_complexidade_e_porte(painel)
    tendencia_temporal(painel)
    custo_real(painel)
    estudo_eventos(painel)
    comparativo_atendimento_conversores(painel)
    correlacoes(painel)
    variancia_within_between(painel)
    qualidade_dados(painel)
    funnel_mortalidade(painel)

    print("\nCONCLUÍDO. Figuras das famílias fig_ae_01 a fig_ae_17 (uma "
          "imagem por gráfico) em analises/figuras_analise_exploratoria; "
          "tabelas tab_ae_* em analises/tabelas.")


if __name__ == "__main__":
    main()
