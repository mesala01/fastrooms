import os
from flask import Flask, session, request, render_template
#Form, TextField, DateField, IntegerField, SelectField, validitors
#from wtforms.validators import DataRequired

app=Flask(__name__)
# Generate a random secret key for the session
app.secret_key = os.urandom(30)

@app.route('/roomsearch', methods=['GET','POST'])
def roomsearch():
	 # Initialize the errors variable to empty string. We will have the error messages
    # in that variable, if any.
    errors = ''
    if request.method == "GET": # If the request is GET, render the form template.
        return render_template("RoomReservation.html", errors=errors)
    else: 
        # The request is POST with some data, get POST data and validate it.
        # The form data is available in request.form dictionary. Stripping it to remove
        # leading and trailing whitespaces
        checkIn = request.form['checkIn'].strip()
        checkOut = request.form['checkOut'].strip()
        numberOfRooms = request.form.get('numberOfRooms', '')

         # Check if all the fields are non-empty and raise an error otherwise
        if not checkIn or not checkOut or not numberOfRooms:
            errors = "Please enter all the fields."
            
        if not errors:
        	
        	 # If there are no errors, create a dictionary containing all the entered data
            data = {'checkIn' : checkIn,
                    'checkOut' : checkOut,
                    'numberOfRooms' : numberOfRooms
                    }
        return render_template('display.html',appname=appname,title=title, errors=errors)



def roomsAvailable(checkIn=datetime.date.today(),checkOut=datetime.date.today()):
	rez = Reservation.query.filter(not Reservation.inDate.between(checkIn,checkOut).all()
	content
	for r in rez:
		content += str(r.roomNumber)
	










if __name__ == '__main__':
	app.run(debug=True)




         







