
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, db
from ..forms import RegisterForm, AdminApproveForm, UserManagementForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if user.status != 'approved':
                flash('您的账号尚未通过审核', 'warning')
                return redirect(url_for('auth.login'))
            login_user(user)
            return redirect(url_for('main.home'))
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            password=form.password.data,
            is_admin=form.is_admin.data
        )
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请等待管理员审核', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@bp.route('/admin/approvals', methods=['GET', 'POST'])
@login_required
def admin_approvals():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    pending_users = User.query.filter_by(status='pending').all()
    form = AdminApproveForm()
    
    if form.validate_on_submit():
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        if form.action.data == 'approve':
            user.status = 'approved'
            user.approved_by = current_user.id
            flash(f'已批准用户 {user.username}', 'success')
        else:
            user.status = 'rejected'
            flash(f'已拒绝用户 {user.username}', 'warning')
        db.session.commit()
        return redirect(url_for('auth.admin_approvals'))
    
    return render_template('admin_approvals.html', users=pending_users, form=form)

@bp.route('/admin/users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    users = User.query.all()
    form = UserManagementForm()
    
    if form.validate_on_submit():
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        if form.action.data == 'promote':
            user.is_admin = True
            flash(f'已提升 {user.username} 为管理员', 'success')
        elif form.action.data == 'demote':
            user.is_admin = False
            flash(f'已降级 {user.username} 为普通用户', 'warning')
        else:
            db.session.delete(user)
            flash(f'已删除用户 {user.username}', 'danger')
        db.session.commit()
        return redirect(url_for('auth.manage_users'))
    
    return render_template('manage_users.html', users=users, form=form)
