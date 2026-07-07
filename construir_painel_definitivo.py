# -*- coding: utf-8 -*-
"""
construir_painel_definitivo.py
==============================
Construção do PAINEL ANALÍTICO DEFINITIVO — Hospitais SUS/SP, 2015-2025.

Implementa os critérios formalizados em "Critérios de Construção do Painel
Analítico Definitivo" (criterios_construcao_painel.md), na seguinte ordem:

    ETAPA A  Exclusão por tipo de estabelecimento
             - hospitais dia          (tipo_hospital cód 62)
             - psiquiátricos          (tipo_hospital cód 07 + especializacao 006)
             - CAPS                   (tipo_hospital cód 70)
             - maternidades (especializacao 005) são MANTIDAS
    ETAPA B  Porte fixo: mediana de total_leitos por CNES nos anos com
             produção; mediana > 50 → hospital inteiro incluído;
             mediana <= 50 → hospital inteiro excluído
    ETAPA C1 Exclusão de hospitais de campanha COVID (unidades criadas
             exclusivamente para a pandemia)
    ETAPA C2 Remoção de procedimentos COVID (código 999) dos hospitais que
             permanecem: indicadores *_sem_covid (não remove linhas)
    ETAPA D  Painel balanceado: apenas CNES com produção em TODOS os anos
    LOG      Auditoria por etapa (tab_auditoria_filtros.csv +
             tab_auditoria_cnes_removidos.csv + tab_auditoria_revisao_manual.csv)

DECISÕES DE IMPLEMENTAÇÃO (a validar com a equipe):
    D-A. tipo_hospital/especializacao variam entre anos para o mesmo CNES.
         A classificação usa o valor MODAL (mais frequente) por CNES, com
         desempate pelo ano mais recente — coerente com a filosofia da
         mediana de leitos (robustez a anos-anomalia). CNES com série
         inconsistente de tipo são listados no log de revisão manual.
    D-C1. O critério formal identifica campanha via class_assistencial em
         {Público, Hospital COVID, Sem Fins Lucrativos} + nome com
         COVID/CAMPANHA. Nos dados reais, porém, hospitais de campanha
         inequívocos aparecem também sob Público Municipal, Direta e
         DESATIVADO. Regra implementada (ampliada):
             candidato = nome contém COVID/CAMPANHA/CORONA (sem acento)
                         OU tipo_hospital/class_assistencial = "Hospital COVID"
             excluído  = candidato E produção restrita a 2020-2021
                         ("criado exclusivamente para COVID", §3 dos critérios)
         Candidatos com produção FORA de 2020-2021 (hospitais regulares
         rebatizados durante a pandemia) NÃO são excluídos — vão para o log
         de revisão manual. O log também marca quais excluídos não atendem
         ao critério literal de classe, para rastreabilidade.
    D-C2. Ocupação (internação/UTI) NÃO tem versão sem-COVID: o denominador
         (leitos × 365) e as diárias vêm prontos do resumo SIH e não são
         decomponíveis por procedimento. Mantida a versão original com nota.

COMPLEXIDADE (§4 dos critérios — DUAS versões, NENHUMA descartada):
    complexidade_estrutural : Pontuação Barcelona pura (fixa por CNES)
    complexidade_pond_mort  : Pontuação Barcelona × (1 + mortalidade relativa
                              do hospital-ano frente à mediana estadual do ano)
    >>> SALVAGUARDA DE CIRCULARIDADE (ver comentário na função
    >>> calcular_escores_complexidade): em modelos com MORTALIDADE como
    >>> variável DEPENDENTE, usar SEMPRE complexidade_estrutural.

MODELO DE GESTÃO: modelo_gestao_proxy (cópia de class_assistencial) é a
    DEFINIÇÃO ADOTADA de modelo de gestão do projeto (decisão jul/2026). Não
    desmembra Autarquia nem PPP e mantém "Público Municipal" como dummy
    única. O crosswalk institucional definitivo foi avaliado e CANCELADO;
    não há pendência de crosswalk.

USO:
    python construir_painel_definitivo.py

Pré-requisito: analises/painel_hospital_ano.csv (ou .parquet) já gerado por
analise_sih.py. O re-stream dos numeradores COVID (2020-2021) roda uma única
vez e fica em cache (analises/covid_numeradores_2020_2021.csv).
"""

import re
import unicodedata

import numpy as np
import openpyxl
import pandas as pd

# Reutiliza caminhos, constantes e utilitários já validados do pipeline base.
# ATENÇÃO: o import já embrulha sys.stdout em UTF-8 (feito em analise_sih);
# NÃO re-embrulhar aqui — o wrapper antigo seria coletado pelo GC e fecharia
# o buffer subjacente, quebrando todos os prints.
import analise_sih as base

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES DESTA ETAPA
# ══════════════════════════════════════════════════════════════════════════════

PAINEL_DEFINITIVO_CSV     = base.PASTA_ANALISES / "painel_definitivo.csv"
PAINEL_DEFINITIVO_PARQUET = base.PASTA_ANALISES / "painel_definitivo.parquet"
CACHE_COVID_NUM           = base.PASTA_ANALISES / "covid_numeradores_2020_2021.csv"
TAB_AUD_FILTROS           = base.PASTA_TABELAS  / "tab_auditoria_filtros.csv"
TAB_AUD_REMOVIDOS         = base.PASTA_TABELAS  / "tab_auditoria_cnes_removidos.csv"
TAB_AUD_REVISAO           = base.PASTA_TABELAS  / "tab_auditoria_revisao_manual.csv"
LEIAME                    = base.PASTA_ANALISES / "LEIAME_painel_definitivo.txt"

CORTE_LEITOS      = 50            # mediana > 50 inclui (critérios §2.2)
# Janela dos hospitais de campanha. Verificado em 2026-07: nenhum CNES
# excluído em C1 dependia de 2019 (a anomalia de cadastro do CNES 8478,
# rotulado "Hospital COVID" em 2019, cai no log de revisão manual de todo
# modo), então a janela segue o documento de critérios: o biênio pandêmico.
ANOS_CAMPANHA     = {2020, 2021}
CLASSES_CRITERIO_LITERAL = {"Público", "Hospital COVID", "Sem Fins Lucrativos"}

# Decisão da equipe (João, 2026-07-01, revista após confirmação externa):
# o HU-UFSCar (5586348) é hospital PÚBLICO FEDERAL administrado pela Ebserh
# (Empresa Brasileira de Serviços Hospitalares/MEC) — o rótulo "Privado" do
# SIH NÃO corresponde à sua natureza jurídica real. Ainda assim, a equipe
# decidiu MANTÊ-LO AGRUPADO em "Privado" no proxy de modelo de gestão, por
# conveniência estatística (eleva o grupo de n=2 para n=3). É escolha de
# agrupamento pragmático registrada, não erro de classificação; qualquer
# leitura do coeficiente da categoria deve considerar essa mistura.
# O mecanismo abaixo permanece para futuras decisões de supressão de rótulo.
CNES_SEM_MODELO_GESTAO: set[int] = set()

AVISO_PROXY = (
    "NOTA — a variável de modelo de gestão (modelo_gestao_proxy) usa as "
    "categorias de class_assistencial (SIH) como DEFINIÇÃO ADOTADA: PPP e "
    "Autarquia não são desmembrados e 'Público Municipal' entra como dummy "
    "única. Os 3 CNES sem pontuação de Barcelona (2042894, 2078031, "
    "2082209) foram EXCLUÍDOS do painel (ETAPA E)."
)


# ══════════════════════════════════════════════════════════════════════════════
# 0. CARGA DO PAINEL BRUTO
# ══════════════════════════════════════════════════════════════════════════════

def carregar_painel_bruto() -> pd.DataFrame:
    """Carrega o painel hospital-ano gerado por analise_sih.py (parquet ou CSV)."""
    painel = base.carregar_painel_cache()
    assert painel is not None, (
        "Painel não encontrado. Rode antes: python analise_sih.py"
    )
    painel = painel.copy()
    painel["cnes"] = pd.to_numeric(painel["cnes"], errors="raise").astype(np.int64)
    painel["ano"]  = painel["ano"].astype(int)
    painel["total_leitos"] = pd.to_numeric(painel["total_leitos"], errors="coerce")
    return painel


def extrair_codigo(valor) -> str | None:
    """
    Extrai o código numérico do prefixo de tipo_hospital/especializacao.
    '62 HOSPITAL/DIA - ISOLADO' → '62'; '005 MATERNIDADE' → '005';
    'HOSPITAL COVID', 'N/A', '#N/A', '-', None → None.
    """
    if not isinstance(valor, str):
        return None
    m = re.match(r"^\s*(\d+)", valor)
    return m.group(1) if m else None


def normalizar_texto(s) -> str:
    """Maiúsculas sem acento (para busca de COVID/CAMPANHA em nomes)."""
    if not isinstance(s, str):
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).upper()


def valor_modal_por_cnes(painel: pd.DataFrame, coluna: str) -> pd.Series:
    """
    Valor modal de `coluna` por CNES, considerando apenas anos com produção
    (qtde > 0) e valores informativos (exclui None/N/A/#N/A/-).
    Desempate: valor do ano mais recente entre os empatados.
    """
    sub = painel[painel["qtde"] > 0][["cnes", "ano", coluna]].copy()
    sub = sub[~sub[coluna].isin(["N/A", "#N/A", "-"]) & sub[coluna].notna()]

    def _moda(grupo: pd.DataFrame):
        contagem = grupo[coluna].value_counts()
        empatados = contagem[contagem == contagem.max()].index
        if len(empatados) == 1:
            return empatados[0]
        recente = grupo[grupo[coluna].isin(empatados)].sort_values("ano")
        return recente[coluna].iloc[-1]

    # seleção explícita de colunas: evita depender de include_groups (pandas>=2.2)
    return sub.groupby("cnes")[["ano", coluna]].apply(_moda)


def nome_referencia_por_cnes(painel: pd.DataFrame) -> pd.Series:
    """
    Nome de referência por CNES para logs: nome_fantasia só existe em
    2020-2021, então usa o mais recente disponível dentro do CNES.
    """
    sub = painel[painel["nome_fantasia"].notna()
                 & (painel["nome_fantasia"].astype(str).str.strip() != "")]
    return (sub.sort_values("ano").groupby("cnes")["nome_fantasia"].last())


# ══════════════════════════════════════════════════════════════════════════════
# AUDITORIA
# ══════════════════════════════════════════════════════════════════════════════

class Auditoria:
    """Acumula o efeito de cada filtro: resumo por etapa + detalhe por CNES."""

    def __init__(self, painel: pd.DataFrame):
        self.resumo:  list[dict] = []
        self.detalhe: list[dict] = []
        self.revisao: list[dict] = []
        self._nomes = nome_referencia_por_cnes(painel)
        self._registrar_estado("ETAPA 0", "painel bruto (sem filtros)", painel,
                               n_cnes_rem=0, n_ha_rem=0)

    def _registrar_estado(self, etapa, criterio, painel, n_cnes_rem, n_ha_rem):
        self.resumo.append({
            "etapa": etapa,
            "criterio": criterio,
            "cnes_removidos": n_cnes_rem,
            "hospital_ano_removidos": n_ha_rem,
            "cnes_restantes": painel["cnes"].nunique(),
            "hospital_ano_restantes": len(painel),
        })

    def aplicar_filtro(self, painel: pd.DataFrame, etapa: str, criterio: str,
                       cnes_excluir: set, motivos: dict) -> pd.DataFrame:
        """
        Remove `cnes_excluir` do painel (hospital INTEIRO — todos os anos),
        registrando resumo e detalhe. `motivos` mapeia cnes → texto do motivo.
        """
        mask_rem = painel["cnes"].isin(cnes_excluir)
        removidos = painel[mask_rem]
        for cnes in sorted(cnes_excluir & set(painel["cnes"])):
            self.detalhe.append({
                "etapa": etapa,
                "cnes": cnes,
                "nome_referencia": self._nomes.get(cnes, ""),
                "motivo": motivos.get(cnes, criterio),
                "anos_removidos": int((removidos["cnes"] == cnes).sum()),
            })
        restante = painel[~mask_rem].copy()
        self._registrar_estado(etapa, criterio, restante,
                               n_cnes_rem=int(removidos["cnes"].nunique()),
                               n_ha_rem=int(mask_rem.sum()))
        print(f"[{etapa}] {criterio}")
        print(f"         −{removidos['cnes'].nunique()} CNES / "
              f"−{mask_rem.sum()} hospital-ano  →  restam "
              f"{restante['cnes'].nunique()} CNES / {len(restante)} hospital-ano")
        return restante

    def marcar_revisao(self, etapa: str, cnes: int, questao: str):
        self.revisao.append({
            "etapa": etapa, "cnes": cnes,
            "nome_referencia": self._nomes.get(cnes, ""),
            "questao": questao,
        })

    def salvar(self):
        pd.DataFrame(self.resumo).to_csv(TAB_AUD_FILTROS, index=False,
                                         encoding="utf-8-sig")
        pd.DataFrame(self.detalhe).to_csv(TAB_AUD_REMOVIDOS, index=False,
                                          encoding="utf-8-sig")
        pd.DataFrame(self.revisao).to_csv(TAB_AUD_REVISAO, index=False,
                                          encoding="utf-8-sig")
        print(f"\n[AUDITORIA] {TAB_AUD_FILTROS.name}, {TAB_AUD_REMOVIDOS.name}, "
              f"{TAB_AUD_REVISAO.name} salvos em {base.PASTA_TABELAS}")
        print("\n[AUDITORIA] Resumo do funil de filtros:")
        print(pd.DataFrame(self.resumo).to_string(index=False))


# ══════════════════════════════════════════════════════════════════════════════
# ETAPA A — TIPO DE ESTABELECIMENTO
# ══════════════════════════════════════════════════════════════════════════════

def etapa_a_tipo(painel: pd.DataFrame, aud: Auditoria) -> pd.DataFrame:
    """
    Exclui hospitais dia (62), psiquiátricos (07 + espec. 006) e CAPS (70),
    pelo valor MODAL de tipo/especialização por CNES (ver D-A no cabeçalho).
    Maternidades (espec. 005) permanecem — a regra não as atinge.
    """
    tipo_modal  = valor_modal_por_cnes(painel, "tipo_hospital")
    espec_modal = valor_modal_por_cnes(painel, "especializacao")
    cod_tipo  = tipo_modal.map(extrair_codigo)
    cod_espec = espec_modal.map(extrair_codigo)

    motivos = {}
    for cnes in cod_tipo.index:
        t, e = cod_tipo.get(cnes), cod_espec.get(cnes)
        if t == "62":
            motivos[cnes] = "hospital dia (tipo 62)"
        elif t == "70":
            motivos[cnes] = "CAPS (tipo 70)"
        elif t == "07" and e == "006":
            motivos[cnes] = "psiquiátrico (tipo 07 + especialização 006)"
    cnes_excluir = set(motivos)

    # Revisão manual: CNES mantidos cuja série de tipo tocou uma categoria de
    # exclusão em algum ano (instabilidade de cadastro)
    sub = painel[painel["qtde"] > 0][["cnes", "tipo_hospital"]].copy()
    sub["cod"] = sub["tipo_hospital"].map(extrair_codigo)
    tocou_exclusao = set(sub[sub["cod"].isin(["62", "70"])]["cnes"])
    for cnes in sorted(tocou_exclusao - cnes_excluir):
        aud.marcar_revisao(
            "ETAPA A", cnes,
            "tipo_hospital tocou categoria de exclusão em ano isolado, "
            "mas o valor modal manteve o hospital — conferir cadastro")

    return aud.aplicar_filtro(
        painel, "ETAPA A",
        "tipo de estabelecimento (hospital dia 62 / psiquiátrico 07+006 / CAPS 70)",
        cnes_excluir, motivos)


# ══════════════════════════════════════════════════════════════════════════════
# ETAPA B — PORTE FIXO PELA MEDIANA DE LEITOS
# ══════════════════════════════════════════════════════════════════════════════

def etapa_b_porte(painel: pd.DataFrame, aud: Auditoria) -> pd.DataFrame:
    """
    Mediana de total_leitos por CNES nos anos com produção (qtde > 0):
    mediana > 50 → hospital inteiro incluído; <= 50 → excluído inteiro.
    CNES sem nenhum leito informado nos anos com produção → excluído
    (não demonstra porte mínimo) e registrado com motivo próprio.
    """
    com_prod = painel[painel["qtde"] > 0]
    mediana = com_prod.groupby("cnes")["total_leitos"].median()

    motivos = {}
    for cnes, med in mediana.items():
        if pd.isna(med):
            motivos[cnes] = "sem informação de leitos nos anos com produção"
        elif med <= CORTE_LEITOS:
            motivos[cnes] = f"mediana de leitos = {med:.1f} (corte: > {CORTE_LEITOS})"
    # CNES que nunca tiveram produção (apenas linha-resumo) tampouco demonstram
    # porte — excluídos com motivo próprio
    sem_prod = set(painel["cnes"]) - set(mediana.index)
    for cnes in sem_prod:
        motivos[cnes] = "nenhum ano com produção registrada"
    cnes_excluir = set(motivos)

    return aud.aplicar_filtro(
        painel, "ETAPA B",
        f"porte fixo: mediana de total_leitos > {CORTE_LEITOS} nos anos com produção",
        cnes_excluir, motivos)


# ══════════════════════════════════════════════════════════════════════════════
# ETAPA C1 — HOSPITAIS DE CAMPANHA COVID
# ══════════════════════════════════════════════════════════════════════════════

def etapa_c1_campanha(painel: pd.DataFrame, aud: Auditoria,
                      painel_bruto: pd.DataFrame) -> pd.DataFrame:
    """
    Exclui unidades criadas exclusivamente para a COVID-19 (regra ampliada
    D-C1 do cabeçalho). Usa o painel BRUTO para detectar candidatos e anos de
    produção — um campanha já removido nas etapas A/B não reaparece, mas o
    log fica completo em relação ao critério.
    """
    b = painel_bruto.copy()
    b["nome_norm"] = b["nome_fantasia"].map(normalizar_texto)
    b["match_nome"]  = b["nome_norm"].str.contains(r"COVID|CAMPANHA|CORONA",
                                                   regex=True)
    b["match_rotulo"] = (
        (b["tipo_hospital"] == "HOSPITAL COVID")
        | (b["class_assistencial"] == "Hospital COVID")
    )
    candidatos = set(b.loc[b["match_nome"] | b["match_rotulo"], "cnes"])

    anos_prod = (b[b["qtde"] > 0].groupby("cnes")["ano"]
                 .agg(lambda s: set(s.astype(int))))

    motivos = {}
    for cnes in sorted(candidatos):
        anos = anos_prod.get(cnes, set())
        classes = set(b.loc[b["cnes"] == cnes, "class_assistencial"].dropna())
        atende_literal = bool(classes & CLASSES_CRITERIO_LITERAL)
        if anos and anos <= ANOS_CAMPANHA:
            sufixo = "" if atende_literal else \
                " [fora do critério literal de classe — regra ampliada D-C1]"
            motivos[cnes] = (f"hospital de campanha COVID (produção restrita a "
                             f"{sorted(anos)}){sufixo}")
        else:
            aud.marcar_revisao(
                "ETAPA C1", cnes,
                f"nome/rótulo indica COVID, mas há produção fora de "
                f"{sorted(ANOS_CAMPANHA)} (anos: {sorted(anos)}) — possível "
                f"hospital regular rebatizado na pandemia; MANTIDO no painel")
    cnes_excluir = set(motivos)

    return aud.aplicar_filtro(
        painel, "ETAPA C1",
        "hospitais de campanha COVID (criados exclusivamente para a pandemia)",
        cnes_excluir, motivos)


# ══════════════════════════════════════════════════════════════════════════════
# ETAPA C2 — NUMERADORES COVID (RE-STREAM 2020/2021) E INDICADORES SEM COVID
# ══════════════════════════════════════════════════════════════════════════════

def restream_numeradores_covid() -> pd.DataFrame:
    """
    O painel em cache tem qtde/dias/valor COVID por hospital-ano, mas NÃO os
    numeradores de óbito e alta complexidade condicionais a COVID — sem eles,
    mortalidade e %alta-complexidade "sem código 999" ficariam com numerador
    contaminado. Re-lê APENAS os arquivos 2020 e 2021 em streaming (mesma
    infraestrutura de analise_sih) acumulando só esses numeradores.
    Resultado fica em cache (CACHE_COVID_NUM); apague o CSV para reprocessar.
    """
    if CACHE_COVID_NUM.exists():
        df = pd.read_csv(CACHE_COVID_NUM, encoding="utf-8-sig")
        print(f"[CACHE] Numeradores COVID carregados de {CACHE_COVID_NUM.name} "
              f"({len(df)} hospital-ano)")
        return df

    arquivos_sih, _, _ = base.localizar_arquivos(base.PASTA_DADOS)
    alvos = [(p, ano) for p, ano in arquivos_sih if ano in base.ANOS_COVID]
    assert alvos, "Nenhum arquivo 2020/2021 encontrado para o re-stream."

    registros = []
    for path, ano in alvos:
        print(f"[RE-STREAM] {path.name} (ano={ano}) — numeradores COVID ...")
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb[base.selecionar_aba_estado(wb)]
        linhas = ws.iter_rows(values_only=True)
        col_idx = base.construir_indice_colunas(next(linhas))
        base.validar_colunas(col_idx, ano, path.name)
        gi = col_idx.__getitem__
        i_cnes, i_qtde = gi("CNES"), gi("QTDE")
        i_desf, i_cplx = gi("DESFECHO"), gi("COMPLEX")
        i_cgrp, i_csub = gi("Cód Grupo"), gi("Cód Subgrupo")

        acc: dict[int, dict] = {}
        for row in linhas:
            cnes, qtde = row[i_cnes], row[i_qtde]
            if cnes is None or qtde is None:
                continue                       # só linhas de produção
            if not base.eh_covid(row[i_cgrp], row[i_csub]):
                continue
            q = base.val_float(qtde)
            a = acc.setdefault(cnes, {"qtde_obito_all_covid": 0.0,
                                      "qtde_obito_sem_excl_covid": 0.0,
                                      "qtde_alta_complex_covid": 0.0})
            desfecho = row[i_desf]
            if base.eh_obito(desfecho):
                a["qtde_obito_all_covid"] += q
                if base.eh_obito_versao_b(desfecho):
                    a["qtde_obito_sem_excl_covid"] += q
            if row[i_cplx] == "Alta complexidade":
                a["qtde_alta_complex_covid"] += q
        wb.close()
        for cnes, a in acc.items():
            registros.append({"cnes": int(cnes), "ano": ano, **a})
        print(f"            {len(acc)} CNES com procedimentos COVID em {ano}")

    df = pd.DataFrame(registros)
    df.to_csv(CACHE_COVID_NUM, index=False, encoding="utf-8-sig")
    print(f"[CACHE] Numeradores COVID salvos → {CACHE_COVID_NUM.name}")
    return df


def etapa_c2_indicadores_sem_covid(painel: pd.DataFrame, aud: Auditoria,
                                   covid_num: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula os indicadores nas versões COM covid (sufixo _com_covid, para
    comparação) e SEM covid (nome principal do painel definitivo, conforme
    §3 dos critérios). Não remove linhas: em anos fora de 2020-2021 as duas
    versões coincidem. Generaliza a lógica de tab_covid_com_sem.csv do
    pipeline base para TODOS os indicadores, agora com numeradores corretos.
    """
    df = painel.merge(covid_num, on=["cnes", "ano"], how="left")
    for c in ["qtde_obito_all_covid", "qtde_obito_sem_excl_covid",
              "qtde_alta_complex_covid"]:
        df[c] = df[c].fillna(0.0)

    _div = base._div
    # Versões COM covid (registro integral, para a comparação antes/depois)
    df["mort_all_com_covid"]         = _div(df["qtde_obito_all"],      df["qtde"])
    df["mort_sem_excl_com_covid"]    = _div(df["qtde_obito_sem_excl"], df["qtde"])
    df["tmp_com_covid"]              = _div(df["dias_perm"],           df["qtde"])
    df["custo_saida_com_covid"]      = _div(df["valor"],               df["qtde"])
    df["pct_alta_complex_com_covid"] = _div(df["qtde_alta_complex"],   df["qtde"])

    # Versões SEM covid — INDICADORES OFICIAIS do painel definitivo
    df["qtde_sem_covid"]  = df["qtde"]      - df["qtde_covid"].fillna(0)
    df["dias_sem_covid"]  = df["dias_perm"] - df["dias_covid"].fillna(0)
    df["valor_sem_covid"] = df["valor"]     - df["valor_covid"].fillna(0)
    df["mort_all"] = _div(df["qtde_obito_all"] - df["qtde_obito_all_covid"],
                          df["qtde_sem_covid"])
    df["mort_sem_excl"] = _div(
        df["qtde_obito_sem_excl"] - df["qtde_obito_sem_excl_covid"],
        df["qtde_sem_covid"])
    df["tmp"]         = _div(df["dias_sem_covid"],  df["qtde_sem_covid"])
    df["custo_saida"] = _div(df["valor_sem_covid"], df["qtde_sem_covid"])
    df["pct_alta_complex"] = _div(
        df["qtde_alta_complex"] - df["qtde_alta_complex_covid"],
        df["qtde_sem_covid"])
    # Ocupação: sem versão sem-COVID (ver D-C2 no cabeçalho) — mantida original

    afetados = df[(df["ano"].isin(base.ANOS_COVID)) & (df["qtde_covid"] > 0)]
    pct_prod = (100 * afetados["qtde_covid"].sum()
                / df.loc[df["ano"].isin(base.ANOS_COVID), "qtde"].sum())
    criterio = (f"procedimentos COVID (cód. 999) removidos dos indicadores: "
                f"{len(afetados)} hospital-ano afetados em 2020-2021 "
                f"({pct_prod:.1f}% da produção do biênio); nenhuma linha removida")
    aud._registrar_estado("ETAPA C2", criterio, df, n_cnes_rem=0, n_ha_rem=0)
    print(f"[ETAPA C2] {criterio}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# ETAPA D — PAINEL BALANCEADO
# ══════════════════════════════════════════════════════════════════════════════

def etapa_d_balanceado(painel: pd.DataFrame, aud: Auditoria) -> pd.DataFrame:
    """
    Retém apenas CNES com produção (qtde > 0) em TODOS os anos do período.
    Restrição de painel balanceado já vigente no projeto.
    """
    anos = sorted(painel["ano"].unique())
    presenca = (painel[painel["qtde"] > 0].groupby("cnes")["ano"].nunique())
    completos = set(presenca[presenca == len(anos)].index)
    incompletos = set(painel["cnes"]) - completos

    motivos = {c: (f"presente em {int(presenca.get(c, 0))}/{len(anos)} anos "
                   f"com produção")
               for c in incompletos}
    return aud.aplicar_filtro(
        painel, "ETAPA D",
        f"painel balanceado: produção em todos os {len(anos)} anos "
        f"({anos[0]}-{anos[-1]})",
        incompletos, motivos)


# ══════════════════════════════════════════════════════════════════════════════
# ETAPA E — EXCLUSÃO DE CNES SEM PONTUAÇÃO DE BARCELONA
# ══════════════════════════════════════════════════════════════════════════════

def etapa_sem_barcelona(painel: pd.DataFrame, aud: Auditoria,
                        df_classif: pd.DataFrame) -> pd.DataFrame:
    """
    Exclui do painel os CNES sem pontuação de Barcelona na planilha de
    classificação (verificados: 2042894, 2078031, 2082209). Sem o escore,
    complexidade_estrutural — controle central da modelagem — ficaria NaN.
    """
    cl = df_classif[["CNES", "Pontuação"]].copy()
    cl["CNES"]      = pd.to_numeric(cl["CNES"],      errors="coerce")
    cl["Pontuação"] = pd.to_numeric(cl["Pontuação"], errors="coerce")
    com_pontuacao = set(cl.loc[cl["Pontuação"].notna(), "CNES"]
                        .dropna().astype(np.int64))
    cnes_excluir = set(painel["cnes"]) - com_pontuacao
    motivos = {c: "sem pontuação de Barcelona na planilha de classificação"
               for c in cnes_excluir}
    return aud.aplicar_filtro(
        painel, "ETAPA E",
        "exclusão de CNES sem pontuação de Barcelona (complexidade indisponível)",
        cnes_excluir, motivos)


# ══════════════════════════════════════════════════════════════════════════════
# COMPLEXIDADE — DUAS VERSÕES (§4 DOS CRITÉRIOS)
# ══════════════════════════════════════════════════════════════════════════════

def calcular_escores_complexidade(painel: pd.DataFrame,
                                  df_classif: pd.DataFrame) -> pd.DataFrame:
    """
    Anexa a classificação Barcelona e calcula DUAS versões do escore de
    complexidade, mantidas como colunas separadas — NENHUMA é descartada:

    complexidade_estrutural
        Pontuação Barcelona pura (leitos, salas, UTI, flags cirúrgicas),
        fixa por CNES. SEM ponderação por desfecho.

    complexidade_pond_mort  (FÓRMULA PROVISÓRIA — pendente de ratificação)
        Pontuação Barcelona × (1 + mort_rel), onde mort_rel é a mortalidade
        geral SEM COVID do hospital-ano dividida pela mediana estadual do
        mesmo ano. Varia por hospital-ano. A forma funcional exata da
        ponderação deve ser deliberada pela equipe (§4 dos critérios); esta
        implementação materializa a decisão de "incorporar a mortalidade
        como variável de peso" da maneira mais simples e transparente.

    ══════════════════════════════════════════════════════════════════════
    SALVAGUARDA DE CIRCULARIDADE (critérios §4 — NÃO REMOVER ESTE AVISO):
      • Em modelos cuja variável DEPENDENTE é MORTALIDADE, usar
        EXCLUSIVAMENTE `complexidade_estrutural`. Usar
        `complexidade_pond_mort` como controle nesses modelos induz
        endogeneidade mecânica (a mortalidade entra dos dois lados).
      • `complexidade_pond_mort` fica reservada aos demais modelos
        (TMP, custo, ocupação, produção), até deliberação em contrário
        da equipe (João, Priscilla, Alberto).
    ══════════════════════════════════════════════════════════════════════
    """
    cl = df_classif[["CNES", "Pontuação", "Classificação"]].copy()
    cl.columns = ["cnes", "pont_barcelona", "faixa_barcelona"]
    cl["cnes"] = pd.to_numeric(cl["cnes"], errors="coerce").astype("Int64")
    cl["pont_barcelona"] = pd.to_numeric(cl["pont_barcelona"], errors="coerce")
    cl = cl.dropna(subset=["cnes"]).drop_duplicates("cnes")
    cl["cnes"] = cl["cnes"].astype(np.int64)

    df = painel.merge(cl, on="cnes", how="left")
    sem_classif = df.loc[df["pont_barcelona"].isna(), "cnes"].nunique()
    if sem_classif:
        print(f"[COMPLEXIDADE] AVISO: {sem_classif} CNES do painel definitivo "
              f"sem classificação Barcelona (escores = NaN) — conferir com Alberto.")

    df["complexidade_estrutural"] = df["pont_barcelona"]
    mediana_ano = df.groupby("ano")["mort_all"].transform("median")
    mort_rel = np.where(mediana_ano > 0, df["mort_all"] / mediana_ano, np.nan)
    df["complexidade_pond_mort"] = df["pont_barcelona"] * (1 + mort_rel)
    return df


def aplicar_decisoes_equipe(painel: pd.DataFrame) -> pd.DataFrame:
    """
    Materializa decisões pontuais da equipe sobre o painel construído.

    modelo_gestao_proxy: cópia de class_assistencial a ser usada em QUALQUER
    corte por modelo de gestão (DEFINIÇÃO ADOTADA). Difere do original apenas
    nos CNES de CNES_SEM_MODELO_GESTAO — mecanismo de supressão de rótulo que
    hoje está VAZIO (nenhum CNES suprimido). class_assistencial permanece
    intacta para rastreabilidade da fonte.
    """
    df = painel.copy()
    df["modelo_gestao_proxy"] = df["class_assistencial"]
    mask = df["cnes"].isin(CNES_SEM_MODELO_GESTAO)
    df.loc[mask, "modelo_gestao_proxy"] = np.nan
    if mask.any():
        print(f"[DECISÃO EQUIPE] {df.loc[mask, 'cnes'].nunique()} CNES com "
              f"modelo_gestao_proxy = NaN (rótulo suprimido pelo mecanismo "
              f"CNES_SEM_MODELO_GESTAO): {sorted(df.loc[mask, 'cnes'].unique())}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# SAÍDAS
# ══════════════════════════════════════════════════════════════════════════════

def salvar_painel_definitivo(df: pd.DataFrame):
    df.to_csv(PAINEL_DEFINITIVO_CSV, index=False, encoding="utf-8-sig")
    print(f"[SAÍDA] Painel definitivo → {PAINEL_DEFINITIVO_CSV}")
    try:
        df.to_parquet(PAINEL_DEFINITIVO_PARQUET, index=False)
        print(f"[SAÍDA] Painel definitivo → {PAINEL_DEFINITIVO_PARQUET}")
    except Exception:
        print("[SAÍDA] pyarrow indisponível; apenas CSV gravado.")

    LEIAME.write_text(
        "PAINEL ANALÍTICO DEFINITIVO — LEIA-ME\n"
        "=====================================\n\n"
        f"{AVISO_PROXY}\n\n"
        "Indicadores principais (mort_all, mort_sem_excl, tmp, custo_saida,\n"
        "pct_alta_complex) são as versões SEM procedimentos COVID (cód. 999),\n"
        "conforme §3 dos critérios. As versões com sufixo _com_covid existem\n"
        "apenas para comparação. Ocupação não possui versão sem-COVID\n"
        "(denominador não decomponível por procedimento).\n\n"
        "Complexidade: duas colunas coexistem por decisão da equipe (§4):\n"
        "  complexidade_estrutural — Barcelona pura; usar OBRIGATORIAMENTE em\n"
        "      modelos com mortalidade como variável dependente (circularidade).\n"
        "  complexidade_pond_mort  — Barcelona ponderada por mortalidade\n"
        "      relativa (fórmula provisória); reservada aos demais modelos.\n\n"
        "Cortes por modelo de gestão devem usar a coluna modelo_gestao_proxy\n"
        "(NUNCA class_assistencial diretamente): é nela que as decisões de\n"
        "agrupamento da equipe são materializadas.\n\n"
        "DECISÃO REGISTRADA — HU-UFSCar (5586348): classificação real\n"
        "CONFIRMADA por fonte externa — hospital público FEDERAL administrado\n"
        "pela Ebserh (empresa pública vinculada ao MEC); o rótulo 'Privado'\n"
        "do SIH NÃO corresponde à sua natureza jurídica. Por decisão da\n"
        "equipe, permanece AGRUPADO em 'Privado' no proxy, por conveniência\n"
        "estatística (eleva o grupo de n=2 para n=3). Não é erro: é escolha\n"
        "de agrupamento pragmático registrada.\n\n"
        "LIMITAÇÃO DE DESENHO (destacar no relatório): dos 5 switchers\n"
        "Direta->OSS documentados, 3 (CNES 2082225, 2091755, 2750511) só\n"
        "viram OSS em 2025 — apenas 1 ano de pós-tratamento no painel, o que\n"
        "limita o poder de identificação within-hospital. Os demais: 2081695\n"
        "(virada em 2019) e 2078287 (virada em 2023).\n\n"
        "ETAPA E — os 3 CNES sem classificação Barcelona (2042894, 2078031,\n"
        "2082209) foram EXCLUÍDOS do painel: todo hospital do painel definitivo\n"
        "tem pontuação de Barcelona.\n\n"
        "DEFINIÇÃO ADOTADA — modelo de gestão: modelo_gestao_proxy usa as\n"
        "categorias de class_assistencial (SIH) como definição adotada, sem\n"
        "desmembrar PPP/Autarquia e com 'Público Municipal' como dummy única.\n\n"
        "RESSALVA ESTATÍSTICA — categoria 'Privado' (n=3): Leforte\n"
        "Liberdade, Unimed Sorocaba e HU-UFSCar (este por agrupamento\n"
        "pragmático — ver decisão acima). O grupo mistura prestadores\n"
        "privados contratualizados de nicho com um hospital universitário\n"
        "federal de perfil assistencial distinto; com n=3, coeficientes\n"
        "dessa categoria NÃO são interpretáveis como efeito médio do modelo\n"
        "de gestão.\n\n"
        "Auditoria dos filtros: analises/tabelas/tab_auditoria_filtros.csv,\n"
        "tab_auditoria_cnes_removidos.csv e tab_auditoria_revisao_manual.csv.\n",
        encoding="utf-8")
    print(f"[SAÍDA] Notas metodológicas → {LEIAME}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("CONSTRUÇÃO DO PAINEL ANALÍTICO DEFINITIVO — SIH/SUS SP 2015-2025")
    print("=" * 70)
    print(f"\n{AVISO_PROXY}\n")

    base.configurar_diretorios()
    painel_bruto = carregar_painel_bruto()
    aud = Auditoria(painel_bruto)

    _, path_classif, _ = base.localizar_arquivos(base.PASTA_DADOS)
    assert path_classif, "Planilha de classificação Barcelona não encontrada."
    df_classif = base.carregar_classificacao(path_classif)

    painel = etapa_a_tipo(painel_bruto, aud)
    painel = etapa_b_porte(painel, aud)
    painel = etapa_c1_campanha(painel, aud, painel_bruto)

    covid_num = restream_numeradores_covid()
    painel = etapa_c2_indicadores_sem_covid(painel, aud, covid_num)

    painel = etapa_d_balanceado(painel, aud)
    painel = etapa_sem_barcelona(painel, aud, df_classif)
    painel = calcular_escores_complexidade(painel, df_classif)
    painel = aplicar_decisoes_equipe(painel)

    aud.salvar()
    salvar_painel_definitivo(painel)

    print("\n" + "=" * 70)
    print(f"CONCLUÍDO: {painel['cnes'].nunique()} hospitais × "
          f"{painel['ano'].nunique()} anos = {len(painel)} hospital-ano.")
    print("=" * 70)


if __name__ == "__main__":
    main()
