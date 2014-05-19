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
	guestID = TextField('guestID')
	name = TextField('name')
	address = TextField('address')
	phone = TextField('phone')

class registration(Form):
  Name = TextField("Name", [validators.Required("Please enter your full name")])
  #Username = TextField("Username", [validators.Required("Please enter a username")])
  Address = TextField("Address", [validators.Required("Please enter your address")])
  Phone = TextField("Phone", [validators.Required("Please enter a valid phone number")]) 
  Email = TextField('Email Address', [validators.Required("Please enter a valid email addresss"), validators.Email()])
  #Password = PasswordField('New Password', [
   #     validators.Required("Please enter a password"),
    #    validators.EqualTo('confirm', message='Passwords must match')
    #])
  #confirm = PasswordField('Repeat Password',[validators.Required("Please confirm your password")])
  Submit = SubmitField("Register")