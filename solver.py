# Solve the timetabling problem using a one-pass approach
#
# Author: Daniel Myers (dmyers@rollins.edu)
# Date: May 2016

import random
import copy
import heapq
import time

INSTRUCTOR_OVERLAP_WEIGHT = 15
INSTRUCTOR_CONFLICT_PENALTY = 400
HEAVY_CONFLICT_PENALTY = 400
MEDIUM_CONFLICT_PENALTY = 20
LIGHT_CONFLICT_PENALTY = 1
CONFLICT_PENALTY_WEIGHT = 25.0
PROXIMITY_PENALTY_WEIGHT = 1.0
MAX_IGNORED_GAP_WIDTH = 2.0
CONFLICT_PENALTY_THRESHOLD = 15
PROXIMITY_PENALTY_THRESHOLD = 1000
UNASSIGNED_ROOM_PENALTY = 1000

LINEAR_COMBO_EDGE_CONFLICT_AVOIDANCE = 0
LINEAR_COMBO_ROOM_CONFLICT_AVOIDANCE = 0

LINEAR_COMBO_CONFLICT = 20
LINEAR_COMBO_PROXIMITY = 1
LINEAR_COMBO_GOOD_TO_BAD_SWITCH = 18

LINEAR_COMBO_GOOD_TO_BAD_ROOMS = 0

NUM_VERTICES_TO_EXPAND = 1
NUM_COLORS_PER_VERTEX = 2
MAX_QUEUE_LENGTH = 5

#PRIORITY_TOTAL_PENALTY_WEIGHT = 31.41
#PRIORITY_TOTAL_BAD_VALUE_WEIGHT = .15
#PRIORITY_TOTAL_EDGE_WEIGHT = 6.11
#PRIORITY_NUM_EDGES_WEIGHT = 8.62
#PRIORITY_BAD_VALUE_OF_EDGES = .83

PRIORITY_TOTAL_PENALTY_WEIGHT = 50
PRIORITY_TOTAL_BAD_VALUE_WEIGHT = 200
PRIORITY_TOTAL_EDGE_WEIGHT = 5
PRIORITY_NUM_EDGES_WEIGHT = 38
PRIORITY_BAD_VALUE_OF_EDGES = 23

USE_ONE_PASS = True

PRINT_CONFLICTS = False

def get_remaining_timeslots(vertex, solution, vertices, edges, overlapping_timeslots):

    remaining_timeslots = []

    acceptable_timeslots = vertices[vertex]['acceptable_timeslots']
    conflict_list = edges[vertex].keys()

    # Check every acceptable timeslot to determine if it's
    # in a heavy or instructor conflict with an already assigned
    # neighbor vertex
    for slot in acceptable_timeslots:

        skip_timeslot = False
        for conflict_course in conflict_list:

            # We only care about heavy or instructor conflicts with
            # neighbor vertices that have already been assigned
            if conflict_course not in solution:
                continue

            severity = edges[vertex][conflict_course]['conflict']
            if severity == 'L' or severity == 'M':
                continue

            solution_slot = solution[conflict_course]['assigned_timeslot']

            if overlapping_timeslots[slot][solution_slot]:
                skip_timeslot = True

        # Keep track of the slots that are not in heavy conflicts
        if not skip_timeslot:
            remaining_timeslots.append(slot)

    return remaining_timeslots


#--- Selects the name of the next vertex
#
# solution: the solution found up to this point
# vertices: the dictionary of course information
# edges: the dictionary of edge conflicts
#
# Returns: the name of the chosen vertex
def select_vertex(solution, vertices, edges, overlapping_timeslots, timeslot_gaps):

    # Select the vertex using the "bad value of colors"
    #
    # The BVoC for a vertex is the number of its colors that fall
    # above given threshold for either conflict or proximity penalties

    keys = vertices.keys()

    max_bad_value_of_colors = -1
    most_troublesome_vertex = None

    # Loop over all vertices
    for vertex in keys:

        # Skip vertices that have already been colored
        if vertex in solution:
            continue

        # Calculate the total conflict penalty across all colors at
        # the vertex
        timeslots = vertices[vertex]['acceptable_timeslots']

        # First look for any unscheduled vertices with only one acceptable
        # timeslot: these should be scheduled before anything that has
        # multiple options
        #if len(timeslots) == 1:
        #    return vertex
            
        value = bad_value_of_colors(vertex, solution, vertices, 
                                    edges, overlapping_timeslots, timeslot_gaps)

        if value > max_bad_value_of_colors:
            max_bad_value_of_colors = value
            most_troublesome_vertex = vertex

    return most_troublesome_vertex


#--- Calculate the conflict penalty increase that would be incurred if
# the given timeslot is assigned to the given vertex
#
# Returns: the increase in conflict penalty
def conflict_penalty_increase(vertex, timeslot, vertices):
    
    if timeslot == None:
        return 0.0
    else:
        return vertices[vertex][timeslot]['conflict_penalty']

    # Get the list of conflicting vertices
    #conflict_list = edges[vertex].keys()

    # Calculate the conflict penalty for all of the edges connected
    # to this vertex
    #conflict_penalty = 0.0

    #for c in conflict_list:

        # If course c has not been assigned a color yet, it doesn't
        # contribute to the conflict penalty
    #    if c not in solution:
    #        continue

    #    slot_2 = solution[c]['assigned_timeslot']

        # If the timeslots overlap, pay the conflict penalty
    #    if overlapping_timeslots[timeslot][slot_2]:
    #        conflict_severity = edges[vertex][c]['conflict']

    #        if conflict_severity == 'I':
    #            conflict_penalty += INSTRUCTOR_CONFLICT_PENALTY
    #        elif conflict_severity == 'H':
    #            conflict_penalty += HEAVY_CONFLICT_PENALTY
    #        elif conflict_severity == 'M':
    #                conflict_penalty += MEDIUM_CONFLICT_PENALTY
    #        elif conflict_severity == 'L':
    #            conflict_penalty += LIGHT_CONFLICT_PENALTY
                
    #if new_result != conflict_penalty:
    #    print new_result, conflict_penalty

    #return conflict_penalty


def proximity_penalty_increase(vertex, timeslot, vertices):
#def proximity_penalty_increase(vertex, timeslot, vertices):

    if timeslot == None:
        return 0.0
    else:
        return vertices[vertex][timeslot]['proximity_penalty']

    # Get the list of conflicting vertices
    #conflict_list = edges[vertex].keys()

    # Calculate the conflict penalty for all of the edges connected
    # to this vertex
    #proximity_penalty = 0.0

    #for c in conflict_list:

        # If course c has not been assigned a color yet, it doesn't
        # contribute to the penalty
    #    if c not in solution:
    #        continue

    #    conflict_slot = solution[c]['assigned_timeslot']

    #    gap = timeslot_gaps[timeslot][conflict_slot]
    #    overlap_factor = edges[vertex][c]['overlap']
    #    proximity_penalty +=  (float(gap)) * overlap_factor

    #if new_result != proximity_penalty:
    #    print new_result, proximity_penalty, vertex, timeslot, conflict_list

    #return proximity_penalty
    
#--- The good to bad switch value considers all vertices that would
# be affected by the assignment of (timeslot, room) to vertex
#
# It returns the number of colors at each vertex that switch from
# "good" to "bad" defined by either penalty crossing a threshold
# or the color losing all its remaining rooms
def good_to_bad_switch_value(vertex, timeslot, room, vertices, edges,
                            overlapping_timeslots, timeslot_gaps):
    
    switched_colors = 0
    
    # Consider all the vertices connected by an edge
    for v in edges[vertex]:
        
        for t in vertices[v]['acceptable_timeslots']:
            
            if overlapping_timeslots[timeslot][t]:
                severity = edges[vertex][v]['conflict']
                
                conflict = vertices[v][t]['conflict_penalty']
                
                if conflict > CONFLICT_PENALTY_THRESHOLD:
                    continue
                
                if severity == 'H' or severity == 'I':
                    conflict += HEAVY_CONFLICT_PENALTY
                elif severity == 'M':
                    conflict += MEDIUM_CONFLICT_PENALTY
                elif severity == 'L':
                    conflict += LIGHT_CONFLICT_PENALTY
                    
                if conflict > CONFLICT_PENALTY_THRESHOLD:
                    switched_colors += 1
                
        proximity = vertices[v][t]['proximity_penalty']
        
        if proximity > PROXIMITY_PENALTY_THRESHOLD:
            continue
            
        gap = timeslot_gaps[timeslot][t]
        overlap_factor = edges[vertex][v]['overlap']
        proximity +=  (float(gap)) * overlap_factor
        
        if proximity > PROXIMITY_PENALTY_THRESHOLD:
            switched_colors += 1
            
    # Consider all vertices that might lose a room assignment if
    # (timeslot, room) is assigned to vertex
    for v in vertices:
        if room not in vertices[v]['acceptable_rooms']:
            continue
            
        for t in vertices[v]['acceptable_timeslots']:
            
            # If the timeslots overlap and room is the only remaining
            # choice at t, then the assignment would remove t's only
            # room option, making it a bad color
            if (overlapping_timeslots[timeslot][t]
                and vertices[v][t]['unassigned_rooms'] == [room]):
                
                switched_colors += 1
                
    return switched_colors
    

def select_color_and_room(vertex, vertices, edges, solution, overlapping_timeslots, timeslot_gaps):
    
    timeslot_list = vertices[vertex]['acceptable_timeslots']

    best_timeslot = None
    best_room = None
    max_linear_combo_score = 10e8
    
    results = []
    
    for timeslot in timeslot_list:
        
        best_timeslot_score = 10e8
        best_timeslot_room = None
        
        room_list = get_available_rooms(vertex, timeslot, solution, vertices,
                                                    overlapping_timeslots)
                                                    
        if len(room_list) == 0:
            continue
            
        conflict_penalty = conflict_penalty_increase(vertex, timeslot, vertices)

        proximity_penalty = proximity_penalty_increase(vertex, timeslot, vertices)

        total_penalty = (CONFLICT_PENALTY_WEIGHT * conflict_penalty +
                                PROXIMITY_PENALTY_WEIGHT * proximity_penalty)
                                
        for room in room_list:
            
            good_to_bad_switch = good_to_bad_switch_value(vertex, timeslot, 
                                            room, vertices, edges, overlapping_timeslots,
                                            timeslot_gaps)
            
            linear_combo_score = (LINEAR_COMBO_CONFLICT * conflict_penalty 
                                + LINEAR_COMBO_PROXIMITY * proximity_penalty
                                + LINEAR_COMBO_GOOD_TO_BAD_SWITCH * good_to_bad_switch)
                                                                                        
            if linear_combo_score < max_linear_combo_score:
                max_linear_combo_score = linear_combo_score
                best_timeslot = timeslot
                best_room = room
                total_penalty_of_best_solution = total_penalty
            
            if linear_combo_score < best_timeslot_score:
                best_timeslot_score = linear_combo_score
                best_timeslot_room = room
                
        results.append((best_timeslot_score, timeslot, best_timeslot_room))

    if NUM_COLORS_PER_VERTEX == 1 or USE_ONE_PASS:
        results = [(0.0, best_timeslot, best_room)]
    elif len(results) == 0:
        results = [(0.0, None, None)]
    else:        
        results = heapq.nsmallest(NUM_COLORS_PER_VERTEX, results)
            
    return results
    
    
#--- Select the color and room simultaneously
def select_color_and_room_old(vertex, vertices, edges, solution, overlapping_timeslots, timeslot_gaps):

    # Get the list of potential timeslots that could be assigned to the
    # vertex
    timeslot_list = vertices[vertex]['acceptable_timeslots']

    best_timeslot = None
    best_room = None
    max_linear_combo_score = -10e8
    total_penalty_of_best_solution = 10e8

    room_cache = {}
    
    results = []

    for timeslot in timeslot_list:
        
        best_timeslot_score = -10e8
        best_timeslot_room = None

        # Get the list of acceptable rooms that are still open at this timeslot
        room_list = get_available_rooms(vertex, timeslot, solution, vertices,
                                            overlapping_timeslots)

        if len(room_list) == 0:
            continue

        conflict_penalty = conflict_penalty_increase(vertex, timeslot, vertices)

        proximity_penalty = proximity_penalty_increase(vertex, timeslot, vertices)

        total_penalty = (CONFLICT_PENALTY_WEIGHT * conflict_penalty +
                            PROXIMITY_PENALTY_WEIGHT * proximity_penalty)

        # Calculate the probability of avoiding a heavy conflict in
        # the future if we select this timeslot
        #
        # Consider every connected vertex that has a heavy or instructor
        # conflict and find the fraction of its remaining acceptable
        # timeslots that *do not* conflict with the proposed color
        #
        # The total estimated prob. of avoiding a future conflict is
        # the product of the probabilities for all such connected
        # vertices

        conflict_list = edges[vertex].keys()

        prob_of_avoiding_conflict = 1.0
        
        good_to_bad_switch = 0

        for c in conflict_list:

            # If the edge is not 'H' or 'I', skip it
            severity = edges[vertex][c]['conflict']
            if severity == 'L' or severity == 'M':
                continue

            # If c has already been scheduled, check if it's in an
            # overlapping timeslot. If so, the probability the color
            # avoiding a conflict must be 0.0
            if c in solution:
                conflict_color = solution[c]['assigned_timeslot']

                if overlapping_timeslots[timeslot][conflict_color]:
                    prob_of_avoiding_conflict = 0.0
                    break

            # Calculate the fraction of remaining acceptable timeslots
            # for course c that do not overlap with the proposed color
            c_slot_list = vertices[c]['acceptable_timeslots']
            c_conflict_list = edges[c].keys()

            num_remaining_timeslots = len(c_slot_list)
            num_nonconflicting_timeslots = 0

            for c_slot in c_slot_list:

                # If the slot is already in conflict with another course
                # don't consider it
                skip_timeslot = False
                for c_conflict_course in c_conflict_list:
                    if c_conflict_course not in solution:
                        continue

                    severity = edges[c][c_conflict_course]['conflict']
                    if severity == 'L' or severity == 'M':
                        continue

                    solution_slot = solution[c_conflict_course]['assigned_timeslot']

                    if overlapping_timeslots[c_slot][solution_slot]:
                        skip_timeslot = True

                if skip_timeslot:
                    num_remaining_timeslots -= 1
                    continue

                if not overlapping_timeslots[c_slot][timeslot]:
                    num_nonconflicting_timeslots += 1

            if num_remaining_timeslots > 0:
                prob_of_avoiding_conflict *= float(num_nonconflicting_timeslots) / num_remaining_timeslots
                
            good_to_bad_switch += num_remaining_timeslots - num_nonconflicting_timeslots

        candidate_solution = copy.deepcopy(solution)
        candidate_solution[vertex] = {}
        candidate_solution[vertex]['assigned_timeslot'] = timeslot

        prob_of_avoiding_edge_conflict = prob_of_avoiding_conflict

        # Consider all rooms that can be assigned at this timeslot
        for room in room_list:  

            prob_of_avoiding_room_conflict = 1.0
            good_to_bad_switch_rooms = 0

            # Construct the set of unscheduled courses that also have this
            # room as one of their suitable choices
            possible_conflicting_courses = []
            for course in vertices:
                if (course not in solution and
                    room in vertices[course]['acceptable_rooms'] and
                    course != vertex):

                    possible_conflicting_courses.append(course)

            # Construct a candidate schedule that makes the color and
            # room assignment
            candidate_solution[vertex]['assigned_room'] = room

            # For each conflicting course, figure out the number of scheduling
            # options it has using the new candidate schedule
            for possible_conflict in possible_conflicting_courses:

                # Number of remaining timeslots
                remaining_timeslots = get_remaining_timeslots(possible_conflict,
                                    solution, vertices, edges, overlapping_timeslots)

                # Calculate the total number of "scheduling opportunities"
                # (timeslots * rooms) that the course could have before
                # and after assigning the (timeslot, room) combination
                num_sched_opps_before_assignment = 0
                num_sched_opps_after_assignment = 0
                num_non_overlaps = 0

                for s in remaining_timeslots:

                    if not overlapping_timeslots[s][timeslot]:
                        num_non_overlaps += 1
                        continue

                    # Get the number of rooms available at this timeslot
                    # before the assignment
                    rooms_at_this_time_before_assignment = get_available_rooms(possible_conflict,
                                        s, solution, vertices, overlapping_timeslots)

                    num_sched_opps_before_assignment += len(rooms_at_this_time_before_assignment)

                    # Get the number of rooms available at this time
                    # after the assignment
                    #rooms_at_this_time_after_assignment = get_available_rooms(possible_conflict,
                    #                    s, candidate_solution, vertices, overlapping_timeslots)
                    
                    rooms_at_this_time_after_assignment = filter(lambda x: x != room, rooms_at_this_time_before_assignment)

                    num_sched_opps_after_assignment += len(rooms_at_this_time_after_assignment)

                if num_non_overlaps == len(remaining_timeslots):
                    prob_of_avoiding_room_conflict *= 1.0
                elif num_sched_opps_before_assignment == 0:
                    prob_of_avoiding_room_conflict = 0.0
                else:
                    prob_of_avoiding_room_conflict *= (float(num_sched_opps_after_assignment) /
                                                        num_sched_opps_before_assignment)
                                                        
                good_to_bad_switch_rooms += num_sched_opps_before_assignment - num_sched_opps_after_assignment

            #prob_of_avoiding_conflict = prob_of_avoiding_edge_conflict * prob_of_avoiding_room_conflict

            # Compare this assignment to the best that we've found so far
            linear_combo_score = (LINEAR_COMBO_EDGE_CONFLICT_AVOIDANCE * prob_of_avoiding_edge_conflict +
                                        LINEAR_COMBO_ROOM_CONFLICT_AVOIDANCE * prob_of_avoiding_room_conflict -
                                        LINEAR_COMBO_CONFLICT * conflict_penalty -
                                        LINEAR_COMBO_PROXIMITY * proximity_penalty -
                                        LINEAR_COMBO_GOOD_TO_BAD_SWITCH * good_to_bad_switch -
                                        LINEAR_COMBO_GOOD_TO_BAD_ROOMS * good_to_bad_switch_rooms)
                                        
            #print (timeslot, room, linear_combo_score, prob_of_avoiding_edge_conflict,
            #    prob_of_avoiding_room_conflict, conflict_penalty, proximity_penalty, good_to_bad_switch,
            #    good_to_bad_switch_rooms)

            if linear_combo_score > max_linear_combo_score:
                max_linear_combo_score = linear_combo_score
                best_timeslot = timeslot
                best_room = room
                total_penalty_of_best_solution = total_penalty
            
            if linear_combo_score > best_timeslot_score:
                best_timeslot_score = linear_combo_score
                best_timeslot_room = room
                
        results.append((best_timeslot_score, timeslot, best_timeslot_room))

    if NUM_COLORS_PER_VERTEX == 1 or USE_ONE_PASS:
        return [(0.0, best_timeslot, best_room)]
    else:        
        results = heapq.nlargest(NUM_COLORS_PER_VERTEX, results)
        
        if len(results) == 0:
            results = [(0.0, None, None)]
            
        return results

#--- Return the set of available rooms that are still available for a
# vertex after it is assigned a given color
def get_available_rooms(vertex, timeslot, solution, vertices, overlapping_timeslots):
    
    return vertices[vertex][timeslot]['unassigned_rooms']

    #acceptable_rooms = vertices[vertex]['acceptable_rooms']
    #remove_list = []

    # Check if the room has already been assigned to any overlapping timeslot
    #for room in acceptable_rooms:
        
    #    for scheduled_course in solution:
    #        scheduled_room = solution[scheduled_course]['assigned_room']
    #        scheduled_timeslot = solution[scheduled_course]['assigned_timeslot']

    #        if (room == scheduled_room and
    #            overlapping_timeslots[timeslot][scheduled_timeslot]):
                #print 'Room conflict with ', scheduled_course, scheduled_timeslot

    #            remove_list.append(room)

    # Remove the unavailable rooms
    #room_list = filter(lambda x: x not in remove_list, acceptable_rooms)

    #if set(room_list) != set(new_list):
    #    print new_list, room_list, vertex,
    #    return None

    #return room_list


#--- Convert time from 12 hour format to a reference decimal value
#
# For example, '1:15 pm' is converted to 13.25
#
# The input is a string in 12-hour time format with either 'am' or 'pm'
def convert_time(time):
    time_fields = time.split(" ")
    hour_minute_fields = time_fields[0].split(":")
    hours = int(hour_minute_fields[0])
    fraction = int(hour_minute_fields[1]) / 60.0

    if 'pm' in time_fields[1].lower() and hours < 12:
        hours += 12
    if 'am' in time_fields[1].lower() and hours > 11:
        hours -= 12
    return hours + fraction


#--- Determines if two timeslot strings overlap
#
# These timeslot strings represent one fixed meeting time on some set
# of days --- compound timeslots meeting at different times on
# different days must be dealt with in a parent routine.
#
# Returns: A tuple with the first element True if the slots overlap
# and the second giving the gap distance bewteen the slots as a float
def check_meeting_overlap_and_gap(meeting_1, meeting_2):

    fields_1 = meeting_1.split(' ')
    fields_2 = meeting_2.split(' ')

    # Extract the meeting days
    days_1 = fields_1[0]
    days_2 = fields_2[0]

    # Overlap is a binary property, it either exists or it doesn't
    # If we find any days where the classes conflict, then overlap_exists
    # is set to True and kept True
    overlap_exists = False
    gap = 0.0

    # Check for meeting times on the same days
    for d in 'MTWRF':
        if d in days_1 and d in days_2:
            
            # Convert the times to decimal
            start_time_1 = fields_1[1] + ' ' + fields_1[2]
            conv_start_1 = convert_time(start_time_1)
            end_time_1 = fields_1[4] + ' ' + fields_1[5]
            conv_end_1 = convert_time(end_time_1)

            start_time_2 = fields_2[1] + ' ' + fields_2[2]
            conv_start_2 = convert_time(start_time_2)
            end_time_2 = fields_2[4] + ' ' + fields_2[5]
            conv_end_2 = convert_time(end_time_2)

            # The slots overlap if either start time lies between the
            # start and end time of the other meeting
            if ((conv_start_1 >= conv_start_2 and conv_start_1 <= conv_end_2) or
                (conv_start_2 >= conv_start_1 and conv_start_2 <= conv_end_1)):

                overlap_exists = True
                gap = 0.0  # Overlapping classes have a gap of 0.0
                break

            else:
                # The gap is the distance between the start and end time
                # If we calculate both differences, one will be positive and
                # the other will be negative --- take the positive one as
                # the gap value
                this_meeting_gap = max(conv_start_2 - conv_end_1, conv_start_1 - conv_end_2)

                if this_meeting_gap > MAX_IGNORED_GAP_WIDTH:
                    gap += this_meeting_gap

    return overlap_exists, gap


#--- Identifies the pairs of overlapping timeslots and calculates gaps
#
# Each timeslot entry has the form
#   0 TR 11:00 am - 12:15 pm
#
# The first number is the unique id of the timeslot
#
# A timeslot may have meeting times at different hours on different
# days --- the components of the timeslot are separated by semicolons
#
# Returns: a dict recording a True/False entry for each pair of timeslot IDs
# and a dict recording gaps for each timeslot pair
def calculate_overlapping_timeslots_and_gaps(timeslot_list):
    are_overlapping = {}
    gaps = {}

    # Loop over each entry in the timeslot list
    for i in range(len(timeslot_list)):
        slot_1 = timeslot_list[i]

        # Extract the id number from the slot string
        index_of_first_space = slot_1.index(' ')
        id_1 = int(slot_1[:index_of_first_space])

        # Multi-part timeslots meet at different times on different
        # days --- each part is separated by a semicolon
        slot_components_1 = slot_1[index_of_first_space+ 1 :].split(' ; ')

        # Each timeslot id gets a dictionary storing an entry for each
        # other timeslot id
        are_overlapping[id_1] = {}
        gaps[id_1] = {}

        # Compare the first entry to every other entry
        for j in range(len(timeslot_list)):
            slot_2 = timeslot_list[j]

            # Extract the id number from the slot string
            index_of_first_space = slot_2.index(' ')
            id_2 = int(slot_2[:index_of_first_space])

            slot_components_2 = slot_2[index_of_first_space + 1 :].split(' ; ')

            # Check all pairs of meeting times between the two slots
            # to determine if there is any overlap
            #
            # Yes, this is a huge pain.

            # Overlap is a binary property: if we find any pair of meetings
            # that overlap, we have to treat the entire timeslots as overlapping
            overlap_exists = False

            # Gap factor is a little more complicated: there might be different
            # gaps among different meeting times on different days. Therefore,
            # we'll report the *maximum* gap as the overall gap between the
            # two timeslots
            max_gap = 0.0

            for meeting_1 in slot_components_1:
                for meeting_2 in slot_components_2:

                    meeting_overlap, meeting_gap = check_meeting_overlap_and_gap(meeting_1, meeting_2)

                    if meeting_overlap:
                        overlap_exists = True

                    #max_gap = max(max_gap, meeting_gap)
                    max_gap += meeting_gap

            # Once all the slot components have been compared we know
            # if any of them overlap and the maximum gap  between any
            # two that occur on the same day
            are_overlapping[id_1][id_2] = overlap_exists
            gaps[id_1][id_2] = round(max_gap)

    # Add entries for None to both tables
    #
    # It's possible for a course to be assigned None as its slot
    # if the scheduler can't find a acceptable timeslot with any
    # open rooms
    are_overlapping[None] = {}
    gaps[None] = {}

    for slot in are_overlapping.keys():
        are_overlapping[None][slot] = False
        are_overlapping[slot][None] = False
        gaps[None][slot] = 0.0
        gaps[slot][None] = 0.0

    return are_overlapping, gaps


#--- Calculate the total penalty of a schedule
#
# solution: the solution dictionary holding the assigned timeslot
#           for each course
# edges: the dictionary of conflicts between courses
# are_overlapping_timeslots: a dict that stores a True/False entry for
#            pairs of timeslots recording whether they overlap
#
# Returns: the penalty value
def calculate_total_penalty(solution, edges, overlapping_timeslots, timeslot_gaps, vertices):

    conflict_penalty = 0
    proximity_penalty = 0
    total_penalty = 0

    edges_tested = {}

    keys = solution.keys()
    keys.sort()

    num_instructor_conflicts = 0
    num_heavy_conflicts = 0
    num_medium_conflicts = 0
    num_light_conflicts = 0
    num_unassigned_rooms = 0

    for course in keys:

        slot_1 = solution[course]['assigned_timeslot']

        # Get the list of conflicting edges
        conflict_list = edges[course].keys()

        course_proximity_penalty = 0.0
        
        if slot_1 == None:
            num_unassigned_rooms += 1
            continue

        # Examine the possible conflicts and check for overlapping
        # timeslot assignments
        for c in conflict_list:
            
            if c not in solution:
                continue

            slot_2 = solution[c]['assigned_timeslot']
            
            if slot_2 == None:
                continue

            # If the timeslots overlap, pay the conflict penalty
            if overlapping_timeslots[slot_1][slot_2]:
                conflict_severity = edges[course][c]['conflict']

                if conflict_severity == 'I':
                    #print 'instructor: ', course, c
                    conflict_penalty += INSTRUCTOR_CONFLICT_PENALTY
                    num_instructor_conflicts += 1
                elif conflict_severity == 'H':
                    #print 'heavy: ', course, c
                    conflict_penalty += HEAVY_CONFLICT_PENALTY
                    num_heavy_conflicts += 1
                elif conflict_severity == 'M':
                    #print 'medium: ', course, c
                    conflict_penalty += MEDIUM_CONFLICT_PENALTY
                    num_medium_conflicts += 1
                elif conflict_severity == 'L':
                    #print 'light: ', course, c
                    conflict_penalty += LIGHT_CONFLICT_PENALTY
                    num_light_conflicts += 1

            # Calculate the gap between the courses and pay the
            # proximity penalty
            #
            # The penalty depends on the gap between the courses as
            # well as the GAP_WIDTH and overlap factor
            #
            # GAP_WIDTH controls the number of hours treated as a unit
            # for the purposes of proximity penalty calculations
            #
            # For example, if GAP_WIDTH is 4.0 and the two courses are
            # separated by 5 hours, the penalty will be
            #
            # overlap_factor * (5 / 4.0)
            #
            # Courses that have an instructor conflict are assigned
            # an additional weight to their overlap factors to encourage
            # compact schedules for instructors
            #
            # The gap must be at least GAP_WIDTH to incur any penalty
            gap = timeslot_gaps[slot_1][slot_2]
            overlap_factor = edges[course][c]['overlap']
            course_proximity_penalty += (float(gap)) * overlap_factor
            proximity_penalty +=  (float(gap)) * overlap_factor

            #print slot_1, slot_2, gap, overlap_factor, (float(gap)) * overlap_factor

    # Each edge has been counted twice: divide the sums by two
    adjusted_conflict_penalty = CONFLICT_PENALTY_WEIGHT * conflict_penalty / 2.0
    adjusted_proximity_penalty = PROXIMITY_PENALTY_WEIGHT * proximity_penalty / 2.0
    
    room_penalty = num_unassigned_rooms * UNASSIGNED_ROOM_PENALTY
    
    total_penalty = adjusted_conflict_penalty + adjusted_proximity_penalty + room_penalty
    

    if PRINT_CONFLICTS:
        print 'Unweighted total conflict penalty: ', conflict_penalty / 2
        print 'Unweighted total proximity penalty: ', proximity_penalty / 2
        print 'Unweighted total penalty: ', str(conflict_penalty / 2 + proximity_penalty / 2)

        print 'Weighted total conflict penalty: ', adjusted_conflict_penalty
        print 'Weighted total proximity penalty: ', adjusted_proximity_penalty
        print 'Weighted total penalty: ', str(adjusted_conflict_penalty + adjusted_proximity_penalty)

        print 'Number of instructor conflicts = ', num_instructor_conflicts / 2
        print 'Number of heavy conflicts = ', num_heavy_conflicts / 2
        print 'Number of medium conflicts = ', num_medium_conflicts / 2
        print 'Number of light conflicts = ', num_light_conflicts / 2
        print 'Number of unassigned rooms = ', num_unassigned_rooms
        
        print (total_penalty, str(conflict_penalty / 2), str(proximity_penalty / 2), 
            str(num_instructor_conflicts / 2 + num_heavy_conflicts / 2), str(num_medium_conflicts / 2), 
            str(num_light_conflicts / 2), num_unassigned_rooms)

    return total_penalty
    
    
def update_penalties_and_room_lists(vertex, timeslot, room, vertices, solution,
                                        edges, overlapping_timeslots, timeslot_gaps, deallocate = False):
                                                                                
    # Update the unassigned rooms and penalties for vertices
    # affected by the assignment
    for v in edges[vertex]:
        severity = edges[vertex][v]['conflict']
        
        if severity == 'H':
            conflict_increase = HEAVY_CONFLICT_PENALTY
        elif severity  == 'I':
            conflict_increase = INSTRUCTOR_CONFLICT_PENALTY
        elif severity  == 'M':
            conflict_increase = MEDIUM_CONFLICT_PENALTY
        elif severity  == 'L':
            conflict_increase = LIGHT_CONFLICT_PENALTY
        
        # Update the penalties for overlapping timeslots 
        for neighbor_slot in vertices[v]['acceptable_timeslots']:
            if overlapping_timeslots[timeslot][neighbor_slot]:
                if deallocate:
                    vertices[v][neighbor_slot]['conflict_penalty'] -= conflict_increase
                else:
                    vertices[v][neighbor_slot]['conflict_penalty'] += conflict_increase
                
            # The change in proximity penalty incurred by assigning
            # timeslot to vertex
            gap = timeslot_gaps[timeslot][neighbor_slot]
            overlap_factor = edges[vertex][v]['overlap']
            proximity_increase =  (float(gap)) * overlap_factor
            
            if deallocate:
                vertices[v][neighbor_slot]['proximity_penalty'] -= proximity_increase
            else:
                vertices[v][neighbor_slot]['proximity_penalty'] += proximity_increase

    # Update room availability    
    for v in vertices:
        
        if v == vertex:
            continue
        
        if room not in vertices[v]['acceptable_rooms']:
            continue
        
        for t in vertices[v]['acceptable_timeslots']:
            if overlapping_timeslots[timeslot][t]:
                
                if deallocate:
                    vertices[v][t]['unassigned_rooms'].append(room)

                else:
                    filtered_rooms = filter(lambda x: x != room, vertices[v][t]['unassigned_rooms'])                
                    vertices[v][t]['unassigned_rooms'] = filtered_rooms
                
    return vertices


#--- Run the one-pass construction algorithm
#
# The one-pass strategy is a basic greedy algorithm:
#
#     while there are uncolored vertices {
#         choose the next vertex to color
#         assign it a color
#     }
#
# The real strategy is in the choice of heuristics to pick the
# "most troublesome" vertex at each step and then choose its color
#
# vertices: the dictionary of course information
# edges: the dictionary of conflcting edge information
#
# Returns: a solution dictionary listing the assigned timeslot and
# room for each course
def one_pass_solver(vertices, edges, overlapping_timeslots, timeslot_gaps):
    
    solution = {}
    
    num_vertices = len(vertices)
    num_colored_vertices = len(solution)

    while num_colored_vertices < num_vertices:

        # Select the "most troublesome" vertex to color
        # Returns the name of a vertex as entered in the vertices
        vertex = select_vertex(solution, vertices, edges, overlapping_timeslots, timeslot_gaps)

        selection = select_color_and_room(vertex, vertices, edges, solution,
                            overlapping_timeslots, timeslot_gaps)
                                                                                    
        color = selection[0][1]
        room = selection[0][2]
        
        # Make the assignment
        solution[vertex] = {}
        solution[vertex]['assigned_timeslot'] = color
        solution[vertex]['assigned_room'] = room
        
        vertices = update_penalties_and_room_lists(vertex, color, room, vertices, solution,
                                                edges, overlapping_timeslots, timeslot_gaps)
                    
        num_colored_vertices += 1

    return solution
    

#--- Add up the number of "bad" timeslots available to a vertex
#
# A timeslot is "bad" if its conflict or proximity penalties exceed
# set thresholds
#
# If the penalty is not high enough to exceed the threshold, the color
# is assigned a partial badness value
def bad_value_of_colors(vertex, solution, vertices, edges, overlapping_timeslots, timeslot_gaps):
        
    bad_value_of_colors = 0.0
    
    # Calculate the total conflict penalty across all colors at
    # the vertex
    timeslots = vertices[vertex]['acceptable_timeslots']
    
    # Vertices with only one timeslot get a big boost to their 
    # badness so they're likely to be chosen at the beginning of the
    # search process
    if len(timeslots) == 1:
        bad_value_of_colors += 10000

    # Loop over all the candidate timeslots that could be assigned to
    # the vertex
    for timeslot in timeslots:

        conflict_penalty = conflict_penalty_increase(vertex, timeslot, vertices)

        proximity_penalty = proximity_penalty_increase(vertex, timeslot, vertices)

        if conflict_penalty > CONFLICT_PENALTY_THRESHOLD:
            bad_value_of_colors += 1
        else:
            bad_value_of_colors += float(conflict_penalty) / CONFLICT_PENALTY_THRESHOLD

        if proximity_penalty > PROXIMITY_PENALTY_THRESHOLD:
            bad_value_of_colors += 1
        else:
            bad_value_of_colors += float(proximity_penalty) / PROXIMITY_PENALTY_THRESHOLD
            
        remaining_rooms = get_available_rooms(vertex, timeslot, solution, vertices, overlapping_timeslots)
        num_remaining_rooms = len(remaining_rooms)
        
        if num_remaining_rooms == 0:
            if 'LAB' in vertex:
                bad_value_of_colors += 5000
            else:
                bad_value_of_colors += 10
        else:
            bad_value_of_colors += 2 ** -(2 * num_remaining_rooms)
                        
    return bad_value_of_colors
    

#--- Return a list of the n most troublesome vertices from the solution
def expand(solution, n, vertices, edges, overlapping_timeslots, timeslot_gaps):
    
    keys = vertices.keys()
    
    list_of_vertices = []

    # Loop over all vertices
    for vertex in keys:

        # Skip vertices that have already been colored
        if vertex in solution:
            continue

        value = bad_value_of_colors(vertex, solution, vertices, 
                                edges, overlapping_timeslots, timeslot_gaps)
                                
        list_of_vertices.append((value, vertex))
        
    list_of_vertices = [y for (x,y) in sorted(list_of_vertices, reverse = True)]
    
    return list_of_vertices[:n]
    
    
#--- Calculate the beam search priority of the input solution
#
# The heuristics are
# 1. total bad value of colors for all uncolored vertices
# 2. total conflict penalty
#
def priority_function(solution, vertices, edges, overlapping_timeslots, timeslot_gaps):
    
    total_bvoc = 0
    total_edge_weight = 0
    number_of_edges = 0
    bad_value_of_edges = 0

    for vertex in vertices:
        if vertex in solution:
            continue
        
        total_bvoc += bad_value_of_colors(vertex, solution, vertices,
                                            edges, overlapping_timeslots,
                                            timeslot_gaps)
            
        neighbors = edges[vertex].keys()
        
        for neighbor in neighbors:
            
            # Only consider edges between uncolored neighbors
            if neighbor in solution:
                continue
            
            weight = edges[vertex][neighbor]['conflict']
            
            if weight == 'H' or weight == 'I':
                edge_weight = HEAVY_CONFLICT_PENALTY
            elif weight == 'M':
                edge_weight = MEDIUM_CONFLICT_PENALTY
            elif weight == 'L':
                edge_weight = LIGHT_CONFLICT_PENALTY
                
            if edge_weight > CONFLICT_PENALTY_THRESHOLD:
                bad_value_of_edges += 1
            else:
                bad_value_of_edges += float(edge_weight) / CONFLICT_PENALTY_THRESHOLD
                
            total_edge_weight += edge_weight
                
            number_of_edges += 1
    
    return total_bvoc, total_edge_weight, number_of_edges, bad_value_of_edges
    
    
def one_pass_priority(vertices, edges, overlapping_timeslots, timeslot_gaps, solution):
        
    num_vertices = len(vertices)
    num_colored_vertices = len(solution)

    while num_colored_vertices < num_vertices:

        # Select the "most troublesome" vertex to color
        # Returns the name of a vertex as entered in the vertices
        vertex = select_vertex(solution, vertices, edges, overlapping_timeslots, timeslot_gaps)

        selection = select_color_and_room(vertex, vertices, edges, solution,
                            overlapping_timeslots, timeslot_gaps)
                                                                                    
        color = selection[0][1]
        room = selection[0][2]
                
        # Make the assignment
        solution[vertex] = {}
        solution[vertex]['assigned_timeslot'] = color
        solution[vertex]['assigned_room'] = room
                
        vertices = update_penalties_and_room_lists(vertex, color, room, vertices, solution,
                                                edges, overlapping_timeslots, timeslot_gaps)
                    
        num_colored_vertices += 1
        
    total_penalty = calculate_total_penalty(solution, edges, overlapping_timeslots, timeslot_gaps, vertices)

    return total_penalty
    
    
def one_pass_lower_bound_current_graph(vertices, edges, overlapping_timeslots, timeslot_gaps, solution):
    
    total_penalty = 0
    
    for vertex in vertices:
        if vertex in solution: 
            continue
            
        min_penalty_for_vertex = 10e8
            
        for t in vertices[vertex]['acceptable_timeslots']:
            conflict = vertices[vertex][t]['conflict_penalty']
            proximity = vertices[vertex][t]['proximity_penalty']
            
            total = LINEAR_COMBO_CONFLICT * conflict + LINEAR_COMBO_PROXIMITY * proximity
            
            min_penalty_for_vertex = min(min_penalty_for_vertex, total)
            
        total_penalty += min_penalty_for_vertex
        
    return total_penalty
    
    
def one_pass_lower_bound(vertices, edges, overlapping_timeslots, timeslot_gaps, solution):
    
    num_vertices = len(vertices)
    starting_solution_size = len(solution)
    num_colored_vertices = len(solution)

    while num_colored_vertices < num_vertices:

        # Select the "most troublesome" vertex to color without regard 
        # for rooms
        max_bad_value_of_colors = -10e8
        most_troublesome_vertex = None
        best_color_for_most_troublesome_vertex = None
        
        for vertex in vertices:
            if vertex in solution:
                continue
                
            bad_value_of_colors = 0.0
            
            if len(vertices[vertex]['acceptable_timeslots']) == 1:
                bad_value_of_colors += 10000
            
            for t in vertices[vertex]['acceptable_timeslots']:
                conflict_penalty = vertices[vertex][t]['conflict_penalty']
                proximity_penalty = vertices[vertex][t]['proximity_penalty']
                
                if conflict_penalty > CONFLICT_PENALTY_THRESHOLD:
                    bad_value_of_colors += 1
                else:
                    bad_value_of_colors += float(conflict_penalty) / CONFLICT_PENALTY_THRESHOLD
                    
                if proximity_penalty > PROXIMITY_PENALTY_THRESHOLD:
                    bad_value_of_colors += 1
                else:
                    bad_value_of_colors += float(proximity_penalty) / PROXIMITY_PENALTY_THRESHOLD
                    
            #if bad_value_of_colors > 0.0:
            #    print vertex, bad_value_of_colors, best_color_for_vertex, min_penalty_for_vertex
            
            if bad_value_of_colors > max_bad_value_of_colors:
                most_troublesome_vertex = vertex
                max_bad_value_of_colors = bad_value_of_colors

        # Find the best timeslot for the most troublesome vertex
        vertex = most_troublesome_vertex
                
        min_penalty_for_vertex = 10e8
        best_color_for_vertex = None
        
        for t in vertices[vertex]['acceptable_timeslots']:
            
            conflict_penalty = vertices[vertex][t]['conflict_penalty']
            proximity_penalty = vertices[vertex][t]['proximity_penalty']
                
            # Calculate the good to bad switch value without considering rooms
            switched_colors = 0

            # Consider all the vertices connected by an edge
            for neighbor in edges[vertex]:
                
                for neighbor_timeslot in vertices[neighbor]['acceptable_timeslots']:
                    
                    if overlapping_timeslots[neighbor_timeslot][t]:
                        severity = edges[vertex][neighbor]['conflict']
                        
                        neighbor_conflict = vertices[neighbor][neighbor_timeslot]['conflict_penalty']
                        
                        if neighbor_conflict > CONFLICT_PENALTY_THRESHOLD:
                            continue
                        
                        if severity == 'H' or severity == 'I':
                            neighbor_conflict += HEAVY_CONFLICT_PENALTY
                        elif severity == 'M':
                            neighbor_conflict += MEDIUM_CONFLICT_PENALTY
                        elif severity == 'L':
                            neighbor_conflict += LIGHT_CONFLICT_PENALTY
                            
                        if neighbor_conflict > CONFLICT_PENALTY_THRESHOLD:
                            switched_colors += 1
                        
                neighbor_proximity = vertices[neighbor][neighbor_timeslot]['proximity_penalty']
                
                if neighbor_proximity > PROXIMITY_PENALTY_THRESHOLD:
                    continue
                    
                gap = timeslot_gaps[neighbor_timeslot][t]
                overlap_factor = edges[vertex][neighbor]['overlap']
                neighbor_proximity +=  (float(gap)) * overlap_factor
                
                if neighbor_proximity > PROXIMITY_PENALTY_THRESHOLD:
                    switched_colors += 1
                
            total = (LINEAR_COMBO_CONFLICT * conflict_penalty
                     + LINEAR_COMBO_PROXIMITY * proximity_penalty
                     + LINEAR_COMBO_GOOD_TO_BAD_SWITCH * switched_colors)
                                     
            if total < min_penalty_for_vertex:
                min_penalty_for_vertex = total
                best_color_for_vertex = t

        # Select the color assignment that minimizes penalty without regard for rooms
        solution[most_troublesome_vertex] = {}
        solution[most_troublesome_vertex]['assigned_timeslot'] = best_color_for_vertex
        solution[most_troublesome_vertex]['assigned_room'] = vertices[vertex]['acceptable_rooms'][0]
        
        #print most_troublesome_vertex, best_color_for_most_troublesome_vertex

        vertices = update_penalties_and_room_lists(most_troublesome_vertex, 
                                                    best_color_for_vertex, 
                                                    None, vertices, solution,
                                                    edges, overlapping_timeslots, timeslot_gaps)
                                                    
        num_colored_vertices += 1
        
    for i in range(10):
        improve(solution, vertices, edges, overlapping_timeslots, timeslot_gaps)
                                                    
    penalty = calculate_total_penalty(solution, edges, overlapping_timeslots, timeslot_gaps, vertices)
    #penalty -= (len(solution) - starting_solution_size) * UNASSIGNED_ROOM_PENALTY
 
    return penalty
        
    
#--- Priority queue solver
def priority_queue_solver(vertices, edges, overlapping_timeslots, timeslot_gaps):
    
    best_solution = None
    best_vertices = None
    min_penalty = 10e8
    
    # The "queue" is really a list that keeps the top MAX_QUEUE_LENGTH
    # partial colorings
    queue = []
    queue.append((0, {}, vertices))
    
    partial_coloring_cache = {}
    
    # Loop until the queue is empty
    while len(queue) > 0:
        
        # Pop the front solution and expand it
        entry = queue.pop(0)
        current_solution = entry[1]
        current_vertices = entry[2]
            
        solution_size = len(current_solution)
        print solution_size
        
        solution_list = [(x, current_solution[x]['assigned_timeslot']) for x in current_solution]
        solution_list = sorted(solution_list)
        solution_list_string = str(solution_list)
        
        if solution_size not in partial_coloring_cache:
            partial_coloring_cache[solution_size] = {}
        
        if solution_list_string in partial_coloring_cache[solution_size]:
            #print 'Already expanded!'
            continue
        else:
            partial_coloring_cache[solution_size][solution_list_string] = True

        list_of_vertices = expand(current_solution, NUM_VERTICES_TO_EXPAND, 
                                    current_vertices, edges, overlapping_timeslots, 
                                    timeslot_gaps)
                                            
        # A leaf node has no remaining uncolored vertices
        if len(list_of_vertices) == 0:            
            penalty = calculate_total_penalty(current_solution, edges, overlapping_timeslots, timeslot_gaps, vertices)
            
            print 'Found solution: ', penalty
            
            if penalty < min_penalty:
                min_penalty = penalty
                best_solution = current_solution
                best_vertices = current_vertices
                
            continue
                        
        # Assign a color to each vertex 
        priority_list = []
        
        for vertex in list_of_vertices:
            selections = select_color_and_room(vertex, current_vertices, 
                                edges, current_solution, overlapping_timeslots, timeslot_gaps)
                                                                        
            # Construct a new solution
            for priority, color, room in selections:
                new_solution = copy.deepcopy(current_solution)
                new_solution[vertex] = {}
                new_solution[vertex]['assigned_timeslot'] = color
                new_solution[vertex]['assigned_room'] = room
                new_vertices = copy.deepcopy(current_vertices)
                
                new_vertices = update_penalties_and_room_lists(vertex, color, room, new_vertices, new_solution,
                                                        edges, overlapping_timeslots, timeslot_gaps)
                                    
                # Calculate the priority of the new solution
                total_bvoc, total_edge_weight, num_edges, bad_value_of_edges = priority_function(new_solution, 
                                                            new_vertices, edges, 
                                                            overlapping_timeslots, 
                                                            timeslot_gaps)
                
                #temp_solution = copy.deepcopy(new_solution)
                #temp_vertices = copy.deepcopy(new_vertices)
                #priority = one_pass_priority(temp_vertices, edges, overlapping_timeslots, timeslot_gaps, temp_solution)
                                
                penalty = calculate_total_penalty(new_solution, edges, overlapping_timeslots, timeslot_gaps, vertices)
                
                #print '\t', vertex, color, room, priority, penalty

                solution_score = (PRIORITY_TOTAL_PENALTY_WEIGHT * penalty
                                    + PRIORITY_TOTAL_BAD_VALUE_WEIGHT * total_bvoc
                                    + PRIORITY_TOTAL_EDGE_WEIGHT * total_edge_weight
                                    + PRIORITY_NUM_EDGES_WEIGHT * num_edges
                                    + PRIORITY_BAD_VALUE_OF_EDGES * bad_value_of_edges)
                
                #solution_score = priority
                                
                #print '\t', penalty, total_bvoc, total_edge_weight, num_edges, vertex
                                
                queue.append((solution_score, new_solution, new_vertices))
            
        if len(queue) > MAX_QUEUE_LENGTH:
            queue = heapq.nsmallest(MAX_QUEUE_LENGTH, queue)
        else:
            queue = sorted(queue)

    return best_solution, best_vertices
    

#--- Read and skip over the parameters block of the input file
def read_parameters_block(f):

    # The first line should be either true or false
    f.readline()

    # The second line is blank
    f.readline()

    # Read through the list of parameters, one per line
    #
    # This could be modified to parse and return the parameters if we
    # ever actually need to use them
    line = f.readline()
    while line.strip() != '':
        line = f.readline()

    # Done with the input block
    return


#--- Read the list of rooms
#
# Assumes that all lines up to but not including the one containing
# the room list have been read
def read_room_list(f):

    line = f.readline().strip()
    rooms = line.split(' ')

    # Read the next blank line
    f.readline()

    return rooms


#--- Read the list of timeslots
#
# Assumes that all lines up to but not including the one beginning
# the list of timeslots have been read
def read_timeslot_list(f):

    timeslots = []

    line = f.readline()

    while line.strip() != '':
        line = line.strip()
        timeslots.append(line)
        line = f.readline()

    # Read five more blank lines
    for i in range(5):
        f.readline()

    return timeslots


#--- Read the list of course prefixes
#
# Each prefix is on its own line with two other fields
#
# In the files that have been automatically generated from the Excel
# spreadsheets, these other fields are all identical to the course
# prefix. In older, hand-encoded files, the other fields record the
# department and program name.
#
# This scheduler doesn't use the prefixes but they're required by
# the older schedulers.
#
# Assumes that all lines up to but not including the one beginning
# the list of timeslots have been read
def read_course_prefixes(f):

    prefixes = []

    line = f.readline()

    while line.strip() != '':
        line = line.strip()
        fields = line.split(' ')

        # The course prefix is the last field on the line
        prefixes.append(fields[-1])

        line = f.readline()

    return prefixes


#--- Read the list of instructor names
#
# Assumes that all lines up to but not including the first instructor
# name have already been read
def read_instructors(f):

    instructors = []

    line = f.readline()

    while line.strip() != '':
        fields = line.split(' :')
        instructors.append(fields[0])
        line = f.readline()

    return instructors


#--- Read the list of courses
#
# Each course entry has the following format:
#
# CMS_230_1 1 0
# 1 : 01 : 2 3 10 86 147 : : BUSH_310 BUSH_212 BUSH_302 BUSH_301 BUSH_102 : : 18 : Myers_Daniel
#
# The first line is the name of the course with the section number appended;
# labs will have an 'L' in the course name. The values 1 and 0 are required
# by the old schedulers and are fixed.
#
# The first two fields of the second line are always 1 and 01, respectively.
# The third field gives the ID numbers of the acceptable timeslots.
# The fourth field is the preferred timeslot, if any.
# The fifth field is the list of acceptable rooms.
# The seventh field is the course cap.
# The eigth field is the instructor name.
#
# The older schedulers used one heading for a course, then listed all
# sections and labs as separate entries under that heading. Our current
# approach favors treating each *section* as a separated entry; all
# sections and labs of the same course are distinguished by adding the
# section number to the course name.
#
# This approach better reflects the basic structure of the problem:
# each section represents a unique vertex in the graph which has
# edges connecting it to other sections.
def read_courses(f):

    courses = {}

    line = f.readline()

    while line.strip() != '':
        new_course = {}

        fields = line.split(' ')
        course_name = fields[0]
        new_course['name'] = course_name

        info = f.readline().strip().split(':')

        # The timeslot id and room lists begin and end with a single
        # space, creating empty strings as the first and last entries
        # in each list after splitting on a single space

        # Convert timeslots to int
        timeslots = info[2].split(' ')
        timeslots = timeslots[1:len(timeslots) - 1]
        new_course['acceptable_timeslots'] = [int(x) for x in timeslots]

        # Code to deal with preferred room could go here

        # Room list
        rooms = info[4].split(' ')
        new_course['acceptable_rooms'] = rooms[1:len(rooms) - 1]

        # Strip the leading space from the instructor name
        new_course['instructor'] = info[7][1:]

        courses[course_name] = new_course

        # Read the first line of the next course entry
        line = f.readline()

    # Read one extra line
    f.readline()

    return courses


#--- Read courses from the Fall 2011 input files
#
# These files have sections of each course listed under the course name
# Labs are also listed under the course name
def read_courses_fall_2011(f):
    
    courses = {}

    line = f.readline()

    while line.strip() != '':
        fields = line.split(' ')
        base_course_name = fields[0]
        num_lectures = int(fields[1])
        num_labs = int(fields[2])
        
        # Fall 2011 lectures with lab section have an additional entry
        # that must be skipped
        if num_labs > 0:
            lab_offset = 1
        else:
            lab_offset = 0

        for i in range(num_lectures):
            new_course = {}
            info = f.readline().strip().split(':')
            
            course_name = base_course_name + '_' + str(i + 1)
            new_course['name'] = course_name
            
            # Convert timeslots to int
            timeslots = info[2 + lab_offset].split(' ')
            timeslots = timeslots[1:len(timeslots) - 1]
            new_course['acceptable_timeslots'] = [int(x) for x in timeslots]

            # Code to deal with preferred timeslot could go here
            preferred_timeslots = info[3 + lab_offset].split()
            preferred_timeslots = preferred_timeslots[1:len(timeslots) - 1]
            new_course['preferred_timeslots'] = [int(x) for x in preferred_timeslots]


            # Room list
            rooms = info[4 + lab_offset].split(' ')
            new_course['acceptable_rooms'] = rooms[1:len(rooms) - 1]

            # Strip the leading space from the instructor name
            new_course['instructor'] = info[7 + lab_offset][1:]

            courses[course_name] = new_course
            
            print course_name, timeslots, new_course['acceptable_rooms'], new_course['instructor']
                        
        for i in range(num_labs):  
            new_course = {}
            info = f.readline().strip().split(':')
            
            course_name = base_course_name + '_' + str(i + 1) + '_' + 'LAB'
            new_course['name'] = course_name
            
            # Convert timeslots to int
            timeslots = info[2].split(' ')
            timeslots = timeslots[1:len(timeslots) - 1]
            new_course['acceptable_timeslots'] = [int(x) for x in timeslots]

            # Code to deal with preferred timeslot could go here
            preferred_timeslots = info[3].split()
            preferred_timeslots = preferred_timeslots[1:len(timeslots) - 1]
            new_course['preferred_timeslots'] = [int(x) for x in preferred_timeslots]
            
            # Room list
            rooms = info[4].split(' ')
            new_course['acceptable_rooms'] = rooms[1:len(rooms) - 1]

            # Strip the leading space from the instructor name
            new_course['instructor'] = info[7][1:]

            courses[course_name] = new_course  
            
            print course_name, timeslots, new_course['acceptable_rooms'], new_course['instructor']


        # First line of the next entry
        line = f.readline()

    # Read two extra lines
    f.readline()
    f.readline()

    return courses
    

#--- Read the list of course conflict pairs
#
# Returns: a list of tuples of the form
# (course1, course2, conflict penalty weight, overlap weight)
def read_conflicts(f):
    conflicts = []

    line = f.readline()

    while line.strip() != '':
        line = line.strip()
        fields = line.split(' ')

        course_1 = fields[0]
        course_2 = fields[1]
        severities = fields[2].split(',')
        conflict_weight = severities[0]
        overlap = int(severities[1])

        conflicts.append((course_1, course_2, conflict_weight, overlap))

        line = f.readline()

    return conflicts


def convert_conflicts(vertices, conflicts):
    new_conflicts = []
    
    for c1, c2, weight, overlap in conflicts:
        print c1, c2, weight, overlap
        
        c1_sections = [x for x in vertices if c1 in vertices[x]['name']]
        c2_sections = [x for x in vertices if c2 in vertices[x]['name']]
        
        num_c1_sections = len([x for x in c1_sections if 'LAB' not in x])
        num_c2_sections = len([x for x in c2_sections if 'LAB' not in x])

        for section_1 in c1_sections:
            for section_2 in c2_sections:
                divisor = max(num_c1_sections, num_c2_sections)
                #if weight == 'H':
                #    divisor = min(divisor, 6)
                #elif weight == 'M':
                #    divisor = min(divisor, 4)
                #elif weight == 'L':
                #    divisor = min(divisor, 2)
                
                divided_overlap = overlap / divisor
                print num_c1_sections, num_c2_sections, divisor
                
                output_weight = weight
                output_overlap = overlap
                
                if weight == 'H':
                    if (divided_overlap <= 2 or
                        ('CHM_220' in section_1 and 'BIO_308' not in section_2) or
                        ('CHM_220' in section_2 and 'BIO_308' not in section_1) or
                        ('BIO_100' in section_1 and 'CHM_120' in section_2) or
                        ('BIO_100' in section_2 and 'CHM_120' in section_1) or
                        ('BIO_121' in section_1 and 'CHM_120' in section_2) or
                        ('BIO_121' in section_2 and 'CHM_120' in section_1) or
                        ('BIO_201' in section_1 and 'CHM_120' in section_2) or
                        ('BIO_201' in section_2 and 'CHM_120' in section_1) or
                        ('CMS_167' in section_1 and 'MAT_111' in section_2) or
                        ('CMS_167' in section_2 and 'MAT_111' in section_1) or
                        ('CMS_167' in section_1 and 'MAT_301' in section_2) or
                        ('CMS_167' in section_2 and 'MAT_301' in section_1) or
                        ('PHY_120' in section_1 and 'BIO_121' in section_2) or
                        ('PHY_120' in section_2 and 'BIO_121' in section_1)):
                        output_weight = 'L'
                        output_overlap = 2
                    elif divided_overlap <= 6:
                        output_weight = 'M'
                        output_overlap = 6
                    else:
                        output_weight = 'H'
                        output_overlap = 12
                    
                new_conflicts.append((section_1, section_2, output_weight, output_overlap))
                print '\t', new_conflicts[-1]
    return new_conflicts

#--- Creates a data structure storing the conflicting edges for each course
#
# Conflicts may exist over an instructor or because a specific
# conflict pair is listed in the input file_name
#
# vertices: a dictionary of course entries
# conflicts: a list of all conflict pairs
#
# Returns: a dictionary with an entry for each course storing that
# course's conflicts
#
# There are really three kinds of conflicts:
#   1. an instructor conflict, which is given a prohibitively high penalty
#   2. the regular conflict penalty, which reflects the co-enrollment
#      between the course pairs
#   3. the overlap factor, which also reflects the co-enrollment
#      between the pairs and is used in calculating the proximity penalty
def build_edges(vertices, conflicts):
    edges = {}

    for course_name in vertices:

        course_info = vertices[course_name]

        # Each entry in edges is a dictionary keyed to the names
        # of courses that have a conflict
        edges[course_name] = {}

        # Identify all courses with the same instructor
        for candidate_name in vertices:

            # A course cannot be in conflict with itself
            if candidate_name == course_name:
                continue

            candidate_info = vertices[candidate_name]

            if course_info['instructor'] == candidate_info['instructor']:
                edges[course_name][candidate_name] = {}
                edges[course_name][candidate_name]['conflict'] = 'I'
                edges[course_name][candidate_name]['overlap'] = INSTRUCTOR_OVERLAP_WEIGHT

        # Identify all courses in the conflict list that have this
        # course as one member of a pair
        for conflict_entry in conflicts:

            # The two courses in the conflict entry
            course_1 = conflict_entry[0]
            course_2 = conflict_entry[1]

            # Check both courses in the conflict entry for a match
            if course_1 == course_name:

                # If the course pair does not have an entry, it was not previously
                # considered as an instructor conflict
                if course_2 not in edges[course_name]:
                    edges[course_name][course_2] = {}
                    edges[course_name][course_2]['conflict'] = conflict_entry[2]
                    edges[course_name][course_2]['overlap'] = conflict_entry[3]

                # If it does have an entry, add the overlap from the conflict entry
                # to the instructor overlap weight
                else:
                    edges[course_name][course_2]['overlap'] += conflict_entry[3]

            elif course_2 == course_name:
                if course_1 not in edges[course_name]:
                    edges[course_name][course_1] = {}
                    edges[course_name][course_1]['conflict'] = conflict_entry[2]
                    edges[course_name][course_1]['overlap'] = conflict_entry[3]

                else:
                    edges[course_name][course_1]['overlap'] += conflict_entry[3]

    return edges


#--- Look for alternate valid timeslots that improve the penalty
def improve(solution, vertices, edges, overlapping_timeslots, timeslot_gaps):
            
    # Sort the vertices by penalty
    penalties = []
    
    for vertex in solution:
        
        assigned_timeslot = solution[vertex]['assigned_timeslot']
        conflict_penalty = conflict_penalty_increase(vertex, assigned_timeslot, vertices)
        proximity_penalty = proximity_penalty_increase(vertex, assigned_timeslot, vertices)
        total_penalty = CONFLICT_PENALTY_WEIGHT * conflict_penalty + PROXIMITY_PENALTY_WEIGHT * proximity_penalty

        penalties.append(total_penalty)
        
    course_order = [y for (x, y) in sorted(zip(penalties, vertices.keys()), reverse = True)]
                
    # Process from highest penalty vertex to lowest
    for vertex in course_order:
        
        assigned_timeslot = solution[vertex]['assigned_timeslot']
        assigned_room = solution[vertex]['assigned_room']

        conflict_penalty = conflict_penalty_increase(vertex, assigned_timeslot, vertices)
        proximity_penalty = proximity_penalty_increase(vertex, assigned_timeslot, vertices)
        
        total_penalty = (CONFLICT_PENALTY_WEIGHT * conflict_penalty 
                         + PROXIMITY_PENALTY_WEIGHT * proximity_penalty)
        
        for s in vertices[vertex]['acceptable_timeslots']:
                            
            room_list = get_available_rooms(vertex, s, solution, vertices, overlapping_timeslots)

            if len(room_list) == 0:
                continue
                
            test_conflict_penalty = conflict_penalty_increase(vertex, s, vertices)
            test_proximity_penalty = proximity_penalty_increase(vertex, s, vertices)
            test_total_penalty = (CONFLICT_PENALTY_WEIGHT * test_conflict_penalty 
                             + PROXIMITY_PENALTY_WEIGHT * test_proximity_penalty)
                                                          
            if test_total_penalty < total_penalty:
                new_room = room_list[0]
                                           
                vertices = update_penalties_and_room_lists(vertex, assigned_timeslot, assigned_room, vertices, solution,
                                                            edges, overlapping_timeslots, timeslot_gaps,
                                                            deallocate = True)
                                                                                                                        
                vertices = update_penalties_and_room_lists(vertex, s, new_room, vertices, solution,
                                                            edges, overlapping_timeslots, timeslot_gaps)
                
                conflict_penalty = test_conflict_penalty
                proximity_penalty = test_proximity_penalty
                total_penalty = test_total_penalty
                
                solution[vertex]['assigned_timeslot'] = s
                solution[vertex]['assigned_room'] = new_room
                                
                assigned_timeslot = solution[vertex]['assigned_timeslot']
                assigned_room = solution[vertex]['assigned_room']
                
    return solution
    
    
#--- Read a .ctb input file and build the couse_info dictionary
#
# The .ctb file format is backwards-compatible with the earlier
# Java-based timetable solvers
def schedule_ctb_file(input_file_name):
        
    f = open(input_file_name, 'r')
        
    read_parameters_block(f)    
    room_list = read_room_list(f)
    print room_list
    timeslot_list = read_timeslot_list(f)
    print timeslot_list
    course_prefix_list = read_course_prefixes(f)
    instructor_list = read_instructors(f)
    
    if 'f11' in input_file_name:
        vertices = read_courses_fall_2011(f)
    else:
        vertices = read_courses(f)
    
    conflicts = read_conflicts(f)
    
    if 'f11' in input_file_name:
        conflicts = convert_conflicts(vertices, conflicts)
    
    # Each vertex has a list of the remaining unassigned rooms at each
    # of its suitable timeslots and a record of the conflict and
    # proximity penalties that would be incurred by the assignment
    # of each suitable timeslot
    for course in vertices:
        for timeslot in vertices[course]['acceptable_timeslots']:
            vertices[course][timeslot] = {}
            vertices[course][timeslot]['unassigned_rooms'] = copy.copy(vertices[course]['acceptable_rooms'])
            
            vertices[course][timeslot]['conflict_penalty'] = 0.0
            vertices[course][timeslot]['proximity_penalty'] = 0.0

    # Build the structure of conflicting edges
    edges = build_edges(vertices, conflicts)
    
    # Build a dict reporting whether pairs of timeslots overlap and
    # a dict reporting the gaps between pairs of timeslots
    overlapping_timeslots, timeslot_gaps = calculate_overlapping_timeslots_and_gaps(timeslot_list)
        
    # Solve
    if USE_ONE_PASS:
        solution = one_pass_solver(vertices, edges, overlapping_timeslots, timeslot_gaps)
    else:
        solution, vertices = priority_queue_solver(vertices, edges, overlapping_timeslots, timeslot_gaps)
        
    penalty = calculate_total_penalty(solution, edges, overlapping_timeslots, timeslot_gaps, vertices)
    print 'Total penalty before improvement: ', penalty

    for improve_count in range(10):
        solution = improve(solution, vertices, edges, overlapping_timeslots, timeslot_gaps)

    # Output the solution
    courses_without_rooms = 0
    
    solution_keys = solution.keys()
    solution_keys.sort()
    for course in solution_keys:
        slot = solution[course]['assigned_timeslot']
        room = solution[course]['assigned_room']
        #print course, slot, room
        
        if room == None:
            courses_without_rooms += 1
                            
    # Calculate and report the penalty
    global PRINT_CONFLICTS
    PRINT_CONFLICTS = True
    penalty = calculate_total_penalty(solution, edges, overlapping_timeslots, timeslot_gaps, vertices)
    PRINT_CONFLICTS = False
    
    print 'Total penalty including unscheduled courses: ', penalty
    
    print 'Number of unscheduled courses = ', courses_without_rooms
    
    return penalty


#--- Solve an input course file using a supplied vector of parameters
#
# This is the entry point into the solver for the DEAP genetic algorithm library
def schedule_ctb_file_with_parameters(individual, file_path):
    
    #global LINEAR_COMBO_CONFLICT
    #global LINEAR_COMBO_PROXIMITY
    #global LINEAR_COMBO_GOOD_TO_BAD_SWITCH
    #global CONFLICT_PENALTY_THRESHOLD
    #global PROXIMITY_PENALTY_THRESHOLD
    
    global PRIORITY_TOTAL_PENALTY_WEIGHT
    global PRIORITY_TOTAL_BAD_VALUE_WEIGHT
    global PRIORITY_TOTAL_EDGE_WEIGHT
    global PRIORITY_NUM_EDGES_WEIGHT
    global PRIORITY_BAD_VALUE_OF_EDGES
    
    # Set global parameters
    PRIORITY_TOTAL_PENALTY_WEIGHT = individual[0]
    PRIORITY_TOTAL_BAD_VALUE_WEIGHT = individual[1]
    PRIORITY_TOTAL_EDGE_WEIGHT = individual[2]
    PRIORITY_NUM_EDGES_WEIGHT = individual[3]
    PRIORITY_BAD_VALUE_OF_EDGES = individual[4]

    return schedule_ctb_file(file_path)
    

#--- Main
if __name__ == "__main__":

    #base_dir = '/Users/dmyers/Desktop/Research/DanJay_Timetabling/Test_Problems_3_to_7_Choices/'
    #file_name = 'Course_Schedules_Fall_2015_'
    
    #base_dir =  '/Users/dmyers/Dropbox/DanJayRuz/Code/CT_Data/'
    #file_name = 'rol_f11_unsch_no_preferences.ctb'

    base_dir = './'
    file_name = 'Course_Schedules_Fall_2015.ctb'

    schedule_ctb_file(base_dir + file_name)

    #s = 0
    #for i in range(10):
    #    full_path = base_dir + file_name + str(i + 0) + '.ctb'
    #    start_time = time.time()
    #    result = schedule_ctb_file(full_path)
    #    end_time = time.time()
    #    print 'Elapsed time: ', str(end_time - start_time)
    #    print full_path, result, '\n'
        
    #    s += result
    
    #print str(s / 10)


    