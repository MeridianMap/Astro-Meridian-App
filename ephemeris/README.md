# Swiss Ephemeris Files Directory

This directory should contain the Swiss Ephemeris data files for high-precision astronomical calculations.

## Required Files

Download from [Swiss Ephemeris website](https://www.astro.com/swisseph/swephinfo_e.htm):

### Essential Files (minimum for basic calculations):
- `sepl_*.se1` - Planet ephemeris files (multiple files covering different date ranges)
- `semo_*.se1` - Moon ephemeris files
- `seleapsec.txt` - Leap seconds table
- `sedeltat` - Delta T table
- `sefstars.txt` - Fixed stars catalog

### Recommended Additional Files:
- `seas_*.se1` - Asteroid ephemeris files
- `semo_*.se1` - Additional moon files for extended date ranges
- Asteroid-specific files as needed

## Download Instructions

1. Visit https://www.astro.com/swisseph/swephinfo_e.htm
2. Download the compressed ephemeris files
3. Extract all `.se1`, `.txt`, and other data files to this directory
4. Ensure no subdirectories - files should be directly in `/ephemeris/`

## File Size Note

The complete ephemeris file set can be several hundred MB to GB depending on date range and precision requirements. For development, the basic planet and moon files (covering ~1800-2200 CE) should be sufficient.

## Usage in Code

Set the ephemeris path in your Python code:
```python
import swisseph as swe
swe.set_ephe_path('/path/to/ephemeris')
```

## Validation

After downloading, test with:
```python
import swisseph as swe
swe.set_ephe_path('./ephemeris')
# Should not raise errors for dates within file coverage
calc_ut = swe.calc_ut(2460000.0, swe.SUN)  
print(calc_ut)
```