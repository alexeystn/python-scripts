import json
import pik_parser
import pik_database

db = pik_database.Database()

with open('projects.json', 'r') as f:
    projects = json.load(f)

for project in projects:
    pairs = pik_parser.download_id_price_pairs(project, archive_enabled=True)
    for price, flat_id in pairs:
        db.write(project['url'], price, flat_id)

db.save_changes()
