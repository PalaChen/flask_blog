import os
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.models import Role, User, Permission, Post, Upload, Category, Comment, \
    BlogInfo, Tag

app = create_app(os.environ.get('APP_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app)

def make_shell_context():
    return dict(app=app, db=db, Role=Role, User=User, Permission=Permission, Post=Post, Upload=Upload,
                Category=Category, Comment=Comment, BlogInfo=BlogInfo, Tag=Tag)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
# jinja2全局变量
app.jinja_env.globals['Category'] = Category
app.jinja_env.globals['Post'] = Post
app.jinja_env.globals['Tag'] = Tag

@manager.command
def dev():
    from livereload import Server
    live_server = Server(app.wsgi_app)
    live_server.watch('**/*.*')
    live_server.serve(open_url=False)

@manager.command
def base():
    from app import db
    db.drop_all()
    db.create_all()
    Role.insert_roles()
    from app.models import User
    user = User(email='koio@163.com',
                username='pala',
                password='qweasd123',
                confirmed=True)
    db.session.add(user)
    db.session.commit()
    Category.generate_fake()
    Tag.generate_fake()
    Post.generate_fake(100)
    BlogInfo.insert_system_indo()

    # 统计分类和标签的文章数量
    Category.category_count()
    Tag.tags_count()
    User.articles_count()



if __name__ == '__main__':
    manager.run()