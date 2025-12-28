# Architecture Overview

- Data ingestion: Open-Meteo for live forecasts; NASA POWER for historical training.
- Storage: TimescaleDB for time-series; Redis for cache.
- ML: LightGBM baseline; optional LSTM for temporal modeling.
- Backend: FastAPI serving cached predictions and admin endpoints.
- Frontend: React SPA with nature theme and SDG footer.
- Admin: Streamlit for model ops and data exploration.
- Deployment: Docker Compose for local dev; Kubernetes manifests for production.
