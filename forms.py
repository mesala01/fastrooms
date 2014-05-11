from flask_wtf import *
from wtforms import *
from wtforms.validators import *

class addRoom(Form):
    _roomNumber = TextField('roomNumber', validators=[DataRequired()])
    _building = TextField('building', validators=[DataRequired()])
    