# Swiss Ephemeris Integration Patterns

**Description**: Proven Swiss Ephemeris integration patterns to preserve  
**Generated**: 2025-09-09 13:46:58  
**Components Found**: 7

## 📋 Component Analysis

### 1. get_planet

**File**: `backend/app/core/ephemeris/tools/ephemeris.py`  
**Type**: integration  
**Value Score**: 5/5 ⭐  
**Complexity**: 2/5  
**Lines**: 73  
**Priority**: high  
**Action**: extract_as_is

**Description**: Swiss Ephemeris integration: get_planet

**Code Sample**:
```python
def get_planet(
    planet_id: int,
    julian_day: float,
    flags: Optional[int] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    altitude: float = 0.0
) -> PlanetPosition:
    """
    Calculate planet position using Swiss Ephemeris.
    
    Args:
        planet_id: Swiss Ephemeris planet constant
        julian_day: Julian Day Number for calculation
        flags: Swiss Ephemeris calculation flags
        latitude: Observer latitude (for topocentric c...
```

**Dependencies**: import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass

import swisseph as swe

from ..const import , from ..settings import settings
from ..classes.cache import cached
from ..models.planet_data import PlanetData




**Notes**: Working Swiss Ephemeris integration pattern

---

### 2. get_houses

**File**: `backend/app/core/ephemeris/tools/ephemeris.py`  
**Type**: integration  
**Value Score**: 5/5 ⭐  
**Complexity**: 2/5  
**Lines**: 45  
**Priority**: high  
**Action**: extract_as_is

**Description**: Swiss Ephemeris integration: get_houses

**Code Sample**:
```python
def get_houses(
    julian_day: float,
    latitude: float,
    longitude: float,
    house_system: str = 'P'
) -> HouseSystem:
    """
    Calculate house system using Swiss Ephemeris.
    
    Args:
        julian_day: Julian Day Number for calculation
        latitude: Observer latitude in degrees
        longitude: Observer longitude in degrees
        house_system: House system code (P=Placidus, K=Koch, etc.)
    
    Returns:
        HouseSystem object with house cusps and angles
        
...
```

**Dependencies**: import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass

import swisseph as swe

from ..const import , from ..settings import settings
from ..classes.cache import cached
from ..models.planet_data import PlanetData




**Notes**: Working Swiss Ephemeris integration pattern

---

### 3. get_fixed_star

**File**: `backend/app/core/ephemeris/tools/ephemeris.py`  
**Type**: integration  
**Value Score**: 5/5 ⭐  
**Complexity**: 2/5  
**Lines**: 40  
**Priority**: high  
**Action**: extract_as_is

**Description**: Swiss Ephemeris integration: get_fixed_star

**Code Sample**:
```python
def get_fixed_star(
    star_name: str,
    julian_day: float
) -> Dict[str, Union[float, str]]:
    """
    Calculate fixed star position using Swiss Ephemeris.
    
    Args:
        star_name: Name of the fixed star
        julian_day: Julian Day Number for calculation
    
    Returns:
        Dictionary with star position data
        
    Raises:
        RuntimeError: If star calculation fails
    """
    try:
        # Swiss Ephemeris fixed star calculation
        result = swe.fixstar_ut...
```

**Dependencies**: import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass

import swisseph as swe

from ..const import , from ..settings import settings
from ..classes.cache import cached
from ..models.planet_data import PlanetData




**Notes**: Working Swiss Ephemeris integration pattern

---

### 4. julian_day_from_datetime

**File**: `backend/app/core/ephemeris/tools/ephemeris.py`  
**Type**: integration  
**Value Score**: 3/5 ⭐  
**Complexity**: 2/5  
**Lines**: 13  
**Priority**: medium  
**Action**: extract_as_is

**Description**: Swiss Ephemeris integration: julian_day_from_datetime

**Code Sample**:
```python
def julian_day_from_datetime(dt: datetime) -> float:
    """Convert datetime to Julian Day Number."""
    # Convert to UTC if timezone-aware
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc)
    
    # SwissEph expects separate date/time components
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour + dt.minute/60.0 + dt.second/3600.0 + dt.microsecond/3600000000.0
    
    return swe.julday(year, month, day, hour)
```

**Dependencies**: import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass

import swisseph as swe

from ..const import , from ..settings import settings
from ..classes.cache import cached
from ..models.planet_data import PlanetData




**Notes**: Working Swiss Ephemeris integration pattern

---

### 5. datetime_from_julian_day

**File**: `backend/app/core/ephemeris/tools/ephemeris.py`  
**Type**: integration  
**Value Score**: 3/5 ⭐  
**Complexity**: 2/5  
**Lines**: 16  
**Priority**: medium  
**Action**: extract_as_is

**Description**: Swiss Ephemeris integration: datetime_from_julian_day

**Code Sample**:
```python
def datetime_from_julian_day(jd: float) -> datetime:
    """Convert Julian Day Number to datetime."""
    year, month, day, hour = swe.revjul(jd)
    
    # Convert fractional hour to hour, minute, second, microsecond
    hour_int = int(hour)
    minute_float = (hour - hour_int) * 60
    minute_int = int(minute_float)
    second_float = (minute_float - minute_int) * 60
    second_int = int(second_float)
    microsecond_int = int((second_float - second_int) * 1000000)
    
    return datetime(
  ...
```

**Dependencies**: import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass

import swisseph as swe

from ..const import , from ..settings import settings
from ..classes.cache import cached
from ..models.planet_data import PlanetData




**Notes**: Working Swiss Ephemeris integration pattern

---

### 6. _setup_swiss_ephemeris_path

**File**: `backend/app/services/ephemeris_service.py`  
**Type**: integration  
**Value Score**: 3/5 ⭐  
**Complexity**: 2/5  
**Lines**: 45  
**Priority**: medium  
**Action**: extract_as_is

**Description**: Swiss Ephemeris integration: _setup_swiss_ephemeris_path

**Code Sample**:
```python
    def _setup_swiss_ephemeris_path(self):
        """Set up Swiss Ephemeris library path for enhanced fixed star calculations."""
        import os
        import swisseph as swe
        
        # Find project root by looking for specific folders
        current_dir = os.path.dirname(__file__)
        project_root = current_dir
        
        # Go up directories until we find the Swiss Eph Library Files folder
        max_levels = 10
        for _ in range(max_levels):
            potential_...
```

**Dependencies**: import time
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from dataclasses import asdict

from ..api.models.schemas import , from ..core.ephemeris.charts.subject import Subject
from ..core.ephemeris.charts.natal import NatalChart
from ..core.ephemeris.const import PLANET_NAMES, get_sign_from_longitude, get_sign_name
from ..core.ephemeris.tools.ephemeris import validate_ephemeris_files, analyze_retrograde_motion
from ..core.ephemeris.tools.aspects import AspectCalculator
from ..core.ephemeris.tools.orb_systems import OrbSystemManager
from ..core.ephemeris.tools.arabic_parts import ArabicPartsCalculator
from ..core.ephemeris.tools.arabic_parts_models import ArabicPartsRequest
from ..core.ephemeris.tools.fixed_stars import FixedStarCalculator


class EphemerisServiceError

**Notes**: Working Swiss Ephemeris integration pattern

---

### 7. EphemerisService._setup_swiss_ephemeris_path

**File**: `backend/app/services/ephemeris_service.py`  
**Type**: integration  
**Value Score**: 3/5 ⭐  
**Complexity**: 2/5  
**Lines**: 45  
**Priority**: medium  
**Action**: extract_as_is

**Description**: Swiss Ephemeris integration: EphemerisService._setup_swiss_ephemeris_path

**Code Sample**:
```python
    def _setup_swiss_ephemeris_path(self):
        """Set up Swiss Ephemeris library path for enhanced fixed star calculations."""
        import os
        import swisseph as swe
        
        # Find project root by looking for specific folders
        current_dir = os.path.dirname(__file__)
        project_root = current_dir
        
        # Go up directories until we find the Swiss Eph Library Files folder
        max_levels = 10
        for _ in range(max_levels):
            potential_...
```

**Dependencies**: import time
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from dataclasses import asdict

from ..api.models.schemas import , from ..core.ephemeris.charts.subject import Subject
from ..core.ephemeris.charts.natal import NatalChart
from ..core.ephemeris.const import PLANET_NAMES, get_sign_from_longitude, get_sign_name
from ..core.ephemeris.tools.ephemeris import validate_ephemeris_files, analyze_retrograde_motion
from ..core.ephemeris.tools.aspects import AspectCalculator
from ..core.ephemeris.tools.orb_systems import OrbSystemManager
from ..core.ephemeris.tools.arabic_parts import ArabicPartsCalculator
from ..core.ephemeris.tools.arabic_parts_models import ArabicPartsRequest
from ..core.ephemeris.tools.fixed_stars import FixedStarCalculator


class EphemerisServiceError

**Notes**: Working Swiss Ephemeris integration pattern

---

