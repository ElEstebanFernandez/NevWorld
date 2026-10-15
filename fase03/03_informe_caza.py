from pathlib import Path
import pandas as pd


#### 1. Preparar las rutas y leer los CSV procesados.

CARPETA_FASE = Path(__file__).resolve().parent
PROYECTO = CARPETA_FASE.parents[2]
DATA_DIR = PROYECTO / 'data/processed'
OUTPUT_DIR = PROYECTO / 'reports'

HUNTS_FILE = DATA_DIR / 'hunts.csv'
RESOURCES_FILE = DATA_DIR / 'resources.csv'

if not HUNTS_FILE.exists():
    raise FileNotFoundError(f'No se encuentra: {HUNTS_FILE.resolve()}')

if not RESOURCES_FILE.exists():
    raise FileNotFoundError(f'No se encuentra: {RESOURCES_FILE.resolve()}')

hunts = pd.read_csv(HUNTS_FILE)
resources = pd.read_csv(RESOURCES_FILE)


#### 2. Comprobar las columnas, los duplicados y los valores ausentes.

required_hunts = ['run_id', 'event_index', 'prey_type', 'simulation_day']
required_resources = ['run_id', 'event_index', 'resource_type', 'amount_delta']

assert all(column in hunts.columns for column in required_hunts), \
    'Faltan columnas necesarias en hunts.csv'
assert all(column in resources.columns for column in required_resources), \
    'Faltan columnas necesarias en resources.csv'

assert not hunts.duplicated(['run_id', 'event_index']).any(), \
    'Hay cacerías duplicadas'
assert not resources.duplicated(['run_id', 'event_index']).any(), \
    'Hay cambios de recursos duplicados'

if not hunts.empty:
    assert hunts[required_hunts].notna().all().all(), \
        'Hay cacerías con campos obligatorios ausentes'

if not resources.empty:
    assert resources[required_resources].notna().all().all(), \
        'Hay cambios de recursos con campos obligatorios ausentes'


#### 3. Resumir las cacerías completadas.

total_hunts = len(hunts)
hunts_by_prey = hunts['prey_type'].value_counts()
prey_percent_raw = hunts['prey_type'].value_counts(normalize=True) * 100
prey_percent = prey_percent_raw.round(1)
hunts_by_day = hunts['simulation_day'].value_counts().sort_index()

print('\nTOTAL DE CACERÍAS COMPLETADAS')
print(total_hunts)

if hunts.empty:
    print('No hay cacerías completadas registradas.')
else:
    print('\nCACERÍAS POR PRESA')
    print(hunts_by_prey)

    print('\nPORCENTAJE POR PRESA')
    print(prey_percent)

    print('\nCACERÍAS POR DÍA')
    print(hunts_by_day)


#### 4. Examinar los cambios de comida.

food = resources[resources['resource_type'] == 'food']
food_gains = food[food['amount_delta'] > 0]['amount_delta'].sum()
food_reductions = food[food['amount_delta'] < 0]['amount_delta'].abs().sum()
food_net_change = food['amount_delta'].sum()

print('\nCAMBIOS DE COMIDA')

if food.empty:
    print('No hay eventos de cambio de comida registrados.')

print('Eventos:', len(food))
print('Incrementos:', food_gains)
print('Reducciones:', food_reductions)
print('Balance neto:', food_net_change)


#### 5. Comprobar los resultados.

assert hunts_by_prey.sum() == total_hunts, \
    'Los recuentos por presa no coinciden con el total'
assert hunts_by_day.sum() == total_hunts, \
    'Los recuentos por día no coinciden con el total'
assert abs((food_gains - food_reductions) - food_net_change) < 0.000001, \
    'El balance de comida no coincide'

if not hunts.empty:
    assert abs(prey_percent_raw.sum() - 100) < 0.000001, \
        'Los porcentajes no suman aproximadamente 100'

print('\nCOMPROBACIONES: OK')


#### 6. Comprobar que las tablas pertenecen a la misma partida y guardar.

same_run = (
    not hunts.empty
    and not resources.empty
    and hunts['run_id'].nunique() == 1
    and resources['run_id'].nunique() == 1
    and hunts['run_id'].iloc[0] == resources['run_id'].iloc[0]
)

if not same_run:
    print('\nERROR: LOS CSV PERTENECEN A PARTIDAS DIFERENTES')
    print('Partida de hunts.csv:', hunts['run_id'].unique())
    print('Partida de resources.csv:', resources['run_id'].unique())
    print('No se crea hunting_summary.csv para no mezclar partidas.')
else:
    summary = pd.DataFrame([
        {'metric': 'hunt_events', 'value': total_hunts},
        {'metric': 'food_change_events', 'value': len(food)},
        {'metric': 'food_gains', 'value': food_gains},
        {'metric': 'food_reductions', 'value': food_reductions},
        {'metric': 'food_net_change', 'value': food_net_change},
    ])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / 'hunting_summary.csv'
    summary.to_csv(output, index=False)
    print(output.resolve(), '->', len(summary), 'filas')


#### 7. Conclusiones obtenidas de los datos actuales.

# Una fila de hunts.csv representa una cacería completada.
# El denominador de los porcentajes es el total de cacerías registradas.
# La presa más frecuente es sheep: 61 cacerías de 64, un 95.3 %.
# El día 19 tiene el mayor recuento, con 9 cacerías completadas.
# Este recuento no indica cuánto tiempo se dedicó a cazar.
# El balance neto de comida es una variación, no las existencias finales.
# No puede demostrarse que cada incremento de comida proceda de una cacería:
# haría falta un identificador que relacionase ambos tipos de evento.
