import sqlite3
import hashlib
import csv
import random
from flask import Flask, render_template, redirect, url_for, request, session, send_from_directory
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
            return redirect(url_for('index'))

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
                    session["username"]=row['usrname']
                    session['logged_in']=True
                    return redirect(url_for('dashboard'))
                else:
                    print("invalid creds")
    return render_template('index.html')

@app.route('/pricing')
def pricing():
    return (render_template('pricing.html'))

@app.route('/design', methods=['GET', 'POST'])
@is_logged_in
def design():
    if request.method == 'POST':
        print("gotten some stuff")
        return("got sometin")
    return (render_template('design.html'))

@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def dashboard():
    if request.method == 'POST':
        return (render_template('dashboard.html'))
    else:
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
        return (redirect(url_for('index')))

    return render_template('register.html', error=error)

@app.route('/parse_data', methods=['GET', 'POST'])
def parse_data():
    datax=None
    if request.method == "POST":
        print("got post")
        datax=request.json
        dat_array=datax.split("*")
        title=dat_array[0]
        header=dat_array[1]
        survey_name=dat_array[2]
        ht=dat_array[3]
        lent=dat_array[4]
        ht=ht.replace("  ","")
        ht=ht.replace('"',"|")
        ht=ht.replace("'","|")
        session["title"]=title
        session["header"]=header
        session["survey_name"]=survey_name
        session["ht"]=ht
        session["lent"]=lent
        print(session["title"])
        print(session["header"])
        print(session["survey_name"])
        print(session["ht"])
        print(session["lent"])
        length=int(session["lent"])
        init_string="create table "+ str(session["survey_name"]) +"("
        for x in range(length):
            num=x+1
            textpend="q"+str(num)+" text ,"
            init_string+=textpend
        init_string=init_string[:-1]
        init_string+=");"
        print(init_string)
        con = mysql.connect
        cur = con.cursor()
        cur.execute(init_string)
        con.commit()
        print("added table")
        quert='''insert into survey values("'''+session["survey_name"]+'''","'''+session["username"]+'''","''' + session["ht"]+'''","''' + session["title"]+'''","''' + session["header"]+'''");'''
        print(quert)
        #cur = mysql.connection.cursor()
        #cur.execute(quert)
        con = mysql.connect
        cur = con.cursor()
        cur.execute(quert)
        con.commit()
        print("registered survey")
        redstring="/survey/"+session["survey_name"]
        return(redirect(redstring))

@app.route('/table', methods=['GET', 'POST'])
def table():
    session['dat']=[]
    session['cols']=[]
    con = mysql.connect
    cur = con.cursor()
    cur.execute("SELECT * FROM "+str(session["surveyname"]))
    list_of_values=[]
    list_of_cols=[]
    with con:
        rows = cur.fetchall()
        for row in rows:
            list_of_values.append(list(row.values()))

    for z in range(len(list_of_values[0])):
        e=z+1
        d="que-"+str(e)
        list_of_cols.append(d)

    session["mentions"]=list_of_values
    session["cols"]=list_of_cols
    session["mentionsx"]=len(list_of_values)
    session["mentionsxy"]=len(list_of_values[0])
    print(session["mentions"])
    return render_template("table.html")

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


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory='static', filename=filename)


@app.route("/survey/<string:name>")
def surve(name):
    session['surveyname']=name
    select_query="select * from survey where nme='"+str(name)+"' ;"
    con = mysql.connect
    cur = con.cursor()
    cur.execute(select_query)
    with con:
        rows = cur.fetchall()
        for row in rows:
            session['nme']=row['nme']
            session['tito']=str(row['title'])
            xc=row['html']
            xc=xc.replace("|",'"')
            xc=xc.replace("wrap",'')
            xc=xc.replace("<ul",'<li')
            xc=xc.replace("</ul",'</li')
            xc=xc.replace('<i class="now-ui-icons ui-1_simple-remove text-dark"></i>',"")
            session['heda']=row['header']
            session['htmlo']=xc
    return redirect(url_for("survey"))

@app.route("/survey", methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        datax=request.json
        print(datax)
        print(datax[1])
        qstring=""
        for x in datax:
            qstring+="'"+x+"',"
        qstring=qstring[:-1]
        print(qstring)
        query="insert into "+str(session['surveyname'])+" values("+qstring+");"
        print(query)
        con = mysql.connect
        cur = con.cursor()
        cur.execute(query)
        con.commit()
        print("complete")
    return render_template("survey.html")
'''
@app.route('/<string:page_name>/')
def render_static(page_name):
    return render_template('%s.html' % page_name)'''

@app.route("/dashboard/<string:name>")
def handle_dash(name):
    if name=="table":
        return redirect(url_for("table"))

    
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port= 8090)
