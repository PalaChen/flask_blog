import os
from flask_script import Manager, Shell
from app import create_app, db
from app.models import Role, User, Permission, Post, Upload, Category, Comment, \
    BlogInfo, Tags

app = create_app(os.environ.get('APP_CONFIG') or 'default')
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, Role=Role, User=User, Permission=Permission, Post=Post, Upload=Upload,
                Category=Category, Comment=Comment, BlogInfo=BlogInfo, Tags=Tags)
manager.add_command('shell', Shell(make_context=make_shell_context))


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
    from app.models import User
    user = User(email='koio@163.com',
                username='pala',
                password='qweasd123',
                confirmed=True,
                role_id='1')
    db.session.add(user)
    db.session.commit()

    Role.insert_roles()
    Category.generate_fake()
    Tags.generate_fake()
    Post.generate_fake(100)
    BlogInfo.insert_system_indo()



if __name__ == '__main__':
    manager.run()