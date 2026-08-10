# 📄 `docs/deployment.md`

```markdown
# 🚀 Guía de Despliegue - SON-IA

## Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Configuración del Entorno](#configuración-del-entorno)
3. [Despliegue con Docker Compose](#despliegue-con-docker-compose)
4. [Despliegue en Producción](#despliegue-en-producción)
5. [Configuración de Cloud](#configuración-de-cloud)
6. [CI/CD con GitHub Actions](#cicd-con-github-actions)
7. [Monitoreo y Logging](#monitoreo-y-logging)
8. [Backup y Recuperación](#backup-y-recuperación)
9. [Plan de Contingencia](#plan-de-contingencia)
10. [Checklist de Producción](#checklist-de-producción)

---

## Requisitos del Sistema

### Hardware Mínimo

| Entorno | CPU | RAM | Almacenamiento |
|---------|-----|-----|----------------|
| **Desarrollo** | 4 cores | 8 GB | 20 GB SSD |
| **Producción (Pequeño)** | 8 cores | 16 GB | 100 GB SSD |
| **Producción (Mediano)** | 16 cores | 32 GB | 250 GB SSD |
| **Producción (Grande)** | 32 cores | 64 GB | 500 GB SSD |

### Software Requerido

| Componente | Desarrollo | Producción |
|------------|------------|------------|
| **Sistema Operativo** | Ubuntu 22.04+ / macOS 13+ | Ubuntu 22.04 LTS |
| **Docker** | 24.0+ | 24.0+ |
| **Docker Compose** | 2.20+ | 2.20+ (o Kubernetes) |
| **Python** | 3.11+ | 3.11+ (en contenedor) |
| **Node.js** | 20+ | 20+ (en contenedor) |
| **PostgreSQL** | 16 | 16 (managed o contenedor) |
| **Redis** | 7 | 7 (managed o contenedor) |
| **Nginx** | - | 1.24+ (reverse proxy) |

### APIs Externas Requeridas

| API | Cuenta Necesaria | Límites |
|-----|------------------|---------|
| **Groq** (DeepSeek-R1) | [console.groq.com](https://console.groq.com) | Plan gratuito: 30 req/min |
| **Google Gemini** | [aistudio.google.com](https://aistudio.google.com) | Cuota gratuita: 60 req/min |
| **Pinecone** (Vector DB) | [pinecone.io](https://pinecone.io) | Tier gratuito: 1 índice |
| **Twilio** (SMS/WhatsApp) | [twilio.com](https://twilio.com) | Pay-as-you-go |
| **SMTP** | Gmail SMTP o SendGrid | Según proveedor |

---

## Configuración del Entorno

### Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```bash
# ============================================
# Application
# ============================================
APP_NAME=SON-IA
APP_VERSION=0.1.0
ENVIRONMENT=production          # development | staging | production
DEBUG=false                     # false en producción
SECRET_KEY=<generar-seguro>     # openssl rand -hex 32

# ============================================
# Database - PostgreSQL
# ============================================
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=sonia_db
POSTGRES_USER=sonia_user
POSTGRES_PASSWORD=<password-seguro>

# ============================================
# Redis
# ============================================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<password-seguro>

# ============================================
# Groq API (DeepSeek-R1)
# ============================================
GROQ_API_KEY=gsk_xxxxxxxxxxxx
GROQ_MODEL=deepseek-r1-distill-llama-70b

# ============================================
# Google Gemini API
# ============================================
GEMINI_API_KEY=xxxxxxxxxxxx
GEMINI_MODEL_PRO=gemini-1.5-pro
GEMINI_MODEL_FLASH=gemini-1.5-flash

# ============================================
# Pinecone (Vector DB)
# ============================================
PINECONE_API_KEY=xxxxxxxxxxxx
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX=sonia-embeddings

# ============================================
# Celery
# ============================================
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# ============================================
# Email (SMTP)
# ============================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notifications@integratel.com
SMTP_PASSWORD=<app-password>

# ============================================
# Twilio (WhatsApp/SMS)
# ============================================
TWILIO_ACCOUNT_SID=xxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+51999999999

# ============================================
# CORS (Producción)
# ============================================
CORS_ORIGINS=https://sonia.integratel.com,https://admin.sonia.integratel.com

# ============================================
# Sentry (Error Tracking)
# ============================================
SENTRY_DSN=https://xxxxxxxx@sentry.io/xxxxxxx
```

### Generar Secretos Seguros

```bash
# Generar SECRET_KEY
openssl rand -hex 32

# Generar contraseña PostgreSQL
openssl rand -base64 24

# Generar contraseña Redis
openssl rand -base64 24
```

---

## Despliegue con Docker Compose

### docker-compose.yml (Desarrollo)

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: sonia-backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - /app/__pycache__
    env_file:
      - ./backend/.env
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - sonia-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: sonia-frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    env_file:
      - ./frontend/.env.local
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    command: npm run dev
    networks:
      - sonia-network

  postgres:
    image: postgres:16-alpine
    container_name: sonia-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-sonia_db}
      POSTGRES_USER: ${POSTGRES_USER:-sonia_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-sonia_password}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-sonia_user} -d ${POSTGRES_DB:-sonia_db}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - sonia-network

  redis:
    image: redis:7-alpine
    container_name: sonia-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-}
    networks:
      - sonia-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: sonia-celery-worker
    command: celery -A app.tasks.celery_app worker -l info -c 4
    env_file:
      - ./backend/.env
    depends_on:
      - redis
      - postgres
    networks:
      - sonia-network

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: sonia-celery-beat
    command: celery -A app.tasks.celery_app beat -l info
    env_file:
      - ./backend/.env
    depends_on:
      - redis
      - postgres
    networks:
      - sonia-network

  flower:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: sonia-flower
    command: celery -A app.tasks.celery_app flower --port=5555
    ports:
      - "5555:5555"
    env_file:
      - ./backend/.env
    depends_on:
      - redis
    networks:
      - sonia-network

volumes:
  postgres_data:
  redis_data:

networks:
  sonia-network:
    driver: bridge
```

### Comandos de Operación

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver estado de los servicios
docker-compose ps

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f celery-worker

# Reiniciar un servicio
docker-compose restart backend

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (RESET completo)
docker-compose down -v

# Sembrar datos de prueba
docker-compose exec backend python scripts/seed-database.py

# Ejecutar migraciones
docker-compose exec backend alembic upgrade head

# Ejecutar tests
docker-compose exec backend pytest

# Acceder a shell del backend
docker-compose exec backend bash
```

---

## Despliegue en Producción

### Arquitectura de Producción

```
                         ┌──────────────┐
                         │   Internet   │
                         └──────┬───────┘
                                │
                         ┌──────┴───────┐
                         │  Cloudflare  │
                         │  (DNS + CDN) │
                         └──────┬───────┘
                                │
                         ┌──────┴───────┐
                         │    Nginx     │
                         │ Reverse Proxy│
                         └──────┬───────┘
                                │
                 ┌──────────────┼──────────────┐
                 │              │              │
                 ▼              ▼              ▼
          ┌────────────┐ ┌────────────┐ ┌────────────┐
          │ Frontend   │ │ Backend   │ │ Backend    │
          │ (Next.js)  │ │ Instance 1│ │ Instance 2 │
          └────────────┘ └─────┬──────┘ └─────┬──────┘
                               │              │
                               └──────┬───────┘
                                      │
                      ┌───────────────┼───────────────┐
                      │               │               │
                      ▼               ▼               ▼
               ┌────────────┐ ┌────────────┐ ┌────────────┐
               │ PostgreSQL │ │   Redis    │ │  Pinecone  │
               │  Primary   │ │  Sentinel  │ │  (Cloud)   │
               └─────┬──────┘ └────────────┘ └────────────┘
                     │
                     ▼
               ┌────────────┐
               │ PostgreSQL │
               │  Replica   │
               └────────────┘
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/sonia-api

upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;  # Instancia adicional
    keepalive 32;
}

upstream frontend {
    server 127.0.0.1:3000;
    keepalive 32;
}

server {
    listen 80;
    server_name api.sonia.integratel.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.sonia.integratel.com;

    ssl_certificate /etc/letsencrypt/live/api.sonia.integratel.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.sonia.integratel.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    limit_req zone=api_limit burst=20 nodelay;

    # Logs
    access_log /var/log/nginx/sonia-api-access.log;
    error_log /var/log/nginx/sonia-api-error.log;

    # Headers de Seguridad
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Proxy al Backend
    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400s;
    }

    # Límite de tamaño de upload
    client_max_body_size 10M;
}
```

### Dockerfile de Producción (Backend)

```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN useradd -m -u 1000 sonia && chown -R sonia:sonia /app
USER sonia

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: sonia-backend-prod
    expose:
      - "8000"
    env_file:
      - ./backend/.env
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - WORKERS=4
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - sonia-network
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: sonia-celery-prod
    command: celery -A app.tasks.celery_app worker -l info -c 4
    env_file:
      - ./backend/.env
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    networks:
      - sonia-network

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: sonia-celery-beat-prod
    command: celery -A app.tasks.celery_app beat -l info
    env_file:
      - ./backend/.env
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    networks:
      - sonia-network

  postgres:
    image: postgres:16-alpine
    container_name: sonia-postgres-prod
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./scripts/backup.sh:/backup.sh
    restart: unless-stopped
    networks:
      - sonia-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: sonia-redis-prod
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_prod_data:/data
    restart: unless-stopped
    networks:
      - sonia-network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    container_name: sonia-nginx-prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/sites-enabled:/etc/nginx/sites-enabled
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - sonia-network

volumes:
  postgres_prod_data:
  redis_prod_data:

networks:
  sonia-network:
    driver: bridge
```

---

## Configuración de Cloud

### AWS (Amazon Web Services)

```yaml
# Infraestructura Recomendada en AWS:

Compute:
  - EC2 t3.large (2 vCPU, 8 GB RAM) x2 para Backend
  - EC2 t3.medium (2 vCPU, 4 GB RAM) x1 para Frontend
  - Auto Scaling Group para Backend (min: 2, max: 6)

Database:
  - RDS PostgreSQL 16 (db.t3.medium, Multi-AZ)
  - ElastiCache Redis 7 (cache.t3.micro, Multi-AZ opcional)

Storage:
  - S3 para backups y archivos estáticos
  - EBS gp3 para volúmenes de EC2

Networking:
  - VPC con subnets públicas y privadas
  - Application Load Balancer (ALB)
  - Route 53 para DNS
  - CloudFront como CDN

Security:
  - Security Groups restrictivos
  - WAF para protección web
  - Secrets Manager para API keys
  - ACM para certificados SSL
```

### Google Cloud Platform (GCP)

```yaml
# Infraestructura Recomendada en GCP:

Compute:
  - Cloud Run para Backend (serverless, escala a 0)
  - Cloud Run para Frontend

Database:
  - Cloud SQL PostgreSQL 16 (db-custom-2-8192)
  - Memorystore Redis 7 (Basic Tier)

Storage:
  - Cloud Storage para backups y archivos
  - Artifact Registry para imágenes Docker

Networking:
  - Cloud Load Balancing
  - Cloud CDN
  - Cloud DNS

Security:
  - Secret Manager para API keys
  - Cloud Armor para WAF
  - IAM para control de acceso
```

### Estimación de Costos Cloud (Mensual)

| Servicio | AWS (USD) | GCP (USD) | Descripción |
|----------|-----------|-----------|-------------|
| Compute (Backend) | $140 | $120 | 2 instancias / Cloud Run |
| Compute (Frontend) | $30 | $25 | 1 instancia / Cloud Run |
| PostgreSQL | $80 | $70 | RDS / Cloud SQL |
| Redis | $25 | $20 | ElastiCache / Memorystore |
| Load Balancer | $25 | $20 | ALB / Cloud LB |
| CDN + DNS | $15 | $10 | CloudFront + Route53 |
| S3 / Cloud Storage | $5 | $5 | Backups y archivos |
| **Total Estimado** | **$320** | **$270** | Por mes |

---

## CI/CD con GitHub Actions

### Workflow: Backend Tests + Deploy

```yaml
# .github/workflows/backend-deploy.yml
name: Backend CI/CD

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
  pull_request:
    branches: [main]
    paths:
      - 'backend/**'

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}-backend

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: sonia_test
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Lint with Ruff
      run: |
        cd backend
        pip install ruff
        ruff check app/
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql+asyncpg://test_user:test_password@localhost:5432/sonia_test
        REDIS_URL: redis://localhost:6379/0
        SECRET_KEY: test-secret
      run: |
        cd backend
        pytest -v --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        file: ./backend/coverage.xml
        flags: backend

  build-and-push:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        file: ./backend/Dockerfile.prod
        push: true
        tags: |
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - name: Deploy to server
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.DEPLOY_HOST }}
        username: ${{ secrets.DEPLOY_USER }}
        key: ${{ secrets.DEPLOY_SSH_KEY }}
        script: |
          cd /opt/son-ia
          docker-compose -f docker-compose.prod.yml pull backend
          docker-compose -f docker-compose.prod.yml up -d --no-deps backend
          docker image prune -f
```

---

## Monitoreo y Logging

### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: sonia-prometheus
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - sonia-network

  grafana:
    image: grafana/grafana:latest
    container_name: sonia-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3001:3000"
    networks:
      - sonia-network

  node-exporter:
    image: prom/node-exporter:latest
    container_name: sonia-node-exporter
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    networks:
      - sonia-network

volumes:
  prometheus_data:
  grafana_data:
```

### Sentry para Error Tracking

```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
    traces_sample_rate=1.0 if settings.DEBUG else 0.1,
    integrations=[FastApiIntegration()],
)
```

### Logging Estructurado

```python
# Configuración de structlog para producción
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),  # JSON en producción
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

---

## Backup y Recuperación

### Script de Backup Automático

```bash
#!/bin/bash
# scripts/backup.sh
# Backup automático de PostgreSQL

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
DB_NAME="sonia_db"
DB_USER="sonia_user"
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR

# Backup completo
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > "$BACKUP_DIR/sonia_backup_$TIMESTAMP.sql.gz"

# Backup solo schemas
pg_dump -U $DB_USER -h localhost --schema-only $DB_NAME | gzip > "$BACKUP_DIR/sonia_schema_$TIMESTAMP.sql.gz"

# Eliminar backups antiguos
find $BACKUP_DIR -name "sonia_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Log
echo "[$(date)] Backup completado: sonia_backup_$TIMESTAMP.sql.gz" >> /var/log/sonia-backup.log
```

### Cron para Backups

```cron
# Backup cada 6 horas
0 */6 * * * /opt/son-ia/scripts/backup.sh

# Backup semanal completo (domingo 2 AM)
0 2 * * 0 /opt/son-ia/scripts/backup-full.sh
```

### Recuperación desde Backup

```bash
# Restaurar desde el último backup
LATEST_BACKUP=$(ls -t /backups/postgres/sonia_backup_*.sql.gz | head -1)
gunzip -c $LATEST_BACKUP | psql -U $DB_USER -h localhost $DB_NAME

# Restaurar un backup específico
gunzip -c /backups/postgres/sonia_backup_20241001_120000.sql.gz | psql -U $DB_USER -h localhost $DB_NAME
```

---

## Plan de Contingencia

### Fases de Implementación

| Fase | Duración | Alcance | Métrica de Éxito |
|------|----------|---------|------------------|
| **Shadow Mode** | Mes 1 | IA en paralelo con proceso manual | 0% errores vs proceso manual |
| **Piloto Controlado** | Mes 2-3 | 20% → 50% → 100% de facturas | DSO reducido 2 días |
| **Producción Completa** | Mes 4+ | 100% automatizado | DSO reducido 5 días |

### Procedimiento de Rollback

```bash
#!/bin/bash
# scripts/rollback.sh

echo "⚠️ Iniciando rollback de SON-IA..."

# 1. Detener procesamiento automático
docker-compose exec backend python -c "
from app.agents.supervisor_agent import supervisor_agent
supervisor_agent.pause_all_agents()
"

# 2. Activar modo manual
export SONIA_MODE=manual
docker-compose restart backend

# 3. Restaurar último backup estable
LATEST_STABLE=$(ls -t /backups/postgres/sonia_backup_*.sql.gz | head -1)
gunzip -c $LATEST_STABLE | psql -U $DB_USER -h localhost $DB_NAME

# 4. Notificar al equipo
curl -X POST https://hooks.slack.com/services/xxx \
  -H "Content-Type: application/json" \
  -d '{"text":"🚨 Rollback de SON-IA ejecutado. Modo manual activado."}'

echo "✅ Rollback completado. Sistema en modo manual."
```

### Trigger Automáticos de Rollback

| Condición | Acción Automática |
|-----------|-------------------|
| Tasa de error > 5% en facturación | Pausar Agente de Facturación |
| 3 fallos consecutivos de Groq API | Cambiar a modo degradado (solo Gemini) |
| Detección de anomalía 5x en 10+ facturas | Rollback completo a modo manual |
| PostgreSQL no disponible | Activar caché Redis y notificar |
| Redis no disponible | Desactivar caché, operación directa |

---

## Checklist de Producción

### Antes del Despliegue

- [ ] `.env` configurado con valores de producción
- [ ] `DEBUG=false`
- [ ] `SECRET_KEY` generado de forma segura
- [ ] `CORS_ORIGINS` limitado a dominios de producción
- [ ] API keys de producción configuradas (Groq, Gemini, Pinecone)
- [ ] Base de datos con backups automáticos configurados
- [ ] SSL/TLS configurado y verificado
- [ ] Firewall y Security Groups configurados
- [ ] Monitoreo (Prometheus + Grafana) configurado
- [ ] Sentry DSN configurado
- [ ] Logs en formato JSON para ELK/CloudWatch
- [ ] Health checks configurados en load balancer
- [ ] Rate limiting activado
- [ ] Plan de rollback documentado y probado

### Verificación Post-Despliegue

- [ ] Health check responde 200: `curl https://api.sonia.integratel.com/api/v1/health`
- [ ] Dashboard métricas responde: `curl https://api.sonia.integratel.com/api/v1/dashboard/metrics`
- [ ] Estado de agentes verificado: `curl https://api.sonia.integratel.com/api/v1/dashboard/agentes/estado`
- [ ] Conexión a Groq verificada
- [ ] Conexión a Gemini verificada
- [ ] Conexión a Pinecone verificada
- [ ] WebSockets funcionando
- [ ] Backups ejecutándose correctamente
- [ ] Logs apareciendo en sistema de monitoreo
- [ ] Alertas configuradas y probadas
- [ ] Equipo notificado del despliegue exitoso

### Monitoreo Continuo

- [ ] Dashboard de Grafana configurado con:
  - Latencia de API (p50, p95, p99)
  - Tasa de error por endpoint
  - Uso de CPU/RAM por servicio
  - Conexiones activas a BD
  - Tasa de requests a APIs externas
  - Estado de agentes IA
  - Facturas procesadas por hora
- [ ] Alertas configuradas para:
  - Tasa de error > 1%
  - Latencia p95 > 2s
  - Disco > 80%
  - API externa no disponible
  - Agente IA con estado "error"

---

**Documentación actualizada: Noviembre 2024**
```

---

✅ **deployment.md completado.** Este archivo contiene:

1. Requisitos de hardware y software para cada entorno
2. APIs externas necesarias con límites
3. Configuración de variables de entorno con generación de secretos
4. Docker Compose completo para desarrollo
5. Comandos de operación diaria
6. Arquitectura de producción con diagrama
7. Configuración de Nginx como reverse proxy
8. Dockerfile optimizado para producción
9. Docker Compose para producción
10. Configuraciones para AWS y GCP con estimación de costos
11. CI/CD con GitHub Actions (test + build + deploy)
12. Monitoreo con Prometheus + Grafana + Sentry
13. Backup automático con script y cron
14. Procedimiento de recuperación
15. Plan de contingencia con fases y rollback
16. Checklist de producción (pre y post despliegue)

¿Continuo con el último archivo `contribution-guide.md`?