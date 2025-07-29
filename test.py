from psycopg2 import connect
from dotenv import load_dotenv
from os import getenv

load_dotenv()


DB_USER = getenv("DB_USER")
DB_HOST = getenv("DB_HOST")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_PORT = getenv("DB_PORT")
DB_NAME = getenv("DB_NAME")
PG_URI = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


with connect(PG_URI) as conn:
    with conn.cursor() as cursor:
        query = """
            SELECT
                table_schema, table_name, column_name 
            FROM information_schema.columns
            WHERE table_schema NOT IN ('public', 'pg_catalog', 'information_schema');
        """
        cursor.execute(query)
        result = cursor.fetchall()

        data = {}
        for schema, table, column in result:
            if schema not in data:
                data[schema] = {}
            if table not in data[schema]:
                data[schema][table] = []
            data[schema][table].append(column)

        print(data)
