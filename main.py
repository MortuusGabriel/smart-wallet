from aiohttp import web
from db import *
import json


class WalletById(web.View):

    async def get(self):
        # walletId = self.request.match_info.get("walletId", None)
        # output = get_wallet_by_id(walletId)
        return web.json_response(status=404)

    async def post(self):
        data = await self.request.json()
        return web.json_response(status=201)

    async def delete(self):
        data = await self.request.json()
        walletId = self.request.match_info.get("walletId", None)
        token = str(data['token'])
        output = delete_wallet(token, walletId)
        return web.json_response(output, status=200)


class Wallets(web.View):

    async def get(self):
        data = await self.request.json()
        token = str(data['token'])
        output = get_wallets(token)
        return web.json_response(output, status=200)

    async def post(self):
        data = await self.request.json()
        wallet = create_wallet(data['token'], data['wallet_info'])
        output = {
            'result': wallet
        }
        return web.json_response(output, status=201)

    async def delete(self):
        return web.json_response(status=404)


class Transactions(web.View):

    async def get(self):
        data = await self.request.json()
        walletId = self.request.match_info.get("Id", None)
        token = str(data['token'])
        output = get_transactions_by_wallet_id(token, walletId)
        return web.json_response(output, status=200)

    async def post(self):
        data = await self.request.json()
        token = str(data['token'])
        output = create_transaction(data, token)
        return web.json_response(output, status=201)

    async def put(self):
        data = await self.request.json()
        transactionId = self.request.match_info.get("Id", None)
        output = update_transaction(data, transactionId)
        return web.json_response(output, status=200)

    async def delete(self):
        return web.json_response(status=204)


class Categories(web.View):

    async def get(self):
        data = await self.request.json()
        value = self.request.match_info.get("value", None)
        token = str(data['token'])
        output = get_categories_by_value(token, value)
        return web.json_response(output, status=200)

    async def post(self):
        data = await self.request.json()
        output = {
            'result': data
        }
        return web.json_response(output, status=201)

    async def delete(self):
        return web.json_response(status=204)


class Registrate(web.View):

    try:
        async def post(self):
            data = await self.request.json()
            output = {
                'token': create_user(data)
            }
            return web.json_response(output, status=201)
    except Exception as ex:
            print(ex)


class MainScreen(web.View):

    async def get(self):
        data = await self.request.json()
        token = str(data['token'])
        output = get_main_screen_data(token)
        return web.json_response(output, status=200)


app = web.Application()

app.router.add_view("/wallets", Wallets)
app.router.add_view("/transactions/{Id}", Transactions)
app.router.add_view("/wallets/{walletId}", WalletById)
app.router.add_view("/mainscreendata", MainScreen)
app.router.add_view("/transactions", Transactions)
app.router.add_view("/categories/person/{value}", Categories)
app.router.add_view("/registrate", Registrate)



if __name__ == '__main__':
    web.run_app(app, port=8000)
