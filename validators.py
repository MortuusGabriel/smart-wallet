import re
import peewee_validates


def validate_value(field, data):
    if field.value and not re.fullmatch('[0-9]+[.]?[0-9]*', field.value):
        raise peewee_validates.ValidationError("invalid value")


def validate_currency(field, data):
    if field.value and not re.fullmatch('[A-Z]{3}', field.value):
        raise peewee_validates.ValidationError("invalid currency")


def validate_name(field, data):
    if field.value and not re.fullmatch('[\s0-9a-zA-Zа-яА-ЯёЁ]+', field.value):
        raise peewee_validates.ValidationError("invalid name")


class TransactionValidator(peewee_validates.Validator):
    walletId = peewee_validates.IntegerField()
    value = peewee_validates.StringField(validators=[validate_value, peewee_validates.validate_not_empty()])
    categoryId = peewee_validates.IntegerField()
    currency = peewee_validates.StringField(validators=[validate_currency, peewee_validates.validate_not_empty()])


class CategoryValidator(peewee_validates.Validator):
    name = peewee_validates.StringField(validators=[validate_name, peewee_validates.validate_not_empty()])
    category_type = peewee_validates.IntegerField()
    icon = peewee_validates.IntegerField()


class UserValidator(peewee_validates.Validator):
    name = peewee_validates.StringField(validators=[validate_name, peewee_validates.validate_not_empty()])
    email = peewee_validates.StringField(validators=[peewee_validates.validate_email(), peewee_validates.validate_not_empty()])


class WalletValidator(peewee_validates.Validator):
    currency_id = peewee_validates.IntegerField()
    name = peewee_validates.StringField(validators=[validate_name, peewee_validates.validate_not_empty()])
    amount = peewee_validates.StringField(validators=[validate_value, peewee_validates.validate_not_empty()])
    limit = peewee_validates.StringField(validators=[validate_value, peewee_validates.validate_not_empty()])