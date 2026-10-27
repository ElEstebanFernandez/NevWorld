from hashlib import sha256
from pathlib import Path
from time import perf_counter

import pandas as pd


RAW_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
files = sorted(RAW_DIR.glob('nevworld_*.jsonl'))
if not files:
    raise FileNotFoundError(f'No hay JSONL de NevWorld en {RAW_DIR}')

start = perf_counter()
frames = []
manifest = []

for path in files:
    checksum = sha256(path.read_bytes()).hexdigest()
    try:
        frame = pd.read_json(path, lines=True, dtype={'run_id': 'string'})
        valid_schema = (
            not frame.empty
            and 'schema_version' in frame.columns
            and frame['schema_version'].eq(2).all()
        )
        status = 'accepted' if valid_schema else 'rejected'
        error = ''
    except (ValueError, OSError) as exc:
        frame = pd.DataFrame()
        valid_schema = False
        status = 'rejected'
        error = str(exc)

    manifest.append({
        'file': path.name,
        'bytes': path.stat().st_size,
        'rows': len(frame),
        'sha256': checksum,
        'status': status,
        'error': error,
    })
    if valid_schema:
        frame['source_file'] = path.name
        frames.append(frame)

pd.DataFrame(manifest).to_csv(REPORTS_DIR / 'manifest.csv', index=False)
if not frames:
    raise ValueError('Ningun archivo utiliza el esquema 2')

events = pd.concat(frames, ignore_index=True)
required = ['run_id', 'event_index', 'tick', 'type']
assert set(required).issubset(events.columns), 'Faltan columnas comunes'
assert events[required].notna().all().all(), 'Hay campos comunes vacios'

duplicates = int(events.duplicated(['run_id', 'event_index']).sum())
if duplicates:
    raise ValueError(f'Se detectaron {duplicates} eventos duplicados')

events = events.sort_values(['run_id', 'event_index']).reset_index(drop=True)
ticks_ok = events.groupby('run_id')['tick'].apply(
    lambda ticks: ticks.is_monotonic_increasing
).all()
assert ticks_ok, 'Los ticks retroceden en alguna partida'

events.to_parquet(OUTPUT_DIR / 'all_events.parquet', index=False)
elapsed = perf_counter() - start
run_report = pd.DataFrame([{
    'files_found': len(files),
    'files_accepted': len(frames),
    'sessions': events['run_id'].nunique(),
    'events': len(events),
    'seconds': round(elapsed, 3),
}])
run_report.to_csv(REPORTS_DIR / 'pipeline_run.csv', index=False)
print(run_report.to_string(index=False))
