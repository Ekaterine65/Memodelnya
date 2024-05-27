from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError
from models import db, Post, User
from tools import EditProfileForm, ImageSaver

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/')
@login_required
def index():
    user = current_user
    posts = db.session.query(Post).filter_by(user_id=user.id).all()
    return render_template('/profile/profile.html', user=user, posts=posts)

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditProfileForm()
    if form.validate_on_submit():
        # Обработка отправки формы редактирования профиля
        current_user.login = form.login.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.set_password(form.password.data)

        f = request.files.get('avatar')
        #flash(f'{f}', 'success')
        if f and f.filename:
            try:
                img = ImageSaver(f).save()
                current_user.avatar_id = img.id
                #flash('Изображение сохранено успешно.', 'success')
            except IntegrityError as err:
                flash(f'Возникла ошибка при сохранении изображения. ({err})', 'danger')
                db.session.rollback()
                return render_template('/profile/edit.html', form=form)


        db.session.commit()
        flash('Изменения сохранены успешно!', 'success')
        return redirect(url_for('profile.index'))
    elif request.method == 'POST':
        flash('Исправьте ошибки в форме', 'danger')
    else:
        # Заполнение формы текущими данными пользователя
        form.login.data = current_user.login
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    return render_template('/profile/edit.html', form=form)

@bp.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    user = current_user
    user_id = user.id
    logout_user()
    try:
        user_to_delete = db.session.execute(db.select(User).filter_by(id=user_id)).scalar()
        if user_to_delete:
            db.session.query(Post).filter_by(user_id=user_id).delete()
            db.session.commit()

            db.session.delete(user_to_delete)
            db.session.commit()
            flash('Ваш аккаунт был успешно удалён.', 'success')
        else:
            flash('Ошибка при удалении аккаунта. Повторите попытку позже.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении аккаунта. Повторите попытку позже. {e}', 'danger')
    return redirect(url_for('index'))