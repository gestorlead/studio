# GestorLead Studio - Especificações Técnicas Complementares
*Documento complementar ao PRD - Foco em tecnologias Open Source*

## 1. Arquitetura de Infraestrutura

### 1.1 Stack de Deploy (Open Source)
```yaml
# docker-compose.yml
services:
  # API Backend
  api:
    image: gestorLead/api:latest
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/gestorLead
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  # Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: gestorLead
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  # Cache & Message Broker
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Task Queue Worker
  celery-worker:
    image: gestorLead/api:latest
    command: celery -A app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/gestorLead
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  # Task Scheduler
  celery-beat:
    image: gestorLead/api:latest
    command: celery -A app.celery beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/gestorLead
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  # Object Storage (MinIO)
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin123
    volumes:
      - minio_data:/data

  # Frontend
  frontend:
    image: gestorLead/frontend:latest
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - api

  # Monitoring Stack
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/:/etc/grafana/provisioning/

volumes:
  postgres_data:
  redis_data:
  minio_data:
  prometheus_data:
  grafana_data:
```

### 1.2 CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/deploy.yml
name: Deploy GestorLead Studio

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_gestorLead
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install -r backend/requirements-dev.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest tests/ -v --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Production
      run: |
        # Deploy script usando Docker Compose
        docker-compose -f docker-compose.prod.yml up -d
```

## 2. Backend - Especificações Detalhadas

### 2.1 Estrutura do Projeto Backend
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configurações
│   ├── celery_app.py        # Celery setup
│   ├── database.py          # Database connection
│   ├── dependencies.py      # FastAPI dependencies
│   │
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── content.py
│   │   └── social_profile.py
│   │
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   └── content.py
│   │
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── tasks.py
│   │   │   ├── content.py
│   │   │   └── agents.py
│   │
│   ├── core/                # Core business logic
│   │   ├── __init__.py
│   │   ├── security.py      # Auth & encryption
│   │   ├── config.py        # Settings
│   │   └── exceptions.py    # Custom exceptions
│   │
│   ├── services/            # Business services
│   │   ├── __init__.py
│   │   ├── ai_gateway.py    # AI provider abstraction
│   │   ├── auth_service.py
│   │   ├── credit_service.py
│   │   ├── task_service.py
│   │   └── social_service.py
│   │
│   ├── workers/             # Celery workers
│   │   ├── __init__.py
│   │   ├── ai_tasks.py      # AI generation tasks
│   │   ├── social_tasks.py  # Social media tasks
│   │   └── agent_tasks.py   # Agent execution tasks
│   │
│   ├── integrations/        # External APIs
│   │   ├── __init__.py
│   │   ├── openai_adapter.py
│   │   ├── google_adapter.py
│   │   ├── piapi_adapter.py
│   │   ├── elevenlabs_adapter.py
│   │   └── asaas_adapter.py
│   │
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── logger.py
│       ├── validators.py
│       └── helpers.py
│
├── alembic/                 # Database migrations
├── tests/                   # Tests
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
└── docker-compose.yml
```

### 2.2 Configuração de Dependências (requirements.txt)
```txt
# Framework core
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9

# Task Queue
celery==5.3.4
redis==5.0.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# HTTP Client
httpx==0.25.2
aiohttp==3.9.1

# AI/ML Libraries
langchain==0.1.0
langchain-openai==0.0.2
langchain-google-genai==0.0.6
langsmith==0.0.70

# File handling
python-magic==0.4.27
pillow==10.1.0

# Monitoring
prometheus-client==0.19.0
sentry-sdk[fastapi]==1.38.0

# Testing (requirements-dev.txt)
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
factory-boy==3.3.0
```

### 2.3 Modelo de Dados Detalhado (SQLAlchemy)
```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    google_id = Column(String(255), unique=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    credit_balance = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    tasks = relationship("Task", back_populates="user")
    api_keys = relationship("ApiKey", back_populates="user")
    social_profiles = relationship("SocialProfile", back_populates="user")
    agents = relationship("Agent", back_populates="user")

# app/models/task.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_type = Column(String(50), nullable=False)  # 'text_to_image', 'chat_completion', etc.
    provider = Column(String(50), nullable=False)   # 'openai', 'google', 'piapi'
    model = Column(String(100), nullable=True)      # 'gpt-4', 'dall-e-3', etc.
    status = Column(String(20), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    credit_cost = Column(Integer, nullable=False)
    request_payload = Column(JSON, nullable=False)
    result_payload = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    content = relationship("GeneratedContent", back_populates="task")
```

### 2.4 Configuração de Segurança (Open Source)
```python
# app/core/security.py
from cryptography.fernet import Fernet
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Encryption for sensitive data (OAuth tokens)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def encrypt_token(token: str) -> bytes:
    """Encrypt OAuth tokens before storing in database"""
    return cipher_suite.encrypt(token.encode())

def decrypt_token(encrypted_token: bytes) -> str:
    """Decrypt OAuth tokens from database"""
    return cipher_suite.decrypt(encrypted_token).decode()
```

## 3. Frontend - Especificações Open Source

### 3.1 Package.json (Next.js + Open Source)
```json
{
  "name": "gestorLead-studio-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "dependencies": {
    "next": "14.0.3",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "typescript": "5.3.2",
    
    "tailwindcss": "3.3.6",
    "autoprefixer": "10.4.16",
    "postcss": "8.4.32",
    
    "@radix-ui/react-accordion": "^1.1.2",
    "@radix-ui/react-alert-dialog": "^1.0.5",
    "@radix-ui/react-button": "^1.0.3",
    "@radix-ui/react-card": "^1.0.4",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-form": "^0.0.3",
    "@radix-ui/react-input": "^1.0.4",
    "@radix-ui/react-label": "^2.0.2",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    
    "next-auth": "^4.24.5",
    "react-hook-form": "^7.48.2",
    "@hookform/resolvers": "^3.3.2",
    "zod": "^3.22.4",
    
    "axios": "^1.6.2",
    "react-query": "^3.39.3",
    "zustand": "^4.4.7",
    
    "framer-motion": "^10.16.16",
    "lucide-react": "^0.294.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    
    "react-dropzone": "^14.2.3",
    "react-calendar": "^4.7.0",
    "recharts": "^2.8.0"
  },
  "devDependencies": {
    "@types/node": "20.10.0",
    "@types/react": "18.2.38",
    "@types/react-dom": "18.2.17",
    "eslint": "8.54.0",
    "eslint-config-next": "14.0.3",
    "jest": "^29.7.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^6.1.5",
    "prettier": "^3.1.0",
    "prettier-plugin-tailwindcss": "^0.5.7"
  }
}
```

### 3.2 Estrutura do Frontend
```
frontend/
├── public/
│   ├── favicon.ico
│   └── images/
├── src/
│   ├── app/                 # Next.js 14 app directory
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── loading.tsx
│   │   ├── error.tsx
│   │   │
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   └── register/
│   │   │
│   │   ├── dashboard/
│   │   │   ├── page.tsx
│   │   │   ├── playground/
│   │   │   ├── agents/
│   │   │   ├── billing/
│   │   │   └── settings/
│   │   │
│   │   └── api/             # API routes
│   │       ├── auth/
│   │       └── webhook/
│   │
│   ├── components/          # Reusable components
│   │   ├── ui/              # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   │
│   │   ├── playground/      # Playground specific
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── ImageGenerator.tsx
│   │   │   ├── VideoGenerator.tsx
│   │   │   └── AudioGenerator.tsx
│   │   │
│   │   ├── agents/          # Agent components
│   │   │   ├── AgentBuilder.tsx
│   │   │   ├── AgentRunner.tsx
│   │   │   └── AgentLibrary.tsx
│   │   │
│   │   └── common/          # Common components
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       ├── CreditDisplay.tsx
│   │       └── LoadingSpinner.tsx
│   │
│   ├── lib/                 # Utilities
│   │   ├── auth.ts          # NextAuth config
│   │   ├── api.ts           # API client
│   │   ├── utils.ts         # General utilities
│   │   └── validations.ts   # Zod schemas
│   │
│   ├── hooks/               # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useCredits.ts
│   │   ├── useTasks.ts
│   │   └── useAgents.ts
│   │
│   ├── store/               # State management
│   │   ├── authStore.ts     # Zustand store
│   │   ├── taskStore.ts
│   │   └── uiStore.ts
│   │
│   └── types/               # TypeScript types
│       ├── auth.ts
│       ├── task.ts
│       ├── agent.ts
│       └── api.ts
│
├── tailwind.config.js
├── next.config.js
├── tsconfig.json
├── jest.config.js
└── Dockerfile
```

## 4. Monitoring e Observabilidade (Open Source)

### 4.1 Configuração do Prometheus
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'gestorLead-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: /metrics
    
  - job_name: 'gestorLead-celery'
    static_configs:
      - targets: ['celery-worker:9540']
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:9187']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### 4.2 Dashboards Grafana (JSON)
```json
{
  "dashboard": {
    "title": "GestorLead Studio - API Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Task Queue Size",
        "type": "stat",
        "targets": [
          {
            "expr": "celery_queue_length",
            "legendFormat": "Queue: {{queue}}"
          }
        ]
      },
      {
        "title": "AI Provider Response Time",
        "type": "heatmap",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(ai_provider_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

### 4.3 Logging Estruturado
```python
# app/utils/logger.py
import logging
import json
from datetime import datetime
from typing import Any, Dict

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log(self, level: str, message: str, **kwargs):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "service": "gestorLead-api",
            **kwargs
        }
        
        if level == "ERROR":
            self.logger.error(json.dumps(log_data))
        elif level == "WARNING":
            self.logger.warning(json.dumps(log_data))
        else:
            self.logger.info(json.dumps(log_data))
    
    def info(self, message: str, **kwargs):
        self.log("INFO", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log("ERROR", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log("WARNING", message, **kwargs)

# Usage
logger = StructuredLogger(__name__)
logger.info("Task started", task_id="123", user_id=456, task_type="text_to_image")
```

## 5. Testes Automatizados (Open Source)

### 5.1 Configuração de Testes Backend
```python
# tests/conftest.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models.user import User

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db):
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        credit_balance=1000
    )
    db_session.add(user)
    db_session.commit()
    return user
```

### 5.2 Testes de API
```python
# tests/test_tasks.py
import pytest
from fastapi.testclient import TestClient

def test_create_task(client: TestClient, test_user):
    response = client.post(
        "/v1/tasks",
        json={
            "task_type": "text_to_image",
            "provider": "openai",
            "model": "dall-e-3",
            "input": {
                "prompt": "A beautiful sunset",
                "size": "1024x1024"
            }
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "PENDING"

def test_get_task_status(client: TestClient, test_user):
    # First create a task
    create_response = client.post("/v1/tasks", json={...})
    task_id = create_response.json()["task_id"]
    
    # Then check its status
    response = client.get(f"/v1/tasks/{task_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["task_id"] == task_id
    assert "status" in data
```

## 6. Performance e Escalabilidade

### 6.1 Configuration de Cache (Redis)
```python
# app/services/cache_service.py
import redis
import json
from typing import Any, Optional
import pickle

class CacheService:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
    
    async def get(self, key: str) -> Optional[Any]:
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
        except Exception:
            return None
        return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        try:
            serialized = pickle.dumps(value)
            self.redis_client.setex(key, expire, serialized)
        except Exception:
            pass
    
    async def delete(self, key: str):
        self.redis_client.delete(key)
    
    # Cache para resultados de AI providers
    async def cache_ai_result(self, provider: str, model: str, 
                            input_hash: str, result: dict, ttl: int = 86400):
        cache_key = f"ai_result:{provider}:{model}:{input_hash}"
        await self.set(cache_key, result, ttl)
    
    async def get_cached_ai_result(self, provider: str, model: str, input_hash: str):
        cache_key = f"ai_result:{provider}:{model}:{input_hash}"
        return await self.get(cache_key)
```

### 6.2 Rate Limiting
```python
# app/middleware/rate_limit.py
import time
from typing import Dict
from fastapi import HTTPException, Request
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.limits = {
            "anonymous": (100, 3600),  # 100 requests per hour
            "authenticated": (1000, 3600),  # 1000 requests per hour
            "premium": (5000, 3600)  # 5000 requests per hour
        }
    
    def is_allowed(self, client_id: str, user_tier: str = "anonymous") -> bool:
        now = time.time()
        limit, window = self.limits.get(user_tier, self.limits["anonymous"])
        
        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < window
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_id]) >= limit:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True

rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    user_tier = getattr(request.state, "user_tier", "anonymous")
    
    if not rate_limiter.is_allowed(client_ip, user_tier):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )
    
    response = await call_next(request)
    return response
```

## 7. Deploy e DevOps

### 7.1 Terraform para Infrastructure as Code
```hcl
# infrastructure/main.tf
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

# Network
resource "docker_network" "gestorLead_network" {
  name = "gestorLead_network"
}

# Volumes
resource "docker_volume" "postgres_data" {
  name = "gestorLead_postgres_data"
}

resource "docker_volume" "redis_data" {
  name = "gestorLead_redis_data"
}

resource "docker_volume" "minio_data" {
  name = "gestorLead_minio_data"
}

# Database
resource "docker_container" "postgres" {
  image = "postgres:15"
  name  = "gestorLead_postgres"
  
  env = [
    "POSTGRES_DB=gestorLead",
    "POSTGRES_USER=gestorLead_user",
    "POSTGRES_PASSWORD=secure_password"
  ]
  
  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }
  
  networks_advanced {
    name = docker_network.gestorLead_network.name
  }
  
  ports {
    internal = 5432
    external = 5432
  }
}

# Redis
resource "docker_container" "redis" {
  image = "redis:7-alpine"
  name  = "gestorLead_redis"
  
  volumes {
    volume_name    = docker_volume.redis_data.name
    container_path = "/data"
  }
  
  networks_advanced {
    name = docker_network.gestorLead_network.name
  }
  
  ports {
    internal = 6379
    external = 6379
  }
}

# MinIO
resource "docker_container" "minio" {
  image = "minio/minio:latest"
  name  = "gestorLead_minio"
  
  command = ["server", "/data", "--console-address", ":9001"]
  
  env = [
    "MINIO_ROOT_USER=minioadmin",
    "MINIO_ROOT_PASSWORD=minioadmin123"
  ]
  
  volumes {
    volume_name    = docker_volume.minio_data.name
    container_path = "/data"
  }
  
  networks_advanced {
    name = docker_network.gestorLead_network.name
  }
  
  ports {
    internal = 9000
    external = 9000
  }
  
  ports {
    internal = 9001
    external = 9001
  }
}
```

### 7.2 Makefile para automação
```makefile
# Makefile
.PHONY: help install dev test build deploy clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev: ## Start development environment
	docker-compose up --build

test: ## Run tests
	cd backend && pytest tests/ -v
	cd frontend && npm test

test-coverage: ## Run tests with coverage
	cd backend && pytest tests/ -v --cov=app --cov-report=html
	cd frontend && npm run test:coverage

build: ## Build production images
	docker-compose -f docker-compose.prod.yml build

deploy: ## Deploy to production
	docker-compose -f docker-compose.prod.yml up -d

clean: ## Clean up containers and volumes
	docker-compose down -v
	docker system prune -f

migrate: ## Run database migrations
	cd backend && alembic upgrade head

seed: ## Seed database with sample data
	cd backend && python scripts/seed_database.py

logs: ## Show logs
	docker-compose logs -f

backup: ## Backup database
	docker exec gestorLead_postgres pg_dump -U gestorLead_user gestorLead > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore: ## Restore database (usage: make restore BACKUP_FILE=backup.sql)
	docker exec -i gestorLead_postgres psql -U gestorLead_user gestorLead < $(BACKUP_FILE)
```

Este conjunto de especificações técnicas complementa o PRD original, preenchendo as lacunas identificadas com foco em tecnologias open-source e gratuitas, mantendo alta qualidade e escalabilidade. 