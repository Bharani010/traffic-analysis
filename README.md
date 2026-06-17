# 🔍 Traffic Analysis Platform

**AI-Powered Anomaly Detection & Traffic Analysis**

An enterprise-grade platform for simulating, processing, and analyzing web traffic at scale. Detects anomalies using rules, statistical methods, and machine learning. Investigates incidents with LLM agents and generates comprehensive reports — all through a real-time dashboard.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│              TypeScript • Tailwind • Vite                │
├─────────────────────────────────────────────────────────┤
│                   Backend (FastAPI)                       │
│         SQLAlchemy • Alembic • Structlog • Prometheus    │
├──────────────┬──────────────────┬────────────────────────┤
│  PostgreSQL  │      Redis       │    PySpark Pipeline    │
│   (Storage)  │  (Cache/Queue)   │  (Processing/ML)       │
└──────────────┴──────────────────┴────────────────────────┘
```

## 📁 Project Structure

```
traffic-analysis/
├── backend/                # FastAPI backend service
│   ├── app/
│   │   ├── core/           # Config, DB, logging, metrics, security
│   │   ├── features/       # Feature modules (health, traffic, anomalies)
│   │   ├── middleware/      # Request ID, metrics middleware
│   │   ├── models/         # SQLAlchemy base models
│   │   └── migrations/     # Alembic migrations
│   ├── tests/              # Pytest unit & integration tests
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/               # React + TypeScript + Tailwind
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── features/       # Feature-based pages
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API client
│   │   ├── types/          # TypeScript types
│   │   └── lib/            # Utilities
│   ├── Dockerfile
│   └── package.json
├── data/                   # PySpark data pipeline
│   ├── jobs/               # Spark jobs (simulate, process, detect)
│   ├── schemas/            # Spark schema definitions
│   └── utils/              # Spark session factory
├── e2e/                    # Playwright end-to-end tests
├── .github/workflows/      # GitHub Actions CI/CD
├── docker-compose.yml      # Full stack orchestration
├── Makefile                # Development convenience commands
└── .env.example            # Environment variable template
```

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose** (recommended)
- **Python 3.11+** (for local backend development)
- **Node.js 20+** (for local frontend development)

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/traffic-analysis.git
cd traffic-analysis

# Copy environment variables
cp .env.example .env

# Start all services
docker compose up --build

# Access the application
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/api/docs
# Metrics:   http://localhost:8000/metrics
```

### Generating the Data Dataset
To test the pipeline locally, you need to generate the anomaly dataset first:
```bash
# This runs the Traffic Simulator, PySpark ETL, and Scikit-Learn Detection Engine
.\run_pipeline.bat
```

### Local Development (Without Docker)

You can run the entire platform locally without Docker by using the provided convenience script:

```bash
# Starts both the FastAPI Backend (Port 8000) and React Frontend (Port 3000)
.\run_local.bat
```

*Note: For the LangChain Investigation Agent to use OpenAI, ensure you add your `OPENAI_API_KEY` to the `.env` file. Otherwise, it will seamlessly fall back to a Mock LLM for offline testing.*

# Run tests
```bash
make test
```

## 📦 Make Commands

| Command | Description |
|---------|-------------|
| `make dev` | Start all services with Docker |
| `make dev-backend` | Start backend locally |
| `make dev-frontend` | Start frontend locally |
| `make test` | Run all tests |
| `make lint` | Run linters |
| `make migrate` | Run database migrations |
| `make clean` | Remove build artifacts |

## 🧪 Testing

```bash
# Backend tests
cd backend && pytest -v

# Frontend build check
cd frontend && npm run build

# End-to-end tests
cd e2e && npx playwright test
```

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, Python 3.11, SQLAlchemy 2.0, Alembic |
| **Frontend** | React 18, TypeScript, Tailwind CSS 3, Vite |
| **Database** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **Data** | PySpark 3.5 |
| **Testing** | Pytest, Playwright |
| **CI/CD** | GitHub Actions |
| **Infra** | Docker, Docker Compose |
| **Monitoring** | Prometheus, Structlog |

## 📄 License

MIT
