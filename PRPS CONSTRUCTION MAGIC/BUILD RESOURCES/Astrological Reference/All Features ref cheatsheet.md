# Astrological Feature Reference Cheatsheet

Purpose: Dense machine-oriented index of all astronomical / astrological feature classes used in Meridian (calculation + interpretive system). Avoids narration; emphasizes identifiers, sourcing, and formula patterns.

## PLANETS**
| Object | Symbol | SE_ID | Internal ID | Type | Mean Motion (°/day) | API Support | Keywords |
|--------|--------|-------|-------------|------|-------------------|-------------|----------|
| **Sun** | ☉ | 0 | `swe.SUN` | Luminary | 0.9856 | ✅ Full | Identity, vitality, consciousness |
| **Moon** | ☽ | 1 | `swe.MOON` | Luminary | 13.1764 | ✅ Full | Emotions, instincts, cycles |
| **Mercury** | ☿ | 2 | `swe.MERCURY` | Inner Planet | 1.3833 | ✅ Full | Communication, intellect, travel |
| **Venus** | ♀ | 3 | `swe.VENUS` | Inner Planet | 1.2000 | ✅ Full | Love, beauty, values, relationships |
| **Mars** | ♂ | 4 | `swe.MARS` | Outer Planet | 0.5240 | ✅ Full | Action, energy, desire, conflict |
| **Jupiter** | ♃ | 5 | `swe.JUPITER` | Gas Giant | 0.0831 | ✅ Full | Expansion, wisdom, philosophy |
| **Saturn** | ♄ | 6 | `swe.SATURN` | Gas Giant | 0.0335 | ✅ Full | Structure, discipline, limitation |
| **Uranus** | ⛢ | 7 | `swe.URANUS` | 1781 | 84 years | ✅ Full + Transit | Innovation, rebellion, freedom |
| **Neptune** | ♆ | 8 | `swe.NEPTUNE` | 1846 | 165 years | ✅ Full + Transit | Dreams, spirituality, dissolution |
| **Pluto** | ♇ | 9 | `swe.PLUTO` | 1930 | 248 years | ✅ Full + Transit | Transformation, power, regeneration |

---

## ASTEROIDS, CENTAURS & MINOR PLANETS** 

| Name              | Type / Group       | Keywords (Core Themes)             | Swiss Ephemeris ID |
| ----------------- | ------------------ | ---------------------------------- | ------------------ |
| **Ceres**         | Asteroid / Dwarf   | Nurturing, cycles, nourishment     | 1                  |
| **Pallas Athena** | Asteroid           | Wisdom, strategy, intelligence     | 2                  |
| **Juno**          | Asteroid           | Partnership, commitment, marriage  | 3                  |
| **Vesta**         | Asteroid           | Devotion, sacredness, focus        | 4                  |
| **Hygiea**        | Asteroid           | Health, hygiene, healing           | 10                 |
| **Eros**          | Asteroid           | Passion, erotic desire, creativity | 433                |
| **Psyche**        | Asteroid           | Soul, psychology, depth            | 16                 |
| **Chiron**        | Centaur            | Wounds, healing, transformation    | 2060               |
| **Pholus**        | Centaur            | Catalyst, chain reactions          | 5145               |
| **Eris**          | Dwarf Planet (TNO) | Discord, disruption, awakening     | 136199             |
| **Sedna**         | Dwarf Planet (TNO) | Survival, trauma, initiation       | 90377              |
| **Haumea**        | Dwarf Planet (TNO) | Fertility, creativity, rebirth     | 136108             |
| **Makemake**      | Dwarf Planet (TNO) | Ritual, culture, ecology           | 136472             |

---

## LUNAR NODES, APOGEE & AUXILIARY POINTS**

### Lunar Nodes
| Point | Symbol | SE_ID | Type | Calculation Method | Motion Rate | API Support |
|-------|--------|-------|------|--------------------|-------------|-------------|
| **North Node (Mean)** | ☊ | 10 | Mean | `swe.MEAN_NODE` | -0.0529°/day | ✅ Full |
| **North Node (True)** | ☊ | 11 | Osculating | `swe.TRUE_NODE` | Variable | ✅ Full |
| **South Node (Mean)** | ☋ | N/A | Derived | Mean Node + 180° | -0.0529°/day | ✅ Full + Enhanced |
| **South Node (True)** | ☋ | N/A | Derived | True Node + 180° | Variable | ✅ Full + Enhanced |

### Black Moon Lilith (Lunar Apogee)
| Point | Symbol | SE_ID | Type | Calculation | Orb Period | API Support |
|-------|--------|-------|------|-------------|------------|-------------|
| **Mean Lilith** | ⚸ | 12 | Mean Apogee | `swe.MEAN_APOG` | 8.85 years | ✅ Full |
| **True Lilith** | ⚸ | 13 | Osculating | `swe.OSCU_APOG` | Variable | ✅ Full |

### Auxiliary Points
| Point | Symbol | SE_ID | Type | Calculation Method | Motion Rate | API Support |
|-------|--------|-------|------|--------------------|-------------|-------------|
| **Vertex** | Vx | N/A | Sensitive Angle | Intersection of ecliptic & prime vertical (west) | Variable (diurnal) | ✅ Calculated |
| **Antivertex** | Avx | N/A | Derived | Vertex + 180° | Variable (diurnal) | ✅ Calculated |
| **Sun/Moon Midpoint** | ⊙☽ | N/A | Derived Midpoint | (Sun longitude + Moon longitude) ÷ 2 | Variable | ✅ Calculated |

### Angle & House Framework
| Angle | Symbol | Calculation | ACG Line Type | Mathematical Definition |
|-------|--------|-------------|---------------|------------------------|
| **Ascendant (ASC)** | ♈︎ | Eastern horizon | AC Line | Intersection of ecliptic & horizon (East) |
| **Descendant (DSC)** | ♎︎ | Western horizon | DC Line | Intersection of ecliptic & horizon (West) |
| **Midheaven (MC)** | ♑︎ | Southern meridian | MC Line | Intersection of ecliptic & meridian (South) |
| **Imum Coeli (IC)** | ♋︎ | Northern meridian | IC Line | Intersection of ecliptic & meridian (North) |


## HOUSE SYSTEMS**

### Supported House Systems (18 Total)
| Code | System Name | Method | Era | Primary Use | Technical Notes |
|------|-------------|--------|-----|-------------|----------------|
| **P** | Placidus | Time-based trisection | 1602 | Modern Western | Most popular, unequal houses |
| **K** | Koch | Birthplace-based | 1971 | German astrology | Modified Placidus |
| **R** | Regiomontanus | Space-based | 1460s | Medieval/Traditional | Equal on celestial equator |
| **C** | Campanus | Prime vertical | 1260s | Medieval | Equal on horizon |
| **E** | Equal House | 30° from ASC | Ancient | Simplified modern | Mathematical equality |
| **W** | Whole Sign | Signs as houses | Hellenistic | Ancient/Traditional | Sign = house |
| **O** | Porphyrius | Space trisection | 3rd cent. | Ancient | Oldest quadrant system |
| **B** | Alcabitus | Diurnal arc | 11th cent. | Arabic medieval | Al-Qabisi method |
| **M** | Morinus | Equatorial | 1661 | French rational | Celestial equator based |
| **T** | Polich-Page | Topocentric | 1961 | Modern topocentric | Observer-centered |
| **V** | Vehlow Equal | 15° from ASC | 1961 | German equal | Offset equal houses |
| **X** | Meridian | Axial rotation | Modern | Theoretical | Rotation-based |
| **H** | Azimuthal | Horizon-based | Modern | Local coordinates | Altitude-azimuth |
| **G** | Galactic Equator | Galactic plane | Modern | Galactic astrology | Galaxy-centered |
| **U** | Krusinski | Polish method | 1995 | Modern European | Hybrid approach |
| **N** | Axial Rotation | Earth axis | Experimental | Research | Rotation considerations |
| **D** | Carter Equal | Poli-equatorial | 20th cent. | Theoretical | Modified equal |
| **I** | Horizontal | True horizon | Observational | Practical | 🟡 Research |


## Aspect Set
| Name | Key | Exact Angle | Default Orb (Major) | Type | Notes |
|------|-----|------------|---------------------|------|-------|
| Conjunction | conj | 0° | 8° (lum), 6° (others) | Major | Blend |
| Opposition | opp | 180° | 8° | Major | Polarity |
| Square | sq | 90° | 6° | Major | Dynamic tension |
| Trine | tri | 120° | 6° | Major | Flow |
| Sextile | sext | 60° | 4° | Major | Opportunity |
| Quincunx | quin | 150° | 3° | Adjustive | Inconjunct |
| Semi-sextile | ssext | 30° | 2° | Minor | Growth edge |
| Semi-square | ssq | 45° | 2° | Minor | Friction |
| Sesquiquadrate | sesq | 135° | 2° | Minor | Internal stress |
| Quintile | qui | 72° | 1.5° | Creative | 5th harmonic |
| Bi-quintile | bqui | 144° | 1.5° | Creative | Harmonic |
| Septile | sep | ~51.4286° | 1° | Esoteric | 7th harmonic |
| Novile | nov | 40° | 1° | Esoteric | 9th harmonic |
| Tridecile | tri10 | 108° | 1.5° | Harmonic | 10th derived |
| Undecile | und | ~32.727° | 1° | Harmonic | 11th |

## Arabic Parts (Hermetic Lots)
Formula convention (Day / Night). ASC = Ascendant longitude; sect aware swap Sun/Moon.

### Core Lots
| Lot | Key | Day Formula | Night Formula | Notes |
|-----|-----|-------------|---------------|-------|
| Fortune | lot_fortune | ASC + Moon − Sun | ASC + Sun − Moon | Material / body |
| Spirit | lot_spirit | ASC + Sun − Moon | ASC + Moon − Sun | Activating principle |
| Basis | lot_basis | ASC + Fortune − Spirit | Same (sect-independent) | Foundation |
| Travel | lot_travel | ASC + 9th cusp − Ruler of 9th | Same (sect-independent) | Journeys |
| Fame | lot_fame | ASC + 10th cusp − Sun | Same (sect-independent) | Reputation |
| Work/Profession | lot_profession | ASC + Mercury − Saturn | ASC + Saturn − Mercury | Career |
| Property | lot_property | ASC + 4th cusp − Ruler of 4th | Same (sect-independent) | Real estate |
| Wealth | lot_wealth | ASC + Jupiter − Sun | ASC + Sun − Jupiter | Assets |
| Eros | lot_eros | ASC + Venus − Spirit | ASC + Spirit − Venus | Desire |
| Necessity | lot_necessity | ASC + Spirit − Fortune | ASC + Fortune − Spirit | Compulsion |
| Victory | lot_victory | ASC + Jupiter − Spirit | ASC + Spirit − Jupiter | Success |
| Nemesis | lot_nemesis | ASC + Spirit − Saturn | ASC + Saturn − Spirit | Obstacles |
| Exaltation | lot_exaltation | ASC + (Degree of Exalted Luminary − Luminary) | Same (sect-independent) | Dignity |
| Marriage | lot_marriage | ASC + Venus − Saturn | ASC + Saturn − Venus | Contract union |
| Faith (Religion) | lot_faith | ASC + Jupiter − Sun | ASC + Sun − Jupiter | Belief |
| Friends | lot_friends | ASC + Mercury − Jupiter | ASC + Jupiter − Mercury | Social network |


## Fixed Stars
Source: `backend/ephemeris/sefstars.txt` (Swiss Ephemeris distribution). Total unique names parsed: 735.

Storage Strategy:
- Maintain canonical unique key = first encountered lowercase name with underscores.
- Provide alias map for alternative transliterations.
- Magnitude, RA/Dec (ICRS), proper motion retained; parallax rarely used.

* **Foundation 24**: The core stars most consistently used in astrology and astrocartography. Highest priority.
* **Extended 77**: The Foundation 24 plus an additional 53 stars drawn from Brady and other traditions. Comprehensive, hemispherically balanced, and culturally significant.

**Fixed Stars show only as points/orbs of influence — they do not render AC, DC, IC, MC, or aspect lines.**

### Foundation 24 (100 mile radius)

1. Regulus (α Leo) — honor, ascent, charisma, hubris risk
2. Aldebaran (α Tau) — integrity, success, guardianship
3. Antares (α Sco) — passion, battle, obsession, danger
4. Fomalhaut (α PsA) — vision, mysticism, ideal vs scandal
5. Spica (α Vir) — talent, gifts, protection, harvest
6. Arcturus (α Boo) — pathfinding, leadership, guidance
7. Sirius (α CMa) — brilliance, renown, longevity
8. Canopus (α Car) — navigation, stewardship, authority
9. Vega (α Lyr) — artistry, charisma, inspiration
10. Capella (α Aur) — guardianship, resourcefulness
11. Betelgeuse (α Ori) — prominence, volatility, force
12. Rigel (β Ori) — mastery, achievement through action
13. Altair (α Aql) — daring, risk, independence
14. Algol (β Per) — extremity, loss, survival, power
15. Procyon (α CMi) — quick rise, nimbleness, ephemeral
16. Bellatrix (γ Ori) — boldness, Amazon, campaigns
17. Deneb Adige (α Cyg) — poetry, imagination, elevation
18. Alcyone (η Tau, Pleiades) — collective vision, sorrow, depth
19. Achernar (α Eri) — endings, ideals, transition
20. Acrux (α Cru) — mysticism, intensity, devotion
21. Alphecca (α CrB) — artistry, dignity, allure
22. Rasalhague (α Oph) — healing, integration, medicine
23. Denebola (β Leo) — outsider, reforms, contrarian
24. Markab (α Peg) — ambition, steadiness, risk of fall

### Extended 77 (80 mile radius)

Includes all **Foundation 24** plus the following:

25. Alpheratz (α And) — independence, freedom, prominence
26. Scheat (β Peg) — misfortune, intensity, brilliance
27. Pollux (β Gem) — courage, martial energy
28. Castor (α Gem) — intellect, duality, instability
29. Deneb (α Cyg) — ascension, spirituality, artistry
30. Sadalsuud (β Aqr) — fortune, abundance
31. Sadalmelik (α Aqr) — benevolence, optimism
32. Zuben Elgenubi (α Lib) — justice, social causes
33. Zuben Eschamali (β Lib) — diplomacy, gain, cunning
34. Vindemiatrix (ε Vir) — foresight, premature action
35. Zosma (δ Leo) — victim/savior dynamics
36. Algorab (δ Crv) — destruction, cunning
37. Kochab (β UMi) — guardianship, stability
38. Ankaa (α Phe) — renewal, cycles of rebirth
39. Phact (α Col) — curiosity, travel, exploration
40. Shaula (λ Sco) — decisive strike, endings
41. Ras Algethi (α Her) — strength, devotion
42. Facies (M22 region) — laser focus, severity
43. Deneb Algedi (δ Cap) — law, order, repercussions
44. Nashira (γ Cap) — success, discipline
45. Nunki (σ Sgr) — navigation, broadcasting
46. Algenib (γ Peg) — ambition, surge
47. Enif (ε Peg) — imagination, force
48. Alnilam (ε Ori) — visibility, prominence
49. Mintaka (δ Ori) — clarity, portals
50. Alnitak (ζ Ori) — ignition, enterprise
51. Mizar (ζ UMa) — networks, visibility
52. Dubhe (α UMa) — guardianship, authority
53. Alderamin (α Cep) — stewardship, planning
54. Almach (γ And) — artistry, union, allure
55. Mirach (β And) — beauty, partnership, charisma
56. Ras Elased Australis (ε Leo) — pride, assertion, drama
57. Ras Elased Borealis (μ Leo) — command, authority
58. Alkes (α Crt) — vessel, receptivity, tradition
59. Gienah (γ Crv) — omens, messages, sharpness
60. Sualocin (α Del) — guidance, nimbleness
61. Rotanev (β Del) — humor, resourcefulness
62. Peacock (α Pav) — pride, vision, creativity
63. Alphard (α Hya) — intensity, passion, solitary themes
64. Menkar (α Cet) — collective sacrifice, deep waters
65. Hamal (α Ari) — leadership, assertion, beginnings
66. Alpherg (η Psc) — spirituality, initiation, mysticism
67. Foramen (θ Car) — navigation, endurance
68. Avior (ε Car) — guidance, exploration
69. Suhail (γ Vel) — command, logistics
70. Kaus Australis (ε Sgr) — aim, trajectory, clarity
71. Unukalhai (α Ser) — healing, danger, intensity
72. Sadachbia (γ Aqr) — good fortune, hidden help
73. Skat (δ Aqr) — teamwork, collective work
74. Alkaid (η UMa) — command, endings
75. Pherkad (γ UMi) — guidance, guardianship
76. Caph (β Cas) — prominence, drama
77. Schedar (α Cas) — dignity, authority


## Astrocartography (ACG) Features
| Feature | Key | Criterion | Lines | Notes |
|---------|-----|----------|-------|-------|
| AC Line | acg_asc | Body rising longitude locus | Polyline | Solve where altitude=0 & rising |
| DC Line | acg_dsc | Body setting | Polyline | altitude=0 & setting |
| MC Line | acg_mc | Culmination (upper transit) | Polyline | Local hour angle = 0 |
| IC Line | acg_ic | Anti-culmination | Polyline | Hour angle = 180° |

| Aspect-to-Angle | acg_aspect_angle | Body forms exact aspect to ASC/MC (trine, square and sextile only) | Dashed | Root-finding across longitude grid |

| Paran | acg_paran | Two bodies simultaneously on different angle states (e.g., one rising, other culminating) | Markers / arcs | Solve time-of-day pairing |

| Feature Orb | acg_orb | Circular highlight at exact body location | Circle | Configurable radius by body type |
| Planet Orb | acg_planet_orb | Circular highlight where planet is angular | Circle | Size varies by planet dignity/importance |
| Fixed Star Orb | acg_star_orb | Circular highlight at star's exact position | Circle | Size proportional to magnitude |
| Paran Intersection orb| acg_paran_point | Highlight where two bodies form paran | Circle | Marks exact crossing location |
| Asteroid Orb | acg_asteroid_orb | Circular highlight at asteroid position | Circle | Smaller radius than major planets |

## Predictive / Temporal Events
| Event | Key | Detection Method | Accuracy | Notes |
|-------|-----|-----------------|----------|-------|
| Planet Sign Ingress | ingress | Longitude crossing sign boundary | <10s | Batch search |
| Retrograde Station | station_retro | Speed sign change (+ to −) | <30s | Derivative zero |
| Direct Station | station_direct | Speed sign change (− to +) | <30s | Derivative zero |
| Exact Aspect (transit) | aspect_exact | Time of longitudinal angle difference = exact | <10s | Root-finding |
| Lunation (New) | new_moon | Sun-Moon elongation = 0° | <5s | Synodic cycle |
| Lunation (Full) | full_moon | Elongation = 180° | <5s | Opposition |
| Solar Eclipse | solar_eclipse | Syzygy + Moon near node (gamma threshold) | ~1m | External NASA elements optional |
| Lunar Eclipse | lunar_eclipse | Syzygy + Earth shadow alignment | ~1m | Umbra/penumbra calc |
| Planet Return | return | Body longitude returns natal degree | <30s | Jupiter/Saturn long spans |
| Secondary Progression | sec_prog | Secondary progression: +1 day/year for all points | ~orb rules | Creates complete progressed chart |
| Solar Arc Directions | solar_arc | Add solar arc to all points | N/A | Arc = progressed Sun − natal Sun |
| Cyclo-Cartography | cyclo_cart | Personal planets as progressions, others as transits | 1 day increments | Special hybrid chart cast from birth |

## Coordinate & Reference Frames
| Frame | Key | Usage |
|-------|-----|-------|
| Tropical Ecliptic (geocentric) | geo_trop | Standard zodiac calculations |
| Sidereal (Lahiri default) | geo_sid_lahiri | Optional sidereal charts |
| Equatorial (RA/Dec) | geo_eq | ACG line solving, star positions |
| Topocentric Ecliptic | topo_trop | Parallax-sensitive (Moon etc.) |
| Heliocentric Ecliptic | helio | Alternative perspective cycles |
| Galactic | galactic | Contextual reference (rare) |

```

## Computational Notes
| Topic | Note |
|-------|------|
| Time Scale | Use UT for ephemeris; convert to TT (ΔT) for high-precision eclipse modules. |
| Light-Time | Swiss Ephemeris handles internally for planets; stars treated fixed except proper motion. |
| House Cusps | Some systems undefined near polar latitudes (Placidus); fallback to Whole Sign. |
| Normalization | Reduce results to 0–360° after arithmetic; handle negative results by +360°. |
| Aspect Matching | Use absolute angular difference minimized modulo 360; support orbed window & applying/separating classification. |



