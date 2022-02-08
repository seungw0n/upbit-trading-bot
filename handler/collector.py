"""
data reader and writer

data collector: Preferred Websocket
    Quotation API
        Websocket: 5 req/sec, 100 req/min
        REST API: 600 req/min, 10 req/sec (종목, 캔들, 체결, 티커, 호가별)

Installations
    pip3 install requests
    pip3 install pandas
"""

import os
import requests
import ast
import time
import pandas as pd
from datetime import datetime

# Response text to List
MARKETS = ast.literal_eval(requests.request("GET", "https://api.upbit.com/v1/market/all?isDetails=false",
                                            headers={"Accept": "application/json"}).text)


def check_platform() -> int:
    """ DUMP : Replace to os.path.join """
    from sys import platform
    if platform == "linux" or platform == "darwin":
        return 0
    elif platform == "win32":
        return 1
    else:
        return -1


def create(df: pd.DataFrame, filename: str, dirPath: str) -> bool:
    path = os.path.join(dirPath, filename)

    if not os.path.isfile(path=path):  # Check file exists
        df.set_index('datetime_kst', inplace=True)
        df.to_pickle(path=path)
        return True

    return False


def read(filename: str, dirPath: str) -> pd.DataFrame:
    path = os.path.join(dirPath, filename)

    try:
        df = pd.read_pickle(filepath_or_buffer=path)
        return df
    except Exception:
        raise RuntimeError("An exception occurred: function \"read\"")


def toDictionary(responseText) -> dict:
    """ convert response to dictionary """
    result = list(eval(responseText))
    return result


def toDataFrame(data: dict) -> pd.DataFrame:
    """ convert dictionary to DataFrame """
    df = pd.DataFrame.from_dict(data=data)
    columns = {'candle_date_time_utc': 'datetime_utc', 'candle_date_time_kst': 'datetime_kst', 'opening_price': 'open',
               'high_price': 'high', 'low_price': 'low', 'trade_price': 'close'}
    df.rename(columns=columns, inplace=True)
    df['datetime_utc'] = pd.to_datetime(df['datetime_utc'])
    df['datetime_kst'] = pd.to_datetime(df['datetime_kst'])

    return df


def isValidMarket(market: str) -> bool:
    for m in MARKETS:
        if m["market"] == market:
            return True

    return False


def minute(unit: int, qMarket: str, qCount: int, qTo='') -> pd.DataFrame:
    units = [1, 3, 5, 10, 15, 30, 60, 120]

    if unit not in units:
        raise ValueError("Parameter \"unit\" must be one of ", units)

    if qCount > 200:
        raise ValueError("Parameter \"count\" must be less or equal than 200")
    try:
        url = "https://api.upbit.com/v1/candles/minutes/" + str(unit)  # how to use path param
        if qTo == '':
            querystring = {"market": qMarket, "count": str(qCount)}
        else:
            querystring = {"market": qMarket, "to": qTo, "count": str(qCount)}

        headers = {"Accepted": "application/json"}

        response = requests.request("GET", url, headers=headers, params=querystring)
        print("Response code:", response)

        # return ast.literal_eval(response.text)
        # return pd.DataFrame.from_dict(ast.literal_eval(response.text))
        # return toDataframe(ast.literal_eval(response.text))
        response = response.text.replace('null', 'None')
        return toDataFrame(toDictionary(response))

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def day(qMarket: str, qCount: int, qTo='') -> pd.DataFrame:
    if qCount > 200:
        raise ValueError("Parameter \"count\" must be less or equal than 200")

    try:
        url = "https://api.upbit.com/v1/candles/days"
        querystring = {"market": qMarket, "count": str(qCount)}

        if qTo != '':
            querystring = {"market": qMarket, "to": qTo, "count": str(qCount)}

        headers = {"Accepted": "application/json"}

        response = requests.request("GET", url, headers=headers, params=querystring)
        print("Response code:", response)

        # return ast.literal_eval(response.text)
        # return pd.DataFrame.from_dict(ast.literal_eval(response.text))
        # print(response.text)

        response = response.text.replace('null', 'None')
        return toDataFrame(toDictionary(response))

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

def collectDaily(market: str, start: str) -> pd.DataFrame:
    """
    start: YYYY-MM-DD HH:MM:SS
    start date is exclusive
    """

    startDate = pd.to_datetime(start)
    currentDate = pd.to_datetime(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    delta = pd.Timedelta(currentDate - startDate).days
    print(delta)

    remainder = delta % 200
    if remainder != 0:
        numIter = int(delta / 200) + 1
        remainder = remainder  # 이 부분 수정해야할 수도 있음.
    else:
        numIter = int(delta / 200)
        remainder = 200

    dataframes = []
    print(currentDate)
    for i in range(numIter):
        if i == numIter - 1:  # Last iteration
            d = day(market, remainder, qTo=currentDate.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            d = day(market, 200, qTo=currentDate.strftime('%Y-%m-%d %H:%M:%S'))
        dataframes.append(d)
        currentDate = currentDate - pd.Timedelta(days=200)
        print(currentDate)
        time.sleep(3)

    df = pd.concat(dataframes, axis=0)
    return df


if __name__ == "__main__":
    df = collectDaily("KRW-BTC", "2017-09-24 00:00:00")

    # create(df, '[day]KRW-BTC.pickle', '')
    print(df['datetime_kst'])
