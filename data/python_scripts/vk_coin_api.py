from requests import post
import json


class VkCoin:
    def __init__(self, user_id, key):
        self.link = 'https://coin-without-bugs.vkforms.ru/merchant/'
        self.user_id = user_id
        self.key = key

    def _send_api_request(self, method, params):
        while True:
            response = post(self.link + method, json=params).json()
            if 'error' not in response:
                return response['response']
            else:
                print(response)

    def set_shop_name(self, name):
        data = {'merchantId': self.user_id, 'key': self.key, 'name': name}
        return self._send_api_request('set', params=data)

    def get_transactions(self, tx, last_tx=None):
        data = {'merchantId': self.user_id, 'key': self.key, 'tx': tx}
        if last_tx:
            data['lastTx'] = last_tx
        return self._send_api_request('tx', params=data)

    def get_balance(self, user=None):
        if not user:
            user = self.user_id
        data = {'merchantId': self.user_id, 'key': self.key, "userIds": [user]}
        response = self._send_api_request('score', params=data)
        return response[str(user)]

    def get_payment_url(self, amount, user_id=False, payload=0, free_amount=False):
        if not user_id:
            user_id = int(self.user_id)
        user_id = '{:x}'.format(user_id)
        amount = '{:x}'.format(amount)
        payload = '{:x}'.format(payload)
        link = f'https://vk.com/coin#m{user_id}_{amount}_{payload}'
        if free_amount:
            link += '_1'
        return link

    def send_payment(self, to_id, amount, mark_as_merchant=False):
        data = {'merchantId': self.user_id, 'key': self.key, 'toId': to_id, 'amount': amount}
        if mark_as_merchant:
            data['markAsMerchant'] = True
        return self._send_api_request('send', params=data)
