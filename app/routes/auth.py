
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .. import db, limiter
from ..services.user_service import UserService
from ..forms import RegisterForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    from ..forms import LoginForm
    form = LoginForm()
    
    # API请求处理
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Invalid credentials'}), 401
            
        user = UserService.get_user_by_username(data['username'])
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
            
        if user.status != 'approved':
            return jsonify({'error': 'Account not approved'}), 403
            
        login_user(user)
        return jsonify({'message': 'Login successful'}), 200
    
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
    if request.is_json:
        return jsonify({'message': 'Logout successful'}), 200
    return '', 200

@bp.route('/register', methods=['GET', 'POST'])
def register():
    from flask import jsonify
    
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request'}), 400
            
        try:
            user = UserService.create_user(
                password=data.get('password'),
                username=data.get('username'),
                is_admin=data.get('is_admin', False),
                status='pending'
            )
            return jsonify({
                'message': 'Registration successful',
                'user_id': user.id
            }), 201
        except ValueError as e:
            current_app.logger.error(f"用户注册失败: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"用户注册异常: {str(e)}")
            return jsonify({'error': 'Registration failed'}), 500
    
    # GET请求返回注册页面
    form = RegisterForm()
    return render_template('register.html', form=form)
