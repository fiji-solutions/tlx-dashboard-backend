import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'catalytics'),
    'user': os.getenv('DB_USER', 'local_user'),
    'password': os.getenv('DB_PASSWORD', 'local_password'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    """
    Get a PostgreSQL database connection using environment variables.
    
    Returns:
        psycopg2.connection: Database connection object
    """
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        raise

def get_db_cursor(connection=None, dict_cursor=True):
    """
    Get a database cursor with optional dictionary format.
    
    Args:
        connection: Existing database connection (optional)
        dict_cursor: If True, returns RealDictCursor for dictionary-like access
        
    Returns:
        psycopg2.cursor: Database cursor object
    """
    if connection is None:
        connection = get_db_connection()
    
    if dict_cursor:
        return connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        return connection.cursor()

def execute_query(query, params=None, fetch_one=False, fetch_all=True, dict_cursor=True):
    """
    Execute a database query with automatic connection management.
    
    Args:
        query: SQL query string
        params: Query parameters (optional)
        fetch_one: If True, return only the first result
        fetch_all: If True, return all results
        dict_cursor: If True, use dictionary cursor
        
    Returns:
        Query results or None
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = get_db_cursor(connection, dict_cursor)
        
        cursor.execute(query, params)
        
        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        else:
            connection.commit()
            return cursor.rowcount
            
    except psycopg2.Error as e:
        if connection:
            connection.rollback()
        print(f"Database query error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def test_connection():
    """
    Test the database connection and print connection details.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        print(f"Connected to PostgreSQL database successfully!")
        print(f"Database: {DB_CONFIG['database']} on {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print(f"PostgreSQL version: {version[0]}")
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return False

if __name__ == "__main__":
    # Test the connection when running this module directly
    test_connection()