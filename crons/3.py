import time
import requests
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection, get_db_cursor


def fetch_all_records():
    try:
        conn = get_db_connection()
        cursor = get_db_cursor(conn, dict_cursor=True)
        cursor.execute('SELECT * FROM lst WHERE coingeckoid != %s', ('',))
        records = cursor.fetchall()  # Fetch all records
        cursor.close()
        conn.close()
        return records

    except Exception as e:
        print(f"Error fetching records from database: {e}")
        return []


def save_price_record(asset_name, price, timestamp):
    try:
        conn = get_db_connection()
        cursor = get_db_cursor(conn, dict_cursor=False)
        cursor.execute('''
            INSERT INTO lst2 (asset_name, price, timestamp)
            VALUES (%s, %s, %s)
        ''', (asset_name, price, timestamp))
        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error saving price record to database: {e}")


records = fetch_all_records()
records.append({
    'coingeckoid': 'solana'
})
ids = ""
for record in records:
    ids += record['coingeckoid'] + ","

url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids[:-1]}&vs_currencies=usd"

headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": os.getenv('COINGECKO_API_KEY', '')
    }

response = requests.get(url, headers=headers)

for asset, details in response.json().items():
    save_price_record(asset, details["usd"], datetime.now().strftime('%Y-%m-%d'))
