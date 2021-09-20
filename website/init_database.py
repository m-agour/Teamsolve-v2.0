from website.application.user import *
from website.application.team import Team, find_team_by_id
from website.application.problem import *
from website.application.set import *
from website.codeforces.codeforces_api import *
from website.additional import *


def load_problems():
    problems = generate_ordered_problems_id_name_solved()
    new_set = Set(name='Most solved on codeforces', type='main')
    new_set.save()

    for i in range(len(problems)):
        name = problems[i][1]
        if len(name) > 50:
            name = name[:45] + '...'
        prob = Problem(code=problems[i][0], name=name, judge='Codeforces')
        prob.save()
        new_set.problems_ids.append(prob.id)
        new_set.count += 1
    new_set.save()


def set_my_team():
    date = get_date_cairo()
    my_team = Team(name='Error Squad', daily_goal=3, index=51, set_id=1, last_updated=date, solved_today=True)
    my_team.save()

    user1 = User(email='mohamedelfeky250@gmail.com', handle='Mohamed.-.Elfeky',
                 password='sha256$FgzKH4Qn$6759112c8d461024fc4a240923c9de3ec0641452e0ea9ea3a3657a5da5bc652b',
                 name='Mohamed Abdelfatah Elfeky', team_id='1')
    user2 = User(email='mo.aggour@gmail.com', handle='M_Agour',
                 password='sha256$TM30OmFM$6eeefef0ac53ade11375cb35d243949e0ff428589b19b3768df13b4d4d931271',
                 name='Mohamed Nagy', team_id='1')
    user3 = User(email='mostafahussinelsayed@gmail.com', handle='Mostafa_Hu',
                 password='sha256$jcPUKg0q$c4be88c1476b43749c93f0b8f31fc8b3919b4a63494fb5bfb9236cf266ede997',
                 name='Mustafa Hussin', team_id='1')

    user1.save()
    user2.save()
    user3.save()


def load_sets():
    sets = json.load(open('website/codeforces/sets.json'))

    existing_problems = Problem.objects
    existing_problems_codes = [x.code for x in existing_problems]
    for s in sets:
        new_set = Set(name=s['name'], type=s['type'])
        new_set.save()
        for prob in s['set']:
            name = prob['name']
            code = prob['code']
            judge = prob['judge']

            if len(name) > 50:
                name = name[:45] + '...'

            # problem = existing_problems.filter(Problem.code == code, Problem.judge == judge).first()
            if code in existing_problems_codes:
                problem = existing_problems[existing_problems_codes.index(code)]
            else:
                problem = Problem(code=prob['code'], name=name, judge=judge)
                problem.save()

            new_set.problems_ids.append(problem.id)
            new_set.count += 1
        new_set.save()
