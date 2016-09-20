from timetabling_server import db
from timetabling_server import Section, Instructor, Room, AcceptableRoom, Timeslot, AcceptableTimeslot, Conflict

def populate_tables():
    db.create_all()
    print db

    db.session.add(Instructor('Myers, Daniel S.'))
    db.session.add(Instructor('Anderson, Mark'))
    db.session.add(Instructor('Carrington, Julie'))
    db.session.add(Instructor('Anderson, Julie A.'))
    db.session.add(Instructor('Summet, Valerie'))
    db.session.add(Instructor('Vitray, Rick'))
    db.session.add(Instructor('Yellen, Jay'))
    db.session.add(Instructor('Teymuroglu, Zeynep'))
    db.session.add(Instructor('Rejniak, Gabriel'))
    db.session.add(Instructor('Boyd, Sheri'))

    db.session.add(Room('BUSH', '105'))
    db.session.add(Room('BUSH', '110'))
    db.session.add(Room('BUSH', '120'))
    #db.session.add(Room('BUSH', '125'))
    #db.session.add(Room('BUSH', '130'))
    #db.session.add(Room('BUSH', '135'))
    #db.session.add(Room('BUSH', '140'))
    #db.session.add(Room('BUSH', '145'))
    #db.session.add(Room('BUSH', '150'))
    #db.session.add(Room('BUSH', '155'))
    #db.session.add(Room('BUSH', '202'))
    #db.session.add(Room('BUSH', '206'))
    db.session.add(Room('BUSH', '301'))
    db.session.add(Room('BUSH', '310'))
    
    db.session.add(Room('CSS', '201'))
    db.session.add(Room('CSS', '203'))
    db.session.add(Room('CSS', '205'))
    db.session.add(Room('CSS', '207'))
    #db.session.add(Room('CSS', '213'))
    #db.session.add(Room('CSS', '217'))
    #db.session.add(Room('CSS', '223'))
    #db.session.add(Room('CSS', '227'))
    #db.session.add(Room('CSS', '246'))
    #db.session.add(Room('CSS', '999'))
    
    db.session.add(Room('KEENE', '101'))
    db.session.add(Room('KEENE', '106'))
    db.session.add(Room('KEENE', '112'))
    #db.session.add(Room('KEENE', '118'))
    #db.session.add(Room('KEENE', '124'))
    #db.session.add(Room('KEENE', '130'))
    #db.session.add(Room('KEENE', '136'))
    #db.session.add(Room('KEENE', '142'))
    #db.session.add(Room('KEENE', '148'))
    #db.session.add(Room('KEENE', '154'))
    #db.session.add(Room('KEENE', '160'))
    #db.session.add(Room('KEENE', '166'))
    #db.session.add(Room('KEENE', '172'))
    #db.session.add(Room('KEENE', '178'))
    
    
    # On-matrix timeslots
    
    # MWF 50 minutes
    db.session.add(Timeslot('MWF 8:00 - 8:50', 'MWF for 50 minutes', '8:00', '8:50',
                            '', '', '8:00', '8:50', '', '', '8:00', '8:50'))
                            
    db.session.add(Timeslot('MWF 10:00 - 10:50', 'MWF for 50 minutes', '10:00', '10:50',
                            '', '', '10:00', '10:50', '', '', '10:00', '10:50'))
                            
    db.session.add(Timeslot('MWF 11:00 - 11:50', 'MWF for 50 minutes', '11:00', '11:50',
                            '', '', '11:00', '11:50', '', '', '11:00', '11:50'))
                            
    db.session.add(Timeslot('MWF 13:00 - 13:50', 'MWF for 50 minutes', '13:00', '13:50',
                            '', '', '13:00', '13:50', '', '', '13:00', '13:50'))
                            
    db.session.add(Timeslot('MWF 15:00 - 15:50', 'MWF for 50 minutes', '15:00', '15:50',
                            '', '', '15:00', '15:50', '', '', '15:00', '15:50'))                        
    
    # TR 75 minutes
    db.session.add(Timeslot('TR 09:00 - 10:15', 'TR for 75 minutes', '', '',
                            '09:00', '10:15', '', '', '09:00', '10:15', '', ''))
                            
    db.session.add(Timeslot('TR 11:00 - 12:15', 'TR for 75 minutes', '', '',
                            '11:00', '12:15', '', '', '11:00', '12:15', '', ''))
                            
    db.session.add(Timeslot('TR 14:00 - 15:15', 'TR for 75 minutes', '', '',
                            '14:00', '15:15', '', '', '14:00', '15:15', '', ''))
                            
    db.session.add(Timeslot('TR 15:30 - 16:45', 'TR for 75 minutes', '', '',
                            '15:30', '16:45', '', '', '15:30', '16:45', '', ''))
                            
    # MW 75 minutes
    db.session.add(Timeslot('MW 10:00 - 11:15', 'MW for 75 minutes', '10:00', '11:15',
                            '', '', '10:00', '11:15', '', '', '', ''))
                            
    db.session.add(Timeslot('MW 11:30 - 12:45', 'MW for 75 minutes', '11:30', '12:45',
                            '', '', '11:30', '12:45', '', '', '', ''))                        
    
    db.session.add(Timeslot('MW 13:00 - 14:15', 'MW for 75 minutes', '13:00', '14:15',
                            '', '', '13:00', '14:15', '', '', '', ''))
                            
    db.session.add(Timeslot('MW 14:30 - 15:45', 'MW for 75 minutes', '14:30', '15:45',
                            '', '', '14:30', '15:45', '', '', '', ''))


    db.session.commit()
    
    teachers = Instructor.query.all()
    print teachers
    places = Room.query.all()
    print places
    
if __name__ == '__main__':
    populate_tables()