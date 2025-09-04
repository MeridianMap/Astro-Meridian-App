# Astrocartography Lines — Technical Implementation Reference

A compact, implementation-first library of line types, math, and edge cases for building, testing, and using astrocartography (A*C*G) and related astromapping features. **Focus: mechanics over interpretation.**

---

## 0) Scope & Conventions

* **Supported frameworks:** Astro*Carto*Graphy (A*C*G), Parans, Local Space (LS), Geodetics, Relocation, C*C*G overlays (transits/progressions), Solar/Lunar Return A*C*G.
* **Angles:** ASC (rising), MC (upper culmination), DSC (setting), IC (lower culmination).
* **Bodies (default):** Sun, Moon, Mercury–Pluto, **Nodes (choose Mean or True; default True)**, Chiron (optional), Vertex/Antivertex (optional). Fixed stars **off by default** (toggleable).
* **Node pairing:** Model **South Node = North Node + 180°** (do not store separately). Consequences (β≈0°): RA\_SN = RA\_NN + 12h; **δ\_SN = −δ\_NN**. If NN lines are drawn, SN behavior is derivable: **NN/MC ↔ SN/IC**, **NN/ASC ↔ SN/DSC**. Prefer rendering **NN only** to avoid duplication.
* **VX/AVX pairing:** **Antivertex = Vertex + 180°**. Derive, don’t duplicate geometry.
* **Sidereal time choice:** If using **apparent RA/Dec** (recommended), use **GAST/LAST** for meridian conditions; if using **mean RA/Dec**, use **GMST/LMST**. Do not mix mean RA with apparent sidereal time.
* **Timescales:** UTC input → UT1 (optional) → TT for ephemerides. Track ΔT.
* **Earth model:** WGS‑84 ellipsoid for mapping; astronomical formulas assume spherical Earth unless otherwise specified. Use **geodetic latitude** for display; spherical formulas may internally use **geocentric latitude** (convert if needed).
* **Projection:** Equirectangular (Plate Carrée) by default; Mercator optional for UI. MC lines are meridians; rise/set lines are curved.

---

## 1) Line Types (A*C*G core)

For each body **B** at a given epoch (birth/return/progressed/transit), compute:

### 1.1 MC/IC (culmination) lines

* **MC (B/MC):** LST(λ) = RA\_B → longitude λ\_MC = (RA\_B − GST)×15° (mod 360°). Plot as a straight N–S line (all latitudes). *GST = GAST or GMST consistent with §0.*
* **IC (B/IC):** LST(λ) = RA\_B + 12h → λ\_IC = λ\_MC − 180° (wrapped). **Note:** MC/IC are a paired set; storing one and deriving the other is permissible.

### 1.2 ASC/DSC (horizon) lines

Alt = 0 condition at each latitude φ gives the **semi‑arc** (H0):

```
sin(h) = sinφ·sinδ + cosφ·cosδ·cosH
h = 0 → cosH0 = −tanφ · tanδ   (|tanφ·tanδ| ≤ 1 for existence)
```

* **Rising (B/ASC):** H = −H0 (east).  LST = RA\_B + H → solve λ.
* **Setting (B/DSC):** H = +H0 (west). LST = RA\_B + H → solve λ.
* Plot as continuous symmetric curves between equator and the body’s co‑latitude (90°−|δ|). No line in circumpolar zones where no rise/set. **Note:** ASC/DSC are a paired set; you may store one curve with a polarity flag.

### 1.3 Optional angle lines

* **Zenith/Nadir paths:** φ = δ (zenith) / φ = −δ (nadir); hour angle H = 0/180° for local meridian. Render as small circles of latitude (advanced/optional).
* **Vertex/Antivertex (VX/AVX):** Horizon–ecliptic intersection points; include as angular lines if using VX. **AVX is derivable from VX (+180°).**

### 1.4 Line ID & naming spec

* **Canonical ID:** `{body}/{angle}` e.g., `sun/MC`, `venus/ASC`, `north_node/ASC`.
* **Opposites:** store polarity `+1` for primary (MC, ASC) and `-1` for derived (IC, DSC). Nodes and VX use NN/VX as primary; SN/AVX implied.

---

## 2) Parans (Simultaneous Angularity)

Curves (usually by latitude) where **two different bodies** are simultaneously on different angles.

**Enumerated types (8):** A(ASC|DSC) with B(MC|IC) and B(ASC|DSC) with A(MC|IC).

Examples:

* **A/ASC with B/MC:**  Alt\_A=0 (east) **and** H\_B=0.
* **A/DSC with B/MC:**  Alt\_A=0 (west) **and** H\_B=0.
* **A/ASC with B/IC:**   Alt\_A=0 (east) **and** H\_B=±180°.

Solve altitude=0 for A at the LST fixed by B’s meridian condition. Iterate φ and compute longitudes.

**Strength model:** Angular lines (ASC/MC/DSC/IC) primary; parans secondary. Use latitude band (±0.5°–1.0°) as paran orb.

---

## 3) Related Mapping Systems

* **Local Space (LS):** Great circles from the birthplace in the azimuth of each body’s **topocentric** direction at birth (and optionally at other epochs). **Exclude Nodes from LS by default** (they are not physical bodies; azimuth is of limited utility).
* **Geodetics:** Wrap the zodiac around Earth longitudes. Simple mapping: geodetic longitude = ecliptic longitude (λ\_ecl) + offset (e.g., 0° Aries ↔ Greenwich). Use for mundane overlays and locality “sign” bands.
* **Relocation charts:** For a target location, compute local angles (ASC/MC etc.) at birth epoch; treat as a standard chart. Mapping provides spatial continuity that relocation alone can’t.
* **C*****C*****G overlays:** Overlay dynamic (transit/progression) angular lines over natal lines. See §10.

---

## 4) Ephemeris & Reference Frames

* **Ephemerides:** Swiss Ephemeris / JPL DE series. Use **apparent** geocentric RA/Dec (precession + nutation + aberration), equinox‑of‑date.
* **Topocentric corrections:** Apply for Moon (parallax), optionally for Sun/planets. Refraction only if modeling apparent horizon (default: off).
* **Time scales:**

  * Input datetime → **UTC**.
  * Compute **ΔT**; TT = UTC + ΔT (+ leap corrections where relevant).
  * **Sidereal time:** Use **GAST/LAST** with apparent RA/Dec; **GMST/LMST** with mean RA/Dec.

---

## 5) Core Formulas (detail)

### 5.1 Ecliptic → Equatorial

```
Given (λ, β) and obliquity ε:
α = atan2( sinλ·cosε − tanβ·sinε, cosλ )
δ = asin( sinβ·cosε + cosβ·sinε·sinλ )
```

Use quadrant‑aware atan2. α in hours if preferred; δ in degrees.

### 5.2 Sidereal time & hour angle

```
LST(λ_geo) = GST(UT) + λ_geo (hours)   # GST = GAST or GMST per §4
H = LST − α      # hour angle (east negative, west positive)
```

### 5.3 Angular conditions

* **MC:** H = 0 → LST = α → solve λ\_geo.
* **IC:** H = ±12h → LST = α + 12h → λ\_geo = λ\_MC − 180°.
* **Horizon:** h = 0 → cosH0 = −tanφ·tanδ, existence if |tanφ·tanδ| ≤ 1.

  * **ASC:** H = −H0; **DSC:** H = +H0.
  * LST = α + H; solve λ\_geo = (LST − GST)×15°.

### 5.4 Numerical strategy

* **MC/IC:** trivial (meridians).
* **ASC/DSC:** step φ (e.g., 0.1°), find H0 per φ, convert to λ. Densify where curvature high (near peak latitudes). Clamp `cosH0` to \[−1, 1]. Skip if no solution.
* **Parans:** step φ; impose meridian condition of B (H\_B=0 or 180°) to fix LST; solve h\_A=0 for A (east/west root) and derive λ.
* **Robustness:** Double precision; normalize angles; guard inverse trig domains; stitch at ±180°.

### 5.5 Local Space (math)

From RA/Dec and location (φ0, λ0), compute **apparent** topocentric altitude/azimuth (A measured clockwise from North):

```
sin h = sinφ0·sinδ + cosφ0·cosδ·cosH
cos A = (sinδ − sinφ0·sinh) / (cosφ0·cosh)
sin A = −(cosδ·sinH) / cosh
```

Great‑circle track from (φ0,λ0) with initial bearing A and angular distance d (radians):

```
φ(d) = asin( sinφ0·cos d + cosφ0·sin d·cos A )
λ(d) = λ0 + atan2( sin A·sin d·cosφ0, cos d − sinφ0·sinφ(d) )
```

Sample d uniformly (e.g., every 50–100 km) until landmask/world extent limits.

---

## 6) Existence & Edge Cases

* **Circumpolar/no‑rise/no‑set:** if |tanφ·tanδ| > 1 → no horizon crossing → suppress ASC/DSC segments at those latitudes.
* **Peak latitude:** rise/set curves reach max |φ| ≈ 90° − |δ|.
* **High‑|δ| bodies (e.g., Moon):** topocentric parallax can shift rise/set noticeably; enable option.
* **Nodes:** Declination flips sign between NN and SN (δ\_SN = −δ\_NN). Expect exact **mirror symmetry** of lines; avoid rendering both to reduce clutter.
* **Semidiameter & refraction:** If modeling apparent contacts, offset h=0 by ±SD and include standard refraction. Default: **off**.
* **Date line wrapping:** Stitch polylines across ±180°. Keep orientation tags (ASC/DSC/MC/IC) intact.

---

## 7) Orbs & Zones (engineering)

* **Primary angular lines:** visual stroke + selectable **zone width**. Suggested defaults: ±1.0° *hour‑angle* for MC/IC; ±1.0° *altitude* for ASC/DSC.
* **Parans:** latitude band ±0.5°–1.0° around the exact crossing latitude.
* **De‑duplication:** When a body has an automatic opposite (NN/SN, VX/AVX), shade a single zone and tag with **polarity** to prevent double counting in scoring.
* **UI shading:** gradient falloff to 0 at zone edge. Hover readouts: angular distance, ground distance approximation, bearing.

---

## 8) Data Model (suggested)

```json
Body {
  id: "sun", name: "Sun", type: "planet",
  ra: hours, dec: deg, ra_app: hours, dec_app: deg,
  lon: deg, lat: deg, distance: AU,
  derived_opposite_of: null | "north_node" | "vertex"   // if present, this body is derived +180°
}
Line {
  bodyId: "sun", angle: "MC|IC|ASC|DSC|PARAN",
  geometry: [[lon,lat], ...],
  meta: { epochISO, topo: false, method: "geocentric", sidereal: "GAST|GMST", polarity: "+1|-1" }
}
Paran {
  a: {bodyId, angle}, b: {bodyId, angle},
  bands: [ {latCenter, latHalfWidthDeg, segments:[ [lon1,lon2], ... ]} ]
}
```

---

## 9) Algorithm Pseudocode

```python
# inputs: epoch (UTC), birthPlace(lat0, lon0), bodies[], ephemeris
sidereal = "GAST"  # with apparent RA/Dec
for B in bodies:
    ra, dec = apparent_RA_Dec(B, epoch, topo=False)
    # MC/IC meridians
    lam_mc = wrap_deg((ra_hours - GST_hours(epoch, sidereal)) * 15)
    line_mc = full_meridian(lam_mc)
    line_ic = full_meridian(wrap_deg(lam_mc - 180))

    # ASC/DSC curves
    for phi in latitudes(-89.9, +89.9, adaptive_step):
        c = -tan(rad(phi)) * tan(rad(dec))
        if -1 <= c <= 1:
            H0 = acos(c)              # radians
            for sgn in (-1, +1):      # -1 rise, +1 set
                H = sgn * H0
                LST = ra + H
                lam = wrap_deg((hours(LST) - GST_hours(epoch, sidereal)) * 15)
                emit_point(angle=("ASC" if sgn < 0 else "DSC"), lon=lam, lat=phi)

# Parans example: A rising while B culminating
for phi in latitudes(-89.9, +89.9, adaptive_step):
    LST = ra_B                      # B on meridian
    H_A = LST - ra_A
    hA = asin( sin(rad(phi))*sin(rad(dec_A)) + cos(rad(phi))*cos(rad(dec_A))*cos(H_A) )
    if abs(deg(hA)) < altitude_tolerance:
        lam = wrap_deg((hours(LST) - GST_hours(epoch, sidereal)) * 15)
        add_paran_point(phi, lam)
```

---

## 10) Dynamics: C*C*G Overlays (time dimension)

* **Progressions:** Secondary progressed; step daily‑as‑year; compute angular lines per step.
* **Transits:** Step hourly–daily; compute angular lines per slice.
* **Overlay:** draw dynamic lines over natal; provide time slider; highlight **spacetime crossings**.
* **Performance:** pre‑tile by time buckets; cache RA/Dec per body per slice.

---

## 11) Returns & Other Charts

* **Solar/Lunar Return A*****C*****G:** Find return instant in TT (or UT) at birthplace (or specific locality); compute chart positions; map angular lines as natal. Provide relocation toggle.
* **Composite/Midpoint mapping (optional):** midpoint positions → map lines (non‑physical); label clearly.

---

## 12) What We Calculate vs. Omit

**Included:** ASC/MC/DSC/IC lines for configured bodies; parans; optional LS and Geodetics; optional VX/AVX; returns; dynamic overlays.

**Excluded by default:** Fixed stars; asteroids beyond Chiron; ecliptic aspect lines; house cusp lines other than angles; atmospheric refraction; semidiameter contacts.

Toggles exist to enable any excluded feature explicitly.

---

## 13) QA & Validation

* **Analytic checks:**

  * MC/IC meridians exactly 180° apart.
  * ASC/DSC curves symmetric about equator; peaks at φ≈90°−|δ|.
  * **Nodes:** Verify SN lines are mirrors of NN lines (MC↔IC, ASC↔DSC) within tolerance.
  * At equator, ASC/DSC separated by ±90° in longitude from MC/IC for each body.
* **Numerical tests:** reproducible lines vs. Swiss Ephemeris/ACG reference within ≤0.2° (MC/IC) and ≤0.3° (ASC/DSC) geocentric; Moon topocentric ≤0.2°.
* **Edge tests:** circumpolar suppress; date‑line continuity; high‑declination bodies; ΔT sensitivity; GAST vs GMST consistency depending on RA type.

---

## 14) Developer Notes

* Use radians internally; expose degrees/hours per API.
* Normalize longitudes to \[−180°, +180°] (UI) and \[0°, 360°] (storage) consistently.
* Tag each polyline with **direction** (rising vs setting) and **body** for legend/filters.
* Provide **hover readouts:** (lon,lat), local LST, local angle offset, nearest city.
* Expose **sampling controls:** step adaptive by |dλ/dφ|; densify near extrema.
* Keep a **deterministic seed** for simplification/decimation so diffs are stable.
* **Sidereal/Tropical switch:** mapping geometry is equatorial; zodiacal labels can be tropical or sidereal as overlays only.
* **Time handling:** accept local time input, convert to UTC with timezone + DST rules; store UTC only.

---

## 15) Glossary (implementation)

* **Right Ascension (RA), Declination (δ):** Equatorial coordinates of a body.
* **Local Sidereal Time (LST):** GST + longitude (hours). GST = GMST or GAST.
* **Hour Angle (H):** H = LST − RA (east negative).
* **Semi‑arc (H0):** Hour‑angle at rise/set: arccos(−tanφ·tanδ).
* **Co‑latitude:** 90° − |δ| (max |φ| for rise/set curve peak).
* **Paran:** Simultaneous angularity of two bodies (e.g., one on horizon, one on meridian).

---

## 16) Overview & Audit Summary

**Completeness:**

* Covers A*C*G core (ASC/MC/DSC/IC), parans, LS (now with math), geodetics, returns, dynamic overlays, data model, and pseudocode.
* Adds explicit **pairing/derivation rules** (MC/IC, ASC/DSC, NN/SN, VX/AVX) and **sidereal time consistency** to prevent subtle errors.
* Defines QA checks, edge cases, and performance tips.

**Effectiveness (agentic use):**

* Deterministic outputs with normalized coordinates and polarity tagging.
* Explicit naming/ID spec and serialization fields for unambiguous filtering and scoring.
* CI‑ready numeric tolerances and mirror‑symmetry tests for Nodes.

**Optional extensions:**

* Fixed‑star angular lines via catalog; small declination orbs.
* Aspect‑to‑angle lines (non‑standard; keep off by default).
* LS map mode using Azimuthal Equidistant centered on birthplace.
* GPU polyline simplification for high‑zoom performance.

**Policy calls implemented:**

* Nodes and VX/AVX collapsed by derivation; Nodes excluded from LS by default; geometric (unrefracted) horizon default; GAST vs GMST coherency enforced.

---

### End of spec.
