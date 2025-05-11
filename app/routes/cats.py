
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

# 猫咪搜索页
@bp.route('/search')
@login_required
def search():
    search_params = {
        'q': request.args.get('q', ''),
        'breed': request.args.get('breed', ''),
        'min_age': request.args.get('min_age', type=int),
        'max_age': request.args.get('max_age', type=int),
        'is_adopted': request.args.get('is_adopted', type=lambda x: x == 'true')
    }
    
    cats = CatService.search_cats(
        keyword=search_params['q'],
        breed=search_params['breed'],
        min_age=search_params['min_age'],
        max_age=search_params['max_age'],
        is_adopted=search_params['is_adopted']
    )
    
    return render_template('search.html', 
                         cats=cats,
                         search_params=search_params)

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
    def before_update(item, form):
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
            return CatService.update_cat(
                item.id,
                images=images,
                name=form.name.data,
                breed=form.breed.data,
                age=form.age.data,
                description=form.description.data,
                is_adopted=form.is_adopted.data
            )
        except Exception as e:
            current_app.logger.error(f"更新猫咪失败: {str(e)}")
            flash('更新猫咪信息失败', 'error')
            return None
    
    @staticmethod
    def before_delete(item):
        """删除前的处理"""
        try:
            # 删除关联图片
            for image in item.images:
                image_path = os.path.join(current_app.static_folder, image.url.lstrip('/static/'))
                if os.path.exists(image_path):
                    os.remove(image_path)
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
@bp.route('/<int:cat_id>/images', methods=['POST'])
@login_required
@admin_required
def manage_images(cat_id):
    """管理猫咪图片"""
    cat = CatService.get(cat_id)
    if not cat:
        flash('猫咪不存在', 'error')
        return redirect(url_for('cats.admin__list'))
    
    action = request.form.get('action')
    image_id = request.form.get('image_id')
    
    if action == 'set_primary' and image_id:
        # 设置主图
        try:
            image_id = int(image_id)
            # 重置所有图片为非主图
            for img in cat.images:
                img.is_primary = (img.id == image_id)
            db.session.commit()
            flash('主图设置成功', 'success')
        except (ValueError, AttributeError):
            flash('设置主图失败', 'error')
            
    elif action == 'delete' and image_id:
        # 删除图片
        try:
            image_id = int(image_id)
            image = next((img for img in cat.images if img.id == image_id), None)
            if image:
                # 删除文件
                image_path = os.path.join(current_app.static_folder, image.url.lstrip('/static/'))
                if os.path.exists(image_path):
                    os.remove(image_path)
                # 删除记录
                db.session.delete(image)
                db.session.commit()
                flash('图片删除成功', 'success')
        except (ValueError, AttributeError):
            flash('删除图片失败', 'error')
    
        return redirect(url_for('cats.admin__edit', id=cat_id))

# 权限控制
for endpoint in bp.view_functions:
    if endpoint != 'detail':  # 详情页不需要admin权限
        bp.view_functions[endpoint] = login_required(admin_required(bp.view_functions[endpoint]))
    else:
        bp.view_functions[endpoint] = login_required(bp.view_functions[endpoint])
