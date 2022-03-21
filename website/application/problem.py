import json

import mongoengine


class Problem(mongoengine.Document):
    id = mongoengine.SequenceField(primary_key=True)
    name = mongoengine.StringField()
    code = mongoengine.StringField()
    judge = mongoengine.StringField()
    paid = mongoengine.BooleanField()


def find_problem_by_id(sid: int, as_json=False):
    if as_json:
        prob = json.loads(Problem.objects(id=sid).first().to_json())
        prob['paid'] = 0
        prob['id'] = prob['_id']
        return prob
    return Problem.objects(id=sid).first()


def find_problem_by_code(code: str):
    problem = Problem.objects(code=code).first()
    return problem
