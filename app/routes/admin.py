
from flask import Blueprint, render_template, redirect, url_for, request, current_app
from flask_login import login_required
import os
from werkzeug.utils import secure_filename
from ..services.cat_service import CatService
from ..services.user_service import UserService
from ..forms import CatForm, UserForm
from ..decorators import admin_required
from .base_crud import crud_blueprint

# 创建管理员蓝图（显式设置名称空间）
bp, crud_route = crud_blueprint('admin', __name__, url_prefix='/admin')
bp.name = 'admin'  # 显式设置蓝图名称
bp.static_folder = 'static'  # 单独设置静态文件夹
bp.static_url_path = '/admin/static'  # 单独设置静态URL路径

@bp.route('/', endpoint='admin_home')
@login_required
@admin_required
def admin_home():
    """后台管理首页"""
    return redirect(url_for('admin.admin_users_list'))

# 猫咪管理CRUD
@crud_route('cats', CatService, CatForm, 'admin_cats.html', 'edit_cat.html')
class CatCRUD:
    """猫咪管理CRUD扩展"""
    
    @staticmethod
    def handle_image(form, item=None):
        """处理多图片上传"""
        if form.images.data and any(form.images.data):
            # 直接返回有效的FileStorage对象
            return [img for img in form.images.data if img]
        return []
    
    @staticmethod
    def before_delete(item):
        """删除前的处理"""
        if item.images:
            for image in item.images:
                if os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], image.url)):
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], image.url))

# 用户管理CRUD
@crud_route('users', UserService, UserForm, 'admin_users.html', 'edit_user.html')
class UserCRUD:
    """用户管理CRUD扩展"""
    
    @staticmethod
    def before_update(id, **data):
        """更新前的处理"""
        return {'is_admin': data['is_admin']}  # 只更新is_admin字段
    
    @bp.route('/users/approve/<int:id>', methods=['POST'], endpoint='admin_users_approve')
    @login_required
    @admin_required
    def approve(id):
        """批准用户"""
        from flask import jsonify
        try:
            user = UserService.get(id)
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            
            UserService.update(id, status='approved')
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/users/reject/<int:id>', methods=['POST'], endpoint='admin_users_reject')
    @login_required
    @admin_required
    def reject(id):
        """拒绝用户"""
        from flask import jsonify
        try:
            user = UserService.get(id)
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            
            UserService.update(id, status='rejected')
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# 应用管理员权限装饰器
for endpoint in bp.view_functions:
    bp.view_functions[endpoint] = login_required(admin_required(bp.view_functions[endpoint]))
