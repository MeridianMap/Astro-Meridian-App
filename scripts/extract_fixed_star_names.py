import pathlib
import sys

STAR_FILE = pathlib.Path(__file__).resolve().parents[1] / 'backend' / 'ephemeris' / 'sefstars.txt'

def iter_star_names(path: pathlib.Path):
    seen = set()
    if not path.exists():
        raise SystemExit(f"Missing star file: {path}")
    with path.open('r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue
            # line format: traditional name ,nomenclature,... OR may start with spaces then comma
            # Split on comma first
            parts = line.rstrip('\n').split(',')
            if not parts:
                continue
            name = parts[0].strip()
            if not name:
                continue
            # Normalize duplicate spacing/case for uniqueness but preserve original canonical first occurrence
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            yield name


def main():
    names = list(iter_star_names(STAR_FILE))
    # Output as a markdown bullet list (compact columns)
    # We'll also output a machine-friendly pipe-separated single line for quick parsing.
    print('# FIXED_STARS_NAME_LIST')
    print(f'Total unique names: {len(names)}')
    print('\n## Pipe separated list (machine parse)')
    print('|'.join(names))
    print('\n## Markdown list')
    for n in names:
        print(f'- {n}')

if __name__ == '__main__':
    main()
