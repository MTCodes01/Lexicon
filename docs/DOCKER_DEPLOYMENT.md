# Lexicon Docker Deployment Guide

## Prerequisites

- Docker Desktop for Windows installed and running
- At least 4GB RAM available for Docker
- Ports 5432, 6379, 8000, 9000, 9001 available

## Quick Start

### 1. Stop Current Development Servers

First, stop your current running servers:

```powershell
# Stop the frontend (Ctrl+C in the terminal running npm run dev)
# Stop the backend (Ctrl+C in the terminal running uvicorn)
```

### 2. Update Environment Configuration

The `.env` file is already configured for Docker. Verify it has PostgreSQL settings:

```bash
DATABASE_URL=postgresql://lexicon:lexicon@postgres:5432/lexicon_db
```

**Note:** When running with Docker, use `postgres` as the hostname (service name in docker-compose).

### 3. Start All Services

```powershell
# From the Lexicon root directory
cd d:\Github\Lexicon

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

This will start:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **MinIO** on ports 9000 (API) and 9001 (Console)
- **Lexicon API** on port 8000

### 4. Verify Services

```powershell
# Check all services are running
docker-compose ps

# Check API health
curl http://localhost:8000/health

# Check API docs
# Open: http://localhost:8000/docs
```

### 5. Access the Application

- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **MinIO Console:** http://localhost:9001 (minioadmin/minioadmin)

### 6. Frontend (Still Running Locally)

The frontend will continue to run locally with `npm run dev`:

```powershell
cd web
npm run dev
```

Then access: http://localhost:3000

---

## Docker Commands Reference

### Start Services
```powershell
docker-compose up -d              # Start in background
docker-compose up                 # Start with logs
```

### Stop Services
```powershell
docker-compose down               # Stop and remove containers
docker-compose down -v            # Stop and remove volumes (deletes data!)
```

### View Logs
```powershell
docker-compose logs               # All services
docker-compose logs api           # Just API
docker-compose logs -f api        # Follow API logs
docker-compose logs --tail=100 api # Last 100 lines
```

### Restart Services
```powershell
docker-compose restart            # Restart all
docker-compose restart api        # Restart just API
```

### Rebuild After Code Changes
```powershell
docker-compose up -d --build      # Rebuild and restart
docker-compose build api          # Just rebuild API
```

### Execute Commands in Containers
```powershell
# Access PostgreSQL
docker-compose exec postgres psql -U lexicon -d lexicon_db

# Access API container shell
docker-compose exec api /bin/bash

# Run Python commands in API container
docker-compose exec api python -c "from api.database import Base; print('OK')"
```

---

## Database Management

### Access PostgreSQL

```powershell
# Via Docker
docker-compose exec postgres psql -U lexicon -d lexicon_db

# Via local psql (if installed)
psql -h localhost -U lexicon -d lexicon_db
# Password: lexicon
```

### Common PostgreSQL Commands

```sql
-- List all tables
\dt

-- Describe a table
\d users

-- Count users
SELECT COUNT(*) FROM users;

-- List all roles
SELECT * FROM roles;

-- Exit
\q
```

### Backup Database

```powershell
# Create backup
docker-compose exec postgres pg_dump -U lexicon lexicon_db > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U lexicon -d lexicon_db < backup.sql
```

### Reset Database

```powershell
# Stop services
docker-compose down

# Remove volumes (THIS DELETES ALL DATA!)
docker-compose down -v

# Start fresh
docker-compose up -d
```

---

## Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```powershell
# Check what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Stop the process or change ports in docker-compose.yml
```

### API Won't Start

```powershell
# Check logs
docker-compose logs api

# Common issues:
# 1. Database not ready - wait a few seconds and check again
# 2. Port conflict - change port in docker-compose.yml
# 3. Code errors - check the logs for Python errors
```

### Database Connection Failed

```powershell
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Verify connection from API container
docker-compose exec api python -c "from api.database import engine; print(engine.url)"
```

### Clean Start

If things are really broken:

```powershell
# Nuclear option - removes everything
docker-compose down -v
docker system prune -a
docker volume prune

# Then start fresh
docker-compose up -d --build
```

---

## Development Workflow

### Option 1: Full Docker (Recommended for Production-like Testing)

```powershell
# Start everything in Docker
docker-compose up -d

# Frontend runs locally
cd web && npm run dev

# Make code changes - API auto-reloads
# View logs: docker-compose logs -f api
```

### Option 2: Hybrid (Current Setup)

```powershell
# Just run PostgreSQL and Redis in Docker
docker-compose up -d postgres redis minio

# Run API locally
cd api
.venv\Scripts\activate
uvicorn api.main:app --reload

# Run frontend locally
cd web
npm run dev
```

### Option 3: Local Development (SQLite)

```powershell
# Stop Docker services
docker-compose down

# Update .env to use SQLite
DATABASE_URL=sqlite:///./lexicon.db

# Run API locally
uvicorn api.main:app --reload

# Run frontend locally
npm run dev
```

---

## Environment Variables

### For Docker Deployment

Create/update `.env` in the root directory:

```bash
# Database (use service name 'postgres' for Docker)
DATABASE_URL=postgresql://lexicon:lexicon@postgres:5432/lexicon_db

# Redis (use service name 'redis' for Docker)
REDIS_URL=redis://redis:6379/0

# MinIO (use service name 'minio' for Docker)
MINIO_ENDPOINT=minio:9000

# Security
SECRET_KEY=your-production-secret-key-min-32-chars
DEBUG=false

# CORS (add your frontend URL)
CORS_ORIGINS=["http://localhost:3000"]
```

### For Local Development

```bash
# Database (use localhost for local)
DATABASE_URL=postgresql://lexicon:lexicon@localhost:5432/lexicon_db
# or SQLite
DATABASE_URL=sqlite:///./lexicon.db

# Redis
REDIS_URL=redis://localhost:6379/0

# MinIO
MINIO_ENDPOINT=localhost:9000
```

---

## Production Deployment

For production deployment, update:

1. **Change default passwords** in docker-compose.yml
2. **Set strong SECRET_KEY** in .env
3. **Set DEBUG=false**
4. **Use environment-specific .env files**
5. **Enable HTTPS** with reverse proxy (nginx/traefik)
6. **Set up backups** for PostgreSQL
7. **Configure monitoring** and logging
8. **Use Docker secrets** for sensitive data

---

## Next Steps

1. ✅ Start Docker services: `docker-compose up -d`
2. ✅ Verify API: http://localhost:8000/docs
3. ✅ Start frontend: `cd web && npm run dev`
4. ✅ Access app: http://localhost:3000
5. ✅ Register a new user
6. ✅ Test the full stack!

---

## Monitoring

### View Resource Usage

```powershell
# Container stats
docker stats

# Disk usage
docker system df

# Specific service stats
docker stats lexicon-api lexicon-postgres
```

### Health Checks

All services have health checks configured. Check status:

```powershell
docker-compose ps
```

Healthy services show "healthy" in the status column.

---

## Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify all services are healthy: `docker-compose ps`
3. Check the documentation: `docs/GETTING_STARTED.md`
4. Try a clean restart: `docker-compose down && docker-compose up -d`
