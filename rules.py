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


@mcp.resource("info://dev-name")
def get_dev_name() -> str:
    return "el desarrollador se llama Juan Diego"


@mcp.tool("get_users")
def get_users():
    "Esta tools retorna los usuarios de la base de datos"
    with connect(PG_URI) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    Select * from users.user;
                    """
            )
            result = cursor.fetchall()
            return result


if __name__ == "__main__":
    mcp.run()
