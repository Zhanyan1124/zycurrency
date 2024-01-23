<<<<<<< HEAD
from flask import Flask, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'currencyex'
db = MySQL(app)


@app.route('/')
def index():
    return render_template('home.html')

if __name__ == "__main__":
=======
from flask import Flask, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'currencyex'
db = MySQL(app)


@app.route('/')
def index():
    return render_template('home.html')

if __name__ == "__main__":
>>>>>>> 606f84da8a5d91bf8b3899e4a4d4df0efe88f8ad
    app.run(debug=True)