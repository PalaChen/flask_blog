from flask import request, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Post, User, Comment, BlogInfo, Tags, Category, Role
from . import manage
from .forms import NewPostForm, TagForm, NewCategoryForm, NewMemberForm, SearchForm

@manage.route('/admin')
@login_required
def admin():
    users = User.query.count()
    posts = Post.query.count()
    categorys = Category.query.count()
    comemnts = Comment.query.count()
    tags = Tags.query.count()
    blog_views = BlogInfo.query.filter_by(id='1').first()
    return render_template('manage/admin.html', users=users, posts=posts, comemnts=comemnts,
                    categorys=categorys, tags=tags, blog_views=blog_views)

# 发布新文章
@manage.route('/admin/new_post', methods=['GET','POST'])
@login_required
def new_post():
    form = NewPostForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]

    type = [(0, '公开'), (1, '草稿'), (2, '审核')]
    form.type.choices = type

    form.author.choices = [(a.id, a.username) for a in User.query.all()]

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        intro = form.intro.data
        alias = form.alias.data
        author_id = form.author.data
        category_id = form.category.data
        # 判断文章类型是否指定选项
        if form.type.data in [0, 1, 2]:
            type_id = form.type.data
        else:
            type_id = 0

        category = Category.query.get(category_id)
        author = User.query.get(author_id)

        if category and author:
            post = Post(title=title, content=content, intro=intro, alias=alias,
                        categoryID=category_id, authorID=author_id, type=type_id)
            db.session.add(post)
            db.session.commit()
            flash('文章发布成功')
            return redirect(url_for('manage.article_manage'))
        else:
            flash('非法数据')

    return render_template('manage/new_post.html', form=form)

# 修改文章
@manage.route('/admin/edit_post?id=<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):
    form = NewPostForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]

    type = [(0, '公开'), (1, '草稿'), (2, '审核')]
    form.type.choices = type

    form.author.choices = [(a.id, a.username) for a in User.query.all()]

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        intro = form.intro.data
        alias = form.alias.data
        author_id = form.author.data
        category_id = form.category.data
        # 判断文章类型是否指定选项
        if form.type.data in [0, 1, 2]:
            type_id = form.type.data
        else:
            type_id = 0

        category = Category.query.get(category_id)
        author = User.query.get(author_id)

        if category and author:
            post = Post(title=title, content=content, intro=intro, alias=alias,
                        categoryID=category_id, authorID=author_id, type=type_id)
            db.session.add(post)
            db.session.commit()
            flash('文章修改成功')
            return redirect(url_for('manage.article_manage'))
        else:
            flash('非法数据')
    return render_template('manage/new_post.html', form=form)

# 删除文章
@manage.route('/admin/delete_post?id=<int:id>', methods=['GET','POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post:
        db.session.delete(post)
        flash(u'文章删除成功')
        return redirect(url_for('manage.article_manage'))
# 标签页
@manage.route('/admin/tags')
@login_required
def tags():
    page = request.args.get('page', 1, type=int)
    if tags is not None:
        pagination = Tags.query.order_by(Tags.order).paginate(
            page, per_page=current_app.config['ADMIN_PER_PAGE'], error_out=False)
        posts = pagination.items
    return render_template('manage/tags.html', posts=posts, pagination=pagination)

# 添加标签
@manage.route('/admin/new_tag', methods=['GET','POST'])
@login_required
def new_tag():
    form = TagForm()
    if form.validate_on_submit():
        tag = Tags(name=form.name.data,
                   alias=form.alias.data,
                   intro=form.intro.data,)
        db.session.add(tag)
        flash(u'添加标签成功')
        return redirect(url_for('manage.tags'))
    return render_template('manage/new_tag.html', form=form)

# 修改标签
@manage.route('/admin/edit_tag?id=<int:id>', methods=['GET','POST'])
@login_required
def edit_tag(id):
    tag = Tags.query.get_or_404(id)
    form = TagForm()
    if form.validate_on_submit():
        tag.name = form.name.data
        tag.alias = form.alias.data
        tag.intro = form.intro.data
        db.session.add(tag)
        flash(u'标签修改成功')
        return redirect(url_for('manage.tags'))
    form.name.data = tag.name
    form.alias.data = tag.alias
    form.intro.data = tag.intro
    return render_template('manage/new_tag.html', form=form)

# 删除标签
@manage.route('/admin/delete_tag?id=<int:id>', methods=['GET','POST'])
@login_required
def delete_tag(id):
    tags = Tags.query.get_or_404(id)
    if tags:
        db.session.delete(tags)
        flash(u'删除标签成功')
        return redirect(url_for('manage.tags'))

# 分类页
@manage.route('/admin/category')
@login_required
def category():
    page = request.args.get('page', 1, type=int)
    if category is not None:
        pagination = Category.query.order_by(Category.order).paginate(
            page, per_page=current_app.config['ADMIN_PER_PAGE'], error_out=False)
        posts = pagination.items
    return render_template('manage/category.html', posts=posts, pagination=pagination)

# 增加分类
@manage.route('/admin/new_category', methods=['GET','POST'])
@login_required
def new_category():
    form = NewCategoryForm()
    # category_name = Category.return_category()
    # form.parent.choices = category_name
    form.order.data = 0
    if form.validate_on_submit():
        category = Category.query.filter_by(name=form.name.data).first()
        if category:
            flash(u'添加分类失败！该分类名称已经存在。')
        else:
            category = Category(name=form.name.data,
                                order=form.order.data,
                                alias=form.alias.data,
                                # rootID=form.parent.data,
                                # parentID=form.parent.data,
                                intro=form.intro.data)
            db.session.add(category)
            flash('添加分类信息成功')
            return redirect(url_for('manage.category'))
    return render_template('manage/new_category.html', form=form)

# 修改分类信息
@manage.route('/admin/edit_category?id=<int:id>', methods=['GET','POST'])
@login_required
def edit_category(id):
    form = NewCategoryForm()
    category = Category.query.get_or_404(id)
    if category:
        if form.validate_on_submit():
            category.name = form.name.data
            category.order = form.order.data
            category.alias = form.alias.data
            category.intro = form.intro.data
            db.session.add(category)
            flash('分类信息修改成功')
            return redirect(url_for("manage.category"))
        form.name.data = category.name
        form.order.data = category.order
        form.alias.data = category.alias
        form.intro.data = category.intro
    return render_template('manage/new_category.html', form=form)

# 删除分类信息
@manage.route('/admin/delete_category?id=<int:id>', methods=['GET','POST'])
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    if category:
        db.session.delete(category)
        flash('分类删除成功')
        return redirect(url_for('manage.category'))

# 用户信息
@manage.route('/admin/member')
@login_required
def member():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id).paginate(
        page, per_page=current_app.config['ADMIN_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('manage/member.html', posts=posts, pagination=pagination)

# 新增用户
@manage.route('/admin/new_member', methods=['GET','POST'])
@login_required
def new_member():
    form = NewMemberForm()
    form.role.choices = [(r.id, r.name) for r in Role.query.all()]

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user:
            flash('存在同名用户，请修改用户名')
            return redirect(url_for('manage.new_member'))

        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('存在相同邮箱，请修改邮箱')
            return redirect(url_for('manage.new_member'))

        role_id = form.role.data
        role = Role.query.get(role_id)
        if role:
            user = User(username=form.name.data,
                        password=form.password.data,
                        confirmed=True,
                        alias=form.alias.data,
                        email=form.email.data,
                        homepage=form.homepage.data,
                        intro=form.intro.data,
                        role_id=role_id)
            db.session.add(user)
            flash('新用户注册成功')
            return redirect(url_for('manage.member'))
        else:
            flash('非法输入信息')
            return redirect(url_for('manage.member'))
    return render_template('manage/new_member.html', form=form)

# 用户修改
@manage.route('/admin/edit_user?id=<int:id>', methods=['GET','POST'])
def edit_user(id):
    form = NewMemberForm()
    user = User.query.get_or_404(id)
    if user:
        form.role.choices = [(r.id, r.name) for r in Role.query.all()]
        if form.validate_on_submit():

            if user.username != form.name.data:
                user = User.query.filter_by(username=form.name.data).first()
                if user:
                    flash('存在同名用户，请修改用户名')
                    return redirect(url_for('manage.new_member'))

            if user.email != form.email.data:
                user = User.query.filter_by(email=form.email.data).first()
                if user:
                    flash('存在相同邮箱，请修改邮箱')
                    return redirect(url_for('manage.new_member'))

            role_id = form.role.data
            role = Role.query.get(role_id)
            if role:
                user.username = form.name.data
                user.password = form.password.data
                user.alias = form.alias.data
                user.email = form.email.data
                user.homepage = form.homepage.data
                user.intro = form.intro.data
                user.role_id = role_id
                db.session.add(user)
                flash('用户资料修改成功')
                return redirect(url_for('manage.member'))
        form.name.data = user.username
        form.alias.data = user.alias
        form.email.data = user.email
        form.homepage.data = user.homepage
        form.intro.data = user.intro
        return render_template('manage/new_member.html', form=form)

# 删除用户
@manage.route('/admin/delete_user?id=<int:id>', methods=['GET','POST'])
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user:
        db.session.delete(user)
        flash('删除用户成功')
        return redirect(url_for('manage.member'))

# 文章管理
@manage.route('/admin/article_manage', methods=['GET', 'POST'])
@login_required
def article_manage():
    form = SearchForm()
    categorys = [(c.id, c.name) for c in Category.query.all()]
    categorys.insert(0,(-1, u'任意'))
    form.category.choices = categorys
    type = [(-1, '任意'), (0, '公开'), (1, '草稿'), (2, '审核')]
    form.type.choices = type

    # if form.validate_on_submit():
    #     from sqlalchemy import or_
    #     post = Post.query.filter(or_(Post.title == form.title.data,
    #                                   Post.categoryID == form.category.data,
    #                                   Post.type == form.type.data)).first()
    #     if post:
    #         page = request.args.get('page', 1, type=int)
    #         pagination = post.query.order_by(post.postTime.desc()).paginate(
    #             page, per_page=current_app.config['ADMIN_PER_PAGE'], error_out=False)
    #         posts = pagination.items

    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.postTime.desc()).paginate(
        page, per_page=current_app.config['ADMIN_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('manage/articles.html', posts=posts, pagination=pagination, form=form)
