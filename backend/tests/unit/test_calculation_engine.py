"""
Tests unitarios para el motor de cálculo simbólico
"""

import pytest
from decimal import Decimal
from datetime import date

from app.core.calculation_engine import CalculationEngine


class TestCalculationEngine:
    """Tests para CalculationEngine"""
    
    def setup_method(self):
        self.engine = CalculationEngine()
    
    def test_calcular_prorrateo_pxq_mes_completo(self):
        """Test: Prorrateo para mes completo (31 días)"""
        cargo_fijo = Decimal("310.00")
        fecha_inicio = date(2024, 10, 1)
        fecha_fin = date(2024, 10, 31)
        
        resultado = self.engine.calcular_prorrateo_pxq(
            cargo_fijo, fecha_inicio, fecha_fin
        )
        
        assert resultado == Decimal("310.00")
    
    def test_calcular_prorrateo_pxq_medio_mes(self):
        """Test: Prorrateo para medio mes (15 días de 30)"""
        cargo_fijo = Decimal("300.00")
        fecha_inicio = date(2024, 4, 1)  # Abril tiene 30 días
        fecha_fin = date(2024, 4, 15)
        
        resultado = self.engine.calcular_prorrateo_pxq(
            cargo_fijo, fecha_inicio, fecha_fin
        )
        
        # 300 / 30 * 15 = 150.00
        assert resultado == Decimal("150.00")
    
    def test_calcular_prorrateo_pxq_un_dia(self):
        """Test: Prorrateo para un solo día"""
        cargo_fijo = Decimal("310.00")
        fecha_inicio = date(2024, 10, 15)
        fecha_fin = date(2024, 10, 15)
        
        resultado = self.engine.calcular_prorrateo_pxq(
            cargo_fijo, fecha_inicio, fecha_fin
        )
        
        # 310 / 31 * 1 = 10.00
        assert resultado == Decimal("10.00")
    
    def test_calcular_igv(self):
        """Test: Cálculo de IGV 18%"""
        monto_total = Decimal("118.00")
        
        base, igv = self.engine.calcular_igv(monto_total)
        
        assert base == Decimal("100.00")
        assert igv == Decimal("18.00")
    
    def test_calcular_igv_desde_base(self):
        """Test: Cálculo de IGV desde base imponible"""
        base = Decimal("100.00")
        
        igv = self.engine.calcular_igv_desde_base(base)
        
        assert igv == Decimal("18.00")
    
    def test_calcular_interes_tamn(self):
        """Test: Cálculo de intereses TAMN"""
        deuda = Decimal("1000.00")
        factor_vencimiento = Decimal("1.0")
        factor_hoy = Decimal("1.05")
        
        interes = self.engine.calcular_interes_tamn(
            deuda, 30, factor_vencimiento, factor_hoy
        )
        
        # 1000 * (1.05/1.0 - 1) = 50.00
        assert interes == Decimal("50.00")
    
    def test_calcular_total_factura(self):
        """Test: Cálculo de total de factura"""
        subtotal = Decimal("100.00")
        igv = Decimal("18.00")
        
        total = self.engine.calcular_total_factura(subtotal, igv)
        
        assert total == Decimal("118.00")
    
    def test_prorrateo_fechas_invalidas(self):
        """Test: Error con fechas inválidas"""
        with pytest.raises(ValueError):
            self.engine.calcular_prorrateo_pxq(
                Decimal("100"),
                date(2024, 10, 31),
                date(2024, 10, 1),  # fecha_inicio > fecha_fin
            )