"""
visualizer.py
-------------
Funções padronizadas de visualização para o projeto.

POR QUE ISSO EXISTE?
Centralizar os gráficos garante que todos tenham o mesmo
visual (cores, fontes, estilo), facilitando a criação de
relatórios e apresentações coesas.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

# Paleta de cores do projeto — tons de laranja/azul que remetem
# às cores da bandeira brasileira e ao tema de e-commerce.
COLORS = {
    "primary":    "#E85D04",   # Laranja vibrante
    "secondary":  "#0077B6",   # Azul profissional
    "accent":     "#F4A261",   # Laranja claro
    "neutral":    "#6B7280",   # Cinza neutro
    "success":    "#2D6A4F",   # Verde (positivo)
    "danger":     "#C1121F",   # Vermelho (negativo)
    "background": "#FAFAFA",   # Fundo quase branco
}

# Mapa de cores para segmentos RFM
RFM_COLORS = {
    "🏆 Campeões":       "#2D6A4F",
    "💛 Clientes Fiéis": "#74C69D",
    "🆕 Novos Clientes": "#0077B6",
    "⚠️ Em Risco":       "#F4A261",
    "❄️ Hibernando":     "#ADB5BD",
    "😴 Perdidos":       "#C1121F",
}


def set_style():
    """
    Define o estilo padrão para todos os gráficos do projeto.
    Chame uma vez no início do notebook.
    """
    sns.set_theme(style="whitegrid", font_scale=1.1)
    plt.rcParams.update({
        "figure.facecolor":  COLORS["background"],
        "axes.facecolor":    COLORS["background"],
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "font.family":       "sans-serif",
        "axes.titleweight":  "bold",
        "axes.titlesize":    14,
    })


def plot_rfm_segments(rfm_df: pd.DataFrame, save_path: Path = None) -> plt.Figure:
    """
    Gráfico de barras com a distribuição de clientes por segmento RFM.

    Parâmetros
    ----------
    rfm_df : pd.DataFrame
        Resultado da função calculate_rfm()
    save_path : Path, opcional
        Se informado, salva o gráfico no caminho especificado.
    """
    contagem = rfm_df["rfm_segment"].value_counts().reset_index()
    contagem.columns = ["segmento", "clientes"]
    contagem = contagem.sort_values("clientes", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(
        contagem["segmento"],
        contagem["clientes"],
        color=[RFM_COLORS.get(s, COLORS["neutral"]) for s in contagem["segmento"]],
        edgecolor="white",
        linewidth=0.5,
    )

    # Adiciona o valor absoluto ao lado de cada barra
    for bar, val in zip(bars, contagem["clientes"]):
        ax.text(
            bar.get_width() + 50, bar.get_y() + bar.get_height() / 2,
            f"{val:,}", va="center", ha="left",
            fontsize=11, color=COLORS["neutral"],
        )

    ax.set_title("Distribuição de Clientes por Segmento RFM", pad=16)
    ax.set_xlabel("Número de Clientes")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Gráfico salvo em: {save_path}")

    return fig


def plot_delay_vs_satisfaction(resultado_df: pd.DataFrame, save_path: Path = None) -> plt.Figure:
    """
    Gráfico de barras duplo: nota média e volume por faixa de atraso.

    Mostra claramente que atraso = cliente insatisfeito.
    """
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Barras de fundo: volume de pedidos (eixo secundário)
    ax2 = ax1.twinx()
    ax2.bar(
        resultado_df["faixa_atraso"],
        resultado_df["total_pedidos"],
        color=COLORS["neutral"], alpha=0.2,
        label="Volume de pedidos",
    )
    ax2.set_ylabel("Volume de Pedidos", color=COLORS["neutral"])
    ax2.tick_params(axis="y", labelcolor=COLORS["neutral"])

    # Linha: nota média (eixo principal)
    cores_linha = [
        COLORS["success"] if n >= 4 else COLORS["danger"]
        for n in resultado_df["nota_media"]
    ]
    ax1.plot(
        resultado_df["faixa_atraso"],
        resultado_df["nota_media"],
        marker="o", linewidth=2.5,
        color=COLORS["primary"], zorder=5, label="Nota média",
    )
    for x, y in zip(resultado_df["faixa_atraso"], resultado_df["nota_media"]):
        ax1.annotate(
            f"{y:.1f}",
            (x, y), textcoords="offset points",
            xytext=(0, 12), ha="center",
            fontsize=11, fontweight="bold", color=COLORS["primary"],
        )

    ax1.set_ylim(0, 6)
    ax1.set_ylabel("Nota Média (1-5)", color=COLORS["primary"])
    ax1.tick_params(axis="y", labelcolor=COLORS["primary"])
    ax1.set_xlabel("")
    ax1.set_title("Impacto do Atraso na Entrega → Satisfação do Cliente", pad=16)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower left")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    return fig


def plot_revenue_by_state(state_df: pd.DataFrame, top_n: int = 10, save_path: Path = None) -> plt.Figure:
    """
    Gráfico de barras horizontal com os top N estados por receita.

    Parâmetros
    ----------
    state_df : pd.DataFrame
        Resultado de revenue_by_state()
    top_n : int
        Quantos estados exibir (padrão: 10)
    """
    top = state_df.head(top_n).sort_values("receita_total")

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(
        top["customer_state"],
        top["receita_total"],
        color=COLORS["secondary"],
        edgecolor="white",
    )

    # Destaca o 1º lugar
    bars[-1].set_color(COLORS["primary"])

    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"R$ {x/1_000_000:.1f}M")
    )
    ax.set_title(f"Top {top_n} Estados por Receita Total", pad=16)
    ax.set_xlabel("Receita Total")
    ax.set_ylabel("Estado")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    return fig
