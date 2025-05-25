
from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash, make_response
from flask.wrappers import Response
from pathlib import Path
from flask_login import login_required, current_user
from .. import limiter, db
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from ..services.cat_service import CatService
from ..services.user_service import UserService
from ..forms import CatForm
from ..decorators import admin_required
from .base_crud import crud_blueprint
from ..models import CatImage, Cat  # 添加CatImage和Cat模型导入

bp, crud_route = crud_blueprint('cats', __name__, url_prefix='/cats')

# 猫咪搜索页
@bp.route('/search')
@login_required
def search() -> Response:
    search_params = {
        'q': request.args.get('q', ''),
        'breed': request.args.get('breed', ''),
        'min_age': request.args.get('min_age', type=int),
        'max_age': request.args.get('max_age', type=int),
        'is_adopted': request.args.get('is_adopted', type=lambda x: x == 'true')
    }
    
    cat_service = CatService(db)
    cats = cat_service.search_cats(
        keyword=search_params['q'],
        breed=search_params['breed'],
        min_age=search_params['min_age'],
        max_age=search_params['max_age'],
        is_adopted=search_params['is_adopted']
    )
    
    return make_response(render_template('search.html', 
                         cats=cats,
                         search_params=search_params))

# 猫咪详情页
@bp.route('/admin/detail/<int:cat_id>')
@login_required
@admin_required
def admin__detail(cat_id: int) -> Response:
    cat_service = CatService(db)
    cat = cat_service.get_cat(cat_id)
    if not cat:
        flash('猫咪不存在', 'error')
        return make_response(redirect(url_for('main.home')))
    return make_response(render_template('cat_detail.html', 
                        cat=cat,
                        is_admin=current_user.is_admin,
                        is_owner=current_user.id == cat.user_id))

# 猫咪管理CRUD
@crud_route('', CatService, CatForm, 'search.html', 'edit_cat.html')
class CatCRUD:
    """猫咪管理CRUD扩展"""
    
    @staticmethod
    def before_create(form) -> dict | None:
        """创建前的处理"""
        if not form.validate():
            return None
            
        return {
            'name': form.name.data,
            'breed': form.breed.data,
            'age': form.age.data,
            'description': form.description.data,
            'is_adopted': form.is_adopted.data,
            'user_id': current_user.id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    
    @staticmethod
    def before_update(item: Cat, form) -> Cat | None:
        """更新前的处理"""
        if not form.validate():
            return None
            
        try:
            # 获取上传的图片文件
            images = []
            if form.images.data:
                try:
                    # 尝试迭代处理，适用于MultipleFileField返回的任何可迭代对象
                    images = [f for f in form.images.data if hasattr(f, 'filename')]
                except TypeError:
                    # 如果不可迭代，则作为单个文件处理
                    if hasattr(form.images.data, 'filename'):
                        images = [form.images.data]
        
            # 直接调用Service层更新
            update_data = {
                'images': images,
                'name': form.name.data,
                'breed': form.breed.data,
                'age': form.age.data,
                'description': form.description.data,
                'is_adopted': form.is_adopted.data
            }
            cat_service = CatService(db)
            return cat_service.update_cat(item.id, **update_data)
        except Exception as e:
            current_app.logger.error(f"更新猫咪失败: {str(e)}")
            flash('更新猫咪信息失败', 'error')
            return None
    
    @staticmethod 
    def before_delete(item: Cat) -> bool:
        """删除前的处理"""
        try:
            # 删除关联图片
            for image in item.images:  # type: ignore
                static_folder = str(current_app.static_folder)
                image_path = Path(static_folder) / image.url.lstrip('/static/')
                if image_path.exists():
                    image_path.unlink()
                    current_app.logger.info(f"已删除图片文件: {image_path}")
            
            # 删除上传目录中的文件
            upload_folder = current_app.config['UPLOAD_FOLDER']
            for filename in os.listdir(upload_folder):
                if filename.startswith(f"cat_{item.id}_"):
                    file_path = os.path.join(upload_folder, filename)
                    os.remove(file_path)
                    current_app.logger.info(f"已删除上传文件: {file_path}")
            
            return True
        except Exception as e:
            current_app.logger.error(f"删除猫咪资源失败: {str(e)}")
            raise

# 添加图片管理路由
    @bp.route('/admin/upload_image/<int:cat_id>', methods=['POST'])
    @login_required
    @admin_required
    @limiter.limit("5 per minute")
    def admin__upload_image(cat_id: int) -> Response:  # type: ignore
        """上传猫咪图片"""
        cat_service = CatService(db)
        cat = cat_service.get_cat(cat_id)
        if not cat:
            flash('猫咪不存在', 'error')
            return make_response(redirect(url_for('cats.admin__list')))
            
        # 处理图片上传
        image = request.files.get('image')
        if not image or not image.filename:
            flash('请选择有效的图片文件', 'error')
            return make_response(redirect(url_for('cats.admin__edit', id=cat_id)))
            
        try:
            # 保存图片
            filename = secure_filename(f"cat_{cat_id}_{image.filename}")
            upload_folder = current_app.config['UPLOAD_FOLDER']
            image.save(os.path.join(upload_folder, filename))
            
            # 创建图片记录
            cat_image = CatImage(
                url=f"/static/uploads/{filename}",
                cat_id=cat_id,
                is_primary=False,
                created_at=datetime.utcnow()
            )
            db.session.add(cat_image)
            db.session.commit()
            flash('图片上传成功', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"上传图片失败: {str(e)}")
            flash('图片上传失败', 'error')
            
        return make_response(redirect(url_for('cats.admin__edit', id=cat_id)))
# 权限控制
from functools import wraps

def add_login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        return login_required(view_func)(*args, **kwargs)
    return wrapped_view

def add_admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        return admin_required(login_required(view_func))(*args, **kwargs)
    return wrapped_view

for endpoint, view_func in bp.view_functions.items():
    if endpoint != 'detail':  # 详情页不需要admin权限
        bp.view_functions[endpoint] = add_admin_required(view_func)
    else:
        bp.view_functions[endpoint] = add_login_required(view_func)
