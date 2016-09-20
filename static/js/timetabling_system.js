// Timetabling System application control logic
// Neeraj Chatlani and D.S. Myers, 2016


// Creates new course sections
//
// Called when:
//   the Save button in the create course modal dialog is pressed.
//
// Effects:
//   Reads the appropriate fields from the modal dialog
//   Creates new list entries for each section (lecture and lab)
//   Inserts those list entries into the course listing
//   Sends information on the new sections to the server, which adds
//     entries for them to its data store
//   
// Inputs:
//   None
//
// Returns:
//   Nothing
function createNewSections() {
  var coursePrefix = $("#dialog_course_prefix").val().toUpperCase();
  var courseNumber = $("#dialog_course_number").val();
  var courseTitle = $("#dialog_course_title").val();
  var numLectures = $("#dialog_num_lectures").val();
  var numLabs = $("#dialog_num_labs").val();
  
  // List of new section names
  var sectionNames = [];
  
  //values to check if course is Holt or Crosslisted
  var holt = "";
  var cross = "";
  var holt_course = "";
  var cross_course = "";
  
  var is_holt = $("#holt_radio").is(' :checked');
  var is_cross = $("#crosslisted_checkbox").is(' :checked');
  
  if (is_holt == true){
    holt = "H";
    holt_course = "H";
  }
  
  if (is_cross == true){
    cross = "X";
    cross_course = "X";
  }

  // Get a reference to the list of sections
  var sectionList = $("#list_of_created_sections");
  var courseList = $("")
    
  // Create <button> items for the lecture sections
  for (var i = 0; i < numLectures; i++) {    
    var sectionName = coursePrefix + " " + courseNumber + " - Lecture " + holt + (i + 1) + cross;
    sectionNames.push(sectionName);
    
    var newListNode = document.createElement("button");
    newListNode.type = "button";
    newListNode.classList.add("list-group-item");
    newListNode.classList.add("section_list_entry");
    var newTextNode = document.createTextNode(sectionName)
    
    newListNode.appendChild(newTextNode);
    sectionList.append(newListNode);
  }
  
  // Create <button> items for the lab sections
  for (var i = 0; i < numLabs; i++) {    
    var sectionName = coursePrefix + " " + courseNumber + " - Lab " + holt + (i + 1) + cross;
    sectionNames.push(sectionName);
    
    var newListNode = document.createElement("button");
    newListNode.type = "button";
    newListNode.classList.add("list-group-item");
    newListNode.classList.add("section_list_entry");
    var newTextNode = document.createTextNode(sectionName);
    
    newListNode.appendChild(newTextNode);
    sectionList.append(newListNode);
  }
  
  // Populate the list of course prefixes and numbers in the "Course Creation" pane
  var newListNode = document.createElement("button");
  newListNode.type = "button";
  newListNode.classList.add("list-group-item");
  newListNode.classList.add("course_list_entry");
  
  // Add Holt and/or crosslisted designations
  if ((is_holt == false) && (is_cross == false)){
    var newTextNode = document.createTextNode(coursePrefix + ' ' + courseNumber);
  } else if ((is_holt == true) && (is_cross == false)){
    var newTextNode = document.createTextNode(coursePrefix + ' ' + courseNumber + " - " + holt_course);
  }  else if ((is_holt == false) && (is_cross == true)){
    var newTextNode = document.createTextNode(coursePrefix + ' ' + courseNumber + " - " + cross_course);
  } else if ((is_holt == true) && (is_cross == true)){
    var newTextNode = document.createTextNode(coursePrefix + ' ' + courseNumber + " - " + holt_course + "/" + cross_course);
  }
  
  newListNode.appendChild(newTextNode);
  $("#list_of_created_courses").append(newListNode);
  
  // Add the course's prefix to the prefix filter list
  // If it does not already exist in the list
  var queryString = "#prefix_filter_box option[value='" + coursePrefix + "']"
  
  if($(queryString).length == 0){
    var newOption = document.createElement("option");
    newOption.innerHTML = coursePrefix;
    newOption.value = coursePrefix;
    $("#prefix_filter_box").append(newOption);
  }
  
  
  // Create an object with section names as its fields
  var newSections = {"prefix" : coursePrefix, "number": courseNumber, 
                     "title": courseTitle, "names" : sectionNames,
                     "is_holt" : is_holt, "is_cross" : is_cross};
                     
  // Send an update to the server with the new section names
  $.ajax({
    url: '/create_new_sections',
    type: 'POST',
    contentType:'application/json',
    data: JSON.stringify(newSections),
    dataType:'json',
    success: function() {
      
      //Refresh the course and section columns with the new course's info
      fillListofSections();
      getPrefixes();
    }
  });
}


// Displays information for a course section in the right-hand pane
//
// Called when:
//   a section button in the left-hand list is clicked
//
// Effects:
//   makes the clicked button the only active button
//   makes the right-hand panel visible if it's not already
//
// Input:
//   a reference to the clicked element
//
// Returns:
//   Nothing.
function showSectionInfo(clicked) {
  
  // Remove the active class from any other section entry
  $('.section_list_entry').each(function() {
    $(this).removeClass("active");
  });
  
  // Add the active class to the clicked entry
  $(clicked).addClass("active");
  
  // Make the right-hand pane visible
  $("#section_info_input_column").removeClass("hidden");
  
  // Get the text of the clicked button element
  var sectionName = $(clicked).text();
  $("#section_name_in_input_panel").text(sectionName);
  
  // Send an update to the server to get any information that it has
  // on this section
  var sectionNameObject = {"name" : sectionName};
  
  $.ajax({
    url: '/get_section_information',
    type: 'POST',
    contentType:'application/json',
    data: JSON.stringify(sectionNameObject),
    dataType:'json',
    success: function(d) {
      // Set course title
      var title = d.course_title;
      $("#title_entry_box").val(title);
      
      // Set instructor
      var instructor = d.instructor;
      if (instructor != '') {
        $('#instructor_select_box').val(instructor);
      } else {
        $('#instructor_select_box').val('-- Select --');
      }
      
      // Set list of acceptable rooms
      rooms = d.acceptable_rooms;
      
      var roomList = $("#acceptable_rooms_list");
      roomList.empty();
      
      for (var i = 0; i < rooms.length; i++){
        var newListNode = document.createElement("button");
        newListNode.type = "button";
        newListNode.classList.add("list-group-item");
        newListNode.classList.add("acceptable_room_item");

        var newTextNode = document.createTextNode(rooms[i]);
    
        newListNode.appendChild(newTextNode);
        roomList.append(newListNode);
      }
      
      // Set list of acceptable timeslots
      timeslots = d.acceptable_timeslots;
      
      var timeslotList = $("#acceptable_timeslots_list");
      timeslotList.empty();
      
      for (var i = 0; i < timeslots.length; i++){
        var newListNode = document.createElement("button");
        newListNode.type = "button";
        newListNode.classList.add("list-group-item");
        newListNode.classList.add("acceptable_timeslot_item");

        var newTextNode = document.createTextNode(timeslots[i]);
    
        newListNode.appendChild(newTextNode);
        timeslotList.append(newListNode);
      }     
      
      // Fill the remaining available rooms and timeslots using the current
      // values of the selection boxes
      fillAvailableRoomList();
      fillAvailableTimeslotList();
    }
  });
  
  $.ajax({
    url: '/get_conflicts',
    type: 'POST',
    contentType:'application/json',
    data: JSON.stringify(sectionNameObject),
    dataType:'json',
    success:function(d){
      
      $("#conflicting_courses_list").empty();
      
      for (var i = 0; i < d.conflicts.length; i++) {
        var btnGroupDiv = document.createElement('div');
        $(btnGroupDiv).addClass("btn-group");
        $(btnGroupDiv).addClass("btn-group-justified");
      
        var dropdown = document.createElement("div");
        $(dropdown).addClass("btn-group");
        dropdown.innerHTML = '<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">'
                              + d.severities[i]
                              + '<span class="caret"></span></button>';
        dropdown.innerHTML += '<ul class="dropdown-menu">'
                            + '<li><a class="severity_menu_item">Heavy</a></li>'
                            + '<li><a class = "severity_menu_item">Medium</a></li>'
                            + '<li><a class = "severity_menu_item">Light</a></li></ul>';
      
        var btnGroupForButton = document.createElement("div");
        $(btnGroupForButton).addClass("btn-group");
        
        var button = document.createElement("button");
        $(button).text(d.conflicts[i]);
        $(button).addClass("btn");
        $(button).addClass("list-group-item");
        $(button).addClass("btn-default");
        $(button).addClass("conflicting_list_entry");

        $(dropdown).appendTo(btnGroupDiv);
        $(button).appendTo(btnGroupForButton);
        $(btnGroupForButton).appendTo(btnGroupDiv);
        $(btnGroupDiv).appendTo("#conflicting_courses_list");
      }
    }
  });
}



// Displays information for a course in the "Scheduling and Editing" pane
//
// Called when:
//   a course button in the left-hand list is clicked
//
// Effects:
//   makes the clicked button the only active button
//   makes the right-hand panel visible if it's not already
//
// Input:
//   a reference to the clicked element
//
// Returns:
//   Nothing.
function showScheduledSectionInfo(clicked) {

  // Remove the active class from any other section entry
  $('.scheduled_list_entry').each(function() {
    $(this).removeClass("active");
  });
  
  // Add the active class to the clicked entry
  $(clicked).addClass("active");
  
  // Make the right-hand pane visible
  $("#scheduled_info_column").removeClass("hidden");
  
  // Get the text of the clicked button element
  var sectionName = $(clicked).text();
  $("#section_name_in_schedule_panel").text(sectionName);
  
  // AJAX request for assigned timeslot and room
  var request = {'name' : sectionName}
  
  $.ajax({
    url: '/get_assigned_timeslot_room_and_conflicts',
    type: 'POST',
    contentType:'application/json',
    data: JSON.stringify(request),
    dataType:'json',
    success: function(d) {
      $('#assigned_timeslot_span').text(d.assigned_timeslot);
      $('#assigned_room_span').text(d.assigned_room.replace('_', ' '));
      
      $("#heavy_conflicts_list").empty();
      $("#medium_conflicts_list").empty();
      $("#light_conflicts_list").empty();

      
      for (var i = 0; i < d.heavy_conflicts.length; i++) {
        var newListNode = document.createElement("button");
        newListNode.type = "button";
        newListNode.classList.add("list-group-item");
        var newTextNode = document.createTextNode(d.heavy_conflicts[i]);
        newListNode.appendChild(newTextNode);
        $("#heavy_conflicts_list").append(newListNode);
      }
      
      for (var i = 0; i < d.medium_conflicts.length; i++) {
        var newListNode = document.createElement("button");
        newListNode.type = "button";
        newListNode.classList.add("list-group-item");
        var newTextNode = document.createTextNode(d.medium_conflicts[i]);
        newListNode.appendChild(newTextNode);
        $("#medium_conflicts_list").append(newListNode);
      }
      
      for (var i = 0; i < d.light_conflicts.length; i++) {
        var newListNode = document.createElement("button");
        newListNode.type = "button";
        newListNode.classList.add("list-group-item");
        var newTextNode = document.createTextNode(d.light_conflicts[i]);
        newListNode.appendChild(newTextNode);
        $("#light_conflicts_list").append(newListNode);
      }
    }
  });
}

// Displays information for a course in the "Create Course" pane
//
// Called when:
//   a course button in the left-hand list is clicked
//
// Effects:
//   makes the clicked button the only active button
//   makes the right-hand panel visible if it's not already
//
// Input:
//   a reference to the clicked element
//
// Returns:
//   Nothing.
function showCourseInfo(clicked) {
  
  // Remove the active class from any other section entry
  $('.course_list_entry').each(function() {
    $(this).removeClass("active");
  });
  
  // Add the active class to the clicked entry
  $(clicked).addClass("active");
  
  // Make the right-hand pane visible
  $("#course_info_column").removeClass("hidden");
  
  // Get the text of the clicked button element
  var courseName = $(clicked).text();
  $("#course_name_in_info_panel").text(courseName);
  
  // Send an update to the server to get any information that it has
  // on this section
  var courseNameObject = {"name" : courseName};
  
  
  //Get course titles and add them to the display in the Create Courses tab
  $.ajax({
    url: '/get_course_information',
    type: 'POST',
    contentType:'application/json',
    data: JSON.stringify(courseNameObject),
    dataType:'json',
    success: function(d) {
      
      var courseTitle = d.course_title;
      
      /**if (courseName.includes('Holt') && courseName.includes('Crosslisted')) {
        courseTitle += ' - Holt/Crosslisted';
      } else if (courseName.includes('Holt')) {
        courseTitle += ' - Holt';
      } else if (courseName.includes('Crosslisted')) {
        courseTitle += ' - Crosslisted'
      }**/
      
      $("#course_title_in_info_panel").text(courseTitle)
      $("#num_lectures_in_info_panel").text(d.num_lectures);
      $("#num_labs_in_info_panel").text(d.num_labs);
    }
  });

}

// Updates the server-side database information for one section
//
// Called when:
//   any section information element changes or the "Save" button is clicked
//
// Effects:
//   pulls section information content from the page and sends it to the server
//
// Inputs:
//   None.
//
// Returns:
//   Nothing.
function updateSectionInformation(){
  
  // Get 'instructor name' and 'course title' field values
  var sectionName = $("#section_name_in_input_panel").text();
  var instructorName = $("#instructor_select_box").val();
  var courseTitle = $("#title_entry_box").val();
  if (instructorName == "-- Select --"){
    instructorName = "";
  }
  
  // Get the acceptable rooms
  var acceptableRoomList = [];
  $(".acceptable_room_item").each(function() {
    var roomText = $(this).text();
    acceptableRoomList.push(roomText);
  });
  
  // Get the acceptable timeslots
  var acceptableTimeslotList = [];
  $(".acceptable_timeslot_item").each(function() {
    var timeslotText = $(this).text();
    acceptableTimeslotList.push(timeslotText);
  });
  
  //Get the possible conflicts and their severity
  var conflictingCourses = [];
  var severities = [];
  $(".conflicting_list_entry").each(function() {
    var dropdown_siblings = $(this).parent().siblings().children();
    var dropdown = dropdown_siblings[0];
    conflictingCourses.push($(this).text());
    severities.push($(dropdown).text());
  });
  
  var section_info = {"instructor" : instructorName, "course_title" : courseTitle,
                      "section_name" : sectionName, "acceptable_rooms" : acceptableRoomList,
                      "acceptable_timeslots" : acceptableTimeslotList,
                      "conflicting_courses" : conflictingCourses,
                      "severities" : severities};
  
  // AJAX request to update database information for this section
   $.ajax({
    url: '/save_section_information',
    type: 'POST',
    contentType:'application/json',
    data: JSON.stringify(section_info),
    dataType:'json'
   });  
}


// Sorts section names alphabetically by prefix, then by number,
// then by lecture/lab, lastly by section number
//
// Called when:
//  Sorting the existing courses on page load
//
// Input:
//  a: a section name string of the form 'CMS 167 - Lecture 1'
//  b: a second section name string
//
// Returns:
//   -1 if a comes before b
//    1 if b bomes before a
//    0 if they're equal
function compareCourseNames(a, b){
  var splitA = a.split(" ");
  var splitB = b.split(" ");
  
  // First element: course prefix
  if (splitA[0] > splitB[0]) {
    return 1;
  } else if (splitA[0] < splitB[0]) {
    return -1;
  }
  
  // Second element: course number
  aNum = parseInt(splitA[1]);
  bNum = parseInt(splitB[1]);
  
  if (aNum > bNum){
    return 1;
  } else if (aNum < bNum){
    return -1;
  }
  
  // Fourth element: Lecture or Lab (third element is "-" from split)
  if ((splitA[3] == "Lecture") && (splitB[3] == "Lab")){
    return -1;
  } else if ((splitA[3] == "Lab") && (splitB[3] == "Lecture")){
    return 1;
  }
  
  // Fifth element: section number
  aCourseNum = parseInt(splitA[4]);
  bCourseNum = parseInt(splitB[4]);
  
  if (aCourseNum > bCourseNum){
    return 1;
  } else if (aCourseNum < bCourseNum){
    return -1;
  }
  
  // Default: return 0 on equality
  return 0;
}

// Fills the list of the available rooms in a given building for choosing 
// acceptable rooms in a section
//
// Called when:
//   The building filter box changes value
//
// Effects:
//   Populates the available rooms list with from the chosen building
//
// Input:
//  None
//
// Returns:
//  Nothing
//
function fillAvailableRoomList() {
  // Get the current value of the box
  var building = $("#building_filter_box").val();
  var requestObject = {"building" : building};
  
  // Request the list of rooms in the building
  $.ajax({
    url: '/get_rooms_by_building',
    type: 'POST',
    contentType:'application/json',
    data: JSON.stringify(requestObject),
    dataType:'json',
    success:function(d){
      rooms = d.rooms;
      rooms.sort();
      
      // Get a reference to the available room list
      var roomList = $("#available_rooms_list");
      roomList.empty();
      
      for (var i = 0; i < rooms.length; i++){
        
        // Skip this available room if it's already in the acceptable rooms list
        var skip = false;
        $(".acceptable_room_item").each(function() {
          if (rooms[i] == $(this).text()) {
            skip = true;
          }
        });
        
        if (skip) {
          continue;
        }
        
        //Add each room as a button to the list
        var newListNode = document.createElement("button");
        newListNode.type = "button";
        newListNode.classList.add("list-group-item");
        newListNode.classList.add("available_room_item");
        var newTextNode = document.createTextNode(rooms[i]);
    
        newListNode.appendChild(newTextNode);
        roomList.append(newListNode);
      }
    }
  });
  
}

// Fills the list of sections in the Course Details tab 
// with sections from a given prefix
//
// Called when:
//   the prefix filter box changes value
//
// Effects:
//   Fills the Course Details tab's section list with sections of that prefix
//
// Input:
//   None
//
// Returns:
//   Nothing
function getSectionsByPrefix(prefix, secListString){
  
  //Get the value of the prefix filter
  //var prefix = $("#prefix_filter_box").val();
  var requestObject = {"prefix" : prefix};
  
  //Request the list of sections from the server
  $.ajax({
    url: '/get_sections_by_prefix',
    type: 'POST',
    contentType:'application/json',
    data: JSON.stringify(requestObject),
    dataType:'json',
    success: function(d){
      sections = d.sections;
      sections.sort();
      
      //Empty the section list and add the received section list
      secList = $(secListString);
      secList.empty();
      
      for(var i = 0; i < sections.length; i++){
        
        var newListNode = document.createElement("button");
        newListNode.type = "button";
        newListNode.classList.add("list-group-item");
        
        if (secListString == '#list_of_scheduled_sections') {
          newListNode.classList.add("scheduled_list_entry");
        } else {
          newListNode.classList.add("section_list_entry");
        }
        var newTextNode = document.createTextNode(sections[i]);
    
        newListNode.appendChild(newTextNode);
        secList.append(newListNode);
        
      }
    }
  
  });
}

// Fills the list of possible conflicts with courses having a selected prefix
//
// Called when:
//   the filter box in the conflict section changes value
//
// Effects:
//   Fills the Course Details tab's section list with sections of that prefix
//
// Input:
//   None
//
// Returns:
//   Nothing
function getCoursesByPrefix(){
  var prefix = $("#course_filter_box").val();
  
  if (prefix.indexOf("Select") >= 0) {
    $("#conflict_courses_list").empty();
    return;
  }
  
  var requestObject = {"prefix" : prefix};
  
  $.ajax({
    url: '/get_courses_by_prefix',
    type: 'POST',
    contentType:'application/json',
    data: JSON.stringify(requestObject),
    dataType:'json',
    success: function(d){
      courses = d.courses;
      courses.sort();
      var splitCourseNames = [courses.length];
      var courseNames = [];
      
      for(var i = 0; i < courses.length; i++){
        var fields = courses[i].split(" ");
        splitCourseNames[i] = fields[0] + " " + fields[1];
        
         if(fields[4].includes('H') && fields[4].includes('X')) {
          splitCourseNames[i] += ' - HX';
        } else if (fields[4].includes('H')) {
          splitCourseNames[i] += ' - H';
        } else if (fields[4].includes('X')) {
          splitCourseNames[i] += ' - X';
        }
      }
      
      var courseList = $("#conflict_courses_list");
      courseList.empty();
      
      // Identify the unique course names that are not already in the
      // list of conflicts
      for (var i = 0; i < splitCourseNames.length; i++){
        
        // Check courses in the current conflict list
        var skip = false;
        $(".conflicting_list_entry").each(function() {
          if($(this).text() == splitCourseNames[i]) {
            skip = true;
          }
        });
        
        // Check to ensure that the course itself is not available to select
        // as a duplicates
        var currentSection = $("#section_name_in_input_panel").text();
        var panelFields = currentSection.split(" ");
        var courseFields = splitCourseNames[i].split(" ");
        if((panelFields[0] + panelFields[1]) == (courseFields[0] + courseFields[1])){
          skip = true;
        }
        
        // Check for uniqueness
        if (courseNames.indexOf(splitCourseNames[i]) >= 0) {
          skip = true;
        }
        
        if (!skip) {
          courseNames.push(splitCourseNames[i]);
        }
      }
      
      for(var i = 0; i < courseNames.length; i++){
        
        var newListNode = document.createElement("button");
        newListNode.type = "button";
        newListNode.classList.add("list-group-item");
        newListNode.classList.add("conflict_list_entry");
        newListNode.classList.add("btn");
        var newTextNode = document.createTextNode(courseNames[i]);
    
        newListNode.appendChild(newTextNode);
        courseList.append(newListNode);
        
      }
    }
  });
}

// Fills the list of available timeslots based on a set time for given days
//
// Called when:
//   the filter box in the Timeslot section changes value
//
// Effects:
//   Fills the Timeslot List with all filtered timeslots
//
// Input:
//   None
//
// Returns:
//   Nothing
function fillAvailableTimeslotList() {
  // Get the current value of the box
  var category = $("#timeslot_filter_box").val();
  var requestObject = {"category" : category};
  
  // Request the list of rooms in the building
  $.ajax({
    url: '/get_timeslots_by_category',
    type: 'POST',
    contentType:'application/json',
    data: JSON.stringify(requestObject),
    dataType:'json',
    success:function(d){
      timeslots = d.timeslots;
      timeslots.sort(compareTimeslots);
      
      // Get a reference to the available room list
      var timeslotList = $("#available_timeslots_list");
      timeslotList.empty();
      
      for (var i = 0; i < timeslots.length; i++){
        
        // Skip this available timeslot if it's already in the acceptable timeslots list
        var skip = false;
        $(".acceptable_timeslot_item").each(function() {
          if (timeslots[i] == $(this).text()) {
            skip = true;
          }
        });
        
        if (skip) {
          continue;
        }
        
        var newListNode = document.createElement("button");
        newListNode.type = "button";
        newListNode.classList.add("list-group-item");
        newListNode.classList.add("available_timeslot_item");
        var newTextNode = document.createTextNode(timeslots[i]);
    
        newListNode.appendChild(newTextNode);
        timeslotList.append(newListNode);
      }
    }
  });
}

// Sorts timeslots numerically by listed time
//
// Called when:
//  
//
// Input:
//  a: a timeslot string of the form 'MWF 8:30 - 9:45'
//  b: a second timeslot string
//
// Returns:
//  -1 if a comes befor b
//  1 if b comes before a
//  0 if equal
//
function compareTimeslots(a, b){
  
  //Split input strings to get times, and split again to get hours in int form
  var splitA = a.split(" ");
  var splitB = b.split(" ");
  
  var numSplitA = parseInt(splitA[1].split(":"));
  var numSplitB = parseInt(splitB[1].split(":"));
  
  // Compare hours to sort numerically
  if (numSplitA[1] > numSplitB[1]) {
    return 1;
  } else if (numSplitA[1] < numSplitB[1]) {
    return -1;
  }
  
}


// Make a clicked element active and remove the active tag from any other
// member of the given class
function makeActive(clicked, memberClass) {
  // Remove the active class from any other section entry
  $(memberClass).each(function() {
    $(this).removeClass("active");
  });
  
  $(clicked).addClass("active");
}


function fillListofSections(){
  $("#list_of_created_courses").empty();
  $("#list_of_created_sections").empty();
  $("#list_of_scheduled_sections").empty();
  
  $.ajax({
    url: '/get_section_names',
    type: 'GET',
    contentType:'application/json',
    dataType:'json',
    success:function(d){
      names = d.names;
      names.sort(compareCourseNames);
      
      var courseNames = [];
      
      for (var i = 0; i < names.length; i++){
        var newListNode = document.createElement("button");
        newListNode.type = "button";
        newListNode.classList.add("list-group-item");
        newListNode.classList.add("section_list_entry");
        var newTextNode = document.createTextNode(names[i])
    
        newListNode.appendChild(newTextNode);
        $("#list_of_created_sections").append(newListNode);
        
        var scheduledListNode = $(newListNode).clone();
        $(scheduledListNode).removeClass("section_list_entry");
        $(scheduledListNode).addClass("scheduled_list_entry");
        $("#list_of_scheduled_sections").append(scheduledListNode);
        
        // Keep track of all the unique course names
        var fields = names[i].split(' ');
        var newCourseName = fields[0] + ' ' + fields[1];
        if (fields[4].includes('H') && fields[4].includes('X')) {
          newCourseName += ' - Holt/Crosslisted';
        } else if (fields[4].includes('H')) {
          newCourseName += ' - Holt';
        } else if (fields[4].includes('X')) {
          newCourseName += ' - Crosslisted';
        }
        
        if (courseNames.indexOf(newCourseName) < 0) {
          courseNames.push(newCourseName);
        }
      }
      
      // Enter the list of unique course names in the "Create Courses" pane
      courseNames.sort();
      
      var courseList = $("#list_of_created_courses");
      var conflictCourseList = $("#conflict_courses_list");
      
      for (var i = 0; i < courseNames.length; i++) {
        var newListNode = document.createElement("button");
        newListNode.type = "button";
        newListNode.classList.add("list-group-item");
        newListNode.classList.add("course_list_entry");
        var newTextNode = document.createTextNode(courseNames[i])
    
        newListNode.appendChild(newTextNode);
        courseList.append(newListNode);
      }
    }
  });
}

// Fills the list of prefixes in the prefix filter boxes
//
// Called when:
//   On load and when a new course is added
//
// Effects:
//   Fills the prefix and course filter boxes with stored prefixes
//
// Input:
//   None
//
// Returns:
//   Nothing
function getPrefixes(){
   
  $("#prefix_filter_box").empty();
  $("#course_filter_box").empty();
  $("#scheduling_prefix_filter_box").empty();
  
  // Re-append the initial "Select" option to the dropdowns
  var newSelect = document.createElement("option");
  newSelect.innerHTML = "-- Select --";
  newSelect.value = "-- Select --";
  $("#prefix_filter_box").append(newSelect);
  $("#prefix_filter_box").val("-- Select --");
  $("#course_filter_box").append($(newSelect).clone());
  $("#course_filter_box").val("-- Select --");
  $("#scheduling_prefix_filter_box").append($(newSelect).clone());
  $("#scheduling_prefix_filter_box").val("-- Select --");
  
   
   // Send a request to the server for the prefixes
   $.ajax({
    url: '/get_prefixes',
    type: 'GET',
    contentType:'application/json',
    dataType:'json',
    success: function(d) {
      var prefixes = d.prefixes;
      prefixes.sort();
      
      
      for (var i = 0; i < prefixes.length; i++) {
        var newOption = document.createElement("option");
        newOption.innerHTML = prefixes[i];
        newOption.value = prefixes[i];
        $("#prefix_filter_box").append(newOption);
        $("#course_filter_box").append($(newOption).clone());
        $("#scheduling_prefix_filter_box").append($(newOption).clone());
      }
    }
  });
}

function loadTimeslotRoomsAndConflicts(clicked) {
  // Remove the active class from any other alternate timeslot
  $('.modal_timeslot_item').each(function() {
    $(this).removeClass("active");
  });
  
  // Add the active class to the clicked entry
  $(clicked).addClass("active");
  
  var sectionName = $("#modal_section_name_span").text();
  var timeslot = $(clicked).text();
  
  // Get the available rooms_ and conflicts from the server
  request = {'name' : sectionName, 'timeslot' : timeslot}
   $.ajax({
    url: '/get_conflicts_and_rooms_at_timeslot',
    type: 'POST',
    contentType:'application/json',
    data: JSON.stringify(request),
    dataType:'json',
    success: function(d) {  
      fillButtonList(d.rooms, '#modal_available_rooms_list', ['modal_available_rooms_list_item']);
      fillButtonList(d.heavy_conflicts, '#modal_alternate_heavy_conflicts', []);
      fillButtonList(d.medium_conflicts, '#modal_alternate_medium_conflicts', []);
      fillButtonList(d.light_conflicts, '#modal_alternate_light_conflicts', []);

      // Set the current room to active if it exists
      $('.modal_available_rooms_list_item').each(function() {
        if ($(this).text() == $("#modal_assigned_room_span").text()) {
          $(this).addClass("active");
        }
      });
    }
  });
}


function fillButtonList(names, list, additionalClasses) {
  names.sort();
  $(list).empty();
  
  for (var i = 0; i < names.length; i++) {
    var newListNode = document.createElement("button");
    newListNode.type = "button";
    newListNode.classList.add("list-group-item");

    for (var c = 0; c < additionalClasses.length; c++) {
      $(newListNode).addClass(additionalClasses[c]);
    }
    
    var newTextNode = document.createTextNode(names[i])
    
    newListNode.appendChild(newTextNode);
    $(list).append(newListNode);       
  }
}


// MAIN --- code below here runs when the script is initially loaded

// Run when the page loads
// Get list of instructor names and existing section names from the server
$(document).ready(function() {
  
  fillListofSections();
  getPrefixes();
  
  $.ajax({
    url: '/get_instructor_names',
    type: 'GET',
    contentType:'application/json',
    dataType:'json',
    success: function(d) {
      names = d.names;
      names.sort();
      
      for (var i = 0; i < names.length; i++) {
        var newOption = document.createElement("option");
        newOption.innerHTML = names[i];
        newOption.value = names[i];
        $("#instructor_select_box").append(newOption);
      }
      
    }
  });
  
  $.ajax({
    url: '/get_buildings',
    type: 'GET',
    contentType:'application/json',
    dataType:'json',
    success: function(d) {
      var buildings = d.buildings;
      buildings.sort();
      
      for (var i = 0; i < buildings.length; i++) {
        var newOption = document.createElement("option");
        newOption.innerHTML = buildings[i];
        newOption.value = buildings[i];
        $("#building_filter_box").append(newOption);
      }
    }
  });
  
  // Clone timeslot selection options
  var days = ["monday", "tuesday", "wednesday", "thursday", "friday"];
  var hours = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"];
  var minutes = ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"];
  var types = ["start", "end"];
  
  for (var i = 0; i < days.length; i++) {
    for (var j = 0; j < types.length; j++) {
      var select_name = "#" + days[i] + "_" + types[j] + "_hour_select";
      for (var h = 0; h < hours.length; h++) {
        var newOption = document.createElement("option");
        newOption.value = hours[h];
        newOption.text = hours[h];
        $(select_name).append(newOption);
      }
      
      select_name = "#" + days[i] + "_" + types[j] + "_minute_select";
      for (var m = 0; m < minutes.length; m++) {
        var newOption = document.createElement("option");
        newOption.value = minutes[m];
        newOption.text = minutes[m];
        $(select_name).append(newOption);
      }
      
      select_name = "#" + days[i] + "_" + types[j] + "_am_pm_select";
      var newOption = document.createElement("option");
      newOption.value = "AM";
      newOption.text = "AM";
      $(select_name).append(newOption);
      
      newOption = document.createElement("option");
      newOption.value = "PM";
      newOption.text = "PM";
      $(select_name).append(newOption);
      
    }
  }
  
});


// When a name in the course section list is clicked, run a function
// that displays its info in the right-hand input pane
$(document).on('click', '.section_list_entry', function(e) {
  showSectionInfo(e.target);
});

// When a section name in the "Scheduling and Editing" panel is clicked, display
// its assigned timeslot and room
$(document).on('click', '.scheduled_list_entry', function(e) {
  showScheduledSectionInfo(e.target);
});

// When a course name in the "Create Course" panel is clicked, show its information
$(document).on('click', '.course_list_entry', function(e) {
  showCourseInfo(e.target);
});


// Trigger a change of the available room list when building filter box
// changes its value
$("#building_filter_box").change(function(e) {
  fillAvailableRoomList();
});


// Run the scheduler when the user loads the "Scheduling and Editing" pane
$(document).on('click', '#scheduling_tab_link', function(e) {
 $.ajax({
    url: '/schedule_with_one_pass',
    type: 'GET',
    contentType:'application/json',
    dataType:'json',
    success: function() {
      
      // Update the view of the active element in the editing pane, if any, to
      // incorporate any changes caused by running the scheduler
      var active = document.getElementsByClassName('scheduled_list_entry active');
      if (active.length > 0) {
        showScheduledSectionInfo(active[0]);
      }
    }
 });
});



// Trigger a change of the available timeslot list when timeslot filter box
// changes its value
$("#timeslot_filter_box").change(function(e) {
  fillAvailableTimeslotList();
});

$("#prefix_filter_box").change(function(e){
  getSectionsByPrefix(($("#prefix_filter_box").val()), "#list_of_created_sections");
});

$("#scheduling_prefix_filter_box").change(function(e){
  getSectionsByPrefix(($("#scheduling_prefix_filter_box").val()), "#list_of_scheduled_sections");
});

$("#course_filter_box").change(function(e){
  getCoursesByPrefix();
});


// Change the active element in a list-group on a click
$(document).on('click', ".available_room_item", function(e) {
  makeActive(e.target, '.available_room_item');
});

$(document).on('click', ".acceptable_room_item", function(e) {
  makeActive(e.target, '.acceptable_room_item');
});

$(document).on('click', ".available_timeslot_item", function(e) {
  makeActive(e.target, '.available_timeslot_item');
});

$(document).on('click', ".acceptable_timeslot_item", function(e) {
  makeActive(e.target, '.acceptable_timeslot_item');
});

$(document).on('click', ".conflict_list_entry", function(e) {
  makeActive(e.target, '.conflict_list_entry');
});

$(document).on('click', ".conflicting_list_entry", function(e) {
  makeActive(e.target, '.conflicting_list_entry');
});

$(document).on('click', ".modal_available_rooms_list_item", function(e) {
  makeActive(e.target, '.modal_available_rooms_list_item');
});





// When the "Add Selected Room" button is clicked, move the selection to
// the "Acceptable Rooms" column
$("#add_selected_room_button").click(function(e) {
  
  $(".available_room_item").each(function() {
    if ($(this).hasClass("active")) {      
      $(this).removeClass("active");
      $(this).removeClass("available_room_item");
      $(this).addClass("acceptable_room_item");
      $(this).appendTo("#acceptable_rooms_list");
    }
  });
  
  updateSectionInformation();
});


// When the "Remove Selected Room" button is clicked, move the selection to
// the "Available Rooms" column
$("#remove_selected_room_button").click(function(e) {
  
  $(".acceptable_room_item").each(function() {
    if ($(this).hasClass("active")) {      
      $(this).removeClass("active");
      $(this).removeClass("acceptable_room_item");
      $(this).addClass("available_room_item");
      
      // Append to the list of available rooms, if the current building
      // selection is the same as the room being removed
      var roomName = $(this).text();
      var fields = roomName.split(' ');
      var building = fields[0];
      if (building == $("#building_filter_box").val()) {
        $(this).appendTo("#available_rooms_list");
      } else {
        $(this).remove();
      }
    }
  });
  
  updateSectionInformation();
});


// When the "Add Selected Timeslot" button is clicked, move the selection to
// the "Acceptable Timeslots" column
$("#add_selected_timeslot_button").click(function(e) {
  
  $(".available_timeslot_item").each(function() {
    if ($(this).hasClass("active")) {      
      $(this).removeClass("active");
      $(this).removeClass("available_timeslot_item");
      $(this).addClass("acceptable_timeslot_item");
      $(this).appendTo("#acceptable_timeslots_list");
    }
  });
  
  updateSectionInformation();
});


// When the "Remove Selected Timeslot" button is clicked, move the selection to
// the "Available Timeslots" column
$("#remove_selected_timeslot_button").click(function(e) {
  
  $(".acceptable_timeslot_item").each(function() {
    if ($(this).hasClass("active")) {      
      $(this).removeClass("active");
      $(this).removeClass("acceptable_timeslot_item");
      $(this).addClass("available_timeslot_item");
      
      // Append to the list of available timeslots if the current category
      // selection is the same as the timeslot being removed
      var timeslotString = $(this).text();
      var fields = timeslotString.split(' ');
      var days = fields[0];
      
      var currentFilter = $("#timeslot_filter_box").val();
      var filterFields = currentFilter.split(' ');
      var filterDays = filterFields[0];
      
      if (days == filterDays) {
        $(this).appendTo("#available_timeslots_list");
      } else {
        $(this).remove();
      }
    }
  });
  
  updateSectionInformation();
});


$("#add_selected_course_button").click(function(e) {
                        
  $(".conflict_list_entry").each(function() {
    if ($(this).hasClass("active")) {
      
      $(this).removeClass("active");
      $(this).removeClass("conflict_list_entry");
      $(this).addClass("conflicting_list_entry");
      $(this).addClass("btn-default");

      var btnGroupDiv = document.createElement('div');
      $(btnGroupDiv).addClass("btn-group");
      $(btnGroupDiv).addClass("btn-group-justified");
      
      var dropdown = document.createElement("div");
      $(dropdown).addClass("btn-group");
      dropdown.innerHTML = '<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">Heavy<span class="caret"></span></button>';
      dropdown.innerHTML += '<ul class="dropdown-menu">'
                            + '<li><a class="severity_menu_item">Heavy</a></li>'
                            + '<li><a class = "severity_menu_item">Medium</a></li>'
                            + '<li><a class = "severity_menu_item">Light</a></li></ul>';
      
      var btnGroupForButton = document.createElement("div");
      $(btnGroupForButton).addClass("btn-group");

      $(dropdown).appendTo(btnGroupDiv);
      $(this).appendTo(btnGroupForButton);
      $(btnGroupForButton).appendTo(btnGroupDiv);
      $(btnGroupDiv).appendTo("#conflicting_courses_list");
    }
  });
  
  updateSectionInformation();
});


// When the "Remove Selected Course" button is clicked, move the selection to
// the "Courses" column
$("#remove_selected_course_button").click(function(e) {
  
  $(".conflicting_list_entry").each(function() {
    if ($(this).hasClass("active")) {      
      $(this).removeClass("active");
      $(this).removeClass("conflicting_list_entry");
      $(this).removeClass("btn-default");
      $(this).addClass("conflict_list_entry");
      
      // Remove the dropdown next to the button
      var dropdown = $(this).parent().siblings();
      $(dropdown).remove();
      
      // Append to the list of available rooms, if the current prefix
      // selection is the same as the room being removed
      var courseName = $(this).text();
      var fields = courseName.split(' ');
      var prefix = fields[0];
      if (prefix == $("#course_filter_box").val()) {
        $(this).appendTo("#conflict_courses_list");
      } else {
        $(this).remove();
      }
    }
  });
  
  updateSectionInformation();
});


// Updates the severity of a conflict when the dropdown menu changes
$(document).on('click', ".severity_menu_item", function(e) {
  var severity_list = $(this).parent().parent();
  var severity_button = $(severity_list).siblings();
  if ($(this).text() != $(severity_button).text()) {
    $(severity_button).html($(this).text() + '<span class="caret"></span>');
    updateSectionInformation();
  }
  
});


// Populate the alternate timeslot selection modal
$(document).on('click', "#alternate_timeslot_button", function(e) {
  var sectionName = $("#section_name_in_schedule_panel").text();
  $("#modal_section_name_span").text(sectionName);
  
  $("#modal_assigned_timeslot_span").text($("#assigned_timeslot_span").text());
  $("#modal_assigned_room_span").text($("#assigned_room_span").text());
  
  // Set the list of acceptable timeslots
  request = {'name' : sectionName};
  
  $.ajax({
    url: '/get_section_information',
    type: 'POST',
    contentType:'application/json',
    data: JSON.stringify(request),
    dataType:'json',
    success: function(d) {
      timeslots = d.acceptable_timeslots;
      var timeslotList = $("#modal_acceptable_timeslots_list");
      timeslotList.empty();
      
      for (var i = 0; i < timeslots.length; i++){
        var newListNode = document.createElement("button");
        newListNode.type = "button";
        newListNode.classList.add("list-group-item");
        newListNode.classList.add("modal_timeslot_item");

        var newTextNode = document.createTextNode(timeslots[i]);
        
        // Make the current timeslot active
        if (timeslots[i] == $("#modal_assigned_timeslot_span").text()) {
          $(newListNode).addClass("active");
          loadTimeslotRoomsAndConflicts(newListNode)
        }
    
        newListNode.appendChild(newTextNode);
        timeslotList.append(newListNode);
      }
    }
  });
  
  // Copy the conflicts at the current assigned timeslot
  $("#modal_current_heavy_conflicts").empty();
  $("#modal_current_medium_conflicts").empty();
  $("#modal_current_light_conflicts").empty();
  
  $("#heavy_conflicts_list > button").clone().appendTo("#modal_current_heavy_conflicts");
  $("#medium_conflicts_list > button").clone().appendTo("#modal_current_medium_conflicts");
  $("#light_conflicts_list > button").clone().appendTo("#modal_current_light_conflicts");

  // Get the list of rooms and conflicts for the current active timeslot
});


// Load the available rooms and conflicts that exist at a selected alternate timeslot
$(document).on('click', '.modal_timeslot_item', function(e) {
  loadTimeslotRoomsAndConflicts(e.target);
});


// Load the available rooms and conflicts that exist at a selected alternate timeslot
$(document).on('click', '#switch_timeslot_button', function(e) {
  var sectionName = $("#modal_section_name_span").text();
  
  var new_timeslot = 'None';
  $('.modal_timeslot_item').each(function() {
    if ($(this).hasClass("active")) {
      new_timeslot = $(this).text();
    }
  });
  
  var new_room = 'None';
  $('.modal_available_rooms_list_item').each(function() {
    if ($(this).hasClass("active")) {
      new_room = $(this).text();
    }
  });
  
  request = {'name' : sectionName, 'room': new_room, 'timeslot' : new_timeslot};
  
  $.ajax({
    url: '/set_assigned_timeslot_and_room',
    type: 'POST',
    contentType:'application/json',
    data: JSON.stringify(request),
    dataType:'json',
    success: function() {
      var visible = document.getElementsByClassName('scheduled_list_entry active');
      showScheduledSectionInfo(visible[0]);
    }
  });
});

// Trigger a save of all section information when any element of the 
// input pane changes
$("#section_info_input_column").change(function(e) {
  updateSectionInformation();
});

$("#save_section_button").click(function(e) {
  updateSectionInformation();
});

// Toggle visiblity of input elements in the custom timeslot creation box
$("#monday_time_checkbox").change(function() {
  $("#monday_start_time_form").toggleClass("hidden");
  $("#monday_end_time_form").toggleClass("hidden");
});

$("#tuesday_time_checkbox").change(function() {
  $("#tuesday_start_time_form").toggleClass("hidden");
  $("#tuesday_end_time_form").toggleClass("hidden");
});

$("#wednesday_time_checkbox").change(function() {
  $("#wednesday_start_time_form").toggleClass("hidden");
  $("#wednesday_end_time_form").toggleClass("hidden");
});

$("#thursday_time_checkbox").change(function() {
  $("#thursday_start_time_form").toggleClass("hidden");
  $("#thursday_end_time_form").toggleClass("hidden");
});

$("#friday_time_checkbox").change(function() {
  $("#friday_start_time_form").toggleClass("hidden");
  $("#friday_end_time_form").toggleClass("hidden");
});


// Create a customized timeslot
$("#create_custom_timeslot_button").click(function() {
  var timeslotString = "";
  
  $(".custom_timeslot_day input").each(function() {
    if ($(this).is(':checked')) {
      
      // Get the text of the label surrounding the checkbox
      var day = $(this).parent().text();
      
      // Abbreviation
      var dayAbbrev;
      if (day != 'Thursday') {
        dayAbbrev = day[0];
      } else {
        dayAbbrev = "R";
      }
      
      // Start times that append to startTime string
      day = day.toLowerCase();
      var queryString = "#" + day + "_start_hour_select";
      var startHour = $(queryString).val();
      
      queryString = "#" + day + "_start_minute_select";
      var startMinute = $(queryString).val();
      
      queryString = "#" + day + "_start_am_pm_select";
      var amOrPm = $(queryString).val();
      
      if (amOrPm == "PM" && parseInt(startHour) < 12) {
        startHour = '' + (parseInt(startHour) + 12);
      }
      
      if (amOrPm == "AM" && parseInt(startHour) == 12) {
        startHour = "0";
      }
      
      startTime = startHour + ":" + startMinute;
      
      // End times that append to endTime string
      var queryString = "#" + day + "_end_hour_select";
      var endHour = $(queryString).val();
      
      queryString = "#" + day + "_end_minute_select";
      var endMinute = $(queryString).val();
      
      queryString = "#" + day + "_end_am_pm_select";
      var amOrPm = $(queryString).val();
      
      if (amOrPm == "PM" && parseInt(endHour) < 12) {
        endHour = '' + (parseInt(endHour) + 12);
      }
      
      if (amOrPm == "AM" && parseInt(endHour) == 12) {
        endHour = "00";
      }
      
      endTime = endHour + ":" + endMinute;
      
      timeslotString += dayAbbrev + " " + startTime + " - " + endTime + " ; ";
    }
  });
  
  // Strip the last " ; " from the timeslot string
  timeslotString = timeslotString.slice(0, timeslotString.length - 3);
  
  // Enter into acceptable timeslots list
  var timeslotList = $("#acceptable_timeslots_list");
  var newListNode = document.createElement("button");
  newListNode.type = "button";
  newListNode.classList.add("list-group-item");
  newListNode.classList.add("acceptable_timeslot_item");
  var newTextNode = document.createTextNode(timeslotString);
  newListNode.appendChild(newTextNode);
  timeslotList.append(newListNode);

  // Save updated list -- this pushes the new timeslot into the list of 
  // acceptable timeslots
  updateSectionInformation();
  
});


// Delete the active section
$("#confirm_delete_button").click(function(e) {
  
  var sectionName = $("#section_name_in_input_panel").text();
  var requestObject = {'name' : sectionName};

  $.ajax({
    url: '/delete_section',
    type: 'POST',
    contentType:'application/json',
    data: JSON.stringify(requestObject),
    dataType:'json',
    success: function() {
      
      // Remove from the left-hand section list
      $('.section_list_entry').each(function() {
        if ($(this).text() == sectionName) {
          $(this).remove();
        }
      });
      
      // Hide the right-hand pane
      $("#section_info_input_column").addClass("hidden");
      fillListofSections();
    }
  });
});
