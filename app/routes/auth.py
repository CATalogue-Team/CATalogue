
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required
from ..models import users

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users.values() if u.username == username), None)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.home'))
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))
