import psycopg2
from dotenv import load_dotenv
from os import makedirs, getenv
from os.path import join, exists
import csv


load_dotenv()

DB_USER = getenv("DB_USER")
DB_HOST = getenv("DB_HOST")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_PORT = getenv("DB_PORT")
DB_NAME = getenv("DB_NAME")

conn = psycopg2.connect(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
cursor = conn.cursor()


query = """
    SELECT f.id, f.RULE , split_part(e.NAME,'.',1) as schema , lower(f.RETURN_DATATYPE) as event
    FROM SYST.FIELDRULEGLOBAL F
    inner join SYST.ENTITYCATAL E on F.ENTITYCATAL_ID = E.ID;
"""

cursor.execute(query)
rows = cursor.fetchall()


with open("field_names.csv", "r", encoding="utf-8") as file:
    names = list(csv.reader(file, delimiter=","))
for id, rule, schema, event in rows:
    for old_name, new_name in names:
        if new_name:
            rule = rule.replace(old_name, new_name)

    file_path = f"rules/{schema}/{event}"
    file_name = f"{id}.js"
    if not exists(file_path):
        makedirs(file_path)
    with open(join(file_path, file_name), "w", encoding="utf-8") as file_rules:
        file_rules.write(rule)

    cursor.execute("INSERT INTO test.new_rules(id, rule) VALUES (%s, %s);", (id, rule))


conn.commit()
cursor.close()
conn.close()
