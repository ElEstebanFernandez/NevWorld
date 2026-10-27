from pathlib import Path

import pandas as pd


RAW_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
names = ['snapshots', 'resources', 'activities', 'needs', 'social']
tables = {}
for name in names:
    path = OUTPUT_DIR / f'{name}.csv'
    if not path.exists():
        raise FileNotFoundError(f'No se encuentra: {path}')
    tables[name] = pd.read_csv(path, dtype={'run_id': 'string'})

snapshots = tables['snapshots']
resources = tables['resources']
activities = tables['activities']
needs = tables['needs']
social = tables['social']

activity_counts = activities['activity'].value_counts()
activity_percent = (activities['activity'].value_counts(normalize=True) * 100).round(1)
resource_balance = resources.groupby('resource_type')['amount_delta'].sum().sort_values(
    ascending=False
)
gains = resources.loc[resources['amount_delta'] > 0].groupby('resource_type')[
    'amount_delta'
].sum()
reductions = resources.loc[resources['amount_delta'] < 0].groupby('resource_type')[
    'amount_delta'
].sum().abs()
critical_needs = needs.loc[needs['state'].eq('critical')]
interaction_counts = social['interaction_type'].value_counts()

print('ACTIVIDADES\n', activity_counts.to_string(), sep='')
print('\nPORCENTAJES\n', activity_percent.to_string(), sep='')
print('\nBALANCE DE RECURSOS\n', resource_balance.to_string(), sep='')
print('\nINCREMENTOS\n', gains.to_string(), sep='')
print('\nREDUCCIONES\n', reductions.to_string(), sep='')
print('\nNECESIDADES CRITICAS\n', critical_needs['need_type'].value_counts().to_string(), sep='')
print('\nINTERACCIONES\n', interaction_counts.to_string(), sep='')

ordered = snapshots.sort_values(['tick', 'event_index'])
last = ordered.iloc[-1] if not ordered.empty else None
summary = pd.DataFrame([
    {'metric': 'events_activity', 'value': len(activities)},
    {'metric': 'events_resource', 'value': len(resources)},
    {'metric': 'critical_needs', 'value': len(critical_needs)},
    {'metric': 'social_interactions', 'value': len(social)},
    {'metric': 'final_population', 'value': None if last is None else last['population']},
    {'metric': 'final_buildings', 'value': None if last is None else last['constructed_buildings']},
])
report_file = REPORTS_DIR / 'metrics_summary.csv'
summary.to_csv(report_file, index=False)
print('\nInforme:', report_file)
