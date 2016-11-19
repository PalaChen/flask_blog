import bleach
from datetime import datetime
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
from app import db, login_manager
import bleach

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.BOOLEAN, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')



    @staticmethod
    def insert_roles():
        roles = {
            '用户': (Permission.FOLLOW |
                     Permission.COMMENT, True),
            '协管员': (Permission.WRITE_ARTICLES |
                       Permission.MODERATE_COMMENTS, False),
            '管理员': (0x80, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

# 用户表
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    member_ip = db.Column(db.String(40))
    last_ip = db.Column(db.String(40))
    # 发布文章数量
    articles = db.Column(db.Integer, default=0)
    # 发布评论数量
    comments = db.Column(db.Integer, default=0)
    uploads = db.Column(db.Integer, default=0)
    homepage = db.Column(db.String(40), default='')
    intro = db.Column(db.Text, default='')
    alias = db.Column(db.String(64), default='')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # role = db.relationship('Role', foreign_keys="User.role_id")
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # uploads = db.relationship('Upload', backref='author', lazy='dynamic')

    # 赋予角色权限
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            # 判断注册邮箱是否等于管理员邮箱
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    # 检查用户是否有指定权限
    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)


   # 密码加密和解密
    @property
    def password(self):
        raise AttributeError('密码不具有可读性')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 用户最近一次登录时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    # 生成激活令牌
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 密码重置安全令牌
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    # 重置密码
    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    # 每个账号对应的文章数量
    @staticmethod
    def articles_count():
        for u in User.query.all():
            articles = Post.query.filter_by(authorID=u.id).count()
            u.articles = articles
            db.session.add(u)
            db.session.commit()

# 检查用户是否有指定权限
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser


# 加载用户回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 文章表
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    # 文章的别名
    alias = db.Column(db.String(64),default=None)
    # 文章类型，公开文章、草稿文章、审核文章，分别对应0,1,2
    type = db.Column(db.Integer, default=0)
    title = db.Column(db.String(180))
    intro = db.Column(db.Text)
    content = db.Column(db.Text)
    # 为日志是否置顶，0为不置顶，1为置顶。
    isTop = db.Column(db.Integer, default=0)
    # 作者id
    authorID = db.Column(db.Integer, db.ForeignKey('users.id'))
    # 文章发布ip地址
    IP = db.Column(db.String(40))
    # 文章发布时间
    postTime = db.Column(db.DateTime, default=datetime.utcnow)
    # 评论数量
    commentNums = db.Column(db.Integer, default=0)
    # 阅读数
    views = db.Column(db.Integer, default=0)
    # 文章标签
    tagID = db.Column(db.Integer, db.ForeignKey('tags.id'))
    # 分类
    categoryID = db.Column(db.Integer, db.ForeignKey('categorys.id'))

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        import forgery_py

        seed()
        for i in range(count):

            p = Post(type=int(randint(0, 2)),
                     content=forgery_py.lorem_ipsum.sentences(randint(5, 10)),
                     title=forgery_py.lorem_ipsum.sentence(),
                     intro=forgery_py.lorem_ipsum.sentences(randint(3, 5)),
                     postTime=forgery_py.date.date(True),
                     authorID=int(1),
                     categoryID=int(randint(1, 9)),
                     tagID=int(randint(1, 10)),
                     views=int(randint(1, 500)))
            db.session.add(p)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    # 浏览量增加
    def add_view(post, db):
        post.views += 1
        db.session.add(post)
        db.session.commit()

    @staticmethod
    # 评论量增加
    def add_comment(post, db):
        post.commentNums += 1
        db.session.add(post)
        db.session.commit



# 评论表
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    # 评论人姓名
    author = db.Column(db.String(64))
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    email = db.Column(db.String(64))
    homePage = db.Column(db.String(40))
    postTime = db.Column(db.DateTime, default=datetime.utcnow)
    # ip地址
    ip = db.Column(db.String(40))
    # 评论人电脑数据、浏览器信息等
    agent = db.Column(db.String(500))
    # 文章ID
    postID = db.Column(db.Integer, db.ForeignKey('posts.id'))
    # posts = db.relationship('Post', backref='com_author', lazy='dynamic')

    @staticmethod
    def on_change_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'aconym', 'p', 'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True
        ))
db.event.listen(Comment.content, 'set', Comment.on_change_body)

# 分类表
class Category(db.Model):
    __tablename__ = 'categorys'
    id = db.Column(db.Integer, primary_key=True)
    # 分类名字
    name = db.Column(db.String(64))
    # 排序
    order = db.Column(db.Integer, default=0)
    # 该分类下所有日志数量
    count = db.Column(db.Integer, default=0)
    # 分类别名
    alias = db.Column(db.String(64), default='')
    intro = db.Column(db.Text, default='')
    rootID = db.Column(db.Integer)
    parentID = db.Column(db.Integer)
    # 分类id反向关联
    articles = db.relationship('Post', backref='category', lazy='dynamic')

    @staticmethod
    def generate_fake():
        import forgery_py

        for i in range(10):
            c = Category(name=forgery_py.lorem_ipsum.word())
            db.session.add(c)
            db.session.commit()

    @staticmethod
    def category_count():
        for c in Category.query.all():
            count = Post.query.filter_by(categoryID=c.id).count()
            c.count = count
            db.session.add(c)
            db.session.commit()

    # @staticmethod
    # def add_category_count(categorys,db):
    #     categorys.count += 1
    #     db.session.add(categorys)
    #     db.session.commit()

# 标签
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    order = db.Column(db.Integer)
    count = db.Column(db.Integer, default=0)
    alias = db.Column(db.String(64), default='')
    intro = db.Column(db.Text)
    templater = db.Column(db.String(20))
    meta = db.Column(db.String(20))


    # 生成数据
    @staticmethod
    def generate_fake():
        import forgery_py

        for i in range(10):
            t = Tag(name=forgery_py.lorem_ipsum.word())
            db.session.add(t)
            db.session.commit()

    # 统计每个tag的文章数量
    @staticmethod
    def tags_count():
        for t in Tag.query.all():
            count = Post.query.filter_by(tagID=t.id).count()
            t.count = count
            db.session.add(t)
            db.session.commit()

# 上传文件表
class Upload(db.Model):
    __tablename__ = 'upload'
    id = db.Column(db.Integer, primary_key=True)
    # 上传文件的用户id
    AuthorID = db.Column(db.Integer, db.ForeignKey('users.id'))
    # 文件大小
    size = db.Column(db.Integer)
    # 文件默认名字
    name = db.Column(db.String(64))
    # 文件原名
    SourceName = db.Column(db.String(64))
    # 文件格式
    MimeType = db.Column(db.String(20))
    PostTime = db.Column(db.DateTime, default=datetime.utcnow)


# 博客信息
class BlogInfo(db.Model):
    __tablename__ = 'blog_info'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    keyword = db.Column(db.String(600))
    description = db.Column(db.String(2000))
    logo = db.Column(db.String(20))
    # 统计代码
    code = db.Column(db.Text)
    # 备案号
    case_number = db.Column(db.String(30))
    views = db.Column(db.Integer)

    @staticmethod
    def insert_system_indo():
        info = BlogInfo(title=u'陈新明博客',
                        keyword='python',
                        description='一个好的博客',
                        views=0,)
        db.session.add(info)
        db.session.commit()

    @staticmethod
    def add_view(db):
        view = BlogInfo.query.first()
        view.views += 1
        db.session.add(view)
        db.session.commit()


