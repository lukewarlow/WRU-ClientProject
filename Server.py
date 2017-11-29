import os
from flask import Flask, redirect, request, render_template, jsonify, make_response, escape, session
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import sqlite3 as sql
from bcrypt import hashpw, gensalt
import sys
import datetime
import smtplib
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
server.ehlo()
server.login("acc0untcreation123", "Lithium3")
DATABASE = "database.db"

#Generated using os.urandom(24), got from flask documentation.
#http://flask.pocoo.org/docs/0.12/quickstart/ Accessed: 28/11/2017
app.secret_key = b'\xac\x9b.\x8ew\xa2\x1b\x8d\xdf\xdbB\x00\xf6r95\xb5fy"\x85G\x11"'
verificationSigner = URLSafeTimedSerializer(b'\xb7\xa8j\xfc\x1d\xb2S\\\xd9/\xa6y\xe0\xefC{\xb6k\xab\xa0\xcb\xdd\xdbV')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route("/Home", methods=['GET'])
def returnHome():
    if request.method == 'GET':
        return render_template('home.html', title="Homepage", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn(), isverified=checkIsVerified())

@app.route("/home", methods=['GET'])
@app.route("/index", methods=['GET'])
@app.route("/Index", methods=['GET'])
def redirectHome():
    return redirect("/Home")

@app.route('/Staff/Verify/<payload>', methods=['GET'])
def returnStaffVerify(payload):
    if request.method == "GET":
        if checkIsLoggedIn() == False and checkIsVerified() == False:
            return render_template('staff/verify.html', title="Verify Login", admin=False, isloggedin=checkIsLoggedIn(), isverified=checkIsVerified(), payload=payload)
        else:
            return redirect("/Home")

@app.route('/Staff/Verify', methods=['POST'])
def returnStaffVerifyPost():
    if request.method == "POST":
        if checkIsLoggedIn() == False and checkIsVerified() == False:
            payload = request.form.get('payload', default="Error")
            try:
                user = verificationSigner.loads(payload)
            except Exception as e:
                print(str(e))
                return "Verification failed"
            username = request.form.get('username', default="Error")
            password = request.form.get('password', default="Error")
            newpassword = encrypt(request.form.get('newpassword', default="Error"))
            if (user == username):
                userexists = checkIfUserExists(username)
                if (userexists != "False"):
                    check = checkLogin(username, password)
                    if (check == False):
                        print("Failed to log in, incorrect password.")
                        return "unsuccessful"
                    else:
                        session['username'] = check.split(":")[1]
                        try:
                            conn = sql.connect(DATABASE)
                            cur = conn.cursor()
                            cur.execute("UPDATE tblStaff SET password=?, verified='True' WHERE username=?", [newpassword, username])
                            conn.commit()
                            print("Password updated")
                        except Exception as e:
                            conn.rollback()
                            print(str(e))
                            print("Error")
                        finally:
                            conn.close()

                        session['usertype'] = check.split(":")[2]
                        session['verified'] = "True"
                        print(str(username) + " has verified")
                        return "successful"
                else:
                    return "User doesn't exist"
            else:
                return "Username doesn't match, your email"


@app.route('/Staff/Verify', methods=['GET'])
@app.route('/Staff/verify', methods=['GET'])
@app.route('/staff/Verify', methods=['GET'])
@app.route('/staff/verify', methods=['GET'])
def redirectVerify():
    return redirect("/Staff/Verify")

# staff page
@app.route('/Staff/Login', methods=['POST', 'GET'])
def returnLogin():
    if request.method == 'POST':
        username = request.form.get('username', default="Error").lower()
        password = request.form.get('password', default="Error")
        userexists = checkIfUserExists(username).split(":")
        if (len(userexists) == 2):
            check = checkLogin(username, password)
            if (check == False):
                print("Failed to log in, incorrect password.")
                return "unsuccessful"
            else:
                session['username'] = check.split(":")[1]
                session['usertype'] = check.split(":")[2]
                session['verified'] = check.split(":")[3]
                print(str(username) + " has logged in")
                return "successful"

        else:
            print("Failed to log in, incorrect username.")
            return "unsuccessful user not found"
    else:
        return render_template('staff/login.html', title="Log In", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn(), isverified=checkIsVerified())

def checkLogin(username, password):
    try:
        conn = sql.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT username, password, usertype, verified FROM tblStaff WHERE username=?;", [username])
        data = cur.fetchone()
        pw = data[1]
        user = data[0]
        usertype = data[2]
        verified = data[3]
        conn.close()
    except sql.ProgrammingError as e:
        print("Error in operation," + str(e))
        conn.close()
        return False;
    if (encrypt(password, pw) == pw):
        return "True:{}:{}:{}".format(user, usertype, verified)
    else:
        return False;
@app.route("/Staff/login", methods=['GET'])
@app.route("/staff/Login", methods=['GET'])
@app.route("/staff/login", methods=['GET'])
def redirectLogin():
    return redirect("/Staff/Login")

@app.route("/Staff/EventForm", methods = ['POST', 'GET'])
def returnEventForm():
    if request.method == 'GET':
        now = datetime.datetime.now()
        return render_template('staff/event.html', title="Event Form", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn(), isverified=checkIsVerified(), date=now.strftime("%Y-%m-%d"))
    elif request.method == 'POST':
        eventDate = request.form.get('eventDate', default="error")
        postcode = request.form.get('postcode', default="error")
        postcode = postcode.upper()
        eventRegion = request.form.get('eventRegion', default="error")
        eventName = request.form.get('eventName', default="error")
        inclusivity = request.form.get('inclusivity', default="error")
        activityTypes = request.form.get('activityTypes', default="error")
        comments = request.form.get('comments', default="error")
        try:
            conn = sql.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO tblEvent ('eventName', 'eventDate', 'postcode', \
            'eventRegion', 'inclusivity', 'activityTypes', 'comments')\
                        VALUES (?,?,?,?,?,?,?)",(eventName, eventDate, postcode, eventRegion,\
                         inclusivity, activityTypes, comments))
            conn.commit()
            msg = "Record successfully added"
        except sql.ProgrammingError as e:
            print("Error in operation," + str(e))
            conn.rollback()
            msg = "Error in insert operation"
        finally:
            conn.close()
            return msg;

@app.route("/Staff/Eventform", methods=['GET'])
@app.route("/Staff/eventForm", methods=['GET'])
@app.route("/Staff/eventform", methods=['GET'])
@app.route("/staff/EventForm", methods=['GET'])
@app.route("/staff/Eventform", methods=['GET'])
@app.route("/staff/eventForm", methods=['GET'])
@app.route("/staff/eventform", methods=['GET'])
def redirectEvent():
    return redirect("/Staff/EventForm")

@app.route("/Staff/TournamentForm", methods = ['POST', 'GET'])
def returnTourForm():
    if request.method == 'GET':
        #https://www.saltycrane.com/blog/2008/06/how-to-get-current-date-and-time-in/ Date Accessed: 29/11/2017
        now = datetime.datetime.now()
        return render_template('staff/tournament.html', title="Tournament Form", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn(), isverified=checkIsVerified(), date=now.strftime("%Y-%m-%d"))
    elif request.method == 'POST':
        eventDate = request.form.get('eventDate', default="error")
        postcode = request.form.get('postcode', default="error")
        postcode = postcode.upper()
        eventName = request.form.get('eventName', default="error")
        peopleNum = request.form.get('peopleNum', default="error")
        ageCategory = request.form.get('ageRange', default="error")
        rugbyOffers = request.form.get('rugbyOffers', default="error")
        genderRatio = request.form.get('genderRatio', default="error")
        eventExists = False
        try:
            conn = sql.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("SELECT ID FROM tblEvent WHERE eventDate=? AND postcode=? ;", [eventDate, postcode])
            # cur.execute("SELECT ID FROM tblEvent WHERE (eventDate=? AND postcode=?) OR (eventName=? AND eventDate=?);", [eventDate, postcode])
            data = cur.fetchone()
            if data:
                eventID = data[0]
                eventExists = True
        except sql.ProgrammingError as e:
            print("Error in operation," + str(e))
        finally:
            conn.close()

        if eventExists == True:
            try:
                conn = sql.connect(DATABASE)
                cur = conn.cursor()
                cur.execute("INSERT INTO tblTournament ('peopleNum',\
                 'ageCategory', 'rugbyOffers', 'genderRatio', 'eventID')\
                            VALUES (?,?,?,?,?)",(peopleNum, ageCategory,\
                             genderRatio, rugbyOffers, eventID))
                conn.commit()
                msg = "Record successfully added"
            except:
                conn.rollback()
                msg = "Error in insert operation"
            finally:
                conn.close()
                return msg
        else:
            print("Error: event not found")
            return "Event data incorrect"

@app.route("/Staff/Tournamentform", methods=['GET'])
@app.route("/Staff/tournamentForm", methods=['GET'])
@app.route("/Staff/tournamentform", methods=['GET'])
@app.route("/staff/TournamentForm", methods=['GET'])
@app.route("/staff/Tournamentform", methods=['GET'])
@app.route("/staff/tournamentForm", methods=['GET'])
@app.route("/staff/tournamentform", methods=['GET'])
def redirectTournament():
    return redirect("/Staff/TournamentForm")

# adding staff to database on the admin page
@app.route("/Admin/AddStaff", methods=['POST', 'GET'])
def returnAddStaff():
    if request.method == 'GET':
        if checkIsAdmin():
            return render_template('admin/addstaff.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn(), isverified=checkIsVerified())
        else:
            return redirect("/Home")
    elif request.method == 'POST':
        firstName = request.form.get('firstName', default="Error")
        surname = request.form.get('surname', default="Error")
        username = surname + firstName[0]
        username = username.lower()
        response = checkIfUserExists(username)
        if (response.split(":")[0] == "True"):
            username = username + response.split(":")[1]

        password = encrypt(request.form.get('password', default="Error"))
        email = request.form.get('email', default="Error").lower()
        usertype = request.form.get('usertype', default="Error")
        organisation = request.form.get('organisation', default="Error")

        print("Adding staff member: " + username)
        if (verifyEmail(email)):
            try:
                conn = sql.connect(DATABASE)
                cur = conn.cursor()

                cur.execute("INSERT INTO tblStaff ('username', 'password', 'email',\
                 'usertype', 'firstname', 'surname', 'organisation', 'verified')\
                            VALUES (?,?,?,?,?,?,?,?)", (username, password, email,\
                             usertype, firstName, surname, organisation, "False"))
                conn.commit()
                msg = "User {} successfully added".format(username)
                print("Added staff member: " + username)

                message = """\
                <p>
                    Hi,<br>
                    You've been added to the WRU staff database for there event data collection tool.<br>
                    Username: {}<br>
                    <a href="http://localhost:5000/Staff/Verify/{}">Click to login.</a>
                </p>""".format(username, verificationSigner.dumps(username))
                sendEmail(email, "New Account", message)
            except Exception as e:
                conn.rollback()
                msg = "Error in insert operation: " + str(e)
                print("Failed to add staff member: " + username)
            finally:
                conn.close()
                return msg
        else:
            return "Email address not found"

@app.route("/Admin/Addstaff", methods=['POST', 'GET'])
@app.route("/Admin/addStaff", methods=['POST', 'GET'])
@app.route("/Admin/addstaff", methods=['POST', 'GET'])
@app.route("/admin/AddStaff", methods=['POST', 'GET'])
@app.route("/admin/Addstaff", methods=['POST', 'GET'])
@app.route("/admin/addStaff", methods=['POST', 'GET'])
@app.route("/admin/addstaff", methods=['POST', 'GET'])
def redirectAddStaff():
    return redirect("/Admin/AddStaff")

#https://en.wikibooks.org/wiki/Python_Programming/Email Accessed: 29/11/2017
def sendEmail(recipientEmail, subject, messageHtml):
    fromAddr = "acc0untcreation123@gmail.com"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = fromAddr
    msg['To'] = recipientEmail
    html = """\
    <html>
      <head></head>
      <body>
        """ + messageHtml + """
      </body>
    </html>
    """
    msg.attach(MIMEText(messageHtml, 'html'))
    text = msg.as_string()
    server.sendmail(fromAddr, recipientEmail, text)

#https://docs.python.org/3.5/library/smtplib.html#smtplib.SMTP.verify Accessed: 29/11/2017
def verifyEmail(email):
    try:
        server.verify(email)
        return True;
    except:
        return False;

@app.route("/Admin/DeleteStaff", methods=['POST', 'GET'])
def returnDeleteStaff():
    if request.method == 'GET':
        if checkIsAdmin():
            return render_template('admin/deletestaff.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn(), isverified=checkIsVerified())
        else:
            return redirect("/Home")
    elif request.method == 'POST':
        username = request.form.get('username', default="Error")
        username = username.lower()
        if (username == session['username']):
            msg = "Can't delete self"
        else:
            try:
                data = getDetailsFromUsername(username)
                conn = sql.connect(DATABASE)
                cur = conn.cursor()
                cur.execute("DELETE FROM tblStaff WHERE username=?;", [username]);
                conn.commit()
                msg = "User {} successfully deleted".format(username)
                print("Deleted staff member:" + username)
                message = """\
                <p>
                    Hi {} {},<br>
                    You've been removed from the WRU staff database.<br>
                    You will no longer have access to the tool.
                </p>""".format(data[0], data[1])
                sendEmail(data[2], "Deleted Account", message)
            except:
                conn.rollback()
                msg = "Error in insert operation"
                print("Failed to delete staff member:" + username)
            finally:
                conn.close()
        return msg

def getDetailsFromUsername(username):
    try:
        conn = sql.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT firstname, surname, email FROM tblStaff WHERE username=?;", [username])
        data = cur.fetchone()
    except:
        print('there was an error', data)
        data = ""
    finally:
        conn.close()
    return data

@app.route("/Admin/Deletestaff", methods=['POST', 'GET'])
@app.route("/Admin/deleteStaff", methods=['POST', 'GET'])
@app.route("/Admin/deletestaff", methods=['POST', 'GET'])
@app.route("/admin/DeleteStaff", methods=['POST', 'GET'])
@app.route("/admin/Deletestaff", methods=['POST', 'GET'])
@app.route("/admin/deleteStaff", methods=['POST', 'GET'])
@app.route("/admin/deletestaff", methods=['POST', 'GET'])
def redirectDeleteStaff():
    return redirect("/Admin/DeleteStaff")

@app.route("/Logout", methods=['POST'])
def logout():
    session['username'] = ""
    session['password'] = ""
    session['usertype'] = ""
    session['verified'] = ""
    return redirect("/Home")

def checkIsLoggedIn():
    usertype = ""
    if 'usertype' in session:
        usertype = escape(session['usertype'])
    if usertype == "Admin" or usertype == "Staff" or usertype == "Guest":
        return True
    return False

def checkIsVerified():
    verified = ""
    if 'verified' in session:
        verified = escape(session['verified'])
    if verified == "True":
        return True
    return False

def checkIsAdmin():
    usertype = ""
    if 'usertype' in session:
        usertype = escape(session['usertype'])
    if usertype == "Admin":
        return True
    return False

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

#http://dustwell.com/how-to-handle-passwords-bcrypt.html Date Accessed 20/11/2017
def encrypt(data, salt=gensalt()):
    hashed = hashpw(bytes(data, 'utf-8'), salt)
    return hashed

if __name__ == "__main__":
    app.run(debug=True)
