from threading import Thread
from .application.functionality import *
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_socketio import send
from . import *

views = Blueprint("views", __name__)


@views.route('/', methods=["GET", "POST"])
@login_required
def home():
    if request.method == 'POST':
        current_user.toggle_dark_mode()

    team = get_current_team()
    user = get_current_user()

    if not team:
        return render_template("home.html", user=user, team=None, problemset=[], solved=[],
                               code='', team_mates=[], colors=[])

    # update_user_and_mates(team)
    # new_day(team)

    thread = Thread(target=refresh, args=(team,))

    thread.daemon = True
    thread.start()

    sol = get_today_solved_problems_ids(get_current_user())
    problems = get_today_problems(team.id)
    team_mates = get_team_mates(current_user)
    team_mates_ind = range(len(team_mates))
    team_mates = [(team_mates[i], len(get_today_solved_problems(team_mates[i])), get_color(i),
                   len(get_dues_list(team_mates[i]))) for i in team_mates_ind]
    team_mates = sorted(team_mates, key=lambda x: x[1], reverse=True)

    team = get_current_team()
    dues = get_dues_list(get_current_user())
    return render_template("home.html", user=user, team=team, problems=problems, solved=sol,
                           code=generate_invitation_code(team.id), team_mates=team_mates, dues=dues)


@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not get_current_user().team_id:
        return redirect(url_for('views.home'))

    set_problems_count = get_current_set().count
    sets = sorted(list(Set.objects), key=lambda x: x.count, reverse=True)
    sets = [i for i in sets if i.count >= 40]
    print([i.name for i in sets])
    if request.method == 'POST':
        if request.form['btn'] == 'change':
            set_id = int(request.form['radio'])
            # team settings
            name = request.form.get('name')
            # user settings
            user_name = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            try:
                daily_goal = int(request.form.get('number'))
            except:
                flash("Please enter the goal.", category='error')
                return render_template("settings.html", user=get_current_user(), team=get_current_team(), sets=sets,
                                       set_count=set_problems_count)

            try:
                index = int(request.form.get('index'))
            except:
                flash("Please enter the index.", category='error')
                return render_template("settings.html", user=get_current_user(), team=get_current_team(), sets=sets,
                                       set_count=set_problems_count)

            user = find_user_by_email(email)

            if user and current_user.id != user.id:
                flash('Email already exists.', category='error')

            elif len(email) < 4:
                flash('Email must be greater than 3 characters.', category='error')

            elif not name:
                flash('Please enter the team name.', category='error')

            elif not user_name:
                flash('Please enter your name.', category='error')

            elif daily_goal <= 0:
                flash('Problems number per day must be larger than 0.', category='error')

            elif daily_goal > 50:
                flash('Woo! take it easy champ, leave some for next month. (max is 50 per day)', category='error')

            elif index < 0:
                flash('Index must be greater than zero.', category='error')

            elif index > set_problems_count:
                flash('Index is so large.', category='error')

            elif password and len(password) < 5:
                flash('Password must be at least 5 characters.', category='error')

            else:
                team = get_current_team()
                user = get_current_user()
                team.name = name
                team.daily_goal = daily_goal
                team.index = index
                if set_id != team.set_id:
                    team.set_id = set_id
                    team.index = 1

                req_keys = request.form.keys()
                for day in team.duty_days.keys():
                    team.duty_days[day] = day in req_keys
                team.save()

                if user.name != user_name:
                    user.name = user_name

                if user.email != email:
                    user.email = email

                if password:
                    print(password)
                    user.password = generate_password_hash(password)

                user.save()

                flash('Settings has been modified.', category='success')
                return redirect(url_for('views.settings'))

        elif request.form['btn'] == 'leave':
            u = get_current_user()
            u.team_id = 0
            u.save()
            flash('You left the team!', category='success')
            return redirect(url_for('views.home'))

        else:
            current_user.toggle_dark_mode()

    return render_template("settings.html", user=get_current_user(), team=get_current_team(), sets=sets,
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
            team = Team(name=name, daily_goal=number, set_id=1)
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


@views.route('/solved')
@login_required
def solved():
    problem_id = int(request.args.get('id'))
    new = request.args.get('type') == 'new'
    team = get_current_team()
    user = get_current_user()

    user.set_solved(problem_id)

    if not new:
        user.due_ids.remove(problem_id)
    else:
        team.solved_today = True

    team.save()
    user.save()
    return redirect(url_for('views.home'))

@socketio.on('message')
def message(msg):
    send(msg)


@socketio.on('update problem set')
def update_problem_set():
    # user progress and problemset
    team = get_current_team()
    solved_problems = get_today_solved_problems(get_current_user())
    today_problems = get_today_problems(team.id)
    problems = [[i.id, i.name, i.code, i.judge, i in solved_problems] for i in today_problems]
    socketio.emit('update problem set', problems)


@socketio.on('update mates progress')
def update_mates_progress():
    # progress of mates
    team_mates = get_team_mates(current_user)
    t_len = len(team_mates)
    team_mates = [[team_mates[i].name, len(get_today_solved_problems(team_mates[i])), len(get_dues_list(team_mates[i])),
                   get_color(i)] for i in range(t_len)]
    socketio.emit('update team mates progress', team_mates)


@socketio.on('update solutions for user')
def update_solutions(user_id, solved_problems_codes):
    update_user_solved_problems(find_user_by_id(user_id), solved_problems_codes)


@socketio.on('dark')
def dark(dm):
    socketio.emit('messages', 'hi')
    user = get_current_user()
    user.settings['darkMode'] = bool(dm)
    user.save()


def get_current_team():
    return find_team_by_id(get_current_user().team_id)


def get_current_user() -> User:
    return find_user_by_id(current_user.id)


def get_current_set():
    set_id = get_current_team().set_id
    my_set = find_set_by_id(set_id)
    return my_set


def refresh(team):
    update_user_and_mates(team)
    new_day(team)
    check_set(team)

