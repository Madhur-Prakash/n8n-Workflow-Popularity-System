<div align="center">

# 🚀 Deployment Guide

<p align="center">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="Kubernetes">
  <img src="https://img.shields.io/badge/AWS-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white" alt="AWS">
  <img src="https://img.shields.io/badge/Production-Ready-green?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Production Ready">
</p>

<p align="center">
  <strong>Complete deployment guide for production environments</strong>
</p>

</div>

---

## 🎯 **Deployment Options**

<div align="center">

<table>
<tr>
<td align="center" width="25%">
<img src="https://img.shields.io/badge/🐳-Docker-blue?style=for-the-badge" alt="Docker">
<br><br>
<strong>Container Deployment</strong><br>
Single machine<br>
Docker Compose<br>
Quick setup
</td>
<td align="center" width="25%">
<img src="https://img.shields.io/badge/☁️-Cloud-green?style=for-the-badge" alt="Cloud">
<br><br>
<strong>Cloud Platforms</strong><br>
AWS, GCP, Azure<br>
Managed services<br>
Auto-scaling
</td>
<td align="center" width="25%">
<img src="https://img.shields.io/badge/🔄-Kubernetes-purple?style=for-the-badge" alt="Kubernetes">
<br><br>
<strong>Container Orchestration</strong><br>
High availability<br>
Load balancing<br>
Enterprise scale
</td>
<td align="center" width="25%">
<img src="https://img.shields.io/badge/🖥️-Bare%20Metal-orange?style=for-the-badge" alt="Bare Metal">
<br><br>
<strong>Traditional Servers</strong><br>
Full control<br>
Custom setup<br>
On-premises
</td>
</tr>
</table>

</div>

---

## 🐳 **Docker Deployment**

### **Quick Production Deploy**

<details>
<summary><b>⚡ One-Command Deployment</b></summary>

```bash
# 1️⃣ Set environment variables
export YOUTUBE_API_KEY=your_youtube_api_key
export POSTGRES_PASSWORD=secure_random_password

# 2️⃣ Deploy everything
docker-compose up -d

# 3️⃣ Initialize database
docker-compose exec api uv run alembic upgrade head
docker-compose exec api uv run python scripts/load_seed_data.py

# ✅ Ready! API available at http://localhost:8000
```

</details>

### **Production Docker Compose**

<details>
<summary><b>🔧 Production Configuration</b></summary>

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: n8n_workflows
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    networks:
      - app-network
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  api:
    build: .
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@postgres:5432/n8n_workflows
      YOUTUBE_API_KEY: ${YOUTUBE_API_KEY}
      LOG_LEVEL: INFO
      REDIS_URL: redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped
    networks:
      - app-network
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - app-network

  scheduler:
    build: .
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@postgres:5432/n8n_workflows
      YOUTUBE_API_KEY: ${YOUTUBE_API_KEY}
      LOG_LEVEL: INFO
    depends_on:
      postgres:
        condition: service_healthy
    command: uv run python scripts/scheduler.py
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

</details>

---

## ☁️ **Cloud Deployment**

### **AWS Deployment**

<details>
<summary><b>🚀 AWS ECS Deployment</b></summary>

#### **1. Create ECR Repository**
```bash
# Create repository
aws ecr create-repository --repository-name n8n-workflow-system

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Build and push image
docker build -t n8n-workflow-system .
docker tag n8n-workflow-system:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/n8n-workflow-system:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/n8n-workflow-system:latest
```

#### **2. ECS Task Definition**
```json
{
  "family": "n8n-workflow-system",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/n8n-workflow-system:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql+asyncpg://user:pass@rds-endpoint:5432/n8n_workflows"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "secrets": [
        {
          "name": "YOUTUBE_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:youtube-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/n8n-workflow-system",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### **3. Application Load Balancer**
```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name n8n-workflow-alb \
  --subnets subnet-12345 subnet-67890 \
  --security-groups sg-12345

# Create target group
aws elbv2 create-target-group \
  --name n8n-workflow-targets \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-12345 \
  --target-type ip \
  --health-check-path /health
```

</details>

### **Google Cloud Run**

<details>
<summary><b>🌐 GCP Cloud Run Deployment</b></summary>

```bash
# 1️⃣ Build and submit to Cloud Build
gcloud builds submit --tag gcr.io/PROJECT_ID/n8n-workflow-system

# 2️⃣ Deploy to Cloud Run
gcloud run deploy n8n-workflow-system \
  --image gcr.io/PROJECT_ID/n8n-workflow-system \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --concurrency 100 \
  --max-instances 10 \
  --set-env-vars DATABASE_URL=postgresql+asyncpg://... \
  --set-secrets YOUTUBE_API_KEY=youtube-api-key:latest

# 3️⃣ Set up Cloud SQL
gcloud sql instances create n8n-postgres \
  --database-version POSTGRES_15 \
  --tier db-f1-micro \
  --region us-central1

# 4️⃣ Create database
gcloud sql databases create n8n_workflows --instance n8n-postgres
```

</details>

---

## 🔄 **Kubernetes Deployment**

### **Kubernetes Manifests**

<details>
<summary><b>⚙️ Complete K8s Configuration</b></summary>

#### **Namespace & ConfigMap**
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: n8n-workflow-system

---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: n8n-workflow-system
data:
  LOG_LEVEL: "INFO"
  DATABASE_URL: "postgresql+asyncpg://postgres:password@postgres:5432/n8n_workflows"
```

#### **Secrets**
```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: n8n-workflow-system
type: Opaque
data:
  YOUTUBE_API_KEY: <base64-encoded-api-key>
  POSTGRES_PASSWORD: <base64-encoded-password>
```

#### **PostgreSQL Deployment**
```yaml
# postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: n8n-workflow-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: n8n_workflows
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: POSTGRES_PASSWORD
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: n8n-workflow-system
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

#### **API Deployment**
```yaml
# api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: n8n-workflow-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: your-registry/n8n-workflow-system:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: n8n-workflow-system
spec:
  selector:
    app: api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

#### **Ingress**
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  namespace: n8n-workflow-system
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: api-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 80
```

</details>

---

## 🔒 **Security Configuration**

### **SSL/TLS Setup**

<details>
<summary><b>🛡️ HTTPS Configuration</b></summary>

#### **Nginx SSL Configuration**
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header Strict-Transport-Security "max-age=63072000" always;
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;

        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### **Let's Encrypt with Certbot**
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

</details>

### **Environment Security**

<details>
<summary><b>🔐 Secrets Management</b></summary>

#### **Docker Secrets**
```bash
# Create secrets
echo "your_youtube_api_key" | docker secret create youtube_api_key -
echo "secure_db_password" | docker secret create postgres_password -

# Use in compose
services:
  api:
    secrets:
      - youtube_api_key
      - postgres_password
    environment:
      YOUTUBE_API_KEY_FILE: /run/secrets/youtube_api_key
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password

secrets:
  youtube_api_key:
    external: true
  postgres_password:
    external: true
```

#### **AWS Secrets Manager**
```python
# Load secrets from AWS
import boto3
import json

def get_secret(secret_name, region_name="us-east-1"):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except Exception as e:
        raise e

# Usage
secrets = get_secret("n8n-workflow-secrets")
YOUTUBE_API_KEY = secrets["youtube_api_key"]
```

</details>

---

## 📊 **Monitoring & Observability**

### **Health Checks & Monitoring**

<details>
<summary><b>🏥 Health Monitoring Setup</b></summary>

#### **Prometheus Configuration**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'n8n-workflow-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
```

#### **Grafana Dashboard**
```json
{
  "dashboard": {
    "title": "n8n Workflow System",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "singlestat",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends{datname=\"n8n_workflows\"}"
          }
        ]
      }
    ]
  }
}
```

</details>

### **Logging Configuration**

<details>
<summary><b>📝 Centralized Logging</b></summary>

#### **ELK Stack Setup**
```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200

volumes:
  elasticsearch_data:
```

#### **Structured Logging**
```python
# Add to main.py
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage in endpoints
@app.get("/workflows")
async def get_workflows():
    logger.info("workflows_requested", 
                user_agent=request.headers.get("user-agent"),
                filters={"platform": platform, "country": country})
```

</details>

---

## 🔄 **Backup & Recovery**

### **Database Backup Strategy**

<details>
<summary><b>💾 Automated Backups</b></summary>

#### **PostgreSQL Backup Script**
```bash
#!/bin/bash
# backup.sh

# Configuration
DB_NAME="n8n_workflows"
DB_USER="postgres"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/n8n_workflows_${DATE}.sql.gz"

# Create backup
pg_dump -h postgres -U $DB_USER -d $DB_NAME | gzip > $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "n8n_workflows_*.sql.gz" -mtime +7 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_FILE s3://your-backup-bucket/database/

echo "Backup completed: $BACKUP_FILE"
```

#### **Backup Cron Job**
```bash
# Add to crontab
0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
```

#### **Recovery Process**
```bash
# Restore from backup
gunzip -c /backups/n8n_workflows_20240101_020000.sql.gz | \
  psql -h postgres -U postgres -d n8n_workflows

# Restore from S3
aws s3 cp s3://your-backup-bucket/database/n8n_workflows_20240101_020000.sql.gz - | \
  gunzip | psql -h postgres -U postgres -d n8n_workflows
```

</details>

---

## ✅ **Production Checklist**

<div align="center">

### **Pre-Deployment Checklist**

| Category | Item | Status |
|----------|------|--------|
| **🔐 Security** | Strong database passwords | ⬜ |
| **🔐 Security** | SSL/TLS certificates configured | ⬜ |
| **🔐 Security** | API keys in secrets management | ⬜ |
| **🔐 Security** | Firewall rules configured | ⬜ |
| **📊 Monitoring** | Health checks enabled | ⬜ |
| **📊 Monitoring** | Logging configured | ⬜ |
| **📊 Monitoring** | Metrics collection setup | ⬜ |
| **💾 Backup** | Database backup strategy | ⬜ |
| **💾 Backup** | Backup restoration tested | ⬜ |
| **🚀 Performance** | Load testing completed | ⬜ |
| **🚀 Performance** | Resource limits set | ⬜ |
| **🔄 Scaling** | Auto-scaling configured | ⬜ |

</div>

---

<div align="center">

## 🎯 **Deployment Success**

<table>
<tr>
<td align="center" width="25%">
<strong>🚀 Fast Deploy</strong><br>
One-command setup<br>
Docker Compose<br>
Production ready
</td>
<td align="center" width="25%">
<strong>☁️ Cloud Native</strong><br>
AWS, GCP, Azure<br>
Managed services<br>
Auto-scaling
</td>
<td align="center" width="25%">
<strong>🔒 Secure</strong><br>
SSL/TLS encryption<br>
Secrets management<br>
Security headers
</td>
<td align="center" width="25%">
<strong>📊 Observable</strong><br>
Health monitoring<br>
Centralized logging<br>
Performance metrics
</td>
</tr>
</table>

---

## 🚀 **Ready to Deploy?**

<p>
<a href="../README.md#-quick-start-options"><img src="https://img.shields.io/badge/🐳-Docker%20Deploy-blue?style=for-the-badge&logo=docker" alt="Docker Deploy"></a>
<a href="ARCHITECTURE.md"><img src="https://img.shields.io/badge/🏗️-Architecture%20Guide-green?style=for-the-badge&logo=kubernetes" alt="Architecture"></a>
<a href="API.md"><img src="https://img.shields.io/badge/🔌-API%20Reference-orange?style=for-the-badge&logo=fastapi" alt="API"></a>
</p>

---

*Production-ready deployment for any environment*

</div>