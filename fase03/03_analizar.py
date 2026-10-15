from pathlib import Path

import pandas as pd


#### 1. Cargar las tablas procesadas.

DATA_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')

# Si se ejecuta desde la carpeta del script en el IDE, completamos las rutas
# desde la raíz de bigdata-game.
if not DATA_DIR.exists():
    PROJECT_DIR = Path(__file__).resolve().parents[3]
    DATA_DIR = PROJECT_DIR / DATA_DIR
    REPORTS_DIR = PROJECT_DIR / REPORTS_DIR

REPORTS_DIR.mkdir(exist_ok=True)

snapshots = pd.read_csv(DATA_DIR / 'snapshots.csv')
resources = pd.read_csv(DATA_DIR / 'resources.csv')
activities = pd.read_csv(DATA_DIR / 'activities.csv')
needs = pd.read_csv(DATA_DIR / 'needs.csv')
social = pd.read_csv(DATA_DIR / 'social.csv')


#### 2. Contar los cambios de actividad y calcular sus porcentajes.

activity_counts = activities['activity'].value_counts()
activity_proportions = activities['activity'].value_counts(normalize=True)
activity_percent = (activity_proportions * 100).round(1)

print('\nACTIVIDADES')
print(activity_counts)
print('\nPORCENTAJES')
print(activity_percent)


#### 3. Calcular el cambio neto registrado de cada recurso.

resource_groups = resources.groupby('resource_type')
delta_groups = resource_groups['amount_delta']
resource_balance = delta_groups.sum()
resource_balance = resource_balance.sort_values(ascending=False)



print('\nBALANCE NETO DE RECURSOS')
print(resource_balance)


#### 4. Separar los incrementos y las reducciones de recursos.

gains = resources[resources['amount_delta'] > 0]
spending = resources[resources['amount_delta'] < 0].copy()
spending['amount_delta'] = spending['amount_delta'].abs()

print('\nINCREMENTOS REGISTRADOS')
print(gains.groupby('resource_type')['amount_delta'].sum())

print('\nREDUCCIONES REGISTRADAS')
print(spending.groupby('resource_type')['amount_delta'].sum())


#### 5. Contar las necesidades que llegaron al estado crítico.

critical_needs = needs[needs['state'] == 'critical']
critical_counts = critical_needs['need_type'].value_counts()

print('\nNECESIDADES CRÍTICAS')
print(critical_counts)


#### 6. Contar los tipos de interacción social.

interaction_counts = social['interaction_type'].value_counts()

print('\nINTERACCIONES SOCIALES')
print(interaction_counts)


#### 7. Comparar la primera y la última fotografía disponibles.

ordered_snapshots = snapshots.sort_values(['tick', 'event_index'])
last = None

print('\nEVOLUCIÓN DEL MUNDO')
if ordered_snapshots.empty:
    print('No hay snapshots para comparar.')
else:
    first = ordered_snapshots.iloc[0]
    last = ordered_snapshots.iloc[-1]

    for column in [
        'population', 'constructed_buildings',
        'wood_stock', 'food_stock', 'gold_stock',
    ]:
        change = last[column] - first[column]
        print(column, ':', first[column], '->', last[column],
              '(cambio:', change, ')')


#### 8. Guardar las métricas seleccionadas en un resumen.

if last is None:
    final_population = None
    final_buildings = None
else:
    final_population = last['population']
    final_buildings = last['constructed_buildings']

summary = pd.DataFrame([
    {'metric': 'events_activity', 'value': len(activities)},
    {'metric': 'events_resource', 'value': len(resources)},
    {'metric': 'critical_needs', 'value': len(critical_needs)},
    {'metric': 'social_interactions', 'value': len(social)},
    {'metric': 'final_population', 'value': final_population},
    {'metric': 'final_buildings', 'value': final_buildings},
])

output = REPORTS_DIR / 'metrics_summary.csv'
summary.to_csv(output, index=False)

print('\nINFORME GUARDADO')
print(output, '->', len(summary), 'filas')
