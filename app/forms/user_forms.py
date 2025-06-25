from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User
from flask import g
from app.extensions import db

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[
        DataRequired(),
        Length(min=6, max=128, message='密码长度需在6-128位之间')
    ])
    password_confirm = PasswordField('确认密码', validators=[
        DataRequired(), 
        EqualTo('password', message='两次密码必须一致')
    ])
    is_admin = BooleanField('申请管理员权限')

    def validate_username(self, username):
        user = db.session.query(User).filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')

class UserForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(message='用户名是必填项'),
        Length(min=3, max=50, message='用户名长度需在3-50字符之间')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码是必填项'),
        Length(min=6, max=128, message='密码长度需在6-128位之间')
    ])
    password_confirm = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次密码必须一致')
    ])
    is_admin = BooleanField('管理员权限')

    def validate_username(self, field):
        user = db.session.query(User).filter_by(username=field.data).first()
        if hasattr(g, 'current_user') and user:
            if user.id != g.current_user.id:
                raise ValidationError('该用户名已被使用')
        elif user:
            raise ValidationError('该用户名已被使用')

class UserManagementForm(FlaskForm):
    action = SelectField('操作', choices=[
        ('promote', '提升为管理员'),
        ('demote', '降级为普通用户'),
        ('delete', '删除账号')
    ], validators=[DataRequired()])
