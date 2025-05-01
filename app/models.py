
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Cat(db.Model):
    __tablename__ = 'cats'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class User(UserMixin):
    def __init__(self, id, username, password, is_admin=False):
        self.id = id
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.is_admin = is_admin

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 示例用户数据
users = {
    1: User(1, 'admin', 'adminpassword', True),
    2: User(2, 'user1', 'user1password')
}
