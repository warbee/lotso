from flask import Flask, url_for, render_template, flash, request, session, redirect, g
from flask.ext.sqlalchemy import SQLAlchemy
import datetime
from flask.ext import admin, login
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import form, fields, validators
from flask.ext.admin.contrib import sqla
from flask.ext.admin import helpers, expose
import os
import random
import json

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config.debug = True
db = SQLAlchemy(app)

# custom app classes
import models
import eforms


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(models.User).get(user_id)

# Initialize flask-login
init_login()

def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')

    base36 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < len(alphabet):
        return sign + alphabet[number]

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36


def base36decode(number):
    return int(number, 36)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    marbles = db.session.query(models.Bag).filter_by(user_id=login.current_user.id).first()
    return render_template('home.html', logged_in=login.current_user.is_authenticated()
                                        ,marbles=marbles.gold_marbles)

@app.route('/signin')
def signin():
    return render_template('signin.html')


@app.route('/signup')
def signup():
    return render_template('newaccount.html')


@app.route('/login', methods=['POST'])
def log_in():
    form = eforms.LoginForm(request.form)
    try:
        if helpers.validate_form_on_submit(form):
            user = form.get_user()

            check = form.validate_login(user)
            if check:
                login.login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Wrong login/pw!')
                return redirect(url_for('signin'))

    except Exception as e:
        flash('error logging in: ', e)
        return redirect(url_for('index'))


@app.route('/register', methods=['POST'])
def register():
    form = eforms.RegistrationForm(request.form)
    if helpers.validate_form_on_submit(form):
        user = models.User()
        bag = models.Bag()

        if form.validate_login(user):
            form.populate_obj(user)

            user.password = generate_password_hash(form.password.data)

            try:
                db.session.add(user)
                db.session.commit()

                login.login_user(user)
                msg = 'User saved'
                bag.user_id = user.id
                bag.gold_marbles = 3

                try:
                    db.session.add(bag)
                    db.session.commit()
                    msg += ' marbles added!'
                except:
                    db.session.rollback()
                    msg += ' failed saving marbles...'

                flash(msg)
                return redirect(url_for('home'))

            except Exception as e:
                flash('Error saving user: %s' % e)
                db.session.rollback()
                return redirect(url_for('signup'))
    else:
        flash('user exists.')
        return redirect(url_for('signup'))

    flash(form.name.data)
    return render_template('debug.html', msg='error')


@app.route('/logout')
def logout():
    login.logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()