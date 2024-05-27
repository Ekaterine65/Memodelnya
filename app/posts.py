from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from models import db, Post, User
from tools import ImageSaver, PostsFilter
from sqlalchemy.orm import joinedload

bp = Blueprint('posts', __name__, url_prefix='/posts')

POST_PARAMS = [
    'user_id', 'title', 'body'
]

def params():
    return { p: request.form.get(p) or None for p in POST_PARAMS }

def search_params():
    return {
        'title': request.args.get('title'),
    }

@bp.route('/')
def index():
    search_params = {
        'search': request.args.get('search', ''),
        'only_subscriptions': request.args.get('only_subscriptions', '0') == '1'
    }

    posts_filter = PostsFilter(**search_params)
    posts_query = posts_filter.perform()

    posts_query = posts_query.options(joinedload(Post.author))

    pagination = db.paginate(posts_query)
    posts = pagination.items

    return render_template('posts/index.html',
                           posts=posts,
                           pagination=pagination,
                           search_params=search_params)


@bp.route('/create', methods=['POST'])
@login_required
def create():
    f = request.files.get('background_img')
    img = None
    post = Post()
    try:
        if f and f.filename:
            img = ImageSaver(f).save()

        image_id = img.id if img else None
        post = Post(
            user_id=current_user.id,
            title=request.form['description'],
            background_image_id=image_id
        )
        db.session.add(post)
        db.session.commit()
    except IntegrityError as err:
        flash(f'Возникла ошибка при записи данных в БД. Проверьте корректность введённых данных. ({err})', 'danger')
        db.session.rollback()
        return render_template('posts/index.html')

    flash(f'Пост {post.title} был успешно добавлен!', 'success')

    return redirect(url_for('posts.index'))

