#Importa Path, una clase de Python para trabajar con rutas de archivos y carpetas.
from pathlib import Path

# En lugar de escribir rutas como simples textos:
# "data/raw/archivo.jsonl"
# puedes tratarlas como objetos:
# Path("data/raw/archivo.jsonl")
# Esto facilita operaciones como crear carpetas, comprobar si existen archivos, construir rutas, etc.


#Pandas se utiliza para trabajar con datos en forma de tablas mediante objetos llamados DataFrame
import pandas as pd

#Aquí guardamos en la variable DATASET la ruta del archivo que vamos a analizar.
DATASET = Path(
    'data/raw/datos_1.jsonl'
)

#Aquí definimos otra ruta:
OUTPUT_DIR = Path('data/processed')

#Esta línea crea la carpeta: data/processed si todavía no existe.
# parents=True -> crea también las carpetas superiores si hacen falta.
# exist_ok=True -> si la carpeta ya existe, no des error.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Pandas lee el archivo JSONL y lo convierte en un DataFrame.
# lines=True -> indica que cada línea del archivo es un JSON independiente.
df = pd.read_json(DATASET, lines=True)


#{..."event_index":1065,"tick":50143,"type":"hunt_completed","villager_id":1166,"prey_type":"deer"}
# Evento para caceria terminada
print("Cacerias: ")
cacerias = df[df["type"] == "hunt_completed"]

print(cacerias[
    ["event_index", "tick", "villager_id", "prey_type"]
])



def event_table(event_type, columns):

    # lista con las columnas que siempre queremos y además las que hayas pasado a la función.
    selected = ['run_id', 'event_index', 'tick', *columns]

    # Esta parte evita errores si alguna columna no existe.

    available = [
        column for column in selected
        if column in df.columns
    ]


    # Aquí hacemos dos operaciones al mismo tiempo: Filtrar filas y seleccionar columnas.
    # "dame las filas cuyo type sea igual al evento que busco, pero únicamente con las columnas de available"
    # Así que aunque el DataFrame original tenga 30 columnas, nuestra tabla podría quedarse con solo 4, las que hemos indicado.
    # .copy() se usa para crear una copia independiente de los datos que acabas de seleccionar,
    # sin .copy(), Pandas a veces puede tratar esa selección como una especie de vista del DataFrame original, no como una tabla
    # totalmente independiente, pudiendo ocasionar conflictos si modificamos algo.
    table = df.loc[
        df['type'] == event_type,
        available,
    ].copy()


    if not table.empty:
        # Creamos una nueva columna simulation_day y su valor es la división
        # entre table['tick'] y 12000, que nos permite sacar cuantos días han transcurrido
        # En NevWorld 12000 ticks es un día.
        table['simulation_day'] = table['tick'] // 12000

    return table

# Crear las tablas python
# Creamos las tablas usando la anterior función indicando el tipo de evento que queremos.
# obtener y las columnas que nos puedan interesar.

tables = {
    # hunts será el nombre de nuestra tabla/CSV.
    # hunt_completed es el type real del evento.
    "hunts": event_table("hunt_completed", [
        "villager_id",
        "prey_type"
    ])
}

hunts = tables["hunts"]

# fijo las columnas
columnas_de_salida = [
    "run_id",
    "event_index",
    "tick",
    "villager_id",
    "prey_type",
    "simulation_day"
]

# Fija las columnas y su orden.
# Si alguna no existe, Pandas la crea vacía.
hunts = hunts.reindex(columns=columnas_de_salida)

# Actualizamos también el valor guardado en el diccionario.
tables["hunts"] = hunts

# Número real de hunt_completed que existen en el RAW.
cantidad_cacerias = (df["type"] == "hunt_completed").sum()

# El CSV debe tener exactamente una fila
# por cada hunt_completed.
assert len(hunts) == cantidad_cacerias, \
    "El número de cacerías no coincide"


# No puede repetirse la pareja run_id + event_index.
assert not hunts.duplicated(
    ["run_id", "event_index"]
).any(), "Hay eventos de caza duplicados"


# Estas columnas son obligatorias si existe una cacería.
campos_obligatorios = [
    "run_id",
    "event_index",
    "tick",
    "villager_id",
    "prey_type"
]

if not hunts.empty:

    # Ninguno de los campos obligatorios puede tener NaN.
    assert hunts[
        campos_obligatorios
    ].notna().all().all(), \
        "Hay campos obligatorios ausentes"

    # Comprobamos que simulation_day se calculó correctamente.
    assert (
        hunts["simulation_day"]
        == hunts["tick"] // 12000
    ).all(), "simulation_day es incorrecto"


# Exportar

output = OUTPUT_DIR / "hunts.csv"

# index=False evita guardar el índice interno de Pandas.
hunts.to_csv(output, index=False)

# El ejercicio pide mostrar la ruta y número de filas.
print("Archivo generado:", output)
print("Número de filas:", len(hunts))