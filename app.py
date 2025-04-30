
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
    return render_template('search.html', cats=cats)

if __name__ == '__main__':
    app.run(debug=True)
