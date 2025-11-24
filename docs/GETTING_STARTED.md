# Lexicon - Getting Started Guide

## Prerequisites

- **Python 3.11+**
- **PostgreSQL 14+**
- **Redis 7+**
- **Docker & Docker Compose** (recommended for easy setup)

## Quick Start with Docker Compose

The easiest way to get started is using Docker Compose:

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/lexicon.git
cd lexicon
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and update the `SECRET_KEY`:

```bash
# Generate a secure secret key
openssl rand -hex 32
```

### 3. Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- MinIO (ports 9000, 9001)
- Lexicon API (port 8000)

### 4. Verify Installation

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development"
}
```

### 5. Access API Documentation

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 6. Create Your First User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePassword123!",
    "username": "admin",
    "full_name": "Admin User"
  }'
```

### 7. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePassword123!"
  }'
```

Save the `access_token` from the response.

---

## Manual Setup (Without Docker)

### 1. Install PostgreSQL and Redis

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql redis-server
```

**macOS:**
```bash
brew install postgresql@16 redis
brew services start postgresql@16
brew services start redis
```

### 2. Create Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE lexicon_db;
CREATE USER lexicon WITH PASSWORD 'lexicon';
GRANT ALL PRIVILEGES ON DATABASE lexicon_db TO lexicon;
\q
```

### 3. Install Python Dependencies

```bash
cd api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp ../.env.example ../.env
```

Edit `.env` with your database credentials.

### 5. Run the API

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Next Steps

1. **Enable MFA**: Set up two-factor authentication for your account
2. **Create API Keys**: Generate API keys for programmatic access
3. **Explore Modules**: Check out the Tasks module at `/tasks`
4. **Read the Docs**: See `docs/` for detailed documentation

---

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. Check PostgreSQL is running:
   ```bash
   docker-compose ps postgres
   ```

2. Verify credentials in `.env`

3. Check database logs:
   ```bash
   docker-compose logs postgres
   ```

### Port Conflicts

If ports are already in use, edit `docker-compose.yml` to use different ports:

```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Permission Errors

If you see permission errors, ensure the database user has proper permissions:

```sql
GRANT ALL PRIVILEGES ON DATABASE lexicon_db TO lexicon;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO lexicon;
```

---

## Development

### Running Tests

```bash
cd api
pytest
```

### Code Formatting

```bash
black api/
ruff check api/
```

### Database Migrations

```bash
# Create a migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

---

## Support

- **Documentation**: See `docs/` directory
- **Issues**: https://github.com/yourusername/lexicon/issues
- **Discussions**: https://github.com/yourusername/lexicon/discussions
