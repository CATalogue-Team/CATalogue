
from flask import Blueprint, render_template, redirect, url_for, request, current_app
from flask_login import login_required
import os
from werkzeug.utils import secure_filename
from ..services.cat_service import CatService
from ..services.user_service import UserService
from ..forms import CatForm, UserForm
from ..decorators import admin_required
from .base_crud import crud_blueprint

# 创建管理员蓝图
bp, crud_route = crud_blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@login_required
@admin_required
def admin_home():
    """后台管理首页"""
    return redirect(url_for('admin.users'))

# 猫咪管理CRUD
@crud_route('cats', CatService, CatForm, 'admin_cats.html', 'edit_cat.html')
class CatCRUD:
    """猫咪管理CRUD扩展"""
    
    @staticmethod
    def handle_image(form, item=None):
        """处理图片上传"""
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            return filename
        return item.image if item else None
    
    @staticmethod
    def before_delete(item):
        """删除前的处理"""
        if item.image and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], item.image)):
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], item.image))

# 用户管理CRUD
@crud_route('users', UserService, UserForm, 'admin_users.html', 'edit_user.html')
class UserCRUD:
    """用户管理CRUD扩展"""
    
    @staticmethod
    def before_update(id, **data):
        """更新前的处理"""
        return {'is_admin': data['is_admin']}  # 只更新is_admin字段

# 应用管理员权限装饰器
for endpoint in bp.view_functions:
    bp.view_functions[endpoint] = login_required(admin_required(bp.view_functions[endpoint]))
