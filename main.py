from aiohttp import web
from db import *
import json


class WalletById(web.View):

    async def get(self):
        walletId = self.request.match_info.get("walletId", None)
        output = get_wallet_by_id(walletId)
        return web.json_response(output, status=200)

    async def post(self):
        data = await self.request.json()
        output = {
            'result': data
        }
        return web.json_response(output, status=201)

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
        return web.json_response(status=204)


class Transactions(web.View):

    async def get(self):
        walletId = await self.request.match_info.get("walletId", None)
        output = get_transactions_by_wallet_id(walletId)
        return web.json_response(output, status=200)

    async def post(self):
        data = await self.request.json()
        output = {
            'result': data
        }
        return web.json_response(output, status=201)

    async def delete(self):
        return web.json_response(status=204)


class Categories(web.View):

    async def get(self):
        value = await self.request.match_info.get("value", None)
        output = get_categories_by_person_id(value)
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


app = web.Application()

app.router.add_view("/wallets", Wallets)
app.router.add_view("/wallets/{walletId}", WalletById)
app.router.add_view("/categories/person/{value}", Categories)
app.router.add_view("/transactions/withCategory/{walletId}", Transactions)
app.router.add_view("/registrate", Registrate)


if __name__ == '__main__':
    web.run_app(app, port=8000)
