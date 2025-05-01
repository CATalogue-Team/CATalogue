
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User

class CatForm(FlaskForm):
    name = StringField('猫咪名字', validators=[DataRequired()])
    description = TextAreaField('描述')
    image = FileField('猫咪图片')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    password_confirm = PasswordField('确认密码', validators=[
        DataRequired(), 
        EqualTo('password', message='两次密码必须一致')
    ])
    is_admin = BooleanField('申请管理员权限')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
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
