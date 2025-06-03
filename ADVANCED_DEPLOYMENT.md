# Advanced Deployment Guide

This guide covers advanced deployment scenarios for workflow-use, including Docker containerization, production deployment, monitoring, and scaling strategies.

## 🚀 Quick Start - Advanced Deployment

### Prerequisites
- **Python 3.11+** with uv package manager
- **Docker & Docker Compose** (for containerized deployment)
- **Node.js 18+** (for UI development)
- **Git** (for repository management)

### Advanced Deployment Script

```batch
# Windows - Advanced deployment with multiple options
deploy-advanced.bat

# Options available:
# 1. Quick Setup (Backend + Web-UI)
# 2. Development Suite (All components)
# 3. Backend Only (API server)
# 4. Web-UI Only (Browser automation)
# 5. Docker Deployment (Containerized)
# 6. Custom Configuration
# 7. Health Check (Check running services)
# 8. Clean Installation (Remove and reinstall)
```

## 🐳 Docker Deployment

### Basic Docker Deployment

```bash
# Start all services with Docker Compose
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Production Docker Deployment

```bash
# Start with production profile (includes nginx reverse proxy)
docker compose --profile production up -d

# Start with database support
docker compose --profile database up -d

# Start with caching layer
docker compose --profile cache up -d

# Full production stack
docker compose --profile production --profile database --profile cache up -d
```

### Docker Services Overview

| Service | Port | Description | Health Check |
|---------|------|-------------|--------------|
| **workflow-backend** | 8000 | FastAPI backend | `/health` endpoint |
| **browser-use-webui** | 7788 | Gradio web interface | HTTP response check |
| **workflow-ui** | 5173 | React frontend | HTTP response check |
| **nginx** | 80/443 | Reverse proxy | Built-in health endpoint |
| **postgres** | 5432 | Database (optional) | PostgreSQL ready check |
| **redis** | 6379 | Cache (optional) | Redis ping |

## 🏗️ Architecture Overview

### Development Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Workflow UI   │    │   Browser-Use   │    │   Workflow      │
│   (React)       │◄──►│   Web-UI        │◄──►│   Backend       │
│   Port: 5173    │    │   (Gradio)      │    │   (FastAPI)     │
└─────────────────┘    │   Port: 7788    │    │   Port: 8000    │
                       └─────────────────┘    └─────────────────┘
```

### Production Architecture
```
┌─────────────────┐
│   Nginx Proxy   │
│   Port: 80/443  │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
┌───▼───┐   ┌───▼───┐   ┌─────────┐
│ UI    │   │WebUI  │   │Backend  │
│:5173  │   │:7788  │   │:8000    │
└───────┘   └───────┘   └─────────┘
                            │
                    ┌───────┴───────┐
                    │               │
                ┌───▼───┐       ┌───▼───┐
                │ DB    │       │Cache  │
                │:5432  │       │:6379  │
                └───────┘       └───────┘
```

## ⚙️ Configuration Management

### Environment Variables

**Backend Configuration** (`workflows/.env`):
```env
# Core settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
HOST=0.0.0.0
PORT=8000

# LLM Provider API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Database (optional)
DATABASE_URL=postgresql://user:pass@postgres:5432/workflow_use

# Redis (optional)
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Browser automation
BROWSER_HEADLESS=true
BROWSER_DISABLE_SECURITY=true
BROWSER_TIMEOUT=30000
```

**Web-UI Configuration** (`browser-use-web-ui/.env`):
```env
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Browser settings
BROWSER_HEADLESS=true
BROWSER_DISABLE_SECURITY=true
BROWSER_PATH=/usr/bin/chromium-browser

# Gradio settings
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7788
GRADIO_SHARE=false
```

**UI Configuration** (`ui/.env`):
```env
VITE_API_URL=http://localhost:8000
VITE_WEBUI_URL=http://localhost:7788
VITE_ENVIRONMENT=production
```

### Docker Environment Variables

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  workflow-backend:
    environment:
      - DEBUG=true
      - LOG_LEVEL=debug
      - CORS_ORIGINS=http://localhost:3000,http://localhost:5173
  
  browser-use-webui:
    environment:
      - BROWSER_HEADLESS=false  # For development
      - GRADIO_SHARE=true       # For external access
```

## 📊 Monitoring and Observability

### Health Checks

**Manual Health Checks:**
```bash
# Check backend health
curl http://localhost:8000/health

# Check web-ui availability
curl http://localhost:7788

# Check UI availability
curl http://localhost:5173

# Docker health status
docker compose ps
```

**Automated Health Monitoring:**
```bash
# Create health check script
cat > health-check.sh << 'EOF'
#!/bin/bash
services=("8000" "7788" "5173")
for port in "${services[@]}"; do
    if curl -f -s "http://localhost:$port" > /dev/null; then
        echo "✅ Service on port $port is healthy"
    else
        echo "❌ Service on port $port is down"
    fi
done
EOF

chmod +x health-check.sh
./health-check.sh
```

### Logging

**Centralized Logging with Docker:**
```yaml
# Add to docker-compose.yml
services:
  workflow-backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Log Aggregation:**
```bash
# View all service logs
docker compose logs -f

# View specific service logs
docker compose logs -f workflow-backend

# Follow logs with timestamps
docker compose logs -f -t
```

### Performance Monitoring

**Resource Usage:**
```bash
# Monitor Docker container resources
docker stats

# Monitor system resources
htop

# Monitor disk usage
df -h
```

**Application Metrics:**
- Backend API response times via `/docs` interface
- Browser automation performance metrics
- Memory and CPU usage per service
- Request rate and error rate monitoring

## 🔒 Security Considerations

### Production Security Checklist

- [ ] **Environment Variables**: Store sensitive data in environment variables
- [ ] **HTTPS**: Enable SSL/TLS certificates for production
- [ ] **Firewall**: Configure firewall rules for required ports only
- [ ] **Authentication**: Implement proper authentication for API endpoints
- [ ] **CORS**: Configure CORS policies appropriately
- [ ] **Rate Limiting**: Implement rate limiting for API endpoints
- [ ] **Input Validation**: Validate all user inputs
- [ ] **Security Headers**: Add security headers via nginx
- [ ] **Regular Updates**: Keep dependencies updated
- [ ] **Secrets Management**: Use proper secrets management tools

### SSL/TLS Configuration

**Generate Self-Signed Certificates (Development):**
```bash
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem -out ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

**Production Certificates:**
```bash
# Using Let's Encrypt with Certbot
certbot certonly --standalone -d your-domain.com
```

### Network Security

**Firewall Configuration:**
```bash
# Allow only necessary ports
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

**Docker Network Isolation:**
```yaml
# Isolate services in custom networks
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
```

## 📈 Scaling and Performance

### Horizontal Scaling

**Load Balancer Configuration:**
```yaml
# docker-compose.scale.yml
services:
  workflow-backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

**Database Scaling:**
```yaml
# Add read replicas
services:
  postgres-primary:
    image: postgres:15-alpine
    environment:
      - POSTGRES_REPLICATION_MODE=master
  
  postgres-replica:
    image: postgres:15-alpine
    environment:
      - POSTGRES_REPLICATION_MODE=slave
      - POSTGRES_MASTER_SERVICE=postgres-primary
```

### Performance Optimization

**Backend Optimization:**
```python
# Add to backend configuration
WORKERS = 4  # Number of Uvicorn workers
WORKER_CLASS = "uvicorn.workers.UvicornWorker"
MAX_REQUESTS = 1000
MAX_REQUESTS_JITTER = 100
```

**Caching Strategy:**
```yaml
# Redis caching configuration
services:
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

**Database Optimization:**
```sql
-- Add database indexes
CREATE INDEX idx_workflows_created_at ON workflows(created_at);
CREATE INDEX idx_workflows_status ON workflows(status);
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy Workflow-Use Suite

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install uv
        run: pip install uv
      - name: Install dependencies
        run: uv sync
      - name: Run tests
        run: uv run pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: docker compose build
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker compose push

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          ssh ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }} '
            cd /opt/workflow-use &&
            git pull origin main &&
            docker compose pull &&
            docker compose up -d
          '
```

### Deployment Automation

**Automated Deployment Script:**
```bash
#!/bin/bash
# deploy.sh - Production deployment script

set -e

echo "🚀 Starting deployment..."

# Pull latest changes
git pull origin main

# Build and deploy with zero downtime
docker compose pull
docker compose up -d --remove-orphans

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Run health checks
./health-check.sh

# Clean up old images
docker image prune -f

echo "✅ Deployment completed successfully!"
```

## 🛠️ Troubleshooting

### Common Issues

**1. Port Conflicts**
```bash
# Find process using port
netstat -tulpn | grep :8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

**2. Docker Issues**
```bash
# Clean Docker system
docker system prune -a

# Rebuild containers
docker compose down
docker compose build --no-cache
docker compose up -d
```

**3. Permission Issues**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x deploy-advanced.bat
```

**4. Memory Issues**
```bash
# Increase Docker memory limit
# Docker Desktop -> Settings -> Resources -> Memory

# Monitor memory usage
docker stats --no-stream
```

### Debug Mode

**Enable Debug Logging:**
```bash
# Set environment variables
export DEBUG=true
export LOG_LEVEL=debug

# Run with verbose output
uv run python main.py suite --verbose
```

**Docker Debug:**
```bash
# Run container interactively
docker run -it workflow-use-suite /bin/bash

# Check container logs
docker logs -f container_name
```

## 📚 Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **Nginx Configuration**: https://nginx.org/en/docs/
- **PostgreSQL Tuning**: https://pgtune.leopard.in.ua/
- **Redis Configuration**: https://redis.io/docs/manual/config/
- **Security Best Practices**: https://owasp.org/www-project-top-ten/

This advanced deployment guide provides comprehensive coverage for production-ready workflow-use deployments with scalability, security, and monitoring considerations.

