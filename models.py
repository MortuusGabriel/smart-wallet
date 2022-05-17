from config import DATABASE
from peewee import *
from json import JSONEncoder
import datetime
import decimal

# перенести креды в переменные окружения
conn = MySQLDatabase(DATABASE['db'], host=DATABASE['host'], port=DATABASE['port'], user=DATABASE['user'], passwd=DATABASE['passwd'])


class DecimalEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


class BaseModel(Model):
    class Meta:
        database = conn


class Categories(BaseModel):
    category_id = AutoField(column_name='category_id', primary_key=True)
    name = CharField(column_name='name', max_length=45)
    category_type = BooleanField(column_name='category_type')
    user_id = IntegerField(column_name='user_id', null=True)
    icon = IntegerField(column_name='icon_id', null=True)

    class Meta:
        table_name = 'categories'


class Wallets(BaseModel):
    wallet_id = AutoField(column_name='wallet_id', primary_key=True)
    user_id = IntegerField(column_name='user_id')
    currency_id = IntegerField(column_name='currency_id')
    name = CharField(column_name='name', max_length=45)
    amount = FloatField(column_name='amount', default=0)
    limit = FloatField(column_name='limit', null=True)
    income = FloatField(column_name='income', null=True, default=0)
    expense = FloatField(column_name='expense', null=True, default=0)
    is_hide = BooleanField(column_name='is_hide', default=False)

    class Meta:
        table_name = 'wallets'


class Users(BaseModel):
    user_id = AutoField(column_name='user_id', primary_key=True)
    name = CharField(column_name='name', max_length=45)
    email = CharField(column_name='email', max_length=255)
    token = CharField(column_name='token', max_length=255)
    create_time = DateTimeField(column_name='create_time', default=datetime.datetime.now)

    class Meta:
        table_name = 'users'


class Transactions(BaseModel):
    transaction_id = AutoField(column_name='transaction_id', primary_key=True)
    wallet_id = IntegerField(column_name='wallet_id')
    category_id = IntegerField(column_name='category_id', null=True)
    value = FloatField(column_name='value')
    currency = CharField(column_name='currency', max_length=45)
    transaction_time = DateTimeField(column_name='transaction_time', default=datetime.datetime.now)

    class Meta:
        table_name = 'transactions'


class Currencies(BaseModel):
    currency_id = AutoField(column_name='currency_id', primary_key=True)
    name = CharField(column_name='name', max_length=45)
    value = FloatField(column_name='value')
    is_up = BooleanField(column_name='is_up')
    icon = CharField(column_name='icon', max_length=45)
    full_name = CharField(column_name='full_name', max_length=255)
    full_list_name = CharField(column_name='full_list_name', max_length=255)


    class Meta:
        table_name = 'currencies'


conn.close()