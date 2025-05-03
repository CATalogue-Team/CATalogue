
from flask import Blueprint, render_template, redirect, url_for, request, current_app
from flask_login import login_required
from functools import wraps

def crud_blueprint(name, import_name, template_folder=None, url_prefix=None):
    """创建基础CRUD蓝图工厂"""
    bp = Blueprint(name, import_name, template_folder=template_folder, url_prefix=url_prefix)
    
    def crud_route(model_name, service, form_class, list_template, edit_template):
        """装饰器：为CRUD操作添加路由"""
        def decorator(cls):
            # 列表路由
            @bp.route(f'/{model_name}', endpoint=f'admin_{model_name}_list')
            @login_required
            def list():
                page = request.args.get('page', 1, type=int)
                per_page = current_app.config.get('ITEMS_PER_PAGE', 10)
                cats = service.get_paginated_cats(page=page, per_page=per_page) if model_name == 'cats' else service.get_paginated(page=page, per_page=per_page)
                return render_template(list_template, cats=cats)
            
            # 创建路由
            @bp.route(f'/{model_name}/create', methods=['GET', 'POST'], endpoint=f'admin_{model_name}_create')
            @login_required
            def create():
                form = form_class()
                if form.validate_on_submit():
                    try:
                        # 处理图片上传
                        image_url = None
                        if hasattr(cls, 'handle_image'):
                            image_url = cls.handle_image(form)
                        
                        # 创建记录
                        data = {k:v for k,v in form.data.items() if k not in ['csrf_token', 'submit', 'image']}
                        if image_url:
                            data['image_url'] = image_url
                        if hasattr(service, 'create_cat'):
                            from flask_login import current_user
                            service.create_cat(current_user.id, **data)
                        elif hasattr(service, 'model'):
                            service.create(service.model, **data)
                        else:
                            service.create(**data)
                        
                        from flask import flash
                        flash(f'{model_name.capitalize()}添加成功!', 'success')
                        from flask_login import current_user
                        if hasattr(current_user, 'is_admin') and current_user.is_admin:
                            return redirect(url_for('admin.cats'))
                        return redirect(url_for(f'admin_{model_name}_list'))
                    except Exception as e:
                        current_app.logger.error(f'创建{model_name}失败: {str(e)}', exc_info=True)
                        from flask import flash
                        flash(f'添加失败: {str(e)}', 'danger')
                elif request.method == 'POST':
                    current_app.logger.warning(f'表单验证失败: {form.errors}')
                    from flask import flash
                    for field, errors in form.errors.items():
                        for error in errors:
                            flash(f'{getattr(form, field).label.text}: {error}', 'danger')
                return render_template(edit_template, form=form)
            
            # 编辑路由
            @bp.route(f'/{model_name}/edit/<int:id>', methods=['GET', 'POST'], endpoint=f'admin_{model_name}_edit')
            @login_required
            def edit(id):
                item = service.get(id)
                if not item:
                    from flask import flash
                    flash('记录不存在', 'danger')
                    return redirect(url_for(f'admin_{model_name}_list'))
                
                form = form_class(obj=item)
                if form.validate_on_submit():
                    try:
                        service.update(id, **form.data)
                        from flask import flash
                        flash(f'{model_name.capitalize()}更新成功!', 'success')
                        return redirect(url_for(f'admin_{model_name}_list'))
                    except Exception as e:
                        current_app.logger.error(f'更新{model_name}失败: {str(e)}', exc_info=True)
                        from flask import flash
                        flash(f'更新失败: {str(e)}', 'danger')
                elif request.method == 'POST':
                    current_app.logger.warning(f'表单验证失败: {form.errors}')
                    from flask import flash
                    for field, errors in form.errors.items():
                        for error in errors:
                            flash(f'{getattr(form, field).label.text}: {error}', 'danger')
                return render_template(edit_template, form=form, item=item)
            
            # 删除路由
            @bp.route(f'/{model_name}/delete/<int:id>', methods=['POST'], endpoint=f'admin_{model_name}_delete')
            @login_required
            def delete(id):
                service.delete(id)
                return redirect(url_for(f'admin_{model_name}_list'))
            
            return cls
        return decorator
    
    return bp, crud_route
