import pandas as pd
import math


def find_rolling_correlation(data1, data2_raw, window):
    for i in data1:
        data1[i] = float(data1[i])

    data2 = {}
    for i in data2_raw:
        data2[i.split(" ")[0]] = data2_raw[i]

    df1 = pd.DataFrame(list(data1.items()), columns=['date', 'market_cap'])
    df1['date'] = pd.to_datetime(df1['date'])
    df1.set_index('date', inplace=True)

    df2 = pd.DataFrame(list(data2.items()), columns=['date', 'price'])
    df2['date'] = pd.to_datetime(df2['date'])
    df2.set_index('date', inplace=True)

    data = df1.merge(df2, left_index=True, right_index=True)

    data['rolling_correlation'] = data['market_cap'].rolling(window).corr(data['price'])

    return data['rolling_correlation'].iloc[-1] if not math.isnan(data['rolling_correlation'].iloc[-1]) else 2
