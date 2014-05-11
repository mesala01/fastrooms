from flask import *
from jinja2 import Template
from flask.ext.sqlalchemy import SQLAlchemy
import datetime
import config
import forms

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

appname = config.appname
build = config.build


#----DATABASE TABLES----
class Reservation(db.Model):
    __tablename__ = 'res'
    resID = db.Column(db.Integer, primary_key=True)
    guestID = db.Column(db.Integer)
    inDate = db.Column(db.Date)
    outDate = db.Column(db.Date)
    roomNumber = db.Column(db.String)
    status = db.Column(db.String) #prior to check in:"booked"  checkedin: "open"  checked out: "closed"

class Room(db.Model):
    __tablename__ = 'rooms'
    roomNumber = db.Column(db.String, primary_key=True)
    building = db.Column(db.String)
    occupancy = db.Column(db.Integer)
    occupied = db.Column(db.Boolean)
    clean = db.Column(db.Boolean)

class Building(db.Model):
	__tablename__ = 'building'
	name = db.Column(db.String, primary_key=True)

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
	fakeRoom.occupied = True
	fakeRoom.clean = False
	db.session.add(fakeRoom)
	db.session.commit()

def createTestRes():
	fakeRes = Reservation()
	fakeRes.resID = 1
	fakeRes.roomNumber = '100'
	fakeRes.inDate = datetime.date(2014,5,10)
	fakeRes.outDate = datetime.date(2014,5,19)
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

def getRoomNumber(room):
	return room.roomNumber

def getRes(rvtnID):
	#rvtnID should be int
	result = []
	for rv in db.session.query(Reservation).filter_by(resID=rvtnID):
		result.append(rv)
	if (len(result) > 1):
		print('DATA ERROR: Duplicate reservation numbers from getRes('+ str(rvtnID) +').')
	return result[0]
	
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
#--------

#----Reservation date accessors----
def getResDates(rvtn):
	return (rvtn.inDate, rvtn.outDate) # returns (checkin date, checkout date)

def op_checkInOn(d=datetime.date.today()):
	result = []
	for rv in db.session.query(Reservation).filter_by(inDate=d):
		result.append(rv)
	return result
	
def op_checkOutOn(d=datetime.date.today()):
	result = []
	for rv in db.session.query(Reservation).filter_by(outDate=d):
		result.append(rv)
	return result
#--------

#----Rooms Overview----
def op_vacancies(includeRoomsWithIncomingRes=True,includeDirtyRooms=False):
	result = []
	if (includeDirtyRooms and includeRoomsWithIncomingRes):
		for rm in db.session.query(Room).filter_by(occupied=False):
			result.append(rm)
	elif (includeDirtyRooms and (not includeRoomsWithIncomingRes)):
		for rm in db.session.query(Room).filter_by(occupied=False): #ADD NEXT RES PART!!!! nextres!=today
			result.append(rm)
	elif ((not includeDirtyRooms) and includeRoomsWithIncomingRes):
		for rm in db.session.query(Room).filter_by(occupied=False, clean=True): 
			result.append(rm)
	elif ((not includeDirtyRooms) and (not includeRoomsWithIncomingRes)):
		for rm in db.session.query(Room).filter_by(occupied=False, clean=True): #ADD NEXT RES PART!!!! nextres!=today
			result.append(rm)
	return result

def op_occupied():
	result = []
	for rm in db.session.query(Room).filter_by(occupied=True):
		result.append(rm)
	return result
#---------

#----Housekeeping functions----
def getDirtyRooms():
	hklist = []
	for r in db.session.query(Room).filter_by(occupied=False,clean=False):
		hklist.append(r)
	return hklist
def cleaned(room, clean=True):
	#change db value for room.clean to opposite of the clean parameter
	pass
#--------
		

	

createTestRoom()
createTestRes()

#----PAGES----
@app.route('/')
def home_page():
	title = "Home"
	content = 'links here'
	return render_template('display.html',appname=appname,title=title,content=content)


@app.route('/res')
def res_page():
	title = "Reservations"
	return render_template('display.html',appname=appname,title=title)

@app.route('/op')
def operations_page():
	title = "Operations"
	checkin = ""
	for rv in op_checkInOn(datetime.date.today()):
		checkin += '<a href="resinfo/' + str(rv.resID) + '">' + str(rv.resID) + '</a><br />'
		
	checkout = ""
	for rv in op_checkOutOn(datetime.date.today()):
		checkout += '<a href="resinfo/' + str(rv.resID) + '">' + str(rv.resID) + '</a><br />'
 
	vacancies = ""
	for rm in op_vacancies(False,True):
		vacancies += '<a href="roominfo/' + rm.roomNumber + '">' + rm.roomNumber + '</a><br />'
	
	occupied = ""
	for rm in op_occupied():
		occupied += '<a href="roominfo/' + rm.roomNumber + '">' + rm.roomNumber + '</a><br />'
		
	return render_template('operations.html',appname=appname,title=title,
								checkin=checkin,checkout=checkout,vacant=vacancies,occupied=occupied)

@app.route('/addroom')
def add_room_page():
	form = forms.addRoom()
	return render_template('form.html',appname=appname,form=form)

@app.route('/roominfo/<myroom>')
def room_info_page(myroom):
	rm = getRoom(myroom)
	title = "Room " + rm.roomNumber
	return render_template('display.html',appname=appname,title=title)
	
@app.route('/resinfo/<myres>')
def res_info_page(myres):
	rv = getRes(int(myres))
	title = "Reservation Lookup: " + str(rv.resID)
	return render_template('display.html',appname=appname,title=title)
	
@app.route('/hk')
def housekeeping_page():
	title = "Housekeeping Overview"
	content = "The following rooms need to be cleaned: "
	for r in getDirtyRooms():
		content += r.roomNumber
	cleaned(getRoom('100'))
	return render_template('display.html',appname=appname,title=title,content=content)
#--------

#Pretty 404 page
@app.errorhandler(404)
def error404(e):
	return render_template('404.html',appname=appname,build=build), 404
	
if __name__ == '__main__':
	app.run()