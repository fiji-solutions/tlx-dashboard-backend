import math
from datetime import datetime
from decimal import Decimal

from database import get_db_connection, get_db_cursor
import numpy as np
import pandas as pd

from prices import fetch_tradingview_price_for_date_range


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


def get_rsps(start_date, end_date, max_market_cap, min_market_cap, results, excluded):
    # start = datetime.strptime(start_date, "%Y-%m-%d")
    # end = datetime.strptime(end_date, "%Y-%m-%d")
    # days_diff = (end - start).days + 1
    index_name = "coingecko-memes"
    coin_dfs = {}
    coins_for_date_range = fetch_coins_for_date_range(start_date, end_date, index_name)

    total_for_date_range_raw = fetch_tradingview_price_for_date_range(start_date, end_date, "total")
    total2_for_date_range_raw = fetch_tradingview_price_for_date_range(start_date, end_date, "total2")
    total3_for_date_range_raw = fetch_tradingview_price_for_date_range(start_date, end_date, "total3")
    others_for_date_range_raw = fetch_tradingview_price_for_date_range(start_date, end_date, "others.d")
    btc_for_date_range_raw = fetch_tradingview_price_for_date_range(start_date, end_date, "btc")
    eth_for_date_range_raw = fetch_tradingview_price_for_date_range(start_date, end_date, "eth")

    total_for_date_range = [{"timestamp": x[0], "price": x[1]} for x in total_for_date_range_raw.items()]
    total2_for_date_range = [{"timestamp": x[0], "price": x[1]} for x in total2_for_date_range_raw.items()]
    total3_for_date_range = [{"timestamp": x[0], "price": x[1]} for x in total3_for_date_range_raw.items()]
    others_for_date_range = [{"timestamp": x[0], "price": x[1]} for x in others_for_date_range_raw.items()]
    btc_for_date_range = [{"timestamp": x[0], "price": x[1]} for x in btc_for_date_range_raw.items()]
    eth_for_date_range = [{"timestamp": x[0], "price": x[1]} for x in eth_for_date_range_raw.items()]

    total_df = pd.DataFrame(total_for_date_range, columns=["timestamp", "price"])
    total2_df = pd.DataFrame(total2_for_date_range, columns=["timestamp", "price"])
    total3_df = pd.DataFrame(total3_for_date_range, columns=["timestamp", "price"])
    others_df = pd.DataFrame(others_for_date_range, columns=["timestamp", "price"])
    btc_df = pd.DataFrame(btc_for_date_range, columns=["timestamp", "price"])
    eth_df = pd.DataFrame(eth_for_date_range, columns=["timestamp", "price"])

    total_df['timestamp'] = pd.to_datetime(total_df['timestamp'])
    total2_df['timestamp'] = pd.to_datetime(total2_df['timestamp'])
    total3_df['timestamp'] = pd.to_datetime(total3_df['timestamp'])
    others_df['timestamp'] = pd.to_datetime(others_df['timestamp'])
    btc_df['timestamp'] = pd.to_datetime(btc_df['timestamp'])
    eth_df['timestamp'] = pd.to_datetime(eth_df['timestamp'])

    # Group records by coin_name
    for record in coins_for_date_range:
        coin_name = record['coin_name']
        if coin_name not in coin_dfs:
            coin_dfs[coin_name] = {
                "coin_name": coin_name,
                "data": []
            }
        coin_dfs[coin_name]["data"].append(record)

    # keys_to_remove = [coin_name for coin_name in coin_dfs if len(coin_dfs[coin_name]["data"]) < days_diff]
    #
    # # Remove the keys from coin_dfs
    # for key in keys_to_remove:
    #     del coin_dfs[key]

    # Create a DataFrame for each unique coin_name and store in the dictionary
    for coin_name, records in coin_dfs.items():
        df = pd.DataFrame(records["data"], columns=["coin_name", "market_cap", "price", "timestamp"])
        df['timestamp'] = pd.to_datetime(df['timestamp'])  # Ensure timestamp is in datetime format
        coin_dfs[coin_name]["df"] = df

    market_cap_sum = {}

    for record in coins_for_date_range:
        date = record['timestamp'].date()  # Get date part of timestamp
        if date not in market_cap_sum:
            market_cap_sum[date] = Decimal(0)
        market_cap_sum[date] += record['market_cap']


    df_market_cap_sum = pd.DataFrame(list(market_cap_sum.items()), columns=['timestamp', 'market_cap'])
    df_market_cap_sum['timestamp'] = pd.to_datetime(df_market_cap_sum['timestamp'])

    # Convert coins_for_date_range to a DataFrame for easier processing
    df_all = pd.DataFrame(coins_for_date_range)
    df_all['timestamp'] = pd.to_datetime(df_all['timestamp'])
    df_all['market_cap'] = pd.to_numeric(df_all['market_cap'])

    # Hardcoded max and min market cap values
    max_market_cap = Decimal(max_market_cap)  # Example max value
    min_market_cap = Decimal(min_market_cap)    # Example min value

    # # Identify tokens with market cap outside the range
    tokens_outside_cap = set()
    for record in coins_for_date_range:
        if record['market_cap'] > max_market_cap or record['market_cap'] < min_market_cap:
            tokens_outside_cap.add(record['coin_name'])

    # Filter coin_dfs to remove tokens outside the range
    for token in tokens_outside_cap:
        if token in coin_dfs:
            del coin_dfs[token]

    df_market_cap_sum = df_market_cap_sum.sort_values(by='timestamp')
    total_df = total_df.sort_values(by='timestamp')
    total2_df = total2_df.sort_values(by='timestamp')
    total3_df = total3_df.sort_values(by='timestamp')
    others_df = others_df.sort_values(by='timestamp')
    btc_df = btc_df.sort_values(by='timestamp')
    eth_df = eth_df.sort_values(by='timestamp')

    for i in coin_dfs:
        coin_dfs[i]["df"] = coin_dfs[i]["df"].sort_values(by='timestamp')

    for i in coin_dfs:
        coin_dfs[i]['df']['ROC'] = coin_dfs[i]['df']['price'].pct_change() * 100
        coin_dfs[i]['df']['ROC'] = coin_dfs[i]['df']['ROC'].astype(float)
        coin_dfs[i]['mean'] = round(coin_dfs[i]['df']['ROC'].mean(skipna=True), 2)
        coin_dfs[i]['std'] = round(coin_dfs[i]['df']['ROC'].astype(float).std(skipna=True), 2)


    df_market_cap_sum['ROC'] = df_market_cap_sum['market_cap'].pct_change() * 100
    df_market_cap_sum_mean = round(df_market_cap_sum['ROC'].mean(skipna=True), 2)
    df_market_cap_sum_std = round(df_market_cap_sum['ROC'].astype(float).std(skipna=True), 2)

    total_df['ROC'] = total_df['price'].pct_change() * 100
    total2_df['ROC'] = total2_df['price'].pct_change() * 100
    total3_df['ROC'] = total3_df['price'].pct_change() * 100
    others_df['ROC'] = others_df['price'].pct_change() * 100
    btc_df['ROC'] = btc_df['price'].pct_change() * 100
    eth_df['ROC'] = eth_df['price'].pct_change() * 100


    for i in coin_dfs:
        del coin_dfs[i]["data"]
        # Calculate percentage difference for mean ROC
        coin_dfs[i]['relative_mean'] = round(((coin_dfs[i]['mean'] - df_market_cap_sum_mean) / abs(df_market_cap_sum_mean)) * 100, 2)

        # Calculate ratio for volatility
        coin_dfs[i]['relative_volatility'] = round(coin_dfs[i]['std'] / df_market_cap_sum_std, 2)

    # Create a list of dictionaries from coin_dfs
    coins_list = [coin_dfs[i] for i in coin_dfs]

    # Sort by relative_mean and relative_volatility
    sort_by_mean = sorted(coins_list, key=lambda x: x['relative_mean'], reverse=True)
    sort_by_volatility = sorted(coins_list, key=lambda x: x['relative_volatility'], reverse=True)

    # Create a dictionary to store the summed indices
    summed_indices = {}

    # Assign indices for each coin in sort_by_mean
    for idx, coin in enumerate(sort_by_mean):
        if coin['coin_name'] not in excluded:
            summed_indices[coin['coin_name']] = idx

    # Add indices for each coin in sort_by_volatility
    for idx, coin in enumerate(sort_by_volatility):
        if coin['coin_name'] not in excluded:
            if coin['coin_name'] in summed_indices:
                summed_indices[coin['coin_name']] += idx
            else:
                summed_indices[coin['coin_name']] = idx

    # Sort coins by their summed indices
    sorted_coins = sorted(summed_indices.items(), key=lambda x: x[1])

    # Extract the top 'results' coins
    top_coins = [coin for coin, _ in sorted_coins[:results]]

    list_to_return = []
    for i in top_coins:
        if i in coin_dfs:
            covariance_total = np.cov(coin_dfs[i]['df']['ROC'][1:], total_df['ROC'][1:])[0, 1] if len(coin_dfs[i]['df']['ROC'][1:]) == len( total_df['ROC'][1:]) else 0
            covariance_total2 = np.cov(coin_dfs[i]['df']['ROC'][1:], total2_df['ROC'][1:])[0, 1] if len(coin_dfs[i]['df']['ROC'][1:]) == len( total2_df['ROC'][1:]) else 0
            covariance_total3 = np.cov(coin_dfs[i]['df']['ROC'][1:], total3_df['ROC'][1:])[0, 1] if len(coin_dfs[i]['df']['ROC'][1:]) == len( total3_df['ROC'][1:]) else 0
            covariance_others = np.cov(coin_dfs[i]['df']['ROC'][1:], others_df['ROC'][1:])[0, 1] if len(coin_dfs[i]['df']['ROC'][1:]) == len( others_df['ROC'][1:]) else 0
            covariance_btc = np.cov(coin_dfs[i]['df']['ROC'][1:], btc_df['ROC'][1:])[0, 1] if len(coin_dfs[i]['df']['ROC'][1:]) == len( btc_df['ROC'][1:]) else 0
            covariance_eth = np.cov(coin_dfs[i]['df']['ROC'][1:], eth_df['ROC'][1:])[0, 1] if len(coin_dfs[i]['df']['ROC'][1:]) == len( eth_df['ROC'][1:]) else 0

            variance_market_total = np.var(total_df['ROC'][1:], ddof=1)
            variance_market_total2 = np.var(total2_df['ROC'][1:], ddof=1)
            variance_market_total3 = np.var(total3_df['ROC'][1:], ddof=1)
            variance_market_others = np.var(others_df['ROC'][1:], ddof=1)
            variance_market_btc = np.var(btc_df['ROC'][1:], ddof=1)
            variance_market_eth = np.var(eth_df['ROC'][1:], ddof=1)

            # Calculate Beta
            beta_total = covariance_total / variance_market_total
            beta_total2 = covariance_total2 / variance_market_total2
            beta_total3 = covariance_total3 / variance_market_total3
            beta_others = covariance_others / variance_market_others
            beta_btc = covariance_btc / variance_market_btc
            beta_eth = covariance_eth / variance_market_eth

            coin_dfs[i]['beta_total'] = round(beta_total, 2)
            coin_dfs[i]['beta_total2'] = round(beta_total2, 2)
            coin_dfs[i]['beta_total3'] = round(beta_total3, 2)
            coin_dfs[i]['beta_others'] = round(beta_others, 2)
            coin_dfs[i]['beta_btc'] = round(beta_btc, 2)
            coin_dfs[i]['beta_eth'] = round(beta_eth, 2)
            del coin_dfs[i]["df"]
            for j in coins_list:
                if j["coin_name"] == i:
                    # Add beta values to the coin dictionary
                    j['beta_total'] = abs(coin_dfs[i]['beta_total'])
                    j['beta_total2'] = abs(coin_dfs[i]['beta_total2'])
                    j['beta_total3'] = abs(coin_dfs[i]['beta_total3'])
                    j['beta_others'] = abs(coin_dfs[i]['beta_others'])
                    j['beta_btc'] = abs(coin_dfs[i]['beta_btc'])
                    j['beta_eth'] = abs(coin_dfs[i]['beta_eth'])
                    list_to_return.append(j)
                    break

    for i in list_to_return:
        if math.isnan(i["mean"]):
            i["mean"] = "-"
        if math.isnan(i["relative_mean"]):
            i["relative_mean"] = "-"
        if math.isnan(i["relative_volatility"]):
            i["relative_volatility"] = "-"
        if math.isnan(i["std"]):
            i["std"] = "-"

    return list_to_return
