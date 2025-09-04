# Meridian Tech Execution Plan (Markdown Extract)

## 1. Core Product Scope (Phase 1 MVP)
- **Features:**
  - Natal chart SVG render (using Swiss Ephemeris).
  - Daily AI-powered transit horoscopes (freemium baseline).
  - Astrocartography map (Leaflet.js, 2D lines for AC/DC/MC/IC).
  - Highlight circle tooltips: line metadata (house, degree, sign).
  - Personal library: saved charts, saved locations, stored interpretations.
  - Paid add-ons: automated reports, synastry readings.

## 2. Roadmap
- **Phase 1 (MVP):** Natal chart, horoscopes, freemium astrocartography map, highlight circles, PWA deployment.
- **Phase 2:** Advanced filters (asteroids, Hermetic lots, parans), relocation auto-casting, cyclocartography overlays, multi-chart library, enhanced AI chat.
- **Phase 3:** Community/social layer, gamification, astrologer marketplace, B2B licensing/API.

## 3. Tech Stack
- **Backend:** Python (FastAPI), Swiss Ephemeris library, Docker, Redis caching.
- **Frontend:** React + Vite, Progressive Web App (PWA), Leaflet.js (maps).
- **Hosting Platforms:**
  - Render.com (backend hosting, $7–25/mo starter).
  - Vercel (frontend hosting, ~$20/mo Pro tier).
  - Railway (DB + microservices, ~$10–25/mo each).
  - Netlify (optional frontend hosting, $19/mo team tier).
- **AI Layer:**
  - Cached lightweight model for horoscopes.
  - GPT API calls (premium outputs: reports, synastry).

## 4. Budget Allocation (Bootstrapped $10k)
- $800 — Swiss Ephemeris license.
- $1,200 — AI/API costs (OpenAI GPT, caching infra).
- $1,000 — Hosting & infrastructure (Render, Vercel, Railway, Netlify baseline).
- $2,500 — Marketing & community seeding (SEO, influencers).
- $2,500 — Contractors & trademark/IP legal.
- $1,000 — Miscellaneous + compliance filings.
- $1,000 — Contingency buffer.

## 5. Scaling & Cost Assumptions
- **Hosting/API per-user:** ~$0.05/month at 10k users; ~$0.02/month at 100k users (caching efficiency).
- **CAC (Customer Acquisition Cost):** $1–2 organic, $3–5 paid; ROI target positive by month 6.
- **Churn Target:** ≤7% monthly.
- **Conversion:** 2% (Year 1), 3–4% (Year 2), 5% (Year 3).

## 6. KPIs (Execution Targets)
- DAU/MAU ratio ≥ 25%.
- D7 retention ≥ 30%; D30 retention ≥ 15%.
- Conversion free→paid: 2–5%.
- Uptime ≥ 99.9%.
- ARPU ~$80 annually for premium users.

## 7. Risks (Execution-Focused)
- **Scalability:** Hosting/API costs spiking → mitigate via caching + batching.
- **Competitive Response:** Larger apps adding maps → Meridian advantage = purpose-built onboarding + advanced features.
- **Founder Bandwidth:** Two-person team → allocate $1.5–3k contractors for QA, marketing, compliance.
- **Legal/Privacy:** Ensure GDPR/CCPA compliance + user consent for data/analytics.

## 8. Execution Milestones
- **M1:** Build PWA MVP + core charting (3–4 months).
- **M2:** Launch closed beta with 500 users.
- **M3:** Public freemium launch, waitlist integration.
- **M4:** Phase 2 expansion (advanced filters, relocation casting).
- **M5:** Phase 3 expansion (community, marketplace, B2B licensing).
