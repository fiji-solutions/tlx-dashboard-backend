from database import get_db_connection, get_db_cursor
from collections import defaultdict
from decimal import Decimal
from datetime import datetime

import pandas as pd

from correlations import find_rolling_correlation
from prices import get_price_chart
from tlx import fetch_tlx_time_series
from toros import fetch_toros_time_series


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def base_index_timeseries(timeseries):
    df = pd.DataFrame(list(timeseries.items()), columns=['timestamp', 'value'])

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp')

    df['value'] = (df['value'] / df['value'].iloc[0]) * 100
    df['timestamp'] = df['timestamp'].dt.strftime("%Y-%m-%d")

    data = df.set_index('timestamp')['value'].to_dict()
    return data


# Database connection function is now imported from database.py


def fetch_coins_for_date_range(start_date, end_date, index_name):
    cnx = get_db_connection()
    cursor = get_db_cursor(cnx)

    query = ("""
        SELECT * FROM table1
        WHERE timestamp >= %s AND timestamp <= %s AND index_name = %s AND market_cap IS NOT NULL
    """)
    cursor.execute(query, (start_date + " 00:00:00", end_date + " 23:59:59", index_name))

    items = cursor.fetchall()
    cursor.close()
    cnx.close()

    return items


def get_participation_percentages(start_date, end_date, index_start, index_end, exclude_ids, index_name):
    table_name = "table2" if index_name == "coingecko" else ("table3" if index_name == "coingecko-sol-memes" else "table4")
    coins_for_date_range = fetch_coins_for_date_range(start_date, end_date, index_name)

    coins_by_date = defaultdict(list)
    for coin in coins_for_date_range:
        date_str = coin['timestamp'].strftime('%Y-%m-%d')
        if coin['coin_name'] not in exclude_ids:
            coins_by_date[date_str].append(coin)

    total_days = len(coins_by_date)
    coin_participation = defaultdict(int)

    for date_str, coins in coins_by_date.items():
        filtered_coins = sorted(coins, key=lambda x: x['market_cap'], reverse=True)
        selected_coins = filtered_coins[index_start:index_end + 1]
        for coin in selected_coins:
            coin_participation[coin['coin_name']] += 1

    participation_percentages = {coin: round((count / total_days) * 100, 2) for coin, count in coin_participation.items()}

    # Fetch icons for the coins
    cnx = get_db_connection()
    cursor = get_db_cursor(cnx)
    cursor.execute("SELECT id, image FROM " + table_name)
    coin_icons = {row['id']: row['image'] for row in cursor.fetchall()}
    cursor.close()
    cnx.close()

    participation_with_icons = [{"coin": coin, "percentage": participation_percentages[coin], "days_participated": coin_participation[coin], "icon": coin_icons.get(coin)} for coin in sorted(participation_percentages, key=participation_percentages.get, reverse=True)]

    return participation_with_icons


def get_market_cap_sums_and_participation(start_date, end_date, index_start, index_end, exclude_ids, index_name, correlation_coin_ids=None):
    if correlation_coin_ids is None:
        correlation_coin_ids = []
    coins_for_date_range = fetch_coins_for_date_range(start_date, end_date, index_name)

    coins_by_date = defaultdict(list)
    for coin in coins_for_date_range:
        date_str = coin['timestamp'].strftime('%Y-%m-%d')
        if coin['coin_name'] not in exclude_ids:
            coins_by_date[date_str].append(coin)

    market_cap_sums = {}
    participation = defaultdict(int)

    for date_str, coins in coins_by_date.items():
        filtered_coins = sorted(coins, key=lambda x: x['market_cap'], reverse=True)
        selected_coins = filtered_coins[index_start:index_end + 1]
        market_cap_sum = sum(coin['market_cap'] for coin in selected_coins)
        market_cap_sums[date_str] = market_cap_sum

        for coin in selected_coins:
            participation[coin['coin_name']] += 1

    market_cap_sums_base_indexed = base_index_timeseries(market_cap_sums)
    participation_percentages = get_participation_percentages(start_date, end_date, index_start, index_end, exclude_ids, index_name)

    correlation_data = dict()

    for correlation_coin in correlation_coin_ids:
        if correlation_coin in ["BTC1L", "BTC2L", "BTC3L", "BTC4L", "BTC5L", "BTC7L", "ETH1L", "ETH2L", "ETH3L", "ETH4L", "ETH5L", "ETH7L", "SOL1L", "SOL2L", "SOL3L", "SOL4L", "SOL5L", "DOGE2L", "DOGE5L"]:
            correlation_data[correlation_coin] = {
                "data": fetch_tlx_time_series(start_date, end_date, correlation_coin)
            }
        elif correlation_coin in ["BTC2XOPT", "BTC3XOPT", "BTC4XOPT", "BTC3XPOL", "BTC2XARB", "BTC3XARB", "ETH2XOPT", "ETH3XOPT", "ETH3XPOL", "ETH2XARB", "ETH3XARB", "STETH2X", "STETH3X", "STETH4X", "SOL2XOPT", "SOL3XOPT"]:
            correlation_data[correlation_coin] = {
                "data": fetch_toros_time_series(start_date, end_date, correlation_coin)
            }
        elif correlation_coin == "Solana":
            correlation_data[correlation_coin] = {
                "data": get_price_chart(start_date, end_date, correlation_coin)
            }

    for item in correlation_data:
        data_values = correlation_data[item]["data"]
        data_values_base_indexed = base_index_timeseries(correlation_data[item]["data"])
        correlation_data[item] = {
            "data": data_values,
            "base_indexed_data": data_values_base_indexed,
            "correlation15": find_rolling_correlation(market_cap_sums, data_values, 15),
            "correlation15_base_indexed": find_rolling_correlation(market_cap_sums_base_indexed,
                                                                   data_values_base_indexed, 15),
            "correlation30": find_rolling_correlation(market_cap_sums, data_values, 30),
            "correlation30_base_indexed": find_rolling_correlation(market_cap_sums_base_indexed,
                                                                   data_values_base_indexed, 30),
            "correlation60": find_rolling_correlation(market_cap_sums, data_values, 60),
            "correlation60_base_indexed": find_rolling_correlation(market_cap_sums_base_indexed,
                                                                   data_values_base_indexed, 60),
            "correlation90": find_rolling_correlation(market_cap_sums, data_values, 90),
            "correlation90_base_indexed": find_rolling_correlation(market_cap_sums_base_indexed,
                                                                   data_values_base_indexed, 90),
            "correlation120": find_rolling_correlation(market_cap_sums, data_values, 120),
            "correlation120_base_indexed": find_rolling_correlation(market_cap_sums_base_indexed,
                                                                    data_values_base_indexed, 120),
        }

    return market_cap_sums, market_cap_sums_base_indexed, participation_percentages, correlation_data
