# Meridian Interpretation Library: Technical Implementation Guide

This guide provides technical details for developers implementing the Meridian Interpretation Library.

## System Architecture

### File-Based Content Approach (Phase 1)

The initial implementation uses a file-based content system for easy editing and management:

```
interpretation-content/
├── base-elements/
│   ├── planets/
│   ├── signs/
│   ├── houses/
│   └── aspects/
├── combinations/
│   ├── planet_in_sign/
│   ├── planet_in_house/
│   └── planet_aspect_planet/
└── patterns/
    ├── aspect_patterns/
    └── chart_shapes/
```

### Content Loading

```typescript
// Example content loading (Node.js)
import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

// Load a specific interpretation
function loadInterpretation(type, id) {
  const filePath = path.join(
    CONTENT_ROOT_DIR,
    type,
    `${id}.yaml`
  );
  
  const content = fs.readFileSync(filePath, 'utf8');
  return yaml.load(content);
}

// Load all interpretations of a type
function loadAllInterpretations(type) {
  const dirPath = path.join(CONTENT_ROOT_DIR, type);
  const files = fs.readdirSync(dirPath);
  
  return files
    .filter(file => file.endsWith('.yaml'))
    .map(file => {
      const content = fs.readFileSync(path.join(dirPath, file), 'utf8');
      return yaml.load(content);
    });
}
```

### Simple API Implementation

```typescript
// Example Express.js API
import express from 'express';
const app = express();

// Get a planet interpretation
app.get('/api/interpret/planet/:id', (req, res) => {
  try {
    const planet = loadInterpretation('base-elements/planets', req.params.id);
    res.json(planet);
  } catch (err) {
    res.status(404).json({ error: 'Planet not found' });
  }
});

// Get a planet in sign interpretation
app.get('/api/interpret/planet-in-sign/:planetId/:signId', (req, res) => {
  try {
    const { planetId, signId } = req.params;
    const interpretation = loadInterpretation(
      'combinations/planet_in_sign',
      `${planetId}_in_${signId}`
    );
    res.json(interpretation);
  } catch (err) {
    res.status(404).json({ error: 'Interpretation not found' });
  }
});

// Interpret a full chart
app.post('/api/interpret/chart', (req, res) => {
  const { chart_data, options } = req.body;
  const interpretations = interpretChart(chart_data, options);
  res.json(interpretations);
});
```

### Template Processing

```typescript
// Simple template processing
function processTemplate(template, data) {
  let result = template;
  
  // Replace variables
  for (const [key, value] of Object.entries(data)) {
    result = result.replace(new RegExp(`{${key}}`, 'g'), value);
  }
  
  // Process conditionals (simplified)
  const conditionalRegex = /{%\s*if\s+([^%]+)\s*%}([\s\S]*?){%\s*endif\s*%}/g;
  result = result.replace(conditionalRegex, (match, condition, content) => {
    return eval(`data.${condition}`) ? content : '';
  });
  
  return result;
}
```

## Database Evolution (Phase 2+)

When content volume grows large enough to justify a database:

### Migration Script

```typescript
// Example migration script (Node.js)
import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import { pool } from './db';

async function migrateContent() {
  // Migrate planets
  const planetFiles = fs.readdirSync(path.join(CONTENT_ROOT_DIR, 'base-elements/planets'));
  
  for (const file of planetFiles) {
    const content = yaml.load(fs.readFileSync(path.join(CONTENT_ROOT_DIR, 'base-elements/planets', file), 'utf8'));
    
    await pool.query(
      'INSERT INTO astrological_objects (id, name, type, keywords, description, mythology, psychology) VALUES ($1, $2, $3, $4, $5, $6, $7)',
      [content.id, content.name, 'planet', content.keywords, content.description, content.mythology, content.psychology]
    );
  }
  
  // Similar processes for other content types
}
```

### Database-Based API

```typescript
// Example database-powered API (Express.js)
app.get('/api/interpret/planet/:id', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM astrological_objects WHERE id = $1 AND type = $2',
      [req.params.id, 'planet']
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Planet not found' });
    }
    
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: 'Database error' });
  }
});
```

## Content Validation

Validation ensures content follows the required structure:

```typescript
// Example validation function
function validateContent(content, type) {
  const schemas = {
    'planet': {
      required: ['id', 'name', 'keywords', 'description'],
      optional: ['mythology', 'psychology']
    },
    'planet_in_sign': {
      required: ['id', 'planet', 'sign', 'keywords', 'levels'],
      optional: ['traditions']
    }
    // More schemas for other content types
  };
  
  const schema = schemas[type];
  if (!schema) {
    throw new Error(`Unknown content type: ${type}`);
  }
  
  // Check required fields
  for (const field of schema.required) {
    if (!content[field]) {
      throw new Error(`Missing required field: ${field}`);
    }
  }
  
  // Validate levels for interpretations
  if (content.levels) {
    for (let i = 1; i <= 5; i++) {
      if (!content.levels[`level_${i}`]) {
        throw new Error(`Missing level_${i} in levels`);
      }
    }
  }
  
  return true;
}
```

## Command-Line Tools

### Content Validation Tool

```bash
#!/bin/bash
# validate_content.sh

echo "Validating interpretation content..."

# Check YAML syntax
find interpretation-content -name "*.yaml" -type f -exec sh -c 'yaml-lint {}' \;

# Run deeper validation
node scripts/validate-content.js

echo "Validation complete!"
```

### Template Generator

```bash
#!/bin/bash
# generate_template.sh

TYPE=$1
ID=$2

case "$TYPE" in
  "planet")
    cat templates/planet.yaml > "interpretation-content/base-elements/planets/${ID}.yaml"
    sed -i "s/TEMPLATE_ID/${ID}/g" "interpretation-content/base-elements/planets/${ID}.yaml"
    ;;
  "planet_in_sign")
    IFS='_' read -ra PARTS <<< "$ID"
    PLANET=${PARTS[0]}
    SIGN=${PARTS[2]}
    cat templates/planet_in_sign.yaml > "interpretation-content/combinations/planet_in_sign/${ID}.yaml"
    sed -i "s/TEMPLATE_ID/${ID}/g" "interpretation-content/combinations/planet_in_sign/${ID}.yaml"
    sed -i "s/TEMPLATE_PLANET/${PLANET}/g" "interpretation-content/combinations/planet_in_sign/${ID}.yaml"
    sed -i "s/TEMPLATE_SIGN/${SIGN}/g" "interpretation-content/combinations/planet_in_sign/${ID}.yaml"
    ;;
  # More types...
esac

echo "Template generated: ${TYPE}/${ID}"
echo "Please edit the file to add your content."
```

## Implementation Guidelines

1. **Start simple**:
   - Begin with file-based approach
   - Focus on core interpretations first
   - Use simple templates

2. **Create clear directory structure**:
   - Organize by interpretation type
   - Use consistent naming conventions
   - Document structure clearly

3. **Build validation early**:
   - Create content validation tools
   - Implement automated testing
   - Document expected formats

4. **Evolve gradually**:
   - Only move to database when needed
   - Keep file-based option for editing
   - Implement migration tools

5. **Separate concerns**:
   - Content storage
   - Content processing
   - Presentation logic

## Next Steps

1. Set up the basic directory structure
2. Create templates for each content type
3. Develop simple content loading functions
4. Build basic API endpoints
5. Implement template processing
6. Create content validation tools
7. Document the system for both technical and non-technical users
