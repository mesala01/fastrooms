from flask import *
from jinja2 import Template
from flask.ext.sqlalchemy import SQLAlchemy
import datetime
import config
import forms
import os
import re
import random



app = Flask(__name__)
app.secret_key = os.urandom(30)
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

appname = config.appname
build = config.build
site = config.sitename
@app.context_processor
def inject_globals():
    return dict(
        appname = appname,
		build = build,
		site = site
    )

def getnewID():
	return random.randint(1,5000)

#----DATABASE TABLES----
class Reservation(db.Model):
    __tablename__ = 'res'
    resID = db.Column(db.Integer, primary_key=True)
    guestID = db.Column(db.Integer)
    inDate = db.Column(db.Date)
    outDate = db.Column(db.Date)
    roomNumber = db.Column(db.String)
    numGuests = db.Column(db.Integer)
    inRoom = db.Column(db.Boolean)

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
	email= db.Column(db.String)	
 
@app.route('/drop')
def droptables():
	db.drop_all()
	db.create_all()
	createTestRoom()
	#createTestRes()
	#createTestGuest()
	print("TABLES REBUILT")
	return render_template('basic.html',title="Tables erased.")
#--------

#----TestCases----
def createTestRoom():
	fakeRoom = Room()
	fakeRoom.roomNumber = '100'
	fakeRoom.occupancy = 2
	fakeRoom.occupied = False
	fakeRoom.clean = False
	db.session.add(fakeRoom)
	db.session.commit()

def createTestRes():
	fakeRes = Reservation()
	fakeRes.resID = 1
	fakeRes.guestID = 4
	fakeRes.roomNumber = '100'
	fakeRes.inDate = datetime.date(2014,5,6)
	fakeRes.outDate = datetime.date.today()
	db.session.add(fakeRes)
	db.session.commit()
	
def createTestGuest():
	fakeGuest = Guest()
	fakeGuest.guestID = 4
	fakeGuest.name = "Steve"
	fakeGuest.address = "123 Street"
	fakeGuest.phone = "8472751128"
	db.session.add(fakeGuest)
	db.session.commit()
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

def addRes(gID,inD,outD,room,guests):
	r=Reservation()
	r.resID=getnewID()
	r.guestID=gID
	r.inDate=inD
	r.outDate=outD
	r.roomNumber=room
	r.numGuests=guests
	r.inRoom=False
	db.session.add(r)
	db.session.commit()
	

def addGuest(ID,name,address,phone,email):
	g = Guest()
	g.guestID = ID
	g.name = name
	g.address = address
	g.phone = phone
	g.email = email
	db.session.add(g)
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
	
def getGuest(guestID_Str):
	gID = int(guestID_Str)
	result = []
	for g in db.session.query(Guest).filter_by(guestID=gID):
		result.append(g)
	if (len(result) > 1):
		print('DATA ERROR: Duplicate guestID from getGuest('+ guestID_Str +').')
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
	for rv in db.session.query(Reservation).filter_by(inDate=d,inRoom=False):
		reservations.append(rv)
	return reservations
	
def op_checkOutOn(d=datetime.date.today()):
	reservations = []
	for rv in db.session.query(Reservation).filter_by(outDate=d,inRoom=True):
		reservations.append(rv)
	return reservations
	
	
def daterange(start, end):
    r = (end-start).days
    return [start+datetime.timedelta(days=i) for i in range(r)]
def getAvailableRoomsBetween(checkIn,checkOut,guests):
	allRooms = Room.query.filter().all()
	content = ""
	goodRoom = []
	for rm in allRooms:
		conflict = False
		if rm.occupancy >= guests:
			for res in getAllResForRoom(rm):
				resRange = daterange(res.inDate, res.outDate)
				testRange = daterange(checkIn, checkOut)
				for testDate in testRange:
					if testDate in resRange:
						conflict = True
			if (conflict == False and rm.occupancy >= guests):
				goodRoom.append(rm)
				print("room is good")
						
	return goodRoom #returns room objects
#--------

#----Reservation Checkin/checkout----
def checkIn(res):
	res.inRoom = True
	occupied(getRoom(res.roomNumber))

def checkOut(res):
	res.inRoom = False
	vacant(getRoom(res.roomNumber))

@app.route('/res/<resID>/in')
def checkIn_page(resID):
	checkIn(getRes(int(resID)))
	return redirect(request.referrer or '/op')
	
@app.route('/res/<resID>/out')
def checkOut_page(resID):
	checkOut(getRes(int(resID)))
	return redirect(request.referrer or '/op')
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
	return redirect(request.referrer or '/op')
@app.route('/room/<roomNumber>/vacant')
def manuallyVacant_page(roomNumber):
	vacant(getRoom(roomNumber))
	return redirect(request.referrer or '/op')
	
	
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
	return redirect(request.referrer or '/op')

@app.route('/room/<roomNumber>/dirty')
def dirty_page(roomNumber):
	room = getRoom(roomNumber)
	cleaned(room,False)
	return redirect(request.referrer or '/op')
#--------
		



#----PAGES----
@app.route('/', methods=['GET','POST'])
def home_page():
	title = "Home"
	return render_template('basic.html',title=title,content='Welcome to FastRooms \
			 <li><a href="/roomsearch">Create Reservation</a></li> \
            <li><a href="/op">Operations</a></li>\
            <li><a href="/hk">Housekeeping</a></li>\
            <li><a href="/config">Configuration</a></li>' )


@app.route('/res')
def res_page():
	title = "Reservations"
	return render_template('basic.html',title=title,content=content)

@app.route('/op')
def operations_page():
	title = "Operations"
	checkin = ""
	for rv in op_checkInOn(datetime.date.today()):
		checkin += '<a href="res/' + str(rv.resID) + '">' + str(rv.resID) + " - " + getGuest(rv.guestID).name + '</a><br />'
		
	checkout = ""
	for rv in op_checkOutOn(datetime.date.today()):
		checkout += '<a href="res/' + str(rv.resID) + '">' + str(rv.resID) + " - " + getGuest(str(rv.guestID)).name + '</a><br />'
 
	vacancies = ""
	for rm in op_vacancies(False,True):
		vacancies += '<a href="room/' + rm.roomNumber + '">' + rm.roomNumber + '</a><br />'
	
	occupied = ""
	for rm in op_occupied():
		occupied += '<a href="room/' + rm.roomNumber + '">' + rm.roomNumber + '</a><br />'
		
	return render_template('operations.html',title=title,
								checkin=checkin,checkout=checkout,vacant=vacancies,occupied=occupied)

@app.route('/room', methods=['GET','POST'])
def room_page():
	if request.method == 'POST':
		addRoom(request.form['roomNumber'],request.form['building'],request.form['occupancy'])
		
	form = forms.addRoom()
	rooms = db.session.query(Room)
	return render_template('room.html',form=form,rooms=rooms)

@app.route('/building', methods=['GET', 'POST'])
def building_page():
	if request.method == 'POST':
		addBuilding(request.form['building'])
	form = forms.addBuilding()
	buildings = db.session.query(Building)
	return render_template('building.html',form=form,buildings=buildings)

@app.route('/addguest')
def add_guest_page():
	pass

@app.route('/room/<myroom>')
def room_info_page(myroom):
	rm = getRoom(myroom)
	title = "Room " + str(rm.roomNumber)
	return render_template('roominfo.html',title=title,r=rm)
	
@app.route('/res/<myres>')
def res_info_page(myres):
	rv = getRes(int(myres))
	g = getGuest(rv.guestID)
	rm = getRoom(rv.roomNumber)
	title = "Reservation Lookup: " + str(rv.resID)
	return render_template('resinfo.html',title=title,res=rv,g=g,rm=rm)
	
@app.route('/hk')
def housekeeping_page():
	title = "Housekeeping Overview"
	return render_template('hk.html',title=title,rooms=getDirtyRooms())
	
	
@app.route('/roomsearch', methods=['GET','POST'])
def roomsearch():
	title = "Room Availability Search"
	errors = ''
	if request.method == "POST":
		checkInS = request.form['checkIn']
		checkOutS = request.form['checkOut']
		numberOfGuests = request.form['numberOfGuests']
		if not checkInS or not checkOutS or not numberOfGuests:
			errors = "Please enter all the fields."
		if not errors:
			checkInD = datetime.datetime.strptime(checkInS,'%m/%d/%Y').date()
			checkOutD = datetime.datetime.strptime(checkOutS,'%m/%d/%Y').date()
			numGuests = int(numberOfGuests)
			print ('Guests' + str(numGuests))
			rooms = getAvailableRoomsBetween(checkInD,checkOutD,numGuests)
			print(len(rooms))
			return render_template('RoomReservation.html',title=title,errors=errors,rooms=rooms,
										inS=checkInS,outS=checkOutS,guestsS=numberOfGuests)
		return render_template('RoomReservation.html',title=title,errors=errors)
	return render_template('RoomReservation.html',title=title)

@app.route('/register', methods=['GET', 'POST'])
def contact():
	form = forms.registration()
	if request.method == 'POST':
		gID=getnewID()
		email = request.form['Email']
		if len(email) > 7:
			if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
		
				addGuest(gID,
					request.form['Name'],
					request.form['Address'],
					request.form['Phone'],
					request.form['Email']
				)
				inD = datetime.datetime.strptime(request.form['inDateS'],'%m/%d/%Y').date()
				outD = datetime.datetime.strptime(request.form['outDateS'],'%m/%d/%Y').date()
				addRes(gID,
					inD,outD,
					request.form['roomNum'],
					request.form['numGuestsS']
					)
				return render_template('basic.html',content="Reservation added")
			elif request.method == 'GET':
				return error404(404)
		return render_template('basic.html',content="Email not valid")
@app.route('/createres', methods=['POST'])
def createResPage():
	form = forms.registration()
	rn = request.form['myRoomNumber']
	inS= request.form['myInS']
	outS = request.form['myOutS']
	numG = request.form['myGuestsS']
	# send hidden form data to contact.html.
	# Contact then sends it along to /register and that part does all the work
	return render_template('contact.html',form=form,rn=rn,inS=inS,outS=outS,numG=numG)

#--------

@app.route('/config')
def config_page():
	content = '<a href="/room">Rooms</a><br />'
	content += '<a href="/building">Building</a><br />'
	content += '<br /><em><a href="/drop">Drop and rebuild database (CAUTION: Erases all data)</a></em><br />'
	return render_template('basic.html',title="Configuration",content=content)


#-----------------------------------------------------------
#Pretty 404 page
@app.errorhandler(404)
def error404(e):
	desc="It looks like the page you were looking for doesn't exist or has been moved.<br />Sorry about that!"
	head="404 - Page Not Found"
	return render_template('404.html',desc=desc,head=head), 404

@app.errorhandler(500)
def error500(e):
	desc="Something major has gone wrong. You should check your log files. 500 INTERNAL SERVER ERROR"
	head="500 - Database error"
	return render_template('404.html',desc=desc,head=head), 500
	
if __name__ == '__main__':
	app.run()