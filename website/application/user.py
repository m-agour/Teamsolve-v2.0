import mongoengine
from flask_login import UserMixin
from website.additional import *
from werkzeug.security import generate_password_hash, check_password_hash


class User(mongoengine.Document, UserMixin):
    id = mongoengine.SequenceField(primary_key=True)
    email = mongoengine.StringField(required=True, unique=True)
    handle = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=True)
    name = mongoengine.StringField(required=True)
    team_id = mongoengine.IntField(default=0)
    settings = mongoengine.DictField(default={
        'darkMode': False
    })
    solved_ids = mongoengine.ListField(default=[])
    due_ids = mongoengine.ListField(default=[])
    meta = {
        'db_alias': 'core',
        'collection': 'users'
    }

    def toggle_dark_mode(self):
        self.settings['darkMode'] = not self.settings['darkMode']
        self.save()

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def join_team(self, team_id):
        self.team_id = team_id
        self.save()

    def set_due(self, problem_id: int):
        self.due_ids.append(problem_id)
        self.save()

    def set_solved(self, problem_id: int):
        self.solved_ids.append(problem_id)
        self.save()


def register_user(name: str, email: str, password: str, handle: str) -> User:
    # creat user object
    password = generate_password_hash(password)
    user = User(email=email, handle=handle, name=name, password=password)
    return user


def find_user_by_email(email: str):
    user = User.objects(email=email).first()
    return user


def find_user_by_id(uid):
    user = User.objects(id=uid).first()
    return user
