# Timetabling System Server
# Neeraj Chatlani and D.S. Myers, 2016

from flask import Flask
from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy
import json
import os

app = Flask(__name__)

# Set up database connection
# In the sqlite location string, three slashes (///) indicates a relative path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/schedule.db'
db = SQLAlchemy(app)

# Each database table is described by a class that extends db.Model

# Schema for Timeslots
#
# Fields:
#   days -- string, e.g. "MWF"
#   start_time -- 
#   end_time --
class Timeslot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    days = db.Column(db.String(8))
    times = db.Column(db.String(30))
    
    def __init__(self, days = '', times = ''):
        self.days = days
        self.times = times
        
    def __repr__(self):
        return 'null'
    
    #-- WRITE RETURN FOR THIS
    

# Schema for Rooms
#
# Fields:
#   building: string
#   room_number: string
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    building = db.Column(db.String(40))
    room_number = db.Column(db.String(10))
    
    def __init__(self, building = '', room_number = ''):
        self.building = building
        self.room_number = room_number
        
    def __repr__(self):
        return '<Room %r>' % (self.building + self.room_number)

    #-- FINISHED


# Schema for Instructors
#
# Table holds list of all instructors
class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    
    def __init__(self, name = ''):
        self.name = name

    def __repr__(self):
        return '<Instructor %r>' % self.name
        


# Schema for Acceptable rooms
#
# Fields:
#   section_name
#   room: e.g. "BUSH 301"
#   building
#   room_number
class AcceptableRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(80))
    room = db.Column(db.String(80))
    building = db.Column(db.String(40))
    room_number = db.Column(db.String(10))
        
    def __init__(self, section_name = '', room = '', building = '', room_number = ''):
        self.section_name = section_name
        self.room = room
        self.building = building
        self.room_number = room_number
        
    def __repr__(self):
        return '<AcceptableRoom %r>' % (self.section_name + " " + self.room)
        
        
# Schema for the table that holds all section information
#
# Fields:
#   section_name -- the name of the section, e.g. 'CMS 167 - Lecture 1'
#   course_prefix -- the three letter course code, e.g. 'CMS'
#   course_number -- stored as a String, e.g. '170 H1X'
#   is_lab -- True if the section is a lab, False otherwise
#   instructor -- name of the instructor
#   course_title -- e.g. 'Problem Solving I with Java'
#   acceptable_room -- list of acceptable rooms
class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(80), unique=True)
    course_prefix = db.Column(db.String(8))
    course_number = db.Column(db.String(24))
    course_title = db.Column(db.String(120))
    is_lab = db.Column(db.Boolean)
    instructor = db.Column(db.String(80))
    

    def __init__(self, section_name, course_prefix = '', course_number = '', 
                 is_lab = False,  course_title = '', instructor = ''):
        self.section_name = section_name
        self.is_lab = is_lab
        self.instructor = instructor
        self.course_title = course_title

    def __repr__(self):
        return '<Section %r>' % self.section_name
        

# Main entry point: returns initial front-end page
@app.route('/')
def index():
    return app.send_static_file('timetabling_system.html')
    

# Creates new object entries for new section sections entered by a user
#
# Inputs from client:
#   A JSON string containing a list of new section names
#
# Effects:
#   Creates a new object to store information on each new section
#
# Returns:
#   Nothing
@app.route('/create_new_sections', methods=['POST'])
def create_new_sections():
    
    # Unpack the name list from the request's JSON content
    content = request.get_json()
    print content
    
    new_section_names = content['names']
    course_prefix = content['prefix']
    course_number = content['number']
    course_title = content['title']
    
    # Pull the existing list of sections from the database
    sections = Section.query.all()
    existing_section_names = [c.section_name for c in sections]
    
    # Create a new entry in the database for each new section name
    for name in new_section_names:
        name = name.encode('utf-8')
        
        # If name is not already in database, make a new row
        if name not in existing_section_names:
            if 'Lab' in name:
                is_lab = True
                course_title_for_this_section = "Lab for " + course_title
            else:
                is_lab = False
                course_title_for_this_section = course_title
                
            s = Section(name, course_prefix, course_number, is_lab, 
                        course_title_for_this_section)
                        
            db.session.add(s)
        
    # Commit the changes
    db.session.commit()

    # The calling AJAX function expects valid JSON as message contents
    # Return null, which is parsed as valid JSON by the client
    return 'null'


# Saves the udpated information for a section into the database
#
# Inputs from client:
#   A JSON string representing an object holding the values from the section
#   information input dialog. The fields are:
#     - section_name
#     - instructor
#     - course_title
#     - OTHERS TO COME...
#
# Effects:
#   Updates the database entry for the section
#
# Returns:
#   Nothing
@app.route('/save_section_information', methods=['POST'])
def save_section_information():
    
    # Get the request's JSON content
    content = request.get_json()
    
    # Update database entries
    section_info = Section.query.filter_by(section_name = content['section_name']).first()
    section_info.instructor = content['instructor'] 
    section_info.course_title = content['course_title']
    
    # Add any new acceptable rooms
    existing_rooms = AcceptableRoom.query.filter_by(section_name = content['section_name']).all()
    print existing_rooms
    existing_room_names = [r.room for r in existing_rooms]
    print existing_room_names
    new_room_names = filter(lambda r: r not in existing_room_names, content['acceptable_rooms'])
    
    for new_room in new_room_names:
        fields = new_room.split(' ')
        building = fields[0]
        room_number = fields[1]
        new_ar = AcceptableRoom(content['section_name'], new_room, building, room_number)
        
        db.session.add(new_ar);
        
    # Remove any room names that are not in content['acceptable_rooms']
    remove_room_names = filter(lambda r: r not in content['acceptable_rooms'], existing_room_names)
    for old_room in remove_room_names:
        AcceptableRoom.query.filter_by(room = old_room).filter_by(section_name = content['section_name']).delete()
        
    db.session.commit()
    
    print AcceptableRoom.query.all()

    return 'null';
    

# Return the section information for the given section name
#
# Inputs from client:
#   A JSON string containing the name of the section
#
# Effects:
#   None (reads from data store)
#
# Returns:
#   A JSON string containing any information in the data store
#   for the given section name
@app.route('/get_section_information', methods=['POST'])
def get_section_information():

    # Unpack the name list from the request's JSON content
    content = request.get_json()
    name = content['name']
    
    # Basic section information
    section_info = Section.query.filter_by(section_name = name).first()
    
    # Acceptable rooms
    acceptable_rooms = AcceptableRoom.query.filter_by(section_name = name).all()
    acceptable_room_names = [r.room for r in acceptable_rooms]
    
    # Construct and send the response
    response = {}
    response['section_name'] = section_info.section_name
    response['course_title'] = section_info.course_title
    response['is_lab'] = section_info.is_lab
    response['instructor'] = section_info.instructor
    response['acceptable_rooms'] = acceptable_room_names
        
    print response

    return jsonify(**response)

    
# Returns the list of instructors
#
# Inputs from client:
#   None
#
# Effects:
#   None
#
# Returns:
#   A JSON string containing the list of instructors from the
#   Instructor database table
@app.route('/get_instructor_names', methods=['GET'])
def get_instructor_names():
    
    # Query the database for instructor names
    instructors = Instructor.query.all()
    name_list = [inst.name for inst in instructors]
    
    response = {"names" : name_list}
    return jsonify(**response)
    

# Returns the list of existing section names in the database
#
# Inputs from client:
#   None
#
# Effects:
#   None
#
# Returns:
#   A JSON string containing the list of section names from the
#   Section database table
@app.route('/get_section_names', methods=['GET'])
def get_section_names():
    
    # Query the database for section names
    sections = Section.query.all()
    sec_list = [inst.section_name for inst in sections]
    
    # Wrap and send dict of names
    response = {"names" : sec_list}
    return jsonify(**response)
    

# Returns the list of existing building names in the database
#
# Inputs from client:
#   None
#
# Effects:
#   None
#
# Returns:
#   A JSON string containing the list of buildings names from the
#   Room database table
@app.route('/get_buildings', methods=['GET'])
def get_building_names():
    
    # Query the database for buildings
    rooms = Room.query.all()
    b_list = [inst.building for inst in rooms]
    
    # Remove duplicates
    b_list = list(set(b_list))

    # Wrap and send dict of buildling names
    response = {"buildings" : b_list}
    return jsonify(**response)
    

# Returns the list of room numbers for a given building name
#
# Inputs from client:
#   A JSON string containing the name of the building
#
# Effects:
#   None
#
# Returns:
#   A JSON string containing the list of room numbers in the given building 
#   from the Room database table
@app.route('/get_rooms_by_building', methods=['POST'])
def get_rooms_by_building():
    
    # Unpack the name list from the request's JSON content
    content = request.get_json()
    
    building_name = content['building']
    
    room_number_list = [bur.room_number for r in matching_rooms]
    matching_rooms = Room.query.filter_by(building = building_name)
    room_number_list = [building_name + ' ' + r.room_number for r in matching_rooms]

    # JSON response
    response = {"rooms" : room_number_list}
    return jsonify(**response)
    
    
#--- Main
app.debug = True

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))

