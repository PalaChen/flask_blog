from flask_wtf import Form
from wtforms import SubmitField, StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Email, Regexp, Length
from wtforms.validators import ValidationError
from app.models import User

class LoginForm(Form):
    name = StringField('账号', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')


class RegisterForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(4, 32)])
    username = StringField('用户名', validators=[DataRequired(), Length(4, 16)])
    password = PasswordField('密码', validators=[DataRequired(), Length(7, 16), EqualTo('password2', '密码不一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired(), Length(7, 16)])
    submit = SubmitField('注册')


    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

class ChangePasswordForm(Form):
    old_password = StringField('旧密码', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired(), Length(7, 16), EqualTo('password2', '密码不一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired(), Length(7, 16)])
    submit = SubmitField('提交')

class PasswordResetRequestForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    submit = SubmitField('提交')

class PasswordResetForm(Form):
    email = StringField('邮箱', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired(), Length(7, 16), EqualTo('password2', '密码不一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired(), Length(7, 16)])
    submit = SubmitField('提交')