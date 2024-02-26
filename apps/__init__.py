from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_seeder import FlaskSeeder
from flask_mail import Mail
from config import Config


db = SQLAlchemy()
migrate = Migrate()
seeder = FlaskSeeder()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    seeder.init_app(app, db)

    mail.init_app(app)
    
    from apps.views import views
    app.register_blueprint(views, url_prefix='/')   
    from apps.auth.views import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from apps.currency.views import currency_bp
    app.register_blueprint(currency_bp, url_prefix='/currency')
    
    from apps.auth.models import User
    from apps.models import Country
    with app.app_context():
        db.create_all()
        print('Connected to Database')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
