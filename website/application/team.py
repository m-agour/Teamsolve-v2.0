import mongoengine
from website.additional import *


class Team(mongoengine.Document):
    id = mongoengine.SequenceField(primary_key=True)
    name = mongoengine.StringField(required=True)
    daily_goal = mongoengine.IntField(default=2)
    index = mongoengine.IntField(default=1)
    last_updated = mongoengine.DateField(default=get_date_cairo())
    solved_today = mongoengine.BooleanField(default=False)
    set_id = mongoengine.IntField()
    no_vacation = mongoengine.IntField()
    meta = {
        'db_alias': 'core',
        'collection': 'teams'
    }


def find_team_by_id(tid: str):
    team = Team.objects(id=tid).first()
    return team

