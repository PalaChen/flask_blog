from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Email, URL, Length


class NewPostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired()])
    content = TextAreaField('正文', validators=[DataRequired()])
    alias = StringField('别名', validators=[DataRequired()])
    intro = TextAreaField('摘要', validators=[DataRequired()])
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

class SearchForm(FlaskForm):
    category = SelectField('搜索：分类')
    type = SelectField('  类型')
    istop = BooleanField('置顶')
    title = StringField()
    submit = SubmitField('提交')

