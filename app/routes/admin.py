
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
import os
from ..services.cat_service import CatService
from ..forms import CatForm

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/cats')
@login_required
def cats():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    cats = CatService.get_all_cats()
    return render_template('admin_cats.html', cats=cats)

@bp.route('/edit_cat/<int:cat_id>', methods=['GET', 'POST'])
@login_required
def edit_cat(cat_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    cat = CatService.get_cat(cat_id)
    if not cat:
        return redirect(url_for('admin.cats'))
    
    form = CatForm()
    
    if request.method == 'GET':
        form.name.data = cat.name
        form.description.data = cat.description
    
    if form.validate_on_submit():
        update_data = {
            'name': form.name.data,
            'description': form.description.data
        }
        
        if form.image.data:
            if cat.image and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], cat.image)):
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], cat.image))
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            update_data['image'] = filename
        
        CatService.update_cat(cat_id, **update_data)
        return redirect(url_for('admin.cats'))
    
    return render_template('edit_cat.html',
                         form=form,
                         cat_id=cat_id,
                         cat=cat)

@bp.route('/delete_cat/<int:cat_id>', methods=['POST'])
@login_required
def delete_cat(cat_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    cat = CatService.get_cat(cat_id)
    if cat and cat.image and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], cat.image)):
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], cat.image))
    
    CatService.delete_cat(cat_id)
    return redirect(url_for('admin.cats'))
