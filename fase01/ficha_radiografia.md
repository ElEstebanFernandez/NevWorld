# Radiografía de una partida de NevWorld

Has terminado una partida y el juego ha generado un archivo JSONL. Tu misión es abrirlo con pandas y preparar una ficha que permita a otra persona comprender qué contiene ese registro.

Utiliza **los datos de tu propia partida** y las operaciones vistas en el tema. No modifiques el archivo RAW.

## Teoría de apoyo

JSONL guarda un evento en cada línea. pandas lo carga con `pd.read_json(..., lines=True)` en un **DataFrame**, una tabla de filas y columnas. La variable `df` recibe ese nombre como abreviatura de DataFrame: cada fila representa un evento y cada columna, un campo.

| Para… | Utiliza… |
| --- | --- |
| Representar y comprobar la ruta | `Path(...)` y `exists()` |
| Ver los primeros eventos | `df.head()` |
| Obtener filas y columnas | `df.shape` |
| Consultar los nombres de los campos | `df.columns.tolist()` |
| Contar eventos de cada tipo | `df['type'].value_counts()` |
| Leer un valor de la primera fila | `df['campo'].iloc[0]` |
| Obtener los extremos de los ticks | `df['tick'].min()` y `max()` |

Los eventos pueden tener campos diferentes: un `NaN` representa una ausencia, no necesariamente un error ni un cero. El tick mide tiempo simulado; varios eventos pueden compartirlo.

## Enunciado

Crea `scripts/actividades/01_radiografia.py` en tu proyecto `bigdata-game`. Carga el JSONL que has guardado en `data/raw`, comprobando antes que la ruta existe. Puedes apoyarte en el script del tema.

Aplica las cuatro validaciones básicas del tema: que la tabla no esté vacía, que existan las columnas principales, que no se repita la pareja `run_id` y `event_index`, y que los ticks no retrocedan al ordenar por `event_index`. Hazlo antes de consultar la primera fila.

Después, muestra las primeras filas y obtén los datos necesarios para completar esta ficha:

| Dato de mi partida | Resultado |
| --- | --- |
| Nombre del archivo JSONL | `nevworld_1150427077545796967_20261007_070934.jsonl` |
| Número total de eventos | 7.013 |
| Número de columnas | 36 |
| Nombres de las columnas | `schema_version`, `run_id`, `seed`, `event_index`, `tick`, `type`, `started_at_utc`, `building_id`, `building_type`, `cell_x`, `cell_y`, `width`, `height`, `villager_id`, `activity`, `resource_type`, `amount_before`, `amount_after`, `amount_delta`, `population`, `constructed_buildings`, `wood_stock`, `food_stock`, `gold_stock`, `day`, `actor_id`, `target_id`, `interaction_type`, `topic`, `relationship_actor_to_target_after`, `relationship_target_to_actor_after`, `need_type`, `state`, `prey_type`, `name`, `age` |
| Tipo del primer evento registrado | `simulation_started` |
| Tipo de evento más frecuente y cantidad | `villager_activity_changed`: 4.331 |
| Recuento de todos los tipos de evento | `villager_activity_changed`: 4.331; `villager_need_changed`: 769; `resource_changed`: 558; `world_snapshot`: 501; `social_interaction`: 351; `villager_drank`: 148; `villager_ate`: 116; `construction_abandoned`: 97; `hunt_completed`: 64; `construction_expired`: 42; `building_created`: 29; `villager_created`: 5; `simulation_started`: 1; `age_changed`: 1 |
| `run_id`, semilla y versión del esquema de la primera fila | `20261007_070934_1150427077545796967_ff0aa8620a704dcf8c0832b521d2af20`; `1150427077545796967`; 2 |
| Tick mínimo y tick máximo | 0 y 300.674 |
| Resultado de las validaciones | OK |

Termina la ficha respondiendo con tus palabras:

1. ¿Qué te permite afirmar el recuento sobre tu partida? ¿Por qué el tipo más frecuente no tiene que ser el más importante?
2. ¿Por qué una celda vacía no significa necesariamente que el registro esté mal?
3. ¿Qué sabes ahora del archivo y qué pregunta sobre tu partida necesitaría un análisis posterior?

1. Predominan los cambios de actividad (4.331), pero frecuencia no equivale a importancia.
2. Cada tipo de evento usa campos distintos; un vacío puede ser un dato no aplicable.
3. Sé su tamaño, estructura y distribución de eventos; faltaría analizar, por ejemplo, cómo evolucionaron los recursos.

Ejecuta desde la raíz de `bigdata-game`, con el entorno de Python que tenga pandas instalado:

```powershell
python scripts/actividades/01_radiografia.py
```

**Entrega:** Cread un repositorio en Github con una carpeta llamada NevWorld, y una subcarpeta llamada fase01, en la que incluiréis el script y la ficha en un archivo de texto, con tus respuestas y resultados reales. Si alguna validación falla, anota el error y explica qué comprobación no se cumple; no alteres el RAW para hacerla pasar.
