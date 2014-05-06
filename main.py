from flask import *
from jinja2 import Template
from flask.ext.sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

appname = "FastRooms"
build = "0.1"


#----DATABASE TABLES----
class Reservation(db.Model):
    __tablename__ = 'res'
    resID = db.Column(db.Integer, primary_key=True)
    guestID = db.Column(db.Integer)
    inDate = db.Column(db.Date)
    outDate = db.Column(db.Date)
    roomNumber = db.Column(db.String)
    #tags = db.relationship('Tag', secondary=enrollment,
    #                            backref=db.backref('courses',lazy='dynamic'))

class Room(db.Model):
    __tablename__ = 'rooms'
    roomNumber = db.Column(db.String, primary_key=True)
    building = db.Column(db.String)
    occupancy = db.Column(db.Integer)
    occupied = db.Column(db.Boolean)
    dirty = db.Column(db.Boolean)

class Guest(db.Model):
	__tablename__ = 'guests'
	guestID = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	address = db.Column(db.String)
	phone = db.Column(db.String)

db.drop_all()
db.create_all()

#class RoomRes(db.Model): #secondary table. Matches rooms with res
#	__tablename__ = 'roomres'
#	roomNumber = db.Column(db.String, db.ForeignKey('rooms.roomNumber'))
#	resID = db.Column(db.Integer, db.ForeignKey('res.resID'))
	
#class GuestRes(db.Model): #secondary table. Matches guests with res
#	__tablename__ = 'guestres'
#	guestID = db.Column(db.Integer, db.ForeignKey('guests.guestID'))
#	resID = db.Column(db.Integer, db.ForeignKey('res.resID'))

#--------



#----TestCases----
def createTestRoom():
	fakeRoom = Room()
	fakeRoom.roomNumber = '100'
	fakeRoom.occupancy = 2
	fakeRoom.occupied = False
	fakeRoom.dirty = True
	db.session.add(fakeRoom)
	db.session.commit()

def createTestRes():
	fakeRes = Reservation()
	fakeRes.roomNumber = '100'
	fakeRes.inDate = datetime.date(2014,6,1)
	db.session.add(fakeRes)
	db.session.commit()
#--------
#----Database Accessors----
def getRoom(roomID):
	#roomID should be str
	result = []
	for rm in db.session.query(Room).filter_by(roomNumber=roomID):
		result.append(rm)
	if (len(result) > 1):
		print('DATA ERROR: Duplicate room numbers from getRoom('+roomID+').')
	return result[0]
	
def getRes(rvtnID):
	#rvtnID should be int
	result = []
	for rv in db.session.query(Reservation).filter_by(resID=rvtnID):
		result.append(rv)
	if (len(result) > 1):
		print('DATA ERROR: Duplicate reservation numbers from getRes('+ str(rvtnID) +').')
	return result[0]

def getDirtyRooms():
	hklist = []
	for r in db.session.query(Room).filter_by(occupied=False,dirty=True):
		hklist.append(r)
	return hklist
		
def getAllResForRoom(room):
	roomNum = room.roomNumber
	rvtns = []
	for rv in db.session.query(Reservation).filter_by(roomNumber=roomNum):
		rvtns.append(rv)
	return rvtns
	
def roomResListing(roomNum):
	rvtns = []
	for rv in getAllResForRoom(getRoom(roomNum)):
		rvtns.append(rv)
	return rvtns

createTestRoom()
createTestRes()

#----PAGES----
@app.route('/res')
def res_page():
	title = "Reservations"
	return render_template('display.html',appname=appname,title=title)

@app.route('/op')
def operations_page():
	title = "Operations"
	content = ""
	for rv in roomResListing('100'):
		 content += str(rv.inDate)
	
	return render_template('display.html',appname=appname,title=title,content=content)

@app.route('/hk')
def housekeeping_page():
	title = "Housekeeping Overview"
	content = "The following rooms need to be cleaned: "
	for r in getDirtyRooms():
		content += r.roomNumber
	return render_template('display.html',appname=appname,title=title,content=content)
	

#Pretty 404 page
@app.errorhandler(404)
def error404(e):
	return render_template('404.html',appname=appname,build=build), 404
	
if __name__ == '__main__':
	app.run()