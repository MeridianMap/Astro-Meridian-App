# PRP 0: Initiation & Environment Setup

## Goal
Establish a clean, reproducible environment and install all required tools, libraries, and reference materials for the Meridian Ephemeris Engine project.

## Deliverables
- Python (>=3.10) installed and available in PATH
- Node.js (>=18) and npm installed
- React + Vite project scaffolded (frontend)
- PySwisseph (2.10.x) installed and ephemeris files downloaded
- Immanuel Python cloned and installed in editable mode (for reference only)
- Swiss Ephemeris files (sepl_*.se1, semo_*.se1, seleapsec.txt, sedeltat, sefstars.txt)
- tzdata (Windows)
- Dev tools: ruff, mypy, pytest, hypothesis, httpx, pytest-asyncio, pytest-benchmark
- Meridian dev philosophy and PRP process docs available

## Steps
1. Install Python >=3.10 ([python.org](https://www.python.org/downloads/))
2. Install Node.js >=18 ([nodejs.org](https://nodejs.org/))
3. `npm create vite@latest` (choose React + TypeScript)
4. `pip install pyswisseph==2.10.* python-dateutil timezonefinder tzdata numpy`
5. Download Swiss Ephemeris files from [astro.com](https://www.astro.com/swisseph/swephinfo_e.htm) and place in a known directory
6. `git clone https://github.com/theriftlab/immanuel-python.git` and `pip install -e ./immanuel-python`
7. `pip install ruff mypy pytest hypothesis httpx pytest-asyncio pytest-benchmark`
8. Ensure `tzdata` is installed on Windows: `pip install tzdata`
9. Place dev philosophy and PRP process docs in `context and plans/`
10. Document all install steps and environment variables in `README.md`

## Validation
- `python --version` and `node --version` print correct versions
- `pytest` runs and passes on a sample test
- `npx vite --version` prints Vite version
- `python -c "import swisseph"` runs without error
- Immanuel Python tests pass
- All reference docs are present and readable

## Additional Tools & References (2025 Update)

- NumPy, Numba, SciPy for vectorized and high-performance calculations
- Redis and hiredis for distributed caching
- Prometheus, Grafana, Sentry, OpenTelemetry for monitoring and error tracking
- Docker, Docker Compose for local and CI environments
- Astroquery, Astropy for JPL Horizons validation
- MkDocs Material, Mermaid, OpenAPI Generator for docs and SDKs
- Playwright, k6 for E2E and load testing
- Strawberry GraphQL for optional API
- PyO3/Rust for future critical-path optimization
- Reference projects: Skyfield, AstroML, Astral, Kosmorrolib, TimezoneFinder

## Swiss Ephemeris as Gold Standard
- All calculations, tests, and validations must use Swiss Ephemeris as the authoritative backend.
- VSOP87, JPL, and other sources are for validation and cross-checking only.

## Notes
- Use virtual environments for Python (`python -m venv venv`)
- Use `requirements.txt` and `requirements-dev.txt` for dependencies
- Document any platform-specific quirks (Windows paths, tzdata)

---

# [END OF INITIATION PRP]
