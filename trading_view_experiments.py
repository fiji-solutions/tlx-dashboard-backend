import os

from database import get_db_connection, get_db_cursor
import psycopg2

# Database connection function is now imported from database.py
PASSWORD = os.getenv('SECRET_PASSWORD2', 'default')

def fetch_records_from_experiments(indicator, experiment, password):
    if password != PASSWORD or PASSWORD == "default":
        return []
    cnx = get_db_connection()
    cursor = get_db_cursor(cnx)

    query = ("""
        SELECT * FROM trading_view_experiments
        WHERE indicator = %s AND experiment = %s
    """)
    cursor.execute(query, (indicator, experiment))

    items = cursor.fetchall()
    cursor.close()
    cnx.close()

    return items

def add_record_to_experiments(indicator, experiment, dd, intra_dd, sortino, sharpe, profit_factor, profitable, trades, omega, net_profit, net_profit_ratio, parameters, password):
    if password != PASSWORD or PASSWORD == "default":
        return
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = ("""
        INSERT INTO trading_view_experiments (
            indicator, experiment, dd, intra_dd, sortino, sharpe, profit_factor, profitable, trades, omega, net_profit, net_profit_ratio, parameters
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """)
    values = (indicator, experiment, dd, intra_dd, sortino, sharpe, profit_factor, profitable, trades, omega, net_profit, net_profit_ratio, parameters)

    try:
        cursor.execute(query, values)
        cnx.commit()
        print("Record added successfully.")
    except psycopg2.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        cnx.close()

def delete_record_from_experiments(record_id, password):
    if password != PASSWORD or PASSWORD == "default":
        return
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = ("""
        DELETE FROM trading_view_experiments
        WHERE id = %s
    """)

    try:
        cursor.execute(query, (record_id,))
        cnx.commit()
        print("Record deleted successfully.")
    except psycopg2.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        cnx.close()
