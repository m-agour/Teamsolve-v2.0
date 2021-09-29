import datetime
import hashlib

import pytz


def get_date_cairo():
    tz = pytz.timezone('Africa/Cairo')
    date = datetime.datetime.now(tz).date()
    return date


def get_today_name_cairo():
    tz = pytz.timezone('Africa/Cairo')
    day = datetime.datetime.now(tz).strftime("%A")
    return day


def get_today_name_initials_cairo():
    return get_today_name_cairo()[:3].lower()


def _encrypt_id(num):
    return str(hex((51 + num) * 651)[2:])[::-1].upper()


def _decrypt_id(enc):
    return int(int(enc[::-1], 16) / 651 - 51)


def generate_invitation_code(team_id):
    return _encrypt_id(team_id)


def get_team_id_from_invitation_code(code):
    return _decrypt_id(code)


def get_color(index):
    colors = ['#fb2d60', '#2478b7', '#ea2128', '#f3bd19', '#8b1ec4']
    return colors[index % 5 ]