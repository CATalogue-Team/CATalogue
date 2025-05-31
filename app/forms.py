
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, PasswordField, BooleanField, SelectField, IntegerField, MultipleFileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange, Optional
from app.models import User

class CatForm(FlaskForm):
    name = StringField('猫咪名字', validators=[
        DataRequired(message='猫咪名字是必填项'),
        Length(min=2, max=100, message='名字长度需在2-100字符之间')
    ])
    breed = StringField('品种', validators=[
        Length(max=50, message='品种长度不能超过50字符'),
        Optional()
    ])
    age = IntegerField('年龄', validators=[
        DataRequired(message='年龄是必填项'),
        NumberRange(min=0, max=30, message='年龄需在0-30之间的正整数')
    ])
    description = TextAreaField('描述', validators=[
        Length(max=500, message='描述不能超过500字符'),
        Optional()
    ])
    images = MultipleFileField('猫咪图片(可多选)', validators=[
        Optional()
    ])
    is_adopted = BooleanField('已被领养', validators=[
        Optional()
    ])

    def validate_images(self, field):
        if field.data:
            for image in field.data:
                if not image:
                    continue
                filename = image.filename.lower()
                if not (filename.endswith('.jpg') or filename.endswith('.png')):
                    raise ValidationError('仅支持JPG/PNG格式图片')
                if image.content_length > 5 * 1024 * 1024:  # 5MB限制
                    raise ValidationError('单张图片大小不能超过5MB')

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
        from app.extensions import db
        user = db.session.query(User).filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用')

class AdminApproveForm(FlaskForm):
    action = SelectField('操作', choices=[
        ('approve', '批准'),
        ('reject', '拒绝')
    ], validators=[DataRequired()])

class UserManagementForm(FlaskForm):
    action = SelectField('操作', choices=[
        ('promote', '提升为管理员'),
        ('demote', '降级为普通用户'),
        ('delete', '删除账号')
    ], validators=[DataRequired()])

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
        from flask import g
        from app.extensions import db
        user = db.session.query(User).filter_by(username=field.data).first()
        # 如果是编辑现有用户，跳过自身检查
        if hasattr(g, 'current_user') and user:
            if user.id != g.current_user.id:
                raise ValidationError('该用户名已被使用')
        elif user:  # 新建用户
            raise ValidationError('该用户名已被使用')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')
