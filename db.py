from config import DATABASE
from peewee import *
from jwt_authorize import  jwt_encode, jwt_decode

# перенести креды в переменные окружения
conn = MySQLDatabase(DATABASE['db'], host=DATABASE['host'], port=DATABASE['port'], user=DATABASE['user'], passwd=DATABASE['passwd'])



class BaseModel(Model):
    class Meta:
        database = conn


class Categories(BaseModel):
    category_id = AutoField(column_name='category_id', primary_key=True)
    name = CharField(column_name='name', max_length=45)
    category_type = BooleanField(column_name='category_type')
    user_id = IntegerField(column_name='user_id', null=True)

    class Meta:
        table_name = 'categories'


class Wallets(BaseModel):
    wallet_id = AutoField(column_name='wallet_id', primary_key=True)
    user_id = IntegerField(column_name='user_id')
    currency_id = IntegerField(column_name='currency_id')
    name = CharField(column_name='name', max_length=45)
    amount = IntegerField(column_name='amount', default=0)
    limit = IntegerField(column_name='limit', null=True)
    income = IntegerField(column_name='income', null=True, default=0)
    expense = IntegerField(column_name='expense', null=True, default=0)
    is_hide = BooleanField(column_name='is_hide', default=False)

    class Meta:
        table_name = 'wallets'


class Users(BaseModel):
    user_id = AutoField(column_name='user_id', primary_key=True)
    name = CharField(column_name='name', max_length=45)
    email = CharField(column_name='email', max_length=255)
    token = CharField(column_name='token', max_length=255)
    create_time = TimestampField(column_name='create_time')

    class Meta:
        table_name = 'users'


class Transactions(BaseModel):
    transaction_id = AutoField(column_name='transaction_id', primary_key=True)
    wallet_id = IntegerField(column_name='wallet_id')
    category_id = IntegerField(column_name='category_id', null=True)
    value = IntegerField(column_name='value')
    currency = CharField(column_name='currency', max_length=45)
    transaction_time = TimestampField(column_name='transaction_time')


class Currencies(BaseModel):
    currency_id = AutoField(column_name='currency_id', primary_key=True)
    name = CharField(column_name='name', max_length=45)
    value = FloatField(column_name='value')
    is_up = BooleanField(column_name='is_up')

    class Meta:
        table_name = 'categories'


def get_wallets(token):
    try:
        email = str(jwt_decode(token)['email'])
        user_query = Users.select().where(Users.email == email)
        user = user_query.dicts().execute()
        print(user[0])


        if user[0]['token'] == token:
            wallets_query = Wallets.select().where(Wallets.user_id == user[0]['user_id'])
            wallets = []
            for i in wallets_query.dicts().execute():
                wallets.append(i)
            return wallets
        else:
            ########Ошибка###########
            pass

    except Exception as e:
        return {"status": str(e)}


def create_wallet(token, json_data):
    try:
        email = str(jwt_decode(token)['email'])
        user_query = Users.select().where(Users.email == email)
        user = user_query.dicts().execute()

        if user[0]['token'] == token:
            wallets_query = Wallets.insert(user_id=user[0]['user_id'], currency_id=json_data['currency_id'],
                                           name=json_data['name'], amount=json_data['amount'], limit=json_data['limit'],
                                           )
            wallets_query.execute()
        return {"status": "OK"}
    except Exception as e:
        return {"status": str(e)}


def delete_wallet(token, walletId):
    try:
        email = str(jwt_decode(token)['email'])
        user_query = Users.select().where(Users.email == email)
        user = user_query.dicts().execute()

        if user[0]['token'] == token:
            wallets_query = Wallets.delete().where(Wallets.user_id == user[0]["user_id"] and Wallets.wallet_id == walletId)
            result = wallets_query.execute()
            if result == 0:
                return {"status": "no such element"}
            else:
                return {"status": "OK"}
    except Exception as e:
        return {"status": str(e)}


def get_wallet_by_id(wallet_id):
    try:
        wal_query = Wallets.select().where(Wallets.wallet_id == wallet_id).limit(1)
        return wal_query.dicts().execute()[0]
    except Exception as e:
        return {"status": str(e)}


def get_transactions_by_wallet_id(wallet_id):
    wal_query = Transactions.select().where(Transactions.wallet_id == wallet_id)
    answer = []
    for i in wal_query.dicts().execute():
        answer.append(i)
    return answer


def get_categories_by_person_id(value):
    wal_query = Categories.select().where(Categories.user_id == value or Categories.user_id == None)
    answer = []
    for i in wal_query.dicts().execute():
        answer.append(i)
    return answer


def create_user(json_data):
    try:
        token = jwt_encode(json_data)
        data_source = [
            {'name': json_data['name'], 'email': json_data['email'], 'token': token},
        ]
        wal_query = Users.insert(data_source)
        wal_query.execute()
        return token
    except Exception as e:
        return {"status": "error"}


conn.close()