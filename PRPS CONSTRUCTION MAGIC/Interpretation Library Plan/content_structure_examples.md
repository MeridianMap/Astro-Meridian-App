# Content Structure Examples

This document provides examples of the content structure for various interpretation components.

## Basic Elements

### Planet Example (Sun)

```yaml
# planets/sun.yaml
id: "sun"
name: "Sun"
type: "planet"
keywords: ["identity", "ego", "self-expression", "vitality", "purpose", "consciousness"]
description: |
  The Sun represents your core identity, conscious mind, and creative self-expression.
  It shows where and how you shine, and what brings vitality and purpose to your life.
mythology: |
  The Sun was associated with the god Apollo in Greek mythology, representing light, 
  truth, healing, music, and prophecy. In other traditions, the Sun is often the 
  primary deity representing life force and divine power.
psychology: |
  Psychologically, the Sun represents the ego, the conscious sense of self, and 
  the integration of personality. It's associated with our conscious will, creative 
  self-expression, and sense of purpose in life.
```

### Sign Example (Aries)

```yaml
# signs/aries.yaml
id: "aries"
name: "Aries"
element: "fire"
modality: "cardinal"
ruler: "mars"
keywords: ["initiative", "courage", "action", "independence", "pioneering", "assertive"]
description: |
  Aries is the first sign of the zodiac, representing new beginnings, initiative, 
  and pioneering energy. It's associated with courage, assertiveness, and a direct 
  approach to life. Aries energy is independent, competitive, and driven to take action.
qualities: |
  Cardinal fire sign, masculine polarity. Aries initiates action, is self-motivated, 
  and leads with courage and enthusiasm. The raw impulse to exist and assert oneself.
challenges: |
  Can be impulsive, impatient, and quick to anger. May start projects but not finish them, 
  act without consideration for others, or be too competitive and combative.
```

### House Example (First House)

```yaml
# houses/house_1.yaml
id: "house_1"
number: 1
name: "First House"
keywords: ["self", "identity", "appearance", "beginnings", "personality", "physical body"]
life_areas: ["personal identity", "physical appearance", "first impressions", "self-image"]
description: |
  The First House represents your outward personality, physical appearance, and the 
  impression you make on others. It shows how you approach new situations and how you 
  initiate action in the world. This house governs self-awareness, personal identity, 
  and how you present yourself.
traditional_name: "House of Self"
natural_sign: "Aries"
opposing_house: 7
```

### Aspect Example (Conjunction)

```yaml
# aspects/conjunction.yaml
id: "conjunction"
name: "Conjunction"
angle: 0
orb: 8
keywords: ["merging", "blending", "fusion", "intensification", "unity", "concentration"]
nature: "amplifying"
description: |
  The conjunction represents a fusion of planetary energies, where two planets occupy 
  approximately the same position in the zodiac. This aspect creates an intensified 
  combination of the planets involved, with their energies blended and expressed as a unit.
interpretation_framework: |
  With a conjunction, the planets' energies merge and operate as a team. The result depends 
  on the nature of the planets involved: harmonious planets enhance each other, while 
  challenging combinations can create internal tension or one-sided expression. The sign 
  and house placement strongly influence how this merged energy manifests.
```

## Combinations

### Planet in Sign Example (Sun in Leo)

```yaml
# planet_in_sign/sun_in_leo.yaml
id: "sun_in_leo"
planet: "Sun"
sign: "Leo"
keywords: ["dramatic", "creative", "proud", "generous", "confident", "theatrical"]
levels:
  level_1: "The Sun is in Leo."
  level_2: "Your core identity and sense of self are expressed through creativity, warmth, and leadership."
  level_3: "You have a natural need to express yourself dramatically and receive recognition for your unique contributions. Your confidence and warmth draw others to you, though you may struggle with pride or attention-seeking behavior."
  level_4: "You thrive in situations that allow creative self-expression, leadership, and recognition. You make an excellent mentor, performer, or leader who inspires through generosity and enthusiasm."
  level_5: "Your soul purpose involves learning to balance healthy pride with humility, using your natural radiance to illuminate and inspire others rather than seeking admiration for its own sake."
traditions:
  modern: "With the Sun in its home sign, you express your authentic self with natural confidence and creative power."
  traditional: "The Sun is in its domicile in Leo, granting dignity and strength to your vital essence and leadership qualities."
  psychological: "Your ego is comfortably at home in Leo, creating a natural harmony between your conscious identity and your self-expression."
```

### Planet in House Example (Moon in 4th House)

```yaml
# planet_in_house/moon_in_house_4.yaml
id: "moon_in_house_4"
planet: "Moon"
house: 4
keywords: ["emotional roots", "family connection", "home focus", "nurturing", "private life"]
levels:
  level_1: "The Moon is in the 4th house."
  level_2: "Your emotional needs and instinctive responses are centered around home, family, and your sense of belonging."
  level_3: "You have a deep emotional connection to your roots, ancestry, and private life. You may be protective of your home environment and seek emotional security through creating a nurturing space."
  level_4: "Creating a secure home base is essential for your emotional well-being. You likely have strong family ties or a deep connection to your heritage. You may excel at nurturing others and creating environments where people feel safe and cared for."
  level_5: "Your soul journey involves healing ancestral patterns and creating emotional foundations that support not just yourself but future generations. Your sensitivity to the past can help you transform family karma."
traditions:
  modern: "With the Moon in the 4th house, you have a natural emotional connection to home and family matters."
  traditional: "The Moon is in a natural, dignified placement in the 4th house, strengthening matters of home, family, and emotional foundations."
  psychological: "Your emotional needs and subconscious patterns are strongly tied to your early home environment and sense of belonging."
```

### Planet Aspect Planet Example (Sun Square Moon)

```yaml
# planet_aspect_planet/sun_square_moon.yaml
id: "sun_square_moon"
planet1: "Sun"
planet2: "Moon"
aspect: "square"
keywords: ["internal tension", "self-awareness", "emotional growth", "identity conflict", "integration challenge"]
levels:
  level_1: "The Sun is square the Moon."
  level_2: "There is tension between your conscious identity and your emotional needs and instincts."
  level_3: "You may experience internal conflict between what you consciously want and your emotional reactions. This creates a productive tension that drives you to develop greater self-awareness and integration of different parts of yourself."
  level_4: "This aspect often manifests as a dynamic internal dialogue between rational will and emotional needs. While challenging, it provides the stimulus for significant personal growth and a rich inner life. You may need to consciously work on balancing assertion with receptivity."
  level_5: "Your soul journey involves integrating masculine and feminine principles within yourself. The internal tension you experience is purposeful, designed to develop a more complete and balanced sense of self that honors both conscious will and unconscious emotional needs."
traditions:
  modern: "This square creates a productive tension between your identity and emotional nature, driving personal growth through integration of these core elements."
  traditional: "The luminaries in square aspect indicate a challenging relationship between the vital spirit and the soul, requiring conscious effort to reconcile."
  psychological: "This aspect suggests potential tension between ego (Sun) and emotional patterns or mothering experiences (Moon), often rooted in parental dynamics."
```

## Chart Patterns

### Aspect Pattern Example (T-Square)

```yaml
# aspect_patterns/t_square.yaml
id: "t_square"
name: "T-Square"
pattern_type: "aspect_pattern"
planets_required: 3
aspects_required: ["opposition", "square", "square"]
keywords: ["dynamic tension", "motivation", "challenge", "achievement", "drive"]
description: |
  A T-Square consists of two planets in opposition, with a third planet square to both.
  This creates a right-angled triangle in the chart, with the third planet (the apex)
  receiving the combined tension of the opposition.
interpretation: |
  The T-Square represents an area of significant challenge and dynamic tension in the chart.
  It creates a powerful drive to resolve the inherent conflict through action and achievement.
  The apex planet shows where and how this energy is expressed, while the empty leg
  (opposite the apex) indicates the direction of resolution and integration.
  
  People with prominent T-Squares often display determination, resilience, and the ability
  to overcome obstacles through persistent effort. The tension of this pattern provides
  motivation and energy for accomplishment, though it can also create stress and conflict
  until the energies are consciously directed.
```

### Chart Shape Example (Bucket)

```yaml
# chart_shapes/bucket.yaml
id: "bucket"
name: "Bucket"
pattern_type: "chart_shape"
definition_criteria: "All planets within 180° except one planet on the opposite side"
keywords: ["focused purpose", "channeling", "one-pointedness", "specialization", "mission"]
description: |
  The Bucket pattern (also called the Bucket with a Handle) occurs when all planets
  except one are grouped within half of the chart, with the singleton planet (the handle)
  on the opposite side. This creates a shape resembling a bucket with a handle.
interpretation: |
  With a Bucket shape, the handle planet becomes a focal point of tremendous significance.
  It represents a channel through which the energies of all other planets are directed
  and expressed. The handle planet often indicates a special mission, talent, or purpose
  that provides focus and direction for the entire personality.
  
  People with this pattern tend to have a sense of specific purpose or specialized talent.
  They may be highly focused on particular goals or areas of life represented by the handle
  planet and its house placement. The house and sign placement of the handle planet show
  where and how this focused energy is directed.
```

## Templates

### Planet Template

```yaml
# Template for a new planet
id: "PLANET_ID"
name: "PLANET_NAME"
type: "planet"
keywords: []
description: |
  Description here.
mythology: |
  Mythology here.
psychology: |
  Psychological meaning here.
```

### Planet in Sign Template

```yaml
# Template for planet in sign
id: "PLANET_ID_in_SIGN_ID"
planet: "PLANET_NAME"
sign: "SIGN_NAME"
keywords: []
levels:
  level_1: "TECHNICAL DESCRIPTION"
  level_2: "BASIC MEANING"
  level_3: "PSYCHOLOGICAL INSIGHT"
  level_4: "LIFE EXPRESSION"
  level_5: "SPIRITUAL/EVOLUTIONARY CONTEXT"
traditions:
  modern: "MODERN INTERPRETATION"
  traditional: "TRADITIONAL INTERPRETATION"
  psychological: "PSYCHOLOGICAL INTERPRETATION"
```
