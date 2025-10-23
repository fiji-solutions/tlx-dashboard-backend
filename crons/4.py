import requests
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection, get_db_cursor

def create_price_table():
    conn = get_db_connection()
    cursor = get_db_cursor(conn, dict_cursor=False)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lst3 (
            id SERIAL PRIMARY KEY,
            asset_name VARCHAR(255),
            price DECIMAL(15, 8),
            daily_volume DECIMAL(20, 8),
            timestamp VARCHAR(255)
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def save_price_record(asset_name, price, daily_volume, timestamp):
    try:
        conn = get_db_connection()
        cursor = get_db_cursor(conn, dict_cursor=False)
        cursor.execute('''
            INSERT INTO lst3 (asset_name, price, daily_volume, timestamp)
            VALUES (%s, %s, %s, %s)
        ''', (asset_name, price, daily_volume, timestamp))
        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error saving price record to database: {e}")
        raise

create_price_table()

url = "https://api.jup.ag/tokens/v1?tags=lst"
headers = {"accept": "application/json"}
response = requests.get(url, headers=headers)
lsts = response.json()
lsts.append({
    "address": "So11111111111111111111111111111111111111112",
    "symbol": "solana",
    "daily_volume": 0.0
})

batch_size = 100
for i in range(0, len(lsts), batch_size):
    batch = lsts[i:i + batch_size]
    addresses = [asset['address'] for asset in batch]
    address_string = ', '.join(addresses)

    price_url = "https://api.jup.ag/price/v2?ids=" + address_string
    price_response = requests.get(price_url, headers=headers)

    price_data = price_response.json()["data"]

    for asset in batch:
        asset_name = asset["symbol"]
        address = asset["address"]
        daily_volume = asset.get("daily_volume", 0.0)

        if address in price_data:
            price = price_data[address]["price"]
            save_price_record(asset_name, price, daily_volume, datetime.now().strftime('%Y-%m-%d'))

