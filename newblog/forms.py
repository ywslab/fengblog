from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, SelectField, TextAreaField, ValidationError, HiddenField, \
    BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, URL, EqualTo
from newblog.models import Category, User, Role


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 128)])
    remember_me = BooleanField('记住账号')
    submit = SubmitField('登陆')


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    nickname = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', message='两次密码必须相同')])
    password2 = PasswordField('再次输入密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已存在')

    def validate_nickname(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该昵称已存在')


class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 60)])
    category = SelectField('分类', coerce=int, default=1)
    body = CKEditorField('主体', validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all()]


class CategoryForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField()

    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('这个名字已经被使用了')


class CommentForm(FlaskForm):
    body = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField()


class CategoryForm(FlaskForm):
    name = TextAreaField('Category', validators=[DataRequired()])
    submit = SubmitField()


class ForgetPasswordForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField()


class ResetPasswordForm(FlaskForm):
    password1 = PasswordField('密码', validators=[DataRequired(), Length(1, 128)])
    password2 = PasswordField('重复', validators=[DataRequired(), Length(1, 128)])
    submit = SubmitField()
