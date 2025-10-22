import requests


def fetch_toros_time_series(start_date, end_date, correlation_coin):
    url = f"https://np40nkw6be.execute-api.us-east-1.amazonaws.com/Prod/toros/?interval=1d&initialInvestment=1000&riskFreeRate=0&fromDate={start_date}&toDate={end_date}&coin={correlation_coin}"
    data = requests.get(url).json()["data"]

    returned_data = dict()
    for item in data:
        returned_data[item["timestamp"]] = item["price"]
    return returned_data
