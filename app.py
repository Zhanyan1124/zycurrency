from apps import create_app
from flask_mail import Mail
from apps.utils import celery_init_app
app= create_app()
celery_app = app.extensions["celery"]
mail = Mail(app)

if __name__ == "__main__":
    app.run(debug=True)