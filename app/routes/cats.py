
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from ..services.cat_service import CatService
from ..forms import CatForm

bp = Blueprint('cats', __name__, url_prefix='/cat')

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

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    form = CatForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        
        CatService.create_cat(
            name=form.name.data,
            description=form.description.data,
            image=filename
        )
        return redirect(url_for('main.home'))
    return render_template('upload.html', form=form)

@bp.route('/edit/<int:cat_id>', methods=['GET', 'POST'])
@login_required
def edit(cat_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    cat = CatService.get_cat(cat_id)
    if not cat:
        return redirect(url_for('main.home'))
    
    form = CatForm(obj=cat)
    if form.validate_on_submit():
        update_data = {
            'name': form.name.data,
            'description': form.description.data
        }
        
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            update_data['image'] = filename
        
        CatService.update_cat(cat_id, **update_data)
        return redirect(url_for('cats.detail', cat_id=cat_id))
    
    return render_template('edit_cat.html', form=form, cat=cat)

@bp.route('/delete/<int:cat_id>', methods=['POST'])
@login_required
def delete(cat_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    CatService.delete_cat(cat_id)
    return redirect(url_for('main.home'))
