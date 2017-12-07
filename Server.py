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

@app.route("/", methods=['GET'])
@app.route("/home", methods=['GET'])
@app.route("/index", methods=['GET'])
@app.route("/Index", methods=['GET'])
def redirectHome():
    return redirect("/Home")

@app.route("/Home", methods=['GET'])
def home():
    if request.method == 'GET':
        name = getUsernameFromSession()
        if (not "error" in name):
            return render_template('index.html', title="Homepage", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn(), username=name)
        else:
            return render_template('index.html', title="Homepage", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn())

@app.route("/Staff/Verify", methods=['GET'])
def redirectFalseVerify():
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
                if (userexists is not False):
                    check = checkLogin(username, password)
                    if (check == False):
                        print("Failed to log in, incorrect password.")
                        return "Error: incorrect password provided."
                    else:
                        msg = updateTable("UPDATE tblStaff SET password=?, verified='True' WHERE username=?", [newpassword, username])
                        if ("Error" not in msg):
                            session['username'] = check.split(":")[1]
                            session['usertype'] = check.split(":")[2]
                            session['verified'] = "True"
                            print(str(username) + " has verified.")

                            data = getDetailsFromUsername(username)
                            message = """\
                            <p>
                                Hi {} {},<br>
                                Your account has been verified.<br>
                                You will now have access to the WRU event tool.
                            </p>""".format(data[0], data[1])
                            sendEmail(data[2], "Account verified", message)
                        return msg
                else:
                    return "unsuccessful user doesn't exist, contact system admin."
            else:
                return "unsuccessful entered username doesn't match, the one linked to your email."

@app.route("/Staff/login", methods=['GET'])
@app.route("/staff/Login", methods=['GET'])
@app.route("/staff/login", methods=['GET'])
def redirectLogin():
    return redirect("/Staff/Login")

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
                return "Error: incorrect password."
            elif (check.split(":")[3] == "True"):
                session['username'] = check.split(":")[1]
                session['usertype'] = check.split(":")[2]
                session['verified'] = True
                print(str(username) + " has logged in")
                return "Log in successful."
            else:
                return "Error: please verify account through the link in email."
        else:
            print("Failed to log in, incorrect username or use.")
            return "Error: user not found"
    else:
        return render_template('staff/login.html', title="Log In", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn())

@app.route("/Staff/account", methods=['GET'])
@app.route("/staff/Account", methods=['GET'])
@app.route("/staff/account", methods=['GET'])
def redirectAccount():
    return redirect("/Staff/Account")

# staff page
@app.route('/Staff/Account', methods=['POST', 'GET'])
def staffAccount():
    if request.method == 'POST':
        username = getUsernameFromSession()
        password = request.form.get('password', default="Error")
        newpassword = request.form.get('newpassword', default="Error")
        newemail = request.form.get('newemail', default="Error")

        if (checkLogin(username, password)):
            data = getDetailsFromUsername(username)
            if (newpassword is not "Error"):
                msg = updateTable("UPDATE tblStaff SET password=?;", [encrypt(newpassword)])
                if ("Error" not in msg):
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
                return msg
            elif (newemail is not "Error"):
                if (verifyEmail(newemail)):
                    if (not checkIfEmailIsUsed(newemail)):
                        msg = updateTable("UPDATE tblStaff SET email=?;", [newemail])
                        if ("Error" not in msg):
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
                            print("{}'s email updated successfully".format(username))
                        else:
                            msg = "Error: email already used"
                    return msg
                else:
                    return "Error: invalid email."
            else:
                return "Error"
        else:
            return "Error: incorrect password."
    else:
        if (checkIsLoggedIn()):
            name = getUsernameFromSession()
            return render_template('staff/account.html', title="Account", admin=checkIsAdmin(), isloggedin=True, username=name)
        else:
            return redirect("/Home")

@app.route("/Staff/Loginissues", methods=['GET'])
@app.route("/Staff/loginIssues", methods=['GET'])
@app.route("/Staff/loginissues", methods=['GET'])
@app.route("/staff/LoginIssues", methods=['GET'])
@app.route("/staff/loginIssues", methods=['GET'])
@app.route("/staff/loginissues", methods=['GET'])
def redirectLoginIssues():
    return redirect("/Staff/LoginIssues")

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
                msg = updateTable("UPDATE tblStaff SET verified='False', password=? WHERE username=?", [randVerificationKey, username])
                if ("Error" not in msg):
                    pass
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
                    return "Password reset successful check emails."
                else:
                    return msg
            else:
                return "Error: email not associated with an account."
        else:
            return "Error"

def checkIfEmailIsUsed(email):
    data = selectFromDatabaseTable("SELECT firstName, surname, username FROM tblStaff WHERE email=?;", [email])

    if (type(data) is not type(None)):
        return "True:{}:{}:{}".format(data[0], data[1], data[2])
    else:
        return False

@app.route("/Staff/Eventform", methods=['GET'])
@app.route("/Staff/eventForm", methods=['GET'])
@app.route("/Staff/eventform", methods=['GET'])
@app.route("/staff/EventForm", methods=['GET'])
@app.route("/staff/Eventform", methods=['GET'])
@app.route("/staff/eventForm", methods=['GET'])
@app.route("/staff/eventform", methods=['GET'])
def redirectEvent():
    return redirect("/Staff/EventForm")

@app.route("/Staff/EventForm", methods = ['POST', 'GET'])
def eventForm():
    if request.method == 'GET':
        now = datetime.datetime.now()
        name = getUsernameFromSession()
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
        if "error" not in msg:
            msg = insertIntoDatabaseTable("INSERT INTO tblEvent ('eventName',\
            'eventStartDate', 'eventEndDate', 'postcode', 'eventRegion',\
            'inclusivity', 'activityTypes', 'comments', 'staffName')\
            VALUES (?,?,?,?,?,?,?,?,?)", (eventName, eventStartDate,\
             eventEndDate, postcode, eventRegion, inclusivity, activityTypes,\
             comments, staffName))
        return msg

@app.route("/Staff/Tournamentform", methods=['GET'])
@app.route("/Staff/tournamentForm", methods=['GET'])
@app.route("/Staff/tournamentform", methods=['GET'])
@app.route("/staff/TournamentForm", methods=['GET'])
@app.route("/staff/Tournamentform", methods=['GET'])
@app.route("/staff/tournamentForm", methods=['GET'])
@app.route("/staff/tournamentform", methods=['GET'])
def redirectTournament():
    return redirect("/Staff/TournamentForm")

@app.route("/Staff/TournamentForm", methods = ['POST', 'GET'])
def tournamentForm():
    if request.method == 'GET':
        #https://www.saltycrane.com/blog/2008/06/how-to-get-current-date-and-time-in/ Date Accessed: 29/11/2017
        now = datetime.datetime.now()
        name = getUsernameFromSession()
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
        if eventName is "":
            data = selectFromDatabaseTable("SELECT ID FROM tblEvent WHERE eventStartDate=? AND postcode=?;", [eventStartDate, postcode])
        elif postcode is "":
            data = selectFromDatabaseTable("SELECT ID FROM tblEvent WHERE eventName=? AND eventStartDate=?;", [eventName, eventStartDate])
        else:
            data = selectFromDatabaseTable("SELECT ID FROM tblEvent WHERE eventName=? AND eventStartDate=? AND postcode=?;", [eventName, eventStartDate, postcode])

        if data:
            eventID = data[0]
            eventExists = True
        if eventExists == True:
            if 'username' in session:
                username = escape(session['username'])
                if username == "":
                    msg = "error not logged in?"
                else:
                    staffName = username
            else:
                msg = "error not logged in?"
            if ("error" not in msg):
                msg = insertIntoDatabaseTable("INSERT INTO tblTournament\
                ('peopleNum', 'ageCategory', 'rugbyOffer', 'genderRatio',\
                'staffName', 'eventID') VALUES (?,?,?,?,?,?)",(peopleNum,\
                 ageCategory, genderRatio, rugbyOffer, staffName, eventID))
            return msg
        else:
            print("Error: event not found")
            return "Event not found, check event data"

@app.route("/Admin/Addstaff", methods=['POST', 'GET'])
@app.route("/Admin/addStaff", methods=['POST', 'GET'])
@app.route("/Admin/addstaff", methods=['POST', 'GET'])
@app.route("/admin/AddStaff", methods=['POST', 'GET'])
@app.route("/admin/Addstaff", methods=['POST', 'GET'])
@app.route("/admin/addStaff", methods=['POST', 'GET'])
@app.route("/admin/addstaff", methods=['POST', 'GET'])
def redirectAddStaff():
    return redirect("/Admin/AddStaff")

@app.route("/Admin/AddStaff", methods=['POST', 'GET'])
def addStaff():
    if request.method == 'GET':
        if checkIsAdmin():
            name = getUsernameFromSession()
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
        if (response != False):
            username = enteredusername + response.split(":")[1]
        else:
            username = enteredusername

        password = encrypt(request.form.get('password', default="Error"))
        email = request.form.get('email', default="Error").lower()
        usertype = request.form.get('usertype', default="Error")
        organisation = request.form.get('organisation', default="Error")

        print("Adding staff member: " + username)
        if (verifyEmail(email)):
            if (not checkIfEmailIsUsed(email)):
                name = ""
                msg = ""
                if 'username' in session:
                    name = escape(session['username'])
                    if name == "":
                        msg = "error not logged in?"
                    else:
                        adminName = name
                else:
                    msg = "error not logged in?"
                if msg == "":
                    msg = insertIntoDatabaseTable("INSERT INTO tblStaff ('username',\
                    'password', 'email', 'usertype', 'firstname', 'surname',\
                    'organisation', 'verified', 'adminName') VALUES (?,?,?,?,?,?,?,?,?)",\
                    (username, password, email, usertype, firstName, surname,\
                    organisation, "False", adminName))

                    if "successful" in msg:
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
            else:
                msg = "Error: email already used."
            return msg
        else:
            return "Error: Email address not found"

@app.route("/Admin/Deletestaff", methods=['GET'])
@app.route("/Admin/deleteStaff", methods=['GET'])
@app.route("/Admin/deletestaff", methods=['GET'])
@app.route("/admin/DeleteStaff", methods=['GET'])
@app.route("/admin/Deletestaff", methods=['GET'])
@app.route("/admin/deleteStaff", methods=['GET'])
@app.route("/admin/deletestaff", methods=['GET'])
def redirectDeleteStaff():
    return redirect("/Admin/DeleteStaff")

@app.route("/Admin/DeleteStaff", methods=['POST', 'GET'])
def deleteStaff():
    if request.method == 'GET':
        if checkIsAdmin():
            name = getUsernameFromSession()
            if (not "error" in name):
                return render_template('admin/deletestaff.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn(), username=name)
            else:
                return render_template('admin/deletestaff.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn())
        else:
            return redirect("/Home")
    elif request.method == 'POST':
        otherusername = request.form.get('username', default="Error")
        otherusername = otherusername.lower()
        password = request.form.get('password', default="Error")
        if (otherusername == getUsernameFromSession()):
            msg = "Can't delete self"
        elif (checkLogin(getUsernameFromSession(), password)):
            data = getDetailsFromUsername(otherusername)
            msg = deleteFromTable("DELETE FROM tblStaff WHERE username=?;", [otherusername])
            if (not "Error" in msg):
                msg = "User {} successfully deleted".format(otherusername)
                print("Deleted staff member:" + otherusername)
                message = """\
                <p>
                    Hi {} {},<br>
                    You've been removed from the WRU staff database.<br>
                    You will no longer have access to the tool.
                </p>""".format(data[0], data[1])
                sendEmail(data[2], "Account Deleted", message)
        else:
            msg = "Error: Incorrect password"
        return msg

@app.route("/Admin/download", methods=['GET'])
@app.route("/admin/Download", methods=['GET'])
@app.route("/admin/download", methods=['GET'])
def redirectAdminDownload():
    return redirect("/Admin/Download")

@app.route("/Admin/Download", methods=['GET'])
def getPage():
    if request.method == 'GET':
        if checkIsAdmin():
            name = getUsernameFromSession()
            if (not "error" in name):
                return render_template('admin/download.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn(), username=name)
            else:
                return render_template('admin/download.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn())
        else:
            return redirect("/Home")

@app.route("/Admin/Downloadfile", methods=['POST'])
def xlsxDatabase():
        if request.method =='POST':
            try:
                headerEvent = ['ID', 'Event name', 'Event date', 'postcode', \
                'Inclusivity', 'Activity type', 'Comments', 'Staff name']
                headerTour = ['ID', 'Number of  people', 'Age category' \
                'Gender ratio', 'Rugby offer', 'Staff name', 'Event ID']

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
                worksheetEvent.set_tab_color('red')
                worksheetTour.set_tab_color('green')
                bold = workbook.add_format({'bold': True})

                #Headings
                title = "Event form information"
                worksheetEvent.write('B1', title, bold)
                title2 = "Tournament form information"
                worksheetTour.write('B1', title2, bold)

                row = 1
                col = 1

                for item in headerEvent:
                    worksheetEvent.write(row, col, item, bold)
                    col += 1
                for item in headerTour:
                    worksheetTour.write(row, col, item, bold)
                    col += 1

                row = 2
                col = 1
                for item in dataEvent:
                    worksheetEvent.write_row(row, col, item)
                    row += 1
                for item in dataTour:
                    worksheetTour.write_row(row, col, item)
                    row += 1

                workbook.close()
            except:
                print("Failed to connect to DB")
                conn.close()
            finally:
                conn.close()
                return render_template('admin/download.html')

@app.route("/Admin/search", methods=['GET'])
@app.route("/admin/Search", methods=['GET'])
@app.route("/admin/search", methods=['GET'])
def redirectAdminSearch():
    return redirect("/Admin/Search")

@app.route("/Admin/Search", methods = ['GET','POST'])
def moduleSearch():
    if request.method =='GET':
        if checkIsAdmin():
            name = getUsernameFromSession()
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

@app.route("/Logout", methods=['POST'])
def logout():
    session.clear()
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

def getDetailsFromUsername(username):
    return selectFromDatabaseTable("SELECT firstname, surname, email FROM tblStaff WHERE username=?;", [username])

def checkIfUserExists(username):
    data = selectFromDatabaseTable("SELECT Count(ID) FROM tblStaff WHERE username=?;", [username])[0]
    if (data > 0):
        return "True:{}".format(data + 1)
    else:
        return False

def selectFromDatabaseTable(sqlStatement, arrayOfTerms=None):
    try:
        conn = sql.connect(DATABASE)
        cur = conn.cursor()
        cur.execute(sqlStatement, arrayOfTerms)
        data = cur.fetchone()
    except sql.ProgrammingError as e:
        print("Error in select operation," + str(e))
        data = "Error"
    finally:
        conn.close()
        return data

def insertIntoDatabaseTable(sqlStatement, tupleOfTerms):
    try:
        conn = sql.connect(DATABASE)
        cur = conn.cursor()
        cur.execute(sqlStatement, tupleOfTerms)
        conn.commit()
        msg = "Record successfully added."
    except sql.ProgrammingError as e:
        conn.rollback()
        msg = "Error in insert operation: " + str(e)
        print(msg)
    finally:
        conn.close()
        return msg

def updateTable(sqlStatement, arrayOfTerms):
    try:
        conn = sql.connect(DATABASE)
        cur = conn.cursor()
        cur.execute(sqlStatement, arrayOfTerms)
        conn.commit()
        msg = "Record successfully updated."
    except sql.ProgrammingError as e:
        conn.rollback()
        msg = "Error in update operation" + str(e)
        print(msg)
    finally:
        conn.close()
        return msg

def deleteFromTable(sqlStatement, arrayOfTerms):
    try:
        conn = sql.connect(DATABASE)
        cur = conn.cursor()
        cur.execute(sqlStatement, arrayOfTerms);
        conn.commit()
        msg = "Record successfully deleted."
    except sql.ProgrammingError as e:
        conn.rollback()
        msg = "Error in delete operation" + str(e)
        print(msg)
    finally:
        conn.close()
        return msg

#http://dustwell.com/how-to-handle-passwords-bcrypt.html Date Accessed 20/11/2017
def encrypt(data, salt=gensalt()):
    hashed = hashpw(bytes(data, 'utf-8'), salt)
    return hashed

def getUsernameFromSession():
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

def checkLogin(username, password):
    data = selectFromDatabaseTable("SELECT username, password, usertype, verified FROM tblStaff WHERE username=?;", [username])
    if (data is not "Error"):
        user = data[0]
        pw = data[1]
        usertype = data[2]
        verified = data[3]
        if (len(pw) is not 8):
            if (encrypt(password, pw) == pw):
                return "True:{}:{}:{}".format(user, usertype, verified)
            else:
                return False;
        elif (password == pw):
            return "True:{}:{}:{}".format(user, usertype, verified)
        else:
            return False
    else:
        return False

@app.before_request
def make_session_permanent():
    session.permanent = True

if __name__ == "__main__":
    app.run(debug=True, port=80)
    # app.run(debug=True, ssl_context=('Certificates/cert.pem', 'Certificates/key.pem'))
