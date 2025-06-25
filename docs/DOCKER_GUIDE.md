# Docker部署指南

## 1. 开发环境
```dockerfile
# Dockerfile.dev
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["flask", "run", "--host=0.0.0.0"]
```

## 2. 生产环境
```dockerfile
# Dockerfile.prod
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV FLASK_ENV=production

CMD ["gunicorn", "-w 4", "-b :80", "app:create_app()"]
```

## 3. docker-compose配置
```yaml
version: '3.8'

services:
  web:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
    environment:
      - DATABASE_URL=postgresql://db:5432
    depends_on:
      - db

  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: example

volumes:
  postgres_data:
```

## 4. 健康检查
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost/health"]
  interval: 30s
  timeout: 10s
  retries: 3
