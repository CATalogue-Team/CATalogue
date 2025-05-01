
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, PasswordField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange
from app.models import User

class CatForm(FlaskForm):
    name = StringField('猫咪名字', validators=[
        DataRequired(),
        Length(min=2, max=100, message='名字长度需在2-100字符之间')
    ])
    breed = StringField('品种', validators=[
        Length(max=50, message='品种长度不能超过50字符')
    ])
    age = IntegerField('年龄', validators=[
        NumberRange(min=0, max=30, message='年龄需在0-30之间')
    ])
    description = TextAreaField('描述', validators=[
        Length(max=500, message='描述不能超过500字符')
    ])
    image = FileField('猫咪图片')
    is_adopted = BooleanField('已被领养')

    def validate_image(self, field):
        if field.data:
            filename = field.data.filename.lower()
            if not (filename.endswith('.jpg') or filename.endswith('.png')):
                raise ValidationError('仅支持JPG/PNG格式图片')

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

class UserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    is_admin = BooleanField('管理员权限')
