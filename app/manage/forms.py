from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Email, URL, Length
from wtforms.validators import ValidationError
from app.models import User

class NewPostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired()])
    content = TextAreaField('正文')
    alias = StringField('别名')
    intro = TextAreaField('摘要')
    tag = StringField('标签')
    category = SelectField('分类', coerce=int)
    type = SelectField('状态', coerce=int)
    author = SelectField('作者', coerce=int)
    submit = SubmitField('提交')

class TagForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    alias = StringField('别名')
    intro = TextAreaField('描述')
    submit = SubmitField('提交')

class NewCategoryForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    alias = StringField('别名')
    order = StringField('排序')
    # parent = SelectField('父分类', validators=[DataRequired(message='项目名称不能为空')])
    intro = TextAreaField('描述')
    submit = SubmitField('提交')


class NewMemberForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired(message='请输入用户名')])
    role = SelectField('用户级别', coerce=int)
    password = PasswordField('密码', validators=[DataRequired(message='请输入密码'), Length(7, 16), EqualTo('password2', '密码不一致')])
    password2 = PasswordField('确认密码', validators=[Length(7, 16)])
    alias = StringField('别名')
    email = StringField('邮箱', validators=[DataRequired(message='请输入邮箱'), Email(message='请填写正确邮箱')])
    homepage = StringField('主页')
    intro = TextAreaField('摘要')
    submit = SubmitField('提交')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')


class SearchForm(FlaskForm):
    category = SelectField('搜索：分类')
    type = SelectField('  类型')
    istop = BooleanField('置顶')
    title = StringField()
    submit = SubmitField('提交')

class SearchComentFrom(FlaskForm):
    search = StringField('搜索')
    submit = SubmitField('提交')

class DeleteComentForm(FlaskForm):
    select = BooleanField()
    submit = SubmitField('删除所选项目')