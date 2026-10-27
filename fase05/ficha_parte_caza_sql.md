# Fase 05: caza con SQL

DuckDB devuelve 61 sheep y 3 deer, igual que pandas. El CSV ocupa 6.295 bytes y el Parquet 5.165.

## Respuestas

**¿Qué representa una fila?** Una presa y su número de cacerías, no comida.

**¿Qué hace AS hunt_count?** Nombra COUNT(*). Si cambia, también cambian ORDER BY y las referencias posteriores.

**¿Qué ocupa menos?** Aquí Parquet, pero no siempre: depende de los datos y del uso.

La salida es **reports/hunts_by_prey_sql.csv**.

## Ejecución

~~~powershell
python scripts/actividades_1/fase05/05_caza_sql.py
~~~

## Código

~~~python
from pathlib import Path

import duckdb
import pandas as pd


RAW_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')
PARQUET_DIR = OUTPUT_DIR / 'parquet'
CSV_FILE = OUTPUT_DIR / 'hunts.csv'
PARQUET_FILE = PARQUET_DIR / 'hunts.parquet'
REPORT_FILE = REPORTS_DIR / 'hunts_by_prey_sql.csv'

if not CSV_FILE.exists():
    raise FileNotFoundError(f'No se encuentra: {CSV_FILE}')

table = pd.read_csv(CSV_FILE, dtype={'run_id': 'string'})
assert 'prey_type' in table.columns, 'Falta la columna prey_type'
if not table.empty:
    assert table['prey_type'].notna().all(), 'Hay cacerias sin presa informada'

PARQUET_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
table.to_parquet(PARQUET_FILE, engine='pyarrow', index=False)

print('CSV:', CSV_FILE.stat().st_size, 'bytes')
print('Parquet:', PARQUET_FILE.stat().st_size, 'bytes')

hunt_query = """
    SELECT
        prey_type,
        COUNT(*) AS hunt_count
    FROM read_parquet('data/processed/parquet/hunts.parquet')
    GROUP BY prey_type
    ORDER BY hunt_count DESC, prey_type
"""

connection = duckdb.connect()
try:
    hunt_summary = connection.execute(hunt_query).fetchdf()
finally:
    connection.close()

if hunt_summary.empty:
    hunt_summary = pd.DataFrame(columns=['prey_type', 'hunt_count'])

assert int(hunt_summary['hunt_count'].sum()) == len(table), \
    'El recuento SQL no coincide con el CSV'

pandas_counts = table['prey_type'].value_counts().sort_index()
sql_counts = hunt_summary.set_index('prey_type')['hunt_count'].sort_index()
assert pandas_counts.equals(sql_counts.astype(pandas_counts.dtype)), \
    'SQL y pandas dan recuentos distintos'

hunt_summary.to_csv(REPORT_FILE, index=False)
print('\nRESULTADO SQL')
print(hunt_summary.to_string(index=False))
print('\nVALIDACIONES: OK')
print('Informe:', REPORT_FILE)
~~~

