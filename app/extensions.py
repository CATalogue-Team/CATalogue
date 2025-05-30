from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_caching import Cache
from flask_babel import Babel
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cache = Cache()
babel = Babel()

def init_app(app):
    babel.init_app(app)
    app.config['BABEL_DEFAULT_LOCALE'] = 'zh'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
