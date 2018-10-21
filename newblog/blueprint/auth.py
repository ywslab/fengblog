from flask import Blueprint, render_template, url_for, current_app
from newblog.forms import LoginForm, RegistrationForm, ResetPasswordForm, ForgetPasswordForm
from newblog.models import User, db
from flask_login import login_user, logout_user, login_required, current_user
from flask import request, redirect, flash
from newblog.emails import send_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)

            return redirect(request.args.get('next') or url_for('main.index'))
        flash('账号或者密码错误')
    return render_template('auth/login.html', form=form)


@auth.route('/confirm/<token>')
@login_required

def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()

        flash('确认成功，您的账号可以正常使用')
    else:
        flash('链接非法或失效')
    return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required

def logout():
    logout_user()

    flash("成功退出")
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])

def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.nickname.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        token = user.generate_confirmation_token()
        send_email(user.email, '确认您的账号', 'auth/email/confirm', user=user, token=token)
        flash('已经往你的注册邮箱发送了一封确认邮件')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '确认您的账号', 'auth/email/confirm', user=current_user, token=token)
    flash('新的邮件已经发往您的邮箱')
    return redirect(url_for('main.index'))


@auth.route('/forget', methods=['POST', 'GET'])

def forget():
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Eamil not exist')
            return redirect(url_for('auth.forget'))
        token = user.generate_confirmation_token()
        send_email(user.email, '修改您的密码', 'auth/email/forget', user=user, token=token)
        flash('已经往你的注册邮箱发送了一封邮件')
        return redirect(url_for('main.index'))
    return render_template('auth/forget.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token.encode('utf-8'))
    except:
        return False
    user = User.query.filter_by(id=data.get('confirm')).first()
    if user is None:
        flash('非法链接')
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if form.password1.data != form.password2.data:
            flash('两次密码不同,请重新输入')
            return redirect(url_for('auth.reset', token=token))
        user.password = form.password1.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('auth/reset.html', form=form)
