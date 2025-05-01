
from flask import Blueprint, render_template, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from ..services.cat_service import CatService
from ..forms import CatForm
from ..decorators import admin_required
from .base_crud import crud_blueprint

bp, crud_route = crud_blueprint('cats', __name__, url_prefix='/cat')

# 猫咪详情页（特殊路由，不在CRUD模板中）
@bp.route('/<int:cat_id>')
@login_required
def detail(cat_id):
    cat = CatService.get_cat(cat_id)
    if not cat:
        return redirect(url_for('main.home'))
    return render_template('cat_detail.html', 
                        cat=cat,
                        cat_id=cat_id,
                        is_admin=current_user.is_admin)

# 猫咪管理CRUD
@crud_route('', CatService, CatForm, 'search.html', 'edit_cat.html')
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
        return redirect(url_for('main.home'))
    
    @staticmethod
    def after_update(id, **data):
        """更新后的处理"""
        return redirect(url_for('cats.detail', cat_id=id))

# 应用权限控制
for endpoint in bp.view_functions:
    if endpoint != 'detail':  # 详情页不需要admin权限
        bp.view_functions[endpoint] = login_required(admin_required(bp.view_functions[endpoint]))
    else:
        bp.view_functions[endpoint] = login_required(bp.view_functions[endpoint])
