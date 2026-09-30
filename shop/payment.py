import json

import requests

MERCHANT_ID = ''
ZP_API_REQUESTS = 'https://sandbox.zarinpal.com/pg/v4/payment/request.json'
ZP_API_VERIFY = 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json'
ZP_API_STARTPAY = 'https://sandbox.zarinpal.com/pg/StartPay/'
CALLBACK_URL = 'https://127.0.0.1:8000/api/v1/shop/payment/verify/'


def send_payment_request(order, phone_number):
    data = {
        'merchant_id': MERCHANT_ID,
        'amount': int(order.total_price),
        'description': CALLBACK_URL,
        'metadata': {'mobile': phone_number}
    }
    headers = {
        'accept': 'application/json', 'content-type': 'application/json'
    }
    try:
        response = requests.post(ZP_API_REQUESTS, data=json.dumps(data), headers=headers, timeout=10)
        result = response.json()
        if result.get('data') and result['data'].get('code') == 100:
            authority = result['data']['authority']
            order.authority = authority
            order.save()
            return f"{ZP_API_STARTPAY}{authority}", None
        return None, result.get('errors')
    except requests.exceptions.RequestException as e:
        return None, str(e)


def verify_payment(authority, amount):
    data = {
        'merchant_id': MERCHANT_ID,
        amount: int(amount),
        'authority': authority
    }
    headers = {'accept': 'application/json', 'content-type': 'application/json'}

    try:
        response = requests.post(ZP_API_VERIFY, data=json.dumps(data), headers=headers, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            'errors': str(e)
        }
