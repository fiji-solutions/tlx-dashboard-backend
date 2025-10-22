import json
import math

from database import get_db_connection, get_db_cursor
from decimal import Decimal
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import skew, kurtosis

# Database configuration is now handled by database.py


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def format_decimal(value):
    if value is None or math.isnan(value):
        return 0
    return float(f"{value:.20f}")


def fetch_all_coins():
    cnx = get_db_connection()
    cursor = get_db_cursor(cnx)

    cursor.execute('SELECT * FROM lst WHERE coingeckoId != ""')
    items = cursor.fetchall()

    cursor.close()
    cnx.close()

    return items


def get_jupiter_all():
    # Fetch all records from the table
    items = fetch_all_coins()

    # Order the items by the "order" field
    items_sorted = sorted(items, key=lambda x: x['name'])

    # Return the items
    response = {
        'body': json.dumps(items_sorted, default=decimal_default)
    }
    return response


def get_jupiter(asset_names):
    cnx = get_db_connection()
    cursor = get_db_cursor(cnx)

    # Prepare the SQL query to fetch prices for the specified assets
    query = '''
        SELECT asset_name, price, timestamp 
        FROM lst2 
        WHERE asset_name IN (%s)
    '''
    # Create a placeholder for each asset name in the query
    format_strings = ','.join(['%s'] * len(asset_names))
    query = query % format_strings

    # Execute the query with the asset names
    cursor.execute(query, tuple(asset_names))
    results = cursor.fetchall()

    cursor.close()
    cnx.close()

    # Structure the response
    response = {}
    price_data = {}

    for row in results:
        asset_name = row['asset_name']
        price_info = {'price': float(row['price']), 'timestamp': row['timestamp']}

        # Add price info to the asset's list
        if asset_name not in response:
            response[asset_name] = []
        response[asset_name].append(price_info)

        # Keep track of all price data for base indexing
        if asset_name not in price_data:
            price_data[asset_name] = {}
        price_data[asset_name][row['timestamp']] = float(row['price'])

    # Find the first common date across all assets
    common_dates = set.intersection(*(set(data.keys()) for data in price_data.values()))
    first_common_date = (datetime.strptime(min(common_dates), "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    # Calculate daily percentage change for each asset
    daily_changes = {}
    cumulative_yield_response = {}
    for asset_name, prices in price_data.items():
        sorted_dates = sorted(prices.keys())
        daily_returns = []

        for i in range(4, len(sorted_dates)):
            current_date = sorted_dates[i]
            previous_date = sorted_dates[i - 1]

            if previous_date in prices and current_date in prices:
                prev_price = prices[previous_date]
                prev_price_sol = price_data["solana"][previous_date]
                curr_price = prices[current_date]
                curr_price_sol = price_data["solana"][current_date]
                if prev_price > 0:
                    daily_return = ((curr_price / curr_price_sol) / (prev_price / prev_price_sol)) - 1
                    daily_returns.append(daily_return)

        if daily_returns:
            # Variance and Standard Deviation
            variance = np.var(daily_returns)
            std_deviation = np.std(daily_returns)

            # Rolling APY Calculation for multiple windows
            rolling_windows = [30, 60, 90, 120]
            rolling_apy = {}

            for window in rolling_windows:
                if len(daily_returns) >= window:
                    rolling_window_returns = daily_returns[-window:]
                    cumulative_return = np.prod([(1 + r) for r in rolling_window_returns])
                    rolling_apy_value = (cumulative_return ** (365 / window)) - 1
                    rolling_apy[f"rolling_apy_{window}d"] = rolling_apy_value
                else:
                    rolling_apy[f"rolling_apy_{window}d"] = None

            # Cumulative Yield Calculation in a similar structure to base_indexed_response
            cumulative_yield_value = 1
            cumulative_yield_response[asset_name] = []

            for i in range(0, len(sorted_dates)):
                current_date = sorted_dates[i]

                if current_date >= first_common_date:
                    daily_return = daily_returns[i - 4]
                    cumulative_yield_value *= (1 + daily_return)
                    cumulative_yield_response[asset_name].append({
                        'timestamp': current_date,
                        'cumulative_yield': cumulative_yield_value - 1
                    })

            # Skewness and Kurtosis
            skewness = skew(daily_returns)
            kurt = kurtosis(daily_returns)

            # Downside Volatility Calculation
            negative_returns = [r for r in daily_returns if r < 0]
            downside_volatility = np.std(negative_returns) if negative_returns else 0

            average_daily_return = np.mean(daily_returns)
            apy = (1 + average_daily_return) ** 365 - 1
            daily_changes[asset_name] = {
                'average_daily_return': average_daily_return,
                'apy': apy,
                'variance': variance,
                'std_deviation': std_deviation,
                'downside_volatility': downside_volatility,
                'rolling_apy_30d': rolling_apy.get('rolling_apy_30d', 0),
                'rolling_apy_60d': rolling_apy.get('rolling_apy_60d', 0),
                'rolling_apy_90d': rolling_apy.get('rolling_apy_90d', 0),
                'rolling_apy_120d': rolling_apy.get('rolling_apy_120d', 0),
                'skewness': format_decimal(skewness),
                'kurtosis': format_decimal(kurt),
                'num_days': len(daily_returns)
            }

    # Create base indexed data starting from the first common date
    base_indexed_response = {}
    for asset_name, prices in price_data.items():
        base_price = prices[first_common_date] if first_common_date in prices else None
        base_indexed_response[asset_name] = []

        for timestamp in sorted(prices.keys()):
            if timestamp >= first_common_date:
                indexed_price = (prices[timestamp] / base_price) * 100 if base_price else None
                base_indexed_response[asset_name].append({
                    'timestamp': timestamp,
                    'indexed_price': indexed_price
                })

    # Return the response as JSON
    return {
        'body': json.dumps({
            'price_data': response,
            'base_indexed_data': base_indexed_response,
            'cumulative_yield_data': cumulative_yield_response,
            'daily_changes': daily_changes
        }, default=decimal_default)
    }

