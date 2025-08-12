# Meridian Ephemeris Engine

A high-precision astronomical calculation engine with React frontend and Python backend, using Swiss Ephemeris as the gold standard for ephemeris calculations.

## Environment Setup

### Prerequisites

- **Python >=3.10** ([python.org](https://www.python.org/downloads/))
- **Node.js >=18** ([nodejs.org](https://nodejs.org/))

### Current Status
- ✅ Node.js v22.14.0 installed
- ❌ Python 3.9.13 detected - **NEEDS UPGRADE to >=3.10**
- ✅ React + Vite project created (`meridian-frontend/`)
- ✅ Project directories created

## Setup Instructions

### 1. Python Environment
```bash
# After upgrading Python to >=3.10, create virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Python Dependencies
```bash
pip install pyswisseph==2.10.* python-dateutil timezonefinder tzdata numpy
pip install ruff mypy pytest hypothesis httpx pytest-asyncio pytest-benchmark
```

### 3. Frontend Dependencies
```bash
cd meridian-frontend
npm install
npm run dev
```

### 4. Swiss Ephemeris Files
Download from [astro.com](https://www.astro.com/swisseph/swephinfo_e.htm):
- `sepl_*.se1` (planet files)
- `semo_*.se1` (moon files) 
- `seleapsec.txt` (leap seconds)
- `sedeltat` (delta T)
- `sefstars.txt` (fixed stars)

Place in `ephemeris/` directory.

### 5. Immanuel Python (Reference)
```bash
git clone https://github.com/theriftlab/immanuel-python.git
pip install -e ./immanuel-python
```

## Project Structure
```
Meridian Ephemeris V1/
├── meridian-frontend/          # React + Vite frontend
├── context and plans/          # Development docs
├── ephemeris/                  # Swiss Ephemeris files (create after download)
├── immanuel-python/           # Reference implementation (after clone)
├── requirements.txt           # Python dependencies (to be created)
├── requirements-dev.txt       # Development dependencies (to be created)
└── README.md                  # This file
```

## Additional Tools (Planned)

### Performance & Optimization
- NumPy, Numba, SciPy for vectorized calculations
- PyO3/Rust for critical-path optimization

### Infrastructure
- Redis and hiredis for distributed caching
- Docker, Docker Compose for containerization

### Monitoring & Observability
- Prometheus, Grafana for metrics
- Sentry for error tracking
- OpenTelemetry for tracing

### Testing & Validation
- Astroquery, Astropy for JPL Horizons validation
- Playwright for E2E testing
- k6 for load testing

### Documentation & API
- MkDocs Material for documentation
- Strawberry GraphQL for optional API
- OpenAPI Generator for SDK generation

## Validation Commands

After setup completion:
```bash
# Version checks
python --version        # Should be >=3.10
node --version         # Should be >=18
npx vite --version     # Should show Vite version

# Import tests
python -c "import swisseph"    # Should run without error
pytest                         # Should run sample tests

# Frontend
cd meridian-frontend && npm run dev  # Should start dev server
```

## Swiss Ephemeris as Gold Standard

All calculations, tests, and validations use Swiss Ephemeris as the authoritative backend. VSOP87, JPL, and other sources are for validation and cross-checking only.

## Reference Projects
- Skyfield, AstroML, Astral, Kosmorrolib, TimezoneFinder

---

*This project follows the Meridian development philosophy and PRP (Phased Release Process) methodology.*