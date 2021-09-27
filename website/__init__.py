import mongoengine
from flask import Flask
from flask_socketio import *
from flask_login import LoginManager

from .application import *
from .application.user import *
from .application.team import *
from .application.problem import *
from .application.set import *
from mongoengine import connect
from .init_database import *


app = Flask(__name__)
socketio = SocketIO(app)

from .views import views
from .auth import auth

app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')
app.secret_key = 'Hello darkness my old friend'

# mongoengine.register_connection(alias='core', name='teamsolve')
# mongoengine.connect('teamsolve', alias='default')
connect(host="mongodb+srv://dodicono:FArs2013@teamsolve.df6hd.mongodb.net/teamsolve",  alias='default')
connect(host="mongodb+srv://dodicono:FArs2013@teamsolve.df6hd.mongodb.net/teamsolve", alias='core')


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(uid):
    return find_user_by_id(uid)


if not find_problem_by_id(1):
    load_problems()

if not find_set_by_id(2):
    load_sets()

if not find_user_by_id(1):
    set_my_team()

for s in Set.objects.all():
    if s.count == 0:
        s.delete()
