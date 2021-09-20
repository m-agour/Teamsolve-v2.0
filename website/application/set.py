import mongoengine


class Set(mongoengine.Document):
    id = mongoengine.SequenceField(primary_key=True)
    name = mongoengine.StringField(required=True)
    type = mongoengine.StringField(required=True)
    problems_ids = mongoengine.ListField(default=[])
    count = mongoengine.IntField(default=0)
    meta = {
        'db_alias': 'core',
        'collection': 'sets'
    }



def find_set_by_id(sid: int):
    print(sid)
    my_set = Set.objects(id=sid).first()
    return my_set
