import pik_parser
import pik_database

p = pik_parser.Parser()
db = pik_database.Database()

projects = pik_parser.load_project_list()

filename = 'temp.html'

for project in projects:
    p.download_html(project)
    pairs = p.get_id_price_pairs()
    for price, flat_id in pairs:
        db.write(project, price, flat_id)
    p.put_to_archive(project)

db.save_changes()
