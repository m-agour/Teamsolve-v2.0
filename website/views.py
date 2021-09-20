import datetime
from flask_login import login_user, login_required, logout_user, current_user
import pytz
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .application.user import *
from .application.team import Team, find_team_by_id
from .application.problem import *
from .application.set import *
from .codeforces.codeforces_api import *

views = Blueprint("views", __name__)


@views.route('/', methods=["GET", "POST"])
@login_required
def home():
    if request.method == 'POST':
        current_user.toggle_dark_mode()

    team = get_team()
    user = current_user
    # update_user_and_mates(team)
    if not team:
        return render_template("home.html", user=user, team=None, problemset=[], solved=[],
                               code='', team_mates=[], colors=[])

    update_user_and_mates(team)
    new_day(team)

    sol = get_today_solved_problems_ids(get_current_user())
    problems = get_today_problems()
    team_mates = get_team_mates(current_user)
    team_mates_ind = range(len(team_mates))
    team_mates = [(team_mates[i].name, len(get_today_solved_problems(team_mates[i])), i,
                   len(get_dues_list(team_mates[i]))) for i in team_mates_ind]

    team_mates = sorted(team_mates, key=lambda x: x[1], reverse=True)

    colors = ['#e6194B', '#4363d8', '#9A6324', '#911eb4', '#469990', '#808000', '#000075']

    while len(colors) < len(team_mates):
        colors += colors

    team = get_team()
    dues = get_dues_list(get_current_user())

    # thread = Thread(target=update_user_and_mates, args=(team,))
    # thread.daemon = True
    # thread.start()

    return render_template("home.html", user=user, team=team, problems=problems, solved=sol,
                           code=generate_invitation_code(team.id), team_mates=team_mates, colors=colors, dues=dues)


@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not get_current_user().team_id:
        return redirect(url_for('views.home'))

    set_problems_count = get_set().count
    sets = list(Set.objects)

    if request.method == 'POST':
        set_id = int(request.form['radio'])
        if request.form['btn'] == 'change':
            # team settings
            name = request.form.get('name')
            # user settings
            user_name = request.form.get('name')
            email = request.form.get('name')
            password = request.form.get('name')

            try:
                daily_goal = int(request.form.get('number'))
            except:
                flash("Please enter the goal.", category='error')
                return render_template("settings.html", user=get_current_user(), team=get_team(), sets=sets,
                                       set_count=set_problems_count)

            try:
                index = int(request.form.get('index'))
            except:
                flash("Please enter the index.", category='error')
                return render_template("settings.html", user=get_current_user(), team=get_team(), sets=sets,
                                       set_count=set_problems_count)

            user = find_user_by_email(email)

            if user and current_user.id != user.id:
                flash('Email already exists.', category='error')

            elif len(email) < 4:
                flash('Email must be greater than 3 characters.', category='error')

            elif not name:
                flash('Please enter the team name.', category='error')

            if not user_name:
                flash('Please enter your name.', category='error')

            elif daily_goal <= 0:
                flash('Problems number per day must be larger than 0.', category='error')

            elif daily_goal > 50:
                flash('Woo! take it easy champ, leave some for next month. (max is 50 per day)', category='error')

            elif index < 0:
                flash('Index must be greater than zero.', category='error')

            elif index > set_problems_count:
                flash('Index is so large.', category='error')

            elif len(password) < 5:
                flash('Password must be at least 5 characters.', category='error')

            else:
                team = get_team()
                team.name = name
                team.daily_goal = daily_goal
                team.index = index
                if set_id != team.set_id:
                    team.set_id = set_id
                    team.index = 0
                team.save()
                flash('Settings has been modified.', category='success')
                return redirect(url_for('views.settings'))

        elif request.form['btn'] == 'leave':
            get_current_user().team_id = 0
            get_current_user().save()
            flash('You left the team!', category='success')
            return redirect(url_for('views.home'))

    return render_template("settings.html", user=get_current_user(), team=get_team(), sets=sets,
                           set_count=set_problems_count)


@views.route('/create-team', methods=['GET', 'POST'])
@login_required
def createTeam():
    if current_user.team_id:
        flash("You have already joined a team.", category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        name = request.form.get('name')
        try:
            number = int(request.form.get('number'))
        except:
            flash("Please enter your goal.", category='error')
            return render_template("create-team.html", user=current_user)

        if not name:
            flash('Please enter the name.', category='error')

        if current_user.team_id:
            flash("You have already joined a team.", category='error')
            return redirect(url_for('views.home'))

        elif number <= 0:
            flash('Problems number per day must be larger than 0.', category='error')

        elif number > 50:
            flash('Woo! take it easy champ, leave some for next month. (max is 50 per day)', category='error')

        else:

            team = Team(name=name, daily_goal=number, members_ids=[current_user.id], set_id=0)
            team.save()

            user = get_current_user()
            user.join_team(team.id)
            user.save()

            flash('Team created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("create-team.html", user=current_user)


@views.route('/join-team', methods=['GET', 'POST'])
@login_required
def joinTeam():
    if request.method == 'POST':
        code = request.form.get('code')
        if not code:
            flash('Please enter the invitation code.', category='error')

        elif not find_team_by_id(get_team_id_from_invitation_code(code)):
            flash('Please enter a valid invitation code.', category='error')

        else:
            team_id = get_team_id_from_invitation_code(code)
            get_current_user().join_team(team_id)
            flash('Joined Team!', category='success')
            return redirect(url_for('views.home'))
    return render_template("join-team.html", user=current_user)


def get_team():
    return find_team_by_id(current_user.team_id)


def get_set():
    set_id = get_team().set_id
    my_set = find_set_by_id(set_id)
    return my_set


def get_current_user() -> User:
    return find_user_by_id(current_user.id)


def get_problem(problem_id):
    return find_problem_by_id(problem_id)


def get_daily_goal():
    return get_team().daily_goal


def get_today_problems():
    set_id = get_team().set_id
    my_set = find_set_by_id(set_id)
    start = get_team().index
    end = min(start + get_daily_goal(), my_set.count + 1)
    return [find_problem_by_id(i) for i in my_set.problems_ids[start:end]]


def get_today_problems_names():
    return [i.name for i in get_today_problems()]


def get_today_solved_problems(user: User):
    today = get_today_problems()
    solved_today = [x for x in today if x in user.solved_ids]
    return solved_today


def get_today_unsolved_problems(user: User):
    today_problems = get_today_problems()
    solved_problems = get_today_solved_problems(user)
    return [i for i in today_problems if i not in solved_problems]


def get_today_solved_problems_ids(user: User):
    return [i.id for i in get_today_solved_problems(user)]


def get_team_members(team_id: int):
    return User.objects(team_id=team_id).all()


def get_team_mates(user: User):
    teamMates = list(get_team_members(user.team_id))
    teamMates.remove(get_current_user())
    return teamMates


def new_day(team):
    if is_new_day(team):
        if is_someone_solved_today(team):
            set_dues(team)
            my_set = get_set()
            if team.index + team.daily_goal <= my_set.count:
                team.index += team.daily_goal
            else:
                team.index = 1
                team.set_id += 1

            team.solved_today = False
            team.last_updated = get_date_cairo()
            team.save()


def set_dues(team):
    members = get_team_members(team.id)
    for i in members:
        for j in get_today_unsolved_problems(i):
            i.dues.append(j)
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

    for code in solved_on_codeforces:
        problem = find_problem_by_code(code)
        if not problem:
            problem = Problem(name=code, code=code, judge='Codeforces')
            problem.save()
        if problem.id not in user.solved_ids:
            if problem in user.due_ids:
                user.due_ids.remove(problem.id)
            else:
                sol = True
            user.solved_ids.append(problem.id)
        user.save()
    return sol


def update_user_and_mates(team):
    lst = get_team_members(team.id)
    for i in lst:
        if update_user_solved_problems(i):
            get_team().solved_today = True
            team.save()


def update_all_teams():
    teams = Team.objects()
    for team in teams:
        update_user_and_mates(team)

# @views.route('/solved')
# @login_required
# def solved():
#     problem_id = int(request.args.get('num'))
#     new = request.args.get('type') == 'new'
#     get_current_user().set_solved(problem_id)
#
#     if not new:
#         for i in list(Problem.query.filter(Problem.id == problemIndex).all()):
#             get_current_user().dues.remove(i)
#     else:
#         get_team().solvedToday = True
#
#     db.session.commit()
#     return redirect(url_for('views.home'))
