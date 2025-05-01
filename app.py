
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from auth import User, users

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

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

# 临时猫咪数据存储
cats = []

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    form = CatForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = None
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cats.append({
            'name': form.name.data,
            'description': form.description.data,
            'image': filename
        })
        return redirect(url_for('home'))
    return render_template('upload.html', form=form)

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '').lower()
    if query:
        filtered_cats = [
            cat for cat in cats 
            if any(query in str(field).lower() for field in [cat['name'], cat['description']])
        ]
        return render_template('search.html', 
                            cats=filtered_cats,
                            no_results=len(filtered_cats) == 0)
    
    # 未查询时推荐最近添加的3只猫咪
    recommended_cats = cats[-3:] if len(cats) > 3 else cats
    return render_template('search.html', 
                         cats=recommended_cats if recommended_cats else None,
                         is_recommendation=bool(recommended_cats))

@app.route('/admin/cats')
@login_required
def admin_cats():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    return render_template('admin_cats.html', cats=cats)

@app.route('/admin/edit_cat/<int:cat_id>', methods=['GET', 'POST'])
@login_required
def edit_cat(cat_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    # 确保cat_id在有效范围内
    if cat_id < 0 or cat_id >= len(cats):
        return redirect(url_for('admin_cats'))
    
    cat = cats[cat_id]
    form = CatForm()
    
    # 初始化表单数据
    if request.method == 'GET':
        form.name.data = cat['name']
        form.description.data = cat['description']
    
    if form.validate_on_submit():
        # 更新猫咪信息
        cat['name'] = form.name.data
        cat['description'] = form.description.data
        
        # 处理图片更新
        if form.image.data:
            # 删除旧图片(如果存在且不是默认图片)
            if cat['image'] and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], cat['image'])):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], cat['image']))
            # 保存新图片
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cat['image'] = filename
        
        return redirect(url_for('admin_cats'))
    
    return render_template('edit_cat.html',
                         form=form,
                         cat_id=cat_id,
                         cat=cat)

if __name__ == '__main__':
    app.run(debug=True)
