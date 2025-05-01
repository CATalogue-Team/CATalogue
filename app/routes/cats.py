
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .. import db
from ..models import Cat
from ..forms import CatForm

bp = Blueprint('cats', __name__, url_prefix='/cat')

@bp.route('/<int:cat_id>')
@login_required
def detail(cat_id):
    cat = Cat.query.get(cat_id)
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
        
        new_cat = Cat(
            name=form.name.data,
            description=form.description.data,
            image=filename
        )
        db.session.add(new_cat)
        db.session.commit()
        return redirect(url_for('main.home'))
    return render_template('upload.html', form=form)
