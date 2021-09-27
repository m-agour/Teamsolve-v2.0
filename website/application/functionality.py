from website.application.user import *
from website.application.team import Team, find_team_by_id
from website.application.problem import *
from website.application.set import *
from website.codeforces.codeforces_api import *


def get_team(tid):
    return find_team_by_id(tid)


def get_set(set_id):
    my_set = find_set_by_id(set_id)
    return my_set


def get_user(uid) -> User:
    return find_user_by_id(uid)


def get_problem(problem_id):
    return find_problem_by_id(problem_id)


def get_today_problems(team_id):
    team = get_team(team_id)
    set_id = team.set_id
    my_set = find_set_by_id(set_id)
    start = team.index - 1
    end = min(start + team.daily_goal, my_set.count + 1)
    return [find_problem_by_id(i) for i in my_set.problems_ids[start:end]]


def get_today_problems_names(team_id):
    return [i.name for i in get_today_problems(team_id)]


def get_today_solved_problems(user: User):
    today = get_today_problems(user.team_id)
    solved_today = [x for x in today if x.id in user.solved_ids]
    return solved_today


def get_today_unsolved_problems(user: User):
    today_problems = get_today_problems(user.team_id)
    solved_problems = get_today_solved_problems(user)
    return [i for i in today_problems if i not in solved_problems]


def get_today_solved_problems_ids(user: User):
    return [i.id for i in get_today_solved_problems(user)]


def get_today_solved_problems_codes(user: User):
    return [i.code for i in get_today_solved_problems(user)]


def get_team_members(team_id: int):
    return User.objects(team_id=team_id).all()


def get_team_mates(user: User):
    teamMates = list(get_team_members(user.team_id))
    teamMates.remove(user)
    return teamMates


def new_day(team):
    if is_new_day(team):
        if is_someone_solved_today(team) and team.duty_days[get_today_name_initials_cairo()]:
            set_dues(team)
            team.index += team.daily_goal
            if team.index > get_set(team.set_id).count:
                team.index = 1
                team.set_id += 1
            check_set(team)
            team.solved_today = False
        team.last_updated = get_date_cairo()
        team.save()


def set_dues(team):
    members = get_team_members(team.id)
    for i in members:
        for j in get_today_unsolved_problems(i):
            i.due_ids.append(j.id)
        i.save()


def is_new_day(team):
    return str(team.last_updated) != str(get_date_cairo())


def is_someone_solved_today(team):
    return team.solved_today


def get_dues_list(user):
    return [find_problem_by_id(i) for i in user.due_ids]


def update_user_solved_problems(user):
    sol = False
    solved_on_codeforces = get_solved_problems(user.handle)
    problems = get_today_problems(user.team_id)
    for code in solved_on_codeforces:
        problem = find_problem_by_code(code)
        if not problem:
            problem = Problem(name=code, code=code, judge='Codeforces')
            problem.save()

        if problem.id not in user.solved_ids:
            user.solved_ids.append(problem.id)
            if problem.id in user.due_ids:
                user.due_ids.remove(problem.id)
            if problem in problems:
                sol = True
        else:
            break

    user.save()
    return sol


def update_user_and_mates(team):
    lst = get_team_members(team.id)
    for i in lst:
        if update_user_solved_problems(i):
            team.solved_today = True
            team.save()


def update_all_teams():
    teams = Team.objects()
    for team in teams:
        update_user_and_mates(team)


def check_set(team):
    my_set = get_set(team.set_id)
    if not my_set or not my_set.count:
        team.set_id = 1
        team.index = 1
        team.save()
    if not my_set or not my_set.count:
        team.set_id += 1
        team.save()

