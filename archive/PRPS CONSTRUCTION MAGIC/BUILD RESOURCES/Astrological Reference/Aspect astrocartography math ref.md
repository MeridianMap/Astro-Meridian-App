# Aspect Astrocartography: Mathematical Reference

This document specifies the math to compute and render:

1. Angular lines (planet on MC/IC/ASC/DSC), and
2. Aspect-to-angle lines (planet forming a zodiacal aspect to the local MC/IC/ASC/DSC).

Angles in radians unless noted. Geographic longitudes are east-positive.

---

## 0. Symbols

* t: UTC as Julian Date (JD\_UTC).  DeltaT = TT - UT1 (seconds).
* T: (JD\_TT - 2451545.0) / 36525 (Julian centuries of TT from J2000.0).
* (lambda, beta): ecliptic longitude, latitude of a body (geocentric, true).
* (alpha, delta): right ascension, declination of a body (geocentric, true).
* eps: true obliquity of the ecliptic.
* theta\_G: Greenwich apparent sidereal time.
* theta\_L = theta\_G + lambda\_E: local apparent sidereal time at geographic longitude lambda\_E (east-positive).
* phi: geographic latitude.
* H = theta\_L - alpha: local hour angle of a body.
* h: altitude; A: azimuth.
* Aspect angles Theta: {0, 60°, 90°, 120°, 180°} = {0, pi/3, pi/2, 2pi/3, pi}.
* Orb Delta: tolerance in radians. Recommend majors Delta in \[1°, 3°] = \[0.01745, 0.05236].

---

### 0.1 Conventions & helpers

* **Longitude/latitude**: Use WGS84 geodetic longitude (east-positive) and latitude for I/O. For horizon formulas, use **geocentric latitude** phi\_gc. Convert:

  * k = (1 - f)^2 with WGS84 flattening f = 1/298.257223563
  * tan(phi\_gc) = k \* tan(phi\_gd)
  * Use phi\_gc in §1.3 and §2.2; keep phi\_gd for output and storage.
* **Sidereal time**: Compute theta\_G using **UT1** (not UTC). If only UTC is available, apply DUT1 (UT1−UTC) or accept <0.1 s error.
* **Wrapping helpers** (pseudo):

  * wrap\_0\_2pi(x) = x − floor(x/(2pi))\*(2pi)
  * wrap\_mpi\_pi(x) = ((x + pi) mod 2pi) − pi
  * angdiff(a) = wrap\_mpi\_pi(a)
* **Aspect distance check**: treat a match when |angdiff(lambda\_angle − lambda\_p − Theta)| ≤ Delta.

## 1. Core astronomy

### 1.1 Time scales and sidereal time

1. JD and TT: Convert UTC to JD\_UTC. JD\_TT = JD\_UTC + (DeltaT + 32.184 s)/86400.
2. Obliquity eps (true): IAU 2006/2000A or Meeus mean + nutation.
3. Greenwich sidereal time (apparent):

   * GMST: standard polynomial in T (e.g., Meeus).
   * GAST: theta\_G = GMST + dpsi \* cos(eps), where dpsi is nutation in longitude. Normalize to \[0, 2pi).
4. Local ST: theta\_L = theta\_G + lambda\_E (normalize to \[0, 2pi)).

### 1.2 Ecliptic -> equatorial

Given (lambda, beta) and eps:

* X\_ecl = cos(beta) \* cos(lambda)
* Y\_ecl = cos(beta) \* sin(lambda)
* Z\_ecl = sin(beta)
  Rotate by eps about the X-axis:
* X\_eq = X\_ecl
* Y\_eq = Y\_ecl \* cos(eps) - Z\_ecl \* sin(eps)
* Z\_eq = Y\_ecl \* sin(eps) + Z\_ecl \* cos(eps)
  Then
* alpha = atan2(Y\_eq, X\_eq)
* delta = asin(Z\_eq)

### 1.3 Horizon relations

For a body with (alpha, delta) at site (phi, lambda\_E):

* sin(h) = sin(phi)\*sin(delta) + cos(phi)\*cos(delta)\*cos(H)
* H = theta\_L - alpha
  On the horizon (ASC/DSC): set h = 0 which yields cos(H0) = -tan(phi) \* tan(delta).
  Rising branch if sin(H) < 0; setting branch if sin(H) > 0.

---

## 2. Angular lines (planet on MC/IC/ASC/DSC)

Loci of geographic points (phi, lambda\_E) at fixed t.

### 2.1 MC / IC

Condition: meridian transit H = 0 (MC) or H = pi (IC).

* Longitudes: lambda\_E = alpha - theta\_G (MC), and lambda\_E = alpha - theta\_G + pi (IC), normalized to \[-pi, pi).
* These are meridians (all latitudes valid). Render pole-to-pole great circles at constant lambda\_E.

### 2.2 ASC / DSC

Condition: horizon crossing h = 0 with rising/setting branch.
Efficient parametric form by longitude:

1. For each lambda\_E: compute theta\_L and H = theta\_L - alpha (normalize to \[-pi, pi)).
2. Latitude where h = 0:

   * phi\_gc(lambda\_E) = atan( -cos(H) / tan(delta) )   \[handle delta -> 0 separately; see §5.3]. If you require geodetic output, convert phi\_gc -> phi\_gd via WGS84 inverse (approx: tan(phi\_gd) = tan(phi\_gc)/k with k from §0.1).
3. Branch: ASC if sin(H) < 0; DSC if sin(H) > 0.
4. Clip segments where the body is circumpolar (no horizon crossing) for the resulting phi: |tan(phi)\*tan(delta)| > 1.

Note: For delta ≈ 0, horizon crossings occur at H = ±pi/2 for all phi; then ASC/DSC longitudes satisfy theta\_L - alpha = ∓ pi/2 (render as meridians at alpha - theta\_G ± pi/2).

---

## 3. Aspect-to-angle lines (planet vs local MC/IC/ASC/DSC)

Map loci where a planet’s ecliptic longitude forms a zodiacal aspect Theta to the local angle’s ecliptic longitude at (phi, lambda\_E).

### 3.1 Local angle longitudes

Let theta\_L be known.

* MC ecliptic longitude lambda\_MC(theta\_L):

  * lambda\_MC = atan2( sin(theta\_L) \* cos(eps), cos(theta\_L) ), normalized to \[0, 2pi).
* IC: lambda\_IC = lambda\_MC + pi (normalize).
* ASC ecliptic longitude lambda\_ASC(phi, theta\_L):

  * lambda\_ASC = atan2( sin(theta\_L) \* cos(eps) - tan(phi) \* sin(eps), cos(theta\_L) ), normalized.
* DSC: lambda\_DSC = lambda\_ASC + pi (normalize).

### 3.2 Aspect condition

Given a planet with longitude lambda\_p, define wrapped difference

* Delta\_a(angle) = wrap\_{-pi,pi}( lambda\_angle - lambda\_p )
  Aspect-to-angle line for aspect Theta is the zero-contour of
* F(phi, lambda\_E) = angdiff( Delta\_a(angle) - Theta )
  Render points where |F| <= Delta (orb).

### 3.3 Character of loci

* MC/IC aspects: lambda\_MC depends only on theta\_L (thus only on longitude). Resulting lines are meridians. Algorithm: solve for theta\_L\* such that lambda\_MC(theta\_L\*) = lambda\_p + Theta, then lambda\_E = theta\_L\* - theta\_G.
* ASC/DSC aspects: lambda\_ASC depends on both latitude and longitude, producing curved loci. Compute via contouring (see §4).

---

## 4. Numerical construction

### 4.1 Marching-contour approach (robust)

For each planet and each angle type:

1. Precompute at t: eps, theta\_G, lambda\_p.
2. Define a lat–lon grid (e.g., 0.25°–1°). For each cell corner, evaluate F(phi, lambda\_E) (from §3.2) or h(phi, lambda\_E) for angular lines (§2).
3. Run marching squares to extract F = 0 (aspect-to-angle) or h = 0 (ASC/DSC) isolines.
4. Refine vertices with bisection or Newton in lambda\_E or phi to reach sub-arcminute precision.

### 4.2 Parametric shortcuts

* MC/IC (angular or aspect): meridian(s) at explicit lambda\_E (see §2.1 and §3.3). No gridding needed.
* ASC/DSC (angular): use §2.2 parametric formula for fast sampling by longitude, then densify by great-circle interpolation.

### 4.3 Precision targets

* Planet positions: < 1 arcsec (Swiss Ephemeris or equivalent).
* Angle longitudes (ASC/MC): < 5 arcsec with double precision and correct quadrant handling.
* Map output: GeoJSON polylines with vertices every 0.25–0.5° great-circle separation.

---

## 5. Edge cases and stability

### 5.1 Quadrants and wrapping

Use atan2 for all inverse tangents. Normalize longitudes/RA consistently. Distinguish \[0, 2pi) vs \[-pi, pi) representations.

### 5.2 Circumpolar regions

For |tan(phi)\*tan(delta)| > 1, horizon crossings do not occur. Clip ASC/DSC angular lines accordingly. Aspect-to-ASC/DSC lines may still exist mathematically; suppress where the underlying angle is undefined (ASC at exact poles).

### 5.3 delta -> 0 or phi -> ±pi/2

* delta -> 0: prefer meridian form for ASC/DSC longitudes (H = ±pi/2).
* Near poles, compute lambda\_ASC using a stable vector method: build local horizon basis and project the ecliptic to solve for the ASC longitude numerically.

### 5.4 Nutation and true vs mean angles

For aspect-to-angle work, use true obliquity and apparent sidereal time so that lambda\_MC and lambda\_ASC are apparent ecliptic longitudes.

### 5.5 Topocentric vs geocentric bodies

Standard A*C*G uses geocentric planetary positions. If topocentric is desired (Moon parallax), compute topocentric (alpha, delta) before constructing lines.

---

## 6. Rendering and layers

* Separate layers per planet, per angle (MC/IC/ASC/DSC), and per aspect Theta.
* Support on/off toggles and orb shading (fill bands where |F| < Delta).
* Use great-circle interpolation between vertices for globe renderers.

---

### 6.4 Dateline stitching & unwrapping

* When exporting polylines, split segments that cross the ±180° meridian and unwrap longitudes per segment to avoid long arcs across the map.
* For globe renderers, emit geodesic segments in increasing longitude with wrap-aware interpolation.

## 7. Minimal algorithmic checklist (per timestamp t)

1. Compute eps and theta\_G. For each planet: (lambda\_p, beta\_p) -> (alpha, delta).
2. Angular lines:

   * MC/IC: explicit meridians at lambda\_E = alpha - theta\_G and + pi.
   * ASC/DSC: parametric §2.2 or contour h = 0.
3. Aspect-to-angle lines (for each Theta):

   * MC/IC: solve lambda\_MC(theta\_L) = lambda\_p + Theta -> lambda\_E = theta\_L - theta\_G.
   * ASC/DSC: contour F(phi, lambda\_E) = 0 with lambda\_ASC from §3.1.
4. Export GeoJSON with CRS WGS84.

---

## 8. Validation

* Unit tests for: lambda\_MC(theta\_L), lambda\_ASC(phi, theta\_L), horizon equation, ASC/DSC branch sign, meridian positions.
* Cross-check a sample epoch against a trusted package (Swiss Ephemeris + existing A*C*G tool) for multiple planets.

---

## 9. Implementation notes

* Earth rotation/GMST: IAU SOFA or Meeus polynomials.
* Nutation/obliquity: IAU 2000A/2006 (or Meeus for simplicity).
* Ephemerides: Swiss Ephemeris (DE431+), JPL, or equivalent high-precision source.

> Structured for direct translation into code (Python/JS/TS/C++).
