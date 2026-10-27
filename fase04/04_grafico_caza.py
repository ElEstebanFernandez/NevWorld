from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd


RAW_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')
CHARTS_DIR = REPORTS_DIR / 'charts'
HUNTS_FILE = OUTPUT_DIR / 'hunts.csv'
CHART_FILE = CHARTS_DIR / '05_hunts_by_prey.png'

if not HUNTS_FILE.exists():
    raise FileNotFoundError(f'No se encuentra: {HUNTS_FILE}')

hunts = pd.read_csv(HUNTS_FILE, dtype={'run_id': 'string'})
required = ['run_id', 'event_index', 'prey_type']
assert set(required).issubset(hunts.columns), 'Faltan columnas en hunts.csv'
assert not hunts.duplicated(['run_id', 'event_index']).any(), 'Hay cacerias duplicadas'
if not hunts.empty:
    assert hunts[required].notna().all().all(), 'Hay una caceria sin presa informada'

counts = hunts['prey_type'].value_counts()
assert counts.sum() == len(hunts), 'Las barras no suman el total de cacerias'

if counts.empty:
    if CHART_FILE.exists():
        CHART_FILE.unlink()
    print('No hay cacerias completadas: no se crea el grafico.')
else:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4))
    counts.plot.bar(color='steelblue')
    plt.title('Cacerias completadas registradas por tipo de presa')
    plt.xlabel('Tipo de presa')
    plt.ylabel('Numero de cacerias completadas')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig(CHART_FILE, dpi=150)
    plt.close()
    print('Grafico:', CHART_FILE)
    print('Total representado:', counts.sum())
