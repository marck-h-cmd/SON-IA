"""
Tests unitarios para el calculador de score de confianza
"""

import pytest
from decimal import Decimal

from app.core.confidence_scorer import ConfidenceScorer


class TestConfidenceScorer:
    """Tests para ConfidenceScorer"""
    
    def setup_method(self):
        self.scorer = ConfidenceScorer()
    
    def test_cliente_excelente(self):
        """Test: Cliente con historial perfecto"""
        score = self.scorer.calcular_score(
            antiguedad_meses=60,
            promedio_mora_dias=0,
            num_disputas_ultimo_anio=0,
            num_pagos_tarde=0,
            monto_promedio=Decimal("1000"),
            segmento="B2B",
        )
        
        assert score >= Decimal("0.90")
    
    def test_cliente_nuevo(self):
        """Test: Cliente nuevo sin historial"""
        score = self.scorer.calcular_score(
            antiguedad_meses=1,
            promedio_mora_dias=20,
            num_disputas_ultimo_anio=5,
            num_pagos_tarde=10,
            monto_promedio=Decimal("100"),
            segmento="B2C",
        )
        
        assert score < Decimal("0.30")
    
    def test_es_cliente_confiable(self):
        """Test: Umbral de cliente confiable"""
        assert self.scorer.es_cliente_confiable(Decimal("0.85")) == True
        assert self.scorer.es_cliente_confiable(Decimal("0.80")) == True
        assert self.scorer.es_cliente_confiable(Decimal("0.79")) == False
        assert self.scorer.es_cliente_confiable(Decimal("0.50")) == False
    
    def test_score_rango_valido(self):
        """Test: El score siempre está entre 0 y 1"""
        score = self.scorer.calcular_score(
            antiguedad_meses=1000,
            promedio_mora_dias=0,
            num_disputas_ultimo_anio=0,
            num_pagos_tarde=0,
            monto_promedio=Decimal("1000000"),
            segmento="Gobierno",
        )
        
        assert Decimal("0") <= score <= Decimal("1")