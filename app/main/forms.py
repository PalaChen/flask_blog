from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Email
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField

class SearchForm(FlaskForm):
    body = StringField(validators=[DataRequired()])
    submit = SubmitField('搜索')

class CommentForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    email = StringField('邮箱')
    url = StringField('网址')
    body = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('提交评论')

