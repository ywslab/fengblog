from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_ckeditor import CKEditor
from wtforms import TextAreaField
from wtforms.widgets import TextArea
from flask_moment import Moment
from flask_login import LoginManager, current_user
from flask_wtf import CSRFProtect
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from newblog.utils import redirect_back
from flask_dropzone import Dropzone
from flask_caching import Cache

bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
ckeditor = CKEditor()
csrf = CSRFProtect()
mail = Mail()
login_manager = LoginManager()
admin = Admin()
dropzone = Dropzone()
cache = Cache()

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
    can_create = False

    def is_accessible(self):
        return current_user.is_administrator()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect_back()

    form_overrides = {
        'body': CKTextAreaField
    }
