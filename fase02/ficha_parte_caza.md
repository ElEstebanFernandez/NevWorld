# El parte de caza: Del registro a una tabla útil

El creador de NevWorld te ha encargado una nueva tabla: quiere consultar **qué aldeano completó una cacería, qué presa consiguió y cuándo ocurrió**. Las seis tablas vistas en la teoría no recogen directamente ese hecho.

Tu misión es diseñar y generar `hunts.csv`. Antes de programar, tendrás que demostrar por qué has elegido esos datos.

Trabaja con tu JSONL, conserva el RAW intacto y utiliza las operaciones vistas en clase.

## 1. Investiga antes de elegir

Consulta los tipos de evento de tu partida con `df['type'].value_counts()`. Localiza el que registra una cacería completada y busca una de sus líneas originales en el JSONL. Puedes buscar el texto en el editor.

No te quedes solo con el nombre del evento: lee sus campos. Copia un ejemplo real en tu entrega e identifica qué información contiene y cuál no.

Si tu partida no contiene cacerías completadas, pide un registro de práctica al profesor para inspeccionar un ejemplo. Tu script debe admitir que tu propio archivo no contenga ninguna y generar un CSV vacío con sus cabeceras. No inventes filas para llenarlo.

Completa esta ficha **antes de escribir la llamada a `event_table()`**:

| Pregunta | Campo o valor elegido | Justificación |
| --- | --- | --- |
| ¿Qué evento demuestra que la cacería terminó? | `hunt_completed` | Registra una cacería completada. |
| ¿Quién la completó? | `villager_id` | Identifica al aldeano. |
| ¿Qué presa aparece registrada? | `prey_type` | Indica el tipo de presa. |
| ¿Cuándo ocurrió? | `tick` | Sitúa el evento en el tiempo simulado. |
| ¿A qué partida pertenece? | `run_id` | Identifica la partida. |
| ¿Cómo localizo el evento original sin confundirlo con otro? | `run_id` + `event_index` | La pareja identifica el evento. |

Explica también por qué `activity`, `food_stock` y `amount_delta` no son necesarios para este parte. ¿Permite el evento saber por sí solo cuánta comida produjo la cacería?

No son necesarios para identificar cazador, presa y momento. El evento no indica por sí solo cuánta comida produjo.

Ejemplo RAW: `{"schema_version":2,"run_id":"20261007_070934_1150427077545796967_ff0aa8620a704dcf8c0832b521d2af20","seed":"1150427077545796967","event_index":1065,"tick":50143,"type":"hunt_completed","villager_id":1166,"prey_type":"deer"}`. Contiene partida, evento, momento, aldeano y presa, pero no cantidad de comida.

## 2. Construye la tabla

Crea `scripts/actividades/02_parte_caza.py` dentro de `bigdata-game`. Reutiliza la lectura del JSONL y la función `event_table()` del tema, copiando las partes necesarias a este script.

El programa debe:

1. Leer el RAW y crear `data/processed` si hace falta.
2. Seleccionar únicamente cacerías completadas y los campos justificados en tu ficha.
3. Conservar `run_id`, `event_index` y `tick`, que la función añade automáticamente.
4. Añadir `simulation_day` mediante `tick // 12000`.
5. Guardar `data/processed/hunts.csv` sin exportar el índice de pandas.
6. Mostrar la ruta del archivo generado y su número de filas.

**Condición adicional:** el CSV debe tener las mismas cabeceras aunque no haya cacerías. Revisa estas dos partes de la función del tema: el filtro de columnas `available` y el `if not table.empty`. Una columna ausente de todo el JSONL y una tabla sin filas son situaciones distintas.

Puedes usar esta operación para fijar las columnas de salida:

```python
# Conserva ese orden y crea con valores vacíos las columnas que falten.
table = table.reindex(columns=columnas_de_salida)
```

Si hay eventos de caza pero falta un campo obligatorio, debes avisar con una validación; añadir la columna vacía no repara el dato.

## 3. Demuestra que funciona

Comprueba con `assert`:

- El número de filas coincide con el número de eventos del tipo elegido en el RAW.
- No se repite la pareja `run_id`, `event_index`.
- Si hay filas, los campos que identifican partida, evento, momento, aldeano y presa no tienen valores ausentes.
- `simulation_day` coincide con la división entera indicada.

Ayudas de sintaxis:

```python
# Cuenta cuántas filas cumplen una condición.
cantidad = (df['type'] == 'TIPO_ELEGIDO').sum()

# Comprueba que los campos obligatorios no tengan celdas ausentes.
assert table[campos_obligatorios].notna().all().all()
```

Abre el CSV exportado. Elige dos filas —o todas si hay menos de dos— y localiza sus eventos originales mediante `run_id` y `event_index`. Comprueba aldeano, presa y tick. Anota la comparación; si no hay filas, explica qué has podido comprobar y qué no.

Comparación: los eventos 1065 y 1078 coinciden en RAW y CSV: aldeano 1166, presa `deer` y ticks 50.143 y 51.273. Validaciones: OK; 64 filas.

Ejecuta desde la raíz de `bigdata-game`, con el entorno de Python que tenga pandas:

```powershell
python scripts/actividades/02_parte_caza.py
```

## 4. Detecta las conclusiones que los datos no sostienen

Responde justificando cada decisión:

1. «Hay seis filas, por tanto hay seis cazadores distintos». ¿Es necesariamente cierto?
2. «Una fila indica que ese aldeano estuvo cazando durante todo el día». ¿Qué registra realmente la fila?
3. «Borro del DataFrame original todas las filas con algún `NaN` y después selecciono las cacerías». ¿Por qué puede desaparecer información válida?
4. «El CSV está vacío, así que nadie intentó cazar». ¿Qué puedes afirmar realmente sobre el registro?

1. No: hay 64 filas, pero solo 4 cazadores distintos.
2. Registra que completó una cacería en un tick, no que cazara todo el día.
3. Otros eventos tienen campos no aplicables como `NaN`; borrarlos antes puede eliminar cacerías válidas.
4. Solo permitiría afirmar que no hay cacerías completadas registradas, no que nadie lo intentara.

## Ampliación para l@s más rápid@s: obras que no llegaron a terminar

Diseña `construction_incidents.csv` para consultar **dónde y cuándo se registraron obras abandonadas o caducadas, conservando el motivo registrado**.

Investiga `construction_abandoned` y `construction_expired`. Esta vez necesitas dos tipos de evento en una tabla y debes conservar `type` para distinguirlos. Comprueba en el RAW si esos eventos incluyen `building_id` antes de darlo por supuesto.

Pista para filtrar varios tipos:

```python
mask = df['type'].isin(['TIPO_A', 'TIPO_B'])
```

Justifica las columnas, exporta sin índice y verifica el recuento. Explica por qué dos registros con las mismas coordenadas no demuestran, por sí solos, que se trate de la misma obra.

## Entrega y valoración

Mismos pasos que la Actividad 1. Entrega el script, `hunts.csv` y una ficha con el ejemplo RAW, tus decisiones de diseño, las comprobaciones y las cuatro respuestas. Si haces el reto, incluye también su CSV y justificación.
