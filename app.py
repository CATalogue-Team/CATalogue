# app.py
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cats.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# 数据库模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')

class Cat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    breed = db.Column(db.String(100))
    age = db.Column(db.Integer)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 路由设置
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('登录失败，请检查用户名和密码')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        cats = Cat.query.all()
    else:
        cats = Cat.query.all()
    return render_template('dashboard.html', cats=cats)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        breed = request.form['breed']
        age = request.form['age']
        description = request.form['description']
        image = request.files['image']
        
        if image:
            filename = f"cat_{Cat.query.count()+1}.{image.filename.split('.')[-1]}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        new_cat = Cat(
            breed=breed,
            age=age,
            description=description,
            image=filename,
            owner_id=current_user.id
        )
        db.session.add(new_cat)
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('upload.html')

@app.route('/search')
def search():
    breed = request.args.get('breed', '')
    age = request.args.get('age', '')
    
    query = Cat.query
    if breed:
        query = query.filter(Cat.breed.ilike(f'%{breed}%'))
    if age:
        query = query.filter(Cat.age == age)
    
    cats = query.all()
    return render_template('search.html', cats=cats)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)