import mongoengine


class Problem(mongoengine.Document):
    id = mongoengine.SequenceField(primary_key=True)
    name = mongoengine.StringField()
    code = mongoengine.StringField()
    judge = mongoengine.StringField()
    paid = mongoengine.BooleanField()


def find_problem_by_id(sid: int):
    problem = Problem.objects(id=sid).first()
    return problem


def find_problem_by_code(code: str):
    problem = Problem.objects(code=code).first()
    return problem
