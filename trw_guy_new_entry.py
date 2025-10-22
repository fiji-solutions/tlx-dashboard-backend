import os

from flask import request, jsonify
from database import get_db_connection, get_db_cursor
import psycopg2
from datetime import date

PASSWORD = os.getenv('SECRET_PASSWORD', 'default')

# Database configuration is now handled by database.py


def add_data(data):
    # Get the password from the request
    password = data.get("password")

    # Check if the password is correct
    if password != PASSWORD or PASSWORD == "default":
        return jsonify({"error": "Unauthorized"}), 401

    # Extract the data you want to store
    date = data.get("date")
    global_liquidity = data.get("global_liquidity")
    bitcoin_price = data.get("bitcoin_price")
    gold_price = data.get("gold_price")

    # Check if required fields are provided
    if not date or global_liquidity is None or bitcoin_price is None or gold_price is None:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the new data into the database (PostgreSQL upsert syntax)
        query = """
            INSERT INTO price_data (date, global_liquidity, bitcoin_price, gold_price)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (date) DO UPDATE SET 
                global_liquidity = EXCLUDED.global_liquidity,
                bitcoin_price = EXCLUDED.bitcoin_price,
                gold_price = EXCLUDED.gold_price
            """
        cursor.execute(query, (date, global_liquidity, bitcoin_price, gold_price))
        conn.commit()

        # Close the connection
        cursor.close()
        conn.close()

        return jsonify({"message": "Data added successfully"}), 201

    except psycopg2.Error as err:
        return jsonify({"error": str(err)}), 500


def delete_data_by_date(date_value, password):
    if password != PASSWORD or PASSWORD == "default":
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "DELETE FROM price_data WHERE date = %s"
        cursor.execute(query, (date_value,))
        conn.commit()

        rows_deleted = cursor.rowcount
        cursor.close()
        conn.close()

        if rows_deleted == 0:
            return jsonify({"error": "No data found for the provided date"}), 404

        return jsonify({"message": "Data deleted successfully"}), 200

    except psycopg2.Error as err:
        return jsonify({"error": str(err)}), 500


def get_data(password):
    # Check if the password is correct
    if password != PASSWORD or PASSWORD == "default":
        return jsonify({"error": "Unauthorized"}), 401
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = get_db_cursor(conn)  # Use dictionary cursor for readable output

        # Fetch all rows from the price_data table
        query = "SELECT * FROM price_data ORDER BY date"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Format the date to YYYY-MM-DD if it is of type 'date'
        for row in rows:
            if 'date' in row and isinstance(row['date'], date):
                row['date'] = row['date'].strftime("%Y-%m-%d")

        # Close the connection
        cursor.close()
        conn.close()

        return jsonify({"data": rows}), 200

    except psycopg2.Error as err:
        return jsonify({"error": str(err)}), 500
