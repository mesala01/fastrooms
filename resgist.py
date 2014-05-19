import os
import re
from wtforms import Form, TextField,BooleanField, TextAreaField, SubmitField,PasswordField, validators

from flask import Flask, render_template, request, flash,session, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime




app = Flask(__name__) 
app.secret_key = os.urandom(30)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = \
'sqlite:///' + os.path.join(basedir, 'data.sqlite')

app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)
# Generate a random secret key for the session

appname = "FastRooms"
build = "0.1"

class Guest(db.Model):
    __tablename__ = 'guests'
    guestID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    Username=db.Column(db.String)
    address = db.Column(db.String)
    phone = db.Column(db.String)
    email= db.Column(db.String)
    Password=db.Column(db.String)

    def __init__(self, name=None, email=None):
        self.guestID = guestID
        self.name = name
        form.Username.data,
        self.address = address
        self.phone = phone
        self.email = email
        self.password = password

    def __repr__(self):
        return '<Guest %r>' % (self.name)
    

db.drop_all()
db.create_all()
 
class ContactForm(Form):
  GuestID = TextField("GuestID", [validators.Required("Please enter your GuestID")])
  Name = TextField("Name", [validators.Required("Please enter your full name")])
  Username = TextField("Username", [validators.Required("Please enter your full name")])
  Address = TextField("Address", [validators.Required("Please enter your address")])
  Phone = TextField("Phone", [validators.Required("Please enter a valid phone number")]) 
  Email = TextField('Email Address', [validators.Required("Please enter a valid email addresss"), validators.Email()])
  Password = PasswordField('New Password', [
        validators.Required("Please enter a password"),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
  confirm = PasswordField('Repeat Password',[validators.Required("Please confirm your  password")])
  Submit = SubmitField("Register")
@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
	return render_template('RoomReservation.html', form=form)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
  form = ContactForm()
 
  if request.method == 'POST':
    if form.validate() == False:
      flash('All fields are required.')
      return render_template('contact.html', form=form)
    else:
      user = Guest(form.GuestID.data, form.Name.data,form.Username.data,form.Address.data,form.Phone.data.form.Email.data,form.Password.data)    
      db.add(user)
      return 'Form posted.'
 
  elif request.method == 'GET':
    return render_template('contact.html', form=form)

# def contact():
#   form = ContactForm()
 
#   if request.method == 'POST':
#     if form.validate() == False:
#       flash('All fields are required.')
#       return "Thank you for registering"
      
#     else:
#       user = Guest(form.GuestID.data, form.Name.data,form.Address.data,form.Phone.data.form.Email.data,form.Password.data)
#       db.add(user)
#       return render_template('RoomReservation.html')
#   return render_template('contact.html', form=form)

if __name__ == '__main__': 
    app.run(debug=True)