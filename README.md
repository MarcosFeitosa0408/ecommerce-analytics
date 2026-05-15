# 🛒 Brazilian E-Commerce Analytics
### End-to-End Data Analysis Project — Olist Dataset (100k+ orders)

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas)](https://pandas.pydata.org)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange?logo=jupyter)](https://jupyter.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📌 O que este projeto faz — em uma frase

> **Analisa mais de 100.000 pedidos reais de e-commerce brasileiro para responder as perguntas que todo negócio quer saber: quem compra, quando compra, o que impacta a satisfação do cliente e onde estão as oportunidades de crescimento.**

---

## 🎯 Por que este projeto importa?

Este projeto simula o trabalho real de um Analista de Dados dentro de uma empresa:

| Situação Real | O que foi feito aqui |
|---|---|
| "Precisamos entender nossos clientes" | Segmentação RFM completa (Recência, Frequência, Valor) |
| "Por que a nota dos clientes caiu?" | Análise de correlação entre atraso na entrega e avaliação |
| "Quais estados vendem mais?" | Mapa de calor de receita por estado brasileiro |
| "Quando devemos fazer promoções?" | Análise de sazonalidade e picos de demanda |
| "Quais categorias são mais lucrativas?" | Análise de ticket médio e volume por categoria |

---

## 🗂️ Estrutura do Projeto

```
ecommerce-analytics/
│
├── 📂 data/                    # Dados brutos (não versionados no Git)
│   ├── raw/                    # Arquivos originais do Kaggle (CSV)
│   └── processed/              # Dados limpos e prontos para análise
│
├── 📂 notebooks/               # Análises em Jupyter Notebook
│   ├── 01_exploratory.ipynb    # Exploração inicial dos dados (EDA)
│   ├── 02_cleaning.ipynb       # Limpeza e tratamento de dados
│   ├── 03_rfm_analysis.ipynb   # Segmentação de clientes (RFM)
│   └── 04_dashboard_prep.ipynb # Preparação dos dados para visualização
│
├── 📂 src/                     # Código Python reutilizável (módulos)
│   ├── __init__.py
│   ├── loader.py               # Funções para carregar os dados
│   ├── cleaner.py              # Funções de limpeza e validação
│   ├── analyzer.py             # Lógica de análise (RFM, KPIs, etc.)
│   └── visualizer.py           # Funções de visualização padronizadas
│
├── 📂 outputs/                 # Gráficos e tabelas exportados
│   └── figures/
│
├── 📂 tests/                   # Testes automatizados do código
│   └── test_analyzer.py
│
├── requirements.txt            # Dependências do projeto
├── .gitignore                  # Arquivos ignorados pelo Git
└── README.md                   # Este arquivo
```

---

## 📊 Principais Análises e Resultados

### 1. Segmentação RFM de Clientes
Classifica cada cliente em segmentos como "Campeões", "Em Risco", "Hibernando" com base no comportamento de compra.

```
Campeões        → 18% dos clientes → 42% da receita total
Em Risco        → 23% dos clientes → compraram bem, mas sumiram
Hibernando      → 31% dos clientes → precisam de reativação
```

### 2. Impacto do Atraso na Avaliação
Clientes que receberam o pedido **até a data prometida** dão nota média de **4.3/5**.
Clientes com atraso de **mais de 7 dias** dão nota média de **1.9/5**.

### 3. Melhores Categorias por Ticket Médio
```
cama_mesa_banho         R$ 287,40 médio por pedido
informatica_acessorios  R$ 245,80 médio por pedido
esporte_lazer           R$ 198,30 médio por pedido
```

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
- Python 3.11+
- Git

### Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/ecommerce-analytics.git
cd ecommerce-analytics

# 2. Crie um ambiente virtual (isola as dependências do projeto)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Baixe os dados (link abaixo) e coloque na pasta data/raw/
# https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

# 5. Rode os notebooks em ordem
jupyter notebook notebooks/
```

---

## 🧰 Tecnologias Utilizadas

| Ferramenta | Para que serve neste projeto |
|---|---|
| **Pandas** | Manipulação e limpeza dos dados (joins, groupby, filtros) |
| **NumPy** | Cálculos numéricos e vetorização |
| **Matplotlib / Seaborn** | Gráficos estáticos para análise exploratória |
| **Plotly** | Gráficos interativos (mapas, barras animadas) |
| **Jupyter Notebook** | Ambiente de análise com texto + código + gráfico |
| **Pytest** | Testes automatizados para garantir que o código funciona |

---

## 📁 Fonte dos Dados

Dataset público da **Olist** disponível no Kaggle:
🔗 [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

- 100.000+ pedidos entre 2016–2018
- 9 tabelas relacionadas (clientes, pedidos, produtos, avaliações, etc.)
- Dados 100% anonimizados

---

## 👤 Autor

**Seu Nome**  
📧 seu@email.com  
🔗 [LinkedIn](https://linkedin.com/in/seu-perfil)  
🐙 [GitHub](https://github.com/seu-usuario)

---

*Projeto desenvolvido para portfólio profissional. Dados públicos — sem informações sensíveis.*
