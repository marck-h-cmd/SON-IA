
# 🔌 API Reference - SON-IA

## Información General

- **Base URL**: `http://localhost:8000/api/v1`
- **Formato**: JSON
- **Codificación**: UTF-8
- **Zona Horaria**: America/Lima (UTC-5)
- **Documentación Interactiva**:
  - Swagger UI: `http://localhost:8000/api/docs`
  - ReDoc: `http://localhost:8000/api/redoc`

---

## Autenticación

**Nota**: La autenticación JWT está planificada para la Fase 2 del MVP. Actualmente los endpoints son públicos para desarrollo.

```
Authorization: Bearer <token>
```

---

## Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Datos inválidos |
| 404 | Not Found - Recurso no encontrado |
| 422 | Unprocessable Entity - Error de validación |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error - Error del servidor |
| 503 | Service Unavailable - Servicio no disponible |

---

## Formato de Respuesta

### Éxito
```json
{
  "status": "success",
  "data": { ... }
}
```

### Error
```json
{
  "status": "error",
  "detail": "Descripción del error",
  "error_type": "ValidationError"
}
```

---

## Endpoints

### 1. Health

#### `GET /health`

Health check básico para monitoreo y balanceadores de carga.

**Request**
```bash
curl http://localhost:8000/api/v1/health
```

**Response 200**
```json
{
  "status": "ok",
  "app": "SON-IA",
  "version": "0.1.0"
}
```

---

#### `GET /health/detailed`

Health check detallado con verificación de componentes.

**Request**
```bash
curl http://localhost:8000/api/v1/health/detailed
```

**Response 200**
```json
{
  "status": "ok",
  "components": {
    "api": "ok",
    "database": "ok",
    "redis": "ok",
    "groq": "healthy",
    "gemini": "healthy"
  }
}
```

**Response 503 (Servicio Degradado)**
```json
{
  "status": "degraded",
  "components": {
    "api": "ok",
    "database": "ok",
    "redis": "error",
    "groq": "healthy",
    "gemini": "healthy"
  }
}
```

---

### 2. Dashboard

#### `GET /dashboard/metrics`

Obtiene métricas en tiempo real para el dashboard interno.

**Request**
```bash
curl http://localhost:8000/api/v1/dashboard/metrics
```

**Response 200**
```json
{
  "status": "success",
  "metrics": {
    "facturas_procesadas_hoy": 245,
    "monto_total_recaudado": 892500.00,
    "indice_morosidad": 3.2,
    "ofertas_activas": 15,
    "facturas_pendientes_revision": 3,
    "tasa_aceptacion_ofertas": 34.5,
    "tiempo_promedio_emision_seg": 12,
    "agentes_activos": 7,
    "timestamp": "2024-10-01T10:00:00-05:00"
  }
}
```

**Campos de la respuesta**:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `facturas_procesadas_hoy` | int | Total de facturas emitidas en el día |
| `monto_total_recaudado` | float | Monto total recaudado hoy (S/) |
| `indice_morosidad` | float | Porcentaje de facturas vencidas |
| `ofertas_activas` | int | Ofertas de negociación pendientes |
| `facturas_pendientes_revision` | int | Facturas esperando revisión humana (HITL) |
| `tasa_aceptacion_ofertas` | float | Porcentaje de ofertas aceptadas |
| `tiempo_promedio_emision_seg` | float | Tiempo promedio de emisión en segundos |
| `agentes_activos` | int | Número de agentes en ejecución |
| `timestamp` | string | Momento de la consulta (ISO 8601) |

---

#### `GET /dashboard/agentes/estado`

Obtiene el estado actual de todos los agentes del ecosistema.

**Request**
```bash
curl http://localhost:8000/api/v1/dashboard/agentes/estado
```

**Response 200**
```json
{
  "status": "success",
  "system_health": {
    "supervisor": "healthy",
    "agents": {
      "billing": "available",
      "collections": "available",
      "negotiation": "available",
      "customer_service": "available",
      "classification": "available",
      "learning": "available"
    }
  },
  "agentes": {
    "supervisor": {
      "estado": "activo",
      "modelo": "deepseek-r1",
      "proveedor": "groq",
      "ultima_ejecucion": "2024-10-01T09:55:00-05:00",
      "tareas_procesadas": 1250,
      "tasa_error": 0.02
    },
    "billing": {
      "estado": "activo",
      "modelo": "deepseek-r1",
      "proveedor": "groq",
      "ultima_ejecucion": "2024-10-01T09:50:00-05:00",
      "tareas_procesadas": 450,
      "tasa_error": 0.01
    },
    "collections": {
      "estado": "activo",
      "modelo": "deepseek-r1",
      "proveedor": "groq",
      "ultima_ejecucion": "2024-10-01T09:45:00-05:00",
      "tareas_procesadas": 320,
      "tasa_error": 0.03
    },
    "negotiation": {
      "estado": "activo",
      "modelo": "deepseek-r1",
      "proveedor": "groq",
      "ultima_ejecucion": "2024-10-01T09:40:00-05:00",
      "tareas_procesadas": 180,
      "tasa_error": 0.01
    },
    "customer": {
      "estado": "activo",
      "modelo": "gemini-1.5-pro",
      "proveedor": "google",
      "ultima_ejecucion": "2024-10-01T09:58:00-05:00",
      "tareas_procesadas": 890,
      "tasa_error": 0.05
    },
    "classifier": {
      "estado": "activo",
      "modelo": "gemini-1.5-flash",
      "proveedor": "google",
      "ultima_ejecucion": "2024-10-01T09:59:00-05:00",
      "tareas_procesadas": 2100,
      "tasa_error": 0.01
    },
    "learning": {
      "estado": "idle",
      "modelo": "deepseek-r1 + gemini-pro",
      "proveedor": "groq + google",
      "ultima_ejecucion": "2024-09-30T23:00:00-05:00",
      "tareas_procesadas": 30,
      "tasa_error": 0.00
    }
  }
}
```

---

#### `GET /dashboard/alertas`

Obtiene alertas de excepción que requieren intervención humana (HITL).

**Request**
```bash
curl http://localhost:8000/api/v1/dashboard/alertas
```

**Query Parameters**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `severidad` | string | null | Filtrar: `alta`, `media`, `baja` |
| `estado` | string | null | Filtrar: `pendiente_revision`, `aprobada`, `rechazada` |
| `skip` | int | 0 | Registros para saltar |
| `limit` | int | 50 | Máximo de registros |

**Response 200**
```json
{
  "status": "success",
  "total_alertas": 2,
  "alertas": [
    {
      "id": 1,
      "tipo": "anomalia_factura",
      "severidad": "alta",
      "mensaje": "Factura #4001: Monto 500% superior al promedio histórico del cliente",
      "factura_id": 4001,
      "cliente_id": 1005,
      "cliente_nombre": "María García Romero",
      "monto_actual": 21500.00,
      "monto_promedio": 4300.00,
      "diferencia_porcentaje": 500.0,
      "fecha": "2024-10-01T09:30:00-05:00",
      "estado": "pendiente_revision",
      "agente_detector": "billing_agent",
      "accion_sugerida": "Revisar consistencia de servicios facturados"
    },
    {
      "id": 2,
      "tipo": "cambio_score",
      "severidad": "media",
      "mensaje": "Cliente #1005: Score de confianza bajó de 0.52 a 0.45",
      "cliente_id": 1005,
      "cliente_nombre": "María García Romero",
      "score_anterior": 0.52,
      "score_actual": 0.45,
      "diferencia": -0.07,
      "fecha": "2024-10-01T08:15:00-05:00",
      "estado": "pendiente_revision",
      "agente_detector": "learning_agent",
      "accion_sugerida": "Evaluar si el cliente requiere cambio de condiciones"
    }
  ]
}
```

**Tipos de Alerta**:

| Tipo | Descripción | Severidad Típica |
|------|-------------|------------------|
| `anomalia_factura` | Factura con monto anormal | Alta |
| `cambio_score` | Cambio significativo en score de confianza | Media |
| `error_sistema` | Error en algún componente | Alta |
| `limite_credito` | Cliente cerca del límite de crédito | Media |
| `disputa_recurrente` | Cliente con disputas frecuentes | Baja |

---

### 3. Billing (Facturación)

#### `POST /billing/ciclos/ejecutar`

Inicia un ciclo de facturación. El Agente Supervisor orquesta todo el proceso.

**Request**
```bash
curl -X POST http://localhost:8000/api/v1/billing/ciclos/ejecutar \
  -H "Content-Type: application/json" \
  -d '{
    "ciclo_id": 15,
    "force_human_review": false
  }'
```

**Body Parameters**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `ciclo_id` | int | Sí | ID del ciclo de facturación (5, 10, 15, 20, 25, 30) |
| `force_human_review` | bool | No | Forzar revisión humana de todas las facturas |

**Response 200 (Completado)**
```json
{
  "status": "completed",
  "cycle_id": 15,
  "steps": [
    {
      "step": "validate_cycle",
      "agent": "supervisor",
      "action": "Validando ciclo de facturación #15",
      "timestamp": "2024-10-01T10:00:00-05:00",
      "duration_ms": 45
    },
    {
      "step": "execute_billing",
      "agent": "billing",
      "action": "Ejecutando facturación para 150 cuentas",
      "timestamp": "2024-10-01T10:00:01-05:00",
      "duration_ms": 12500
    },
    {
      "step": "check_anomalies",
      "agent": "supervisor",
      "action": "Verificando anomalías en facturación",
      "timestamp": "2024-10-01T10:00:14-05:00",
      "duration_ms": 230
    }
  ],
  "resultados": {
    "total_cuentas": 150,
    "facturas_emitidas": 148,
    "facturas_validadas_auto": 120,
    "facturas_pendientes_revision": 2,
    "errores": 0
  },
  "requires_human_review": false,
  "execution_time_ms": 12775
}
```

**Response 200 (Requiere HITL)**
```json
{
  "status": "pending_human_review",
  "cycle_id": 15,
  "steps": [
    {
      "step": "validate_cycle",
      "agent": "supervisor",
      "action": "Validando ciclo de facturación #15"
    },
    {
      "step": "execute_billing",
      "agent": "billing",
      "action": "Ejecutando facturación"
    },
    {
      "step": "human_review",
      "agent": "human_review",
      "action": "2 facturas requieren revisión humana",
      "facturas_pendientes": [4001, 4002]
    }
  ],
  "requires_human_review": true,
  "facturas_revision": [
    {
      "factura_id": 4001,
      "cliente": "María García Romero",
      "monto": 21500.00,
      "motivo": "Monto 500% superior al promedio"
    }
  ]
}
```

**Response 400 (Ciclo Inválido)**
```json
{
  "status": "error",
  "detail": "Ciclo de facturación inválido. Valores permitidos: 5, 10, 15, 20, 25, 30",
  "error_type": "ValidationError"
}
```

---

#### `GET /billing/facturas`

Lista facturas con filtros opcionales.

**Request**
```bash
curl "http://localhost:8000/api/v1/billing/facturas?skip=0&limit=20&estado=Pendiente"
```

**Query Parameters**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Registros para saltar (paginación) |
| `limit` | int | 100 | Máximo de registros (1-500) |
| `estado` | string | null | `Pendiente`, `Pagado`, `Vencido`, `Anulado` |
| `cliente_id` | int | null | Filtrar por ID de cliente |
| `desde` | string | null | Fecha desde (YYYY-MM-DD) |
| `hasta` | string | null | Fecha hasta (YYYY-MM-DD) |
| `validacion` | string | null | `automatica` o `manual` |

**Response 200**
```json
{
  "status": "success",
  "total": 450,
  "skip": 0,
  "limit": 20,
  "facturas": [
    {
      "id_factura": "S9AA-0083159839",
      "id_cuenta": "129741406",
      "f_emision": "2026-07-01",
      "f_vencimiento": "2026-07-17",
      "importe_total": 63.63,
      "estado_pago": "Vencido",
      "validacion_automatica": true
    },
    {
      "id_factura": "S9AA-0083349818",
      "id_cuenta": "789189737",
      "f_emision": "2026-07-01",
      "f_vencimiento": "2026-07-17",
      "importe_total": 59.15,
      "estado_pago": "Vencido",
      "validacion_automatica": true
    }
  ]
}
```

---

#### `GET /billing/facturas/{factura_id}`

Obtiene el detalle completo de una factura específica.

**Request**
```bash
curl http://localhost:8000/api/v1/billing/facturas/4001
```

**Path Parameters**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `factura_id` | int | ID de la factura |

**Response 200**
```json
{
  "status": "success",
  "factura": {
    "id_factura": 4001,
    "id_cuenta": 2001,
    "serie": "F001",
    "correlativo": 1,
    "f_emision": "2024-10-01",
    "f_vencimiento": "2024-10-15",
    "subtotal_gravado": 3644.07,
    "igv_total": 655.93,
    "importe_total": 4300.00,
    "estado_pago": "Pendiente",
    "validacion_automatica": true,
    "dias_para_vencimiento": 14,
    "cliente": {
      "id_cliente": 1001,
      "tipo_doc": "6",
      "num_doc": "20100000001",
      "nombre": "Integratel Tech S.A.C.",
      "segmento": "B2B",
      "email": "facturacion@integratel-tech.com",
      "score_confianza": 0.92
    },
    "detalles": [
      {
        "id_detalle": 1,
        "id_servicio": 3001,
        "concepto": "Servicio Fibra Óptica - Octubre 2024",
        "tecnologia": "Fibra Óptica",
        "identificador_recurso": "FO-LIMA-001",
        "periodo_inicio": "2024-10-01",
        "periodo_fin": "2024-10-31",
        "dias_facturados": 31,
        "monto_linea": 2500.00
      },
      {
        "id_detalle": 2,
        "id_servicio": 3002,
        "concepto": "Servicio Cloud - Octubre 2024",
        "tecnologia": "Cloud",
        "identificador_recurso": "CLOUD-001",
        "periodo_inicio": "2024-10-01",
        "periodo_fin": "2024-10-31",
        "dias_facturados": 31,
        "monto_linea": 1800.00
      }
    ],
    "ofertas": [
      {
        "id_oferta": 1,
        "descuento_ofrecido": 5.0,
        "descuento_monto": 215.00,
        "nuevo_total": 4085.00,
        "nuevo_plazo_dias": 5,
        "fecha_limite_aceptacion": "2024-10-13",
        "estado": "pendiente"
      }
    ],
    "historial_pagos_relacionados": [
      {
        "fecha_vencimiento": "2024-09-15",
        "fecha_pago": "2024-09-13",
        "dias_mora": 0,
        "monto_pagado": 4300.00
      }
    ],
    "created_at": "2024-10-01T10:00:00-05:00"
  }
}
```

**Response 404**
```json
{
  "status": "error",
  "detail": "Factura no encontrada",
  "error_type": "NotFoundError"
}
```

---

#### `POST /billing/facturas/{factura_id}/validar`

Valida manualmente una factura que requiere revisión humana (HITL).

**Request**
```bash
curl -X POST http://localhost:8000/api/v1/billing/facturas/4001/validar \
  -H "Content-Type: application/json" \
  -d '{
    "aprobado_por": "juan.perez@integratel.com",
    "comentario": "Factura verificada, servicios correctos"
  }'
```

**Body Parameters**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `aprobado_por` | string | Sí | Email del aprobador |
| `comentario` | string | No | Comentario de la validación |

**Response 200**
```json
{
  "status": "success",
  "message": "Factura validada manualmente",
  "factura_id": 4001,
  "validado_por": "juan.perez@integratel.com",
  "fecha_validacion": "2024-10-01T10:30:00-05:00",
  "nuevo_estado": "Pendiente"
}
```

**Response 400 (Factura ya validada)**
```json
{
  "status": "error",
  "detail": "La factura ya fue validada (validación automática)",
  "error_type": "ValidationError"
}
```

---

### 4. Clients (Clientes)

#### `GET /clients/`

Lista clientes con filtros opcionales.

**Request**
```bash
curl "http://localhost:8000/api/v1/clients/?segmento=B2B&skip=0&limit=20"
```

**Query Parameters**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Registros para saltar |
| `limit` | int | 100 | Máximo de registros (1-500) |
| `segmento` | string | null | `B2B`, `B2C`, `Gobierno` |
| `score_min` | float | null | Score de confianza mínimo (0-1) |
| `score_max` | float | null | Score de confianza máximo (0-1) |

**Response 200**
```json
{
  "status": "success",
  "total": 350,
  "skip": 0,
  "limit": 20,
  "clientes": [
    {
      "id_cliente": "2042422772",
      "nombre": "CLIENT_00369",
      "segmento": "SEGMENTO_002",
      "score_confianza": 0.80
    },
    {
      "id_cliente": "2006917349",
      "nombre": "CLIENT_00708",
      "segmento": "SEGMENTO_002",
      "score_confianza": 0.80
    }
  ]
}
```

---

#### `GET /clients/{cliente_id}`

Obtiene información detallada de un cliente.

**Request**
```bash
curl http://localhost:8000/api/v1/clients/1001
```

**Response 200**
```json
{
  "status": "success",
  "cliente": {
    "id_cliente": 1001,
    "tipo_doc": "6",
    "num_doc": "20100000001",
    "nombre_razon_social": "Integratel Tech S.A.C.",
    "segmento": "B2B",
    "email_contacto": "facturacion@integratel-tech.com",
    "telefono_contacto": "+51999888777",
    "score_confianza": 0.92,
    "es_confiable": true,
    "factores_score": {
      "antiguedad_meses": 36,
      "promedio_mora_dias": 0.5,
      "num_disputas_ultimo_anio": 0,
      "num_pagos_tarde": 1,
      "monto_promedio": 4300.00
    },
    "cuentas": [
      {
        "id_cuenta": 2001,
        "ciclo_facturacion": 15,
        "metodo_pago": "Transferencia",
        "estado_cuenta": "Activo",
        "limite_credito": 50000.00,
        "dias_plazo_estandar": 15,
        "servicios_activos": [
          {
            "id_servicio": 3001,
            "tecnologia": "Fibra Óptica",
            "identificador_recurso": "FO-LIMA-001",
            "cargo_fijo_mensual": 2500.00,
            "fecha_alta": "2023-01-15",
            "estado_servicio": "Activo"
          },
          {
            "id_servicio": 3002,
            "tecnologia": "Cloud",
            "identificador_recurso": "CLOUD-001",
            "cargo_fijo_mensual": 1800.00,
            "fecha_alta": "2023-03-01",
            "estado_servicio": "Activo"
          }
        ]
      }
    ],
    "estadisticas": {
      "total_facturado_anio": 51600.00,
      "promedio_mensual": 4300.00,
      "total_pagos_tarde": 1,
      "total_disputas": 0,
      "antiguedad_dias": 1095
    }
  }
}
```

---

#### `GET /clients/{cliente_id}/historial-facturas`

Obtiene el historial de facturas de un cliente.

**Request**
```bash
curl "http://localhost:8000/api/v1/clients/1001/historial-facturas?skip=0&limit=12"
```

**Query Parameters**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Registros para saltar |
| `limit` | int | 50 | Máximo de registros (1-200) |
| `anio` | int | null | Filtrar por año |
| `mes` | int | null | Filtrar por mes (1-12) |

**Response 200**
```json
{
  "status": "success",
  "cliente_id": 1001,
  "total": 24,
  "facturas": [
    {
      "id_factura": 4001,
      "serie": "F001",
      "correlativo": 1,
      "f_emision": "2024-10-01",
      "f_vencimiento": "2024-10-15",
      "importe_total": 4300.00,
      "estado_pago": "Pendiente",
      "fecha_pago": null,
      "dias_mora": 0
    },
    {
      "id_factura": 3950,
      "serie": "F001",
      "correlativo": 50,
      "f_emision": "2024-09-01",
      "f_vencimiento": "2024-09-15",
      "importe_total": 4300.00,
      "estado_pago": "Pagado",
      "fecha_pago": "2024-09-13",
      "dias_mora": 0
    }
  ]
}
```

---

#### `GET /clients/{cliente_id}/score`

Obtiene el score de confianza detallado de un cliente.

**Request**
```bash
curl http://localhost:8000/api/v1/clients/1001/score
```

**Response 200**
```json
{
  "status": "success",
  "cliente_id": 1001,
  "score_actual": 0.92,
  "es_confiable": true,
  "factores": {
    "antiguedad": {
      "valor": 36,
      "unidad": "meses",
      "peso": 0.25,
      "contribucion": 0.23
    },
    "promedio_mora": {
      "valor": 0.5,
      "unidad": "dias",
      "peso": 0.30,
      "contribucion": 0.28
    },
    "disputas": {
      "valor": 0,
      "unidad": "disputas/año",
      "peso": 0.20,
      "contribucion": 0.20
    },
    "pagos_tarde": {
      "valor": 1,
      "unidad": "pagos/año",
      "peso": 0.15,
      "contribucion": 0.13
    },
    "monto_promedio": {
      "valor": 4300.00,
      "unidad": "S/",
      "peso": 0.10,
      "contribucion": 0.08
    }
  },
  "historial_cambios": [
    {
      "fecha": "2024-09-01",
      "score_anterior": 0.90,
      "score_nuevo": 0.92,
      "motivo": "Pago puntual consistente por 3 meses"
    }
  ],
  "proxima_actualizacion": "2024-11-01"
}
```

---

### 5. Collections (Cobranzas)

#### `GET /collections/facturas-vencidas`

Lista facturas vencidas con su etapa de mora.

**Request**
```bash
curl "http://localhost:8000/api/v1/collections/facturas-vencidas?etapa=critica"
```

**Query Parameters**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Registros para saltar |
| `limit` | int | 100 | Máximo de registros |
| `etapa` | string | null | `temprana`, `media`, `tardia`, `critica` |

**Response 200**
```json
{
  "status": "success",
  "total_vencidas": 45,
  "por_etapa": {
    "temprana": 20,
    "media": 12,
    "tardia": 8,
    "critica": 5
  },
  "facturas": [
    {
      "id_factura": 3900,
      "cliente_id": 1005,
      "cliente_nombre": "María García Romero",
      "importe_total": 120.00,
      "f_vencimiento": "2024-08-15",
      "dias_mora": 47,
      "etapa": "critica",
      "interes_tamn_acumulado": 15.60,
      "total_deuda": 135.60,
      "score_confianza": 0.45,
      "estrategia_recomendada": {
        "canal": "carta_notarial",
        "tono": "aviso_legal",
        "frecuencia": "semanal",
        "ofrecer_negociacion": false
      }
    }
  ]
}
```

---

#### `POST /collections/calcular-tamn/{factura_id}`

Calcula los intereses moratorios TAMN para una factura vencida.

**Request**
```bash
curl -X POST http://localhost:8000/api/v1/collections/calcular-tamn/3900
```

**Response 200**
```json
{
  "status": "success",
  "factura_id": 3900,
  "calculo": {
    "monto_deuda_original": 120.00,
    "dias_mora": 47,
    "tasa_tamn_anual": 0.1525,
    "factor_vencimiento": 1.000000,
    "factor_actual": 1.019840,
    "interes_tamn": 15.60,
    "total_pagar": 135.60,
    "fecha_calculo": "2024-10-01",
    "proyeccion_30_dias": {
      "interes_proyectado": 25.30,
      "total_proyectado": 145.30
    }
  }
}
```

**Response 404**
```json
{
  "status": "error",
  "detail": "Factura no encontrada o no está vencida",
  "error_type": "NotFoundError"
}
```

---

#### `POST /collections/procesar-pago`

Registra un pago y concilia con la factura correspondiente.

**Request**
```bash
curl -X POST http://localhost:8000/api/v1/collections/procesar-pago \
  -H "Content-Type: application/json" \
  -d '{
    "factura_id": 3900,
    "monto_pagado": 135.60,
    "fecha_pago": "2024-10-01",
    "comprobante_pago": "OPE-12345678",
    "canal_pago": "Transferencia"
  }'
```

**Body Parameters**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `factura_id` | int | Sí | ID de la factura |
| `monto_pagado` | float | Sí | Monto pagado por el cliente |
| `fecha_pago` | string | Sí | Fecha del pago (YYYY-MM-DD) |
| `comprobante_pago` | string | No | Número de comprobante |
| `canal_pago` | string | No | Canal por el que se realizó el pago |

**Response 200**
```json
{
  "status": "success",
  "message": "Pago procesado correctamente",
  "factura_id": 3900,
  "monto_pagado": 135.60,
  "monto_deuda": 120.00,
  "interes_cubierto": 15.60,
  "nuevo_estado": "Pagado",
  "fecha_conciliacion": "2024-10-01T11:00:00-05:00"
}
```

---

### 6. Negotiations (Negociación)

#### `GET /negotiations/ofertas`

Lista ofertas de negociación con filtros.

**Request**
```bash
curl "http://localhost:8000/api/v1/negotiations/ofertas?estado=pendiente&skip=0&limit=20"
```

**Query Parameters**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Registros para saltar |
| `limit` | int | 50 | Máximo de registros (1-200) |
| `estado` | string | null | `pendiente`, `aceptada`, `rechazada`, `expirada` |
| `cliente_id` | int | null | Filtrar por cliente |

**Response 200**
```json
{
  "status": "success",
  "total": 15,
  "ofertas": [
    {
      "id_oferta": 1,
      "id_factura": 4001,
      "cliente": {
        "id_cliente": 1001,
        "nombre": "Integratel Tech S.A.C."
      },
      "fecha_oferta": "2024-10-10",
      "descuento_ofrecido": 5.0,
      "descuento_monto": 215.00,
      "monto_original": 4300.00,
      "nuevo_total": 4085.00,
      "nuevo_plazo_dias": 5,
      "fecha_limite_aceptacion": "2024-10-13",
      "dias_restantes": 3,
      "estado": "pendiente",
      "probabilidad_aceptacion": 0.72
    }
  ]
}
```

---

#### `POST /negotiations/ofertas/{oferta_id}/aceptar`

Cliente acepta una oferta de negociación.

**Request**
```bash
curl -X POST http://localhost:8000/api/v1/negotiations/ofertas/1/aceptar
```

**Response 200**
```json
{
  "status": "success",
  "message": "Oferta aceptada exitosamente",
  "oferta_id": 1,
  "factura_id": 4001,
  "nuevo_total": 4085.00,
  "ahorro_cliente": 215.00,
  "nueva_fecha_vencimiento": "2024-10-20",
  "acciones_realizadas": [
    "Nota de crédito generada: NC001-0001",
    "Fecha de vencimiento actualizada",
    "Notificación enviada al cliente"
  ]
}
```

---

#### `POST /negotiations/ofertas/{oferta_id}/rechazar`

Cliente rechaza una oferta de negociación.

**Request**
```bash
curl -X POST http://localhost:8000/api/v1/negotiations/ofertas/1/rechazar
```

**Response 200**
```json
{
  "status": "success",
  "message": "Oferta rechazada",
  "oferta_id": 1,
  "factura_id": 4001,
  "accion_siguiente": "Se enviará recordatorio de pago 2 días antes del vencimiento original"
}
```

---

### 7. Audit (Auditoría)

#### `GET /audit/log`

Obtiene el log de auditoría de todas las acciones de los agentes.

**Request**
```bash
curl "http://localhost:8000/api/v1/audit/log?agente=billing&accion=ejecutar_facturacion&skip=0&limit=50"
```

**Query Parameters**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Registros para saltar |
| `limit` | int | 100 | Máximo de registros (1-500) |
| `agente` | string | null | Filtrar por nombre de agente |
| `accion` | string | null | Filtrar por tipo de acción |
| `resultado` | string | null | `success`, `error`, `warning` |
| `desde` | string | null | Fecha desde (ISO 8601) |
| `hasta` | string | null | Fecha hasta (ISO 8601) |

**Response 200**
```json
{
  "status": "success",
  "total": 1250,
  "skip": 0,
  "limit": 50,
  "logs": [
    {
      "id": 1001,
      "timestamp": "2024-10-01T10:00:00-05:00",
      "agente": "billing_agent",
      "modelo": "deepseek-r1",
      "proveedor": "groq",
      "accion": "ejecutar_facturacion",
      "resultado": "success",
      "detalle_resumen": {
        "cuenta_id": 2001,
        "factura_id": 4001,
        "monto": 4300.00,
        "validacion": "automatica",
        "score_confianza": 0.92
      },
      "duracion_ms": 245,
      "tokens_utilizados": 150
    },
    {
      "id": 1002,
      "timestamp": "2024-10-01T10:00:01-05:00",
      "agente": "billing_agent",
      "modelo": "deepseek-r1",
      "proveedor": "groq",
      "accion": "deteccion_anomalia",
      "resultado": "warning",
      "detalle_resumen": {
        "cuenta_id": 2005,
        "factura_id": 4002,
        "monto": 21500.00,
        "motivo": "Monto 500% superior al promedio"
      },
      "duracion_ms": 180,
      "tokens_utilizados": 200
    }
  ]
}
```

---

#### `GET /audit/log/{action_id}`

Obtiene el detalle completo de una acción de auditoría específica.

**Request**
```bash
curl http://localhost:8000/api/v1/audit/log/1001
```

**Response 200**
```json
{
  "status": "success",
  "audit_detail": {
    "id": 1001,
    "timestamp": "2024-10-01T10:00:00-05:00",
    "agente": "billing_agent",
    "modelo": "deepseek-r1",
    "proveedor": "groq",
    "version_agente": "1.0.0",
    "accion": "ejecutar_facturacion",
    "resultado": "success",
    "input": {
      "cuenta_id": 2001,
      "periodo": "2024-10",
      "servicios": [3001, 3002]
    },
    "output": {
      "factura_id": 4001,
      "subtotal": 3644.07,
      "igv": 655.93,
      "total": 4300.00,
      "validacion_automatica": true
    },
    "llm_interaction": {
      "prompt": "Analiza los siguientes datos de facturación...",
      "response": "Facturación completada. No se detectaron anomalías.",
      "tokens_input": 100,
      "tokens_output": 50,
      "model": "deepseek-r1-distill-llama-70b",
      "temperature": 0.0
    },
    "symbolic_engine_calls": [
      {
        "funcion": "calcular_prorrateo_pxq",
        "parametros": {
          "cargo_fijo": 2500.00,
          "fecha_inicio": "2024-10-01",
          "fecha_fin": "2024-10-31"
        },
        "resultado": 2500.00
      },
      {
        "funcion": "calcular_igv_desde_base",
        "parametros": {
          "base_imponible": 3644.07
        },
        "resultado": 655.93
      }
    ],
    "duracion_ms": 245,
    "trace_id": "abc123-def456-ghi789"
  }
}
```

---

## WebSockets

### Conexión al Dashboard

```javascript
const ws = new WebSocket("ws://localhost:8000/api/v1/ws/dashboard");

ws.onopen = () => {
  console.log("Conectado al dashboard de SON-IA");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Actualización recibida:", data);
};
```

**Mensajes del Servidor**:

| Tipo | Descripción | Payload |
|------|-------------|---------|
| `connection_established` | Conexión exitosa | `{ "type": "connection_established", "message": "..." }` |
| `metrics_update` | Actualización de métricas | `{ "type": "metrics_update", "metrics": {...} }` |
| `agent_status_change` | Cambio de estado de agente | `{ "type": "agent_status_change", "agent": "...", "status": "..." }` |
| `new_alert` | Nueva alerta HITL | `{ "type": "new_alert", "alert": {...} }` |
| `billing_cycle_complete` | Ciclo facturación completado | `{ "type": "billing_cycle_complete", "cycle_id": 15, "results": {...} }` |

---

### Conexión del Cliente

```javascript
const clienteId = 1001;
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/cliente/${clienteId}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case "new_invoice":
      console.log("Nueva factura disponible:", data.invoice);
      break;
    case "payment_confirmed":
      console.log("Pago confirmado:", data.payment);
      break;
    case "new_offer":
      console.log("Nueva oferta de negociación:", data.offer);
      break;
    case "reminder":
      console.log("Recordatorio:", data.message);
      break;
  }
};
```

---

## Modelos de Datos

### Cliente

```json
{
  "id_cliente": 1001,
  "tipo_doc": "6",
  "num_doc": "20100000001",
  "nombre_razon_social": "Integratel Tech S.A.C.",
  "segmento": "B2B",
  "email_contacto": "facturacion@integratel-tech.com",
  "telefono_contacto": "+51999888777",
  "score_confianza": 0.92
}
```

### Factura

```json
{
  "id_factura": 4001,
  "id_cuenta": 2001,
  "serie": "F001",
  "correlativo": 1,
  "f_emision": "2024-10-01",
  "f_vencimiento": "2024-10-15",
  "subtotal_gravado": 3644.07,
  "igv_total": 655.93,
  "importe_total": 4300.00,
  "estado_pago": "Pendiente",
  "validacion_automatica": true
}
```

### Oferta de Negociación

```json
{
  "id_oferta": 1,
  "id_factura": 4001,
  "fecha_oferta": "2024-10-10",
  "descuento_ofrecido": 5.0,
  "nuevo_plazo_dias": 5,
  "fecha_limite_aceptacion": "2024-10-13",
  "estado": "pendiente"
}
```

---

## Rate Limiting

| Endpoint | Límite | Ventana |
|----------|--------|---------|
| Todos los endpoints | 100 requests | Por minuto (por IP) |
| POST /billing/ciclos/ejecutar | 10 requests | Por hora |
| POST /collections/procesar-pago | 60 requests | Por minuto |

**Response 429 (Rate Limit Excedido)**:
```json
{
  "status": "error",
  "detail": "Demasiadas solicitudes. Intente de nuevo en 30 segundos.",
  "error_type": "RateLimitError",
  "retry_after_seconds": 30
}
```

