import os
from flask import Flask, redirect, request

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

eventDates = []


@app.route("/eventForm", methods = ['POST', 'GET'])
def form():
    global eventDate
    global postcode
    global eventRegion
    global peopleNum
    global tourNum
    global ageRange
    global comments
    print("Processing form")
    if request.method == 'POST':
        eventDate = request.form['eventDate']
        postcode = request.form['postcode']
        eventRegion = request.form['eventRegion']
        peopleNum = request.form['peopleNum']
        tourNum = request.form['tourNum']
        ageRange = request.form['ageRange']
        comments = request.form['comments']
        eventDates.append(eventDate)
        postcodes.append(postcode)
        eventRegions.append(eventRegion)
        peopleNums.append(peopleNum)
        tourNums.append(tourNum)
        ageRanges.append(ageRange)
        comments.append(comments)
    if request.method == 'POST':
