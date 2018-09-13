import sqlite3
import hashlib
from flask import Flask, render_template, redirect, url_for, request, session
from functools import wraps
from main import *
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "nico"
#mysql = MySQL()
print("initializing database")
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = "'123'"
app.config['MYSQL_DB'] = 'ccsats'
app.config['MYSQL_PORT'] = 3360
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
print("database initialized")

#mysql.init_app(app)
app.debug = True


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return wrap

@app.route('/')
def index():
    return (render_template('index.html')) 

@app.route('/', methods=['POST','GET'])
def process_login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        print(email)
        print(password)
        con = mysql.connect
        cur = con.cursor()
        cur.execute("SELECT * FROM users")
        with con:
            rows = cur.fetchall()
            print("===================")
            print(rows[0])
            print(rows[1])
            print("===================")
            for row in rows:
                print("===")
                print(row['usrname'])
                print(row['passwrd'])
                print("===")
                if row['usrname']==email and row['passwrd']==password:
                    return redirect(url_for('design'))
                else:
                    print("invalid creds")
    return render_template('index.html')

@app.route('/pricing')
def pricing():
    return (render_template('pricing.html'))

@app.route('/design')
def design():
    return (render_template('design.html'))

@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def dashboard():
    if request.method == 'POST':
        session["to_search"] = request.form["to_search"]
        print("gotten some stuff")
        session["y"], session["x"] = main(session['to_search'])
        session["mentions"] = f_mentions()
        session["id_comment"] = f_id()
        session["comment_x"] = f_comments()
        session["time_x"] = f_time()
        session["date_x"] = f_date()
        session["polarity_x"] = f_polarity()
        session["colors"] = f_colors()
        return (render_template('dashboard.html'))
    else:
        session["y"], session["x"] = main(session['username'])
        session["mentions"] = f_mentions()
        session["id_comment"] = f_id()
        session["comment_x"] = f_comments()
        session["time_x"] = f_time()
        session["date_x"] = f_date()
        session["polarity_x"] = f_polarity()
        session["colors"] = f_colors()
        return (render_template('dashboard.html'))


@app.route('/topics')
def topics():
    return (render_template('topics.html'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        print("get req")
        emailreg = request.form['emailreg']
        passwordreg = request.form['passwordreg']
        print("====register=====")
        print(emailreg)
        print(passwordreg)
        print("====+++++++=====")
        que='''select * from users;'''
        quert='''insert into users values("'''+emailreg+'''","'''+passwordreg+'''");'''
        print(quert)
        #cur = mysql.connection.cursor()
        #cur.execute(quert)
        con = mysql.connect
        cur = con.cursor()
        cur.execute(quert)
        con.commit()
        print("registered")
        #rv = cur.fetchall()
        #print(rv)
        return (render_template('index.html'))

    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        completion = validate(username, password)
        if completion == False:
            app.logger.info("PASSWORD NOT MATCHED")
            error = 'Invalid Credentials. Please try again...'
        else:
            app.logger.info("PASSWORD MATCHED")
            session['logged_in'] = True
            session['username'] = username
            con = sqlite3.connect('static/login.db')
            with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM users")
                rows = cur.fetchall()
                for row in rows:
                    dbUser = row[0]
                    dbsub = row[3]
                    if dbUser == username:
                        subscription = dbsub
            session['subscription'] = subscription
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)


def validate(username, password):
    con = sqlite3.connect('static/login.db')
    completion = False
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        for row in rows:
            dbUser = row[0]
            dbPass = row[1]
            if dbUser == username:
                completion = check_password(dbPass, password)
    return completion


def check_password(hashed_password, user_password):
    return hashed_password == user_password


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/survey/<string:name>")
def surve(name):
    name=name
    return redirect(url_for("survey",name=name))

@app.route("/survey")
def survey():
    name="name"
    return render_template("survey.html",name=name)
'''
@app.route('/<string:page_name>/')
def render_static(page_name):
    return render_template('%s.html' % page_name)'''

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port= 8090)
