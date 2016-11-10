from flask import render_template, redirect, request, current_app, request, flash, \
    url_for
from app import db
from app.main import main
from app.models import Post, User, Comment, BlogInfo
from .forms import PostForm, CommentForm

@main.route('/')
def index():
    BlogInfo.add_view(db)
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.postTime.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)

@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    BlogInfo.add_view(db)
    post = Post.query.get_or_404(id)
    user = User.query.get_or_404(post.authorID)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(author=form.name.data,
                          email=form.email.data,
                          homePage=form.url.data,
                          content=form.body.data,
                          postID=post.id,
                          ip=request.remote_addr,
                          agent=request.headers.get('User-Agent'))
        db.session.add(comment)
        db.session.commit()
        # 增加评论次数
        post.add_comment(post,db)
        flash(u'评论成功')
        return redirect(url_for('.post', id=post.id, page=1))

    page = request.args.get('page', 1, type=int)
    if page == -1:
        if post.commentNums > 0:
            page = (post.commentNums) / \
                   current_app.config['COMENTS_PER_PAGE'] + 1
    pagination = Comment.query.order_by(Comment.postTime.asc()).paginate(
        page, per_page=current_app.config['COMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    # 增加浏览量
    post.add_view(post, db)

    return render_template('post.html', post=post, user=user, form=form,
                           comments=comments, pagination=pagination)