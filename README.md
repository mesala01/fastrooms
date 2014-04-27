fastrooms
=========

FastRooms hotel/room management system

FastRooms is a hotel/dorm room management system that will keep track of reservations and rooms. There will be three main components to this system:

- Reservations module:
	Form: Users input a date range, (building preference optional), and client information.
	Returns listing of rooms available during the entire date range in the applicable buildings (if selected) with # of beds.
	Select rooms and create reservation
- Today’s operations view:
	Displays a list of rooms that are being checked in today, checking out today, occupied today, and rooms that are empty and clean today
- Housekeeping view:
	Displays a list of rooms that are vacant and dirty
	Housekeeping staff mark rooms as clean as they are completed.

This will be powered by a SQL database containing three tables.
- Reservations
	Reservation ID - int
	Client ID - int
	Check in/out dates - date range
	Room number - int or string, probably string to handle letters, if applicable (ex. D510 or Room 39A)
	Cost? - float/currency
	Paid? - bool
- Rooms
	Room number - String
	Max_occupancy - int
	Next check in date - Date
	Occupied - bool
	Dirty - bool
- Clients
	Client ID - int
	Group name - optional String
	Contact Name - String
	Address - String
	Phone Number - String
