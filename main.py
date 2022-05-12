from time import sleep
from aiohttp import web
from db import *
from datetime import datetime, timedelta
import json
from threading import Timer
import schedule


class WalletById(web.View):

    async def get(self):
        return web.json_response(status=404)

    async def post(self):
        data = await self.request.json()
        return web.json_response(status=201)

    async def delete(self):
        try:
            data = await self.request.json()
            walletId = self.request.match_info.get("walletId", None)
            token = str(data['token'])
            output = delete_wallet(token, walletId)
            return web.json_response(output, status=200)
        except Exception as ex:
            return str(ex)


class Wallets(web.View):

    async def get(self):
        try:
            data = await self.request.json()
            token = str(data['token'])
            output = get_wallets(token)
            return web.json_response(output, status=200)
        except Exception as ex:
            return str(ex)

    async def post(self):
        try:
            data = await self.request.json()
            output = create_wallet(data['token'], data['wallet_info'])
            return web.json_response(output, status=201)
        except Exception as ex:
            return str(ex)

    async def delete(self):
        return web.json_response(status=404)


class Transactions(web.View):

    async def get(self):
        try:
            data = await self.request.json()
            walletId = self.request.match_info.get("Id", None)
            token = str(data['token'])
            output = get_transactions_by_wallet_id(token, walletId)
            return web.json_response(output, status=200)
        except Exception as ex:
            return str(ex)

    async def post(self):
        try:
            data = await self.request.json()
            token = str(data['token'])
            output = create_transaction(data, token)
            return web.json_response(output, status=200)
        except Exception as ex:
            return str(ex)

    async def put(self):
        try:
            data = await self.request.json()
            transactionId = self.request.match_info.get("Id", None)
            output = update_transaction(data, transactionId)
            return web.json_response(output, status=200)
        except Exception as ex:
            return str(ex)

    async def delete(self):
        try:
            data = await self.request.json()
            transactionId = self.request.match_info.get("Id", None)
            output = delete_transaction(data, transactionId)
            return web.json_response(output, status=200)
        except Exception as ex:
            return str(ex)


class Categories(web.View):

    async def get(self):
        try:
            data = await self.request.json()
            value = self.request.match_info.get("value", None)
            token = str(data['token'])
            output = get_categories_by_value(token, value)
            return web.json_response(output, status=200)
        except Exception as ex:
            return str(ex)

    async def post(self):
        try:
            data = await self.request.json()
            output = create_category(data)
            return web.json_response(output, status=201)
        except Exception as ex:
            return str(ex)

    async def delete(self):
        return web.json_response(status=204)


class Registrate(web.View):

    async def post(self):
        try:
            data = await self.request.json()
            output = {
                'token': create_user(data)
            }
            return web.json_response(output, status=201)
        except Exception as ex:
            return str(ex)


class MainScreen(web.View):

    async def get(self):
        try:
            data = await self.request.json()
            token = str(data['token'])
            output = get_main_screen_data(token)
            return web.json_response(output, status=200)
        except Exception as ex:
            return str(ex)


app = web.Application()

app.router.add_view("/wallets", Wallets)
app.router.add_view("/transactions/{Id}", Transactions)
app.router.add_view("/wallets/{walletId}", WalletById)
app.router.add_view("/mainscreen", MainScreen)
app.router.add_view("/transactions", Transactions)
app.router.add_view("/categories/person/{value}", Categories)
app.router.add_view("/categories", Categories)
app.router.add_view("/person", Registrate)


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


if __name__ == '__main__':
    # update_currencies()
    # timer = RepeatTimer(60, update_currencies)
    # timer.start()
    web.run_app(app, port=8000)
    # timer.cancel()
