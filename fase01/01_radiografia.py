from pathlib import Path
import pandas as pd


#### 1. Preparar la ruta y leer el archivo RAW.

DATASET = Path('data/raw/nevworld_1150427077545796967_20261007_070934.jsonl'

)

# Si se ejecuta desde la carpeta del script en el IDE, completamos la ruta
# desde la raíz de bigdata-game.
if not DATASET.exists():
    PROJECT_DIR = Path(__file__).resolve().parents[3]
    DATASET = PROJECT_DIR / DATASET

if not DATASET.exists():
    raise FileNotFoundError(f'No se encuentra: {DATASET.resolve()}')

# Cada línea del JSONL se convierte en una fila del DataFrame.
df = pd.read_json(
    DATASET,
    lines=True,
    dtype={'run_id': 'string', 'seed': 'string'}
)


#### 2. Realizar las cuatro validaciones antes de consultar la primera fila.

required = ['run_id', 'event_index', 'tick', 'type']

assert not df.empty, 'El dataset está vacío'
assert all(column in df.columns for column in required), \
    'Faltan columnas principales'
assert not df.duplicated(['run_id', 'event_index']).any(), \
    'Hay eventos duplicados'

ordered = df.sort_values('event_index')
assert ordered['tick'].is_monotonic_increasing, \
    'Los ticks retroceden al ordenar por event_index'

print('VALIDACIÓN BÁSICA: OK')


#### 3. Mostrar los primeros eventos.

print('\nPRIMEROS EVENTOS')
print(df.head())


#### 4. Obtener los datos de la ficha.

filas, columnas = df.shape
column_names = df.columns.tolist()

first_event_type = df['type'].iloc[0]
event_counts = df['type'].value_counts()
most_frequent_type = event_counts.index[0]
most_frequent_amount = event_counts.iloc[0]

first_run_id = df['run_id'].iloc[0]
first_seed = df['seed'].iloc[0]
first_schema_version = df['schema_version'].iloc[0]

minimum_tick = df['tick'].min()
maximum_tick = df['tick'].max()

print('\nDATOS DE MI PARTIDA')
print('Nombre del archivo JSONL:', DATASET.name)
print('Número total de eventos:', filas)
print('Número de columnas:', columnas)
print('Nombres de las columnas:', column_names)
print('Tipo del primer evento registrado:', first_event_type)
print(
    'Tipo de evento más frecuente y cantidad:',
    most_frequent_type,
    '-',
    most_frequent_amount
)

print('\nRECUENTO DE TODOS LOS TIPOS DE EVENTO')
print(event_counts)

print('\nDATOS DE LA PRIMERA FILA')
print('run_id:', first_run_id)
print('Semilla:', first_seed)
print('Versión del esquema:', first_schema_version)

print('\nINTERVALO DE TICKS')
print('Tick mínimo:', minimum_tick)
print('Tick máximo:', maximum_tick)
print('Resultado de las validaciones: las cuatro validaciones pasan')


#### 5. Responder las preguntas de la ficha.

print('\nRESPUESTAS')

print('\n1. ¿Qué permite afirmar el recuento?')
print(
    'Permite saber cuántos eventos de cada tipo se registraron en la partida. '
    'El más frecuente no tiene que ser el más importante, porque la frecuencia '
    'no mide la duración ni la importancia de un evento.'
)

print('\n2. ¿Por qué una celda vacía no significa que el registro esté mal?')
print(
    'Cada tipo de evento utiliza campos diferentes. Una celda vacía puede '
    'indicar que ese campo no corresponde a ese tipo de evento; no significa '
    'automáticamente que exista un error ni que su valor sea cero.'
)

print('\n3. ¿Qué sabemos y qué análisis posterior haría falta?')
print(
    'Ahora conocemos el tamaño del archivo, sus columnas, los tipos de evento, '
    'la partida y el intervalo de ticks. Para saber, por ejemplo, cómo cambió '
    'la población durante la partida habría que analizar los eventos o las '
    'fotografías que contienen datos de población.'
)
