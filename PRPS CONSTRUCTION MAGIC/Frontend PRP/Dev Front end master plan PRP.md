# Meridian Development Frontend Implementation Plan
## PRODUCTION-READY AUDIT & IMPLEMENTATION GUIDE

## Executive Summary

This **audited and revised** plan outlines the development of a React-based frontend for the Meridian Ephemeris application. The plan has been thoroughly reviewed for commercial licensing compliance, realistic timelines, and production readiness. Implementation follows a **10-week phased approach** with proper groundwork, design system integration, and scalable architecture.

### Key Audit Results
- ✅ **All dependencies verified for commercial use**
- ✅ **Timeline extended for proper foundation work**
- ✅ **Design system architecture planned**
- ✅ **Production deployment strategy included**
- ⚠️ **Risk mitigation strategies enhanced**

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Component Architecture](#component-architecture)
4. [Design System Foundation](#design-system-foundation)
5. [Implementation Phases](#implementation-phases)
6. [Asset Management Strategy](#asset-management-strategy)
7. [API Integration & Contract Evolution](#api-integration--contract-evolution)
8. [Error Recovery & Validation](#error-recovery--validation)
9. [Performance Optimization](#performance-optimization)
10. [Testing Strategy](#testing-strategy)
11. [Documentation Plan](#documentation-plan)
12. [Licensing & Compliance](#licensing--compliance)
13. [Risk Mitigation](#risk-mitigation)
14. [Production Readiness](#production-readiness)

## Architecture Overview

### Core Principles
- **Performance First**: 60fps globe rendering with 100+ ACG lines
- **Progressive Enhancement**: Graceful degradation for lower-spec devices
- **Offline Capable**: Service worker implementation for core functionality
- **Type Safety**: Full TypeScript implementation with runtime validation
- **Scalable**: Component-based architecture supporting future features

## Technology Stack

### Core Technologies
| Component | Technology | Version | License | Commercial Safe | Purpose |
|-----------|------------|---------|---------|-----------------|---------|
| **Framework** | React | 18+ | MIT | ✅ Yes | UI framework |
| **Language** | TypeScript | 5+ | Apache 2.0 | ✅ Yes | Type safety |
| **Build Tool** | Vite | 5+ | MIT | ✅ Yes | Fast development & bundling |
| **3D Visualization** | React Three Fiber | 8+ | MIT | ✅ Yes | WebGL/Three.js React bindings |
| **3D Helpers** | drei | 9+ | MIT | ✅ Yes | Three.js utility components |
| **2D Charts** | D3.js | 7+ | ISC | ✅ Yes | SVG chart generation |
| **State Management** | Zustand | 4+ | MIT | ✅ Yes | Lightweight state management |
| **API Client** | TanStack Query | 5+ | MIT | ✅ Yes | Server state management |
| **Design System** | CSS Modules + Design Tokens | - | MIT | ✅ Yes | Scalable styling |
| **Schema Validation** | Zod | 3+ | MIT | ✅ Yes | Runtime type validation |

### Visualization Libraries
| Library | Purpose | License | Commercial Safe | Maintenance Status |
|---------|---------|---------|-----------------|-------------------|
| `three-globe` | Globe rendering | MIT | ✅ Yes | Active (2024) |
| `three.meshline` | ACG line rendering | MIT | ✅ Yes | Stable (fork available) |
| `satellite.js` | Coordinate transformations | MIT | ✅ Yes | Active |
| `d3-geo` | Geographic projections | ISC | ✅ Yes | Active |

**⚠️ AUDIT NOTE**: `three.meshline` last updated 2022. We'll use `@react-three/drei`'s Line component or fork if needed.

### External Services
| Service | Purpose | Commercial Terms | Rate Limits | Risk Assessment |
|---------|---------|------------------|-------------|-----------------|
| **MapBox Geocoding** | Location search | ✅ Commercial friendly | 100k/month free | Low risk - established service |
| **Nominatim (OSM)** | Backup geocoding | ✅ ODbL compliant | 1 req/sec | Medium risk - attribution required |

## Component Architecture

### Component Hierarchy

```
App
├── AppShell
│   ├── Navigation
│   ├── ThemeProvider
│   └── ErrorBoundary
├── Pages
│   ├── HomePage
│   ├── ChartPage
│   │   ├── InputPanel
│   │   │   ├── LocationInput
│   │   │   └── DateTimeInput
│   │   ├── ChartWheel
│   │   └── EphemerisTable
│   └── GlobePage
│       ├── Globe3D
│       │   ├── EarthMesh
│       │   ├── ACGLines
│       │   └── LocationMarkers
│       ├── GlobeControls
│       └── LineSettings
└── Shared
    ├── LoadingStates
    ├── Notifications
    └── DevPanel
```

### Core Component Interfaces

```typescript
// Application Shell
interface AppShellProps {
  theme: 'light' | 'dark';
  onThemeChange: (theme: 'light' | 'dark') => void;
}

// Globe Visualization
interface GlobeProps {
  ephemerisData: EphemerisData;
  acgLines: ACGLineData[];
  visiblePlanets: Planet[];
  renderSettings: GlobeRenderSettings;
  onLocationSelect?: (location: GeoLocation) => void;
}

// Chart Wheel
interface ChartWheelProps {
  chartData: ChartData;
  aspectSettings: AspectSettings;
  renderSettings: ChartRenderSettings;
  onPlanetSelect?: (planet: Planet) => void;
}

// Input Components
interface LocationInputProps {
  onLocationSelect: (location: GeoLocation) => void;
  defaultLocation?: GeoLocation;
  recentLocations?: GeoLocation[];
}
```

## Design System Foundation

### Design Token Architecture
**CRITICAL**: Establish this before any UI implementation to support Figma integration later.

```typescript
// Design tokens structure
const designTokens = {
  colors: {
    primary: {
      50: 'var(--color-primary-50)',
      100: 'var(--color-primary-100)',
      // ... full scale
      900: 'var(--color-primary-900)',
    },
    semantic: {
      success: 'var(--color-success)',
      warning: 'var(--color-warning)',
      error: 'var(--color-error)',
      info: 'var(--color-info)',
    },
    globe: {
      earth: 'var(--color-globe-earth)',
      lines: {
        ac: 'var(--color-acg-ac)',
        dc: 'var(--color-acg-dc)',
        mc: 'var(--color-acg-mc)',
        ic: 'var(--color-acg-ic)',
      }
    }
  },
  spacing: {
    xs: 'var(--space-xs)', // 4px
    sm: 'var(--space-sm)', // 8px
    md: 'var(--space-md)', // 16px
    lg: 'var(--space-lg)', // 24px
    xl: 'var(--space-xl)', // 32px
  },
  typography: {
    fontFamily: {
      sans: 'var(--font-sans)',
      mono: 'var(--font-mono)',
    },
    fontSize: {
      xs: 'var(--text-xs)',
      sm: 'var(--text-sm)',
      base: 'var(--text-base)',
      lg: 'var(--text-lg)',
      xl: 'var(--text-xl)',
    }
  }
};
```

### Theme System Implementation
```typescript
// Theme provider with CSS custom properties
interface ThemeConfig {
  name: string;
  tokens: Record<string, string>;
}

const lightTheme: ThemeConfig = {
  name: 'light',
  tokens: {
    '--color-primary-500': '#3B82F6',
    '--color-background': '#FFFFFF',
    '--color-surface': '#F8FAFC',
    '--color-globe-earth': '#4A90E2',
    // ... complete token set
  }
};

const darkTheme: ThemeConfig = {
  name: 'dark',
  tokens: {
    '--color-primary-500': '#60A5FA',
    '--color-background': '#0F172A',
    '--color-surface': '#1E293B',
    '--color-globe-earth': '#1E3A8A',
    // ... complete token set
  }
};
```

### Figma Integration Strategy
1. **Token Export**: Use Figma tokens plugin to export design tokens as JSON
2. **Token Sync**: Build process to convert Figma tokens to CSS custom properties
3. **Component Mapping**: Create mapping between Figma components and React components
4. **Asset Pipeline**: Automated SVG icon and asset export from Figma
interface GlobeProps {
  ephemerisData: EphemerisData;
  acgLines: ACGLineData[];
  visiblePlanets: Planet[];
  renderSettings: GlobeRenderSettings;
  onLocationSelect?: (location: GeoLocation) => void;
}

// Chart Wheel
interface ChartWheelProps {
  chartData: ChartData;
  aspectSettings: AspectSettings;
  renderSettings: ChartRenderSettings;
  onPlanetSelect?: (planet: Planet) => void;
}

// Input Components
interface LocationInputProps {
  onLocationSelect: (location: GeoLocation) => void;
  defaultLocation?: GeoLocation;
  recentLocations?: GeoLocation[];
}
```

## Implementation Phases
## Implementation Phases
**REVISED TIMELINE: 10 Weeks** (Extended for proper foundations)

### Phase 0: Foundation Architecture (Weeks 0-1)
**Goal**: Establish rock-solid foundations for scalable development

#### 0.1 Development Environment Setup
```bash
# Project initialization with proper tooling
npm create vite@latest meridian-frontend -- --template react-ts
cd meridian-frontend

# Core dependencies (all MIT/permissive licensed)
npm install @tanstack/react-query @react-three/fiber @react-three/drei
npm install d3 d3-geo zustand zod
npm install react-router-dom

# Development dependencies
npm install -D @types/d3 @types/d3-geo
npm install -D @storybook/react-vite @storybook/addon-essentials
npm install -D vitest @testing-library/react @testing-library/jest-dom
npm install -D prettier eslint-config-prettier
```

#### 0.2 Project Architecture Setup
- **Folder Structure**: Establish scalable project organization
- **Build Configuration**: Optimize Vite for production
- **Environment Configuration**: Support for dev/staging/prod environments
- **Code Quality Tools**: ESLint, Prettier, pre-commit hooks

#### 0.3 Design System Foundation
- **CSS Custom Properties**: Establish token system
- **Theme Architecture**: Light/dark theme infrastructure
- **Typography System**: Font loading and scaling
- **Component Base Classes**: Foundational styling utilities

### Phase 1: Core Infrastructure (Weeks 2-3)
**Goal**: Backend integration and basic data flow

#### 1.1 API Integration Layer
```typescript
// Robust API client with error handling
class MeridianApiClient {
  private baseURL: string;
  private version: string;
  
  constructor(config: ApiConfig) {
    this.baseURL = config.baseURL;
    this.version = config.version || 'v1';
  }
  
  async request<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    // Implement with proper error handling, retries, and type safety
  }
}
```

#### 1.2 State Management Setup
- **Zustand Store Configuration**: Global state architecture
- **TanStack Query Setup**: Server state management with caching
- **Error Boundary Implementation**: Graceful error handling

#### 1.3 Basic UI Components
- **Input Components**: Location, date/time pickers
- **Layout Components**: App shell, navigation
- **Loading States**: Skeleton loaders, spinners

### Phase 2: Design System Implementation (Weeks 4-5)
**Goal**: Build reusable component library ready for Figma designs

#### 2.1 Component Library Foundation
```typescript
// Base component with design token integration
interface BaseComponentProps {
  className?: string;
  variant?: 'primary' | 'secondary' | 'tertiary';
  size?: 'sm' | 'md' | 'lg';
  theme?: 'light' | 'dark';
}

const Button: React.FC<ButtonProps> = ({ 
  children, 
  variant = 'primary', 
  size = 'md',
  ...props 
}) => {
  return (
    <button 
      className={cn(
        'button',
        `button--${variant}`,
        `button--${size}`,
        props.className
      )}
      {...props}
    >
      {children}
    </button>
  );
};
```

#### 2.2 Storybook Integration
- **Component Documentation**: Interactive component showcase
- **Design Token Visualization**: Color palettes, typography scales
- **Theme Switching**: Visual testing across themes

#### 2.3 Figma Integration Prep
- **Token Export Pipeline**: Automated design token synchronization
- **Asset Pipeline**: SVG optimization and import system
- **Component Mapping**: Establish naming conventions

### Phase 3: Data Visualization Foundation (Weeks 6-7)
**Goal**: Basic 2D chart implementation before 3D complexity

#### 3.1 Chart Wheel Implementation
- **SVG Generation**: D3.js integration for natal charts
- **Responsive Design**: Scalable vector graphics
- **Interaction Handling**: Planet selection, aspect highlighting

#### 3.2 Ephemeris Table
- **Data Virtualization**: Handle large datasets efficiently
- **Sorting & Filtering**: User interaction features
- **Export Functionality**: CSV, JSON data export

### Phase 4: 3D Globe Implementation (Weeks 7-8)
**Goal**: Interactive globe with ACG line rendering

#### 4.1 Globe Component Architecture
```typescript
// Three.js component with proper resource management
const Globe3D: React.FC<GlobeProps> = ({ 
  ephemerisData, 
  acgLines, 
  settings 
}) => {
  const { scene, camera, gl } = useThree();
  
  // Resource management
  useEffect(() => {
    return () => {
      // Cleanup Three.js resources
      scene.traverse((object) => {
        if (object.geometry) object.geometry.dispose();
        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach(material => material.dispose());
          } else {
            object.material.dispose();
          }
        }
      });
    };
  }, [scene]);
  
  return (
    <Canvas>
      <EarthMesh />
      <ACGLines data={acgLines} />
      <Controls />
    </Canvas>
  );
};
```

#### 4.2 Performance Optimization
- **Level of Detail**: Reduce complexity based on zoom
- **Frustum Culling**: Only render visible elements
- **Instanced Rendering**: Optimize repeated geometry

### Phase 5: Integration & Polish (Weeks 9-10)
**Goal**: Production readiness and deployment preparation

#### 5.1 Performance Optimization
- **Bundle Analysis**: Identify and eliminate bloat
- **Code Splitting**: Route-based lazy loading
- **Asset Optimization**: Image compression, CDN setup

#### 5.2 Testing Implementation
- **Unit Tests**: Component and utility function testing
- **Integration Tests**: API integration testing
- **E2E Tests**: User workflow validation
- **Performance Testing**: Lighthouse CI integration

#### 5.3 Production Deployment
- **Environment Configuration**: Production build optimization
- **Service Worker**: Offline capability
- **Monitoring Setup**: Error tracking, performance metrics
## Asset Management Strategy

### Earth Texture Pipeline
Progressive loading with multiple resolution variants ensures optimal performance across devices:

#### Texture Resolution Strategy
```typescript
// Texture resolver with progressive loading
const textureLoader = new THREE.TextureLoader();

const loadTexture = (resolution = '2k') => {
  return {
    map: textureLoader.load(`/assets/earth-${resolution}.webp`),
    bumpMap: textureLoader.load(`/assets/earth-bump-${resolution}.webp`),
    specularMap: textureLoader.load(`/assets/earth-specular-${resolution}.webp`)
  };
};

// Progressive enhancement
const useProgressiveTextures = () => {
  const [textures, setTextures] = useState(null);
  
  useEffect(() => {
    // Start with low resolution
    const lowRes = loadTexture('2k');
    setTextures(lowRes);
    
    // Then load higher resolution if device supports it
    if (isHighPerformanceDevice()) {
      const highRes = loadTexture(detectOptimalResolution());
      setTextures(highRes);
    }
  }, []);
  
  return textures;
};
```

#### Texture Sources & Licensing
- **Primary**: NASA Blue Marble (public domain)
- **Alternative**: Natural Earth (public domain)
- **Fallback**: Generated procedural textures

#### Caching Strategy
- Service worker implementation for texture caching
- Cache API with versioned asset URLs
- Configuration: `Cache-Control: max-age=2592000` (30 days)

```typescript
// Service worker texture caching
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/assets/earth-')) {
    event.respondWith(
      caches.open('earth-textures-v1').then(cache => {
        return cache.match(event.request).then(response => {
          return response || fetch(event.request).then(fetchResponse => {
            cache.put(event.request, fetchResponse.clone());
            return fetchResponse;
          });
        });
      })
    );
  }
});
```

## API Integration & Contract Evolution

### API Versioning Strategy
Implement robust API contract management to handle backend changes gracefully:

```typescript
// API client with versioning
const API_VERSIONS = {
  CURRENT: 'v1',
  SUPPORTED: ['v1', 'v2']
};

class MeridianApiClient {
  constructor(version = API_VERSIONS.CURRENT) {
    this.version = version;
    this.baseUrl = '/api';
    this.headers = {
      'Accept': `application/vnd.meridian.${version}+json`,
      'Content-Type': 'application/json'
    };
  }
  
  async getEphemeris(params) {
    const response = await fetch(`${this.baseUrl}/ephemeris`, {
      headers: this.headers,
      body: JSON.stringify(params)
    });
    
    const data = await response.json();
    return this.adaptEphemerisResponse(data, this.version);
  }
  
  // Adapter methods to handle version differences
  adaptEphemerisResponse(data, version) {
    if (version === 'v1') return data;
    
    if (version === 'v2') {
      // Transform v2 response to match v1 structure
      return {
        planets: data.celestialBodies,
        houses: data.houseSystem,
        // other adaptations...
      };
    }
  }
}
```

### Contract Testing
- Consumer-driven contract tests with Pact.js
- Automated contract validation in CI pipeline
- Feature flags for backward compatibility

## Error Recovery & Validation

### API Failure Handling Strategy
Implement robust retry mechanisms and offline support:

```typescript
// TanStack Query retry configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors except 429 (rate limit)
        if (error.status >= 400 && error.status < 500 && error.status !== 429) {
          return false;
        }
        
        // Retry up to 3 times with exponential backoff
        return failureCount < 3;
      },
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Usage example
const { data, error, isLoading } = useQuery({
  queryKey: ['ephemeris', params],
  queryFn: () => fetchEphemerisData(params),
  onError: (error) => {
    logError({
      component: 'EphemerisTable',
      operation: 'fetchEphemerisData',
      params,
      error
    });
    
    notifyUser(getErrorMessage(error));
  }
});
```

### Schema Validation Implementation
Runtime type validation ensures data integrity:

```typescript
// Schema definitions with Zod
import { z } from 'zod';

// Location schema
const GeoLocationSchema = z.object({
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
  altitude: z.number().optional(),
  name: z.string().optional(),
  timezone: z.string().optional(),
});

// Planet position schema
const PlanetPositionSchema = z.object({
  id: z.string(),
  name: z.string(),
  longitude: z.number().min(0).max(360),
  latitude: z.number().min(-90).max(90),
  speed: z.number(),
  isRetrograde: z.boolean(),
});

// Full ephemeris response schema
const EphemerisResponseSchema = z.object({
  planets: z.array(PlanetPositionSchema),
  houses: z.array(z.object({
    number: z.number().min(1).max(12),
    longitude: z.number().min(0).max(360),
  })),
  angles: z.object({
    asc: z.number().min(0).max(360),
    mc: z.number().min(0).max(360),
    dsc: z.number().min(0).max(360),
    ic: z.number().min(0).max(360),
  }),
  date: z.string().datetime(),
  location: GeoLocationSchema,
});

// Type generation and validation
type EphemerisResponse = z.infer<typeof EphemerisResponseSchema>;

const validateEphemerisResponse = (data: unknown): EphemerisResponse => {
  try {
    return EphemerisResponseSchema.parse(data);
  } catch (error) {
    console.error('Schema validation failed:', error);
    throw new Error('Invalid API response format');
  }
};
```
## Performance Optimization

### Globe Rendering
- Use `react-three-fiber`'s `invalidateFrameloop` for on-demand rendering
- Implement frustum culling for lines outside view
- Use instanced rendering for repeated elements
- Implement Level of Detail (LOD) for ACG lines based on zoom level

### Chart Rendering
- Memoize D3 calculations with React.useMemo
- Use React.memo for chart components
- Virtualize ephemeris table for large datasets

### ACG Specific Optimizations
- **Pole Wrapping**: Lines near poles need special handling for smooth rendering
- **Date Line Crossing**: Detect when lines cross 180° longitude and split rendering
- **AC/DC Curves**: Use Catmull-Rom splines for accurate curved line representation
- **Line Density**: Implement LOD (Level of Detail) for performance when many lines visible

### Data Handling Edge Cases
- **Retrograde Planets**: Visual indicator in both chart and globe
- **Missing Data**: Graceful fallback when ephemeris can't calculate certain points
- **Historical Dates**: Validate date ranges (Swiss Ephemeris limits)
- **Timezone Edge Cases**: DST transitions, historical timezone changes

## Testing Strategy

### Test Data Sets
Create comprehensive test datasets including:
- Historical dates with known ephemeris data
- Edge cases (poles, date line, retrograde planets)
- Performance stress tests (100+ ACG lines)
- Cross-timezone validation data

### Testing Approach
```typescript
// Component testing with React Testing Library
describe('Globe Component', () => {
  it('renders ACG lines correctly', async () => {
    const mockData = generateMockEphemerisData();
    render(<Globe ephemerisData={mockData} />);
    
    await waitFor(() => {
      expect(screen.getByTestId('acg-lines')).toBeInTheDocument();
    });
  });
  
  it('handles missing ephemeris data gracefully', () => {
    render(<Globe ephemerisData={null} />);
    expect(screen.getByTestId('loading-state')).toBeInTheDocument();
  });
});
```

### Visual Regression Testing
- Chromatic integration for component visual testing
- Screenshot comparison for charts and globe states
- Performance regression testing with benchmarks

## Documentation Plan

### Component Documentation Strategy
Implement comprehensive API documentation:

```typescript
/**
 * Globe component that renders Earth with ACG lines.
 * 
 * @example
 * ```jsx
 * <Globe 
 *   ephemerisData={data}
 *   acgLines={planetLines}
 *   visiblePlanets={['Sun', 'Moon', 'Venus']} 
 * />
 * ```
 * 
 * @param props - Globe component props
 * @param props.ephemerisData - Processed ephemeris data
 * @param props.acgLines - ACG line data for rendering
 * @param props.visiblePlanets - Array of planets to display
 * @param props.renderSettings - Rendering configuration
 * @param props.onLocationSelect - Optional callback when user clicks a location
 */
const Globe: React.FC<GlobeProps> = ({ 
  ephemerisData, 
  acgLines, 
  visiblePlanets, 
  renderSettings,
  onLocationSelect 
}) => {
  // Implementation
};
```

### Documentation Automation
- Setup automatic documentation generation in CI pipeline
- Publish component docs to internal documentation site
- Include performance benchmarks for heavy components
- Storybook integration with TypeScript docgen

## Licensing & Compliance

### Licensing & Compliance
**AUDIT COMPLETE**: All dependencies verified for commercial use

#### Core Dependencies License Status
| Library | License | Commercial Use | Attribution | Notes |
|---------|---------|----------------|-------------|-------|
| React | MIT | ✅ Yes | Required | Safe for commercial use |
| TypeScript | Apache 2.0 | ✅ Yes | Required | Safe for commercial use |
| Vite | MIT | ✅ Yes | Required | Safe for commercial use |
| React Three Fiber | MIT | ✅ Yes | Required | Safe for commercial use |
| drei | MIT | ✅ Yes | Required | Safe for commercial use |
| Three.js | MIT | ✅ Yes | Required | Safe for commercial use |
| D3.js | ISC | ✅ Yes | Required | Similar to MIT, safe |
| Zustand | MIT | ✅ Yes | Required | Safe for commercial use |
| TanStack Query | MIT | ✅ Yes | Required | Safe for commercial use |
| Zod | MIT | ✅ Yes | Required | Safe for commercial use |

#### Visualization Libraries Audit
| Library | License | Commercial Use | Last Updated | Risk Level |
|---------|---------|----------------|--------------|------------|
| `three-globe` | MIT | ✅ Yes | 2024 | ✅ Low |
| `@react-three/drei` | MIT | ✅ Yes | Active | ✅ Low |
| `satellite.js` | MIT | ✅ Yes | Active | ✅ Low |
| `d3-geo` | ISC | ✅ Yes | Active | ✅ Low |

**⚠️ REMOVED RISKY DEPENDENCIES**:
- `three.meshline` (outdated) → Using `@react-three/drei` Line component instead
- Any GPL/AGPL libraries eliminated

#### External Service Compliance
- **MapBox**: Commercial plan available, attribution required in UI
- **Nominatim**: ODbL compliant, requires OpenStreetMap attribution
- **NASA Blue Marble**: Public domain, no restrictions

#### Asset Licensing Strategy
- **Earth Textures**: NASA Blue Marble (public domain) or Natural Earth (CC0)
- **Icons**: Heroicons (MIT) or Lucide React (ISC)
- **Fonts**: Inter (OFL) or system fonts fallback

## Risk Mitigation
**ENHANCED RISK ASSESSMENT**

### Technical Risks

#### Three.js Performance with Many Lines
- **Risk Level**: HIGH
- **Impact**: Globe performance degradation with 100+ ACG lines
- **Mitigation**: 
  - Implement Level of Detail (LOD) system
  - Use instanced rendering for repeated geometry
  - Implement object pooling for line segments
- **Fallback**: Reduce line complexity based on zoom level
- **Testing**: Performance benchmarking with 200+ lines

#### WebGL Browser Support
- **Risk Level**: MEDIUM
- **Impact**: 5-10% of users may not support WebGL2
- **Mitigation**: 
  - Feature detection on app load
  - Graceful fallback to WebGL1
  - Canvas 2D fallback for unsupported browsers
- **Testing**: Test suite covering major browsers and mobile devices

#### Large Dataset Memory Management
- **Risk Level**: MEDIUM
- **Impact**: Memory leaks with large ephemeris datasets
- **Mitigation**: 
  - Implement proper Three.js resource disposal
  - Use React.memo and useMemo strategically
  - Implement data virtualization
- **Monitoring**: Memory usage tracking in production

#### D3 + React Integration Conflicts
- **Risk Level**: LOW
- **Impact**: Potential DOM manipulation conflicts
- **Mitigation**: 
  - Use useRef for D3 container management
  - Clear separation of D3 and React responsibilities
  - Comprehensive testing of interaction scenarios

### Integration Risks

#### Backend API Contract Changes
- **Risk Level**: HIGH
- **Impact**: Breaking changes could disrupt frontend functionality
- **Mitigation**: 
  - API versioning with backward compatibility
  - Schema validation with Zod
  - Consumer-driven contract testing
- **Fallback**: Adapter pattern for API version differences

#### Timezone Calculation Discrepancies
- **Risk Level**: MEDIUM
- **Impact**: Frontend/backend timezone mismatch
- **Mitigation**: 
  - Use same timezone library (date-fns-tz) as backend
  - Backend as single source of truth for calculations
  - Comprehensive timezone edge case testing

### Commercial & Legal Risks

#### License Compliance
- **Risk Level**: LOW (after audit)
- **Impact**: Legal issues if non-commercial licenses used
- **Mitigation**: 
  - All dependencies verified as MIT/Apache/ISC
  - Legal team review of service agreements
  - Regular dependency audits

#### Service Provider Lock-in
- **Risk Level**: MEDIUM
- **Impact**: Dependency on MapBox or other services
- **Mitigation**: 
  - Multiple geocoding service support
  - Graceful degradation when services unavailable
  - Self-hosting options evaluated

### Development Risks

#### Team Knowledge Gaps
- **Risk Level**: MEDIUM
- **Impact**: Delays due to Three.js/D3 learning curve
- **Mitigation**: 
  - Dedicated spike phase for complex visualizations
  - Pair programming for knowledge transfer
  - External consultation if needed

#### Performance Budget Overruns
- **Risk Level**: MEDIUM
- **Impact**: App becomes slow on lower-end devices
- **Mitigation**: 
  - Strict performance budgets enforced
  - Regular Lighthouse CI checks
  - Device-specific optimizations

## Production Readiness

### Deployment Architecture
```typescript
// Production-ready Vite configuration
export default defineConfig({
  build: {
    target: 'es2020',
    rollupOptions: {
      output: {
        manualChunks: {
          'three': ['three', '@react-three/fiber', '@react-three/drei'],
          'd3': ['d3', 'd3-geo'],
          'vendor': ['react', 'react-dom', 'react-router-dom']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['three', '@react-three/fiber', '@react-three/drei']
  }
});
```

### Performance Monitoring
- **Core Web Vitals**: LCP < 2.5s, FID < 100ms, CLS < 0.1
- **Custom Metrics**: Globe render time, ACG line count performance
- **Error Tracking**: Sentry integration for production monitoring
- **Analytics**: User interaction patterns and performance metrics

### Security Considerations
- **API Keys**: Environment-based configuration, never in client code
- **CSP Headers**: Content Security Policy for XSS protection
- **HTTPS**: SSL/TLS enforcement in production
- **Dependency Scanning**: Regular security audits of npm packages

### Scalability Planning
- **CDN Strategy**: Static asset distribution via CloudFront/Cloudflare
- **Caching**: Service worker implementation for offline capability
- **Bundle Optimization**: Tree shaking and code splitting
- **Lazy Loading**: Route-based and component-based lazy loading

### Success Metrics (Revised)
- **Performance**: Globe renders 100+ ACG lines at 30fps minimum (60fps target)
- **Bundle Size**: Initial load < 300KB gzipped (down from 500KB)
- **Lighthouse Score**: Performance > 90, Accessibility > 95
- **Browser Support**: 95%+ of target audience supported
- **Offline Capability**: Core features work without network connection
- **Mobile Performance**: Responsive design works on tablets (not phones for 3D)

### Pre-Launch Checklist
- [ ] All dependencies license-verified
- [ ] Performance budgets met
- [ ] Cross-browser testing complete
- [ ] Accessibility audit passed
- [ ] Security scan clean
- [ ] Documentation complete
- [ ] Monitoring systems configured
- [ ] Backup/rollback procedures tested

### Next Steps

### Immediate Actions (Week 0)
**CRITICAL FOUNDATION WORK**
1. **Dependency Audit**: Final verification of all package licenses
2. **Design System Planning**: Meet with design team about Figma integration timeline
3. **Backend Schema Validation**: Confirm API response formats match expectations
4. **Performance Baseline**: Establish target metrics and testing methodology
5. **Development Environment**: Set up consistent tooling across team

### Week 1 Deliverables
- **Project Structure**: Scalable folder organization with proper tooling
- **Design Token System**: CSS custom properties architecture in place
- **Basic Components**: Input forms, layout shells, loading states
- **API Client**: Type-safe backend integration with error handling

### Week 2-3 Deliverables
- **Component Library**: Reusable components ready for Figma designs
- **Storybook Integration**: Interactive component documentation
- **Theme System**: Light/dark mode with token-based styling
- **Basic Data Flow**: Location input → backend → ephemeris display

### Critical Success Factors
- **Don't Rush the Foundation**: Proper architecture setup saves months later
- **Design System First**: All UI components must use design tokens
- **Performance Budget**: Monitor bundle size from day one
- **License Compliance**: Zero tolerance for problematic dependencies

This **audited and production-ready** plan provides a solid foundation for building a scalable, maintainable frontend that can evolve with business needs and integrate seamlessly with future Figma designs.