# notebooks/03_rfm_analysis.py
# Equivalente ao Jupyter Notebook 03_rfm_analysis.ipynb
#
# ============================================================
# NOTEBOOK 3: Segmentação de Clientes com RFM
#
# OBJETIVO: Classificar os clientes em segmentos estratégicos
# para que a equipe de marketing saiba em quem focar.
#
# Pergunta de negócio respondida:
#   "Quem são nossos melhores clientes e quem está sumindo?"
# ============================================================

# %% [markdown]
# # 👥 Segmentação RFM de Clientes
#
# ## O que é RFM?
# RFM é uma técnica usada por empresas como Amazon, Magazine Luiza e iFood
# para entender o comportamento dos clientes:
#
# | Letra | Significado | Pergunta |
# |-------|-------------|----------|
# | **R** | Recency (Recência) | Quando foi a última compra? |
# | **F** | Frequency (Frequência) | Quantas vezes comprou? |
# | **M** | Monetary (Monetário) | Quanto gastou no total? |
#
# Cada cliente recebe uma nota de **1 a 4** em cada dimensão.
# A combinação define seu **segmento estratégico**.

# %% CÉLULA 1: Setup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
sys.path.insert(0, "..")

from src.loader import load_table
from src.cleaner import clean_orders, clean_reviews, merge_master_table
from src.analyzer import calculate_rfm, calculate_kpis, analyze_delay_vs_satisfaction, revenue_by_state
from src.visualizer import set_style, plot_rfm_segments, plot_delay_vs_satisfaction, plot_revenue_by_state
from pathlib import Path

set_style()
OUTPUT_DIR = Path("../outputs/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("✅ Setup concluído.")


# %% CÉLULA 2: Carregar e limpar os dados
print("Carregando dados...")
orders      = clean_orders(load_table("orders"))
order_items = load_table("order_items")
customers   = load_table("customers")
reviews     = clean_reviews(load_table("reviews"))
products    = load_table("products")
cat_names   = load_table("category_names")

# Monta a tabela mestre (equivalente a vários JOINs em SQL)
df = merge_master_table(orders, order_items, customers, reviews, products, cat_names)
print(f"\nTabela mestre: {df.shape[0]:,} linhas × {df.shape[1]} colunas")


# %% CÉLULA 3: KPIs do negócio
print("\n" + "="*50)
print("📊 KPIs PRINCIPAIS DO NEGÓCIO")
print("="*50)
kpis = calculate_kpis(df)

print(f"💰 Receita Total:         R$ {kpis['receita_total']:,.2f}")
print(f"🛒 Total de Pedidos:       {kpis['total_pedidos']:,}")
print(f"👥 Total de Clientes:      {kpis['total_clientes']:,}")
print(f"🎫 Ticket Médio:          R$ {kpis['ticket_medio']:,.2f}")
print(f"⭐ Nota Média:            {kpis['nota_media']}/5")
print(f"📦 Taxa de Atraso:        {kpis['taxa_atraso_pct']}% dos pedidos")


# %% CÉLULA 4: Calcular o RFM
rfm = calculate_rfm(df)

print("\nPrimeiras linhas do RFM:")
print(rfm[["customer_id", "recencia_dias", "frequencia", "valor_total",
           "R_score", "F_score", "M_score", "rfm_segment"]].head(10).to_string())


# %% CÉLULA 5: Visualizar distribuição dos segmentos
fig = plot_rfm_segments(rfm, save_path=OUTPUT_DIR / "03_rfm_segmentos.png")
plt.show()


# %% CÉLULA 6: Valor de negócio de cada segmento
# Aqui vemos não só quantos clientes há em cada segmento,
# mas QUANTO cada segmento representa em receita.
segmento_valor = rfm.groupby("rfm_segment").agg(
    total_clientes  = ("customer_id", "count"),
    receita_total   = ("valor_total", "sum"),
    ticket_medio    = ("valor_total", "mean"),
).round(2).sort_values("receita_total", ascending=False)

segmento_valor["pct_receita"] = (
    segmento_valor["receita_total"] / segmento_valor["receita_total"].sum() * 100
).round(1)

print("\n" + "="*60)
print("💡 VALOR DE CADA SEGMENTO PARA O NEGÓCIO")
print("="*60)
print(segmento_valor.to_string())

# %% [markdown]
# ### 📌 Interpretação dos Resultados
#
# | Segmento | Ação Recomendada |
# |---|---|
# | 🏆 Campeões | Recompensar com programa de fidelidade, pedir reviews |
# | 💛 Clientes Fiéis | Oferecer upsell, lançamentos em primeira mão |
# | 🆕 Novos Clientes | Engajar com onboarding, cupom para 2ª compra |
# | ⚠️ Em Risco | Campanha de reativação urgente com oferta personalizada |
# | ❄️ Hibernando | E-mail "sentimos sua falta" com desconto agressivo |
# | 😴 Perdidos | Custo alto de reativação — avaliar se vale o investimento |


# %% CÉLULA 7: Impacto do atraso na satisfação
resultado_atraso = analyze_delay_vs_satisfaction(df)
print("\nImpacto do Atraso na Nota de Satisfação:")
print(resultado_atraso.to_string(index=False))

fig = plot_delay_vs_satisfaction(resultado_atraso, save_path=OUTPUT_DIR / "03_atraso_vs_satisfacao.png")
plt.show()


# %% CÉLULA 8: Receita por estado
estado_receita = revenue_by_state(df)
fig = plot_revenue_by_state(estado_receita, top_n=10, save_path=OUTPUT_DIR / "03_receita_estados.png")
plt.show()

print("\n✅ Análise RFM concluída!")
print("   Gráficos salvos em: outputs/figures/")
print("   Próximo passo: 04_dashboard_prep.ipynb")
