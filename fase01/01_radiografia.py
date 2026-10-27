from pathlib import Path

import pandas as pd


RAW_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')
RAW_FILE = RAW_DIR / 'nevworld_1150427077545796967_20261007_070934.jsonl'

if not RAW_FILE.exists():
    raise FileNotFoundError(f'No se encuentra el RAW: {RAW_FILE}')

df = pd.read_json(
    RAW_FILE,
    lines=True,
    dtype={'run_id': 'string', 'seed': 'string'},
)

required = ['schema_version', 'run_id', 'seed', 'event_index', 'tick', 'type']
assert not df.empty, 'El dataset esta vacio'
assert set(required).issubset(df.columns), 'Faltan columnas principales'
assert not df.duplicated(['run_id', 'event_index']).any(), 'Hay eventos duplicados'

ordered = df.sort_values(['run_id', 'event_index'])
ticks_ok = ordered.groupby('run_id')['tick'].apply(
    lambda ticks: ticks.is_monotonic_increasing
).all()
assert ticks_ok, 'Los ticks retroceden al ordenar los eventos'

event_counts = df['type'].value_counts()
first = df.iloc[0]

print('VALIDACIONES: OK')
print('\nPRIMEROS EVENTOS')
print(df.head())
print('\nRADIOGRAFIA DE LA PARTIDA')
print('Archivo:', RAW_FILE.name)
print('Filas y columnas:', df.shape)
print('Columnas:', df.columns.tolist())
print('Primer tipo:', first['type'])
print('Tipo mas frecuente:', event_counts.index[0], '-', event_counts.iloc[0])
print('\nRECUENTO POR TIPO')
print(event_counts.to_string())
print('\nDATOS DE LA PRIMERA FILA')
print('run_id:', first['run_id'])
print('Semilla:', first['seed'])
print('Version del esquema:', first['schema_version'])
print('Ticks:', df['tick'].min(), '->', df['tick'].max())
