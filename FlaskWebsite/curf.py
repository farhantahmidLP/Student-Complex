from cgitb import reset
from flask import Flask, render_template, request, redirect
import csv
from os.path import exists
import os
import sqlite3 
from cgitb import reset
from datetime import datetime
from datetime import date


app = Flask(__name__)

user = []
passw = []
userType = []
loggedin = False
dateposted=[]
timeposted=[]
content=[]
email=[]
uName=[]
name=[]
prof=[]
university=[]
emailid=""
admin=False



@app.route('/')
def defaultPage():
    return render_template("index.html")

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/energy')
def energy():
    return redirect("http://192.168.1.197/")


@app.route('/login')
def loginpage():
    return render_template("login.html")


@app.route('/residents', methods=['GET', 'POST'])
def residents():
    con = sqlite3.connect("apartment.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("SELECT Users.name, Users.profile, Users.university, Users.email FROM Users WHERE Users.usertype=1")   
    rows = cur.fetchall()
    cur.close()
    return render_template("residents.html", rows=rows)


@app.route('/login', methods=['POST', 'GET'])
def login():
    global user, passw, userType, loggedin, admin
    if(loggedin):
        con = sqlite3.connect("apartment.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT Users.email, Users.passw, Users.usertype FROM Users")   
        rows = cur.fetchall()
        for row in rows:
            user.append(row['email'])
            passw.append(row['passw'])
            userType.append(row['usertype'])
        cur.close()
        admin=False
        return render_template("login.html", rows=rows)
    else:
        return render_template("dashboard.html", rows=rows)

@app.route('/authenticate', methods=['POST', 'GET'])
def autheticate():
    global user, passw, userType, loggedin, uName, name, emailid, admin
    loggedin = False
    admin=False
    con = sqlite3.connect("apartment.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("SELECT Users.email, Users.name, Users.passw, Users.usertype FROM Users")   
    rows = cur.fetchall()
    for row in rows:
        user.append(row['email'])
        uName.append(row['name'])
        passw.append(row['passw'])
        userType.append(row['usertype'])
    username = request.form['username']
    password = request.form['password']
    length = len(user)
    for i in range(length):
        if username == user[i] and password == passw[i]:
            loggedin = True
            emailid=username
            name=uName[i]
            print("Login successful")
            cur.close()
            if userType[i]==1:
                return redirect('/dashboard')
            else:
                admin=True
                return redirect('/admin')
    print("Login failed")
    cur.close()
    return render_template('login.html')


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    global loggedin, dateposted, timeposted,  content, email, name
    if(loggedin):
        con = sqlite3.connect("apartment.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT Notice.dateposted, Users.name as name, Notice.timeposted, Notice.content, Notice.email FROM Notice, Users WHERE Notice.visible=1 AND Users.email=Notice.email")   
        rows = cur.fetchall()
        for row in rows:
            dateposted.append(row['dateposted'])
            timeposted.append(row['timeposted'])
            content.append(row['content'])
        cur.close()
        return render_template("dashboard.html", rows=rows, name=name)
    else:
        return render_template("login.html")

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    global loggedin, dateposted, timeposted,  content, email, name, admin
    if(loggedin and admin):
        con = sqlite3.connect("apartment.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT Users.name, Users.email FROM Users WHERE Users.usertype=1")   
        rows = cur.fetchall()
        cur.close()
        return render_template("admin.html", rows=rows)
    else:
        return render_template("login.html")


@app.route('/addstudent', methods=['POST', 'GET'])
def addstudent():
    usernameForm = request.form['Email']
    passwordForm = request.form['Password']
    nameForm = request.form['Name']
    profileForm = request.form['Profile']
    universityForm = request.form['University']
    
    con = sqlite3.connect("apartment.db")
    cur = con.cursor()  
    cur.execute("INSERT INTO Users(email, name, university, profile, passw, usertype, loggedin) VALUES ( (?), (?), (?), (?), (?), 1, 0)",(usernameForm, nameForm, universityForm, profileForm, passwordForm,) )   
    con.commit()
    cur.close()
    return render_template('index.html')

@app.route('/removestudent', methods=['POST', 'GET'])
def removestudent():
    con = sqlite3.connect("apartment.db")
    cur = con.cursor()  
    cur.execute("DELETE FROM Notice;")
    con.commit()
    cur.execute("DELETE FROM Payment;")
    con.commit()
    cur.execute("DELETE FROM Users WHERE Users.usertype=1;")   
    con.commit()
    cur.close()
    return render_template('index.html')


@app.route('/remove', methods=['POST', 'GET'])
def remove():
    con = sqlite3.connect("apartment.db")
    cur = con.cursor()  
    cur.execute("UPDATE Notice SET visible=1")
    con.commit()
    cur.execute("DELETE FROM Notice WHERE Notice.rowid=(SELECT MIN(Notice.rowid)FROM Notice);")   
    con.commit()
    print("Updated")
    print("Deleted")
    cur.close()
    return redirect("/dashboard")

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    global loggedin, name, prof, university, emailid
    if(loggedin):
        name=[]
        prof=[]
        university=[]
        con = sqlite3.connect("apartment.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT Users.name, Users.profile, Users.university, Users.email FROM Users WHERE Users.email=(?)",(emailid,))  
        rows = cur.fetchall()
        for row in rows:
            name.append(row['name'])
            prof.append(row['profile'])
            university.append(row['university'])
            emailid=row['email']
        cur.close()
        return render_template("profile.html", emailid=emailid, name=name, prof=prof, university=university)
    else:
        return redirect("/login")


@app.route('/profupdate', methods=['POST', 'GET'])
def profupdate():
    global loggedin, name, prof, university, emailid
    formName = request.form['name'] 
    formEmail = request.form['email'] 
    formProfile = request.form['profile'] 
    formUniversity = request.form['university'] 
    print(formName, formEmail, formProfile, formUniversity, emailid)
    con = sqlite3.connect("apartment.db") 
    cur = con.cursor()  
    cur.execute("UPDATE Users SET name=(?), email=(?), profile=(?), university=(?) WHERE Users.email=(?)", (formName,formEmail,formProfile,formUniversity,emailid,))
    con.commit()
    print("Updated")
    cur.close()
    name=formName
    prof=formProfile
    university=formUniversity
    emailid=formEmail
    loggedin=False
    return redirect("/residents")

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    global loggedin, admin
    loggedin=False
    admin=False
    return render_template("login.html")

@app.route('/create', methods=['POST', 'GET'])
def create():
    return render_template("create.html")

@app.route('/add', methods=['POST', 'GET'])
def add():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    today = date.today()
    current_date = today.strftime("%d/%m/%Y")
    print("Current Time =", current_time)
    print("Current date =", current_date)

    formNote = request.form['note'] 
    print(formNote)

    con = sqlite3.connect("apartment.db") 
    cur = con.cursor()  
    cur.execute("INSERT INTO Notice(dateposted, timeposted, content, email, visible) VALUES ( (?), (?), (?), (?), 1)",(current_date, current_time, formNote, emailid,))
    con.commit()
    print("Added")
    cur.close()
    return redirect("/dashboard")



@app.errorhandler(405)
def pageNotFound(e):
    return render_template('index.html'),405


app.run(host="127.0.0.1",port=5000, debug=True)
#app.run()
