
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
from ..services.user_service import UserService
from ..forms import RegisterForm, AdminApproveForm, UserManagementForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    from ..forms import LoginForm
    form = LoginForm()
    current_app.logger.debug(f"登录表单验证状态: {form.validate_on_submit()}")
    current_app.logger.debug(f"表单错误: {form.errors}")
    
    if form.validate_on_submit():
        current_app.logger.debug("表单验证通过")
        user = UserService.get_user_by_username(form.username.data)
        current_app.logger.debug(f"找到用户: {user is not None}")
        
        if user and user.check_password(form.password.data):
            current_app.logger.debug("密码验证通过")
            if user.status != 'approved':
                current_app.logger.warning(f"用户未审核: {user.username}")
                flash('您的账号尚未通过审核', 'warning')
                return redirect(url_for('auth.login'))
            
            current_app.logger.info(f"用户登录成功: {user.username}")
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.home'))
        
        if not user:
            current_app.logger.warning(f"用户名不存在: {form.username.data}")
            flash('用户名不存在', 'danger')
        else:
            current_app.logger.warning(f"密码错误: {form.username.data}")
            flash('密码错误', 'danger')
    
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            UserService.create_user(
                password=form.password.data,
                username=form.username.data,
                is_admin=form.is_admin.data,
                status='pending'
            )
            flash('注册成功，请等待管理员审核', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(f'注册失败: {str(e)}', 'danger')
            current_app.logger.error(f"用户注册失败: {str(e)}")
        except Exception as e:
            flash(f'注册过程中发生错误: {str(e)}', 'danger')
            current_app.logger.error(f"用户注册异常: {str(e)}")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}错误: {error}", 'danger')
    return render_template('register.html', form=form)

@bp.route('/admin/approvals', methods=['GET', 'POST'])
@login_required
def admin_approvals():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    pending_users = UserService.get_pending_users()
    form = AdminApproveForm()
    
    if form.validate_on_submit():
        user_id = request.form.get('user_id')
        if form.action.data == 'approve':
            if UserService.approve_user(user_id, current_user.id):
                flash(f'已批准用户 {user_id}', 'success')
            else:
                flash('审批失败: 用户不存在', 'danger')
        else:
            if UserService.reject_user(user_id):
                flash(f'已拒绝用户 {user_id}', 'warning')
            else:
                flash('拒绝失败: 用户不存在', 'danger')
        return redirect(url_for('auth.admin_approvals'))
    
    return render_template('admin_approvals.html', users=pending_users, form=form)

@bp.route('/admin/users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    users = UserService.get_all_users()
    form = UserManagementForm()
    
    if form.validate_on_submit():
        user_id = request.form.get('user_id')
        if form.action.data == 'promote':
            if UserService.update_user_role(user_id, True):
                flash(f'已提升用户 {user_id} 为管理员', 'success')
            else:
                flash('提升失败: 用户不存在', 'danger')
        elif form.action.data == 'demote':
            if UserService.update_user_role(user_id, False):
                flash(f'已降级用户 {user_id} 为普通用户', 'warning')
            else:
                flash('降级失败: 用户不存在', 'danger')
        else:
            if UserService.delete_user(user_id):
                flash(f'已删除用户 {user_id}', 'danger')
            else:
                flash('删除失败: 用户不存在', 'danger')
        return redirect(url_for('auth.manage_users'))
    
    return render_template('manage_users.html', users=users, form=form)
