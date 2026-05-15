"""
test_analyzer.py
----------------
Testes automatizados para as funções de análise.

POR QUE ISSO EXISTE?
Testes garantem que o código funciona corretamente e que
futuras alterações não "quebram" o que já funcionava.
É uma prática profissional que diferencia um projeto sério
de um script experimental.

Como rodar:
    pytest tests/ -v
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Importa as funções que vamos testar
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
from src.analyzer import calculate_rfm, calculate_kpis, _atribuir_segmento


# =============================================================================
# FIXTURES — Dados sintéticos para os testes
#
# Em vez de usar dados reais (que podem mudar), criamos dados
# controlados que sabemos exatamente o que devem produzir.
# =============================================================================

@pytest.fixture
def sample_rfm_data():
    """
    Cria um DataFrame pequeno e controlado para testar o RFM.

    3 clientes com perfis bem diferentes:
    - cliente_A: comprou recentemente, várias vezes, muito dinheiro → Campeão
    - cliente_B: comprou há muito tempo, poucas vezes → Hibernando/Perdido
    - cliente_C: comprou recentemente pela primeira vez → Novo
    """
    today = datetime(2018, 12, 31)  # Data de referência fixa

    data = {
        "customer_id": [
            "cliente_A", "cliente_A", "cliente_A",   # 3 compras
            "cliente_B",                               # 1 compra antiga
            "cliente_C",                               # 1 compra recente
        ],
        "order_id": ["o1", "o2", "o3", "o4", "o5"],
        "order_purchase_timestamp": [
            today - timedelta(days=10),    # Recente
            today - timedelta(days=30),    # Recente
            today - timedelta(days=60),    # Recente
            today - timedelta(days=400),   # Antigo
            today - timedelta(days=5),     # Muito recente
        ],
        "price": [500.0, 300.0, 450.0, 50.0, 80.0],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_kpi_data():
    """DataFrame com dados mínimos para testar os KPIs."""
    return pd.DataFrame({
        "order_id":                   ["o1", "o1", "o2"],     # 2 pedidos únicos
        "customer_id":                ["c1", "c1", "c2"],     # 2 clientes únicos
        "price":                      [100.0, 50.0, 200.0],   # Receita: 350
        "review_score":               [5, 5, 3],
        "delivery_delay_days":        [-2, -2, 5],             # o1 no prazo, o2 atrasado
        "order_purchase_timestamp":   pd.to_datetime(["2018-01-01", "2018-01-01", "2018-02-01"]),
    })


# =============================================================================
# TESTES
# =============================================================================

class TestCalculateRFM:
    """Testes para a função calculate_rfm()"""

    def test_retorna_dataframe(self, sample_rfm_data):
        """O resultado deve ser um DataFrame"""
        resultado = calculate_rfm(sample_rfm_data, reference_date=datetime(2018, 12, 31))
        assert isinstance(resultado, pd.DataFrame)

    def test_uma_linha_por_cliente(self, sample_rfm_data):
        """Deve ter exatamente um registro por cliente único"""
        resultado = calculate_rfm(sample_rfm_data, reference_date=datetime(2018, 12, 31))
        n_clientes = sample_rfm_data["customer_id"].nunique()
        assert len(resultado) == n_clientes

    def test_colunas_obrigatorias(self, sample_rfm_data):
        """O resultado deve ter as colunas de score e segmento"""
        resultado = calculate_rfm(sample_rfm_data, reference_date=datetime(2018, 12, 31))
        colunas_esperadas = {"R_score", "F_score", "M_score", "rfm_score", "rfm_segment"}
        assert colunas_esperadas.issubset(resultado.columns)

    def test_scores_entre_1_e_4(self, sample_rfm_data):
        """Scores R, F e M devem estar entre 1 e 4"""
        resultado = calculate_rfm(sample_rfm_data, reference_date=datetime(2018, 12, 31))
        for col in ["R_score", "F_score", "M_score"]:
            assert resultado[col].between(1, 4).all(), f"Score inválido na coluna {col}"


class TestAtribuirSegmento:
    """Testes unitários para a lógica de segmentação"""

    def _fazer_row(self, r, f, m):
        """Helper para criar uma linha de teste"""
        return pd.Series({"R_score": r, "F_score": f, "M_score": m})

    def test_campiao(self):
        """Scores altos em tudo → Campeão"""
        row = self._fazer_row(r=4, f=4, m=4)
        assert _atribuir_segmento(row) == "🏆 Campeões"

    def test_perdido(self):
        """Scores baixos em tudo → Perdido"""
        row = self._fazer_row(r=1, f=1, m=1)
        assert _atribuir_segmento(row) == "😴 Perdidos"

    def test_novo_cliente(self):
        """Alta recência, baixa frequência → Novo Cliente"""
        row = self._fazer_row(r=4, f=1, m=2)
        assert _atribuir_segmento(row) == "🆕 Novos Clientes"


class TestCalculateKPIs:
    """Testes para a função calculate_kpis()"""

    def test_receita_total_correta(self, sample_kpi_data):
        """Receita total deve ser a soma de todos os preços"""
        kpis = calculate_kpis(sample_kpi_data)
        assert kpis["receita_total"] == pytest.approx(350.0, rel=1e-3)

    def test_total_pedidos_correto(self, sample_kpi_data):
        """Deve contar pedidos únicos, não linhas"""
        kpis = calculate_kpis(sample_kpi_data)
        assert kpis["total_pedidos"] == 2

    def test_taxa_atraso_correta(self, sample_kpi_data):
        """1 de 2 pedidos atrasou → 50%"""
        kpis = calculate_kpis(sample_kpi_data)
        assert kpis["taxa_atraso_pct"] == pytest.approx(50.0, rel=1e-1)
