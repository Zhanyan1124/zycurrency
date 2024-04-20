# zycurrency

python app.py - running web server

flask db migrate -m "" - generate migration files for model changes

flask db upgrade - update model changes to database

flask seed run - add seed data to the database

#  Run redis for using celery library
sudo service redis-server start
#  Run celery to execute background tasks (sending emails ...)
celery -A app.celery_app  worker --loglevel=info --pool=solo
