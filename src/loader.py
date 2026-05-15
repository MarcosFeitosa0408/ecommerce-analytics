"""
loader.py
---------
Responsável por carregar os dados brutos do dataset Olist.

POR QUE ISSO EXISTE?
Em vez de repetir pd.read_csv() em cada notebook, centralizamos
aqui. Se o caminho dos dados mudar, alteramos em um único lugar.
Isso é a prática 'DRY' (Don't Repeat Yourself) em ação.
"""

import pandas as pd
from pathlib import Path
from typing import Optional
import logging

# Configura o sistema de logs — assim sabemos o que está acontecendo
# sem precisar de print() espalhados pelo código.
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Caminho base do projeto (sobe 2 níveis a partir deste arquivo)
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


# Dicionário com todos os arquivos disponíveis no dataset Olist.
# Mapeia um nome amigável para o nome real do arquivo CSV.
OLIST_FILES = {
    "orders":        "olist_orders_dataset.csv",
    "order_items":   "olist_order_items_dataset.csv",
    "customers":     "olist_customers_dataset.csv",
    "products":      "olist_products_dataset.csv",
    "reviews":       "olist_order_reviews_dataset.csv",
    "sellers":       "olist_sellers_dataset.csv",
    "payments":      "olist_order_payments_dataset.csv",
    "geolocation":   "olist_geolocation_dataset.csv",
    "category_names":"product_category_name_translation.csv",
}


def load_table(table_name: str, data_dir: Optional[Path] = None) -> pd.DataFrame:
    """
    Carrega uma tabela específica do dataset Olist.

    Parâmetros
    ----------
    table_name : str
        Nome amigável da tabela. Use as chaves de OLIST_FILES.
        Exemplos: "orders", "customers", "reviews"

    data_dir : Path, opcional
        Caminho para a pasta com os CSVs. Se não informado,
        usa o padrão: data/raw/

    Retorna
    -------
    pd.DataFrame
        O conteúdo da tabela como um DataFrame do Pandas.

    Exemplos
    --------
    >>> df_pedidos = load_table("orders")
    >>> df_clientes = load_table("customers")
    """
    if table_name not in OLIST_FILES:
        opcoes_validas = list(OLIST_FILES.keys())
        raise ValueError(
            f"Tabela '{table_name}' não encontrada. "
            f"Opções válidas: {opcoes_validas}"
        )

    folder = data_dir or RAW_DATA_DIR
    file_path = folder / OLIST_FILES[table_name]

    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {file_path}\n"
            f"Baixe os dados em: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce"
        )

    logger.info(f"Carregando tabela '{table_name}' de {file_path.name}...")
    df = pd.read_csv(file_path)
    logger.info(f"✓ {len(df):,} linhas carregadas.")

    return df


def load_all_tables(data_dir: Optional[Path] = None) -> dict[str, pd.DataFrame]:
    """
    Carrega todas as tabelas do dataset de uma vez.

    Útil para análises que precisam cruzar várias tabelas.

    Retorna
    -------
    dict
        Dicionário onde cada chave é o nome da tabela e o valor
        é o DataFrame correspondente.

    Exemplos
    --------
    >>> tabelas = load_all_tables()
    >>> tabelas["orders"].head()
    >>> tabelas["reviews"].shape
    """
    tabelas = {}
    for nome in OLIST_FILES:
        try:
            tabelas[nome] = load_table(nome, data_dir)
        except FileNotFoundError as e:
            logger.warning(f"Pulando '{nome}': arquivo não encontrado.")

    logger.info(f"\n✅ {len(tabelas)} tabelas carregadas com sucesso.")
    return tabelas
