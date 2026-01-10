# 🏆 MIT ClimateTech Case Study: SolarSight
## Decarbonizing the Decentralized Grid

### 1. The Challenge: The "Last-Mile" Climate Gap
The global energy transition is currently bifurcated. While utility-scale solar is reaching record efficiency in stable markets, hundreds of millions of people in the Global South rely on decentralized solar coupled with backup diesel generators. Meanwhile, households in the Global North struggle with high-cost peak grid loads. 

The missing link isn't the hardware (panels/batteries); it’s **Predictive Intelligence**. Without high-resolution forecasting, solar energy is wasted, batteries are mismanaged, and diesel generators continue to fill the gaps.

### 2. The Solution: SolarSight Intelligence Engine
SolarSight is an AI-driven "Resilience-First" renewable energy forecasting platform. We provide a sub-300ms API layer that translates raw meteorological satellite data into actionable energy, financial, and climate metrics.

**Key Innovations:**
*   **Request Collapsing & Edge Optimization**: Architecture designed to serve high-fidelity forecasts even on low-bandwidth networks in emerging markets.
*   **Scientific Guardrails (Astronomical Night-Hour Zeroing)**: Implements physics-based models to eliminate "ghost energy" predictions, ensuring zero-carbon reporting integrity.
*   **Dynamic Regional Telemetry**: Proprietary mapping of grid-emission factors for 15 global cities, ensuring GHG Protocol Scope 2 compliance.

### 3. Market Scalability & Commercial Strategy
SolarSight targets the **Decentralized Energy Stakeholder** as its beachhead market:
1.  **Microgrid Operators (Global South)**: Providing the BMS (Battery Management System) intelligence layer to reduce diesel run-time by an estimated **20%**.
2.  **Smart-Home Ecosystems (Global North)**: Managing peak-load shifting for residential battery users in Europe and North America.
3.  **Industrial Agriculture**: Optimizing solar-powered irrigation and crop-drying windows (SDG 2).

**Scale Potential**: Our Docker-based infrastructure allows a single unified instance to serve 1,000+ global hubs with marginal cost nearing zero.

### 4. Quantified Climate Impact
By 2030, SolarSight aims to bridge the decarbonization gap for 5 million decentralized solar users, achieving a **Net Carbon Offset of 5.2 Megatonnes of CO2e**.

**SDG Matrix Integration:**
*   **SDG 7 (Clean Energy)**: 24h predictive yield optimization.
*   **SDG 13 (Climate Action)**: Regional carbon intensity accounting for GHG avoidance.
*   **SDG 2 & 3 (Resilience)**: Agricultural drying windows and UV-health advisories for outdoor workers.

### 5. Intellectual Property & Path to Finance
*   **IP Strategy**: Development of the **Location-Specific Correction Coefficients (LSCC)**—a proprietary algorithmic layer that adjusts for local soiling, humidity, and dust factors (Future Patent Path).
*   **Financial Path**: Seeking $250k in philanthropic climate grants (Seed) to pilot with 10 utility providers in Lagos and Madrid, transitioning to a B2B SaaS model ($0.05/API call).

---

# 👋 New Team Member Onboarding: "The SolarSight Way"

Welcome to the team! You are contributing to a platform built on the intersection of **Climate Science**, **Machine Learning**, and **High-Performance Web Engineering**.

### 1. The Core Philosophy
We build for **Resilience**. Our code must work whether the user is on a fiber-optic connection in Berlin or a 3G network in Nairobi. We prioritize data integrity, low latency, and scientific accuracy over "placeholders."

### 2. The Tech Stack
*   **Backend (The Brain)**: FastAPI (Python 3.11). It handles the orchestration of ML models, weather API rotation, and Redis caching.
*   **ML Pipeline (The Engine)**: Hybrid LightGBM and LSTM models. We use satellite data from Open-Meteo as primary features.
*   **Frontend (The Interface)**: React + TypeScript + Vite. Focus on "Glassmorphism" aesthetics to convey a premium, high-tech experience.
*   **Infrastructure (The Foundation)**: Docker Compose. We treat "Dev equals Prod" by containerizing everything.

### 3. How to Contribute
*   **Feature Branches**: Always branch from `master`.
*   **Atomic Commits**: Keep your commits focused (e.g., `feat: add new city`, `fix: chart alignment`).
*   **Documentation First**: If you add a new API or model parameter, update `README.md` and `CHANGES.md`.
*   **Testing**: Use `test_backend.py` and `verify_fixes.py` before pushing.

### 4. Key Directories
*   `/backend`: API logic, jobs, and services.
*   `/frontend`: React components and dashboard logic.
*   `/ml`: Training scripts and model artifacts.
*   `/infra`: Docker and deployment manifests.

### 5. Your First Task
Run the stack locally! 
```powershell
cd infra
docker-compose up --build
```
Once it's up, explore the **Streamlit Admin Hub** at `localhost:8502` to see how we monitor model performance across our 15 global cities.

---
**Building for the World, One Kilowatt at a Time.**
