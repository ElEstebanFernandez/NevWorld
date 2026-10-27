from pathlib import Path

import pandas as pd


RAW_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')
HUNTS_FILE = OUTPUT_DIR / 'hunts.csv'
RESOURCES_FILE = OUTPUT_DIR / 'resources.csv'

for path in (HUNTS_FILE, RESOURCES_FILE):
    if not path.exists():
        raise FileNotFoundError(f'No se encuentra: {path}')

hunts = pd.read_csv(HUNTS_FILE, dtype={'run_id': 'string'})
resources = pd.read_csv(RESOURCES_FILE, dtype={'run_id': 'string'})

required_hunts = ['run_id', 'event_index', 'prey_type', 'simulation_day']
required_resources = ['run_id', 'event_index', 'resource_type', 'amount_delta']
assert set(required_hunts).issubset(hunts.columns), 'Faltan columnas en hunts.csv'
assert set(required_resources).issubset(resources.columns), 'Faltan columnas en resources.csv'
assert not hunts.duplicated(['run_id', 'event_index']).any(), 'Hay cacerias duplicadas'
assert not resources.duplicated(['run_id', 'event_index']).any(), \
    'Hay cambios de recursos duplicados'
if not hunts.empty:
    assert hunts[required_hunts].notna().all().all(), 'Hay datos de caza vacios'
if not resources.empty:
    assert resources[required_resources].notna().all().all(), \
        'Hay datos de recursos vacios'

hunt_runs = set(hunts['run_id'].dropna().astype(str))
resource_runs = set(resources['run_id'].dropna().astype(str))
assert len(hunt_runs) <= 1 and len(resource_runs) <= 1, 'Hay varias partidas en un CSV'
if hunt_runs and resource_runs:
    assert hunt_runs == resource_runs, 'Los CSV pertenecen a partidas distintas'

total_hunts = len(hunts)
hunts_by_prey = hunts['prey_type'].value_counts()
prey_percent_raw = hunts['prey_type'].value_counts(normalize=True) * 100
prey_percent = prey_percent_raw.round(1)
hunts_by_day = hunts['simulation_day'].value_counts().sort_index()

print('TOTAL DE CACERIAS:', total_hunts)
if hunts.empty:
    print('No hay cacerias completadas registradas.')
else:
    print('\nCACERIAS POR PRESA\n', hunts_by_prey.to_string(), sep='')
    print('\nPORCENTAJES\n', prey_percent.to_string(), sep='')
    print('\nCACERIAS POR DIA\n', hunts_by_day.to_string(), sep='')

food = resources.loc[resources['resource_type'].eq('food')]
food_gains = food.loc[food['amount_delta'] > 0, 'amount_delta'].sum()
food_reductions = food.loc[food['amount_delta'] < 0, 'amount_delta'].abs().sum()
food_net_change = food['amount_delta'].sum()

print('\nCAMBIOS DE COMIDA')
print('Eventos:', len(food))
print('Incrementos:', food_gains)
print('Reducciones:', food_reductions)
print('Balance neto:', food_net_change)

assert hunts_by_prey.sum() == total_hunts, 'Falla el recuento por presa'
assert hunts_by_day.sum() == total_hunts, 'Falla el recuento por dia'
assert abs((food_gains - food_reductions) - food_net_change) < 0.000001, \
    'Falla el balance de comida'
if not hunts.empty:
    assert abs(prey_percent_raw.sum() - 100) < 0.000001, 'Los porcentajes no suman 100'

summary = pd.DataFrame([
    {'metric': 'hunt_events', 'value': total_hunts},
    {'metric': 'food_change_events', 'value': len(food)},
    {'metric': 'food_gains', 'value': food_gains},
    {'metric': 'food_reductions', 'value': food_reductions},
    {'metric': 'food_net_change', 'value': food_net_change},
])
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
report_file = REPORTS_DIR / 'hunting_summary.csv'
summary.to_csv(report_file, index=False)
print('\nVALIDACIONES: OK')
print('Informe:', report_file)
