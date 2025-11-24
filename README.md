# Lexicon: Your Lifetime Personal Operating System

Lexicon is an open-source, self-hosted, modular, and extensible multi-user Personal Operating System designed to empower individuals and teams with ultimate control over their digital lives. It provides a robust platform for managing tasks, notes, calendar, finance, health, files, and more, all within a secure and privacy-focused environment.

## ✨ Features

- **🔐 Secure Authentication**: JWT tokens, MFA (TOTP), API keys, and OAuth support
- **👥 Multi-User**: Support for personal, family, and organizational accounts with role-based access control
- **🧩 Modular Architecture**: Plug-and-play modules that extend functionality without touching core code
- **🔒 Privacy-First**: Self-hosted, field-level encryption, and zero-knowledge vault option
- **📊 Comprehensive Modules**: Tasks, Notes, Calendar, Finance, Health, Files, and more
- **🚀 Modern Stack**: FastAPI, PostgreSQL, Redis, MinIO, Next.js
- **🐳 Easy Deployment**: Docker Compose for local setup, Kubernetes for production
- **📱 PWA Support**: Progressive Web App for mobile and offline access
- **🔍 Powerful Search**: Semantic search with vector database integration
- **🤖 AI-Powered**: Optional AI features for insights, summaries, and automation

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/lexicon.git
cd lexicon

# Create environment file
cp .env.example .env

# Generate a secure secret key
openssl rand -hex 32
# Add it to .env as SECRET_KEY

# Start all services
docker-compose up -d

# Verify installation
curl http://localhost:8000/health
```

**Access the API:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

### Manual Setup

See [Getting Started Guide](docs/GETTING_STARTED.md) for detailed instructions.

## 📚 Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** - Installation and setup
- **[Module Development](docs/MODULE_DEVELOPMENT.md)** - Create custom modules
- **[API Reference](http://localhost:8000/docs)** - Interactive API documentation
- **[Architecture](docs/ARCHITECTURE.md)** - System design and architecture (coming soon)

## 🏗️ Architecture

Lexicon is structured as a monorepo with clear separation of concerns:

```
/lexicon/
├── api/           # FastAPI backend (modular apps)
├── web/           # Next.js/React frontend
├── worker/        # Celery/RQ background workers
├── services/      # Microservices (search, AI, automation)
├── infra/         # Docker Compose + Kubernetes configs
├── docs/          # Documentation
└── shared/        # Shared schemas and utilities
```

### Core Technologies

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL 16+
- Redis 7+
- SQLAlchemy ORM
- Pydantic validation

**Frontend:**
- Next.js 14+
- React 18+
- Tailwind CSS
- TypeScript

**Storage:**
- PostgreSQL (structured data)
- Redis (caching, queues)
- MinIO (file storage)
- pgvector (semantic search)

## 🔐 Security

Lexicon takes security seriously:

- **Authentication**: JWT with refresh tokens, MFA (TOTP), OAuth
- **Authorization**: Role-based access control (RBAC) with fine-grained permissions
- **Encryption**: Field-level encryption for sensitive data, Argon2id password hashing
- **Audit Logging**: Comprehensive audit trail for all actions
- **API Security**: Rate limiting, CORS, API keys for services
- **Data Isolation**: Multi-tenant architecture with row-level security

## 🧩 Module System

Lexicon's modular architecture makes it easy to extend:

### Built-in Modules

- **Tasks**: Task management with priorities, due dates, and tags
- **Notes**: Rich text notes with organization and sharing (coming soon)
- **Calendar**: Events and scheduling (coming soon)
- **Finance**: Transaction tracking and budgeting (coming soon)
- **Health**: Health metrics and tracking (coming soon)
- **Files**: File management with versioning (coming soon)

### Creating Custom Modules

Creating a new module is simple:

```python
# api/modules/your_module/module_config.py
module_config = {
    "name": "YourModule",
    "slug": "your-module",
    "version": "1.0.0",
    "api_router": "routes.py",
    "permissions": [...],
}
```

See [Module Development Guide](docs/MODULE_DEVELOPMENT.md) for details.

## 🛠️ Development

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (recommended)

### Running Locally

```bash
# Backend
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload

# Frontend (coming soon)
cd web
npm install
npm run dev
```

### Running Tests

```bash
cd api
pytest
pytest --cov=api --cov-report=html
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- PostgreSQL for reliable data storage
- The open-source community for inspiration and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/lexicon/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/lexicon/discussions)
- **Documentation**: [docs/](docs/)

## 🗺️ Roadmap

- [x] Core authentication system with MFA
- [x] Module system with auto-discovery
- [x] Tasks module
- [ ] Frontend application (Next.js)
- [ ] Notes module
- [ ] Calendar module
- [ ] Finance module
- [ ] File management module
- [ ] Search service with vector DB
- [ ] AI integration
- [ ] Automation engine
- [ ] Mobile apps (iOS/Android)

---

**Built with ❤️ by the Lexicon Team**

