# notebooks/01_exploratory.py
# Equivalente ao Jupyter Notebook 01_exploratory.ipynb
# Cole cada bloco em uma célula separada no Jupyter.
#
# ============================================================
# NOTEBOOK 1: Exploração Inicial dos Dados (EDA)
#
# OBJETIVO: Conhecer o dataset antes de qualquer análise.
# Perguntas respondidas aqui:
#   - Quantos dados temos?
#   - Há dados faltando?
#   - Qual é o período coberto?
#   - Quais são as distribuições básicas?
# ============================================================

# %% [markdown]
# # 🔍 Análise Exploratória — E-Commerce Brasileiro (Olist)
#
# **Dataset:** 100k+ pedidos reais de 2016 a 2018
# **Objetivo:** Entender a estrutura dos dados antes de analisar

# %% CÉLULA 1: Importações
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
sys.path.insert(0, "..")   # Permite importar os módulos da pasta src/

from src.loader import load_table
from src.cleaner import clean_orders, clean_reviews, merge_master_table
from src.visualizer import set_style

set_style()   # Aplica o estilo visual padrão do projeto
print("✅ Bibliotecas importadas com sucesso.")


# %% CÉLULA 2: Carregar os dados
orders       = load_table("orders")
order_items  = load_table("order_items")
customers    = load_table("customers")
reviews      = load_table("reviews")
products     = load_table("products")
cat_names    = load_table("category_names")

print(f"\nResumo das tabelas carregadas:")
print(f"  orders:       {orders.shape}")
print(f"  order_items:  {order_items.shape}")
print(f"  customers:    {customers.shape}")
print(f"  reviews:      {reviews.shape}")


# %% CÉLULA 3: Verificar qualidade dos dados
# Uma das primeiras coisas que um analista faz: checar dados faltantes.
print("=== Dados Faltantes (%) — Tabela de Pedidos ===")
faltantes = (orders.isnull().mean() * 100).round(2)
print(faltantes[faltantes > 0])

# Interpretação esperada:
# order_approved_at: ~0.2% → pedidos aprovados quase imediatamente
# order_delivered_carrier_date: ~1.1% → ainda não saiu para entrega
# order_delivered_customer_date: ~2.9% → ainda não chegou ao cliente


# %% CÉLULA 4: Período dos dados
orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
print(f"Período dos dados:")
print(f"  Início: {orders['order_purchase_timestamp'].min().date()}")
print(f"  Fim:    {orders['order_purchase_timestamp'].max().date()}")
print(f"  Total de dias: {(orders['order_purchase_timestamp'].max() - orders['order_purchase_timestamp'].min()).days}")


# %% CÉLULA 5: Distribuição de status dos pedidos
# Entender quais pedidos chegaram ao cliente vs. foram cancelados etc.
status_counts = orders["order_status"].value_counts()
print("\nDistribuição de Status dos Pedidos:")
print(status_counts)
print(f"\nPedidos entregues: {status_counts.get('delivered', 0) / len(orders) * 100:.1f}% do total")


# %% CÉLULA 6: Distribuição de notas de avaliação
fig, ax = plt.subplots(figsize=(8, 4))
reviews["review_score"].value_counts().sort_index().plot(
    kind="bar",
    color=["#C1121F", "#E85D04", "#F4A261", "#74C69D", "#2D6A4F"],
    edgecolor="white",
    ax=ax,
)
ax.set_title("Distribuição de Notas de Avaliação")
ax.set_xlabel("Nota (1-5)")
ax.set_ylabel("Número de Avaliações")
ax.set_xticklabels(["1\n⭐", "2\n⭐⭐", "3\n⭐⭐⭐", "4\n⭐⭐⭐⭐", "5\n⭐⭐⭐⭐⭐"], rotation=0)

# Adiciona % em cada barra
total = len(reviews)
for p in ax.patches:
    pct = p.get_height() / total * 100
    ax.annotate(f"{pct:.1f}%", (p.get_x() + p.get_width() / 2, p.get_height() + 200),
                ha="center", fontsize=10)

plt.tight_layout()
plt.savefig("../outputs/figures/01_distribuicao_notas.png", dpi=150)
plt.show()

# Insight esperado: a maioria dos clientes dá nota 5 (satisfação alta),
# mas há um segundo pico em nota 1 (insatisfação extrema). Não há meio-termo.


# %% CÉLULA 7: Volume de pedidos por mês
orders_clean = clean_orders(orders)
pedidos_por_mes = (
    orders_clean
    .groupby(["order_year", "order_month"])["order_id"]
    .count()
    .reset_index(name="total_pedidos")
)
pedidos_por_mes["mes_ano"] = pd.to_datetime(
    pedidos_por_mes[["order_year", "order_month"]].assign(day=1)
)

fig, ax = plt.subplots(figsize=(12, 5))
ax.fill_between(pedidos_por_mes["mes_ano"], pedidos_por_mes["total_pedidos"],
                alpha=0.3, color="#E85D04")
ax.plot(pedidos_por_mes["mes_ano"], pedidos_por_mes["total_pedidos"],
        color="#E85D04", linewidth=2.5, marker="o", markersize=5)
ax.set_title("Volume de Pedidos por Mês (2016–2018)")
ax.set_xlabel("Mês")
ax.set_ylabel("Total de Pedidos")

# Destaca o pico (Black Friday 2017)
pico = pedidos_por_mes.loc[pedidos_por_mes["total_pedidos"].idxmax()]
ax.annotate(
    f"Pico: Black Friday\n{int(pico['total_pedidos']):,} pedidos",
    xy=(pico["mes_ano"], pico["total_pedidos"]),
    xytext=(-80, -50), textcoords="offset points",
    arrowprops=dict(arrowstyle="->", color="#C1121F"),
    fontsize=10, color="#C1121F",
)

plt.tight_layout()
plt.savefig("../outputs/figures/01_volume_mensal.png", dpi=150)
plt.show()

print("\n✅ Análise exploratória concluída. Próximo passo: notebook 02_cleaning.ipynb")
