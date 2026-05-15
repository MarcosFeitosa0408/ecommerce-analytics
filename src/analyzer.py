"""
analyzer.py
-----------
Lógica central de análise: KPIs, RFM, correlações e tendências.

POR QUE ISSO EXISTE?
Separar a lógica de análise do notebook permite reutilizar
as funções em diferentes contextos (outros notebooks, APIs,
pipelines de dados) sem copiar código.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# SEÇÃO 1: KPIs (Key Performance Indicators)
# Métricas de negócio que toda empresa quer monitorar.
# =============================================================================

def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calcula os principais KPIs do negócio a partir da tabela mestre.

    KPIs calculados:
    - Receita Total
    - Ticket Médio (valor médio por pedido)
    - Total de Pedidos
    - Total de Clientes Únicos
    - Nota Média de Satisfação
    - Taxa de Atraso nas Entregas

    Retorna
    -------
    dict
        Dicionário com os KPIs. Fácil de converter para
        um painel de métricas ou relatório.
    """
    total_pedidos = df["order_id"].nunique()
    total_clientes = df["customer_id"].nunique()
    receita_total = df.groupby("order_id")["price"].sum().sum()
    ticket_medio = receita_total / total_pedidos

    nota_media = df.groupby("order_id")["review_score"].first().mean()

    # Taxa de atraso: % de pedidos que chegaram depois do prazo
    pedidos_com_atraso = df.groupby("order_id")["delivery_delay_days"].first()
    taxa_atraso = (pedidos_com_atraso > 0).mean() * 100

    kpis = {
        "receita_total":       round(receita_total, 2),
        "ticket_medio":        round(ticket_medio, 2),
        "total_pedidos":       total_pedidos,
        "total_clientes":      total_clientes,
        "nota_media":          round(nota_media, 2),
        "taxa_atraso_pct":     round(taxa_atraso, 1),
    }

    logger.info("KPIs calculados:")
    for k, v in kpis.items():
        logger.info(f"  {k}: {v}")

    return kpis


# =============================================================================
# SEÇÃO 2: Análise RFM
#
# RFM é uma técnica clássica de segmentação de clientes usada em
# marketing e CRM. Avalia cada cliente em três dimensões:
#
#   R (Recency)   = Há quantos dias o cliente comprou pela última vez?
#                   → Quanto menor, mais "recente" e engajado.
#
#   F (Frequency) = Quantas vezes o cliente comprou?
#                   → Quanto maior, mais fiel.
#
#   M (Monetary)  = Quanto o cliente gastou no total?
#                   → Quanto maior, mais valioso.
#
# Cada dimensão recebe uma nota de 1 a 4 (usando quartis).
# A combinação das três notas define o segmento do cliente.
# =============================================================================

def calculate_rfm(df: pd.DataFrame, reference_date: datetime = None) -> pd.DataFrame:
    """
    Calcula o score RFM para cada cliente.

    Parâmetros
    ----------
    df : pd.DataFrame
        Tabela mestre com colunas: customer_id, order_purchase_timestamp, price
    reference_date : datetime, opcional
        Data de referência para calcular recência.
        Padrão: data mais recente nos dados + 1 dia.

    Retorna
    -------
    pd.DataFrame
        Um DataFrame com uma linha por cliente e colunas:
        R_score, F_score, M_score, rfm_segment
    """
    # Data de referência: "hoje" do ponto de vista dos dados
    if reference_date is None:
        reference_date = df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)

    logger.info(f"Calculando RFM com data de referência: {reference_date.date()}")

    # --- Agrega os dados por cliente ---
    rfm = df.groupby("customer_id").agg(
        ultima_compra  = ("order_purchase_timestamp", "max"),   # para Recência
        frequencia     = ("order_id", "nunique"),                # para Frequência
        valor_total    = ("price", "sum"),                       # para Monetário
    ).reset_index()

    # Recência = quantos dias passaram desde a última compra
    rfm["recencia_dias"] = (reference_date - rfm["ultima_compra"]).dt.days

    # --- Atribui scores de 1 a 4 usando quartis ---
    # Para Recência: score 4 = comprou há pouco tempo (bom)
    # Para Freq/Monetário: score 4 = comprou muito (bom)
    rfm["R_score"] = pd.qcut(rfm["recencia_dias"], q=4, labels=[4, 3, 2, 1])
    rfm["F_score"] = pd.qcut(rfm["frequencia"].rank(method="first"), q=4, labels=[1, 2, 3, 4])
    rfm["M_score"] = pd.qcut(rfm["valor_total"], q=4, labels=[1, 2, 3, 4])

    # Converte para inteiro para facilitar operações
    rfm[["R_score", "F_score", "M_score"]] = rfm[["R_score", "F_score", "M_score"]].astype(int)

    # Score combinado (soma simples — pode ser ponderado conforme o negócio)
    rfm["rfm_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

    # --- Classifica em segmentos de negócio ---
    rfm["rfm_segment"] = rfm.apply(_atribuir_segmento, axis=1)

    logger.info(f"✅ RFM calculado para {len(rfm):,} clientes.")
    logger.info(f"\nDistribuição de segmentos:\n{rfm['rfm_segment'].value_counts()}")

    return rfm


def _atribuir_segmento(row) -> str:
    """
    Regras de negócio para classificar um cliente em um segmento.
    Baseado nas melhores práticas de CRM e segmentação RFM.

    Esta função é chamada internamente por calculate_rfm().
    """
    r, f, m = row["R_score"], row["F_score"], row["M_score"]

    if r >= 3 and f >= 3 and m >= 3:
        return "🏆 Campeões"           # Compram muito, gastam muito, vieram recentemente
    elif r >= 3 and f >= 2:
        return "💛 Clientes Fiéis"      # Compram com frequência e recentemente
    elif r >= 3 and f == 1:
        return "🆕 Novos Clientes"      # Compraram recentemente, mas só uma vez
    elif r == 2 and f >= 2:
        return "⚠️ Em Risco"            # Antes fiéis, mas sumiram
    elif r == 1 and f >= 2:
        return "❄️ Hibernando"          # Fiéis no passado, inativos há muito tempo
    else:
        return "😴 Perdidos"            # Compraram pouco e faz muito tempo


# =============================================================================
# SEÇÃO 3: Análise de Satisfação vs Atraso
# Responde: "Atraso na entrega impacta a nota do cliente?"
# =============================================================================

def analyze_delay_vs_satisfaction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analisa a relação entre atraso na entrega e nota de satisfação.

    Agrupa os atrasos em faixas e calcula a nota média de cada faixa.
    Resultado esperado: quanto maior o atraso, menor a nota.

    Retorna
    -------
    pd.DataFrame
        Tabela com faixas de atraso, nota média e volume de pedidos.
    """
    # Pega uma linha por pedido (evita duplicatas de itens)
    df_pedido = df.groupby("order_id").agg(
        atraso = ("delivery_delay_days", "first"),
        nota   = ("review_score", "first"),
    ).dropna()

    # Cria faixas de atraso interpretáveis
    bins   = [-float("inf"), -7, 0, 3, 7, float("inf")]
    labels = ["Adiantado >7d", "No prazo", "Até 3d atraso", "4-7d atraso", ">7d atraso"]

    df_pedido["faixa_atraso"] = pd.cut(df_pedido["atraso"], bins=bins, labels=labels)

    resultado = (
        df_pedido.groupby("faixa_atraso", observed=True)
        .agg(
            nota_media      = ("nota", "mean"),
            total_pedidos   = ("nota", "count"),
        )
        .round(2)
        .reset_index()
    )

    return resultado


# =============================================================================
# SEÇÃO 4: Análise de Receita por Estado
# =============================================================================

def revenue_by_state(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula receita total, ticket médio e volume de pedidos por estado.
  
    Útil para criar mapas de calor geográficos e identificar
    regiões com maior potencial de expansão.
    """
    resultado = (
        df.groupby("customer_state")
        .agg(
            receita_total   = ("price", "sum"),
            total_pedidos   = ("order_id", "nunique"),
            ticket_medio    = ("price", lambda x: x.sum() / df.loc[x.index, "order_id"].nunique()),
        )
        .round(2)
        .sort_values("receita_total", ascending=False)
        .reset_index()
    )

    return resultado
