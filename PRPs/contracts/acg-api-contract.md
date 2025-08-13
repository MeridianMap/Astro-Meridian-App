# ACG API Contract

Feature: Astrocartography (ACG)

Task: Create detailed API contract specification for backend/frontend coordination

1. Define RESTful endpoints:

```yaml
Base URL: /api/v1/acg

Endpoints:
- POST /api/v1/acg/lines
  Description: Calculate and return all ACG lines for a given chart
  Body: ACGLinesRequest
  Response: GeoJSON FeatureCollection (ACGLinesResponse)

- POST /api/v1/acg/batch
  Description: Batch calculation of ACG lines for multiple charts
  Body: ACGBatchRequest
  Response: ACGBatchResponse (array of FeatureCollections with correlation ids)

- GET /api/v1/acg/features
  Description: List supported line types, aspects, bodies, and defaults
  Response: ACGFeaturesResponse

- GET /api/v1/acg/schema
  Description: Return metadata schema used in Feature properties
  Response: JSON Schema document

- POST /api/v1/acg/animate
  Description: Calculate time-based frames for animation (e.g., progressions/transits)
  Body: ACGAnimateRequest
  Response: ACGAnimateResponse (sequence of FeatureCollections)
```

2. Define request/response DTOs:

```typescript
// Shared types
interface ACGBody {
  id: string;               // e.g., "Sun", "Venus", "Regulus"
  type: "planet" | "asteroid" | "lot" | "node" | "fixed_star" | "point";
  number?: number;          // Swiss Ephemeris index (optional)
}

interface ACGOptions {
  line_types?: ("AC" | "DC" | "MC" | "IC")[];                  // defaults: all
  aspects?: ("conjunction" | "sextile" | "square" | "trine" | "opposition")[]; // to AC/MC lines
  include_parans?: boolean;                                         // default: true
  include_fixed_stars?: boolean;                                    // default: false
  orb_deg?: number;                                                 // default: 1.0
  flags?: number;                                                   // Swiss Ephemeris flags
}

interface ACGNatalData {
  birthplace_lat?: number;  // -90..90
  birthplace_lon?: number;  // -180..180
  birthplace_alt_m?: number; // meters (optional)
  houses_system?: string;    // e.g., "placidus"
}

// Requests
interface ACGLinesRequest {
  epoch: string;            // ISO 8601 UTC
  jd?: number;              // Optional Julian Day override
  bodies?: ACGBody[];       // Defaults to standard set
  options?: ACGOptions;
  natal?: ACGNatalData;     // Optional; used for metadata enrichment
}

interface ACGBatchRequest {
  requests: Array<ACGLinesRequest & { correlation_id?: string }>; // per-chart correlation id
}

interface ACGAnimateRequest {
  epoch_start: string;      // ISO 8601 UTC
  epoch_end: string;        // ISO 8601 UTC
  step_minutes: number;     // frame step in minutes
  bodies?: ACGBody[];
  options?: ACGOptions;
  natal?: ACGNatalData;
}

// Responses
// GeoJSON FeatureCollection where feature.properties adhere to ACG metadata schema
interface ACGLinesResponse {
  type: "FeatureCollection";
  features: Array<{
    type: "Feature";
    geometry: { type: "LineString" | "MultiLineString"; coordinates: number[][] | number[][][] };
    properties: {
      id: string;
      type: string;
      number?: number;
      epoch: string;
      jd: number;
      gmst: number;
      obliquity: number;
      coords: { ra: number; dec: number; lambda: number; beta: number; distance?: number; speed?: number };
      line: { angle: number; aspect?: string; line_type: string; method: string; segment_id?: string; orb?: number };
      natal?: { dignity?: string; house?: string | number; retrograde?: boolean; sign?: string; element?: string; modality?: string; aspects?: any[] };
      flags?: number;
      se_version?: string;
      source: string; // "Meridian-ACG"
      calculation_time_ms: number;
      color?: string; style?: string; z_index?: number; hit_radius?: number;
      custom?: Record<string, any>;
    };
  }>;
}

interface ACGBatchResponse {
  results: Array<{ correlation_id?: string; response: ACGLinesResponse }>;
}

interface ACGFeaturesResponse {
  bodies: ACGBody[];
  line_types: string[];
  aspects: string[];
  defaults: Required<ACGOptions>;
  metadata_keys: string[]; // list of properties keys in feature.properties
}

interface ACGAnimateResponse {
  frames: Array<{ epoch: string; jd: number; data: ACGLinesResponse }>;
}
```

3. Define error responses:

```json
{
  "timestamp": "2025-08-13T10:30:00Z",
  "status": 400,
  "error": "Bad Request",
  "message": "Validation failed",
  "path": "/api/v1/acg/lines",
  "errors": [
    { "field": "epoch", "message": "Must be ISO 8601 UTC" }
  ]
}
```

4. Define validation rules:
- Backend: Pydantic models, strict types, geographic bounds
- Frontend: Matching Zod schemas

```
epoch: required ISO 8601 (UTC)
jd: optional, positive number
birthplace_lat: -90..90
birthplace_lon: -180..180
step_minutes: 1..43200
orb_deg: 0..5
bodies: non-empty if provided
```

5. Define status codes:
- 200: OK (GET/POST)
- 201: Created (reserved; not used here)
- 400: Bad Request (validation)
- 404: Not Found (unknown body)
- 409: Conflict (incompatible params)
- 500: Internal Server Error

6. Integration requirements:
- CORS: Allow frontend origin
- Content-Type: application/json
- Authentication: Bearer token (if needed)
- Responses compressed (gzip/br)
- Use orjson for serialization where possible

7. Backend implementation notes:

```python
# FastAPI suggested patterns
# - Define Pydantic models mirroring DTOs above
# - Use Response(media_type="application/geo+json") for GeoJSON
# - Stream large FeatureCollections if needed
# - Cache per (epoch,jd,bodies,options) key
```

8. Frontend implementation notes:
```typescript
// Zod schemas mirror DTOs
// API client with baseURL /api/v1/acg
// TanStack Query hooks for lines, batch, animate, features
// Map layers: each feature line type as a separate overlay with styling from properties
```

Save this contract as: PRPs/contracts/acg-api-contract.md

Share this file between backend and frontend teams for alignment.
