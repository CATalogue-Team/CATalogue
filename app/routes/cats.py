
from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash, make_response, jsonify
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
from ..models import CatImage, Cat

bp = Blueprint('cats', __name__, url_prefix='/cats')

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
@bp.route('/admin/detail/<int:id>')
@login_required
@admin_required
def admin__detail(id: int) -> Response:
    cat_service = CatService(db)
    cat = cat_service.get_cat(id)
    if not cat:
        flash('猫咪不存在', 'error')
        return make_response(redirect(url_for('main.home')))
    return make_response(render_template('cat_detail.html', 
                        cat=cat,
                        is_admin=current_user.is_admin,
                        is_owner=current_user.id == cat.user_id))

# 猫咪管理CRUD路由
@bp.route('', endpoint='admin_cats_list')
@login_required
def cats_list():
    """猫咪列表"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 10)
    items = CatService(db).get_paginated_cats(page=page, per_page=per_page)
    return render_template('search.html', cats=items)

@bp.route('/create', methods=['GET', 'POST'], endpoint='admin_cats_create')
@login_required
def cats_create():
    """创建猫咪"""
    form = CatForm()
    if form.validate_on_submit():
        try:
            data = {
                'name': form.name.data,
                'breed': form.breed.data,
                'age': form.age.data,
                'description': form.description.data,
                'is_adopted': form.is_adopted.data,
                'user_id': current_user.id,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            CatService(db).create_cat(**data)
            flash('猫咪添加成功!', 'success')
            return redirect(url_for('cats.admin_cats_list'))
        except Exception as e:
            current_app.logger.error(f'创建猫咪失败: {str(e)}')
            flash(f'添加失败: {str(e)}', 'danger')
    return render_template('edit_cat.html', form=form)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'], endpoint='admin_cats_edit')
@login_required
def cats_edit(id):
    """编辑猫咪"""
    cat = CatService.get_cat(id)
    if not cat:
        flash('猫咪不存在', 'danger')
        return redirect(url_for('cats.admin_cats_list'))
    
    form = CatForm(obj=cat)
    if form.validate_on_submit():
        try:
            update_data = {
                'name': form.name.data,
                'breed': form.breed.data,
                'age': form.age.data,
                'description': form.description.data,
                'is_adopted': form.is_adopted.data
            }
            CatService(db).update_cat(id, **update_data)
            flash('猫咪更新成功!', 'success')
            return redirect(url_for('cats.admin_cats_list'))
        except Exception as e:
            current_app.logger.error(f'更新猫咪失败: {str(e)}')
            flash(f'更新失败: {str(e)}', 'danger')
    return render_template('edit_cat.html', form=form, cat=cat)

@bp.route('/delete/<int:id>', methods=['POST'], endpoint='admin_cats_delete')
@login_required
def cats_delete(id):
    """删除猫咪"""
    try:
        cat = CatService.get_cat(id)
        if not cat:
            return jsonify({'error': '猫咪不存在'}), 404
            
        # 删除关联图片
        for image in cat.images:
            image_path = Path(str(current_app.static_folder)) / image.url.lstrip('/static/')
            if image_path.exists():
                image_path.unlink()
                
        # 删除记录
        CatService(db).delete_cat(id)
        flash('猫咪删除成功!', 'success')
        return redirect(url_for('cats.admin_cats_list'))
    except Exception as e:
        current_app.logger.error(f'删除猫咪失败: {str(e)}')
        return jsonify({'error': str(e)}), 500

# 添加图片管理路由
@bp.route('/admin/upload_image/<int:id>', methods=['POST'])
@login_required
@admin_required
@limiter.limit("5 per minute")
def admin__upload_image(id: int) -> Response:  # type: ignore
    """上传猫咪图片"""
    cat_service = CatService(db)
    cat = cat_service.get_cat(id)
    if not cat:
        flash('猫咪不存在', 'error')
        return make_response(redirect(url_for('cats.admin_cats_list')))
            
    # 处理图片上传
    image = request.files.get('image')
    if not image or not image.filename:
        flash('请选择有效的图片文件', 'error')
        return make_response(redirect(url_for('cats.admin_cats_edit', id=id)))
            
    try:
        # 保存图片
        filename = secure_filename(f"cat_{id}_{image.filename}")
        upload_folder = current_app.config['UPLOAD_FOLDER']
        image.save(os.path.join(upload_folder, filename))
            
        # 创建图片记录
        cat_image = CatImage(
            url=f"/static/uploads/{filename}",
            cat_id=id,
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
            
    return make_response(redirect(url_for('cats.admin_cats_edit', id=id)))
