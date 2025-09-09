# ACG Parans (Jim Lewis) — Technical Implementation Reference (Agentic v1.3)

A rigorous, implementation‑first guide for **Jim Lewis–style Astro*Carto*Graphy (ACG) planetary parans**: places where **two planets are simultaneously on different cardinal angles** (ASC, DSC, MC, IC) at a single instant. This is **planet–planet** only (no fixed‑star parans), aligned to classic ACG practice. Keep interpretation out of this file.

---

## 0) Scope and definitions

**Paran (ACG, Jim Lewis):** At a given location and instant, bodies *A* and *B* simultaneously occupy two different angles of the local sky: rising (ASC), setting (DSC), upper culmination (MC), or lower culmination (IC). For a fixed epoch *t*, the locus of locations where a given event pair happens **simultaneously** forms one or more **parallels (constant latitudes)** on the Earth.

Supported

* **Planet–planet** parans using **geocentric apparent** places on the **true equator/equinox of date** (Sun–Pluto; Moon optional; include Uranus/Neptune/Pluto per ACG norm).
* Event pairs **E × E with E = {R, S, MC, IC}**. In practice, ACG emphasizes **meridian–horizon** pairs; we fully support all.

Outputs

* Latitude solutions **φ** (degrees) per ordered pair and event combo.
* Optional visibility flags (e.g., meridian body above horizon) and daylight flags.
* Optional **local timing labels** by longitude using sidereal time.
* GeoJSON polylines for rendering parallels, or analytic parallel primitives.

Non‑goals (out of scope for this spec)

* Fixed‑star parans (Brady style) — excluded.
* Daily “proximity bands”/orbs — we compute exact simultaneity; any stylistic banding is a rendering concern.

---

## 1) Time scales, frames, models

**Time scales**

* Input epoch **t** in **UTC**. Sidereal time uses **UT1**. If UT1 not available, use UTC (UT1–UTC error is negligible for map placement). If you already track **ΔT**, keep it for consistency elsewhere; not required here.

**Ephemerides**

* **Planets**: use **geocentric apparent** right ascension **α** and declination **δ** on the **true equator/equinox of date** (include light‑time, aberration, precession‑nutation). Most libraries expose this directly.

**Topocentric vs geocentric**

* **Default geocentric**, consistent with ACG. Provide an optional **topocentric** mode (mainly for Moon) if a product demands sub‑pixel agreement with local rise/set clocks. Default off.

**Observer**

* Latitude **φ ∈ (−90°, +90°)**. Longitude **λ** is used only for **timing labels**; latitude solutions are **independent of λ**.

**Horizon convention**

* Default **geometric horizon**: altitude **h = 0°**. Optional apparent horizon mode with a constant refraction offset **h₀ = −0.5667°** (Sun/Moon semidiameter/parallax can be included for *visibility flags only*). Keep geometry pure for line placement.

### 1.1 Units & tolerances

* Internal angles: **radians**; I/O may expose degrees. Document conversions.
* Longitude sign: **east positive**. Use same sign in GMST/LST routines.
* Float: **float64** throughout. Target |Δφ| ≤ **0.03°** for planets.
* Helpers: `wrap_0_2π`, `wrap_−π_π`, `wrap_0_π`; `clip(x, −1, +1)` before every `acos`.
* Epsilons: `EPS = 1e−12` rad (angle equality), `EPS_LAT = 1e−8` rad (solver).
* Time anchoring: choose a fixed daily epoch (e.g., **12:00 UTC**) for deterministic products.
* Vectorize over pairs and bodies; avoid Python loops in prod.

---

## 2) Spherical astronomy identities (ACG baseline)

Altitude at hour angle **H** for equatorial coordinates (**α, δ**) and latitude **φ**:

**sin h = sin φ sin δ + cos φ cos δ cos H**.

Horizon crossings (h = 0) occur at hour‑angle magnitude

**cos H₀(φ, δ) = − tan φ tan δ**, with **H₀ ∈ \[0, π]**.

Event hour angles **Hₑ** and sign convention **H = LST − α**:

* **R** (rising): Hᴿ = − H₀
* **S** (setting): Hˢ = + H₀
* **MC** (upper culmination): Hᴹᶜ = 0
* **IC** (lower culmination): Hᴵᶜ = π

Local sidereal time at an event for body *i*:

**LSTᵢ = αᵢ + Hₑ,ᵢ**  (wrap to \[0, 2π)).

Meridian altitudes (for visibility tests):

**hᴹᶜ = 90° − |φ − δ|**, **hᴵᶜ = −(90° − |φ + δ|)**.

Domain note: horizon events exist only if **|tan φ tan δ| ≤ 1**.

### 2.1 Event constants and signs (for code clarity)

* Horizon sign **s\_H**: `s_R = −1`, `s_S = +1` so that **H\_horizon = s\_H · H₀**.
* Meridian constants **H\_const**: `H_MC = 0`, `H_IC = π`.
* Define **Δα** for closed‑form branches as:

  * **Δα = α\_meridian − α\_horizon** (ordered), wrapped to (−π, π].

Sanity checks

* If **δ = φ** then **hᴹᶜ = 90°** (zenith), **hᴵᶜ = −90°**.
* Symmetry: δ → −δ with swapped events mirrors φ across the equator.

---

## 3) Simultaneity (paran) equation

Two bodies **A, B** are in paran for events **e\_A, e\_B** at any latitude **φ** satisfying

**α\_A + Hₑ(A, φ) = α\_B + Hₑ(B, φ)**  (mod 2π).

For the common **meridian–horizon** case, prefer the unified recipe of §3.1.1 with the ordered **Δα = α\_meridian − α\_horizon**. For other cases use the general equation below.

Let **Δα\_general = wrap\_−π\_π(α\_B − α\_A)** (A/B in the order they are passed). Solve

**Hₑ(A, φ) − Hₑ(B, φ) = Δα\_general**.

### 3.2 Numeric solution (horizon vs horizon)

Solve for φ:

**s\_A · arccos( − tan φ tan δ\_A ) − s\_B · arccos( − tan φ tan δ\_B ) = Δα\_general**, with **s\_R = −1**, **s\_S = +1**.

Use **Brent** or **bisection** over φ ∈ \[−89.9°, +89.9°]; reject sub‑intervals where either **|tan φ tan δᵢ| > 1** (no R/S at that φ). Optional Newton refinement with derivative

**d/dφ arccos g(φ) = − g′(φ) / √(1 − g(φ)²)**, where **g(φ) = − tan φ tan δ**, **g′(φ) = − sec² φ tan δ**.

Return `None` where either horizon crossing is impossible. Ensure monotonic bracketing by splitting the search domain at singularities **|tan φ tan δ| = 1**.

### 3.3 Visibility filters (optional) (optional)

Modes

* `all`: no filter beyond horizon geometry.
* `both_visible`: both planets above the geometric horizon at the instant.
* `meridian_visible_only`: only the meridian planet must be above horizon.

Checks

* Horizon events are at **h = 0°** by definition (or **h₀** if using apparent horizon). For `both_visible`, compute the companion’s altitude via the identity in §2.
* For **MC/IC**, use **hᴹᶜ** and **hᴵᶜ**. At high |φ|, IC is often below horizon.

**Realism toggles (do not move lines)**

* Constant refraction offset **R₀ ≈ 0.5667°** as a switchable UI feature.
* Sun/Moon semidiameter & horizontal parallax **only** affect visibility flags, not φ.

### 3.4 Degeneracies / non‑solutions

* **Meridian vs meridian**: solutions only when **Δα ∈ {0, ±π}** → trivial or empty; suppress.
* **Circumpolarity**: if **|tan φ tan δ| > 1** for any horizon body, R/S doesn’t exist there. The closed‑form path guarantees feasibility for the designated horizon body only.
* **Polar limits**: as |φ|→90°, guard solvers and clamp rendering.

---

## 4) Sidereal time & timing labels (UX only)

You may annotate each paran latitude with a **local civil time** by longitude **λ**.

1. Compute **GMST** (or **GAST**) at epoch *t* (e.g., SOFA `iauGmst06`/`iauGst06`).
2. Local sidereal time: **LST(λ) = GMST + λ** (east‑positive, wrap to \[0, 2π)).
3. For a given paran line (A, e\_A, B, e\_B, φ), **LST\_paran = α\_A + Hₑ(A, φ)** (equivalently, = α\_B + Hₑ(B, φ)).
4. To get local **UTC** at longitude λ, solve **LST(UTC, λ) = LST\_paran** within the 24 h bracketing *t* (one solution per day per λ). Use a root finder stepping **−12 h … +12 h** around *t*.

This labeling does **not** affect latitude placement.

---

## 5) Algorithm outline (ACG parans)

**Inputs** at epoch *t*

* Planets **P = { (id, α, δ) }** on the true equator/equinox of date.
* Ordered event pairs to evaluate.

**Pair enumeration policy**

* Use **ordered pairs** to avoid double‑counting; e.g., evaluate `(A: horizon, B: meridian)` distinctly from `(B: horizon, A: meridian)` only if you intentionally want both.
* Recommended default set (captures all unique meridian–horizon parans without redundancy):

  * For each unordered planet pair {A, B}:

    * A on horizon (R and S) with B on MC and IC (4 combos)
    * B on horizon (R and S) with A on MC and IC (4 combos)

**Compute**

1. Precompute arrays **sin δ**, **cos δ**, **tan δ** for all planets.
2. For each ordered pair (**A, e\_A**), (**B, e\_B**):

   * If one is **meridian** and the other **horizon**:

     * Set **X = horizon body**, **Y = meridian body**; compute **Δα = wrap\_−π\_π(α\_Y − α\_X)**.
     * **H₀ = wrap\_0\_π(Δα + H\_const(Y))**; **φ = atan2( − cos H₀ cos δ\_X,  sin δ\_X )**.
   * If **both horizon** → numeric (§3.2).
   * If **both meridian** → ignore (degenerate).
   * Apply visibility filters if configured.
   * Append a line with **φ (deg)** and metadata.

**Rendering**

* Render each paran as a **parallel** at constant latitude **φ**. Sample 361 points for λ ∈ \[−180°, +180°], or use an analytic parallel primitive if available.
* Style by pair type and bodies.

---

## 6) Numerical practices & edge cases

* **Wrapping**: single authoritative helpers `wrap_0_2π`, `wrap_−π_π`, `wrap_0_π` implemented with branch‑light `fmod` and corrections.
* **Clamp** all `acos` inputs to **\[−1, +1]** to kill round‑off spikes.
* **atan2 form** for φ: **atan2( − cos H₀ cos δ,  sin δ )** to avoid tan δ blow‑ups.
* **Circumpolar**: explicitly test **|tan φ tan δ| ≤ 1** for horizon bodies; short‑circuit numeric solver outside domains.
* **Polar guard**: keep solvers away from |φ| ≥ 89.999°. Clamp rendered φ to ±89.999°.
* **Equatorial/zenith**: when **δ ≈ φ**, MC altitude → zenith; use formulas, not inference.
* **Time anchoring**: fix a daily epoch (e.g., 12:00 UTC). Planetary RA/Dec drift moves φ by << 0.1° within a day.
* **Performance**: batch by event type, precompute trig, use vectorized kernels. Defer horizon–horizon to a separate pass.

---

## 7) Validation plan

1. **Unit tests**

   * Identities: **Δα = 0**, **Δα = ±π**, and **δ = 0** limit behaviors for the closed‑form path.
   * Randomized fuzzing (≥ 10k pairs): verify **|(α\_A + Hₑ(A)) − (α\_B + Hₑ(B))| < 1e−8 rad** at returned φ.

2. **Cross‑library**

   * Compare against a reference stack (SOFA + your horizon logic, or Swiss Ephemeris apparent places) for a canonical date. Require agreement **≤ 0.05°** in φ when models match.

3. **Regression**

   * Freeze `{α, δ, pair} → φ` per epoch; assert within epsilon in CI.

4. **Sanity plots**

   * Visual: exact **parallels** with no longitudinal curvature. Equatorial mirroring holds for symmetric inputs.

5. **Worked symbolic checks (no ephemeris needed)**

   * **δ\_X = 0**, **Y on MC**, **Δα = 0** ⇒ **H₀ = 0**, **φ → −90°** (limit case), confirming the formula’s behavior at the pole.
   * **δ\_X = φ**, **Y on MC**, any Δα ⇒ **hᴹᶜ = 90°** (zenith), visibility filter behavior only; φ unaffected.

---

## 8) Performance

* Vectorize across pairs; closed‑form is a handful of trig ops per pair.
* Batch meridian–horizon combos into tight loops; isolate horizon–horizon numeric solves.
* Cache planet positions at the epoch; reuse across UI interactions.
* Share longitude grids when emitting sampled polylines.

---

## 9) Differences from Brady fixed‑star parans (for clarity)

* **Bodies**: this spec uses **planets only** (geocentric apparent). Brady parans emphasize **fixed stars** with proper motion to date.
* **Instantaneity**: we enforce **exact simultaneity at an instant** (sidereal‑time equality). Brady literature sometimes treats daily windows/visibility traditions.
* **Mapping**: results are **constant‑latitude parallels**; no star catalogs or space‑motion propagation here.

---

## 10) Local timing bands (optional UX)

After computing **φ**, compute **LST\_paran = α\_A + Hₑ(A, φ)**. At longitude **λ**, solve **GMST(UTC) + λ = LST\_paran** within ±12 h of the epoch to label tooltips (e.g., “\~09:42 local”). This is a display aid only.

---

## 11) Pseudocode (concise)

````python
# Inputs: epoch t (UTC); planets = [{id, alpha, delta}], PAIRS = [(i,e_i,j,e_j)]
# Angles in radians; east-positive longitudes; wrap/clip helpers provided

pre = [(math.sin(b.delta), math.cos(b.delta), math.tan(b.delta)) for b in planets]

lines = []
for (i, e_i, j, e_j) in PAIRS:
    ai, di = planets[i].alpha, planets[i].delta
    aj, dj = planets[j].alpha, planets[j].delta
    si, ci, ti = pre[i]
    sj, cj, tj = pre[j]

    def Hc(e):
        return 0.0 if e == 'MC' else (math.pi if e == 'IC' else None)

    Hi, Hj = Hc(e_i), Hc(e_j)

    if (Hi is not None) ^ (Hj is not None):
        # one meridian, one horizon (closed form)
        if Hj is None:
            # j on horizon, i on meridian
            d_alpha = wrap_mpi_pi(ai - aj)  # Δα = α_meridian − α_horizon
            H0 = wrap_0_pi(d_alpha + Hi)
            phi = math.atan2(-math.cos(H0) * cj, sj)
            mer_delta = di; mer_event = e_i
        else:
            # i on horizon, j on meridian
            d_alpha = wrap_mpi_pi(aj - ai)
            H0 = wrap_0_pi(d_alpha + Hj)
            phi = math.atan2(-math.cos(H0) * ci, si)
            mer_delta = dj; mer_event = e_j

        if visible_mode:
            # horizon planet at h=0 by definition
            if mer_event == 'MC':
                h_mer = math.radians(90) - abs(phi - mer_delta)
            else:  # IC
                h_mer = -(math.radians(90) - abs(phi + mer_delta))
            if require_meridian_above and h_mer <= 0:
                continue

        lines.append({'i': planets[i].id, 'e_i': e_i,
                      'j': planets[j].id, 'e_j': e_j,
                      'lat_deg': math.degrees(phi)})

    elif (Hi is None) and (Hj is None):
        # horizon vs horizon (numeric)
        s_i = -1.0 if e_i == 'R' else 1.0
        s_j = -1.0 if e_j == 'R' else 1.0

        def F(phi):
            g_i = -math.tan(phi) * ti
            g_j = -math.tan(phi) * tj
            if abs(g_i) > 1 or abs(g_j) > 1:
                return None
            ai_ = max(-1.0, min(1.0, g_i))
            aj_ = max(-1.0, min(1.0, g_j))
            # Δα_general = α_B − α_A with A=i, B=j
            d_ag = wrap_mpi_pi(aj - ai)
            return s_i * math.acos(ai_) - s_j * math.acos(aj_) - d_ag

        phi = brent_root(F, math.radians(-89.9), math.radians(89.9), tol=1e-8)
        if phi is not None:
            lines.append({'i': planets[i].id, 'e_i': e_i,
                          'j': planets[j].id, 'e_j': e_j,
                          'lat_deg': math.degrees(phi)})

    else:
        # both meridian: degenerate; ignore
        continue
```python
# Inputs: epoch t (UTC); planets = [{id, alpha, delta}], PAIRS = [(i,e_i,j,e_j)]
# Angles in radians; east-positive longitudes; wrap/clip helpers provided

pre = [(math.sin(b.delta), math.cos(b.delta), math.tan(b.delta)) for b in planets]

lines = []
for (i, e_i, j, e_j) in PAIRS:
    ai, di = planets[i].alpha, planets[i].delta
    aj, dj = planets[j].alpha, planets[j].delta
    si, ci, ti = pre[i]
    sj, cj, tj = pre[j]
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
            mer_delta = di; mer_event = e_i
        else:
            # i on horizon
            H_req = (-d_alpha - Hj) if e_i == 'R' else (Hj + d_alpha)
            H0 = wrap_0_pi(H_req)
            phi = math.atan2(-math.cos(H0) * ci, si)
            mer_delta = dj; mer_event = e_j

        if visible_mode:
            # horizon planet is at h=0 by definition
            if mer_event == 'MC':
                h_mer = math.radians(90) - abs(phi - mer_delta)
            else:  # IC
                h_mer = -(math.radians(90) - abs(phi + mer_delta))
            if require_meridian_above and h_mer <= 0:
                continue

        lines.append({'i': planets[i].id, 'e_i': e_i,
                      'j': planets[j].id, 'e_j': e_j,
                      'lat_deg': math.degrees(phi)})

    elif (Hi is None) and (Hj is None):
        # horizon vs horizon (numeric)
        s_i = -1.0 if e_i == 'R' else 1.0
        s_j = -1.0 if e_j == 'R' else 1.0

        def F(phi):
            g_i = -math.tan(phi) * ti
            g_j = -math.tan(phi) * tj
            if abs(g_i) > 1 or abs(g_j) > 1:
                return None  # outside domain
            ai = max(-1.0, min(1.0, g_i))
            aj = max(-1.0, min(1.0, g_j))
            return s_i * math.acos(ai) - s_j * math.acos(aj) - d_alpha

        phi = brent_root(F, math.radians(-89.9), math.radians(89.9), tol=1e-8)
        if phi is not None:
            lines.append({'i': planets[i].id, 'e_i': e_i,
                          'j': planets[j].id, 'e_j': e_j,
                          'lat_deg': math.degrees(phi)})

    else:
        # both meridian: degenerate; ignore
        continue
````

---

## 12) Agentic data schema

**Request**

```json
{
  "epoch_utc": "2025-09-04T12:00:00Z",
  "planets": [
    {"id": "Sun",   "alpha": 2.123, "delta": 0.182},
    {"id": "Saturn", "alpha": 5.678, "delta": -0.321}
  ],
  "pairs": [
    {"a": "Sun", "event_a": "MC", "b": "Saturn", "event_b": "R"}
  ],
  "visibility": "all",
  "models": {"horizon": "geometric", "refraction": null, "topocentric": false},
  "policy": {"pair_enumeration": "both-directions", "time_anchor": "12:00Z"}
}
```

**Response**

```json
{
  "paran_lines": [
    {
      "a": "Sun", "event_a": "MC", "b": "Saturn", "event_b": "R",
      "latitude_deg": -23.456,
      "meta": {
        "epoch_utc": "2025-09-04T12:00:00Z",
        "horizon": "geometric",
        "visibility": "all",
        "line_id": "Sun-MC__Saturn-R__2025-09-04T12:00Z"
      }
    }
  ]
}
```

**Response**

```json
{
  "paran_lines": [
    {
      "a": "Sun", "event_a": "MC", "b": "Saturn", "event_b": "R",
      "latitude_deg": -23.456,
      "meta": {"epoch_utc": "2025-09-04T12:00:00Z", "horizon": "geometric", "visibility": "all"}
    }
  ]
}
```

---

## 13) Helper API (recommended signatures)

```python
wrap_0_2pi(x: float) -> float
wrap_mpi_pi(x: float) -> float
wrap_0_pi(x: float) -> float
clip(x: float, lo: float=-1.0, hi: float=1.0) -> float
altitude(phi: float, delta: float, H: float) -> float  # returns h in radians
GMST(t_utc: datetime) -> float
LST(gmst: float, lon_east_rad: float) -> float
```

---

## 14) Acceptance criteria

* Deterministic φ across platforms for the same epoch and model flags.
* Units, wraps, and horizon convention documented; tests pass.
* Fuzz and regression tests meet stated error budgets.
* Visual inspection: constant‑latitude lines; symmetry checks pass.
* Metadata records models so QA can reproduce.

---

## 15) Notes for ACG parity

* Use **apparent** geocentric positions of date (Sun: center; Moon: center; planets: apparent).
* Default geometric horizon for **placement**; refraction/semidiameter only for **visibility** flags to match classic ACG conventions.
* Optional product layer: overlay classic single‑planet ACG **angularity lines** (ASC/DSC/MC/IC) if you want to show where the constituent angles lie; **not** required for paran computation.

End of spec.
