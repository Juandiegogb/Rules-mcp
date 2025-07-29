from psycopg2 import connect
from mcp.server import FastMCP
from dotenv import load_dotenv
from os import getenv
import logging
from typing import Dict, List, Tuple, Any

load_dotenv()


DB_USER = getenv("DB_USER")
DB_HOST = getenv("DB_HOST")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_PORT = getenv("DB_PORT")
DB_NAME = getenv("DB_NAME")

mcp = FastMCP("rules")
PG_URI = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.resource("fields://database-fields")
def get_new_field_names() -> Dict[str, Dict[str, List[str]]]:
    """
    Este resource retorna un diccionario con los schemas, tablas y columnas presentes
    en la base de datos.

    Returns:
        Dict[str, Dict[str, List[str]]]: Diccionario con la estructura:
            {
                "schema": {
                    "table": ["column1", "column2", ...],
                    ...
                },
                ...
            }
    """
    try:
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
                return data
    except Exception as e:
        logger.error(f"Error al conectar o consultar la base de datos: {e}")
        return "Error: No se pudo obtener la información de la base de datos."


@mcp.tool("query")
def execute_query(query: str) -> List[Tuple[Any,...]]:
    """
    Esta tool permite realizar queries a la base de datos tomando como contexto
    los schemas, tablas y campos del recurso respectivo.

    Args:
        query: Query que se desea ejecutar en la DB

    Returns:
        List[Tuple[Any]]

    """
    with connect(PG_URI) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


@mcp.tool("update_rule")
def update_rule(rule_id: str, rule_content):
    """
    Esta tool permite actualizar el contenido de una regla despues de la revisión del LLM

    Args:

        rule_id: UUID de la regla que se va a actualizar
        rule_content: Regla revisada y con los cambios realizados por el LLM
    """
    with connect(PG_URI) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "update test.old_rules set new_rule = %s , checked = True , updated_at = now() where id = %s;",
                (rule_content, rule_id),
            )
        conn.commit()


if __name__ == "__main__":
    mcp.run()
