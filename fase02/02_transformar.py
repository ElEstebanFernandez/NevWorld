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


def event_table(event_type, columns):
    selected = ['run_id', 'event_index', 'tick', *columns]
    missing = set(selected) - set(df.columns)
    if missing:
        raise ValueError(f'Faltan columnas en el RAW: {sorted(missing)}')
    table = df.loc[df['type'].eq(event_type), selected].copy()
    table['simulation_day'] = table['tick'] // 12000
    return table


tables = {
    'snapshots': event_table('world_snapshot', [
        'population', 'constructed_buildings', 'wood_stock', 'food_stock',
        'gold_stock', 'day',
    ]),
    'resources': event_table('resource_changed', [
        'resource_type', 'amount_before', 'amount_after', 'amount_delta',
    ]),
    'activities': event_table('villager_activity_changed', [
        'villager_id', 'activity', 'resource_type',
    ]),
    'needs': event_table('villager_need_changed', [
        'villager_id', 'need_type', 'state',
    ]),
    'social': event_table('social_interaction', [
        'actor_id', 'target_id', 'interaction_type', 'topic',
        'relationship_actor_to_target_after',
        'relationship_target_to_actor_after',
    ]),
    'buildings': event_table('building_created', [
        'building_id', 'building_type', 'cell_x', 'cell_y', 'width', 'height',
    ]),
}

resources = tables['resources']
if not resources.empty:
    coherent = (
        resources['amount_before'] + resources['amount_delta']
    ).eq(resources['amount_after'])
    assert coherent.all(), 'Hay cambios de recursos incoherentes'

for name, table in tables.items():
    assert not table.duplicated(['run_id', 'event_index']).any(), \
        f'Hay eventos duplicados en {name}'
    output_file = OUTPUT_DIR / f'{name}.csv'
    table.to_csv(output_file, index=False)
    print(name, '->', len(table), 'filas ->', output_file)
