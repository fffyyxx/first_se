# coding:utf-8
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from controllers.models.models import User
from werkzeug.security import check_password_hash

loginView = Blueprint('loginView', __name__)


@loginView.route('/login', methods=['GET', 'POST'])
def login_view():
    # 登录界面
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(User.LoginName == username).first()
        if user and check_password_hash(user.password_hash, password):
            try:
                model = User.query.filter_by(LoginName=username).first()
                session['login'] = 'A1akPTQJiz9wi9yo4rDz8ubM1b1'
                session['loginname'] = model.LoginName
                # session['password'] = password
                session['user_id'] = model.id
                session['is_admin'] = model.IsAdmin
                return redirect(url_for('Frame.view_frame'))
            except Exception as e:
                print(e)
        else:
            return redirect(url_for('loginView.login_view'))
    return render_template('login.html')


# 登出
@loginView.route('/login-out')
def login_out():
    session.clear()
    return redirect(url_for('loginView.login_view'))


def login_check(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            if "login" in session:
                if session['login'] == 'A1akPTQJiz9wi9yo4rDz8ubM1b1':
                    return f(*args, **kwargs)
                else:
                    return redirect(url_for('loginView.login_view'))
            else:
                return redirect(url_for('loginView.login_view'))
        except Exception as e:
            print(e)
            return redirect(url_for('loginView.login_view'))
    return wrapper
