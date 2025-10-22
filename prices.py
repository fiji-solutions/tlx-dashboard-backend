from database import get_db_connection, get_db_cursor

# Database connection function is now imported from database.py


def fetch_coin_price_for_date_range(start_date, end_date, coin):
    cnx = get_db_connection()
    cursor = get_db_cursor(cnx)

    query = ("""
        SELECT * FROM table1
        WHERE timestamp >= %s AND timestamp <= %s AND coin_name = %s AND index_name = "coingecko"
    """)
    cursor.execute(query, (start_date + " 00:00:00", end_date + " 23:59:59", coin))

    items = {row['timestamp'].strftime('%Y-%m-%d'): float(row['price']) for row in cursor.fetchall()}
    cursor.close()
    cnx.close()

    return items


def fetch_tradingview_price_for_date_range(start_date, end_date, coin):
    cnx = get_db_connection()
    cursor = get_db_cursor(cnx)

    query = ("""
        SELECT * FROM table1
        WHERE timestamp >= %s AND timestamp <= %s AND coin_name = %s AND index_name = "tradingview"
    """)
    cursor.execute(query, (start_date + " 00:00:00", end_date + " 23:59:59", coin))

    items = {row['timestamp'].strftime('%Y-%m-%d'): float(row['price']) for row in cursor.fetchall()}
    cursor.close()
    cnx.close()

    return items


def get_price_chart(start_date, end_date, coin):
    data = fetch_coin_price_for_date_range(start_date, end_date, coin)
    return data
