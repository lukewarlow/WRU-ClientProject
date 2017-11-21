import os
from flask import Flask, redirect, request, render_template, jsonify, make_response, escape, session
import random
import sqlite3 as sql
from bcrypt import hashpw, gensalt
import sys
app = Flask(__name__)

DATABASE = "database.db"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route("/Home", methods=['GET'])
def returnHome():
    if request.method == 'GET':
        return render_template('home.html', title="Homepage", admin=checkIsAdmin())

# staff page
@app.route('/Login', methods=['POST', 'GET'])
def returnStaff():
    if request.method == 'POST':
        try:
            username = request.form.get('username', default="Error")
            password = request.form.get('password', default="Error")
            conn = sql.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("SELECT password FROM tblStaff WHERE username=?;", [username])
            pw = cur.fetchone()[0]
        except sql.ProgrammingError as e:
            print("Error in operation," + str(e))
        finally:
            conn.close()
        print(pw)
        if (encrypt(password, pw) == pw):
            #Cookies go here
            print(str(username) + " has logged in")
            return "Log in successful"
        else:
            print("Failed to log in, incorrect password.")
            return "Log in unsuccessful"
    else:
        return render_template('staff.html', title="Log In", admin=checkIsAdmin())

# adding staff to database on the admin page
@app.route("/Admin", methods=['POST', 'GET'])
def returnAdmin():
    if request.method == 'GET':
        if checkIsAdmin():
            return render_template('admin.html', title="Admin", admin=True)
        else:
            return render_template('home.html', title="Homepage", admin=False)
    elif request.method == 'POST':
        firstName = request.form.get('firstName', default="Error")
        surname = request.form.get('surname', default="Error")
        username = surname + firstName[0]
        username = username.lower()
        response = checkIfUserExists(username)
        if (response.split(":")[0] == "True"):
            username = username + response.split(":")[1]
        password = request.form.get('password', default="Error")
        password = encrypt(password)
        usertype = request.form.get('usertype', default="Error")

        print("Adding staff member:" + username)

        try:
            conn = sql.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO tblStaff ('username', 'password', 'usertype', 'firstname', 'surname')\
                        VALUES (?,?,?,?,?)", (username, password, usertype, firstName, surname))

            conn.commit()
            msg = "Record successfully added"
            print("Added staff member:" + username)
        except:
            conn.rollback()
            msg = "Error in insert operation"
            print("Failed to add staff member:" + username)
        finally:
            conn.close()
            return msg

def checkIsAdmin():
    return True

def checkIfUserExists(username):
    try:
        conn = sql.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM tblStaff WHERE username=?;", [username])
        data = cur.fetchall()
    except:
        print('there was an error', data)
        data = ""
    finally:
        conn.close()
        if (len(data) > 0):
            return "True:{}".format(len(data) + 1)
        else:
            return "False"
        
@app.route("/eventForm", methods = ['POST', 'GET'])
    if request.method == 'GET':
        return render_template('eventForm.html')
    if request.method == 'POST':
        eventDate = request.form.get('eventDate', default="error")
        postcode = request.form.get('postcode', default="error")
        eventRegion = request.form.get('eventRegion', default="error")
        peopleNum = request.form.get('peopleNum', default="error")
        tourNum = request.form.get('tourNum', default="error")
        ageRange = request.form.get('ageRange', default="error")
        comments = request.form.get('comments', default="error")
        try:
            conn = sqlite3.connect(DATABASE)
            cur = con.cursor()
            cur.execute("INSERT INTO eventForm ('eventDate', 'postcode', 'eventRegion', 'peopleNum', 'tourNum', 'ageRange', 'comments')\
                        VALUES (?,?,?,?,?,?,?)",(eventDate, postcode, eventRegion, peopleNum, tourNum, ageRange, comments) )
            conn.commit()
            msg = "Record successfully added"
        except:
            conn.rollback()
            msg = "Error in insert operation"
        finally:
            conn.close()

#http://dustwell.com/how-to-handle-passwords-bcrypt.html Date Accessed 20/11/2017
def encrypt(data, salt=gensalt()):
    return hashpw(bytes(data, 'utf-8'), salt)

if __name__ == "__main__":
    app.run(debug=True)
