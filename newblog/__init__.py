from flask import Flask, render_template
from flask_login import current_user
import click
from newblog.blueprint.editor import editor
from newblog.blueprint.auth import auth
from newblog.blueprint.main import main
from newblog.config import config
from newblog.models import Category
from newblog.extensions import dropzone, bootstrap, db, moment, ckeditor, mail, login_manager, csrf, admin, \
    NewBlogModelView,cache
from newblog.models import User, Post, Permission, Comment, Category, Role, db
from flask_admin.contrib.sqla import ModelView
from wtforms import TextAreaField
from wtforms.widgets import TextArea
from newblog.utils import redirect_back
import os


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask('newblog')
    app.config.from_object(config[config_name])
    register_extensions(app)
    register_template_context(app)
    register_blueprints(app)
    register_commands(app)

    # register_shell_context(app)
    # register_template_context(app)
    return app


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        categories = Category.query.order_by(Category.id.desc())
        role = Role.query.filter_by(name='Editor').first()
        editors = User.query.filter_by(role=role)
        unread_comments = False;
        if current_user.is_authenticated:
            unread_comments = Comment.query.join(Post, Post.id == Comment.post_id).filter(
                Post.author_id == current_user.id, Comment.reviewed == False).count()
        permission = Permission()
        return dict(categories=categories, editors=editors, Permission=permission, unread_comments=unread_comments)


def register_commands(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, User=User, Role=Role, Post=Post, Permission=Permission)

    @app.cli.command()
    @click.option('--username', prompt=True, help='enter your username')
    @click.option('--password', prompt=True, help='Enter yout password')
    def createeditor(username, password):
        """ Create a editor account"""
        u = User(username=username, password=password)
        u.role = Role.query.filter_by(name='Editor').first()
        db.session.add(u)
        db.session.commit()
        click.echo('Done')

    # 创建具有编辑、发表文章的用户(只能编辑自己的文章)
    @app.cli.command()
    @click.option('--username', prompt=True, help='enter your username')
    @click.option('--password', prompt=True, help='Enter yout password')
    def createsuperuser(username, password):
        """ Create a editor account"""
        u = User(username=username, password=password,confirmed=True)
        u.role = Role.query.filter_by(name='Admin').first()
        db.session.add(u)
        db.session.commit()
        click.echo('Done')

    # 创建具有管理员权限的超级用户

    @app.cli.command()
    @click.option('--editor', default=5, help='Quantity of editors,default is 5')
    @click.option('--category', default=10, help='Quantity of categories,default is 10')
    @click.option('--post', default=50, help='Quantity of posts,default is 50')
    @click.option('--comment', default=500, help='Quantity of commant,default is 500')
    def forge(editor, category, post, comment):
        """ Generates the fake categories,posts,and comments"""
        from newblog.fakes import fake_editor, fake_categories, fake_posts, fake_comments

        db.drop_all()
        db.create_all()
        Role.insert_roles()
        click.echo('Generating %d editors...' % editor)
        fake_editor(editor)
        click.echo('Generating %d categories...' % category)
        fake_categories(category)
        click.echo('Generating %d posts...' % post)
        fake_posts(post)
        click.echo('Generating %d comments...' % comment)
        fake_comments(comment)
        click.echo('Done')


# 创建虚拟用户

def register_extensions(app):
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    bootstrap.init_app(app)
    db.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)
    admin.init_app(app, index_view=None, endpoint=None, url=None)
    # dropzone.init_app(app)
    cache.init_app(app)


def register_blueprints(app):
    app.register_blueprint(editor, url_prefix='/editor')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(main)


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


# def register_template_context(app):
#     @app.context_processor
#     def make_template_context():
#         editor = Admin.query.first()
#         categories = Category.query.order_by(Category.name).all()
#         return dict(editor=editor,categories=categories)

class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


class NewBlogModelView(ModelView):
    def is_accessible(self):
        return current_user.is_administrator()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect_back()

    form_overrides = {
        'body': CKTextAreaField
    }


class UserModelView(NewBlogModelView):
    column_searchable_list = ('email', 'username')


admin.add_view(UserModelView(User, db.session))
admin.add_view(NewBlogModelView(Post, db.session))
admin.add_view(NewBlogModelView(Category, db.session))
admin.add_view(NewBlogModelView(Comment, db.session))
