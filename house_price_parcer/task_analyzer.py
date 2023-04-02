import json
import numpy as np
import matplotlib
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import pik_database


db = pik_database.Database()
timestamps, labels = db.get_timestamps()
t0 = timestamps[0]
days_count = int((timestamps[-1]-timestamps[0])/24/3600) + 2

with open('projects.json', 'r') as f:
    project_names = json.load(f)

counts = db.get_number_of_projects_in_sessions(timestamps)

legend = []
cmap = matplotlib.cm.get_cmap('tab10')

fig1, ax1 = plt.subplots()
fig1.set_size_inches([16, 4.8])

for p, prj in enumerate(db.get_project_names()):
    flat_ids = db.get_most_exposed_flats(prj)
    for flat_id in flat_ids:
        prices, timestamps = db.get_price_change(flat_id)
        timestamps = (timestamps - t0)/3600/24

        prices = (prices/prices[0] - 1) * 100
        legend.append('{0} ({1})'.format(project_names[prj], flat_id))
        plt.plot(timestamps, prices, '.-', color=cmap(p),
                 linewidth=1.5, markersize=3)

plt.xlabel('День')
plt.ylabel('Изменение, %')
plt.ylim([-8, 12])
_, _, ymin, ymax = plt.axis()
plt.yticks(np.arange(ymin, ymax+1))
plt.xticks(np.arange(0, days_count, 2), rotation=45)
plt.grid(True)
plt.title(datetime.now().strftime('%Y-%m-%d  %H:%M:%S'))

plt.legend(legend, loc='upper left', ncol=2)
plt.savefig('output/output.png', dpi=300)

fig2, ax2 = plt.subplots()
fig2.set_size_inches([16, 4.8])
legend = []

with open('favourites.json', 'r') as f:
    favourites = json.load(f)

for i, favourite in enumerate(favourites):
    prices, timestamps = db.get_price_change(favourite['id'])
    timestamps = (timestamps - t0)/3600/24
    prices = prices / 1000

    legend.append('{0} ({1})'.format(favourite['comment'], favourite['id']))
    plt.plot(timestamps, prices, '.-', color=cmap(i),
             linewidth=1.5, markersize=3)

plt.legend(legend, loc='lower right')
plt.ylabel('Цена, тыс.руб.')
plt.xticks(np.arange(0, days_count, 2), rotation=45)
plt.grid(True)
plt.title(datetime.now().strftime('%Y-%m-%d  %H:%M:%S'))

plt.savefig('output/favourites.png', dpi=300)  # render figure before set_xtick

for ax in [ax1, ax2]:
    labels = [item.get_text() for item in ax.get_xticklabels()]
    labels_int = [int(s.replace('−', '-')) for s in labels]
    t0_datetime = datetime.fromtimestamp(t0)
    labels_dt = [t0_datetime + timedelta(days=d) for d in labels_int]
    labels_txt = [dt.strftime('%d %b') for dt in labels_dt]
    ax.set_xticklabels(labels_txt)

fig1.savefig('output/output.png', dpi=300)
fig2.savefig('output/favourites.png', dpi=300)
plt.show()
