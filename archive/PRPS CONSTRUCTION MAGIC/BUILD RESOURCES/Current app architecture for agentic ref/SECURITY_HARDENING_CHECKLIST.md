# Security Hardening Checklist

Holistic security baseline for Meridian Ephemeris pre-production launch.

## 1. Network & Transport
- [ ] Enforce HTTPS (HSTS, preload list consideration)
- [ ] TLS 1.2+ only; strong ciphers; automated cert renewal (Let's Encrypt / ACM)
- [ ] Remove server banner headers (uvicorn, FastAPI defaults) or obfuscate
- [ ] Rate limiting middleware validated (unit + integration tests)

## 2. Authentication & Authorization
- [ ] Decide auth model (API keys vs OAuth2/JWT)
- [ ] Implement dependency-based auth enforcement per route group
- [ ] Scoped tokens (read, write, batch)
- [ ] Token rotation procedure documented
- [ ] Replay protection (nonce / timestamp for signed requests if API keys)

## 3. Input Validation
- [x] Pydantic models for core payloads
- [ ] Coordinate↔timezone consistency check
- [ ] Enforce max payload size (FastAPI / ASGI server settings)
- [ ] Strict JSON content-type validation

## 4. Output & Error Handling
- [ ] Normalize error schema (single canonical format)
- [ ] Strip internal tracebacks in production
- [ ] Include correlation/request ID header in responses

## 5. Caching & Data Protection
- [ ] Sensitive data excluded from cache keys/values
- [ ] Redis AUTH / TLS configured (if remote)
- [ ] Cache key hashing (sha256) for large composite keys
- [ ] Memory cache size & TTL tuned to prevent data retention beyond purpose

## 6. Dependency & Supply Chain
- [ ] Automated dependency scan (pip-audit / safety) in CI
- [ ] Pin transitive deps via lock (uv/poetry or pip-tools optional)
- [ ] SBOM generation (CycloneDX) stored with build artifact
- [ ] Monitor Swiss Ephemeris updates for security advisories

## 7. Secrets Management
- [ ] No secrets in repo (scan via gitleaks)
- [ ] Central secret store (Vault / AWS SM / Azure KV)
- [ ] Rotational schedule documented (quarterly min)

## 8. Logging & Monitoring
- [ ] Structured logging w/ level controls
- [ ] PII classification rules; mask user identifiers beyond name hash
- [ ] Alerting thresholds: error rate, latency, cache miss spike
- [ ] 24h retention for debug logs (prod), extended in cold storage if needed

## 9. Metrics & Tracing
- [ ] Prometheus metrics validated (requests, durations, cache hits)
- [ ] High-cardinality label audit (prevent blowups)
- [ ] Tracing (OpenTelemetry) instrumentation plan

## 10. Data Integrity & Accuracy
- [ ] Ephemeris file checksum verification at startup
- [ ] Fallback behavior if files missing (fail fast vs degraded mode)
- [ ] Cross-validation sample against Immanuel reference on deploy

## 11. Performance & Abuse Prevention
- [ ] API concurrency limit (uvicorn workers sizing plan)
- [ ] Burst traffic soak test (k6) with pass criteria
- [ ] Pagination or streaming for large batch responses

## 12. Frontend / PWA Specific
- [ ] Content Security Policy (script-src 'self'; no inline) + nonce support
- [ ] Service Worker scope restricted; no opaque third-party caching
- [ ] Input sanitization for any dynamic HTML (avoid dangerouslySetInnerHTML)
- [ ] Offline cache versioning to purge stale sensitive data

## 13. Infrastructure & Deployment
- [ ] Immutable image builds (digest pinned)
- [ ] CI/CD signed artifacts (cosign / provenance attestations)
- [ ] Rollback playbook documented & tested
- [ ] Resource limits (CPU/memory) set for containers

## 14. Backup & Recovery
- [ ] Ephemeris data immutable mirror (S3 bucket / CDN)
- [ ] Configuration snapshot per deploy
- [ ] Disaster recovery test (simulate ephemeris path loss)

## 15. Legal & Compliance
- [ ] License compliance audit (Swiss Ephemeris redistribution terms)
- [ ] Privacy notice for stored logs / telemetry
- [ ] Data retention policy published

## 16. Final Pre-Launch Gate
| Gate | Criteria |
|------|----------|
| Security Review | All high-risk items closed or accepted with mitigation |
| Pen Test | Critical vulns remediated |
| Load Test | Meets latency SLO (<100ms median) |
| DR Drill | Recovery < target RTO |

---
Status: Draft – update as controls are implemented.
