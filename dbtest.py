from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)



# class Enrollment(db.Model):
#     __table__ = 'enrollment'
#     course_num = db.Column(db.Integer, db.ForeignKey('course.course_num'))
#     student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))


#enrollment = db.Table('enrollment',
#    db.Column('course_num',db.Integer, db.ForeignKey('course.course_num')),
#    db.Column('student_id',db.Integer, db.ForeignKey('student.student_id')),
#    db.Column('grade',db.Integer)
#)


class Reservation(db.Model):
    __tablename__ = 'res'
    rID = db.Column(db.Integer, primary_key=True)
    cID = db.Column(db.Integer)
    inDate = db.Column(db.Date)
    outDate = db.Column(db.Date)
    roomNumber = db.Column(db.String)
    #tags = db.relationship('Tag', secondary=enrollment,
    #                            backref=db.backref('courses',lazy='dynamic'))

class Rooms(db.Model):
    __tablename__ = 'rooms'
    roomNumber = db.Column(db.String, primary_key=True)
    occupancy = db.Column(db.Integer)
    occupied = db.Column(db.Boolean)
    dirty = db.Column(db.Boolean)

class Guests(db.Model):
	__tablename__ = 'guests'
	gID = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	address = db.Column(db.String)
	phone = db.Column(db.String)

db.drop_all()
db.create_all()



#db.session.add_all([r1])

#db.session.add(p1)



db.session.commit()
