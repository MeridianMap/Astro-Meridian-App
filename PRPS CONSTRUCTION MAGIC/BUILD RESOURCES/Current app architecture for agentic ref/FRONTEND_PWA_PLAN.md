# Frontend PWA Plan

## 1. Objectives
Provide an installable, offline-capable, low-latency UI for Meridian Ephemeris (natal charts, ACG lines, animation) leveraging existing REST API; enable future agentic augmentation.

## 2. Scope (Phase Breakdown)
| Phase | Feature Set | Exit Criteria |
|-------|-------------|---------------|
| P0 | Scaffold React+Vite TS, routing, service worker, manifest | App loads, installable, /health ping |
| P1 | Natal chart form + results view | Submit → chart JSON rendered, basic validation |
| P2 | ACG map (static lines) | Map with requested planetary lines overlaid |
| P3 | ACG animation player | Time slider / play, prefetch frames, offline replay |
| P4 | Batch submission dashboard | Upload CSV / paste list, show aggregated progress |
| P5 | Offline & Sync Enhancements | Background sync queue; resilient caching policies |
| P6 | Performance & UX Polish | Lighthouse PWA score ≥95; sub‑second nav |

## 3. Technology Choices
| Concern | Choice | Rationale |
|---------|--------|-----------|
| Build Tool | Vite + TS | Fast HMR, modern output |
| State / Server Data | TanStack Query | Built-in caching, retries, de-dupe |
| Global UI State | Zustand (or Context early) | Minimal boilerplate |
| Routing | React Router v6 | Nested routes, code splitting |
| 3D Globe/Mapping | Three.js, three-geo, Geo-Three, MeshLine, signal-line | 3D globe, animated astrocartography lines |
| Chart Rendering (fallback) | Canvas/SVG components | Simplify initial chart UI |
| PWA | vite-plugin-pwa + Workbox | Auto SW generation, runtimeCaching |
| Styling | Tailwind CSS | Rapid layout prototyping |
| Testing | Vitest + React Testing Library + Playwright | Unit + E2E + visual regression |
| i18n (future) | Lingui | Lightweight extraction |

## 4. Directory Structure (Proposed)
```
meridian-frontend/
  src/
    api/              # Fetch wrappers + types
    components/       # Reusable UI
    features/
      natal/
      acg/
      batch/
      animation/
      globe/          # Three.js globe and visualization logic
    hooks/
    pages/
    state/
    styles/
    swClient.ts
  public/
    manifest.webmanifest
    icons/
```

## 5. Core Data Flows
### Natal Chart Submission
Form → validate (client) → POST /ephemeris/natal → cache (react-query) → render components (planets table, houses) → offer export (JSON / PNG).

### ACG Lines
Form (epoch, bodies, lines) → POST /acg/lines → convert lat/lon to 3D globe coordinates (Three.js) → render lines/animations → offline line cache (IndexedDB) keyed by hash(params).

### ACG Animation
Request start/end/step → stream/iterate frames (consider chunked requests vs sequential) → convert to 3D globe coordinates → animate lines/frames on globe (Three.js) → maintain LRU frame store → playback controller.

## 6. Offline & Caching Strategy
| Asset/Data Type | Strategy | TTL |
|-----------------|----------|-----|
| Static build | Precache (revisioned) | Until next deploy |
| API GET meta (house systems etc.) | Stale‑While‑Revalidate | 24h |
| Natal chart POST results | Write-through cache (keyed by normalized input hash) | 12h |
| ACG lines | NetworkFirst fallback cache | 24h |
| Animation frames | Opportunistic prefetch + LRU in IndexedDB | Session |
| Globe assets/tiles | StaleWhileRevalidate with cap | 7d |

## 7. Normalized Cache Key (Pseudo)
```
key = sha256(json.dumps({endpoint, version:1, payload:canonical_sort(payload)}, separators=(',',':')))
```

## 8. Performance Targets
| Metric | Target |
|--------|--------|
| First Contentful Paint | < 1.5s (desktop), < 2.5s (mobile) |
| Interactive (TTI) | < 3s mobile |
| API latency mask | Show skeleton if >150ms |
| Page bundle (initial) | < 180KB gzipped |

## 9. Security & Privacy Considerations
- Strip PII beyond name (optional hash) before local persistence.
- Service worker: validate origin; no opaque third‑party caching.
- Future auth: attach JWT via interceptor; refresh handling.

## 10. Accessibility
- WCAG 2.1 AA baseline (focus ring, color contrast, ARIA landmarks, keyboard map nav).
- Provide textual alt for chart components.

## 11. Telemetry (Opt‑In)
| Event | Fields |
|-------|--------|
| natal_calculated | duration_ms, cache_hit, planet_count |
| acg_lines_loaded | duration_ms, line_types, bodies |
| animation_played | frame_count, span_minutes |

## 12. Risk & Mitigation
| Risk | Mitigation |
|------|-----------|
| Large animation payload | Lazy frame fetch; compression (gzip) |
| Map tile licensing | Confirm provider TOS; configurable tile URL |
| Offline stale data | Embed generation timestamp + staleness UI |
| SW update confusion | Use `registerSW` onNeedRefresh toast |

## 13. Incremental Delivery Milestones
- M1: Natal only, no map.
- M2: Add map with static lines.
- M3: Add animation timeline.
- M4: Offline caching & install prompt.
- M5: Batch dashboard + CSV ingest.

## 14. Automated Testing Matrix
| Layer | Tool | Focus |
|-------|------|-------|
| Unit | Vitest | Components / hooks |
| Integration | RTL + MSW | API interaction & error states |
| E2E | Playwright | Critical flows (natal, ACG lines) |
| Perf | Lighthouse CI | PWA scores |
| Visual | Playwright snapshots | Map & chart regressions |

## 15. Backlog (Future)
- Push notifications for saved chart completion.
- Background Sync for offline batch queue.
- WebAssembly astro kernels (optional).
- Theming system (user palettes / dark forced). 
- GraphQL client support when backend added.
- Advanced globe features: planetary animation, interactive 3D controls, custom shaders for lines.

---
Status: Draft approved baseline for frontend kickoff.
