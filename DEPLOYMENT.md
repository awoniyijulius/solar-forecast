# 🚀 SolarSight Deployment Guide

## Pre-Deployment Checklist

### ✅ Completed Fixes
- [x] Vite configuration created
- [x] Chart.js components registered
- [x] Pandas deprecated methods fixed
- [x] Streamlit requirements added
- [x] Admin API endpoints implemented
- [x] Frontend dependencies installed
- [x] Frontend build tested successfully

### 📋 Before Starting Docker Compose

1. **Verify Docker is running**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Review environment variables** (optional)
   ```bash
   cp .env.example .env
   # Edit .env if you want to customize settings
   ```

3. **Ensure ports are available**
   - 3000 (Frontend)
   - 8000 (Backend API)
   - 8502 (Streamlit)
   - 6379 (Redis)
   - 5432 (PostgreSQL)

## Quick Start (Recommended)

### Option 1: Full Stack with Docker Compose

```bash
# Navigate to infrastructure directory
cd infra

# Start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### What This Does

1. **Builds** all Docker images (backend, frontend, streamlit)
2. **Starts** Redis and PostgreSQL with health checks
3. **Waits** for dependencies to be healthy
4. **Starts** backend API with model server
5. **Runs** precompute job to cache predictions
6. **Starts** frontend and Streamlit admin

### Expected Timeline

- **Build time**: 3-5 minutes (first time)
- **Startup time**: 30-60 seconds
- **Precompute job**: 10-30 seconds (fetches forecasts for 10 cities)

## Accessing the Application

Once all services are running:

### 🌐 Frontend
**URL**: http://localhost:3000

**Features**:
- Location selector (10 cities)
- 24-hour prediction chart with confidence bands
- CO₂ metrics card with daily/weekly/monthly projections
- Auto-refresh every 15 minutes
- "Streamlight" button to admin dashboard

### 📊 API Documentation
**URL**: http://localhost:8000/docs

**Endpoints**:
- `GET /api/predictions/{location}` - Get forecasts
- `GET /health` - Health check
- `POST /admin/retrain` - Trigger retraining
- `GET /admin/metrics` - System metrics
- `GET /admin/cities` - List cities

### 🔧 Streamlit Admin
**URL**: http://localhost:8502

**Pages**:
- Overview - System metrics
- City Explorer - Fetch and visualize predictions
- Model Metrics - Performance stats
- Retrain Controls - Trigger model retraining
- Cache Stats - Redis statistics

## Verification Steps

### 1. Check Service Health

```bash
# Backend health
curl http://localhost:8000/health

# Expected: {"status":"healthy","service":"solar-sight-backend","version":"0.1.0"}
```

### 2. Test Predictions API

```bash
# Get predictions for Lagos
curl http://localhost:8000/api/predictions/lagos

# Expected: JSON with hours, pred_kwh, confidence, co2_kg_per_hour, co2_kg_total
```

### 3. Check Admin Endpoints

```bash
# List configured cities
curl http://localhost:8000/admin/cities

# Get system metrics
curl http://localhost:8000/admin/metrics
```

### 4. Frontend Checklist

- [ ] Page loads at http://localhost:3000
- [ ] Location selector shows 10 cities
- [ ] Chart renders with green line
- [ ] Confidence bands visible (dashed lines)
- [ ] CO₂ metrics card displays
- [ ] Hovering over chart shows CO₂ in tooltip
- [ ] "Streamlight" button opens http://localhost:8502

### 5. Streamlit Checklist

- [ ] Dashboard loads at http://localhost:8502
- [ ] Can navigate between pages
- [ ] City Explorer fetches data
- [ ] Charts render correctly

## Troubleshooting

### Issue: "Prediction not precomputed" (503 error)

**Cause**: Precompute job hasn't run yet or failed

**Solution**:
```bash
# Check precompute logs
docker-compose logs precompute

# Manually run precompute
docker-compose run --rm precompute
```

### Issue: Frontend can't connect to backend

**Cause**: Backend not started or proxy misconfigured

**Solution**:
```bash
# Check backend logs
docker-compose logs backend

# Verify backend is running
curl http://localhost:8000/health

# Restart backend
docker-compose restart backend
```

### Issue: Chart doesn't render

**Cause**: Chart.js not loaded or data format issue

**Solution**:
- Check browser console for errors
- Verify predictions API returns data
- Ensure frontend build completed successfully

### Issue: Model not found warning

**Cause**: No trained model artifact exists

**Solution**:
This is expected! The system will use a heuristic fallback based on solar radiation data. To train a real model:

```bash
# Install ML dependencies
cd ml
pip install -r ../backend/requirements.txt

# Train model
python train.py

# Model will be saved to ml/artifacts/lightgbm_model.joblib
```

### Issue: Redis connection failed

**Cause**: Redis not started or port conflict

**Solution**:
```bash
# Check Redis logs
docker-compose logs redis

# Verify Redis is running
docker-compose ps redis

# Restart Redis
docker-compose restart redis
```

## Development Mode

### Run Backend Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

### Run Precompute Job Manually

```bash
cd backend
python -m app.jobs.precompute
```

## ☁️ Cloud Deployment (Production Ready)

### Option A: Render.com (Recommended - Blueprints)

We have included a `render.yaml` Blueprint specification for one-click deployment.

1. **Push your code** to GitHub.
2. **Log in to Render.com** and go to "Blueprints".
3. **Click "New Blueprint Instance"** and select your repository.
4. Render will automatically detect the `render.yaml` file and provision:
   - **Backend API** (Python/FastAPI)
   - **Frontend** (Static Site/React)
   - **Admin Dashboard** (Streamlit)
   - **Redis Instance** (Managed Cache)
   - **Cron Job** (Precompute engine running every 15 mins)

**Note:** You will need to set the `ADMIN_API_KEY` manually in the Dashboard if you want to protect your admin routes.

### Option B: Railway / Heroku

If deploying manually (e.g., on Railway):

1. **Deploy Redis**: Start a Redis service first.
2. **Deploy Backend**:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Variables: `REDIS_URL=<your-redis-url>`
3. **Deploy Frontend**:
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `dist`
   - Variables: `VITE_API_URL=<your-backend-url>`
4. **Deploy Streamlit**:
   - Build Command: `pip install -r streamlit/requirements.txt`
   - Start Command: `streamlit run streamlit/app.py --server.port $PORT`

## Monitoring

### Health Checks

All services have health checks configured in docker-compose.yml:
- Redis: `redis-cli ping`
- PostgreSQL: `pg_isready`
- Backend: `curl /health`

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f precompute
docker-compose logs -f frontend
```

### Metrics to Monitor

- API response time
- Cache hit rate
- Prediction accuracy
- CO₂ calculation totals
- Error rates
- Precompute job success rate

## Next Steps

1. **Train a Real Model**
   ```bash
   cd ml
   python train.py
   ```

2. **Add Real NASA POWER Data**
   - Use `ml/scripts/fetch_historical_nasa_power.py`
   - Download historical data for your locations

3. **Customize Cities**
   - Edit `backend/app/jobs/precompute.py`
   - Or set `CITY_LIST` environment variable

4. **Set Up Continuous Precompute**
   - Use Kubernetes CronJob
   - Or set up system cron to run precompute every 15 minutes

5. **Deploy to Cloud**
   - Render, Railway, or Heroku for quick deployment
   - AWS/GCP/Azure for production scale

## Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify health: `curl http://localhost:8000/health`
3. Review CHANGES.md for what was fixed
4. Check README.md for architecture details

## Success Indicators

You'll know everything is working when:

✅ All Docker containers are running
✅ Backend health check returns 200
✅ Frontend loads and shows chart
✅ Predictions API returns data for all cities
✅ CO₂ metrics display correctly
✅ Streamlit admin dashboard is accessible
✅ No errors in docker-compose logs

**Happy forecasting! 🌞**
