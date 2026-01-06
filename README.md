# 🌞 SolarSight - Solar Energy Forecasting Platform

Real-time solar energy prediction platform with 24-hour hourly forecasts, carbon offset tracking, and multi-city support.

## Features

- ✅ **24-hour hourly predictions** with confidence bands
- ✅ **Multi-city support** (10 global cities)
- ✅ **Carbon offset calculations** (CO₂ avoided from solar generation)
- ✅ **Precompute + cache pattern** (Redis for instant API responses)
- ✅ **Streamlit admin dashboard** for model debugging and retraining
- ✅ **Nature-themed React frontend** with SDG footer
- ✅ **Docker Compose** for local development
- ✅ **Financial ROI Estimator** (Dynamic currency calc per city)
- ✅ **Scientific Asset Telemetry** (Pyranometer, Inverter, & Revenue-Grade metering)
- ✅ **Production-ready architecture** with health checks and monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (React + TypeScript + Vite)                   │
│  • Location selector • Charts • CO₂ metrics             │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  Backend API (FastAPI)                                  │
│  • /api/predictions/{city} • /admin/* • /health         │
└─────┬──────────────────────────────────┬────────────────┘
      │                                  │
┌─────▼──────────┐              ┌────────▼───────────────┐
│  Redis Cache   │              │  PostgreSQL/TimescaleDB│
│  (15min TTL)   │              │  (Historical data)     │
└────────────────┘              └────────────────────────┘
      ▲                                  ▲
      │                                  │
┌─────┴──────────────────────────────────┴────────────────┐
│  Precompute Job (Runs on startup + manual trigger)      │
│  1. Fetch forecasts (Open-Meteo API)                    │
│  2. Run inference (LightGBM Model)                      │
│  3. Calculate CO₂ avoided                               │
│  4. Cache results → Redis + DB                          │
```

##  Cloud Deployment (Zero-Cost Architecture)

The platform is deployed on **Render Free Tier** using a highly optimized "Zero-Cost" blueprint:
- **Core Engine**: FastAPI Backend with `DiskCache` (No external Redis required).
- **Frontend**: React + Vite (Static Site).
- **Admin Hub**: Streamlit (Python Service).
- **Automation**: AsyncIO Background Loop for data precomputation (No external Cron required).

**[👉 View Live Demo](https://solarsight-intel.onrender.com)**

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### 1. Clone and Setup

```bash
cd solar-forecast
cp .env.example .env
# Edit .env if needed
```

### 2. Start All Services

```bash
cd infra
docker-compose up --build
```

This will start:
- **Redis** (port 6379)
- **PostgreSQL/TimescaleDB** (port 5432)
- **Backend API** (port 8000)
- **Frontend** (port 3000)
- **Streamlit Admin** (port 8502)
- **Precompute Job** (runs once on startup)

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Streamlit Admin**: http://localhost:8502
- **Health Check**: http://localhost:8000/health

## Development

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Precompute Job Manually

```bash
cd backend
python -m app.jobs.precompute
```

### Train ML Model

```bash
cd ml
python train.py
```

## Project Structure

```
solar-forecast/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints (predictions, admin)
│   │   ├── services/    # Weather client, cache, CO₂, features
│   │   ├── models/      # Model server
│   │   └── jobs/        # Precompute job
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            # React + TypeScript frontend
│   ├── src/
│   │   ├── components/  # Dashboard, Chart, InsightCard
│   │   └── styles/      # Tailwind CSS
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── ml/                  # Machine learning pipeline
│   ├── train.py         # Model training
│   ├── preprocess.py    # Data preprocessing
│   ├── artifacts/       # Trained models
│   └── data/           # Training data
├── streamlit/          # Admin dashboard
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
└── infra/              # Infrastructure
    ├── docker-compose.yml
    └── k8s/            # Kubernetes manifests (future)
```

## API Endpoints

### Predictions

- `GET /api/predictions/{location}` - Get 24-hour forecast for a city
  - Returns: hourly predictions, confidence bands, CO₂ avoided
  - Cached with 15-minute TTL

### Admin (Protected)

- `POST /admin/retrain` - Trigger model retraining
- `GET /admin/metrics` - System health and cache stats
- `PUT /admin/emission-factor/{location}` - Update CO₂ emission factor
- `GET /admin/cities` - List configured cities

### Health

- `GET /health` - Health check endpoint

## Supported Cities

- Lagos, Nigeria
- Nairobi, Kenya
- Cape Town, South Africa
- London, UK
- Berlin, Germany
- Paris, France
- Tokyo, Japan
- New York, USA
- Dubai, UAE
- Sydney, Australia

## CO₂ Calculation

**Formula**: `CO₂ avoided (kg) = Energy (kWh) × Emission Factor (kg CO₂/kWh)`

- Default emission factor: **0.475 kg CO₂/kWh** (global average grid intensity)
- Configurable per region via admin API
- Confidence bands derived from prediction uncertainty

## Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `REDIS_URL` - Redis connection string
- `DATABASE_URL` - PostgreSQL connection string
- `MODEL_PATH` - Path to trained model artifact
- `TTL_SECONDS` - Cache TTL (default: 900 = 15 minutes)
- `ADMIN_API_KEY` - Admin API authentication key

## Troubleshooting

### Predictions return 503

The precompute job may still be running. Wait 1-2 minutes and refresh.

### Frontend can't connect to backend

Check that:
1. Backend is running on port 8000
2. CORS is enabled (already configured)
3. Vite proxy is configured correctly

### Model not found

Train the model first:
```bash
cd ml
python train.py
```

Or use the heuristic fallback (automatic if no model exists).

## Production Deployment

### Kubernetes

See `infra/k8s/` for deployment manifests (coming soon).

### Cloud Platforms

- **Render**: Deploy backend + frontend + Redis
- **Railway**: Full-stack deployment with PostgreSQL
- **AWS/GCP/Azure**: Use managed Kubernetes (EKS/GKE/AKS)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open a GitHub issue.

## Acknowledgments

- Weather data: [Open-Meteo API](https://open-meteo.com/)
- Historical data: [NASA POWER](https://power.larc.nasa.gov/)
- Aligned with **UN SDG 7** (Affordable and Clean Energy), **SDG 11** (Sustainable Cities), and **SDG 13** (Climate Action)

---

**Built with ❤️ for a sustainable future** 🌍