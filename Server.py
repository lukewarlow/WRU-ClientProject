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
import xlsxwriter

app = Flask(__name__)
DATABASE = "database.db"

#Generated using os.urandom(24), got from flask documentation.
#http://flask.pocoo.org/docs/0.12/quickstart/ Accessed: 28/11/2017
app.secret_key = b'\xac\x9b.\x8ew\xa2\x1b\x8d\xdf\xdbB\x00\xf6r95\xb5fy"\x85G\x11"'
verificationSigner = URLSafeTimedSerializer(b'\xb7\xa8j\xfc\x1d\xb2S\\\xd9/\xa6y\xe0\xefC{\xb6k\xab\xa0\xcb\xdd\xdbV')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'ico'])

@app.route("/Home", methods=['GET'])
def home():
    if request.method == 'GET':
        name = getUsername()
        if (not "error" in name):
            return render_template('index.html', title="Homepage", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn(), username=name)
        else:
            return render_template('index.html', title="Homepage", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn())

@app.route("/home", methods=['GET'])
@app.route("/index", methods=['GET'])
@app.route("/Index", methods=['GET'])
def redirectHome():
    return redirect("/Home")

#http://flask.pocoo.org/snippets/50/ Accessed: 29/11/2017
#https://pythonhosted.org/itsdangerous/ Accessed: 29/11/2017
@app.route('/Staff/Verify/<payload>', methods=['GET'])
def staffVerifyGet(payload):
    if request.method == "GET":
        if checkIsLoggedIn() == False and checkIsVerified() == False:
            return render_template('staff/verify.html', title="Verify Login", admin=False, isloggedin=False, payload=payload)
        else:
            logout()
            return render_template('staff/verify.html', title="Verify Login", admin=False, isloggedin=False, payload=payload)


@app.route('/Staff/Verify', methods=['POST'])
def staffVerifyPost():
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
                        return "unsuccessful wrong password provided."
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

                        data = getDetailsFromUsername(username)
                        message = """\
                        <p>
                            Hi {} {},<br>
                            Your account has been verified.<br>
                            You will now have access to the WRU event tool.
                        </p>""".format(data[0], data[1])
                        sendEmail(data[2], "Account verified", message)
                        return "successful"
                else:
                    return "unsuccessful user doesn't exist, contact system admin."
            else:
                return "unsuccessful entered username doesn't match, the one linked to your email."

@app.route('/Staff/Verify', methods=['GET'])
@app.route('/Staff/verify', methods=['GET'])
@app.route('/staff/Verify', methods=['GET'])
@app.route('/staff/verify', methods=['GET'])
def redirectVerify():
    return redirect("/Staff/Verify")

# staff page
@app.route('/Staff/Login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', default="Error").lower()
        password = request.form.get('password', default="Error")
        userexists = checkIfUserExists(username).split(":")
        if (len(userexists) == 2):
            check = checkLogin(username, password)
            if (check == False):
                print("Failed to log in, incorrect password.")
                return "unsuccessful"
            elif (check.split(":")[3] == "True"):
                session['username'] = check.split(":")[1]
                session['usertype'] = check.split(":")[2]
                session['verified'] = True
                print(str(username) + " has logged in")
                return "successful"
            else:
                return "unsuccessful please verify account through the link in email."

        else:
            print("Failed to log in, incorrect username or use.")
            return "unsuccessful user not found"
    else:
        return render_template('staff/login.html', title="Log In", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn())

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
    if (len(pw) is not 8):
        if (encrypt(password, pw) == pw):
            return "True:{}:{}:{}".format(user, usertype, verified)
        else:
            return False;
    elif (password == pw):
        return "True:{}:{}:{}".format(user, usertype, verified)
    else:
        return False

@app.route("/Staff/login", methods=['GET'])
@app.route("/staff/Login", methods=['GET'])
@app.route("/staff/login", methods=['GET'])
def redirectLogin():
    return redirect("/Staff/Login")

# staff page
@app.route('/Staff/Account', methods=['POST', 'GET'])
def staffAccount():
    if request.method == 'POST':
        username = getUsername()
        password = request.form.get('password', default="Error")
        newpassword = request.form.get('newpassword', default="Error")
        newemail = request.form.get('newemail', default="Error")

        if (checkLogin(username, password)):
            data = getDetailsFromUsername(username)
            if (newpassword is not "Error"):
                try:
                    conn = sql.connect(DATABASE)
                    cur = conn.cursor()
                    cur.execute("UPDATE tblStaff SET password=?;", [encrypt(newpassword)])
                    conn.commit()
                    msg = "successful"
                    message = """\
                    <p>
                        Hi {} {},<br>
                        You're password has been changed.<br>
                        If this was done by you, you can safely ignore this email.<br>
                        If this wasn't done by you please contact a system admin immediately!<br>
                    </p>""".format(data[0], data[1])
                    sendEmail(data[2], "Password Changed", message)
                    print("{} password updated successfully".format(username))
                    logout()
                except Exception as e:
                    conn.rollback()
                    msg = "Error in update operation: " + str(e)
                    print(msg)
                finally:
                    conn.close()
                    return msg
            elif (newemail is not "Error"):
                if (verifyEmail(newemail)):
                    try:
                        conn = sql.connect(DATABASE)
                        cur = conn.cursor()
                        cur.execute("UPDATE tblStaff SET email=?;", [newemail])
                        conn.commit()
                        msg = "successful"
                        message1 = """\
                        <p>
                            Hi {} {},<br>
                            You're email address has been changed to: {}.<br>
                            If this was done by you, you can safely ignore this email.<br>
                            If this wasn't done by you please contact a system admin immediately.<br>
                        </p>""".format(data[0], data[1], newemail)
                        message2 = """\
                        <p>
                            Hi,<br>
                            Your account is now registered to this email account.<br>
                            If you do not recognise this service.<br>
                            Please contact {} and let them know they entered the wrong email address.<br>
                        </p>""".format(data[2])
                        sendEmail(data[2], "Email Changed", message1)
                        sendEmail(newemail, "Email Changed", message2)
                        logout()
                        print("{} email updated successfully".format(username))
                    except Exception as e:
                        conn.rollback()
                        msg = "Error in update operation: " + str(e)
                        print(msg)
                    finally:
                        conn.close()
                        return msg
                else:
                    return "unsuccessful invalid email."
            else:
                return "Error"
        else:
            return "unsuccessful, incorrect password."
    else:
        if (checkIsLoggedIn()):
            name = getUsername()
            return render_template('staff/account.html', title="Account", admin=checkIsAdmin(), isloggedin=True, username=name)
        else:
            return redirect("/Home")

@app.route("/Staff/LoginIssues", methods=['GET', 'POST'])
def loginIssues():
    if request.method == 'GET':
        if (not checkIsLoggedIn()):
            return render_template('staff/loginissues.html', title="Log In issues", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn())
        else:
            return redirect("/Home")

    elif request.method == 'POST':
        email = request.form.get('email', default="Error")
        username = request.form.get('username', default="Error")
        if (username is "Error"):
            check = checkIfEmailIsUsed(email).split(":")
            if (not check[0] == False):
                message = """\
                <p>
                    Hi {},<br>
                    Here's your username {}.<br>
                    Many Thanks
                </p>""".format(check[1], check[3])
                sendEmail(email, "Username Reminder", message)
                return "successful"
            else:
                return "email not associated with an account."
        elif (email is not "Error"):
            check = checkIfEmailIsUsed(email).split(":")
            if (not check[0] == False):
                #https://docs.python.org/3.5/library/random.html Accessed: 7/12/2017
                randVerificationKey = random.randrange(10000000, 99999999)
                try:
                    conn = sql.connect(DATABASE)
                    cur = conn.cursor()
                    cur.execute("UPDATE tblStaff SET verified='False', password=? WHERE username=?", [randVerificationKey, username])
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    conn.close()
                    print(str(e))
                    return "unsuccessful error in update operation."
                conn.close()
                message = """\
                <p>
                    Hi {},<br>
                    You (or someone pretending to be you) has requested a password reset.<br>
                    If you did NOT make this request then ignore this email; no changes will be made.<br>
                    If you did make this request, click <a href="http://localhost:5000/Staff/Verify/{}">here</a> to reset your password.<br>
                    Your new temporary password is {}.<br>
                    Many Thanks
                </p>""".format(check[1], verificationSigner.dumps(username), randVerificationKey)
                sendEmail(email, "Password Reset Request", message)
                return "successful check emails."
            else:
                return "email not associated with an account."
        else:
            return "Error"

def checkIfEmailIsUsed(email):
    try:
        conn = sql.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT firstName, surname, username FROM tblStaff WHERE email=?;", [email])
        data = cur.fetchone()
    except:
        print('there was an error', data)
        data = ""
    finally:
        conn.close()

        if (len(data) > 0):
            return "True:{}:{}:{}".format(data[0], data[1], data[2])
        else:
            return "False"

@app.route("/Staff/EventForm", methods = ['POST', 'GET'])
def eventForm():
    if request.method == 'GET':
        now = datetime.datetime.now()
        name = getUsername()
        if (not "error" in name):
            return render_template('staff/event.html', title="Event Form", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn(), date=now.strftime("%Y-%m-%d"), username=name)
        else:
            return render_template('staff/event.html', title="Event Form", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn(), date=now.strftime("%Y-%m-%d"))
    elif request.method == 'POST':
        eventStartDate = request.form.get('eventStartDate', default="error")
        eventEndDate = request.form.get('eventEndDate', default="error")
        postcode = request.form.get('postcode', default="error")
        postcode = postcode.upper()
        eventRegion = request.form.get('eventRegion', default="error")
        eventName = request.form.get('eventName', default="error")
        inclusivity = request.form.get('inclusivity', default="error")
        activityTypes = request.form.get('activityTypes', default="error")
        comments = request.form.get('comments', default="error")
        username = ""
        if 'username' in session:
            username = escape(session['username'])
            if username == "":
                msg = "error not logged in?"
            else:
                staffName = username
        else:
            msg = "error not logged in?"
        try:
            conn = sql.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO tblEvent ('eventName', 'eventStartDate', 'eventEndDate', 'postcode', \
            'eventRegion', 'inclusivity', 'activityTypes', 'comments', 'staffName')\
                        VALUES (?,?,?,?,?,?,?,?,?)",(eventName, eventStartDate, eventEndDate, postcode, eventRegion,\
                         inclusivity, activityTypes, comments, staffName))
            conn.commit()
            msg = "Record successfully added"
        except Exception as e:
            conn.rollback()
            msg = "Error in insert operation: " + str(e)
            print(msg)
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
def tournamentForm():
    if request.method == 'GET':
        #https://www.saltycrane.com/blog/2008/06/how-to-get-current-date-and-time-in/ Date Accessed: 29/11/2017
        now = datetime.datetime.now()
        name = getUsername()
        if (not "error" in name):
            return render_template('staff/tournament.html', title="Tournament Form", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn(), date=now.strftime("%Y-%m-%d"), username=name)
        else:
            return render_template('staff/tournament.html', title="Tournament Form", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn(), date=now.strftime("%Y-%m-%d"))

    elif request.method == 'POST':
        eventStartDate = request.form.get('eventDate', default="error")
        postcode = request.form.get('postcode', default="error")
        postcode = postcode.upper()
        eventName = request.form.get('eventName', default="error")
        peopleNum = request.form.get('peopleNum', default="error")
        ageCategory = request.form.get('ageRange', default="error")
        rugbyOffer = request.form.get('rugbyOffer', default="error")
        genderRatio = request.form.get('genderRatio', default="error")
        eventExists = False
        try:
            conn = sql.connect(DATABASE)
            cur = conn.cursor()
            if eventName is "":
                cur.execute("SELECT ID FROM tblEvent WHERE eventStartDate=? AND postcode=?;", [eventStartDate, postcode])
            elif postcode is "":
                cur.execute("SELECT ID FROM tblEvent WHERE eventName=? AND eventStartDate=?;", [eventName, eventStartDate])
            else:
                cur.execute("SELECT ID FROM tblEvent WHERE eventName=? AND eventStartDate=? AND postcode=?;", [eventName, eventStartDate, postcode])
            data = cur.fetchone()
            if data:
                eventID = data[0]
                eventExists = True
        except sql.ProgrammingError as e:
            print("Error in operation," + str(e))
        finally:
            conn.close()
        if eventExists == True:
            if 'username' in session:
                username = escape(session['username'])
                if username == "":
                    msg = "error not logged in?"
                else:
                    staffName = username
            else:
                msg = "error not logged in?"
            try:
                conn = sql.connect(DATABASE)
                cur = conn.cursor()
                cur.execute("INSERT INTO tblTournament ('peopleNum',\
                 'ageCategory', 'rugbyOffer', 'genderRatio', 'staffName', 'eventID')\
                            VALUES (?,?,?,?,?,?)",(peopleNum, ageCategory,\
                             genderRatio, rugbyOffer, staffName, eventID))
                conn.commit()
                msg = "Record successfully added"
            except Exception as e:
                conn.rollback()
                msg = "Error in insert operation: " + str(e)
                print(msg)
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

@app.route("/Admin/AddStaff", methods=['POST', 'GET'])
def addStaff():
    if request.method == 'GET':
        if checkIsAdmin():
            name = getUsername()
            if (not "error" in name):
                return render_template('admin/addstaff.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn(), username=name)
            else:
                return render_template('admin/addstaff.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn())
        else:
            return redirect("/Home")
    elif request.method == 'POST':
        firstName = request.form.get('firstName', default="Error")
        surname = request.form.get('surname', default="Error")
        enteredusername = surname + firstName[0]
        enteredusername = enteredusername.lower()
        response = checkIfUserExists(enteredusername)
        if (response.split(":")[0] == "True"):
            username = enteredusername + response.split(":")[1]
        else:
            username = enteredusername

        password = encrypt(request.form.get('password', default="Error"))
        email = request.form.get('email', default="Error").lower()
        usertype = request.form.get('usertype', default="Error")
        organisation = request.form.get('organisation', default="Error")

        print("Adding staff member: " + username)
        if (verifyEmail(email)):
            name = ""
            if 'username' in session:
                name = escape(session['username'])
                if name == "":
                    msg = "error not logged in?"
                else:
                    adminName = name
            else:
                msg = "error not logged in?"
            try:
                conn = sql.connect(DATABASE)
                cur = conn.cursor()

                cur.execute("INSERT INTO tblStaff ('username', 'password', 'email',\
                 'usertype', 'firstname', 'surname', 'organisation', 'verified', 'adminName')\
                            VALUES (?,?,?,?,?,?,?,?,?)", (username, password, email,\
                             usertype, firstName, surname, organisation, "False", adminName))
                conn.commit()
                msg = "User {} successfully added".format(username)
                print("Added staff member: " + username)
                message = """\
                <p>
                    Hi {} {},<br>
                    You've been added to the WRU staff database for there event data collection tool.<br>
                    Username: {}<br>
                    <a href="http://localhost:5000/Staff/Verify/{}">Click to login.</a>
                </p>""".format(firstName, surname, username, verificationSigner.dumps(username))
                sendEmail(email, "New Account", message)
            except Exception as e:
                conn.rollback()
                msg = "Error in insert operation: " + str(e)
                print(msg)
                print("Failed to add staff member: " + username)
            finally:
                conn.close()
                return msg
        else:
            return "Email address not found"

def getUsername():
    name = ""
    if 'username' in session:
        name = escape(session['username'])
        if name == "":
            msg = "error not logged in?"
        else:
            return name
    else:
        msg = "error not logged in?"
    return msg

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
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("acc0untcreation123", "Lithium3")
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
    server.quit()

#https://docs.python.org/3.5/library/smtplib.html#smtplib.SMTP.verify Accessed: 29/11/2017
def verifyEmail(email):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("acc0untcreation123", "Lithium3")
        server.verify(email)
        server.quit()
        return True;
    except:
        return False;

@app.route("/Admin/DeleteStaff", methods=['POST', 'GET'])
def deleteStaff():
    if request.method == 'GET':
        if checkIsAdmin():
            name = getUsername()
            if (not "error" in name):
                return render_template('admin/deletestaff.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn(), username=name)
            else:
                return render_template('admin/deletestaff.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn())
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

@app.route("/Admin/Deletestaff", methods=['POST', 'GET'])
@app.route("/Admin/deleteStaff", methods=['POST', 'GET'])
@app.route("/Admin/deletestaff", methods=['POST', 'GET'])
@app.route("/admin/DeleteStaff", methods=['POST', 'GET'])
@app.route("/admin/Deletestaff", methods=['POST', 'GET'])
@app.route("/admin/deleteStaff", methods=['POST', 'GET'])
@app.route("/admin/deletestaff", methods=['POST', 'GET'])
def redirectDeleteStaff():
    return redirect("/Admin/DeleteStaff")

@app.route("/Admin/Download", methods=['GET'])
def getPage():
    if request.method == 'GET':
        if checkIsAdmin():
            name = getUsername()
            if (not "error" in name):
                return render_template('admin/download.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn(), username=name)
            else:
                return render_template('admin/download.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn())
        else:
            return redirect("/Home")

@app.route("/Admin/Downloadfile", methods=['GET'])
def xlsxDatabase():
        if request.method =='POST':
            try:
                conn = sql.connect(DATABASE)
                cur = conn.cursor()
                cur.execute("SELECT * FROM tblEvent;")
                dataEvent = cur.fetchall()
                cur.execute("SELECT * FROM tblTournament;")
                dataTour = cur.fetchall()

                #Documentation - http://xlsxwriter.readthedocs.io/
                workbook = xlsxwriter.Workbook('FormInformation.xlsx')
                worksheetEvent = workbook.add_worksheet()
                worksheetTour = workbook.add_worksheet()

                #Formatting
                date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})

                # Set the columns widths.
                worksheetEvent.set_column('B:J', 15)
                worksheetTour.set_column('B:H', 19)

                # Aesthetic
                worksheet1.set_tab_color('red')
                worksheet2.set_tab_color('green')
                bold = workbook.add_format({'bold': True})

                #Headings
                title = "Event form information"
                worksheetEvent.write('B1', title, bold)
                title2 = "Tournament form information"
                worksheetTour.write('B1', title2, bold)

                #Event form table titles
                worksheetEvent.add_table('B2:J11', {'dataEvent': dataEvent,
                                               'columns': [{'header': 'ID'},
                                                           {'header': 'Event name'},
                                                           {'header': 'Event date'},
                                                           {'header': 'Postcode'},
                                                           {'header': 'Event region'},
                                                           {'header': 'Inclusivity'},
                                                           {'header': 'Activity type'},
                                                           {'header': 'Comments'},
                                                           {'header': 'Staff name'},
                                                           ]})
                #Tournament form table titles
                worksheetTour.add_table('B2:H9', {'dataTour': dataTour,
                                               'columns': [{'header': 'ID'},
                                                           {'header': 'Number of people'},
                                                           {'header': 'Age category'},
                                                           {'header': 'Gender ratio'},
                                                           {'header': 'Rugby offer'},
                                                           {'header': 'Staff name'},
                                                           {'header': 'Event ID'},
                                                           ]})
                workbook.close()
            except:
                print("Failed to connect to DB")
                conn.close()
            finally:
                conn.close()
                return render_template('admin/.download.html')

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

@app.route("/Admin/Search", methods = ['GET','POST'])
def moduleSearch():
    if request.method =='GET':
        if checkIsAdmin():
            name = getUsername()
            if (not "error" in name):
                return render_template('admin/search.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn(), username=name)
            else:
                return render_template('admin/search.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn())
        else:
            return redirect("/Home")
    if request.method =='POST':
        try:
            data = ""
            data2 = ""

            event = request.form.get('eventsearch')
            tournament = request.form.get('tournamentsearch')

            conn = sql.connect(DATABASE)
            cur = conn.cursor()

            if (event != None):
                cur.execute("SELECT * FROM tblEvent WHERE eventName=? ;", [event])
                data = cur.fetchall()

            if (tournament != None):
                cur.execute("SELECT * FROM tblTournament WHERE ageCategory=? ;", [tournament])
                data2 = cur.fetchall()

        except:
            print("Failed to connect to DB")
            conn.close()
        finally:
            conn.close()
            return render_template('admin/search.html', data=data, data2=data2)

@app.route("/Admin/search", methods = ['GET'])
@app.route("/Admin/Search", methods = ['GET'])
@app.route("/Admin/search", methods = ['GET'])
def redirectStaffSearch():
    return redirect("/Admin/Search")

@app.route("/Logout", methods=['POST'])
def logout():
    session['username'] = ""
    session['password'] = ""
    session['usertype'] = ""
    session['verified'] = ""
    return "successful"

@app.route("/SW", methods = ['GET'])
def serviceWorker():
    return app.send_static_file('sw.js')

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

@app.before_request
def make_session_permanent():
    session.permanent = True

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(debug=True, ssl_context=('Certificates/cert.pem', 'Certificates/key.pem'))
