| Dato de mi partida | Resultado |
| --- | --- |
| Nombre del archivo JSONL | nevworld_1150427077545796967_20261007_070934.jsonl |
| Número total de eventos | 7013 |
| Número de columnas | 36 |
| Tipo del primer evento registrado | simulation_started |
| Tipo de evento más frecuente y cantidad | villager_activity_changed (4331 veces) |
| Recuento de todos los tipos de evento | 14 |
| `run_id`, semilla y versión del esquema de la primera fila  | run_id: 20261007_070934_1150427077545796967_ff0aa8620a704dcf8c0832b521d2af20<br>Semilla: 1150427077545796967<br>Versión del esquema: 2 |
| Tick mínimo y tick máximo | 0 - 300674 |
| Resultado de las validaciones | VALIDACIÓN OK |

### Nombres de las columnas

- schema_version
- run_id
- seed
- event_index
- tick
- type
- started_at_utc
- building_id
- building_type
- cell_x
- cell_y
- width
- height
- villager_id
- activity
- resource_type
- amount_before
- amount_after
- amount_delta
- population
- constructed_buildings
- wood_stock
- food_stock
- gold_stock
- day
- actor_id
- target_id
- interaction_type
- topic
- relationship_actor_to_target_after
- relationship_target_to_actor_after
- need_type
- state
- prey_type
- name
- age

1) Se han producido 14 tipos de eventos diferentes. El más frecuente es villager_activity_changed, con 4331 apariciones. Que sea el más frecuente no significa que sea el más importante, solo que es el que más veces se ha registrado.

2) Una celda puede estar vacía porque esa columna no está relacionada con el tipo de evento de esa fila. Cada tipo de evento utiliza solo las columnas que necesita.

3) Ahora sé que el archivo contiene 7013 eventos, 36 columnas y 14 tipos de eventos diferentes. También conozco el primer evento, el evento más frecuente y el rango de ticks. Para saber, por ejemplo, cómo evolucionaron los recursos durante la partida necesitaría hacer un análisis posterior.