
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField
from wtforms.validators import DataRequired

class CatForm(FlaskForm):
    name = StringField('猫咪名字', validators=[DataRequired()])
    description = TextAreaField('描述')
    image = FileField('猫咪图片')
