
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from functools import wraps

def crud_blueprint(name, import_name, template_folder=None, url_prefix=None):
    """创建基础CRUD蓝图工厂"""
    bp = Blueprint(name, import_name, template_folder=template_folder, url_prefix=url_prefix)
    
    def crud_route(model_name, service, form_class, list_template, edit_template):
        """装饰器：为CRUD操作添加路由"""
        def decorator(cls):
            # 列表路由
            @bp.route(f'/{model_name}', endpoint=f'{model_name}_list')
            @login_required
            def list():
                items = service.get_all_users() if model_name == 'users' else service.get_all_cats()
                return render_template(list_template, items=items)
            
            # 创建路由
            @bp.route(f'/{model_name}/create', methods=['GET', 'POST'], endpoint=f'{model_name}_create')
            @login_required
            def create():
                form = form_class()
                if form.validate_on_submit():
                    service.create_user(**form.data) if model_name == 'users' else service.create_cat(**form.data)
                    return redirect(url_for(f'{name}.{model_name}_list'))
                return render_template(edit_template, form=form)
            
            # 编辑路由
            @bp.route(f'/{model_name}/edit/<int:id>', methods=['GET', 'POST'], endpoint=f'{model_name}_edit')
            @login_required
            def edit(id):
                item = service.get_user(id) if model_name == 'users' else service.get_cat(id)
                if not item:
                    return redirect(url_for(f'{name}.{model_name}_list'))
                
                form = form_class(obj=item)
                if form.validate_on_submit():
                    service.update_user(id, **form.data) if model_name == 'users' else service.update_cat(id, **form.data)
                    return redirect(url_for(f'{name}.{model_name}_list'))
                return render_template(edit_template, form=form, item=item)
            
            # 删除路由
            @bp.route(f'/{model_name}/delete/<int:id>', methods=['POST'], endpoint=f'{model_name}_delete')
            @login_required
            def delete(id):
                service.delete_user(id) if model_name == 'users' else service.delete_cat(id)
                return redirect(url_for(f'{name}.{model_name}_list'))
            
            return cls
        return decorator
    
    return bp, crud_route
