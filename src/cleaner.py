"""
cleaner.py
----------
Funções de limpeza e validação dos dados do Olist.

POR QUE ISSO EXISTE?
Dados reais são sujos: datas em formato errado, valores nulos,
duplicatas, categorias com nomes inconsistentes. Esta etapa
é onde ~60% do trabalho de um analista acontece na prática.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e prepara a tabela de pedidos para análise.

    O que faz:
    - Converte colunas de data de texto para datetime
    - Remove pedidos cancelados ou com status inválido
    - Cria coluna de dias de atraso (prometido vs real)
    - Remove linhas sem data de entrega real (pedidos em aberto)

    Parâmetros
    ----------
    df : pd.DataFrame
        DataFrame bruto da tabela 'orders'

    Retorna
    -------
    pd.DataFrame
        DataFrame limpo, pronto para análise
    """
    df = df.copy()  # Nunca modificamos o original — boa prática

    # --- 1. Converter datas de string para datetime ---
    # O Pandas não reconhece datas automaticamente, precisamos dizer
    # explicitamente para ele que aquelas colunas são datas.
    colunas_data = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in colunas_data:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # --- 2. Filtrar apenas pedidos entregues ---
    # Para análise de satisfação e tempo de entrega, precisamos
    # apenas de pedidos que chegaram ao cliente.
    tamanho_original = len(df)
    df = df[df["order_status"] == "delivered"].copy()
    removidos = tamanho_original - len(df)
    logger.info(f"Status: {removidos:,} pedidos não-entregues removidos.")

    # --- 3. Remover pedidos sem data de entrega real ---
    df = df.dropna(subset=["order_delivered_customer_date"])
    logger.info(f"Após limpeza: {len(df):,} pedidos válidos.")

    # --- 4. Criar feature de atraso em dias ---
    # Diferença entre entrega real e entrega prometida.
    # Valor positivo = atrasou; negativo = chegou antes do prazo.
    df["delivery_delay_days"] = (
        df["order_delivered_customer_date"]
        - df["order_estimated_delivery_date"]
    ).dt.days

    # --- 5. Criar features de tempo ---
    df["order_year"]  = df["order_purchase_timestamp"].dt.year
    df["order_month"] = df["order_purchase_timestamp"].dt.month
    df["order_weekday"] = df["order_purchase_timestamp"].dt.day_name()

    logger.info("✓ Tabela 'orders' limpa com sucesso.")
    return df


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa a tabela de avaliações dos clientes.

    O que faz:
    - Remove avaliações duplicadas (mantém a mais recente)
    - Valida que as notas estão entre 1 e 5
    - Classifica as notas em categorias legíveis
    """
    df = df.copy()

    # --- 1. Remover duplicatas ---
    # Alguns pedidos têm mais de uma avaliação. Mantemos a mais recente.
    df["review_creation_date"] = pd.to_datetime(
        df["review_creation_date"], errors="coerce"
    )
    antes = len(df)
    df = (
        df.sort_values("review_creation_date", ascending=False)
        .drop_duplicates(subset="order_id", keep="first")
    )
    logger.info(f"Reviews: {antes - len(df):,} duplicatas removidas.")

    # --- 2. Validar notas ---
    notas_invalidas = ~df["review_score"].between(1, 5)
    if notas_invalidas.any():
        logger.warning(f"{notas_invalidas.sum()} avaliações com nota inválida removidas.")
        df = df[~notas_invalidas]

    # --- 3. Criar categoria de satisfação ---
    # Transforma nota numérica em rótulo interpretável.
    # Útil para gráficos e segmentação.
    df["satisfaction"] = pd.cut(
        df["review_score"],
        bins=[0, 2, 3, 5],
        labels=["Negativa (1-2)", "Neutra (3)", "Positiva (4-5)"],
    )

    logger.info("✓ Tabela 'reviews' limpa com sucesso.")
    return df


def merge_master_table(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    customers: pd.DataFrame,
    reviews: pd.DataFrame,
    products: pd.DataFrame,
    category_names: pd.DataFrame,
) -> pd.DataFrame:
    """
    Junta todas as tabelas em uma única tabela mestre para análise.

    Pensa nisso como um JOIN do SQL, mas em Pandas.
    Cada pedido terá informações do cliente, produto, avaliação e valor.

    Retorna
    -------
    pd.DataFrame
        Tabela única e completa com todas as informações relevantes.
    """
    logger.info("Construindo tabela mestre...")

    # Traduz nomes de categorias para inglês (o dataset tem as duas versões)
    products = products.merge(category_names, on="product_category_name", how="left")

    # Junta pedidos com itens (preço, produto)
    df = orders.merge(order_items, on="order_id", how="left")

    # Adiciona informações do produto
    df = df.merge(
        products[["product_id", "product_category_name_english"]],
        on="product_id",
        how="left",
    )

    # Adiciona informações do cliente (estado)
    df = df.merge(
        customers[["customer_id", "customer_state", "customer_city"]],
        on="customer_id",
        how="left",
    )

    # Adiciona avaliação do pedido
    df = df.merge(
        reviews[["order_id", "review_score", "satisfaction"]],
        on="order_id",
        how="left",
    )

    logger.info(f"✅ Tabela mestre criada: {df.shape[0]:,} linhas × {df.shape[1]} colunas.")
    return df
