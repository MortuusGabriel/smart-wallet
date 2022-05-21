from datetime import datetime, timedelta, timezone
from jwt import (
    JWT,
    jwk_from_dict,
    jwk_from_pem,
)
from jwt.utils import get_int_from_datetime

payload_data = {
    "name": "Oleg",
    "email": "olegmail.com",
    'iat': get_int_from_datetime(datetime.now(timezone.utc)),
    'exp': get_int_from_datetime(datetime.now(timezone.utc) + timedelta(days=1))

}


def jwt_encode(payload_data):
    payload_data['iat'] = get_int_from_datetime(datetime.now(timezone.utc))
    payload_data['exp'] = get_int_from_datetime(datetime.now(timezone.utc) + timedelta(days=1))
    instance = JWT()

    with open('rsa_private_key.pem', 'rb') as fh:
        signing_key = jwk_from_pem(fh.read())

    token = instance.encode(payload_data, signing_key, alg='RS256')
    return token


def jwt_decode(token):
    instance = JWT()
    with open('rsa_public_key.pem', 'rb') as fh:
        verifying_key = jwk_from_pem(fh.read())

    message_received = instance.decode(
        token, verifying_key, do_time_check=False)
    return message_received

