# coingecko_sol_api.py

import json
from database import get_db_connection, get_db_cursor
from decimal import Decimal

# Database configuration is now handled by database.py


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def fetch_all_coins():
    cnx = get_db_connection()
    cursor = get_db_cursor(cnx)

    cursor.execute("SELECT * FROM table2")
    items = cursor.fetchall()

    cursor.close()
    cnx.close()

    return items


def fetch_sol_meme_all_coins():
    cnx = get_db_connection()
    cursor = get_db_cursor(cnx)

    cursor.execute("SELECT * FROM table3")
    items = cursor.fetchall()

    cursor.close()
    cnx.close()

    return items


def fetch_meme_all_coins():
    cnx = get_db_connection()
    cursor = get_db_cursor(cnx)

    cursor.execute("SELECT * FROM table4")
    items = cursor.fetchall()

    cursor.close()
    cnx.close()

    return items


def get_coingecko_sol_all():
    # Fetch all records from the table
    items = fetch_all_coins()

    # Order the items by the "order" field
    items_sorted = sorted(items, key=lambda x: x['order'])

    # Return the items
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Origin": "*",
        },
        'body': json.dumps(items_sorted, default=decimal_default)
    }
    return response


def get_coingecko_sol_all_memes():
    # Fetch all records from the table
    items = fetch_sol_meme_all_coins()

    # Order the items by the "order" field
    items_sorted = sorted(items, key=lambda x: x['order'])

    # Return the items
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Origin": "*",
        },
        'body': json.dumps(items_sorted, default=decimal_default)
    }
    return response


def get_coingecko_all_memes():
    # Fetch all records from the table
    items = fetch_meme_all_coins()

    # Order the items by the "order" field
    items_sorted = sorted(items, key=lambda x: x['order'])

    # Return the items
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Origin": "*",
        },
        'body': json.dumps(items_sorted, default=decimal_default)
    }
    return response
