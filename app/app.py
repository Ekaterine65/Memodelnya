from flask import Flask, render_template, send_from_directory
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from models import db, Image
from auth import bp as auth_bp, init_login_manager
from posts import bp as posts_bp
from profile import bp as profile_bp
from flask import g
from flask_login import current_user

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

db.init_app(app)
migrate = Migrate(app, db)

init_login_manager(app)

@app.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(err):
    error_msg = ('Возникла ошибка при подключении к базе данных. '
                 'Повторите попытку позже.')
    return f'{error_msg} (Подробнее: {err})', 500

@app.context_processor
def inject_user():
    return dict(user=current_user)

app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(profile_bp)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/images/<image_id>')
def image(image_id):
    img = db.get_or_404(Image, image_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               img.storage_filename)
