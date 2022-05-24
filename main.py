from aiohttp import web
from db import *
from threading import Timer


class WalletById(web.View):
    async def put(self):
        try:
            data = await self.request.json()
            walletId = self.request.match_info.get("walletId", None)
            token = str(self.request.headers['Authorization']).split()[1]
            output, status = update_wallet(data, token, walletId)
            if output:
                return web.json_response(output, status=status)
            else:
                return web.Response(status=status)
        except Exception as ex:
            return web.Response(status=400)

    async def delete(self):
        try:
            data = await self.request.json()
            walletId = self.request.match_info.get("walletId", None)
            token = str(self.request.headers['Authorization']).split()[1]
            output, status = delete_wallet(token, walletId)
            if output:
                return web.json_response(output, status=status)
            else:
                return web.Response(status=status)
        except Exception as ex:
            return web.Response(status=400)


class Wallets(web.View):

    async def get(self):
        try:
            data = await self.request.json()
            token = str(self.request.headers['Authorization']).split()[1]
            output, status = get_wallets(token)

            if output:
                return web.json_response(output, status=status)
            else:
                return web.Response(status=status)
        except Exception as ex:
            return web.Response(status=400)

    async def post(self):
        try:
            data = await self.request.json()
            token = str(self.request.headers['Authorization']).split()[1]
            output, status = create_wallet(token, data)
            if output:
                return web.json_response(output, status=status)
            else:
                return web.Response(status=status)
        except Exception as ex:
            return web.Response(status=400)



class Transactions(web.View):

    async def get(self):
        try:
            data = await self.request.json()
            walletId = self.request.match_info.get("Id", None)
            token = str(self.request.headers['Authorization']).split()[1]
            output, status = get_transactions_by_wallet_id(token, walletId)
            if output:
                return web.json_response(output, status=status)
            else:
                return web.Response(status=status)
        except Exception as ex:
            return web.Response(status=400)

    async def post(self):
        try:
            data = await self.request.json()
            token = str(self.request.headers['Authorization']).split()[1]
            output, status = create_transaction(data, token)
            if output:
                return web.json_response(output, status=status)
            else:
                return web.Response(status=status)
        except Exception as ex:
            return web.Response(status=400)

    async def put(self):
        try:
            data = await self.request.json()
            transactionId = self.request.match_info.get("Id", None)
            token = str(self.request.headers['Authorization']).split()[1]
            output, status = update_transaction(data, token, transactionId)
            if output:
                return web.json_response(output, status=status)
            else:
                return web.Response(status=status)
        except Exception as ex:
            return web.Response(status=400)

    async def delete(self):
        try:
            data = await self.request.json()
            transactionId = self.request.match_info.get("Id", None)
            token = str(self.request.headers['Authorization']).split()[1]
            output, status = delete_transaction(data, token, transactionId)
            if output:
                return web.json_response(output, status=status)
            else:
                return web.Response(status=status)
        except Exception as ex:
            return web.Response(status=400)


class Categories(web.View):

    async def get(self):
        try:
            data = await self.request.json()
            token = str(self.request.headers['Authorization']).split()[1]
            output, status = get_categories_by_value(token)
            if output:
                return web.json_response(output, status=status)
            else:
                return web.Response(status=status)
        except Exception as ex:
            return web.Response(status=400)

    async def post(self):
        try:
            data = await self.request.json()
            token = str(self.request.headers['Authorization']).split()[1]
            output, status = create_category(data, token)
            if output:
                return web.json_response(output, status=status)
            else:
                return web.Response(status=status)
        except Exception as ex:
            return web.Response(status=400)


class Registrate(web.View):

    async def post(self):
        try:
            data = await self.request.json()
            result, status = create_user(data)
            if result:
                return web.json_response(result, status=status)
            else:
                return web.Response(status=status)

        except Exception as ex:
            return web.Response(status=400)


class MainScreen(web.View):

    async def get(self):
        try:
            data = await self.request.json()
            token = str(self.request.headers['Authorization']).split()[1]
            output, status = get_main_screen_data(token)
            if output:
                return web.json_response(output, status=status)
            else:
                return web.Response(status=status)
        except Exception as ex:
            return web.Response(status=400)


class Currencies(web.View):

    async def get(self):
        try:
            data = await self.request.json()
            token = str(self.request.headers['Authorization']).split()[1]
            output, status = get_currencies(token)
            if output:
                return web.json_response(output, status=status)
            else:
                return web.Response(status=status)
        except Exception as ex:
            return web.Response(status=400)


app = web.Application()

app.router.add_view("/wallets", Wallets)
app.router.add_view("/transactions/{Id}", Transactions)
app.router.add_view("/wallets/{walletId}", WalletById)
app.router.add_view("/mainscreen", MainScreen)
app.router.add_view("/transactions", Transactions)
app.router.add_view("/categories", Categories)
app.router.add_view("/person", Registrate)
app.router.add_view("/currencies", Currencies)


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


if __name__ == '__main__':
    update_currencies()
    timer = RepeatTimer(3600, update_currencies)
    timer.start()
    web.run_app(app, port=8000)
    timer.cancel()
