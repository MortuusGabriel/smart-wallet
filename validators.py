import re
import peewee_validates


def money_to_string(dic):
    names = ['amount', 'limit', 'income', 'expense', 'value']
    for i in dic:
        if i in names:
            dic[i] = str(dic[i])
    return dic


def validate_value(field, data):
    if field.value and not re.fullmatch('^[0-9]+[.]?[0-9]*', field.value):
        raise peewee_validates.ValidationError("invalid value")


def validate_currency(field, data):
    if field.value and not re.fullmatch('[A-Z]{3}', field.value):
        raise peewee_validates.ValidationError("invalid currency")


def validate_name(field, data):
    if field.value and not re.fullmatch('[\s0-9a-zA-Zа-яА-ЯёЁ_\s]+', field.value):
        raise peewee_validates.ValidationError("invalid name")


class TransactionValidator(peewee_validates.Validator):
    wallet_id = peewee_validates.IntegerField(validators=[peewee_validates.validate_required()])
    value = peewee_validates.StringField(validators=[validate_value, peewee_validates.validate_not_empty(), peewee_validates.validate_required()])
    category_id = peewee_validates.IntegerField(validators=[peewee_validates.validate_required()])
    currency_id = peewee_validates.IntegerField(validators=[peewee_validates.validate_required()])
    transaction_time = peewee_validates.StringField(validators=[validate_value, peewee_validates.validate_not_empty(), peewee_validates.validate_required()])


class CategoryValidator(peewee_validates.Validator):
    name = peewee_validates.StringField(validators=[validate_name, peewee_validates.validate_not_empty(), peewee_validates.validate_required()])
    category_type = peewee_validates.BooleanField(validators=[peewee_validates.validate_required()])
    icon_id = peewee_validates.IntegerField(validators=[peewee_validates.validate_required()])


class UserValidator(peewee_validates.Validator):
    name = peewee_validates.StringField(validators=[validate_name, peewee_validates.validate_required()])
    email = peewee_validates.StringField(validators=[peewee_validates.validate_email(), peewee_validates.validate_not_empty(), peewee_validates.validate_required()])


class WalletValidator(peewee_validates.Validator):
    currency_id = peewee_validates.IntegerField(validators=[peewee_validates.validate_required()])
    name = peewee_validates.StringField(validators=[validate_name, peewee_validates.validate_not_empty(), peewee_validates.validate_required()])
    amount = peewee_validates.StringField(validators=[validate_value, peewee_validates.validate_not_empty(), peewee_validates.validate_required()])
    limit = peewee_validates.StringField(validators=[validate_value])