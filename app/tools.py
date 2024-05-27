import hashlib
import uuid
import os
from werkzeug.utils import secure_filename
from flask import current_app
from models import db, Image, Post
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators

class ImageSaver:
    def __init__(self, file):
        self.file = file

    def save(self):
        self.img = self.__find_by_md5_hash()
        if self.img is not None:
            return self.img
        file_name = secure_filename(self.file.filename)
        self.img = Image(
            id=str(uuid.uuid4()),
            file_name=file_name,
            mime_type=self.file.mimetype,
            md5_hash=self.md5_hash)
        self.file.save(
            os.path.join(current_app.config['UPLOAD_FOLDER'],
                         self.img.storage_filename))
        db.session.add(self.img)
        db.session.commit()
        return self.img

    def __find_by_md5_hash(self):
        self.md5_hash = hashlib.md5(self.file.read()).hexdigest()
        self.file.seek(0)
        return db.session.execute(db.select(Image).filter(Image.md5_hash == self.md5_hash)).scalar()

class PostsFilter:
    def __init__(self, search='', only_subscriptions=False):
        self.search = search
        self.only_subscriptions = only_subscriptions

    def perform(self):
        query = db.session.query(Post).order_by(Post.created_at.desc())
        if self.search:
            query = query.filter(Post.title.ilike(f"%{self.search}%"))
        # Если нужно фильтровать только подписки, добавьте соответствующую логику здесь
        # if self.only_subscriptions:
        #     query = query.filter(...)  # Логика для фильтрации подписок
        return query

class RegistrationForm(FlaskForm):
    login = StringField('Логин', [
        validators.DataRequired(message="Поле обязательно для заполнения"),
        validators.Length(min=4, max=25, message="Логин должен быть от 4 до 25 символов")
    ])
    first_name = StringField('Имя', [
        validators.DataRequired(message="Поле обязательно для заполнения"),
        validators.Length(min=1, max=100, message="Имя должно быть не длиннее 100 символов")
    ])
    last_name = StringField('Фамилия', [
        validators.DataRequired(message="Поле обязательно для заполнения"),
        validators.Length(min=1, max=100, message="Фамилия должна быть не длиннее 100 символов")
    ])
    password = PasswordField('Пароль', [
        validators.DataRequired(message="Поле обязательно для заполнения"),
        validators.EqualTo('confirm_password', message='Пароли должны совпадать'),
        validators.Length(min=6, message="Пароль должен быть не короче 6 символов")
    ])
    confirm_password = PasswordField('Подтвердите пароль', [
        validators.DataRequired(message="Поле обязательно для заполнения")
    ])