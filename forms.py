from flask_wtf import *
from wtforms import *
from wtforms.validators import *

class addRoom(Form):
    roomNumber = TextField('Room Number', validators=[DataRequired()])
    building = TextField('Building')
    occupancy = TextField('Occupancy', validators=[DataRequired()])

class addBuilding(Form):
    building = TextField('Add building')

class addGuestInfo(Form):
	_guestID = TextField('guestID')
	_name = TextField('name')
	_address = TextField('address')
	_phone = TextField('phone')