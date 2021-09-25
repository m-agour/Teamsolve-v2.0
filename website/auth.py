import datetime
import pytz
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .application.user import *
from .application.problem import *

from .codeforces.codeforces_api import get_solved_problems
from flask_login import login_user, login_required, logout_user, current_user, user_logged_out, AnonymousUserMixin

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if logged_in():
        return redirect(url_for('views.home'))

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        user = find_user_by_email(email)

        if user:
            if user.check_password(password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    email = ""
    name = ""

    if logged_in():
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        handle = request.form.get('handle')
        pass1 = request.form.get('password1')
        pass2 = request.form.get('password2')

        user = find_user_by_email(email)
        solved_problems = get_solved_problems(handle)

        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif pass1 != pass2:
            flash('Passwords don\'t match.', category='error')
        elif len(pass1) < 7:
            flash('Password must be at least 7 characters.', category='error')

        elif isinstance(solved_problems, tuple):
            flash('Please enter a valid codeforces handle.', category='error')

        else:
            new_user = register_user(name, email, pass1, handle)
            new_user.save()
            login_user(new_user, remember=True)

            for code in solved_problems:
                problem = find_problem_by_code(code)
                if not problem:
                    problem = Problem(name=code, code=code, judge='Codeforces')
                    problem.save()
                new_user.solved_ids.append(problem.id)
            new_user.save()
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("register.html", email=email, name=name, user=None)


def get_current_user():
    return find_user_by_id(current_user.id)


def logged_in():
    return not isinstance(current_user, AnonymousUserMixin)
