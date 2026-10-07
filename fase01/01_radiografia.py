from pathlib import Path
import pandas as pd




DATASET = Path("data/raw/nevworld_1150427077545796967_20261007_070934.jsonl")

if not DATASET.exists():
    raise FileNotFoundError(
        f"No se encuentra el archivo: {DATASET.resolve()}"
    )

df = pd.read_json(DATASET, lines=True)

filas, columnas = df.shape

assert not df.empty, "El dataset está vacío"

#Valido

print("COMPROBACIÓN:")

required = [
    "run_id",
    "event_index",
    "tick",
    "type"
]

# Comprobar que existen las columnas principales
assert all(columna in df.columns for columna in required), \
    "Faltan columnas principales"

# Comprobar que no hay eventos duplicados
assert not df.duplicated(["run_id", "event_index"]).any(), \
    "Hay eventos duplicados"

# Comprobar que los ticks no retroceden dentro de cada partida
for run_id, grupo in df.groupby("run_id"):
    ordered = grupo.sort_values("event_index")

    assert ordered["tick"].is_monotonic_increasing, \
        f"Los ticks retroceden en el run_id {run_id}"

print("\nVALIDACIÓN BÁSICA: OK ************\n")



print("DATOS DE MI PARTIDA")

print("Nombre del archivo JSONL:", DATASET.name)

print("Número total de eventos:", filas)

print("Número de columnas:", columnas)

print("\nNOMBRES DE LAS COLUMNAS:")
for clave , valor in df.items():
    print(clave)
print("\n")

# Primer evento

primer_evento = df["type"].iloc[0]

print("\nTipo del primer evento registrado:")
print(primer_evento)
print("\n")


# Eventos por tipo

eventos_por_tipo = df["type"].value_counts()
print("Eventos por tipo: ",len(eventos_por_tipo))

tipo_mas_frecuente = eventos_por_tipo.index[0]
cantidad_mas_frecuente = eventos_por_tipo.iloc[0]

print("\nTipo de evento más frecuente:")
print(tipo_mas_frecuente, "-", cantidad_mas_frecuente)


print("\nRECUENTO DE TODOS LOS TIPOS DE EVENTO:")
print(eventos_por_tipo)
print("\n")



# Primera fila

primera_fila = df.iloc[0]

print("\nDATOS DE LA PRIMERA FILA:")

print("run_id:", primera_fila["run_id"])

if "seed" in df.columns:
    print("Semilla:", primera_fila["seed"])

if "schema_version" in df.columns:
    print("Versión del esquema:", primera_fila["schema_version"])

print("\n")

# Rango tick

tick_minimo = df["tick"].min()
tick_maximo = df["tick"].max()

print("\nTick mínimo:", tick_minimo)
print("Tick máximo:", tick_maximo)
print("\n")

# Resumen

print("RESUMEN")

print(f"Archivo: {DATASET.name}")
print(f"Total de eventos: {filas}")
print(f"Total de columnas: {columnas}")
print(f"Primer evento: {primer_evento}")
print(
    f"Evento más frecuente: "
    f"{tipo_mas_frecuente} ({cantidad_mas_frecuente} veces)"
)
print(f"Ticks: {tick_minimo} - {tick_maximo}")
print("Resultado de las validaciones: VALIDACIÓN OK")


