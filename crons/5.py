import requests
import os
import sys

# Add the parent directory to the path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection, get_db_cursor

def create_table():
    conn = get_db_connection()
    cursor = get_db_cursor(conn, dict_cursor=False)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lst4 (
            id SERIAL PRIMARY KEY,
            address VARCHAR(255),
            name VARCHAR(255) UNIQUE,
            symbol VARCHAR(255) UNIQUE,
            logoURI VARCHAR(255),
            coingeckoId VARCHAR(255)
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def record_exists(name, symbol):
    conn = get_db_connection()
    cursor = get_db_cursor(conn, dict_cursor=False)
    cursor.execute('''
        SELECT COUNT(*) FROM lst4 WHERE name = %s OR symbol = %s
    ''', (name, symbol))
    exists = cursor.fetchone()[0] > 0
    cursor.close()
    conn.close()
    return exists

def save_record(record):
    try:
        name = record['name']
        symbol = record['symbol']

        # Check if the record already exists
        if record_exists(name, symbol):
            print(f"Record for {name} ({symbol}) already exists. Skipping.")
            return

        conn = get_db_connection()
        cursor = get_db_cursor(conn, dict_cursor=False)
        cursor.execute('''
            INSERT INTO lst4 (
                address, name, symbol, logoURI, coingeckoId
            ) VALUES (%s, %s, %s, %s, %s)
        ''', (
            record['address'], name, symbol, record['logoURI'],
            record['extensions']['coingeckoId'] if 'coingeckoId' in record['extensions'] else ''
        ))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Inserted record for {name} ({symbol}).")

    except Exception as e:
        print(f"Error saving record to database: {e}")
        raise

create_table()

url = "https://api.jup.ag/tokens/v1?tags=lst"
headers = {"accept": "application/json"}
response = requests.get(url, headers=headers)
lsts = response.json()

for record in lsts:
    save_record(record)
