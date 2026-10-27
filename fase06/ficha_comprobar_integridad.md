# Fase 06: lote e integridad

El pipeline aceptó 6 archivos, 6 partidas y 14.644 eventos. Genera all_events.parquet, manifest.csv y pipeline_run.csv.

| Archivo | Esperado | Recibido | SHA | Conclusión |
| --- | ---: | ---: | --- | --- |
| partida_A.jsonl | 1.755.298 | 1.755.298 | Coincide | Intacta |
| partida_B.jsonl | 1.755.298 | 1.755.297 | No coincide | Cambiada |

Había una referencia completa llamada referemcia.txt y otra incompleta llamada referencia.txt. El código prueba ambas sin recalcularlas.

## Respuestas

1. SHA-256 mira los bytes, no el nombre.
2. El tamaño puede quedar igual aunque cambie un carácter. Aquí B perdió un byte.
3. La huella no localiza el campo; compararía los JSONL.
4. Se guarda antes para no comparar el archivo cambiado consigo mismo.
5. Coincidir prueba igualdad con la referencia, no que el dato original sea verdadero.

## Código del pipeline

~~~python
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
~~~

## Código de verificación

~~~python
from hashlib import sha256
from pathlib import Path


RAW_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')
ENVIO_DIR = RAW_DIR.parent / 'intercambio' / 'envio'
REFERENCE_FILES = [
    ENVIO_DIR / 'referencia.txt',
    ENVIO_DIR / 'referemcia.txt',  # nombre antiguo que existe en esta copia
]
NAMES = ['partida_A.jsonl', 'partida_B.jsonl']


def checksum(path):
    return sha256(path.read_bytes()).hexdigest()


def read_reference(path):
    references = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[0] in NAMES and parts[1].isdigit():
            references[parts[0]] = {
                'size': int(parts[1]),
                'sha256': parts[2].lower(),
            }
    return references


references = {}
reference_used = None
for candidate in REFERENCE_FILES:
    if candidate.exists():
        candidate_references = read_reference(candidate)
        if set(candidate_references) == set(NAMES):
            references = candidate_references
            reference_used = candidate
            break
if not references:
    raise ValueError('No hay una referencia valida con nombre, tamano y SHA-256 para A y B')

print('Referencia utilizada:', reference_used)
print('RESULTADO DE LA VERIFICACION')
for name in NAMES:
    path = ENVIO_DIR / name
    expected = references[name]
    if not path.exists():
        print(f'{name}: NO RECIBIDO')
        continue
    current_hash = checksum(path)
    current_size = path.stat().st_size
    result = 'COINCIDE' if current_hash == expected['sha256'] else 'NO COINCIDE'
    print(f'\n{name}')
    print('Tamano esperado:', expected['size'])
    print('Tamano recibido:', current_size)
    print('SHA esperado:', expected['sha256'])
    print('SHA calculado:', current_hash)
    print('Resultado:', result)
~~~

