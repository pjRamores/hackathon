import os
import urllib.parse
from sqlalchemy import create_engine, text, inspect
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("Oracle-SQLAlchemy-Developer")

# --- CONFIGURATION ---
# For Kerberos, the username/password are omitted.
# The DSN/Service name must be defined in your tnsnames.ora.
TNS_NAME = os.getenv("ORACLE_DSN", "MY_ORACLE_SERVICE")

# Construct the SQLAlchemy URL for pyodbc with External Auth
# Format: oracle+pyodbc://@TNS_NAME
# The '@' with no leading user:pass triggers the 'UID=/' logic in the driver
params = urllib.parse.quote_plus(f"DSN={TNS_NAME};")
DATABASE_URL = f"oracle+pyodbc:///?odbc_connect={params}"

# Create Engine
# pool_pre_ping ensures the connection is still valid (important for Kerberos tickets)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

@mcp.tool()
def list_tables():
    """List all tables available to the current user."""
    inspector = inspect(engine)
    return inspector.get_table_names()

@mcp.tool()
def describe_table(table_name: str):
    """Get columns, types, and primary keys for a specific table."""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name.upper())
    # Clean up the dictionary for the LLM to read easily
    return [
        {"name": c["name"], "type": str(c["type"]), "nullable": c["nullable"]}
        for c in columns
    ]

@mcp.tool()
def run_query(sql_query: str):
    """Execute a read-only SELECT query."""
    if not sql_query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT statements are permitted."

    with engine.connect() as connection:
        try:
            result = connection.execute(text(sql_query))
            # Limit results to avoid hitting LLM context limits
            rows = result.fetchmany(50)
            return {
                "columns": list(result.keys()),
                "data": [list(row) for row in rows]
            }
        except Exception as e:
            return f"Database Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()