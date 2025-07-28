from psycopg2 import connect
from mcp.server import FastMCP
from dotenv import load_dotenv
from os import getenv
import logging


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
def get_new_field_names():
    """Retorna una lista de nombres de campos de la base de datos en el formato
    schema__table__column, excluyendo esquemas públicos y de sistema.

    Returns:
        List: una lista con los nombres de los campos de la base de datos
    """
    try:
        with connect(PG_URI) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        TABLE_SCHEMA || '__' || TABLE_NAME || '__' || COLUMN_NAME as field_name
                    FROM INFORMATION_SCHEMA.COLUMNS C
                    WHERE
                        TABLE_SCHEMA NOT IN ( 'public', 'pg_catalog', 'information_schema' )
                    order by TABLE_SCHEMA;
                    """
                )
                result = [field_name for (field_name,) in cursor.fetchall()]
                return result
    except Exception as e:
        logger.error(f"Error al conectar o consultar la base de datos: {e}")
        return "Error: No se pudo obtener la información de la base de datos."


@mcp.resource("tables://database-tables")
def get_table_names():
    """Retorna una lista de nombres de tablas de la base de datos en el formato
    schema.table, excluyendo esquemas públicos y de sistema.

    Returns:
        List: una lista con los nombres de las tablas de la base de datos
    """
    try:
        with connect(PG_URI) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        TABLE_SCHEMA || '.' || TABLE_NAME as table_name
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE
                        TABLE_SCHEMA NOT IN ('public', 'pg_catalog', 'information_schema')
                    ORDER BY TABLE_SCHEMA, TABLE_NAME;
                    """
                )
                result = [table_name for (table_name,) in cursor.fetchall()]
                return result
    except Exception as e:
        logger.error(
            f"Error al conectar o consultar las tablas de la base de datos: {e}"
        )
        return "Error: No se pudo obtener la información de las tablas."


@mcp.tool(
    "query", description="Esta tool permite hacer read-only queries a la base de datos"
)
def execute_query(query: str) -> list[tuple]:
    with connect(PG_URI) as conn:
        with conn.cursor() as cursor:
            cursor.execute("BEGIN READ ONLY;")
            cursor.execute(query)
            return cursor.fetchall()


@mcp.prompt(
    "Estructura de corrección de reglas",
    description="Este prompt permite optener contexto de como se espera que se modifiquen las reglas de javascript",
)
def rules_prompt():
    with open("rules_prompt.md", "r") as file:
        return file.read()


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
