from flask import Blueprint, abort, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from models import db, Post, User, Like
from tools import ImageSaver, PostsFilter
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from config import ADMIN_ROLE

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
    user_id = current_user.id if current_user.is_authenticated else None
    search_params = {
        'search': request.args.get('search', ''),
        'only_subscriptions': request.args.get('only_subscriptions') == '1',
        'user_id': user_id
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

@bp.route('/admin')
@login_required
def admin():
    if current_user.role_id == ADMIN_ROLE:
        user_id = current_user.id if current_user.is_authenticated else None
        
        posts_query = db.session.query(Post)
        posts_query = posts_query.filter(Post.status == '1')
        posts_query = posts_query.options(joinedload(Post.author))
        pagination = db.paginate(posts_query)
        posts = pagination.items

        return render_template('posts/admin.html',
                            posts=posts,
                            pagination=pagination)
    else:
        flash('Доступ к этой странице запрещен', 'danger')
        return redirect(url_for('posts.index'))



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


@bp.route('/subscribe/<int:user_id>', methods=['GET','POST'])
@login_required
def subscribe(user_id):
    if user_id == current_user.id:
        flash('Вы не можете подписаться на себя.', 'warning')
        return redirect(url_for('posts.index'))
    user_to_subscribe = db.session.execute(db.select(User).filter_by(id=user_id)).scalar()
    if user_to_subscribe:
        current_user.followed.append(user_to_subscribe)
        db.session.commit()
        flash(f'Вы успешно подписались на пользователя {user_to_subscribe.login}.', 'success')
    else:
        flash('Пользователь не найден.', 'danger')
    return redirect(url_for('posts.index'))


@bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like(post_id):
    post = db.session.execute(db.select(Post).filter_by(id=post_id)).scalar()
    
    if post:
        # Проверяем, лайкал ли пользователь этот пост
        if current_user.id in [like.user_id for like in post.post_likes]:
            like_delete = db.session.execute(db.select(Like).filter_by(user_id=current_user.id, post_id=post.id)).scalar()
            db.session.delete(like_delete)
            db.session.commit()
            flash('Вы убрали лайк с поста(', 'success')
        else:
            like = Like(user_id=current_user.id, post_id=post.id)
            db.session.add(like)
            db.session.commit()
            flash('Пост лайкнут!', 'success')
    else:
        flash('Пост не найден.', 'danger')
    
    return redirect(url_for('posts.index'))

@bp.route('/report/<int:post_id>', methods=['GET','POST'])
@login_required
def report(post_id):
    post = db.session.execute(db.select(Post).filter_by(id=post_id)).scalar()
    if post:
        post.status = 1
        db.session.add(post)
        db.session.commit()
    return redirect(url_for('posts.index'))


@bp.route('/post_policy/<int:post_id>', methods=['POST'])
@login_required
def post_policy(post_id):
    post = db.session.execute(db.select(Post).filter_by(id=post_id)).scalar()
    if not post:
        return redirect(url_for('posts.index'))

    action = request.form.get('action')

    if action == '1':
        post.status = 0
        db.session.add(post)
    elif action == '2':
        post.author.status = 1
        post.author.unlocked_at = datetime.now() + timedelta(weeks=1)
        post.status = 2
        db.session.add(post)
        db.session.add(post.author)
    elif action == '3':
        post.author.status = 1
        post.author.unlocked_at = datetime.now() + timedelta(days=30)
        post.status = 2
        db.session.add(post)
        db.session.add(post.author)
    elif action == '4':
        post.author.status = 2
        post.status = 2
        db.session.add(post)
        db.session.add(post.author)
    else:
        flash('Ошибка при применении политики', 'success')
        return redirect(url_for('posts.admin'))

    db.session.commit()
    flash('Политика успешно применена', 'success')
    return redirect(url_for('posts.admin'))
