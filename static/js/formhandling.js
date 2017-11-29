function validatePassword(form)
{
  var password = document.forms[form]["password"].value;

  if(password.length > 8)
  {
    //https://gist.github.com/Michael-Brooks/fbbba105cd816ef5c016 Accessed 21/11/2017
    if(password.match(/^(?=.*[a-z|A-Z])(?=.*[A-Z])(?=.*\d).+$/) != null)
    {
      if (form == "login") login();
      else if (form == "addstaff") addStaff();
    }
    else alert("Passwords contain at least 1 lower and upper case letter. And 1 number.");
  }
  else alert("Passwords are at least 9 Characters long.");
  return false;
}

function deleteStaff()
{
  var username = document.forms["deletestaff"]["username"].value;
  document.forms["deletestaff"].reset();
  params = 'username='+username;
  var xhttp = new XMLHttpRequest();
  xhttp.open("POST", '/Admin/DeleteStaff', true); // true is asynchronous
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.onload = function()
  {
    if (xhttp.readyState === 4 && xhttp.status === 200)
    {
      console.log(xhttp.responseText);
      document.getElementById("txt").innerHTML = xhttp.responseText;
    }
    else console.error(xhttp.statusText);
  };
  xhttp.send(params);
  return false;
}

function addStaff()
{
  var firstName = document.forms["addstaff"]["firstName"].value;
  var surname = document.forms["addstaff"]["surname"].value;
  var password = document.forms["addstaff"]["password"].value;
  var email = document.forms["addstaff"]["email"].value;
  var usertype = document.forms["addstaff"]["usertype"].value;
  document.forms["addstaff"].reset();
  params = 'firstName='+firstName+'&surname='+surname+'&password='+password+'&email='+email+'&usertype='+usertype;
  var xhttp = new XMLHttpRequest();
  xhttp.open("POST", '/Admin/AddStaff', true); // true is asynchronous
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.onload = function()
  {
    if (xhttp.readyState === 4 && xhttp.status === 200)
    {
      console.log(xhttp.responseText);
      document.getElementById("txt").innerHTML = xhttp.responseText;
    }
    else console.error(xhttp.statusText);
  };
  xhttp.send(params);
  return false;
}

function login()
{
  var username = document.forms["login"]["username"].value;
  var password = document.forms["login"]["password"].value;
  params = 'username='+username+'&password='+password;
  var xhttp = new XMLHttpRequest();
  xhttp.open("POST", '/Staff/Login', true); // true is asynchronous
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.onload = function()
  {
    if (xhttp.readyState === 4 && xhttp.status === 200)
    {
      response = "Log in " + xhttp.responseText;
      console.log(response);
      alert(response);
       //if (xhttp.responseText == "successful") document.forms["login"].reset();
       // if (xhttp.responseText == "unsuccessful") return false; //TO-DO fix
    }
    else console.error(xhttp.statusText);
  };
  xhttp.send(params);
  return false; //TODO fix this
}

function validateEventForm()
{
  //TODO add validation
  return addEvent();
}

function addEvent()
{
  var eventDate = document.forms["eventForm"]["eventDate"].value;
  var postcode = document.forms["eventForm"]["postcode"].value;
  var eventRegion = document.forms["eventForm"]["eventRegion"].value;
  if (eventRegion == "Other") eventRegion = document.forms["eventForm"]["otherbox3"].value;
  try
  {
    var eventName = document.forms["eventForm"]["eventname"].values;
  }
  catch (TypeError)
  {
    var eventName = "";
  }
  var inclusivity = document.forms["eventForm"]["inclusivity"].value;
  if (inclusivity == "Other") inclusivity = document.getElementById("otherbox2").value;
  var comments = document.forms["eventForm"]["comments"].value;

  var activityTypes = []
  var checkboxes = document.querySelectorAll('input[type=checkbox]:checked')

  for (var i = 0; i < checkboxes.length; i++)
  {
    if (checkboxes[i].value == "Other") activityTypes.push(document.getElementById("otherbox").value)
    else activityTypes.push(checkboxes[i].value)
  }

  params = 'eventName='+eventName+'&eventDate='+eventDate+'&postcode='+postcode+'&eventRegion='+eventRegion+'&eventName='+eventName+'&inclusivity='+inclusivity+'&activityTypes='+activityTypes+'&comments='+comments;
  var xhttp = new XMLHttpRequest();
  xhttp.open("POST", '/Staff/EventForm', true); // true is asynchronous
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.onload = function()
  {
    if (xhttp.readyState === 4 && xhttp.status === 200)
    {
      console.log(xhttp.responseText);
      document.getElementById("txt").innerHTML = xhttp.responseText;
      if (xhttp.responseText.includes("successful"))
      {
        document.forms["eventForm"].reset();
      }
    }
    else console.error(xhttp.statusText);
  };
  xhttp.send(params);
  return false;
}

function otherSelected(selectbox, idOfTextBox)
{
    if (selectbox.value == "Other") document.getElementById(idOfTextBox).style.display = "block";
    else document.getElementById(idOfTextBox).style.display = "none";
}

function otherChecked(checkbox)
{
  if(checkbox.checked) document.getElementById("otherbox").style.display = "block";
  else document.getElementById("otherbox").style.display = "none";
}

function validateTournamentForm()
{
  //TODO add validation
  return addTournament();
}

function addTournament()
{
  var eventDate = document.forms["tournamentForm"]["eventDate"].value;
  var postcode = document.forms["tournamentForm"]["postcode"].value;
  var eventName = document.forms["tournamentForm"]["eventName"].value;
  var peopleNum = document.forms["tournamentForm"]["peopleNum"].value;
  var ageRange = document.forms["tournamentForm"]["ageRange"].value;
  var genderRatio = document.forms["tournamentForm"]["genderRatio"].value;

  var rugbyOffers = []
  var checkboxes = document.querySelectorAll('input[type=checkbox]:checked')

  for (var i = 0; i < checkboxes.length; i++)
  {
    if (checkboxes[i].value == "Other") rugbyOffers.push(document.getElementById("otherbox").value)
    else rugbyOffers.push(checkboxes[i].value)
  }

  try
  {
    var eventName = document.forms["eventForm"]["eventname"].values;
  }
  catch (TypeError)
  {
    var eventName = "";
  }

  params = 'eventName='+eventName+'&eventDate='+eventDate+'&postcode='+postcode+'&eventName'+eventName+'&peopleNum='+peopleNum+'&ageRange='+ageRange+'&rugbyOffers='+rugbyOffers+'&genderRatio='+genderRatio;
  var xhttp = new XMLHttpRequest();
  xhttp.open("POST", '/Staff/TournamentForm', true); // true is asynchronous
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.onload = function()
  {
    if (xhttp.readyState === 4 && xhttp.status === 200)
    {
      console.log(xhttp.responseText);
      document.getElementById("txt").innerHTML = xhttp.responseText;
      if (xhttp.responseText.includes("successful"))
      {
        document.forms["tournamentForm"].reset();
      }
    }
    else console.error(xhttp.statusText);
  };
  xhttp.send(params);
  return false;
}

//SLider work in progress
function outputUpdate(ratio)
{
  document.getElementById("maleRatio").innerHTML = "Male: " + ratio + "%"
  document.getElementById("femaleRatio").innerHTML = "Female: " + (100 - ratio) + "%"
}
