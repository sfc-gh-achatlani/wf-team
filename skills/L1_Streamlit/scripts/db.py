"""
db.py - Database Connection and Query Utilities

Handles all Snowflake connectivity and provides safe query execution
with proper error handling and logging.
"""

import os
from typing import Any, Dict, List, Optional
from datetime import date
import snowflake.connector


def get_connection(connection_name: Optional[str] = None) -> snowflake.connector.SnowflakeConnection:
    """
    Create a Snowflake connection using the specified connection name.
    
    Args:
        connection_name: Name of the connection profile. 
                        Defaults to SNOWFLAKE_CONNECTION_NAME env var or 'snowhouse'.
    
    Returns:
        Active Snowflake connection object.
    """
    conn_name = connection_name or os.getenv("SNOWFLAKE_CONNECTION_NAME") or "snowhouse"
    conn = snowflake.connector.connect(connection_name=conn_name)
    conn.cursor().execute("USE WAREHOUSE APP_AIRFLOW")
    return conn


def execute_query(
    conn: snowflake.connector.SnowflakeConnection,
    query: str,
    description: str = "",
) -> List[Dict[str, Any]]:
    """
    Execute a SQL query and return results as list of dictionaries.
    
    Args:
        conn: Active Snowflake connection
        query: SQL query string
        description: Human-readable description for logging/debugging
    
    Returns:
        List of dicts, one per row, with lowercase column names as keys.
    
    Raises:
        snowflake.connector.errors.ProgrammingError: On SQL errors
    """
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        cursor.close()


def safe_string(value: Any) -> str:
    """
    Safely convert a value to a SQL-safe string.
    
    - Escapes single quotes
    - Handles None values
    - Converts to string
    
    Args:
        value: Any value to convert
    
    Returns:
        SQL-safe string representation
    """
    if value is None:
        return ""
    return str(value).replace("'", "''")


def to_json_safe(obj: Any) -> Any:
    """
    Recursively convert an object to JSON-serializable format.
    
    Handles:
    - datetime/date objects → ISO format strings
    - Decimal → float
    - Nested dicts and lists
    
    Args:
        obj: Any Python object
    
    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, dict):
        return {k: to_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_json_safe(v) for v in obj]
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif obj is None:
        return None
    elif isinstance(obj, (int, float, str, bool)):
        return obj
    else:
        try:
            return float(obj)
        except (TypeError, ValueError):
            return str(obj)


def get_available_run_dates(conn) -> List[date]:
    """
    Get all available snapshot run dates from the actuals table.
    
    Returns:
        List of dates, most recent first.
    """
    from .config import ACTUALS_TABLE, RUN_DATE_COLUMN
    
    query = f"""
    SELECT DISTINCT {RUN_DATE_COLUMN} AS run_date
    FROM {ACTUALS_TABLE}
    ORDER BY run_date DESC
    """
    
    results = execute_query(conn, query, "Get available run dates")
    return [row['run_date'] for row in results]
