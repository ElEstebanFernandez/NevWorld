from pathlib import Path
import pandas as pd


#### 1. Preparar las rutas y leer el archivo RAW.

# Aquí guardamos en la variable DATASET la ruta del archivo que vamos a analizar.
DATASET = Path('data/raw/nevworld_1150427077545796967_20261007_070934.jsonl'

)

# Aquí definimos la carpeta de salida.
OUTPUT_DIR = Path('data/processed')

# Si se ejecuta desde la carpeta del script en el IDE, completamos las rutas
# desde la raíz de bigdata-game.
if not DATASET.exists():
    PROJECT_DIR = Path(__file__).resolve().parents[3]
    DATASET = PROJECT_DIR / DATASET
    OUTPUT_DIR = PROJECT_DIR / OUTPUT_DIR

if not DATASET.exists():
    raise FileNotFoundError(f'No se encuentra: {DATASET.resolve()}')

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Cada línea del JSONL se convierte en una fila del DataFrame.
df = pd.read_json(DATASET, lines=True)


#### 2. Crear una función para seleccionar un tipo de evento.

def event_table(event_type, columns):
    # Estas columnas permiten localizar el evento en el RAW.
    selected = ['run_id', 'event_index', 'tick', *columns]

    # Conservamos solo las columnas que existen en el DataFrame.
    available = [
        column for column in selected
        if column in df.columns
    ]

    # Filtramos el tipo de evento y creamos una tabla independiente.
    table = df.loc[
        df['type'] == event_type,
        available,
    ].copy()

    # reindex mantiene las columnas y su orden incluso si la tabla está vacía.
    table = table.reindex(columns=selected)

    # En NevWorld, 12000 ticks representan un día simulado.
    table['simulation_day'] = table['tick'] // 12000

    return table


#### 3. Crear las seis tablas especializadas.

tables = {
    'snapshots': event_table('world_snapshot', [
        'population', 'constructed_buildings',
        'wood_stock', 'food_stock', 'gold_stock', 'day',
    ]),
    'resources': event_table('resource_changed', [
        'resource_type', 'amount_before',
        'amount_after', 'amount_delta',
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
        'building_id', 'building_type',
        'cell_x', 'cell_y', 'width', 'height',
    ]),
}


#### 4. Comprobar la coherencia de los cambios de recursos.

resources = tables['resources']

if not resources.empty:
    valid = (
        resources['amount_before']
        + resources['amount_delta']
        == resources['amount_after']
    )
    assert valid.all(), 'Hay cambios de recursos incoherentes'


#### 5. Guardar las tablas en data/processed.

for name, table in tables.items():
    output = OUTPUT_DIR / f'{name}.csv'
    table.to_csv(output, index=False)
    print(name, '->', len(table), 'filas')
