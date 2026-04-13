import sqlite3
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("SQL-Developer")

# Change this to your actual DB path or connection logic
DB_PATH = "my_database.db"

@mcp.tool()
def list_tables():
    """List all tables in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

@mcp.tool()
def describe_table(table_name: str):
    """Get the schema/column information for a specific table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = cursor.fetchall()
    conn.close()
    return schema

@mcp.tool()
def run_query(sql_query: str):
    """Execute a read-only SQL query and return results."""
    # Safety: In production, strictly limit to SELECT statements
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return results
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        conn.close()

if __name__ == "__main__":
    mcp.run()