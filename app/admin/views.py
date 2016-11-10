from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, login_user, current_user, logout_user
from sqlalchemy import or_
from app import db
from app.models import User
from app.email import send_mail
from . import admin
from .forms import LoginForm, RegisterForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm


@admin.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'admin'\
                and request.endpoint != 'static':
            return redirect(url_for('admin.unconfirmed'))

@admin.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('admin/unconfirmed.html')

@admin.route('/resend_confirmation')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email, '账号激活', 'mail/confirm', user=current_user, token=token)
    flash(u'激活邮件发送成功')
    return redirect(url_for('main.index'))


@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(or_(User.username == form.name.data, User.email == form.name.data)).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'账号密码无效')
    if form.errors:
        flash('登陆失败，请尝试重新登陆.')

    return render_template('admin/login.html', form=form)


# 账号退出
@admin.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash(u'账号退出成功')
    return redirect(url_for('main.index'))

# 更改密码
@admin.route('/change_password', methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(password=form.old_password.data):
            if form.old_password.data == form.password.data:
                flash(u'密码不可以和原密码一样')
            else:
                current_user.password = form.password.data
                db.session.add(current_user)
                flash(u'密码修改成功')
        else:
            flash(u'无效密码')
    return render_template('admin/change_password.html', form=form)

# 重置密码发送重置链接
@admin.route('/reset', methods=['GET','POST'])
def password_reset_request():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_mail(user.email, '重置密码',
                      'mail/reset_password', user=user, token=token,
                      next=request.args.get('next'))
            flash(u'包含重置密码的邮件已经发送到您的邮箱')
            return redirect(url_for('admin.login'))
        else:
            flash(u'该邮箱不存在')
    return render_template('admin/reset_password.html', form=form)

# 点击重置链接重置密码
@admin.route('/reset/<token>', methods=['GET','POST'])
def password_reset(token):
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash(u'您的密码重置成功')
            return redirect(url_for('admin.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('admin/reset_password.html', form=form)




@admin.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_mail(user.email, '账号激活', 'mail/confirm', user=user, token=token)
        flash(u'一封激活邮件发送到你的注册邮箱')
        return redirect(url_for('main.index'))
    return render_template('admin/register.html', form=form)

@admin.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash(u'你已经成功激活账号，谢谢')
    else:
        flash(u'激活链接无效或失效')
    return redirect(url_for('main.index'))

