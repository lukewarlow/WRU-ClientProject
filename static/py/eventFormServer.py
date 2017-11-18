import os
from flask import Flask, redirect, request

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

eventDates = []


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
