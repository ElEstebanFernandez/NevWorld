from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


#### 1. Preparar las rutas y cargar las tablas procesadas.

DATA_DIR = Path('data/processed')
CHARTS_DIR = Path('reports/charts')

# Si se ejecuta desde la carpeta del script en el IDE, completamos las rutas
# desde la raíz de bigdata-game.
if not DATA_DIR.exists():
    PROJECT_DIR = Path(__file__).resolve().parents[3]
    DATA_DIR = PROJECT_DIR / DATA_DIR
    CHARTS_DIR = PROJECT_DIR / CHARTS_DIR

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

snapshots = pd.read_csv(DATA_DIR / 'snapshots.csv')
activities = pd.read_csv(DATA_DIR / 'activities.csv')
needs = pd.read_csv(DATA_DIR / 'needs.csv')
social = pd.read_csv(DATA_DIR / 'social.csv')


#### 2. Representar la evolución de los recursos.

# Ordena las fotografías por tiempo antes de unir sus valores.
ordered = snapshots.sort_values('tick')

if ordered.empty:
    print('No hay snapshots para crear el gráfico de recursos.')
else:
    # Crea una figura: figsize indica ancho y alto en pulgadas.
    plt.figure(figsize=(10, 5))

    # Dibuja cada línea y asigna su nombre para la leyenda.
    plt.plot(ordered['tick'], ordered['wood_stock'], label='Madera')
    plt.plot(ordered['tick'], ordered['food_stock'], label='Comida')
    plt.plot(ordered['tick'], ordered['gold_stock'], label='Oro')

    plt.title('Evolución de los recursos')
    plt.xlabel('Tick')
    plt.ylabel('Cantidad disponible')
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '01_resources_timeline.png')
    plt.close()


#### 3. Representar la distribución de actividades.

activity_counts = activities['activity'].value_counts()

if activity_counts.empty:
    print('No hay actividades para crear el gráfico.')
else:
    plt.figure(figsize=(10, 5))
    activity_counts.plot.bar(color='steelblue')
    plt.title('Cambios de actividad registrados')
    plt.xlabel('Actividad')
    plt.ylabel('Número de eventos')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '02_activities.png')
    plt.close()


#### 4. Representar las necesidades críticas.

critical = needs[needs['state'] == 'critical']
critical_counts = critical['need_type'].value_counts()

if critical_counts.empty:
    print('No hay necesidades críticas para crear el gráfico.')
else:
    plt.figure(figsize=(7, 4))
    critical_counts.plot.bar(color='darkorange')
    plt.title('Necesidades que alcanzaron estado crítico')
    plt.xlabel('Necesidad')
    plt.ylabel('Número de eventos')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '03_critical_needs.png')
    plt.close()


#### 5. Representar los tipos de interacción social.

interaction_counts = social['interaction_type'].value_counts()

if interaction_counts.empty:
    print('No hay interacciones sociales para crear el gráfico.')
else:
    plt.figure(figsize=(8, 4))
    interaction_counts.plot.bar(color='seagreen')
    plt.title('Tipos de interacción social')
    plt.xlabel('Interacción')
    plt.ylabel('Número de eventos')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '04_social_interactions.png')
    plt.close()
