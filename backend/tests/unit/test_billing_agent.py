"""
Tests unitarios para el Agente de Facturación
"""

import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import AsyncMock, patch

from app.agents.billing_agent import BillingAgent


class TestBillingAgent:
    """Tests para BillingAgent"""
    
    def setup_method(self):
        self.agent = BillingAgent()
    
    @pytest.mark.asyncio
    async def test_execute_billing_success(self):
        """Test: Ejecución exitosa de facturación"""
        task = {
            "cuenta_id": 2001,
            "periodo": "2024-10",
            "servicios": [
                {
                    "id_servicio": 3001,
                    "cargo_fijo_mensual": 2500.00,
                    "concepto": "Fibra Óptica",
                    "fecha_inicio": date(2024, 10, 1),
                    "fecha_fin": date(2024, 10, 31),
                }
            ],
            "cliente_score": 0.85,
        }
        
        result = await self.agent.execute(task)
        
        assert result["status"] == "success"
        assert "factura" in result
        assert result["factura"]["validacion_automatica"] == True
        assert result["factura"]["score_confianza"] == 0.85
    
    @pytest.mark.asyncio
    async def test_auto_validation_high_score(self):
        """Test: Validación automática para score alto"""
        task = {
            "cuenta_id": 2001,
            "periodo": "2024-10",
            "servicios": [
                {
                    "id_servicio": 3001,
                    "cargo_fijo_mensual": 100.00,
                    "fecha_inicio": date(2024, 10, 1),
                    "fecha_fin": date(2024, 10, 31),
                }
            ],
            "cliente_score": 0.90,
        }
        
        result = await self.agent.execute(task)
        assert result["factura"]["validacion_automatica"] == True
    
    @pytest.mark.asyncio
    async def test_manual_validation_low_score(self):
        """Test: Validación manual para score bajo"""
        task = {
            "cuenta_id": 2005,
            "periodo": "2024-10",
            "servicios": [
                {
                    "id_servicio": 3006,
                    "cargo_fijo_mensual": 120.00,
                    "fecha_inicio": date(2024, 10, 1),
                    "fecha_fin": date(2024, 10, 31),
                }
            ],
            "cliente_score": 0.45,
        }
        
        result = await self.agent.execute(task)
        assert result["factura"]["validacion_automatica"] == False
    
    @pytest.mark.asyncio
    async def test_prorrateo_calculation(self):
        """Test: Cálculo de prorrateo en factura"""
        task = {
            "cuenta_id": 2001,
            "periodo": "2024-04",
            "servicios": [
                {
                    "id_servicio": 3001,
                    "cargo_fijo_mensual": 300.00,
                    "fecha_inicio": date(2024, 4, 1),
                    "fecha_fin": date(2024, 4, 15),
                }
            ],
            "cliente_score": 0.80,
        }
        
        result = await self.agent.execute(task)
        
        # 300 / 30 * 15 = 150.00
        monto_linea = result["factura"]["lineas"][0]["monto_linea"]
        assert monto_linea == 150.00
    
    @pytest.mark.asyncio
    async def test_empty_servicios_error(self):
        """Test: Error con servicios vacíos"""
        task = {
            "cuenta_id": 2001,
            "periodo": "2024-10",
            "servicios": [],
            "cliente_score": 0.80,
        }
        
        result = await self.agent.execute(task)
        assert result["status"] == "error"