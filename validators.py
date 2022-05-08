import re
import peewee_validates


def validate_value(field, data):
    if field.value and not re.fullmatch('[0-9]+[.]?[0-9]*', field.value):
        raise peewee_validates.ValidationError("invalid value")


def validate_currency(field, data):
    if field.value and not re.fullmatch('[A-Z]{3}', field.value):
        raise peewee_validates.ValidationError("invalid currency")


class SimpleValidator(peewee_validates.Validator):
    walletId = peewee_validates.IntegerField()
    value = peewee_validates.StringField(validators=[validate_value, peewee_validates.validate_not_empty()])
    categoryId = peewee_validates.IntegerField()
    currency = peewee_validates.StringField(validators=[validate_currency, peewee_validates.validate_not_empty()])