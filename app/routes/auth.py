
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .. import db, limiter
from ..services.user_service import UserService
from ..forms import RegisterForm, LoginForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    form = LoginForm()
    
    # 页面请求处理
    if form.validate_on_submit():
        if not form.username.data or not form.password.data:
            flash('请输入用户名和密码', 'danger')
            return redirect(url_for('auth.login'))
            
        user = UserService.get_user_by_username(form.username.data)
        
        if user and user.check_password(form.password.data):
            if user.status != 'approved':
                flash('您的账号尚未通过审核', 'warning')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        
        flash('用户名或密码错误', 'danger')
    
    return render_template('login.html', form=form)

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            if not form.password.data:
                raise ValueError('密码不能为空')
            UserService(db).create_user(
                password=str(form.password.data),
                username=form.username.data,
                is_admin=False,
                status='pending'
            )
            flash('注册成功，请等待管理员审核', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(f'注册失败: {str(e)}', 'danger')
        except Exception as e:
            current_app.logger.error(f"用户注册异常: {str(e)}")
            flash('注册失败，请稍后再试', 'danger')
    
    form = RegisterForm()
    return render_template('register.html', form=form)
