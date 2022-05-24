from jwt_authorize import jwt_encode, jwt_decode
from pycbrf.toolbox import ExchangeRates
from models import *
from datetime import *
from validators import *


def get_wallets(token):
    try:
        email = str(jwt_decode(token)['email'])
    except Exception:
        return None, 401

    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    wallets_query = Wallets.select().where(Wallets.user_id == user[0]['user_id'])
    wallets = [i for i in wallets_query.dicts().execute()]

    for i in wallets:
        i = money_to_string(i)
        currency_query = Currencies.select().where(Currencies.currency_id == i['currency_id'])
        i['currency'] = money_to_string(currency_query.dicts().execute()[0])
        del i['currency_id']

    return {"result": wallets}, 200


def create_wallet(token, json_data):
    try:
        email = str(jwt_decode(token)['email'])
    except Exception:
        return None, 401

    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    validator = WalletValidator()
    validator.validate(json_data)

    if len(validator.errors) != 0:
        return None, 406

    wal = Wallets.insert(user_id= user[0]['user_id'], currency_id= validator.data['currency_id'],
         name=validator.data['name'], amount=validator.data['amount'],
         limit=validator.data['limit'])
    wal.execute()

    result_query = Wallets.select().where(Wallets.wallet_id == Wallets.select(fn.MAX(Wallets.wallet_id))).limit(1)
    result = money_to_string(result_query.dicts().execute()[0])
    currency_query = Currencies.select().where(Currencies.currency_id == result['currency_id']).limit(1)
    result['currency'] = currency_query.dicts().execute()[0]
    del result['currency_id']

    return {"result": result}, 201


def update_wallet(data, token, walletId):
    try:
        email = str(jwt_decode(token)['email'])
    except Exception:
        return None, 401

    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    validator = WalletValidator()
    validator.validate(data)

    if len(validator.errors) != 0:
        return None, 406

    wal_query = Wallets.update(user_id= user[0]['user_id'], currency_id= validator.data['currency_id'],
         name=validator.data['name'], amount= validator.data['amount'],
         limit=validator.data['limit']).where(Wallets.wallet_id==walletId)
    wal_query.execute()

    result_query = Wallets.select().where(Wallets.wallet_id == walletId).limit(1)
    result = money_to_string(result_query.dicts().execute()[0])
    currency_query = Currencies.select().where(Currencies.currency_id == result['currency_id']).limit(1)
    result['currency'] = currency_query.dicts().execute()[0]
    del result['currency_id']

    return {"result": result}, 201


def delete_wallet(token, walletId):
    try:
        email = str(jwt_decode(token)['email'])
    except Exception:
        return None, 401

    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    wallets_query = Wallets.delete().where(
        (Wallets.user_id == user[0]["user_id"]) & (Wallets.wallet_id == walletId))
    result = wallets_query.execute()

    if result == 0:
        return None, 406

    return {"result": {"status": "OK"}}, 200


def get_transactions_by_wallet_id(token, wallet_id):
    try:
        email = str(jwt_decode(token)['email'])
    except Exception:
        return None, 401

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

    wal_query = Transactions.select().where(Transactions.wallet_id == wallet_id)
    answer = [i for i in wal_query.dicts().execute()]

    for i in answer:
        i = money_to_string(i)
        category_query = Categories.select().where(Categories.category_id == i['category_id'])
        category = money_to_string(category_query.dicts().execute()[0])
        currency_query = Currencies.select().where(Currencies.currency_id == i['currency_id'])
        currency = money_to_string(currency_query.dicts().execute()[0])
        i['category'] = category
        i['currency'] = currency
        i['value'] = str(i['value'])
        del i['currency_id']
        del i['category_id']

    return {"result": answer}, 200


def get_categories_by_value(token):
    try:
        email = str(jwt_decode(token)['email'])
    except Exception:
        return None, 401

    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    categories_query = Categories.select().where(
        ((Categories.user_id.is_null()) | (Categories.user_id == user[0]['user_id']))).order_by(Categories.category_id)
    categories = [i for i in categories_query.dicts().execute()]

    return {"result": categories}, 200


def create_user(json_data):
    validator = UserValidator()
    validator.validate(json_data)

    if len(validator.errors) != 0:
        return None, 406

    user_query = Users.select(Users.user_id).where(Users.email == validator.data['email'])
    user = user_query.dicts().execute()

    if user:
        token = jwt_encode(validator.data)
        query = Users.update(token=token).where(Users.user_id == int(user[0]['user_id']))
        query.execute()
        return token, 200

    token = jwt_encode(validator.data)
    data_source = [
        {'name': validator.data['name'], 'email': validator.data['email'], 'token': token},
    ]
    wal_query = Users.insert(data_source)
    wal_query.execute()
    return {"result": token}, 200


def get_main_screen_data(token):
    try:
        email = str(jwt_decode(token)['email'])
    except Exception:
        return None, 401

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

    currency_query = Currencies.select(Currencies.name, Currencies.value, Currencies.is_up).where(Currencies.currency_id > 1).limit(3)
    currencies = [money_to_string(i) for i in currency_query.dicts().execute()]

    wallets_query = Wallets.select().where(Wallets.user_id == user[0]['user_id'])
    wallets = [money_to_string(i) for i in wallets_query.dicts().execute()]

    for i in wallets:
        currency_query = Currencies.select().where(Currencies.currency_id == i['currency_id'])
        i['currency'] = money_to_string(currency_query.dicts().execute()[0])
        del i['currency_id']

    return {"balance": balance, "currencyDto": currencies, "wallets": wallets}, 200


def create_transaction(data, token):
    try:
        email = str(jwt_decode(token)['email'])
    except Exception:
        return None, 401

    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    validator = TransactionValidator()
    validator.validate(data)

    if len(validator.errors) != 0:
        return None, 406

    tr = Transactions.insert(wallet_id=validator.data['wallet_id'],
                                             category_id=validator.data['category_id'],
                                             value=validator.data['value'],
                                             currency_id=validator.data['currency_id'],
                      transaction_time=validator.data['transaction_time'])

    tr.execute()

    result_query = Transactions.select().where(Transactions.transaction_id == Transactions.select(fn.MAX(Transactions.transaction_id))).limit(1)
    result = money_to_string(result_query.dicts().execute()[0])

    currency_query = Currencies.select().where(Currencies.currency_id == result['currency_id']).limit(1)
    result['currency'] = currency_query.dicts().execute()[0]
    del result['currency_id']

    category_query = Categories.select().where(Categories.category_id == result['category_id']).limit(1)
    result['category'] = category_query.dicts().execute()[0]
    del result['category_id']

    return {"result": result}, 201


def update_transaction(data, token, transactionId):
    try:
        email = str(jwt_decode(token)['email'])
    except Exception:
        return None, 401

    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    validator = TransactionValidator()
    validator.validate(data)

    if len(validator.errors) != 0:
        return None, 406

    transactions_query = Transactions.update(wallet_id=validator.data['wallet_id'],
                                             category_id=validator.data['category_id'],
                                             value=validator.data['value'],
                                             currency_id=validator.data['currency_id'],
                                             transaction_time=validator.data['transaction_time']).where(
        Transactions.transaction_id == transactionId)

    transactions_query.execute()

    result_query = Transactions.select().where(Transactions.transaction_id == transactionId).limit(1)
    result = money_to_string(result_query.dicts().execute()[0])

    currency_query = Currencies.select().where(Currencies.currency_id == result['currency_id']).limit(1)
    result['currency'] = currency_query.dicts().execute()[0]
    del result['currency_id']

    category_query = Categories.select().where(Categories.category_id == result['category_id']).limit(1)
    result['category'] = category_query.dicts().execute()[0]
    del result['category_id']

    return {"result": result}, 200


def delete_transaction(data, token, transactionId):
    try:
        email = str(jwt_decode(token)['email'])
    except Exception:
        return None, 401

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
        return None, 406

    return {"status": "OK"}, 200


def create_category(data, token):
    try:
        email = str(jwt_decode(token)['email'])
    except Exception:
        return None, 401

    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    validator = CategoryValidator()
    validator.validate(data)

    if len(validator.errors) != 0:
        return None, 406

    cat = Categories.insert(name=validator.data['name'],
                                       category_type=validator.data['category_type'],
                                       icon_id=int(validator.data['icon_id']), user_id=user[0]['user_id'])
    cat.execute()

    result_query = Categories.select().where(Categories.category_id == Categories.select(fn.MAX(Categories.category_id))).limit(1)
    result = money_to_string(result_query.dicts().execute()[0])

    return {"result": result}, 201


def get_currencies(token):
    try:
        email = str(jwt_decode(token)['email'])
    except Exception:
        return None, 401

    user_query = Users.select().where(Users.email == email)
    user = user_query.dicts().execute()

    if user[0]['token'] != token:
        return None, 401

    currency_query = Currencies.select()
    currencies = [money_to_string(i) for i in currency_query.dicts().execute()]

    return {"result": currencies}, 200


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

