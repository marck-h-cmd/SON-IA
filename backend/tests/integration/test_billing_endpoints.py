"""
Tests de integración para endpoints de facturación
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test: Health check endpoint"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["app"] == "SON-IA"


@pytest.mark.asyncio
async def test_dashboard_metrics():
    """Test: Dashboard metrics endpoint"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/dashboard/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "facturas_procesadas_hoy" in data["metrics"]


@pytest.mark.asyncio
async def test_listar_facturas():
    """Test: Listar facturas endpoint"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/billing/facturas")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_factura_no_encontrada():
    """Test: Factura no encontrada"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/billing/facturas/99999")
        
        assert response.status_code == 404