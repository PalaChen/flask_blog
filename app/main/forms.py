from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Email
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField

class PostForm(Form):
    title = StringField('标题', validators=[DataRequired()])
    body = PageDownField(validators=[DataRequired()])
    submit = SubmitField('提交')

class CommentForm(Form):
    name = StringField('名称', validators=[DataRequired()])
    email = StringField('邮箱')
    url = StringField('网址')
    body = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('提交评论')

