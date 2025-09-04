
---
**NOTE: This document and all PRPs in this folder pertain to Version 2 ACG, which will be implemented as a modular engine, cleanly connected through the main API.**
---
# Astrocartography Engineering Guide (Python + Swiss Ephemeris)

Version: 1.0 • Focus: methods, math, and production implementation
Scope: All planets, luminaries, lunar nodes, Black Moon Lilith, popular Hermetic Lots, major asteroids, fixed stars as fixed points, AC/DC/MC/IC lines, AC/MC aspect lines (square, trine, sextile), parans

---

## 0) Assumptions and Inputs

* You already compute high‑precision geocentric or topocentric positions with Swiss Ephemeris (SE):

  * For each body `b` at UTC time `t`: ecliptic longitude `λ_b` (deg), ecliptic latitude `β_b` (deg), apparent right ascension `α_b` (deg), apparent declination `δ_b` (deg).
  * True obliquity `ε` (deg).
  * Optional: topocentric correction for a nominal observer. For mapping angular conditions, topocentric corrections are not needed, since you solve for the observer’s location. Keep everything apparent and consistent.
* Timescale: UTC.
* Earth fixed model: WGS‑84, spherical Earth is sufficient for drawing lines.
* East longitudes positive, north latitudes positive.
* Sidereal time convention: IAU 2006/2000A or equivalent precision.

---

## 1) Mathematical Foundations

### 1.1 Sidereal Time

Let `JD_UT1` be the UT1 Julian Date at time `t`. If you only have UTC, UT1 ≈ UTC is generally adequate for mapping. Compute Greenwich Mean Sidereal Time (GMST):

```
T = (JD_UT1 − 2451545.0) / 36525
GMST_deg = 280.46061837
         + 360.98564736629 * (JD_UT1 − 2451545.0)
         + 0.000387933 * T^2
         − (T^3) / 38710000
```

Normalize to \[0, 360). Local Sidereal Time at longitude λ (deg, east-positive):

```
LST_deg(λ) = GMST_deg + λ
```

Normalize to \[0, 360).

Hour angle of body `b` at longitude λ:

```
H_b(λ) = LST_deg(λ) − α_b
```

Normalize to (−180, 180], in degrees.

---

### 1.2 Angular Conditions

All “on-angle” conditions are statements about hour angle `H` and altitude `h`.

Spherical trig relation:

```
sin h = sin φ sin δ_b + cos φ cos δ_b cos H
```

With latitude `φ` and declination `δ_b` (deg). Azimuth can be used for disambiguation, but not strictly required when you constrain `H`.

#### MC (culminating) and IC (anti-culminating)

* MC: body on local meridian above horizon. Hour angle `H_b = 0`.
* IC: body on local anti-meridian. Hour angle `H_b = 180°` or `−180°`.

Because `LST` does not depend on latitude, MC and IC loci at a fixed time are **meridians**:

```
MC meridian longitude:  λ_MC(b) = wrap(α_b − GMST_deg)
IC meridian longitude:  λ_IC(b) = wrap(α_b + 180° − GMST_deg)
```

Each is a north–south line spanning φ ∈ \[−89.9°, +89.9°], clipped where the body never rises if desired for cosmetics. Refraction does not change the meridian condition.

#### Ascendant (AC) and Descendant (DC)

Altitude `h = 0` yields:

```
0 = sin φ sin δ_b + cos φ cos δ_b cos H
⇒ tan φ = −(cos δ_b cos H) / sin δ_b
⇒ φ = atan2( −cos δ_b cos H, sin δ_b )
```

At a fixed time, let `H_b(λ) = LST(λ) − α_b`. Then the locus of points where the body is on the horizon is the set of pairs:

```
λ ∈ [−180°, +180°]  →  φ(λ) = atan2( −cos δ_b cos H_b(λ), sin δ_b )
```

This relation describes both rising and setting. Split into AC vs DC by the sign of `H_b`:

* AC: `H_b(λ) ∈ (−180°, 0)` (body east of meridian).
* DC: `H_b(λ) ∈ (0, +180°)` (body west of meridian).

Clip where `|tan φ|` explodes near `sin δ_b ≈ 0`. Numerically, compute φ with robust `atan2`.

**Circumpolar constraints:** If `|φ| + |δ_b| > 90°`, rising or setting may not occur. You will see gaps where `cos H` would need to be outside \[−1, +1]. Implement a mask:

```
has_horizon_crossing = |tan φ * tan δ_b| ≤ 1        (classic form)
```

Since we solve for φ from H rather than for H from φ, you enforce AC/DC existence by checking that computed φ lives in \[−90°, 90°] and that the implied altitude crosses zero with the correct `H` sign.

---

### 1.3 Ascendant longitude and AC aspect lines

For AC aspect lines you need the **ecliptic longitude of the local Ascendant** at each (φ, λ). For obliquity `ε`:

Let `Θ = LST_rad` and use the standard formulae for the ecliptic longitudes of the horizon intersections. One robust form:

```
tan Λ_ASC =  (sin Θ cos ε + tan φ sin ε) / cos Θ
Λ_ASC = atan2( sin Θ cos ε + tan φ sin ε, cos Θ )
```

Return Λ\_ASC in degrees \[0, 360).

**Aspect to AC** for a body with ecliptic longitude `λ_b`:

```
Δ = wrap( λ_b − Λ_ASC )
Target aspects A ∈ {60°, 90°, 120°, 300°(=−60°), 270°(=−90°), 240°(=−120°)}
Condition:  min_angle(Δ, A) ≤ orb_tolerance
```

In practice you do not use an orb for the line itself. You draw the zero-width curve where Δ equals the exact aspect, then later use an orb for hit testing. Numerically, solve for `(φ, λ)` such that `wrap(λ_b − Λ_ASC(φ, λ)) = A`. Implementation strategy in Section 2.

---

### 1.4 MC aspect lines

Aspect to MC is simple in sidereal time:

“Body is A degrees from MC” means the local meridian is at `α_b + A`:

```
LST = α_b + A    ⇒    λ = α_b + A − GMST_deg
```

These are again **meridians**. Draw for A ∈ {60°, 90°, 120°, 240°, 270°, 300°}.

---

### 1.5 Parans (Jim Lewis convention)

A paran is a latitude at which two bodies (or a body with the ecliptic) are simultaneously on specified angles at the same local sidereal time. Common angle pairs:

* Rise with Culminate
* Rise with Set
* Culminate with Anti‑culminate
* Set with Culminate
* And the four-way set for both bodies across {Rise, Set, Culminate, Anti‑culminate}

Let body 1 and 2 have RAs `α1, α2`, declinations `δ1, δ2`.

Define the event hour angles at latitude φ:

* Rise:  `H_rise(δ, φ)  = −arccos(−tan φ tan δ)`
* Set:   `H_set(δ, φ)   = +arccos(−tan φ tan δ)`
* Culm:  `H_culm        = 0`
* Anti:  `H_anti        = ±180°` (choose +180°)

A paran exists at latitude φ where the **local sidereal times** of the two events match:

```
LST1(φ) = α1 + H_event1(δ1, φ)
LST2(φ) = α2 + H_event2(δ2, φ)
Paran condition:  wrap( LST1(φ) − LST2(φ) ) = 0
```

Solve the 1D root for φ. This yields one or more φ where the pair is in paran. Parans are plotted as **latitude bands**. To display on a world map, convert the matching LST to longitudes:

```
λ(φ) = wrap( LST1(φ) − GMST_deg )
```

You will typically render paran lines as nearly horizontal curves at those latitudes, possibly with periodic discontinuities when converted to longitude. For fixed stars, treat `α*, δ*` as constants for the epoch of date with precession and proper motion as applicable.

Numerical details in Section 2.6.

---

### 1.6 Fixed stars

Fixed stars are treated as bodies with `α*, δ*` at time `t` (precessed to date; include proper motion if desired). Then all the above line logic applies. For display, also add an **orb radius on the map** for point hits; the star itself is a point, but angular conditions generate lines exactly as for a planet.

---

### 1.7 Lots (Hermetic lots)

A Lot is an ecliptic longitude computed from other longitudes. Example, Lot of Fortune (day formula):

```
Λ_ Fortune = Λ_Moon + Λ_ASC − Λ_Sun   (normalized to [0,360))
```

Other lots similar. Once you have `Λ_Lot`, compute:

* MC lines using its RA/Dec derived from `Λ_Lot` with β = 0 on the ecliptic.
* AC/DC via the generic horizon crossing formula by first converting the ecliptic point `(Λ_Lot, β=0)` to equatorial `(α, δ)` using obliquity `ε`:

  ```
  α = atan2( sin Λ_Lot cos ε, cos Λ_Lot )
  δ = arcsin( sin Λ_Lot sin ε )
  ```

Then treat as a “body”.

---

## 2) Python Implementation

### 2.1 Dependencies

* `numpy` for vector math
* `pyproj` for projections if you pre-project server-side (optional)
* `swisseph` (pyswisseph) for positions
* `shapely` for geometry ops and line clipping (optional but useful)
* `orjson` or `ujson` for GeoJSON serialization
* `numba` optional for JIT speedups

```bash
pip install numpy swisseph pyproj shapely orjson
```

### 2.2 Utilities

```python
import numpy as np

DEG = np.pi / 180.0

def wrap_deg(x):
    # Wrap to [0, 360)
    y = np.mod(x, 360.0)
    y[y < 0] += 360.0
    return y

def wrap_pm180(x):
    # Wrap to (-180, 180]
    y = (x + 180.0) % 360.0 - 180.0
    # ensure +180 not returned as -180
    y[y <= -180.0] += 360.0
    return y

def gmst_deg_from_jd_ut1(jd):
    T = (jd - 2451545.0) / 36525.0
    gmst = (280.46061837
            + 360.98564736629 * (jd - 2451545.0)
            + 0.000387933 * T*T
            - (T**3) / 38710000.0)
    return wrap_deg(gmst)

def lst_deg(gmst_deg, lon_deg):
    return wrap_deg(gmst_deg + lon_deg)
```

### 2.3 MC and IC Lines

```python
def mc_ic_longitudes(alpha_deg, gmst_deg):
    lam_mc = wrap_deg(alpha_deg - gmst_deg)
    lam_ic = wrap_deg(alpha_deg + 180.0 - gmst_deg)
    return lam_mc, lam_ic

def build_ns_meridian(lon_deg, n_samples=721):
    # Create a N-S line of latitudes
    lats = np.linspace(-89.9, 89.9, n_samples)
    lons = np.full_like(lats, ((lon_deg + 540) % 360) - 180)  # convert to [-180,180)
    return np.column_stack([lons, lats])
```

Usage per body `b`: compute `lam_mc, lam_ic`, then generate the polyline with `build_ns_meridian`.

### 2.4 AC and DC Lines

We trace `(λ, φ(λ))` by sweeping longitudes:

```python
def ac_dc_line(alpha_deg, delta_deg, gmst_deg, kind='AC', n_samples=1441):
    """
    kind: 'AC' or 'DC'
    Returns Nx2 array of lon,lat where the body is on the horizon.
    """
    lons = np.linspace(-180.0, 180.0, n_samples)  # plot domain
    lsts = lst_deg(gmst_deg, lons)                # deg
    H = wrap_pm180(lsts - alpha_deg)              # deg

    # For AC, require H in (-180, 0). For DC, (0, +180)
    if kind == 'AC':
        mask = (H < 0)
    else:
        mask = (H > 0)

    # φ = atan2( -cos δ cos H, sin δ )
    cd = np.cos(delta_deg * DEG)
    sd = np.sin(delta_deg * DEG)
    cH = np.cos(H * DEG)

    num = -cd * cH
    den = sd
    phis = np.rad2deg(np.arctan2(num, den))

    # Apply mask, also guard impossible regions where |phis|>90 slightly due to rounding
    keep = mask & (np.isfinite(phis)) & (np.abs(phis) <= 90.0)
    lons_keep = lons[keep]
    phis_keep = phis[keep]

    # Optionally split at large jumps to create MultiLineString segments later
    return np.column_stack([lons_keep, phis_keep])
```

**Gaps and segmentation:** After computing the polyline, split where `|Δφ| > 5°` between neighbors or where `keep` introduces holes. Store as MultiLineString.

### 2.5 AC aspect lines

We need `Λ_ASC(φ, λ)` and solve `wrap(λ_b − Λ_ASC) = A`. Use a longitude sweep with a root in latitude via 1D solve or directly compute φ from the condition. A robust discrete approach:

```python
def ascendant_longitude(phi_deg, lst_deg_val, eps_deg):
    # Λ_ASC = atan2( sin Θ cos ε + tan φ sin ε, cos Θ )
    Θ = lst_deg_val * DEG
    eps = eps_deg * DEG
    tphi = np.tan(phi_deg * DEG)
    num = np.sin(Θ) * np.cos(eps) + tphi * np.sin(eps)
    den = np.cos(Θ)
    Λ = np.rad2deg(np.arctan2(num, den))
    return wrap_deg(Λ)

def ac_aspect_lines(lambda_body_deg, gmst_deg, eps_deg, aspect_deg, n_lon=721, n_lat=721):
    """
    Brute-force sampling grid with contour extraction logic:
    Find curve where wrap(lambda_body - Λ_ASC(phi, λ)) = aspect_deg.
    """
    lons = np.linspace(-180.0, 180.0, n_lon)
    lats = np.linspace(-89.5, 89.5, n_lat)

    LON, LAT = np.meshgrid(lons, lats)
    LST = lst_deg(gmst_deg, LON)
    Λasc = ascendant_longitude(LAT, LST, eps_deg)
    Δ = wrap_deg(lambda_body_deg - Λasc)

    # We want Δ == aspect_deg. Find near-zero of wrap_pm180(Δ − aspect_deg)
    target = wrap_pm180(Δ - aspect_deg)

    # Extract an approximate contour (zero level set). For production, use skimage.measure.find_contours on a regular grid.
    # Here, return sampled points close to zero within tolerance.
    tol = 0.25  # degrees in the lattice; visualization quality depends on resolution
    mask = np.abs(target) <= tol
    pts = np.column_stack([LON[mask], LAT[mask]])
    # Optionally post-process to order points and split segments.
    return pts
```

You can refine by:

* Using marching squares to extract smooth contours.
* Increasing resolution locally with quadtree refinement near the curve.
* Caching Λ\_ASC over a reusable grid for many bodies.

### 2.6 Parans

Root solve in latitude for each pair of events.

```python
def H_rise(phi_deg, delta_deg):
    # −arccos(−tan φ tan δ)
    tphi = np.tan(phi_deg * DEG)
    td = np.tan(delta_deg * DEG)
    x = -tphi * td
    x = np.clip(x, -1.0, 1.0)
    return -np.rad2deg(np.arccos(x))

def H_set(phi_deg, delta_deg):
    tphi = np.tan(phi_deg * DEG)
    td = np.tan(delta_deg * DEG)
    x = -tphi * td
    x = np.clip(x, -1.0, 1.0)
    return +np.rad2deg(np.arccos(x))

def H_event(event, phi_deg, delta_deg):
    if event == 'RISE': return H_rise(phi_deg, delta_deg)
    if event == 'SET':  return H_set(phi_deg, delta_deg)
    if event == 'CULM': return 0.0
    if event == 'ANTI': return 180.0
    raise ValueError("event")

def find_paran_latitudes(alpha1, delta1, alpha2, delta2,
                         event1, event2,
                         lat_min=-89.0, lat_max=89.0, lat_step=0.1, tol=1e-3):
    """
    Solve wrap(LST1 - LST2) = 0, where LSTi = αi + H_eventi(δi, φ).
    Returns list of (phi_deg, lst_deg_at_paran)
    """
    phis = np.arange(lat_min, lat_max + lat_step, lat_step)
    vals = []
    for φ in phis:
        H1 = H_event(event1, φ, delta1)
        H2 = H_event(event2, φ, delta2)
        F = wrap_pm180((alpha1 + H1) - (alpha2 + H2))
        vals.append(F)
    vals = np.array(vals)

    # Find sign changes indicating roots
    roots = []
    for i in range(len(phis) - 1):
        if vals[i] == 0 or vals[i+1] == 0 or (vals[i] * vals[i+1] < 0):
            # Bisection
            a, b = phis[i], phis[i+1]
            fa, fb = vals[i], vals[i+1]
            for _ in range(40):
                m = 0.5 * (a + b)
                fm = wrap_pm180((alpha1 + H_event(event1, m, delta1)) -
                                (alpha2 + H_event(event2, m, delta2)))
                if np.sign(fm) == np.sign(fa):
                    a, fa = m, fm
                else:
                    b, fb = m, fm
                if abs(b - a) < tol:
                    break
            phi_star = 0.5 * (a + b)
            LST = wrap_deg(alpha1 + H_event(event1, phi_star, delta1))
            roots.append((phi_star, LST))
    return roots

def paran_longitude(lst_deg_val, gmst_deg):
    return wrap_deg(lst_deg_val - gmst_deg)
```

For each paran solution `(φ*, LST*)`, get the longitude `λ* = LST* − GMST` and draw a short latitudinal segment around `φ*` across longitudes or display as a band with given thickness.

---

### 2.7 Ecliptic–Equatorial conversions (for Lots and AC aspect math)

```python
def ecl_to_eq(lambda_deg, beta_deg, eps_deg):
    lam = lambda_deg * DEG
    bet = beta_deg * DEG
    eps = eps_deg * DEG
    sin_dec = np.sin(bet) * np.cos(eps) + np.cos(bet) * np.sin(eps) * np.sin(lam)
    dec = np.arcsin(sin_dec)
    y = np.sin(lam) * np.cos(eps) - np.tan(bet) * np.sin(eps)
    x = np.cos(lam)
    ra = np.arctan2(y, x)
    return wrap_deg(np.rad2deg(ra)), np.rad2deg(dec)
```

---

### 2.8 Body catalog and metadata

Create a registry so the pipeline is data-driven.

```python
BODY_REGISTRY = [
    # name, kind, source, options
    {"id":"Sun",    "kind":"planet", "flag":"SE_SUN"},
    {"id":"Moon",   "kind":"planet", "flag":"SE_MOON"},
    {"id":"Mercury","kind":"planet", "flag":"SE_MERCURY"},
    {"id":"Venus",  "kind":"planet", "flag":"SE_VENUS"},
    {"id":"Earth",  "kind":"point",  "note":"for lots if needed"},
    {"id":"Mars",   "kind":"planet", "flag":"SE_MARS"},
    {"id":"Jupiter","kind":"planet", "flag":"SE_JUPITER"},
    {"id":"Saturn", "kind":"planet", "flag":"SE_SATURN"},
    {"id":"Uranus", "kind":"planet", "flag":"SE_URANUS"},
    {"id":"Neptune","kind":"planet", "flag":"SE_NEPTUNE"},
    {"id":"Pluto",  "kind":"planet", "flag":"SE_PLUTO"},
    {"id":"TrueNode","kind":"point", "flag":"SE_TRUE_NODE"},
    {"id":"MeanNode","kind":"point", "flag":"SE_MEAN_NODE"},
    {"id":"LilithMean","kind":"point","flag":"SE_MEAN_APOG"},
    {"id":"LilithOsc","kind":"point","flag":"SE_OSCU_APOG"},
    {"id":"Chiron", "kind":"asteroid","flag":"SE_CHIRON"},
    {"id":"Ceres",  "kind":"asteroid","flag":"SE_CERES"},
    {"id":"Pallas", "kind":"asteroid","flag":"SE_PALLAS"},
    {"id":"Juno",   "kind":"asteroid","flag":"SE_JUNO"},
    {"id":"Vesta",  "kind":"asteroid","flag":"SE_VESTA"},
    {"id":"Eris",   "kind":"dwarf","flag":"SE_ERIS"},
    # Fixed stars handled separately by name via swe.fixstar
]

LOTS = [
    {"id":"Fortune", "formula_day": "Moon + ASC − Sun", "formula_night":"Sun + ASC − Moon"},
    {"id":"Spirit",  "formula_day": "Sun + ASC − Moon", "formula_night":"Moon + ASC − Sun"},
    {"id":"Eros",    "formula":     "Venus + ASC − LotOfSpirit"},  # example
    {"id":"Necessity","formula":    "Mercury + ASC − LotOfFortune"},
]
```

Metadata schema (stored alongside each feature geometry):

```json
{
  "id": "Sun",
  "type": "body",
  "kind": "planet",
  "epoch": "UTC 2025-08-12T00:00:00Z",
  "coords": {
    "ra": 123.456,
    "dec": -12.345,
    "lambda": 130.000,
    "beta": 0.000
  },
  "line": {
    "angle": "MC",            // AC, DC, MC, IC, AC_SQUARE, AC_TRINE, MC_SEXTILE, etc.
    "aspect": 90,             // null for pure angles
    "method": "apparent, true obliquity, topocentric=no"
  }
}
```

---

## 3) Building GeoJSON for Leaflet or Cesium

### 3.1 Feature model

* **Feature types:**

  * MC, IC lines: `LineString` meridians
  * AC, DC lines: `MultiLineString` with gaps segmented
  * AC aspect lines: `MultiLineString` extracted from contours
  * MC aspect lines: `LineString` meridians
  * Parans: `MultiLineString` or `Polygon` narrow band
  * Fixed star markers: `Point` for the star itself, plus lines same as other bodies if desired
* **Collections:** Group by body and by line type.

### 3.2 Precision and encoding

* Use 6 decimals in lon/lat to stay at sub‑meter precision in WGS‑84.
* Avoid unnecessary densification. For smooth AC/DC curves, 720 to 1440 samples across longitude is enough. Split segments across discontinuities.
* For aspect contours, post-process with Douglas–Peucker on geographic coordinates with a tolerance of 0.05° to 0.1° to reduce vertex count without visible artifacts.

### 3.3 Example GeoJSON assembly

```python
import orjson

def to_feature_line(coords, props):
    # coords: Nx2 array of [lon, lat] in degrees
    # props: dict
    return {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coords.tolist()
        },
        "properties": props
    }

def to_feature_multiline(segments, props):
    return {
        "type": "Feature",
        "geometry": {
            "type": "MultiLineString",
            "coordinates": [seg.tolist() for seg in segments]
        },
        "properties": props
    }

def save_geojson(path, features):
    fc = {"type": "FeatureCollection", "features": features}
    with open(path, "wb") as f:
        f.write(orjson.dumps(fc, option=orjson.OPT_INDENT_2))
```

### 3.4 Segmentation strategy

For AC/DC and AC-aspects:

* Sort by longitude.
* Start a new segment when:

  * `|Δlon| > 1.0°` between consecutive samples
  * `|Δlat| > 5.0°`
  * Crossing ±180° meridian
    This yields stable MultiLine rendering in Leaflet and Cesium.

### 3.5 Leaflet and Cesium rendering notes

* **Leaflet**:

  * Use `L.geoJSON` with `pane` layering for z‑order control.
  * For large datasets, pre-tile with `geojson-vt` or render as vector tiles (MVT). Otherwise, lazy load per body or per angle type.
  * Keep per-feature properties minimal; store verbose metadata in a sidecar index keyed by feature `id`.
  * For hover performance, do hit testing against simplified geometries or use map-level mousemove throttle.

* **Cesium**:

  * Convert to `PolylineGraphics` or CZML for streaming.
  * For best performance, pre-simplify and group polylines by material.
  * If using 3D globe, do not pre-project. Supply lon/lat directly.

### 3.6 Caching

* Cache body ephemerides at a time step grid. Interpolate line longitudes between steps for animated or time-scrubbed views.
* Cache Λ\_ASC and derived AC aspect contours on a latitude–longitude grid per `GMST` value. If the user scrubs time, recompute GMST and reuse grids with shifted phases when feasible.
* Memoize paran solutions per pair `(b1, b2, event1, event2)` across time slices. Latitude solutions drift slowly.

---

## 4) Accuracy Benchmarks and Options

* Use apparent RA/Dec consistent with Astro.com and Solar Fire conventions. Enable nutation and aberration in Swiss Ephemeris flags.
* Acceptable visual tolerance on lines: within \~0.2° against reference plots.
* Include atmospheric refraction only for alt=0 events if you want horizon crossings to shift by \~34 arcminutes. Industry norm often ignores refraction for line locus.
* For fixed stars, include precession to date and proper motion for bright stars to match professional software.

---

## 5) Putting It Together: Pipeline Outline

1. Compute `JD_UT1`, `GMST_deg`, `ε`.
2. For each body or lot:

   * Get `λ_b, β_b, α_b, δ_b`.
   * **MC/IC**:

     * Compute `λ_MC, λ_IC`.
     * Build meridian polylines.
   * **AC/DC**:

     * Generate curve via Section 2.4.
     * Segment and simplify.
   * **MC aspects**:

     * For A in {60, 90, 120, 240, 270, 300}: meridian at `λ = α_b + A − GMST`.
   * **AC aspects**:

     * For A in {60, 90, 120, 240, 270, 300}: extract contour from `λ_b − Λ_ASC(φ, λ) = A`.
   * Attach metadata.
3. **Parans**:

   * For selected pairs `(b1, b2)` across events, solve φ roots from Section 2.6.
   * Convert each `(φ*, LST*)` to longitudes, draw thin bands or latitude polylines.
4. Emit GeoJSON feature collections per body and per line type.

---

## 6) Agent‑Readable Tasks and Contracts

Define precise tasks your agent can execute with deterministic inputs and outputs.

### 6.1 Compute angle lines for a body

**Input**

```json
{
  "epoch_utc": "2025-08-12T00:00:00Z",
  "jd_ut1": 2460601.5,
  "gmst_deg": 123.456789,
  "obliquity_deg": 23.43657,
  "body": {
    "id": "Venus",
    "ra_deg": 201.2345,
    "dec_deg": -5.6789,
    "lambda_deg": 215.6789,
    "beta_deg": 1.2345
  },
  "aspect_set": [60, 90, 120]
}
```

**Output**

* `FeatureCollection` with features:

  * `MC`, `IC` meridians
  * `AC` MultiLineString
  * `DC` MultiLineString
  * `MC_SEXTILE`, `MC_SQUARE`, `MC_TRINE` meridians
  * `AC_SEXTILE`, `AC_SQUARE`, `AC_TRINE` MultiLineString contours

### 6.2 Compute parans for a pair

**Input**

```json
{
  "epoch_utc": "2025-08-12T00:00:00Z",
  "jd_ut1": 2460601.5,
  "gmst_deg": 123.456789,
  "pair": {
    "body1": {"id":"Sun","ra_deg":...,"dec_deg":...},
    "body2": {"id":"Regulus","ra_deg":...,"dec_deg":...}
  },
  "events": [["RISE","CULM"], ["SET","CULM"], ["RISE","SET"], ["CULM","ANTI"]],
  "lat_grid": {"min": -88.0, "max": 88.0, "step": 0.05}
}
```

**Output**

* `FeatureCollection` with one feature per paran event, encoded as `MultiLineString` latitude bands with metadata describing `(event1, event2)`.

---

## 7) Robustness and Edge Cases

* Normalize angles at every step. Always use `wrap_deg` and `wrap_pm180`.
* Handle `δ ≈ ±90°` with care. Bodies near the pole can make AC/DC numerically unstable. Clip latitudes to ±89.9° and filter spikes.
* Crossing the anti‑meridian: split segments when `sign(Δlon)` flips large.
* Circumpolar zones: do not draw AC/DC segments where no horizon crossing exists.
* AC aspect contour extraction can produce speckle in polar regions. Post-filter segments shorter than `~1°` great-circle length.
* For lots, correctly switch Fortune/Spirit day vs night formula.

---

## 8) Performance Tuning

* Vectorize the AC/DC generation across all longitudes using NumPy.
* Precompute `Λ_ASC` on a coarse grid once per time step. For each body and each aspect, run marching squares to extract the isocontours from a cached scalar field. Store as a compressed grid keyed by GMST within ±0.5 seconds.
* Use Douglas–Peucker simplification in geographic space with a tolerance tuned per zoom level. Store multiple LODs.
* If serving many bodies, compile the math with `numba` or port hotspots to Cython.

---

## 9) Validation Playbook

* Cross-check MC/IC meridian longitudes against `LST = α` and `α + 180`. Spot-check several UTC times. Expect exact matches to within 0.01°.
* For AC/DC, pick a handful of longitudes, compute the implied latitude, then forward-compute `h` with the spherical formula to ensure `|h| < 0.01°`.
* Compare final line positions with Astro.com or Solar Fire for multiple dates and bodies. Expect agreement within \~0.2° visually.

---

## 10) End‑to‑End Example (sketch)

```python
def build_body_lines(body, jd_ut1, gmst_deg, eps_deg):
    feats = []

    # MC / IC
    lam_mc, lam_ic = mc_ic_longitudes(body['ra_deg'], gmst_deg)
    feats.append(to_feature_line(build_ns_meridian(lam_mc), {
        "id": body["id"], "angle":"MC"}))
    feats.append(to_feature_line(build_ns_meridian(lam_ic), {
        "id": body["id"], "angle":"IC"}))

    # AC / DC
    ac = ac_dc_line(body['ra_deg'], body['dec_deg'], gmst_deg, 'AC')
    dc = ac_dc_line(body['ra_deg'], body['dec_deg'], gmst_deg, 'DC')
    # segment_ac = segmentize(ac)  # implement splits
    # segment_dc = segmentize(dc)
    feats.append(to_feature_line(ac, {"id":body["id"], "angle":"AC"}))
    feats.append(to_feature_line(dc, {"id":body["id"], "angle":"DC"}))

    # MC Aspects
    for A in (60, 90, 120, 240, 270, 300):
        lam = wrap_deg(body['ra_deg'] + A - gmst_deg)
        feats.append(to_feature_line(build_ns_meridian(lam), {
            "id":body["id"], "angle":"MC_ASPECT", "aspect":A}))

    # AC Aspects
    for A in (60, 90, 120, 240, 270, 300):
        pts = ac_aspect_lines(body['lambda_deg'], gmst_deg, eps_deg, A)
        feats.append(to_feature_line(pts, {
            "id": body["id"], "angle":"AC_ASPECT", "aspect":A}))

    return feats
```

---

## 11) Comprehensive Feature List

**Bodies**

* Luminaries: Sun, Moon
* Planets: Mercury to Pluto
* Dwarf/outer objects: Chiron, Eris (extendable)
* Asteroids: Ceres, Pallas, Juno, Vesta
* Lunar Nodes: True Node, Mean Node
* Black Moon Lilith: Mean and Osculating
* Fixed Stars: catalog via `swe.fixstar` (by name), precession to date
* Lots: Fortune, Spirit, Eros, Necessity, plus extensible formulas

**Line Types**

* Primary angles: AC, DC, MC, IC
* Aspect to AC: sextile, square, trine
* Aspect to MC: sextile, square, trine
* Parans: combinations among {RISE, SET, CULM, ANTI} across body pairs
* Optional: anti‑aspect lines for completion, already included via 240, 270, 300

**Metadata**

* Computation flags: apparent vs mean, nutation, aberration, refraction on/off
* Time tags: UTC, JD, GMST, UT1–UTC if used
* Provenance: SE version and flags
* Visual encoding hints: color family per body, style per line type
* Hit‑test thresholds: angular orb for tooltips, separate from drawing

---

## 12) Interaction Hooks (for later integration)

* On hover or click:

  * Resolve nearest line within tolerance to retrieve `(body, angle, aspect, epoch)`.
  * Compute local details on the fly: local azimuth, altitude, exact angular separation to target angle or aspect.
* For time scrubbers:

  * Update `GMST` and only recompute MC/IC meridians and translate cached AC aspects if you maintain a Λ\_ASC grid keyed by GMST.
* For fixed stars:

  * Provide a per‑star orb in degrees for map interaction separate from line thickness.

---

## 13) Production Checklist

* Deterministic math with complete angle normalization
* Unit tests:

  * MC/IC exact identities
  * AC/DC forward altitude check
  * AC aspect contour residuals
  * Paran equality of LST
* LOD tiling strategy in place
* Cached grids for Λ\_ASC and marching squares
* Benchmarks against references for 10 random epochs and 10 bodies


Reference:

*download, scan and use as detailed reference for our implementation:

Astrocartography-Specific
Astrolog – Full-featured open-source astrology software with built-in astrocartography (MC/AC/DC/IC lines, aspects, parans).
GitHub: https://github.com/astrolog/astrolog
Homepage: https://www.astrolog.org/astrolog.htm

Astrology Libraries (No Astrocartography, but useful for ephemeris/aspect logic)
Kerykeion – Python astrology library using Swiss Ephemeris; good for data structuring and chart logic.
GitHub: https://github.com/g-battaglia/kerykeion

Immanuel-Python – Modern astrology computations, aspects, progressions, JSON output.
GitHub: https://github.com/theriftlab/immanuel-python

Flatlib – Python library for traditional astrology calculations via Swiss Ephemeris.
GitHub: https://github.com/flatangle/flatlib

Mapping / Line Rendering References (Non-Astrology)
Leaflet.Geodesic – Plugin for rendering accurate great-circle lines on Leaflet maps.
GitHub: https://github.com/henrythasler/Leaflet.Geodesic

Leaflet GeoJSON Examples – Official Leaflet examples for rendering line features (e.g., contours, isolines) from GeoJSON.
Docs: https://leafletjs.com/examples/geojson/

GIS StackExchange – Great Circle Lines – Community solutions for plotting great-circle and contour lines in mapping apps.
Thread: https://gis.stackexchange.com/questions/tagged/great-circle


---