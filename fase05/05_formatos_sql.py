from pathlib import Path

import duckdb
import pandas as pd


RAW_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')
PARQUET_DIR = OUTPUT_DIR / 'parquet'
PARQUET_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

names = ['snapshots', 'resources', 'activities', 'needs', 'social', 'buildings']
for name in names:
    csv_path = OUTPUT_DIR / f'{name}.csv'
    parquet_path = PARQUET_DIR / f'{name}.parquet'
    table = pd.read_csv(csv_path, dtype={'run_id': 'string'})
    table.to_parquet(parquet_path, engine='pyarrow', index=False)
    print(name, '- CSV:', csv_path.stat().st_size,
          'bytes; Parquet:', parquet_path.stat().st_size, 'bytes')

connection = duckdb.connect()
try:
    resource_summary = connection.execute("""
        SELECT resource_type, SUM(amount_delta) AS net_change, COUNT(*) AS changes
        FROM read_parquet('data/processed/parquet/resources.parquet')
        GROUP BY resource_type
        ORDER BY net_change DESC
    """).fetchdf()
    daily_summary = connection.execute("""
        SELECT day, MAX(population) AS population,
               MAX(constructed_buildings) AS buildings,
               ROUND(AVG(wood_stock), 2) AS average_wood,
               ROUND(AVG(food_stock), 2) AS average_food
        FROM read_parquet('data/processed/parquet/snapshots.parquet')
        GROUP BY day
        ORDER BY day
    """).fetchdf()
finally:
    connection.close()

print('\nRECURSOS CONSULTADOS CON SQL')
print(resource_summary.to_string(index=False))
daily_summary.to_csv(REPORTS_DIR / 'daily_summary.csv', index=False)
