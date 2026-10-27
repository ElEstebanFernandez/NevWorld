"""Crea un dashboard comparativo a partir del lote de la fase 06.

Ejecutar desde bigdata-game:
python scripts/actividades_1/fase07/07_dashboard.py
"""

from pathlib import Path

import matplotlib

# Generamos archivos sin necesitar una ventana gráfica abierta.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd


RAW_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')
EVENTS_FILE = OUTPUT_DIR / 'all_events.parquet'


def category_counts(table, column):
    """No ocultar registros cuya categoría falta."""
    return table[column].fillna('Sin informar').value_counts()


def main():
    if not EVENTS_FILE.exists():
        raise FileNotFoundError(f'No se encuentra: {EVENTS_FILE}')
    events = pd.read_parquet(EVENTS_FILE)
    required = ['run_id', 'event_index', 'tick', 'type']
    if not set(required).issubset(events.columns):
        raise ValueError('Faltan columnas comunes del lote')
    if events.empty or events[required].isna().any().any():
        raise ValueError('El lote está vacío o tiene campos comunes sin informar')
    events['run_id'] = events['run_id'].astype(str)
    if events.duplicated(['run_id', 'event_index']).any():
        raise ValueError('Hay eventos duplicados dentro de una partida')

    optional = ['population', 'constructed_buildings', 'wood_stock', 'food_stock',
                'activity', 'state', 'need_type', 'interaction_type']
    events = events.reindex(columns=list(dict.fromkeys([*events.columns, *optional])))

    # Cada sesión mantiene su propia escala temporal y sus propios eventos.
    sessions = []
    records = []
    for number, (run_id, data) in enumerate(events.groupby('run_id', sort=True), 1):
        label = f'Partida {number}'
        snapshots = data[data['type'] == 'world_snapshot'].sort_values(['tick', 'event_index'])
        activities = data[data['type'] == 'villager_activity_changed']
        needs = data[data['type'] == 'villager_need_changed']
        critical = needs[needs['state'] == 'critical']
        social = data[data['type'] == 'social_interaction']

        record = {
            'partida': label, 'run_id': run_id, 'events': len(data),
            'first_tick': data['tick'].min(), 'last_tick': data['tick'].max(),
            'snapshots': len(snapshots), 'activity_events': len(activities),
            'critical_events': len(critical), 'social_events': len(social),
            'need_events_without_state': int(needs['state'].isna().sum()),
            'first_snapshot_tick': None, 'last_snapshot_tick': None,
        }
        for field in ['population', 'constructed_buildings', 'wood_stock', 'food_stock']:
            # Un valor desconocido queda ausente: no se sustituye por cero.
            record[f'{field}_initial'] = snapshots.iloc[0][field] if len(snapshots) else None
            record[f'{field}_final'] = snapshots.iloc[-1][field] if len(snapshots) else None
        if len(snapshots):
            record['first_snapshot_tick'] = snapshots.iloc[0]['tick']
            record['last_snapshot_tick'] = snapshots.iloc[-1]['tick']

        records.append(record)
        sessions.append((label, snapshots, category_counts(activities, 'activity'),
                         category_counts(critical, 'need_type'),
                         category_counts(social, 'interaction_type')))


    # Las mismas categorías y escalas en cada fila facilitan la comparación.
    categories = []
    for index in [2, 3, 4]:
        names = sorted({name for session in sessions for name in session[index].index})
        categories.append(names)

    fig, axes = plt.subplots(6, len(sessions), figsize=(6 * len(sessions), 23),
                             squeeze=False, sharey='row')
    fig.suptitle(f'NevWorld · Comparación de {len(sessions)} partidas', fontsize=23, weight='bold')

    def empty(ax, message):
        ax.text(0.5, 0.5, message, ha='center', va='center',
                transform=ax.transAxes, color='#64748b', wrap=True)

    def value(number):
        return 'Sin datos' if pd.isna(number) else f'{number:g}'

    for col, ((label, snapshots, activities, critical, social), record) in enumerate(zip(sessions, records)):
        # Primera fila: contexto y valores extremos para interpretar los gráficos.
        ax = axes[0, col]
        ax.axis('off')
        ax.set_title(label, fontsize=19, weight='bold', pad=15)
        lines = [
            f"Eventos: {record['events']:,} · Snapshots: {record['snapshots']}",
            f"Ticks registrados: {value(record['first_tick'])} → {value(record['last_tick'])}",
            f"Ticks de snapshots: {value(record['first_snapshot_tick'])} → {value(record['last_snapshot_tick'])}",
            '',
            f"Población: {value(record['population_initial'])} → {value(record['population_final'])}",
            f"Edificios: {value(record['constructed_buildings_initial'])} → {value(record['constructed_buildings_final'])}",
            f"Madera: {value(record['wood_stock_initial'])} → {value(record['wood_stock_final'])}",
            f"Comida: {value(record['food_stock_initial'])} → {value(record['food_stock_final'])}",
            f"Necesidades sin estado informado: {record['need_events_without_state']}",
        ]
        ax.text(0.03, 0.92, '\n'.join(lines), va='top', fontsize=11, linespacing=1.7,
                transform=ax.transAxes)

        # Filas 2 y 3: evoluciones independientes, con escalas comunes entre partidas.
        for row, fields, title, unit in [
            (1, [('population', 'Población', '#2563eb'),
                 ('constructed_buildings', 'Edificios', '#7c3aed')], 'Población y edificios', 'Cantidad'),
            (2, [('wood_stock', 'Madera', '#a16207'),
                 ('food_stock', 'Comida', '#059669')], 'Reservas registradas', 'Unidades'),
        ]:
            ax = axes[row, col]
            for field, legend, color in fields:
                if snapshots[field].notna().any():
                    # Marcadores visibles incluso cuando solo existe un snapshot.
                    ax.plot(snapshots['tick'], snapshots[field], label=legend,
                            color=color, marker='.', markersize=3)
            if ax.lines:
                ax.legend(fontsize=9)
            else:
                empty(ax, 'Sin snapshots con valores disponibles')
            ax.set(title=title, xlabel='Tick de la partida', ylabel=unit)


            # Filas 4 a 6: todos los tipos registrados, incluidos los de otras sesiones.
        for row, counts, names, title, color in [
            (3, activities, categories[0], 'Cambios de actividad', '#2563eb'),
            (4, critical, categories[1], 'Eventos de necesidad crítica', '#ea580c'),
            (5, social, categories[2], 'Interacciones sociales', '#059669'),
        ]:
            ax = axes[row, col]
            if names:
                values = counts.reindex(names, fill_value=0)
                bars = ax.bar(range(len(names)), values, color=color)
                ax.set_xticks(range(len(names)), names, rotation=40, ha='right', fontsize=9)
                ax.bar_label(bars, labels=[str(int(v)) if v else '' for v in values], padding=3, fontsize=9)
            if counts.empty:
                empty(ax, 'Sin eventos registrados de este tipo')
            ax.set(title=title, ylabel='Eventos (recuento)')
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # Homogeneizamos también el eje temporal: no conectamos sesiones entre sí.
    for row in [1, 2]:
        lo, hi = events['tick'].min(), events['tick'].max()
        for ax in axes[row]:
            ax.set_xlim(lo, hi if hi > lo else lo + 1)
    for row in range(1, 6):
        for ax in axes[row]:
            ax.grid(axis='y', alpha=0.2)
            ax.set_axisbelow(True)
            ax.margins(y=0.18)

    fig.text(0.5, 0.018,
             'Snapshot = registro del estado del mundo en un instante. Las flechas resumen el primer y último snapshot.\n'
             'Recuentos brutos: las partidas pueden tener distinta duración y población. No miden tiempo dedicado ni eficiencia.\n'
             'La última observación puede no coincidir con el final real de la partida. Identificadores completos en el CSV.',
             ha='center', fontsize=11, color='#475569')
    fig.tight_layout(rect=(0, 0.065, 1, 0.975), h_pad=3, w_pad=3)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output = REPORTS_DIR / 'nevworld_dashboard_C.png'
    fig.savefig(output, dpi=160)
    fig.savefig(REPORTS_DIR / 'nevworld_dashboard_C.pdf')
    plt.close(fig)

    summary = pd.DataFrame(records)
    summary.to_csv(REPORTS_DIR / 'dashboard_C_kpis.csv', index=False)
    print(summary[['partida', 'events', 'snapshots', 'critical_events', 'social_events']].to_string(index=False))
    print('Dashboard:', output)


if __name__ == '__main__':
    main()
