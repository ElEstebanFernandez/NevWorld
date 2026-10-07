# El parte de caza

## 1. Investiga antes de elegir

Al consultar los tipos de evento con:

```python
df['type'].value_counts()
```

se encuentra que el evento que registra una cacería completada es `hunt_completed`.

Ejemplo real del JSONL:

```json
{"schema_version":2,"run_id":"20261007_070934_1150427077545796967_ff0aa8620a704dcf8c0832b521d2af20","seed":"1150427077545796967","event_index":1065,"tick":50143,"type":"hunt_completed","villager_id":1166,"prey_type":"deer"}
```

| Pregunta | Campo o valor elegido | Justificación |
| --- | --- | --- |
| ¿Qué evento demuestra que la cacería terminó? | `type = hunt_completed` | Este tipo de evento indica que una cacería ha finalizado. |
| ¿Quién la completó? | `villager_id` | Identifica al aldeano que completó la cacería. |
| ¿Qué presa aparece registrada? | `prey_type` | Indica el tipo de presa de la cacería. |
| ¿Cuándo ocurrió? | `tick` | Indica el momento de la simulación en el que ocurrió. |
| ¿A qué partida pertenece? | `run_id` | Identifica la partida a la que pertenece el evento. |
| ¿Cómo localizo el evento original sin confundirlo con otro? | `run_id` + `event_index` | La combinación permite identificar el evento concreto dentro de una partida. |

`activity` no es necesario porque indica la actividad de un aldeano, pero el evento `hunt_completed` ya indica que la cacería terminó.

`food_stock` no es necesario porque representa el stock de comida y no identifica la cacería completada.

`amount_delta` no es necesario porque representa el cambio en la cantidad de un recurso y no forma parte del evento `hunt_completed`.

El evento `hunt_completed` no permite saber por sí solo cuánta comida produjo la cacería, ya que no contiene ningún campo que indique esa cantidad.


## 2. Construye la tabla

Se genera la tabla `hunts` seleccionando únicamente los eventos `hunt_completed`.

Las columnas de salida son:

- `run_id`
- `event_index`
- `tick`
- `villager_id`
- `prey_type`
- `simulation_day`

`simulation_day` se calcula mediante la división entera de `tick` entre 12000.

El resultado se guarda en:

`data/processed/hunts.csv`

El CSV mantiene las mismas cabeceras aunque no haya ninguna cacería completada.


## 3. Demuestra que funciona

Se comprueba mediante `assert` que:

- El número de filas coincide con el número de eventos `hunt_completed` del RAW.
- No se repite la pareja `run_id`, `event_index`.
- Si existen filas, `run_id`, `event_index`, `tick`, `villager_id` y `prey_type` no tienen valores ausentes.
- `simulation_day` coincide con `tick // 12000`.

Una de las filas comprobadas corresponde al evento:

- `event_index`: 1065
- `tick`: 50143
- `villager_id`: 1166
- `prey_type`: deer

Los valores coinciden con el evento original del JSONL.


## 4. Detecta las conclusiones que los datos no sostienen

### 1. «Hay seis filas, por tanto hay seis cazadores distintos». ¿Es necesariamente cierto?

No. Cada fila representa una cacería completada. Un mismo aldeano puede completar varias cacerías y aparecer en varias filas.

### 2. «Una fila indica que ese aldeano estuvo cazando durante todo el día». ¿Qué registra realmente la fila?

No. La fila registra que el aldeano completó una cacería en el momento indicado por `tick`. No indica que estuviera cazando durante todo el día.

### 3. «Borro del DataFrame original todas las filas con algún `NaN` y después selecciono las cacerías». ¿Por qué puede desaparecer información válida?

Porque los distintos tipos de eventos utilizan campos diferentes. Un `NaN` puede indicar simplemente que ese campo no corresponde a ese tipo de evento. Al borrar todas las filas con algún `NaN` se pueden eliminar eventos válidos.

### 4. «El CSV está vacío, así que nadie intentó cazar». ¿Qué puedes afirmar realmente sobre el registro?

Solo se puede afirmar que no hay eventos `hunt_completed` registrados. No se puede afirmar que nadie intentara cazar.