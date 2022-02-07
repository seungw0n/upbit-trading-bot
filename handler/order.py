#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Seung Won Joeng

시세 캔들 조회 : https://docs.upbit.com/reference#%EC%8B%9C%EC%84%B8-%EC%BA%94%EB%93%A4-%EC%A1%B0%ED%9A%8C
시세 종목 조회 : https://docs.upbit.com/reference#%EC%8B%9C%EC%84%B8-%EC%A2%85%EB%AA%A9-%EC%A1%B0%ED%9A%8C
"""

import hashlib
import jwt
import os
import requests
import uuid
from urllib.parse import urlencode

# Note that you need to
# Initialize str variables for access_key, secret_key which are personal keys from UpBit
# Where you can get it?
# https://upbit.com/mypage/open_api_management?



os.environ['UPBIT_OPEN_API_ACCESS_KEY'] = 'Your API ACCESS KEY'
os.environ['UPBIT_OPEN_API_SECRET_KEY'] = 'Your API SECRET KEY'
os.environ['UPBIT_OPEN_API_SERVER_URL'] = 'https://api.upbit.com'


# You can set your keys here, then ignore the above lines.
access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']


def parameterPayload(query: str) -> dict:
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    return payload


def marketBuy(market: str, price: str) -> bool:
    query = {
        'market': market,
        'side': 'bid',
        'price': price,
        'ord_type': 'price',
    }

    # payload = parameterPayload(query)
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    try:
        res = requests.request("POST", server_url + "/v1/orders", params=query, headers=headers)
        print("Response code: ", res)
        print(res.text)  # To handle history, modify here
        return True

    except requests.exceptions.RequestException as erra:
        print("AnyException : ", erra)
        return False


def marketSell(market: str, volume: str) -> bool:
    query = {  # price 을 None 로 해야할 수 있음
        'market': market,
        'side': 'bid',
        'price': None,
        'volume': volume,
        'ord_type': 'market',
    }

    payload = parameterPayload(query)

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    try:
        res = requests.request("POST", server_url + "/v1/orders", params=query, headers=headers)
        print("Response code: ", res)
        print(res.text)  # To handle history, modify here
        return True

    except requests.exceptions.RequestException as erra:
        print("AnyException : ", erra)
        return False



def calculateFee(quantity, price, fee):
    """ default fee: KRW 0.005"""
    return quantity * price * fee


if __name__ == '__main__':
    # marketBuy('KRW-BTC', '5000')
