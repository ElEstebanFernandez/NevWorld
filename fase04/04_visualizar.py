from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd


RAW_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')
CHARTS_DIR = REPORTS_DIR / 'charts'
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

snapshots = pd.read_csv(OUTPUT_DIR / 'snapshots.csv')
activities = pd.read_csv(OUTPUT_DIR / 'activities.csv')
needs = pd.read_csv(OUTPUT_DIR / 'needs.csv')
social = pd.read_csv(OUTPUT_DIR / 'social.csv')

ordered = snapshots.sort_values(['tick', 'event_index'])
if not ordered.empty:
    plt.figure(figsize=(10, 5))
    for column, label in [('wood_stock', 'Madera'), ('food_stock', 'Comida'),
                          ('gold_stock', 'Oro')]:
        plt.plot(ordered['tick'], ordered[column], label=label)
    plt.title('Evolucion de los recursos')
    plt.xlabel('Tick')
    plt.ylabel('Cantidad disponible')
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '01_resources_timeline.png')
    plt.close()

charts = [
    (activities['activity'].value_counts(), 'Cambios de actividad registrados',
     'Actividad', '02_activities.png', 'steelblue'),
    (needs.loc[needs['state'].eq('critical'), 'need_type'].value_counts(),
     'Necesidades que alcanzaron estado critico', 'Necesidad',
     '03_critical_needs.png', 'darkorange'),
    (social['interaction_type'].value_counts(), 'Tipos de interaccion social',
     'Interaccion', '04_social_interactions.png', 'seagreen'),
]
for counts, title, xlabel, filename, color in charts:
    if counts.empty:
        print('Sin datos para:', title)
        continue
    plt.figure(figsize=(9, 4))
    counts.plot.bar(color=color)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('Numero de eventos')
    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / filename)
    plt.close()
