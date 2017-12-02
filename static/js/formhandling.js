function verifyForm()
{
  if (validatePassword("verify", "password"))
  {
    if (validatePassword("verify", "newpassword"))
    {
      var username = document.forms["verify"]["username"].value;
      var password = document.forms["verify"]["password"].value;
      var newpassword = document.forms["verify"]["newpassword"].value;
      var payload = document.getElementById("txt").innerHTML;
      params = 'username='+username+'&password='+password+'&newpassword='+newpassword+'&payload='+payload;
      document.getElementById("msg").innerHTML = "Verifying";
      var xhttp = new XMLHttpRequest();
      xhttp.open("POST", '/Staff/Verify', true); // true is asynchronous
      xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
      xhttp.onload = function()
      {
        if (xhttp.readyState === 4 && xhttp.status === 200)
        {
          console.log("Verification was: " + xhttp.responseText);
          document.getElementById("msg").innerHTML = "Verification was: " + xhttp.responseText;
          if (xhttp.responseText == "successful") setTimeout(redirect, 700, "/Home")
        }
        else console.error(xhttp.statusText);
      };
      xhttp.send(params);
      return false;
    }
    return false;
  }
  return false;
}

function validatePassword(form, id)
{
  var password = document.forms[form][id].value;

  if(password.length > 8)
  {
    //https://gist.github.com/Michael-Brooks/fbbba105cd816ef5c016 Accessed 21/11/2017
    if(password.match(/^(?=.*[a-z|A-Z])(?=.*[A-Z])(?=.*\d).+$/) != null)
    {
      if (form == "login") login();
      else if (form == "addstaff") addStaff();
      else return true;
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
      document.getElementById("msg").innerHTML = xhttp.responseText;
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
  var organisation = document.forms["addstaff"]["organisation"].value;
  document.forms["addstaff"].reset();
  params = 'firstName='+firstName+'&surname='+surname+'&password='+password+'&email='+email+'&usertype='+usertype+'&organisation='+organisation;
  var xhttp = new XMLHttpRequest();
  xhttp.open("POST", '/Admin/AddStaff', true); // true is asynchronous
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.onload = function()
  {
    if (xhttp.readyState === 4 && xhttp.status === 200)
    {
      console.log(xhttp.responseText);
      document.getElementById("msg").innerHTML = xhttp.responseText;
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
      console.log("Log in " + xhttp.responseText);
      document.getElementById("msg").innerHTML = "Log in " + xhttp.responseText;
      if (xhttp.responseText == "successful") setTimeout(redirect, 700, "/Home")
    }
    else console.error(xhttp.statusText);
  };
  xhttp.send(params);
  return false;
}

function redirect(location)
{
  window.location.href = "/Home";
}

function validateEventForm()
{
  var checkboxes = document.querySelectorAll('input[type=checkbox]:checked')
  if (checkboxes.length == 0)
  {
    alert("You need to select at least one activity type!");
    return false;
  }
  else
  {
    return addEvent();
  }
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
  ajaxData("POST", "/Staff/EventForm", params);
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
  var checkboxes = document.querySelectorAll('input[type=checkbox]:checked')
  if (checkboxes.length == 0)
  {
    alert("You need to select at least one rugby offer!");
    return false;
  }
  else return addTournament();
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
  ajaxData("POST", "/Staff/TournamentForm", params);
  return false;
}

function resendStoredData()
{
  var msg = "null"
  var myStorage = window.localStorage;
  messages = [];
  for (message in myStorage)
  {
    var messageObj = JSON.parse(myStorage.getItem(message));
    messages.push(messageObj);
  }
  myStorage.clear()
  console.log(messages);
  for (i=0;i< messages.length;i++)
  {
    if (messages[i] != null)
    {
      console.log(messages[i]);
      ajaxData(messages[i]["method"], messages[i]["action"], messages[i]["params"]);
    }
  }
}

function ajaxData(method, action, params)
{
  var xhttp = new XMLHttpRequest();
  xhttp.open(method, action, true); // true is asynchronous
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.onreadystatechange = function()
  {
    var msg = null;
    if (xhttp.readyState === 4)
    {
      if (xhttp.status === 200)
      {
        console.log(xhttp.responseText);
        msg = xhttp.responseText;
      }
      else if (xhttp.status === 503 || xhttp.status === 0)
      {
        console.error(xhttp.statusText);
        storeOffline(method, action, params);
        msg = "Browser off line data stored for later use";
      }
      else
      {
        console.error(xhttp.statusText);
        msg = "other wierd error " + xhttp.status;
      }
      document.getElementById("msg").innerHTML = msg + "<br>"+document.getElementById("msg").innerHTML;
    }
  };
  xhttp.send(params);
}

function storeOffline(method, action, params)
{
  myStorage = window.localStorage;
  storageItem = JSON.stringify({"action":action, "method":method, "params":params});
  myStorage.setItem('dataStorage', storageItem);
}

//Adapted from https://ponyfoo.com/articles/backgroundsync Accessed: 1/12/2017
function isOnline ()
{
  if (navigator.onLine) resendStoredData();
}

window.addEventListener('online', isOnline);
isOnline();

//SLider work in progress
function outputUpdate(ratio)
{
  document.getElementById("maleRatio").innerHTML = "Male: " + ratio + "%"
  document.getElementById("femaleRatio").innerHTML = "Female: " + (100 - ratio) + "%"
}
