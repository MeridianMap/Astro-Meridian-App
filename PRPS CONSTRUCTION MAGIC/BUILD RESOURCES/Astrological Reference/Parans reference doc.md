# Paran Lines — Technical Implementation Reference

A rigorous, implementation-first guide for computing planetary and star parans for astrocartography. Focus: math, numerical robustness, and predictable rendering. Keep interpretation out of this file.

---

## 0) Scope and definitions

Paran (paranatellonta): At a given location and instant, two bodies simultaneously occupy two different cardinal angles of the local sky: rising (ASC), setting (DSC), upper culmination (MC), or lower culmination (IC). For a fixed epoch, the set of locations where a given pair and event combo is simultaneous traces one or more circles of latitude.

Supported

* Planet–planet parans (geocentric apparent RA/Dec on the true equator and equinox of date).
* Planet–fixed star parans (stars precessed to date, optional proper motion and radial velocity).
* Event pairs E × E with E = {R, S, MC, IC}. Most maps prefer one meridian event and one horizon event; we support all.

Outputs

* Latitude solutions φ (degrees) per ordered pair and event combo.
* Optional visibility flags and daylight flags.
* Optional local timing by longitude using sidereal time.
* GeoJSON or analytic parallel primitives for rendering.

---

## 1) Time scales, coordinate frames, and inputs

Time scales

* Input epoch t in UTC. Sidereal time uses UT1. If UT1 is not available, UTC with small UT1 error is acceptable for mapping. If you already track ΔT for other modules, keep it, but it is not required for paran placement at daily cadence.

Ephemerides

* Planets: geocentric apparent right ascension α and declination δ on the true equator and equinox of date. If your provider returns astrometric places, apply light-time, annual aberration, precession-nutation to get apparent places. Most libraries expose a direct apparent call.
* Stars: start in ICRS at J2000 with position, proper motion (μα\*, μδ), parallax ϖ, and radial velocity if available. Propagate to epoch of date using IAU 2006/2000A precession-nutation. For bright high-μ stars (Sirius, Arcturus, Barnard’s), proper motion matters across decades.

Topocentric vs geocentric

* Use geocentric apparent positions for consistency with standard A*C*G. Provide an optional topocentric mode for the Moon and nearby planets if you need sub-pixel agreement with local rise/set clocks. Default off.

Observer

* Latitude φ in (−90°, +90°). Longitude λ is used for timing labels, not for the latitude solution itself.

Horizon convention

* Use the geometric horizon h = 0° for computations. Provide an optional apparent horizon mode with standard refraction at the horizon h0 = −0.5667° for stars and planets. For the Sun and Moon, you may include semidiameter and parallax if you want visual-event realism. Keep the default geometric for purity and reproducibility.

### 1.1) Units and numerical tolerances

* Angles: internal math in **radians**; I/O may expose degrees. Document conversion at API boundaries.
* Longitude sign: **east positive**. Ensure consistency with your GMST/GAST routine.
* Float precision: use **float64** throughout. Target absolute latitude error ≤ 0.03° for planets, ≤ 0.1° for high‑μ stars.
* Wrap helpers: implement `wrap_0_2π`, `wrap_−π_π`, `wrap_0_π`. Define them once in a shared math module and unit‑test.
* Clamp helper: `clip(x, −1, +1)` before every `acos`.
* Epsilon: `EPS = 1e−12` rad for equality checks on angles; `EPS_LAT = 1e−8` rad for solver convergence.
* Time anchor: prefer fixed daily epoch (e.g., 12:00 UTC) for deterministic products.
* Vectorization: batch operations over pairs and bodies; avoid Python loops in production code.

---

## 2) Spherical astronomy identities

Altitude at hour angle H for equatorial coordinates (α, δ) and latitude φ:

sin h = sin φ sin δ + cos φ cos δ cos H.

Horizon crossings (h = 0) occur at hour angle magnitude

cos H0(φ, δ) = − tan φ tan δ, with H0 in \[0, π].

Event hour angles He and sign convention H = LST − α:

* Rising (R): HR = − H0
* Setting (S): HS = + H0
* Upper culmination (MC): HMC = 0
* Lower culmination (IC): HIC = π

Local sidereal time at the event for body i:

LST\_i = α\_i + He\_i (wrap to \[0, 2π)).

Meridian altitudes (useful for visibility tests):

h\_MC = 90° − |φ − δ|,    h\_IC = −(90° − |φ + δ|).

Domain note: horizon events exist only if |tan φ tan δ| ≤ 1. Handle this explicitly.

**Sanity checks**

* If δ = φ, then h\_MC = 90° (zenith) and h\_IC = −90° (nadir).
* If δ = 0 and H0 = 0 (MC/R pair with Δα = 0), φ → −90° in the closed form — a useful limiting check.
* For symmetrical inputs (δ → −δ with same events), derived latitudes mirror across the equator.

---

## 3) Simultaneity condition (the paran equation)

Two bodies A and B are in paran for events e\_A and e\_B at any latitude φ satisfying

α\_A + He\_A(φ) = α\_B + He\_B(φ)  (mod 2π).

Let Δα = wrap to (−π, π] of (α\_B − α\_A). Then solve

He\_A(φ) − He\_B(φ) = Δα.

### 3.1 Closed form: one meridian event and one horizon event

Let body X be on the horizon with declination δX and event H in {R, S}; body Y is on the meridian with event M in {MC, IC}. Compute the required horizon angle H\_req from Δα and the event combo:

| Pair (Y on meridian, X on horizon) | H\_req before wrapping |
| ---------------------------------- | ---------------------- |
| (MC, R)                            | H\_req = +Δα           |
| (MC, S)                            | H\_req = −Δα           |
| (IC, R)                            | H\_req = Δα − π        |
| (IC, S)                            | H\_req = −Δα − π       |

Wrap into \[0, π] with a branch‑light helper: H0 = acos( clip( cos(H\_req), −1, +1 ) ). This keeps the principal solution while allowing Δα outside \[−π, π] in edge tests.

Recover latitude using a numerically stable arctangent form that avoids tan δ blow‑ups:

φ = atan2( − cos H0 · cos δX,  sin δX ).

This returns φ in (−90°, 90°). The construction guarantees a valid horizon crossing for X.

**Derivation note**
Using H = LST − α with H\_MC = 0 and H\_IC = π, the simultaneity condition reduces to matching LST at the meridian body and extracting the required H0 for the horizon body. The identity cos H0 = − tan φ tan δX then yields φ analytically.

**Notes**

* Swapping roles of A and B changes Δα. Compute each ordered pair explicitly.
* If you also require visibility (see 3.3), verify the meridian body’s altitude sign at the derived φ.

Notes

* Swapping roles of A and B changes Δα. Compute each ordered pair explicitly.
* If you also require visibility (see 3.3), verify the meridian body’s altitude sign at the derived φ.

### 3.2 General numeric solution: horizon vs horizon

Equation to solve for φ:

s\_A · arccos( − tan φ tan δ\_A )  −  s\_B · arccos( − tan φ tan δ\_B ) = Δα,

with signs s\_R = −1, s\_S = +1.

Use Brent or bisection over φ in \[−89.9°, +89.9°] and reject subintervals where either |tan φ tan δ\_i| > 1. Optional Newton refinement uses derivative

d/dφ arccos g(φ) = − g'(φ) / sqrt(1 − g(φ)^2),  where  g(φ) = − tan φ tan δ  and  g'(φ) = − sec^2 φ tan δ.

Return `None` for intervals where either horizon crossing is impossible. Ensure monotonic bracketing by splitting the latitude domain at the singular points where |tan φ tan δ| = 1 for either body.

Most production maps omit horizon–horizon parans. Keep support for QA and completeness.

### 3.3 Visibility filters (optional but useful)

Provide modes:

* all: no filtering beyond horizon definitions.
* both\_visible: both bodies above the geometric horizon at the instant.
* meridian\_visible\_only: only the meridian body must be above the horizon.

Checks:

* Horizon events are at h = 0° by definition (or h0 if using apparent horizon). If you require both\_visible, test the companion body’s altitude using the altitude identity at the simultaneous hour angle.
* For MC and IC, use h\_MC and h\_IC formulas above. At high latitudes, IC altitudes are often negative.

Optional realism:

* Apply a constant refraction offset R0 ≈ 0.5667° for stars and planets near the horizon. Bennett or Saemundsson formulas are available if you want temperature and pressure inputs. Keep the default off to avoid mixing models.
* For the Sun and Moon, include semidiameter and horizontal parallax when computing visible flags. This is for visual correctness only and does not change latitude solutions in geometric mode.

### 3.4 Degeneracies and non-solutions

* Both meridian events: solutions only when Δα ∈ {0, ±π}; these correspond to all latitudes (trivial) or none; suppress in maps.
* Circumpolarity: if |tan φ tan δ| > 1 for either body, R/S do not occur at that φ. The closed‑form path guarantees feasibility for the designated horizon body but not for the companion’s visibility.
* Polar limit: as |φ| → 90°, numerical noise grows; enforce solver guards and rendering clamps.

---

## 4) Sidereal time and timing labels

You may annotate each paran latitude with a local time label by longitude λ.

1. Compute GMST or GAST at epoch t using a tested routine (for example, SOFA iauGmst06 or iauGst06).
2. Local sidereal time at longitude λ is LST(λ) = GMST + λ (use GAST if you want the true equinox). Wrap to \[0, 2π). Use east‑positive λ in radians.
3. For a given paran line defined by (A, e\_A, B, e\_B, φ), the event LST is fixed: LST\_paran = α\_A + He\_A(φ).
4. To produce a local civil time at longitude λ, solve LST(UTC, λ) = LST\_paran for UTC using a root finder over the 24 h around t. The sidereal day is about 23 h 56 m; your root should find one solution per day per longitude.

This labeling is UX only. The position of the latitude does not depend on longitude.

---

## 5) Algorithm outline

Inputs at epoch t

* Bodies B = { (id, α, δ, is\_star) } on the true equator of date.
* Ordered event pairs to evaluate.

Compute

1. Precompute sin δ and cos δ arrays for all bodies.
2. For each ordered pair (A, e\_A), (B, e\_B):

   * Δα = wrap to (−π, π] of (α\_B − α\_A).
   * If one event is meridian and the other is horizon, use the closed form in 3.1.
   * If both are horizon, use the numeric solver in 3.2.
   * If both are meridian, a solution exists only when Δα is 0 or ±π. These are degenerate and usually suppressed.
   * Apply visibility filters if requested.
   * If a solution exists, append a line with φ (deg) and metadata.

Rendering

* Render each line as a parallel at constant latitude φ. Either sample 361 points (λ, φ) for λ in \[−180, 180] or use an analytic parallel primitive if your renderer supports it.
* Style by pair type and bodies.

---

## 6) Numerical practices and edge cases

* Wrapping: implement helpers wrap\_0\_2pi, wrap\_mpi\_pi, and wrap\_0\_pi using branch-light fmod and adjustments. Do not copy paste ad hoc wrap code.
* Clamps: clamp all acos inputs into \[−1, +1] to remove round-off spikes.
* atan2 form: prefer φ = atan2( − cos H0 cos δ,  sin δ ). Avoid atan of tan because tan δ loses precision near ±90°.
* Float precision: use float64; avoid mixed-precision on GPU pipelines unless thoroughly validated.
* Circumpolar: at high absolute φ, some bodies never rise or set. The analytic path guarantees a valid horizon crossing for the horizon body. If you also require the companion to be visible, test its altitude.
* Polar guard: keep numeric solvers away from |φ| ≥ 89.999°. Clamp rendered latitude to ±89.999° to avoid tile singularities.
* Equatorial and zenith cases: when δ is near φ, MC altitude approaches zenith and small numerical errors can flip the sign of h\_IC. Use the formulas in section 2 rather than inference.
* Time anchoring: use a fixed ephemeris epoch, for example t = 12:00 UTC for daily products, to maximize day-to-day stability. Planetary RA and Dec drift across a day is small and moves lines by a fraction of a degree.
* Stars: apply proper motion in ICRS, then precess to date. For catalogs that provide μα\* = dα/dt cos δ, convert carefully. A safe path is to form a Cartesian state vector in ICRS, add space motion, then apply precession-nutation; most libraries expose this.
* Refraction: if you enable it, keep a single model across the app to avoid user confusion. Record the model in metadata.
* Performance: precompute sin δ, cos δ, tan δ arrays; batch by event type; emit shared longitude grids for polyline sampling.

---

## 7) Validation plan

1. Unit tests

   * Analytic identity checks where Δα = 0, Δα = ±π, and δ = 0. Compare closed form and numeric solver outputs within 1e−10 rad.
   * Randomized fuzzing for 10k pairs. Ensure the wrapped difference (α\_A + He\_A) − (α\_B + He\_B) is below 1e−8 rad.

2. Cross-library

   * Compare a matrix of pairs for a canonical date to an independent implementation (Swiss Ephemeris or SOFA plus your own horizon logic). Require agreement within 0.05° for planets and 0.1° for high-μ stars when models match.

3. Regression

   * Freeze test vectors {α, δ, pair} → φ and assert within epsilon. Store per-epoch golden files.

4. Sanity plots

   * Visual check: lines must be exact parallels, symmetric about the equator for symmetric inputs. Any longitudinal curvature indicates a bug.

---

## 8) Performance

* Vectorize across pairs. The closed form costs a handful of trig ops per pair.
* Batch by pair type so horizon and meridian closed forms run in tight loops. Defer horizon and horizon numeric solves to a separate pass.
* Cache star positions for the date. They are constant for a daily map.
* If you emit sampled polylines, generate a shared longitude grid and broadcast φ.

---

## 9) Extensions

### 9.1 Planet–fixed star parans

* Treat the star as either horizon or meridian body. Same math. Include a toggle for classical all versus visible only.

### 9.2 Transit parans by latitude (dynamic overlays)

* For a sliding window, recompute α and δ and update φ in real time. Interpolate smoothly; do not jump between discrete epochs.

### 9.3 Local timing bands

* After computing φ, obtain LST\_paran = α\_A + He\_A(φ). At any longitude λ, solve GMST(UTC) + λ = LST\_paran for UTC within the civil day. Expose the next occurrence for tooltips.

---

## 10) Pseudocode (concise)

````python
# Inputs: epoch t (UTC); bodies = [{id, alpha, delta, is_star}], PAIRS = [(i,e_i,j,e_j)]
# Angles in radians; east-positive longitude; wrap helpers provided

pre = []
for b in bodies:
    pre.append((math.sin(b.delta), math.cos(b.delta)))

lines = []
for (i, e_i, j, e_j) in PAIRS:
    ai, di = bodies[i].alpha, bodies[i].delta
    aj, dj = bodies[j].alpha, bodies[j].delta
    si, ci = pre[i]
    sj, cj = pre[j]
    d_alpha = wrap_mpi_pi(aj - ai)

    def Hc(e):
        return 0.0 if e == 'MC' else (math.pi if e == 'IC' else None)

    Hi, Hj = Hc(e_i), Hc(e_j)

    if (Hi is not None) ^ (Hj is not None):
        # one meridian, one horizon (closed form)
        if Hj is None:
            # j on horizon
            H_req = (d_alpha - Hi) if e_j == 'R' else (Hi - d_alpha)
            H0 = wrap_0_pi(H_req)
            phi = math.atan2(-math.cos(H0) * cj, sj)
            mer_delta = di
            mer_event = e_i
        else:
            # i on horizon
            H_req = (-d_alpha - Hj) if e_i == 'R' else (Hj + d_alpha)
            H0 = wrap_0_pi(H_req)
            phi = math.atan2(-math.cos(H0) * ci, si)
            mer_delta = dj
            mer_event = e_j

        if visible_mode:
            # horizon body at h = 0 by definition
            if mer_event == 'MC':
                h_mer = math.radians(90) - abs(phi - mer_delta)
            else:  # IC
                h_mer = -(math.radians(90) - abs(phi + mer_delta))
            if require_meridian_above and h_mer <= 0:
                continue

        lines.append({
            'i': bodies[i].id, 'e_i': e_i,
            'j': bodies[j].id, 'e_j': e_j,
            'lat_deg': math.degrees(phi)
        })

    elif (Hi is None) and (Hj is None):
        # horizon vs horizon (numeric)
        s_i = -1.0 if e_i == 'R' else 1.0
        s_j = -1.0 if e_j == 'R' else 1.0
        ti, tj = math.tan(di), math.tan(dj)

        def F(phi):
            g_i = -math.tan(phi) * ti
            g_j = -math.tan(phi) * tj
            if abs(g_i) > 1 or abs(g_j) > 1:
                return None
            ai = max(-1.0, min(1.0, g_i))
            aj = max(-1.0, min(1.0, g_j))
            return s_i * math.acos(ai) - s_j * math.acos(aj) - d_alpha

        phi = brent_root(F, math.radians(-89.9), math.radians(89.9), tol=1e-8)
        if phi is not None:
            lines.append({
                'i': bodies[i].id, 'e_i': e_i,
                'j': bodies[j].id, 'e_j': e_j,
                'lat_deg': math.degrees(phi)
            })

    else:
        # both meridian: degenerate; ignore
        continue
```python
# Inputs: epoch t (UTC); bodies = [{id, alpha, delta, is_star}], PAIRS = [(i,e_i,j,e_j)]
# Angles in radians

pre = []
for b in bodies:
    pre.append((sin(b.delta), cos(b.delta)))

lines = []
for (i, e_i, j, e_j) in PAIRS:
    ai, di = bodies[i].alpha, bodies[i].delta
    aj, dj = bodies[j].alpha, bodies[j].delta
    si, ci = pre[i]
    sj, cj = pre[j]
    d_alpha = wrap_mpi_pi(aj - ai)

    def Hc(e):
        return 0.0 if e == 'MC' else (math.pi if e == 'IC' else None)

    Hi, Hj = Hc(e_i), Hc(e_j)

    if (Hi is not None) ^ (Hj is not None):
        # one meridian, one horizon (closed form)
        if Hj is None:
            # j on horizon
            H_req = (d_alpha - Hi) if e_j == 'R' else (Hi - d_alpha)
            H0 = wrap_0_pi(H_req)
            phi = math.atan2(-math.cos(H0) * cj, sj)
            mer_delta = di
            mer_event = e_i
        else:
            # i on horizon
            H_req = (-d_alpha - Hj) if e_i == 'R' else (Hj + d_alpha)
            H0 = wrap_0_pi(H_req)
            phi = math.atan2(-math.cos(H0) * ci, si)
            mer_delta = dj
            mer_event = e_j

        if visible_mode:
            # horizon body at h = 0 by definition
            if mer_event == 'MC':
                h_mer = math.radians(90) - abs(phi - mer_delta)
            else:  # IC
                h_mer = -(math.radians(90) - abs(phi + mer_delta))
            if require_meridian_above and h_mer <= 0:
                continue

        lines.append({
            'i': bodies[i].id, 'e_i': e_i,
            'j': bodies[j].id, 'e_j': e_j,
            'lat_deg': math.degrees(phi)
        })

    elif (Hi is None) and (Hj is None):
        # horizon vs horizon (numeric)
        s_i = -1.0 if e_i == 'R' else 1.0
        s_j = -1.0 if e_j == 'R' else 1.0
        ti, tj = math.tan(di), math.tan(dj)

        def F(phi):
            g_i = -math.tan(phi) * ti
            g_j = -math.tan(phi) * tj
            if abs(g_i) > 1 or abs(g_j) > 1:
                return None
            ai = max(-1.0, min(1.0, g_i))
            aj = max(-1.0, min(1.0, g_j))
            return s_i * math.acos(ai) - s_j * math.acos(aj) - d_alpha

        phi = brent_root(F, math.radians(-89.9), math.radians(89.9))
        if phi is not None:
            lines.append({
                'i': bodies[i].id, 'e_i': e_i,
                'j': bodies[j].id, 'e_j': e_j,
                'lat_deg': math.degrees(phi)
            })

    else:
        # both meridian: degenerate; ignore
        continue
````

---

## 11) Data schema (agentic)

Request

````json
{
  "epoch_utc": "2025-09-04T12:00:00Z",
  "bodies": [
    {"id": "Sun", "alpha": 2.123, "delta": 0.182},
    {"id": "Sirius", "alpha": 1.767, "delta": -0.290, "is_star": true}
  ],
  "pairs": [
    {"a": "Sun", "event_a": "MC", "b": "Sirius", "event_b": "R"}
  ],
  "visibility": "all",
  "models": {"horizon": "geometric", "refraction": null, "topocentric": false}
}
```json
{
  "epoch_utc": "2025-09-04T00:00:00Z",
  "bodies": [
    {"id": "Sun", "alpha": 2.123, "delta": 0.182},
    {"id": "Sirius", "alpha": 1.767, "delta": -0.290, "is_star": true}
  ],
  "pairs": [
    {"a": "Sun", "event_a": "MC", "b": "Sirius", "event_b": "R"}
  ],
  "visibility": "all"
}
````

Response

````json
{
  "paran_lines": [
    {
      "a": "Sun", "event_a": "MC", "b": "Sirius", "event_b": "R",
      "latitude_deg": -23.456,
      "meta": {
        "epoch_utc": "2025-09-04T12:00:00Z",
        "horizon": "geometric",
        "visibility": "all"
      }
    }
  ]
}
```json
{
  "paran_lines": [
    {
      "a": "Sun", "event_a": "MC", "b": "Sirius", "event_b": "R",
      "latitude_deg": -23.456,
      "meta": {"epoch_utc": "2025-09-04T00:00:00Z", "horizon": "geometric"}
    }
  ]
}
````

---

## 12) Checklists

### Core correctness

*

### Reproducibility

*

### Performance

*

### QA fixtures

*

---

## 13) Sources for the math (keep brief)

* Standard spherical astronomy identities for altitude and hour angle.
* IAU 2006/2000A precession‑nutation and sidereal time (SOFA is the reference implementation).
* Classical paran practice in the astrological literature for visibility options.

## 14) Helper API (recommended signatures)

```python
wrap_0_2pi(x: float) -> float
wrap_mpi_pi(x: float) -> float
wrap_0_pi(x: float) -> float
clip(x: float, lo: float=-1.0, hi: float=1.0) -> float
altitude(phi: float, delta: float, H: float) -> float  # returns h in radians
GMST(t_utc: datetime) -> float
LST(gmst: float, lon_east_rad: float) -> float
```

## 15) Acceptance criteria

* Deterministic lines across platforms for the same epoch and model flags.
* Unit and regression tests passing; fuzz tests within stated error budgets.
* Visual inspection: constant‑latitude lines with no longitudinal curvature; symmetry checks pass.
* Metadata clearly states models used so QA can reproduce results.

End of spec.
