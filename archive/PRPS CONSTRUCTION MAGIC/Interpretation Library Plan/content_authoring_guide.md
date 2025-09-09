# Meridian Interpretation Library: Content Authoring Guide

This guide provides instructions for astrologers and content authors to contribute to the Meridian Interpretation Library without requiring programming knowledge.

## Getting Started

### Content Organization

The interpretation content is organized in a simple folder structure:

```
interpretation-content/
├── base-elements/         # Basic astrological elements
├── combinations/          # Combinations of elements
└── patterns/              # Chart patterns and formations
```

Each folder contains YAML or Markdown files that you can edit directly.

### Working with Content Files

#### Option 1: Direct Editing (Easiest)

1. Navigate to the appropriate folder
2. Open the YAML or Markdown file in any text editor
3. Edit the content following the existing format
4. Save the file

#### Option 2: Git Workflow (Collaborative)

1. Clone the repository
2. Create a branch for your changes
3. Make your edits
4. Commit with a descriptive message
5. Push and create a pull request for review

## Content Templates

### Planet Template

```yaml
# planets/mars.yaml
id: "mars"
name: "Mars"
type: "planet"
keywords: ["action", "energy", "assertion", "drive", "courage"]
description: |
  Mars represents our energy, drive, and how we assert ourselves.
  It shows what motivates us to take action and how we pursue our desires.
mythology: |
  Mars was the Roman god of war, representing courage, aggression, and military prowess.
  The Greek equivalent is Ares.
psychology: |
  In psychological terms, Mars represents our will to act, our assertive drive,
  and how we express anger and pursue our desires.
```

### Planet in Sign Template

```yaml
# planet_in_sign/mars_in_aries.yaml
id: "mars_in_aries"
planet: "Mars"
sign: "Aries"
keywords: ["assertive", "pioneering", "energetic", "impulsive", "courageous"]
levels:
  level_1: "Mars is in Aries."
  level_2: "Your energy and drive are expressed in a direct, assertive manner."
  level_3: "You approach challenges head-on with courage and determination. You may act first and think later, as your impulses are strong and immediate."
  level_4: "You excel in situations requiring initiative, competition, and quick action. Physical activities and sports can be excellent outlets for your abundant energy."
  level_5: "Your soul purpose involves learning to use your warrior energy in service of pioneering new paths while mastering impulse control and patience."
traditions:
  modern: "Mars in its home sign grants you natural assertiveness and leadership qualities."
  traditional: "Mars is in its domicile, bringing great strength to your capacity for action and courage."
  psychological: "The ego's drive finds pure, unfiltered expression, creating a personality that's direct and unambiguous in pursuing desires."
```

## Writing Guidelines

### Tone & Style

- Use neutral, non-judgmental language
- Balance between specific and general statements
- Avoid absolute predictions
- Use empowering rather than limiting language

### Structure Patterns

- **Problem-solution format**: "While you may face challenges with X, your strengths in Y allow you to..."
- **Strength-challenge-growth format**: "Your strengths include X, challenges involve Y, and growth comes through Z"
- **Manifestation across life areas**: "This influence affects your career by X, relationships by Y, and personal growth by Z"

### Ethical Guidelines

- No health diagnoses
- No absolute financial predictions
- Ethical relationship advice
- Cultural sensitivity

## Content Validation

After editing content, run the validation script to ensure your content follows the required format:

```bash
./validate_content.sh
```

This will check for:
- Required fields
- Proper formatting
- Consistency with other content

## Example Content Workflow

1. **Identify content to create**: For example, "Mars in Aries" interpretation
2. **Find the appropriate template**: Use the planet_in_sign template
3. **Create or edit the file**: Create `planet_in_sign/mars_in_aries.yaml`
4. **Fill in the content**: Follow the template structure
5. **Validate your content**: Run the validation script
6. **Submit your content**: Commit and push, or notify the content manager

## Contact & Support

For questions or assistance with content authoring:
- Email: content@meridian.example.com
- Slack: #content-authoring channel
