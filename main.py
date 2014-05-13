from flask import *
from jinja2 import Template
from flask.ext.sqlalchemy import SQLAlchemy
import datetime
import config
import forms
import os

app = Flask(__name__)
app.secret_key = os.urandom(30)
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
 
@app.route('/drop')
def droptables():
	db.drop_all()
	db.create_all()
	createTestRoom()
	createTestRes()
	createTestGuest()
	return render_template('display.html',title="Tables erased.")

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
	fakeRes.inDate = datetime.date(2014,4,12)
	fakeRes.outDate = datetime.date.today()
	db.session.add(fakeRes)
	db.session.commit()
	
def createTestGuest():
	pass
#--------

#----Database Adders----
def addBuilding(name):
	b = Building()
	b.name = name
	db.session.add(b)
	db.session.commit()

def addRoom(num,bldg,occ):
	r = Room()
	r.roomNumber = num
	r.building = bldg
	try:
		r.occupancy = int(occ)
	except:
		pass
	if not r.occupancy:
		r.occupancy = 4
	r.occupied = False
	r.clean = False
	db.session.add(r)
	db.session.commit() 
#-------

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
	
def getAllResForRoom(room):
	roomNum = room.roomNumber
	rvtns = []
	for rv in db.session.query(Reservation).filter_by(roomNumber=roomNum):
		rvtns.append(rv)
	return rvtns
#--------

#----Reservation date accessors----
def getResDates(rvtn):
	return (rvtn.inDate, rvtn.outDate) # returns (checkin date, checkout date)

def op_checkInOn(d=datetime.date.today()):
	reservations = []
	for rv in db.session.query(Reservation).filter_by(inDate=d):
		reservations.append(rv)
	return reservations
	
def op_checkOutOn(d=datetime.date.today()):
	reservations = []
	for rv in db.session.query(Reservation).filter_by(outDate=d):
		reservations.append(rv)
	return reservations
	
	
def daterange(start, end):
    r = (end-start).days
    return [start+datetime.timedelta(days=i) for i in range(r)]
def getAvailableRoomsBetween(checkIn=datetime.date.today(),checkOut=datetime.date(2014,5,16)):
	allRooms = Room.query.filter().all()
	content = ""
	goodRoom = []
	for rm in allRooms:
		conflict = False
		for res in getAllResForRoom(rm):
			resRange = daterange(res.inDate, res.outDate)
			testRange = daterange(checkIn, checkOut)
			for testDate in testRange:
				if testDate in resRange:
					conflict = True
		if (conflict == False):
			goodRoom.append(rm)
						
	return goodRoom #returns room objects
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

def occupied(room):
	room.occupied = True
	cleaned(room,False)
	db.session.commit()
	
def vacant(room):
	room.occupied = False
	db.session.commit()

@app.route('/room/<roomNumber>/occupied')
def manuallyOccupied_page(roomNumber):
	occupied(getRoom(roomNumber))
	return redirect('/op')
@app.route('/room/<roomNumber>/vacant')
def manuallyVacant_page(roomNumber):
	vacant(getRoom(roomNumber))
	return redirect('/op')
	
	
#---------

#----Housekeeping functions----
def getDirtyRooms():
	hklist = []
	for r in db.session.query(Room).filter_by(occupied=False,clean=False):
		hklist.append(r)
	return hklist
	
def cleaned(room, clean=True):
	#change db value for room.clean to opposite of the clean parameter
	room.clean=clean
	db.session.commit()
@app.route('/room/<roomNumber>/clean')
def clean_page(roomNumber):
	room = getRoom(roomNumber)
	cleaned(room)
	return redirect('/hk')

@app.route('/room/<roomNumber>/dirty')
def dirty_page(roomNumber):
	room = getRoom(roomNumber)
	cleaned(room,False)
	return redirect('/hk')
#--------
		



#----PAGES----
@app.route('/', methods=['GET','POST'])
def home_page():
	title = "Home"
	content = 'links here'
	return render_template('display.html',appname=appname,title=title,content=content)


@app.route('/res')
def res_page():
	title = "Reservations"
	return render_template('display.html',appname=appname,title=title,content=content)

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
		vacancies += '<a href="room/' + rm.roomNumber + '">' + rm.roomNumber + '</a><br />'
	
	occupied = ""
	for rm in op_occupied():
		occupied += '<a href="room/' + rm.roomNumber + '">' + rm.roomNumber + '</a><br />'
		
	return render_template('operations.html',appname=appname,title=title,
								checkin=checkin,checkout=checkout,vacant=vacancies,occupied=occupied)

@app.route('/room', methods=['GET','POST'])
def room_page():
	if request.method == 'POST':
		addRoom(request.form['roomNumber'],request.form['building'],request.form['occupancy'])
		
	form = forms.addRoom()
	rooms = db.session.query(Room)
	return render_template('room.html',appname=appname,form=form,rooms=rooms)

@app.route('/building', methods=['GET', 'POST'])
def building_page():
	if request.method == 'POST':
		addBuilding(request.form['building'])
	form = forms.addBuilding()
	buildings = db.session.query(Building)
	return render_template('building.html',appname=appname,form=form,buildings=buildings)

@app.route('/addguest')
def add_guest_page():
	pass


@app.route('/room/<myroom>')
def room_info_page(myroom):
	rm = getRoom(myroom)
	title = "Room " + str(rm.roomNumber)
	content = "Building: " + str(rm.building) + "<br />"
	content += "Occupancy: " + str(rm.occupancy) + "<br />"
	content += "<hr />"
	if (rm.occupied):
		content += "Occupied <br />"
	else:
		content += "Vacant <br />"
	if (rm.clean):
		content += "Clean <br />"
	else:
		content += "Dirty <br />"
	return render_template('display.html',appname=appname,title=title,content=content)
	
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
		content += "<br /> <a href=\"/room/" + r.roomNumber +"/clean\">" +r.roomNumber
	return render_template('display.html',appname=appname,title=title,content=content)
	
	
@app.route('/roomsearch', methods=['GET','POST'])
def roomsearch():
	title = "Room Availability Search"
	errors = ''
	if request.method == "POST":
		checkInS = request.form['checkIn']
		checkOutS = request.form['checkOut']
		numberOfRooms = request.form['numberOfRooms']
		if not checkInS or not checkOutS or not numberOfRooms:
			errors = "Please enter all the fields."
		if not errors:
			checkInD = datetime.datetime.strptime(checkInS,'%Y/%m/%d').date()
			checkOutD = datetime.datetime.strptime(checkOutS,'%Y/%m/%d').date()
			rooms = getAvailableRoomsBetween(checkInD,checkOutD)
			return render_template('RoomReservation.html',appname=appname,title=title,errors=errors,rooms=rooms)
		return render_template('RoomReservation.html',appname=appname,title=title,errors=errors)
	return render_template('RoomReservation.html',appname=appname,title=title)

#--------

@app.route('/config')
def config_page():
	content = '<a href="/room">Rooms</a><br />'
	content += '<a href="/building">Building</a><br />'
	content += '<br /><em><a href="/drop">Drop and rebuild database (CAUTION: Erases all data)</a></em><br />'
	return render_template('display.html',appname=appname,title="Configuration",content=content)


#Pretty 404 page
@app.errorhandler(404)
def error404(e):
	desc="It looks like the page you were looking for doesn't exist or has been moved.<br />Sorry about that!"
	head="404 - Page Not Found"
	return render_template('404.html',appname=appname,build=build,desc=desc,head=head), 404

@app.errorhandler(500)
def error500(e):
	desc="Something major has gone wrong. You should check your log files. 500 INTERNAL SERVER ERROR"
	head="500 - Database error"
	return render_template('404.html',appname=appname,build=build,desc=desc,head=head), 500
	
if __name__ == '__main__':
	app.run()