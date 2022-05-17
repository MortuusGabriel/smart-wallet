from jwt_authorize import jwt_encode, jwt_decode
from pycbrf.toolbox import ExchangeRates
from models import *
from datetime import *
from validators import *
import threading


def get_wallets(token):
    email = str(jwt_decode(token)['email'])
    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    wallets_query = Wallets.select().where(Wallets.user_id == user[0]['user_id'])
    wallets = []
    for i in wallets_query.dicts().execute():
        wallets.append(i)
    return wallets, 200


def create_wallet(token, json_data):
    email = str(jwt_decode(token)['email'])
    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()


    if user[0]['token'] != token:
        return None, 401

    validator = WalletValidator()
    validator.validate(json_data)

    if len(validator.errors) != 0:
        return None, 406

    data_source = [
        {"user_id": user[0]['user_id'], "currency_id": validator.data['currency_id'],
         "name": validator.data['name'], "amount": validator.data['amount'],
         "limit": validator.data['limit']},
    ]

    wallets_query = Wallets.insert(data_source)
    result = wallets_query.execute()
    return data_source, 201


def delete_wallet(token, walletId):
    email = str(jwt_decode(token)['email'])

    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    wallets_query = Wallets.delete().where(
        (Wallets.user_id == user[0]["user_id"]) & (Wallets.wallet_id == walletId))
    result = wallets_query.execute()

    if result == 0:
        return None, 400

    return {"status": "OK"}, 200


def get_transactions_by_wallet_id(token, wallet_id):
    email = str(jwt_decode(token)['email'])
    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    wallets_query = Wallets.select(Wallets.wallet_id).where(Wallets.user_id == user[0]['user_id'])
    wallets = [i['wallet_id'] for i in wallets_query.dicts().execute()]

    if len(wallets) == 0:
        return None, 400

    if user[0]['token'] != token:
        return None, 401

    if int(wallet_id) not in wallets:
        return None, 400

    answer = []
    wal_query = Transactions.select().where(Transactions.wallet_id == wallet_id)
    for i in wal_query.dicts().execute():
        i['transaction_time'] = i['transaction_time'].isoformat()
        answer.append(i)

    if len(answer) == 0:
        return None, 400

    return answer, 200


def get_categories_by_value(token, value):
    email = str(jwt_decode(token)['email'])
    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    categories_query = Categories.select().where(
        ((Categories.user_id.is_null()) | (Categories.user_id == user[0]['user_id']))).select().where(
        Categories.category_type == int(value)).order_by(Categories.category_id)
    categories = [i for i in categories_query.dicts().execute()]

    if len(categories) == 0:
        return None, 400

    return categories, 200


def create_user(json_data):
    validator = UserValidator()
    validator.validate(json_data)

    user_query = Users.select(Users.user_id).where(Users.email == validator.data['email'])
    user = user_query.execute()
    if user:
        token = jwt_encode(validator.data)
        return token, 200

    if len(validator.errors) != 0:
        return None, 406

    token = jwt_encode(validator.data)
    data_source = [
        {'name': validator.data['name'], 'email': validator.data['email'], 'token': token},
    ]
    wal_query = Users.insert(data_source)
    wal_query.execute()
    return token, 200


def get_main_screen_data(token):
    email = str(jwt_decode(token)['email'])
    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    balance_query = Wallets.select(fn.SUM(Wallets.amount), fn.SUM(Wallets.income),
                                   fn.SUM(Wallets.expense)).where(Wallets.user_id == user[0]['user_id'])
    balance = balance_query.dicts().execute()[0]

    if len(balance) == 0:
        return None, 400

    for i in balance:
        balance[i] = DecimalEncoder().encode(balance[i])
    currency_query = Currencies.select(Currencies.name, Currencies.value, Currencies.is_up)
    currencies = [i for i in currency_query.dicts().execute()]

    ######какие поля выбирать#########
    wallets_query = Wallets.select().where(Wallets.user_id == user[0]['user_id'])
    wallets = [i for i in wallets_query.dicts().execute()]

    if len(balance) == 0:
        return None, 400

    return {"balance": balance, "currencyDto": currencies, "wallets": wallets}, 200


def create_transaction(data, token):
    email = str(jwt_decode(token)['email'])
    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    validator = TransactionValidator()
    validator.validate(data['data'])

    if len(validator.errors) != 0:
        return None, 406

    transactions_query = Transactions.insert(wallet_id=validator.data['walletId'],
                                             category_id=validator.data['categoryId'],
                                             value=validator.data['value'],
                                             currency=validator.data['currency'])

    transactions_query.execute()

    return {"status": "OK"}, 201


def update_transaction(data, token, transactionId):
    email = str(jwt_decode(token)['email'])
    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    validator = TransactionValidator()
    validator.validate(data['data'])

    if len(validator.errors) != 0:
        return None, 406

    transactions_query = Transactions.update(wallet_id=validator.data['walletId'],
                                             category_id=validator.data['categoryId'],
                                             value=validator.data['value'],
                                             currency=validator.data['currency']).where(
        Transactions.transaction_id == transactionId)

    transactions_query.execute()
    return {"status": "OK"}, 200


def delete_transaction(data, token, transactionId):
    email = str(jwt_decode(token)['email'])
    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    transactions = Transactions.select(Transactions.transaction_id
                                       ).where(
        Transactions.wallet_id.in_(Wallets.select().where(Wallets.user_id == user[0]['user_id'])))
    transactions = [str(i) for i in transactions]

    if str(transactionId) not in transactions:
        return None, 400

    transactions_query = Transactions.delete().where(Transactions.transaction_id == transactionId)
    result = transactions_query.execute()

    if result == 0:
        return None, 400

    return {"status": "OK"}, 200


def create_category(data, token):
    email = str(jwt_decode(token)['email'])
    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    validator = CategoryValidator()
    validator.validate(data['data'])

    if len(validator.errors) != 0:
        return None, 406

    category_query = Categories.insert(name=validator.data['name'],
                                       category_type=validator.data['category_type'],
                                       icon=int(validator.data['icon']), user_id=user[0]['user_id'])
    category_query.execute()
    return {"status": "OK"}, 201


def get_currencies(token):
    email = str(jwt_decode(token)['email'])
    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    currency_query = Currencies.select()
    currencies = [i for i in currency_query.dicts().execute()]

    return currencies, 200


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

        query = Currencies.update(value=rates_today[str(i['name'])].value, is_up=is_up).where(
            Currencies.currency_id == i['currency_id'])
        query.execute()

    print("Валюты обновлены")
