"""
Tests de integración para orquestación de agentes
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.agents.supervisor_agent import SupervisorAgent, TaskType
from app.agents.billing_agent import BillingAgent
from app.agents.collections_agent import CollectionsAgent
from app.agents.negotiation_agent import NegotiationAgent


class TestAgentOrchestration:
    """Tests de orquestación entre agentes"""
    
    def setup_method(self):
        self.supervisor = SupervisorAgent()
        self.billing_agent = BillingAgent()
        self.collections_agent = CollectionsAgent()
        self.negotiation_agent = NegotiationAgent()
    
    @pytest.mark.asyncio
    async def test_supervisor_routes_billing_cycle(self):
        """Test: Supervisor enruta ciclo de facturación correctamente"""
        task = {
            "type": "start_billing_cycle",
            "ciclo_id": 15,
            "force_human_review": False,
        }
        
        result = await self.supervisor.execute(task)
        
        assert result["status"] in ["in_progress", "completed", "pending_human_review"]
        assert "steps" in result
        assert len(result["steps"]) > 0
    
    @pytest.mark.asyncio
    async def test_supervisor_human_review_trigger(self):
        """Test: Supervisor activa HITL cuando es forzado"""
        task = {
            "type": "start_billing_cycle",
            "ciclo_id": 15,
            "force_human_review": True,
        }
        
        result = await self.supervisor.execute(task)
        
        assert result["requires_human_review"] == True
        assert result["status"] == "pending_human_review"
    
    @pytest.mark.asyncio
    async def test_supervisor_delegates_task(self):
        """Test: Supervisor delega tarea a agente específico"""
        task = {"factura_id": 4001, "monto": 4300.00}
        
        result = self.supervisor.delegate_task(TaskType.BILLING, task)
        
        assert result["status"] == "delegated"
        assert result["agent"] == "billing_agent"
        assert result["agent_type"] == TaskType.BILLING
    
    @pytest.mark.asyncio
    async def test_billing_to_negotiation_flow(self):
        """Test: Flujo de facturación a negociación"""
        # 1. Facturar
        billing_task = {
            "cuenta_id": 2005,
            "periodo": "2024-10",
            "servicios": [
                {
                    "id_servicio": 3006,
                    "cargo_fijo_mensual": 120.00,
                    "fecha_inicio": __import__('datetime').date(2024, 10, 1),
                    "fecha_fin": __import__('datetime').date(2024, 10, 31),
                }
            ],
            "cliente_score": 0.45,
        }
        
        billing_result = await self.billing_agent.execute(billing_task)
        assert billing_result["status"] == "success"
        
        # 2. Generar oferta de negociación
        negotiation_task = {
            "factura_id": 4001,
            "cliente_score": 0.45,
            "probabilidad_pago": 0.30,
            "monto_factura": billing_result["factura"]["importe_total"],
            "dias_para_vencimiento": 5,
        }
        
        negotiation_result = await self.negotiation_agent.execute(negotiation_task)
        assert negotiation_result["status"] == "success"
        assert negotiation_result["decision"] == "unhappy_path"
        assert negotiation_result["oferta"] is not None
    
    @pytest.mark.asyncio
    async def test_collections_flow(self):
        """Test: Flujo de cobranzas"""
        task = {
            "type": "check_overdue",
        }
        
        result = await self.collections_agent.execute(task)
        
        assert result["status"] == "success"
        assert "total_overdue" in result
        assert "invoices" in result
    
    @pytest.mark.asyncio
    async def test_tamn_calculation_integration(self):
        """Test: Cálculo TAMN en flujo de cobranzas"""
        task = {
            "type": "calculate_tamn",
            "monto_deuda": 1000.00,
            "dias_mora": 15,
            "factor_vencimiento": 1.0,
            "factor_actual": 1.025,
        }
        
        result = await self.collections_agent.execute(task)
        
        assert result["status"] == "success"
        assert result["interes_tamn"] > 0
        assert result["total_pagar"] > result["monto_deuda"]
    
    @pytest.mark.asyncio
    async def test_system_health_check(self):
        """Test: Verificación de salud del sistema"""
        health = self.supervisor.check_system_health()
        
        assert health["supervisor"] == "healthy"
        assert "agents" in health
        assert len(health["agents"]) > 0