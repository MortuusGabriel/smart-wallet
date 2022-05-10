from jwt_authorize import jwt_encode, jwt_decode
from pycbrf.toolbox import ExchangeRates
from models import *
from datetime import *
from validators import *
import threading


def get_wallets(token):
    try:
        email = str(jwt_decode(token)['email'])
        user_query = Users.select().where(Users.email == email)
        user = user_query.dicts().execute()


        if user[0]['token'] == token:
            wallets_query = Wallets.select().where(Wallets.user_id == user[0]['user_id'])
            wallets = []
            for i in wallets_query.dicts().execute():
                wallets.append(i)
            return wallets
        else:
            return {"status": "invalid token"}

    except Exception as e:
        return {"status": str(e)}


def create_wallet(token, json_data):
    try:
        email = str(jwt_decode(token)['email'])
        user_query = Users.select().where(Users.email == email)
        user = user_query.dicts().execute()
        if user[0]['token'] == token:
            validator = WalletValidator()
            validator.validate(json_data)
            if len(validator.errors) == 0:
                wallets_query = Wallets.insert(user_id=user[0]['user_id'], currency_id=validator.data['currency_id'],
                                               name=validator.data['name'], amount=validator.data['amount'],
                                               limit=validator.data['limit'],
                                               )
                wallets_query.execute()
                return {"status": "OK"}
            else:
                return str(validator.errors)
        else:
            return {"status": "invalid token"}
    except Exception as e:
        return {"status": str(e)}


def delete_wallet(token, walletId):
    try:
        email = str(jwt_decode(token)['email'])
        user_query = Users.select().where(Users.email == email)
        user = user_query.dicts().execute()

        if user[0]['token'] == token:
            wallets_query = Wallets.delete().where((Wallets.user_id == user[0]["user_id"]) & (Wallets.wallet_id == walletId))
            result = wallets_query.execute()
            if result == 0:
                return {"status": "no such element"}
            else:
                return {"status": "OK"}
        else:
            return {"status": "invalid token"}
    except Exception as e:
        return {"status": str(e)}


def get_wallet_by_id(wallet_id):
    try:
        wal_query = Wallets.select().where(Wallets.wallet_id == wallet_id).limit(1)
        return wal_query.dicts().execute()[0]
    except Exception as e:
        return {"status": str(e)}


def get_transactions_by_wallet_id(token, wallet_id):
    try:
        # получение токена пользователя из бд
        email = str(jwt_decode(token)['email'])
        user_query = Users.select().where(Users.email == email)
        user = user_query.dicts().execute()

        wallets_query = Wallets.select(Wallets.wallet_id).where(Wallets.user_id == user[0]['user_id'])
        wallets = [i['wallet_id'] for i in wallets_query.dicts().execute()]

        ######здесь ошибка, если не нашлось пользователей#######
        if user[0]['token'] == token:
            answer = []
            if int(wallet_id) in wallets:
                wal_query = Transactions.select().where(Transactions.wallet_id == wallet_id)
                for i in wal_query.dicts().execute():
                    i['transaction_time'] = i['transaction_time'].isoformat()
                    answer.append(i)
            if len(answer) == 0 or int(wallet_id) not in wallets:
                return {"status": "nothing found"}
            else:
                return answer
        else:
            return {"status": "invalid token"}
    except Exception as e:
        return {"status": str(e)}


def get_categories_by_value(token, value):
    try:
        email = str(jwt_decode(token)['email'])
        user_query = Users.select().where(Users.email == email)
        user = user_query.dicts().execute()

        if user[0]['token'] == token:
            categories_query = Categories.select().where(((Categories.user_id.is_null()) | (Categories.user_id == user[0]['user_id']))).select().where(Categories.category_type == int(value)).order_by(Categories.category_id)
            categories = [i for i in categories_query.dicts().execute()]
            if len(categories) == 0:
                return {"status": "nothing found"}
            else:
                return categories
        else:
            return {"status": "invalid token"}
    except Exception as e:
        return {"status": str(e)}


def create_user(json_data):
    try:
        validator = UserValidator()
        validator.validate(json_data)
        if len(validator.errors) == 0:
            token = jwt_encode(validator.data)
            data_source = [
                {'name': validator.data['name'], 'email': validator.data['email'], 'token': token},
            ]
            wal_query = Users.insert(data_source)
            wal_query.execute()
            return token
        else:
            return str(validator.errors)

    except Exception as e:
        return {"status": "error"}


def get_main_screen_data(token):
    try:
        email = str(jwt_decode(token)['email'])
        user_query = Users.select().where(Users.email == email)
        user = user_query.dicts().execute()

        if user[0]['token'] == token:
            balance_query = Wallets.select(fn.SUM(Wallets.amount), fn.SUM(Wallets.income), fn.SUM(Wallets.expense)).where(Wallets.user_id == user[0]['user_id'])
            balance = balance_query.dicts().execute()[0]
            for i in balance:
                balance[i] = DecimalEncoder().encode(balance[i])
            currency_query = Currencies.select(Currencies.name, Currencies.value, Currencies.is_up)
            currencies = [i for i in currency_query.dicts().execute()]
            ######какие поля выбирать#########
            wallets_query = Wallets.select().where(Wallets.user_id == user[0]['user_id'])
            wallets = [i for i in wallets_query.dicts().execute()]


            if len(balance) == 0 or len(currencies)==0 or len(wallets)==0:
                return {"status": "nothing found"}
            else:
                return {"balance": balance, "currencyDto": currencies, "wallets": wallets}
        else:
            return {"status": "invalid token"}
    except Exception as e:
        return {"status": str(e)}


def create_transaction(data, token):
    try:
        email = str(jwt_decode(token)['email'])
        user_query = Users.select().where(Users.email == email)
        user = user_query.dicts().execute()

        if user[0]['token'] == token:
            validator = TransactionValidator()
            validator.validate(data['data'])
            if len(validator.errors) == 0:
                transactions_query = Transactions.insert(wallet_id=validator.data['walletId'], category_id=validator.data['categoryId'],
                                                         value=float(validator.data['value']), currency=validator.data['currency'])
                transactions_query.execute()
                return {"status": "OK"}
            else:
                return str(validator.errors)
        else:
            return {"status": "invalid token"}
    except Exception as e:
        return {"status": str(e)}


def update_transaction(data, transactionId):
    try:
        token = data['token']
        email = str(jwt_decode(token)['email'])
        user_query = Users.select().where(Users.email == email)
        user = user_query.dicts().execute()

        if user[0]['token'] == token:
            validator = TransactionValidator()
            validator.validate(data['data'])
            if len(validator.errors) == 0:
                transactions_query = Transactions.update(wallet_id=validator.data['walletId'], category_id=validator.data['categoryId'],
                                                         value=float(validator.data['value']), currency=validator.data['currency']).where(Transactions.transaction_id == transactionId)

                transactions_query.execute()
                return {"status": "OK"}
            else:
                return str(validator.errors)
        else:
            return {"status": "invalid token"}
    except Exception as e:
        return {"status": str(e)}


def delete_transaction(data, transactionId):
    try:
        token = data['token']
        email = str(jwt_decode(token)['email'])
        user_query = Users.select().where(Users.email == email)
        user = user_query.dicts().execute()

        if user[0]['token'] == token:
            transactions = Transactions.select(Transactions.transaction_id
                                               ).where(Transactions.wallet_id.in_(Wallets.select().where(Wallets.user_id==user[0]['user_id'])))
            transactions = [str(i) for i in transactions]
            if str(transactionId) in transactions:
                transactions_query = Transactions.delete().where(Transactions.transaction_id==transactionId)
                if transactions_query.execute() > 0:
                    return {"status": "OK"}
                else:
                    return {"status": "no rows deleted"}
            else:
                return {"status": "no such transaction"}
        else:
            return {"status": "invalid token"}
    except Exception as e:
        return {"status": str(e)}


def create_category(data):
    try:
        token = data['token']
        email = str(jwt_decode(token)['email'])
        user_query = Users.select().where(Users.email == email)
        user = user_query.dicts().execute()

        if user[0]['token'] == token:
            validator = CategoryValidator()
            validator.validate(data['data'])
            if len(validator.errors) == 0:
                category_query = Categories.insert(name=validator.data['name'], category_type=validator.data['category_type'],
                                                         icon=int(validator.data['icon']), user_id=user[0]['user_id'])
                category_query.execute()
                return {"status": "OK"}
            else:
                return str(validator.errors)
        else:
            return {"status": "invalid token"}
    except Exception as e:
        return {"status": str(e)}


def update_currencies():
    currencies_query = Currencies.select().where(Currencies.currency_id > 1)
    currencies = currencies_query.dicts().execute()
    rates_today = ExchangeRates(datetime.now())
    rates_the_day_before = ExchangeRates(datetime.now() - timedelta(days=1))

    for i in currencies:
        is_up = i['is_up']
        if rates_today[str(i['name'])].value > rates_the_day_before[str(i['name'])].value:
            is_up = True
        elif rates_today[str(i['name'])].value < rates_the_day_before[str(i['name'])].value:
            is_up = False

        query = Currencies.update(value=rates_today[str(i['name'])].value, is_up=is_up).where(Currencies.currency_id == i['currency_id'])
        query.execute()

    print("Валюты обновлены")
