# System Architecture

The Meridian Ephemeris API is built with a modern, scalable architecture designed for high-performance astrological calculations.

## High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WebApp[Web Applications]
        Mobile[Mobile Apps]
        SDK[Client SDKs]
        Direct[Direct HTTP Calls]
    end
    
    subgraph "API Gateway"
        Gateway[Load Balancer/Gateway]
        RateLimit[Rate Limiting]
        Auth[Authentication]
    end
    
    subgraph "Application Layer"
        FastAPI[FastAPI Application]
        Validation[Input Validation]
        Service[Ephemeris Service]
    end
    
    subgraph "Core Engine"
        Engine[Swiss Ephemeris Engine]
        Cache[Intelligent Cache]
        Parallel[Parallel Processing]
    end
    
    subgraph "Data Layer"
        Ephemeris[Ephemeris Data Files]
        Config[Configuration]
        Logs[Logging System]
    end
    
    WebApp --> Gateway
    Mobile --> Gateway
    SDK --> Gateway
    Direct --> Gateway
    
    Gateway --> RateLimit
    RateLimit --> Auth
    Auth --> FastAPI
    
    FastAPI --> Validation
    Validation --> Service
    Service --> Engine
    
    Engine --> Cache
    Engine --> Parallel
    Engine --> Ephemeris
    
    Cache --> Config
    Parallel --> Config
    
    FastAPI --> Logs
    Service --> Logs
    Engine --> Logs
```

## Component Overview

### Client Layer

**Web Applications & Mobile Apps**
- Frontend applications consuming the API
- Real-time chart calculations and visualizations
- User interface for astrological analysis

**Client SDKs**
- Type-safe wrappers for Python, TypeScript, Go
- Automatic error handling and retry logic
- Built from OpenAPI specification

**Direct HTTP Calls**
- Raw REST API access
- Maximum flexibility for custom implementations
- Suitable for any HTTP-capable programming language

### API Gateway

**Load Balancer/Gateway**
- Distributes requests across multiple application instances
- SSL termination and security headers
- Request routing and path-based routing

**Rate Limiting**
- Per-IP rate limiting (100 req/min)
- Burst protection (10 req/sec)
- Fair usage enforcement

**Authentication** *(Future)*
- API key validation
- JWT token processing
- User session management

### Application Layer

**FastAPI Application**
- Modern Python web framework
- Automatic OpenAPI documentation generation
- Built-in request/response validation
- Async request handling

**Input Validation**
- Pydantic schema validation
- Multiple input format support
- Comprehensive error reporting
- Type safety and conversion

**Ephemeris Service**
- Business logic layer
- Coordinate system conversions
- Request preprocessing
- Response formatting

### Core Engine

**Swiss Ephemeris Engine**
- Professional astronomical calculations
- High-precision planetary positions
- Multiple house system support
- Fixed star calculations

**Intelligent Cache**
- LRU (Least Recently Used) caching
- Calculation result memoization
- Configurable TTL (Time To Live)
- Memory-efficient storage

**Parallel Processing**
- Concurrent planet calculations
- Thread-safe operations
- Optimized for multi-core systems
- Reduces calculation time

### Data Layer

**Ephemeris Data Files**
- Swiss Ephemeris binary files
- Planetary motion data
- Fixed star catalogs
- Time zone databases

**Configuration**
- Environment-based settings
- Cache configuration
- Logging levels
- Feature flags

**Logging System**
- Structured JSON logging
- Request/response tracking
- Performance metrics
- Error monitoring

## Data Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant Validation
    participant Service
    participant Cache
    participant Engine
    participant SwissEph as Swiss Ephemeris
    
    Client->>API: POST /ephemeris/natal
    API->>Validation: Validate request
    
    alt Validation Success
        Validation->>Service: Process request
        Service->>Cache: Check cache
        
        alt Cache Hit
            Cache-->>Service: Return cached result
        else Cache Miss
            Service->>Engine: Calculate chart
            Engine->>SwissEph: Get planet positions
            SwissEph-->>Engine: Return coordinates
            Engine->>SwissEph: Calculate houses
            SwissEph-->>Engine: Return house cusps
            Engine-->>Service: Return chart data
            Service->>Cache: Store result
        end
        
        Service-->>API: Return chart data
        API-->>Client: 200 OK + Chart JSON
    else Validation Error
        Validation-->>API: Return validation errors
        API-->>Client: 422 Unprocessable Entity
    end
```

## Performance Architecture

### Caching Strategy

The system implements a multi-level caching strategy:

```mermaid
graph LR
    Request[Incoming Request] --> L1[Memory Cache]
    L1 --> |Cache Miss| Engine[Calculation Engine]
    Engine --> SwissEph[Swiss Ephemeris]
    SwissEph --> Result[Calculation Result]
    Result --> L1
    L1 --> Response[JSON Response]
    
    subgraph "Cache Layers"
        L1[L1: Memory Cache<br/>LRU, 1000 entries<br/>TTL: 1 hour]
    end
    
    subgraph "Cache Keys"
        Key1["datetime + coordinates + house_system"]
        Key2["planet_id + julian_day"]
        Key3["house_system + latitude + longitude + datetime"]
    end
```

**Cache Characteristics:**
- **Hit Rate**: ~85% for typical usage patterns
- **Memory Usage**: ~100MB for 1000 cached calculations
- **TTL**: 1 hour (ephemeris data is static)
- **Eviction**: LRU (Least Recently Used)

### Parallel Processing

Planet calculations are parallelized for optimal performance:

```python
# Pseudo-code for parallel planet calculation
async def calculate_planets_parallel(julian_day, location):
    planet_ids = [SUN, MOON, MERCURY, VENUS, MARS, JUPITER, SATURN, URANUS, NEPTUNE, PLUTO]
    
    # Calculate planets in parallel
    tasks = [
        calculate_planet_async(planet_id, julian_day, location)
        for planet_id in planet_ids
    ]
    
    results = await asyncio.gather(*tasks)
    return dict(zip(planet_ids, results))
```

### Memory Management

```mermaid
pie title Memory Usage Distribution
    "Swiss Ephemeris Data" : 60
    "Application Code" : 15
    "Cache Storage" : 20
    "Request Processing" : 5
```

## Deployment Architecture

### Container Structure

```mermaid
graph TB
    subgraph "Docker Container"
        App[FastAPI Application]
        Python[Python 3.10 Runtime]
        SwissEph[Swiss Ephemeris Library]
        Data[Ephemeris Data Files]
    end
    
    subgraph "External Services"
        LB[Load Balancer]
        Monitor[Monitoring]
        Logs[Log Aggregation]
    end
    
    LB --> App
    App --> Monitor
    App --> Logs
```

### Scalability Considerations

**Horizontal Scaling**
- Stateless application design
- Shared cache layer (Redis) for multi-instance deployments
- Load balancing across multiple containers

**Vertical Scaling**
- CPU-intensive calculations benefit from more cores
- Memory usage scales with cache size
- I/O optimization for ephemeris data access

**Database-Free Design**
- No persistent database required
- Ephemeris data files are read-only
- Configuration via environment variables

## Security Architecture

### Input Security

```mermaid
graph LR
    Input[User Input] --> Validate[Schema Validation]
    Validate --> Sanitize[Input Sanitization]
    Sanitize --> Process[Safe Processing]
    
    Validate --> |Invalid| Reject[422 Error]
    
    subgraph "Validation Layers"
        Schema[Pydantic Schemas]
        Range[Range Checking]
        Type[Type Validation]
        Format[Format Validation]
    end
    
    Validate --> Schema
    Schema --> Range
    Range --> Type
    Type --> Format
```

**Security Features:**
- Input validation prevents injection attacks
- No SQL database = No SQL injection risk
- Rate limiting prevents DoS attacks
- CORS configuration for web security
- No sensitive data storage

### Error Security

- Stack traces hidden in production
- Sanitized error messages
- No internal path disclosure
- Logging of security events

## Monitoring and Observability

### Metrics Collection

```mermaid
graph TB
    subgraph "Application Metrics"
        Request[Request Rate]
        Latency[Response Latency]
        Errors[Error Rate]
        Cache[Cache Hit Rate]
    end
    
    subgraph "System Metrics"
        CPU[CPU Usage]
        Memory[Memory Usage]
        Disk[Disk I/O]
        Network[Network I/O]
    end
    
    subgraph "Business Metrics"
        Charts[Charts Calculated]
        PopularSystems[Popular House Systems]
        GeoDistribution[Geographic Distribution]
    end
    
    Request --> Dashboard[Monitoring Dashboard]
    Latency --> Dashboard
    Errors --> Dashboard
    Cache --> Dashboard
    
    CPU --> Dashboard
    Memory --> Dashboard
    
    Charts --> Analytics[Business Analytics]
    PopularSystems --> Analytics
    GeoDistribution --> Analytics
```

### Health Checks

Multiple health check endpoints for different deployment scenarios:

- **Liveness Probe**: `/health` - Basic service availability
- **Readiness Probe**: `/ephemeris/health` - Swiss Ephemeris readiness
- **Deep Health Check**: Validates ephemeris data integrity

### Logging Strategy

```mermaid
graph LR
    App[Application] --> Structured[Structured Logs]
    Structured --> Local[Local Files]
    Structured --> Remote[Log Aggregation]
    
    subgraph "Log Types"
        Access[Access Logs]
        Error[Error Logs]
        Performance[Performance Logs]
        Business[Business Events]
    end
    
    Structured --> Access
    Structured --> Error
    Structured --> Performance
    Structured --> Business
```

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Web Framework** | FastAPI | 0.104+ | REST API, OpenAPI generation |
| **Runtime** | Python | 3.10+ | Application runtime |
| **Validation** | Pydantic | 2.0+ | Data validation and serialization |
| **Astronomical Engine** | Swiss Ephemeris | 2.10+ | Planetary calculations |
| **HTTP Client** | httpx | 0.25+ | Async HTTP client for testing |
| **Testing** | pytest | 7.0+ | Unit and integration testing |

### Development Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Black** | Code formatting | Line length: 88 |
| **isort** | Import sorting | Profile: black |
| **flake8** | Linting | Max complexity: 10 |
| **mypy** | Type checking | Strict mode |
| **pytest-cov** | Coverage | Target: 90%+ |

### Infrastructure

| Service | Purpose | Provider |
|---------|---------|----------|
| **Container Registry** | Docker images | Docker Hub/AWS ECR |
| **Load Balancer** | Traffic distribution | AWS ALB/Cloudflare |
| **Monitoring** | Observability | Prometheus/Grafana |
| **Logging** | Log aggregation | ELK Stack/CloudWatch |
| **CI/CD** | Automation | GitHub Actions |

This architecture ensures high availability, scalability, and maintainability while providing fast, accurate astrological calculations.