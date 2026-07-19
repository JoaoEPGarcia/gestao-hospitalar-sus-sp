# -*- coding: utf-8 -*-
"""
_rodar_item_1_3.py
==================
Executa APENAS a função nova do item 1.3 (ocupacao_sem_pandemia) de
diagnostico_painel_definitivo.py, sem regenerar as demais figuras/tabelas do
diagnóstico — evita reprocessamento desnecessário antes do ciclo único da
Etapa 3. O painel lido é o ATUAL em disco (pré-patch 1.11): a tabela será
regenerada na Etapa 3 já com o Guilherme Álvaro reclassificado.

USO: python _rodar_item_1_3.py
"""

import pandas as pd

import construir_painel_definitivo as cpd
import diagnostico_painel_definitivo as diag

painel = pd.read_csv(cpd.PAINEL_DEFINITIVO_CSV, encoding="utf-8-sig")
print(f"[CARGA] {painel['cnes'].nunique()} CNES / {len(painel)} hospital-ano "
      f"(painel em disco, PRÉ-patch 1.11)")
diag.ocupacao_sem_pandemia(painel)
print("\nOK — apenas tab_def_ocupacao_sem_pandemia.csv foi gerada/atualizada.")
