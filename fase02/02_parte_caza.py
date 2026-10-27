from pathlib import Path

import pandas as pd


RAW_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')
RAW_FILE = RAW_DIR / 'nevworld_1150427077545796967_20261007_070934.jsonl'

if not RAW_FILE.exists():
    raise FileNotFoundError(f'No se encuentra el RAW: {RAW_FILE}')

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
df = pd.read_json(RAW_FILE, lines=True, dtype={'run_id': 'string'})

required_raw = ['run_id', 'event_index', 'tick', 'type', 'villager_id', 'prey_type']
assert set(required_raw).issubset(df.columns), 'Faltan columnas necesarias en el RAW'

output_columns = [
    'run_id', 'event_index', 'tick', 'villager_id', 'prey_type',
    'simulation_day',
]
hunts = df.loc[
    df['type'].eq('hunt_completed'),
    output_columns[:-1],
].copy()
hunts['simulation_day'] = hunts['tick'] // 12000
hunts = hunts.reindex(columns=output_columns)

expected = int(df['type'].eq('hunt_completed').sum())
assert len(hunts) == expected, 'El numero de cacerias no coincide'
assert not hunts.duplicated(['run_id', 'event_index']).any(), 'Hay cacerias duplicadas'
if not hunts.empty:
    assert hunts[output_columns].notna().all().all(), 'Hay campos obligatorios vacios'
    assert hunts['simulation_day'].eq(hunts['tick'] // 12000).all(), \
        'simulation_day es incorrecto'

output_file = OUTPUT_DIR / 'hunts.csv'
hunts.to_csv(output_file, index=False)

print('VALIDACIONES: OK')
print('Archivo generado:', output_file)
print('Cacerias completadas:', len(hunts))
print('Cazadores distintos:', hunts['villager_id'].nunique())
print('\nCacerias por presa')
print(hunts['prey_type'].value_counts().to_string())
