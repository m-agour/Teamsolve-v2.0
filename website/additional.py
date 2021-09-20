import datetime
import hashlib

import pytz


def get_date_cairo():
    tz = pytz.timezone('Africa/Cairo')
    date = datetime.datetime.now(tz).date()
    return date


def _encrypt_id(num):
    return str(hex((51 + num) * 651)[2:])[::-1].upper()


def _decrypt_id(enc):
    return int(int(enc[::-1], 16) / 651 - 54)


def generate_invitation_code(team_id):
    return _encrypt_id(team_id)


def get_team_id_from_invitation_code(code):
    return _decrypt_id(code)


