
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from auth import User, users
import sqlite3
from contextlib import closing

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['DATABASE'] = 'cats.db'

def init_db():
    with closing(sqlite3.connect(app.config['DATABASE'])) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users.values() if u.username == username), None)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os

app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class CatForm(FlaskForm):
    name = StringField('猫咪名字', validators=[DataRequired()])
    description = TextAreaField('描述')
    image = FileField('猫咪图片')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    form = CatForm()
    if form.validate_on_submit():
        db = get_db()
        image = form.image.data
        filename = None
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        db.execute(
            'INSERT INTO cats (name, description, image) VALUES (?, ?, ?)',
            [form.name.data, form.description.data, filename]
        )
        db.commit()
        db.close()
        return redirect(url_for('home'))
    return render_template('upload.html', form=form)

@app.route('/search')
@login_required
def search():
    db = get_db()
    query = request.args.get('q', '').lower()
    
    if query:
        cats = db.execute(
            'SELECT * FROM cats WHERE LOWER(name) LIKE ? OR LOWER(description) LIKE ?',
            [f'%{query}%', f'%{query}%']
        ).fetchall()
        no_results = len(cats) == 0
    else:
        # 未查询时推荐最近添加的3只猫咪
        cats = db.execute(
            'SELECT * FROM cats ORDER BY created_at DESC LIMIT 3'
        ).fetchall()
        no_results = False
        is_recommendation = bool(cats)
    
    db.close()
    return render_template('search.html',
                        cats=cats,
                        no_results=no_results,
                        is_recommendation=is_recommendation if not query else None)

@app.route('/cat/<int:cat_id>')
@login_required
def cat_detail(cat_id):
    db = get_db()
    cat = db.execute(
        'SELECT * FROM cats WHERE id = ?', 
        [cat_id]
    ).fetchone()
    db.close()
    
    if not cat:
        return redirect(url_for('home'))
    return render_template('cat_detail.html', 
                        cat=cat,
                        cat_id=cat_id,
                        is_admin=current_user.is_admin)

@app.route('/admin/cats')
@login_required
def admin_cats():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    db = get_db()
    cats = db.execute('SELECT * FROM cats ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('admin_cats.html', cats=cats)

@app.route('/admin/edit_cat/<int:cat_id>', methods=['GET', 'POST'])
@login_required
def edit_cat(cat_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    db = get_db()
    cat = db.execute(
        'SELECT * FROM cats WHERE id = ?', 
        [cat_id]
    ).fetchone()
    
    if not cat:
        db.close()
        return redirect(url_for('admin_cats'))
    
    form = CatForm()
    
    # 初始化表单数据
    if request.method == 'GET':
        form.name.data = cat['name']
        form.description.data = cat['description']
    
    if form.validate_on_submit():
        # 处理图片更新
        filename = cat['image']
        if form.image.data:
            # 删除旧图片(如果存在且不是默认图片)
            if cat['image'] and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], cat['image'])):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], cat['image']))
            # 保存新图片
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # 更新猫咪信息
        db.execute(
            'UPDATE cats SET name = ?, description = ?, image = ? WHERE id = ?',
            [form.name.data, form.description.data, filename, cat_id]
        )
        db.commit()
        db.close()
        return redirect(url_for('admin_cats'))
    
    db.close()
    return render_template('edit_cat.html',
                         form=form,
                         cat_id=cat_id,
                         cat=cat)

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
