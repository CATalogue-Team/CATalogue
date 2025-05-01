
from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from ..services.cat_service import CatService
from ..services.user_service import UserService
from ..forms import CatForm
from ..decorators import admin_required
from .base_crud import crud_blueprint

bp, crud_route = crud_blueprint('cats', __name__, url_prefix='/cat')

# 猫咪详情页
@bp.route('/<int:cat_id>')
@login_required
def detail(cat_id):
    cat = CatService.get_cat(cat_id)
    if not cat:
        flash('猫咪不存在', 'error')
        return redirect(url_for('main.home'))
    return render_template('cat_detail.html', 
                        cat=cat,
                        is_admin=current_user.is_admin,
                        is_owner=current_user.id == cat.user_id)

# 猫咪管理CRUD
@crud_route('', CatService, CatForm, 'search.html', 'edit_cat.html')
class CatCRUD:
    """猫咪管理CRUD扩展"""
    
    @staticmethod
    def before_create(form):
        """创建前的处理"""
        if not form.validate():
            return None
            
        # 处理图片上传
        image_url = CatCRUD.handle_image(form)
        
        return {
            'name': form.name.data,
            'breed': form.breed.data,
            'age': form.age.data,
            'description': form.description.data,
            'image_url': image_url,
            'user_id': current_user.id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    
    @staticmethod
    def before_update(item, form):
        """更新前的处理"""
        if not form.validate():
            return None
            
        # 处理图片更新
        image_url = CatCRUD.handle_image(form, item)
        
        return {
            'name': form.name.data,
            'breed': form.breed.data,
            'age': form.age.data,
            'description': form.description.data,
            'image_url': image_url,
            'updated_at': datetime.utcnow()
        }
    
    @staticmethod
    def handle_image(form, item=None):
        """处理图片上传"""
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(save_path)
            return f'/static/uploads/{filename}'
        return item.image_url if item else None
    
    @staticmethod
    def before_delete(item):
        """删除前的处理"""
        if item.image_url:
            image_path = os.path.join(current_app.static_folder, item.image_url.lstrip('/static/'))
            if os.path.exists(image_path):
                os.remove(image_path)
        return True

# 权限控制
for endpoint in bp.view_functions:
    if endpoint != 'detail':  # 详情页不需要admin权限
        bp.view_functions[endpoint] = login_required(admin_required(bp.view_functions[endpoint]))
    else:
        bp.view_functions[endpoint] = login_required(bp.view_functions[endpoint])
