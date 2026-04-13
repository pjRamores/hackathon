import oracledb
import os
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("Oracle-Developer")

# --- CONFIGURATION ---
# The DSN can be a TNS name or a connection string like "host:port/service_name"
# Ensure your TNS_ADMIN environment variable points to your tnsnames.ora/sqlnet.ora
ORACLE_DSN = os.getenv("ORACLE_DSN", "MY_TNS_SERVICE_NAME")

def get_connection():
    """
    Establish a connection using Kerberos cache.
    externalauth=True tells Oracle to look for a Kerberos ticket or OS user.
    """
    return oracledb.connect(
        dsn=ORACLE_DSN,
        externalauth=True
    )

@mcp.tool()
def list_tables():
    """List all tables owned by the current user."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Oracle-specific query for user tables
            cursor.execute("SELECT table_name FROM user_tables ORDER BY table_name")
            tables = [row[0] for row in cursor.fetchall()]
            return tables

@mcp.tool()
def describe_table(table_name: str):
    """Get columns, types, and nullability for an Oracle table."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            sql = """
                SELECT column_name, data_type, data_length, nullable
                FROM user_tab_columns
                WHERE table_name = :tname
                ORDER BY column_id
            """
            cursor.execute(sql, tname=table_name.upper())
            columns = cursor.fetchall()
            return columns

@mcp.tool()
def run_query(sql_query: str):
    """Execute a SELECT query on the Oracle database."""
    # Note: Keep this read-only for safety!
    if not sql_query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT statements are allowed."

    with get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(sql_query)
                # Fetch column names for context
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchmany(100) # Limit to 100 rows for LLM context
                return {"columns": columns, "data": rows}
            except Exception as e:
                return f"Oracle Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()