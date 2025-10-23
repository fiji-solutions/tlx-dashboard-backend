import requests
import uuid
import os
import sys
from datetime import datetime
import time

# Add the parent directory to the path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection, get_db_cursor

def fetch_all_coins_in_category(category_id):
    API_KEY = os.getenv('COINGECKO_API_KEY', '')
    headers = {"x-cg-demo-api-key": API_KEY}

    coins_url = "https://api.coingecko.com/api/v3/coins/markets"

    all_coins = []
    page = 1
    per_page = 250

    while True:
        params = {
            "vs_currency": "usd",
            "category": category_id,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": "false"
        }

        response = requests.get(coins_url, headers=headers, params=params)
        response.raise_for_status()

        coins = response.json()
        if not coins:
            break

        all_coins.extend(coins)
        page += 1

    return all_coins

def format_decimal(value):
    if value is None:
        return None
    return f"{value:.20f}"

def fetch_and_store_coin_history(coins, date, category, table):
    cnx = get_db_connection()
    cursor = get_db_cursor(cnx, dict_cursor=False)

    for index, coin in enumerate(coins, start=1):
        item = {
            "composite_key": f"{coin['id']}#{category}#{date}",
            "coin_name": coin["id"],
            "index_name": category,
            "liquidity": format_decimal(coin["price_change_percentage_24h"]),
            "market_cap": format_decimal(coin["market_cap"]),
            "price": format_decimal(coin["current_price"]),
            "timestamp": datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d %H:%M:%S+00:00"),
            "unique_id": str(uuid.uuid4()),
            "volume24h": format_decimal(coin["total_volume"])
        }

        try:
            cursor.execute(
                "INSERT INTO table1 (composite_key, coin_name, index_name, liquidity, market_cap, price, timestamp, unique_id, volume24h) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (composite_key) DO NOTHING",
                (item['composite_key'], item['coin_name'], item['index_name'], item['liquidity'], item['market_cap'], item['price'], item['timestamp'], item['unique_id'], item['volume24h'])
            )
        except Exception as e:
            print(f"Error inserting table1: {e}")

        try:
            cursor.execute(
                f'INSERT INTO "{table}" (id, image, "order") VALUES (%s, %s, %s) '
                f'ON CONFLICT (id) DO UPDATE SET "order" = EXCLUDED."order"',
                (coin["id"], coin["image"], index)
            )
        except Exception as err:
            print(f"Error inserting/updating {table}: {err}")

    cnx.commit()
    cursor.close()
    cnx.close()

date = datetime.now().strftime("%d-%m-%Y")

#solana_meme_coins = fetch_all_coins_in_category("solana-meme-coins")
#time.sleep(60)
#solana_ecosystem_coins = fetch_all_coins_in_category("solana-ecosystem")
#time.sleep(60)
all_meme_coins = fetch_all_coins_in_category("meme-token")

#solana_meme_coins = [x for x in solana_meme_coins if x["market_cap"] and x["market_cap"] > 0]
#solana_ecosystem_coins = [x for x in solana_ecosystem_coins if x["market_cap"] and x["market_cap"] > 0]
#all_meme_coins = [x for x in all_meme_coins if x["market_cap"] and x["market_cap"] > 0]

#fetch_and_store_coin_history(solana_ecosystem_coins, date, "coingecko", "table2")
#fetch_and_store_coin_history(solana_meme_coins, date, "coingecko-sol-memes", "table3")
fetch_and_store_coin_history(all_meme_coins, date, "coingecko-memes", "table4")
