import random
from flask import *
from jinja2 import Template
app = Flask(__name__)
app.debug = True

appname = "FastRooms"




@app.route('/res')
def res_page():
	title = "Reservations"
	return render_template('display.html',appname=appname,title=title)

@app.route('/op')
def operations_page():
	title = "Operations"
	return render_template('display.html',appname=appname,title=title)

@app.route('/hk')
def housekeeping_page():
	title = "Housekeeping Overview"
	return render_template('display.html',appname=appname,title=title)
	