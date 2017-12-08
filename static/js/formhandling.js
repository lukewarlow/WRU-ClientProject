function verifyForm()
{
  if (validatePassword("verify", "newpassword"))
  {
    var username = document.forms["verify"]["username"].value;
    var password = document.forms["verify"]["password"].value;
    var newpassword = document.forms["verify"]["newpassword"].value;
    var payload = document.getElementById("txt").innerHTML;
    params = 'username='+username+'&password='+password+'&newpassword='+newpassword+'&payload='+payload;
    document.getElementById("msg").innerHTML = "Verifying";
    ajaxData("POST", "/Staff/Verify", params);
    setTimeout(5000);
    msg = document.getElementById("msg").innerHTML.split("<br>")[0];
    if (!msg.includes("Error")) setTimeout(redirect, 700, "/Home");
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

function validateAccountChanges()
{
  var password = document.forms["accountChange"]["password"].value;
  params = "";
  try
  {
    var newpassword = document.forms["accountChange"]["newpassword"].value;
    params = "password="+password+"&newpassword="+newpassword;
  }
  catch (TypeError)
  {
    try
    {
      var newemail = document.forms["accountChange"]["newemail"].value;
      params = "password="+password+"&newemail="+newemail;
    }
    catch (TypeError)
    {
      document.getElementById("msg").innerHTML = "Error";
      return false;
    }
  }
  ajaxData("POST", "/Staff/Account", params);
  setTimeout(5000);
  msg = document.getElementById("msg").innerHTML.split("<br>")[0];
  if (!msg.includes("Error")) setTimeout(redirect, 700, "/Home");
  return false;
}

function validateLoginIssues()
{
  params = "";
  try
  {
    var username = document.forms["loginIssue"]["username"].value;
    var email = document.forms["loginIssue"]["email"].value;
    params = "username="+username+"&email="+email;
  }
  catch (TypeError)
  {
    try
    {
      var email = document.forms["loginIssue"]["email"].value;
      params = "email="+email;
    }
    catch (TypeError)
    {
      document.getElementById("msg").innerHTML = "Error";
      return false;
    }
  }
  ajaxData("POST", "/Staff/LoginIssues", params);
  setTimeout(5000);
  msg = document.getElementById("msg").innerHTML.split("<br>")[0];
  if (!msg.includes("Error")) setTimeout(redirect, 700, "/Home");
  return false;
}

function deleteStaff()
{
  var username = document.forms["deletestaff"]["username"].value;
  var password = document.forms["deletestaff"]["password"].value;
  params = 'username='+username+'&password='+password;
  ajaxData("POST", "/Admin/DeleteStaff", params);
  setTimeout(5000);
  msg = document.getElementById("msg").innerHTML.split("<br>")[0];
  if (!msg.includes("Error")) document.forms["deletestaff"].reset();
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
  params = 'firstName='+firstName+'&surname='+surname+'&password='+password+'&email='+email+'&usertype='+usertype+'&organisation='+organisation;
  ajaxData("POST", "/Admin/AddStaff", params);
  setTimeout(5000);
  msg = document.getElementById("msg").innerHTML.split("<br>")[0];
  if (!msg.includes("Error")) document.forms["addstaff"].reset();
  return false;
}

function login()
{
  var username = document.forms["login"]["username"].value;
  var password = document.forms["login"]["password"].value;
  params = 'username='+username+'&password='+password;
  ajaxData("POST", "/Staff/Login", params);
  setTimeout(5000);
  msg = document.getElementById("msg").innerHTML.split("<br>")[0];
  if (!msg.includes("Error")) setTimeout(redirect, 700, "/Home");
  return false;
}

function redirect(location)
{
  window.location.href = location;
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
  try
  {
    var eventName = document.forms["eventForm"]["eventName"].values;
  }
  catch (TypeError)
  {
    var eventName = "";
  }

  var eventStartDate = document.forms["eventForm"]["eventStartDate"].value;

  try
  {
    var eventEndDate = document.forms["eventForm"]["eventEndDate"].value;
  }
  catch (TypeError)
  {
    var eventEndDate = "";
  }

  var postcode = document.forms["eventForm"]["postcode"].value;
  var eventRegion = document.forms["eventForm"]["eventRegion"].value;
  if (eventRegion == "Other") eventRegion = document.forms["eventForm"]["otherbox3"].value;

  var inclusivity = document.forms["eventForm"]["inclusivity"].value;
  if (inclusivity == "Other") inclusivity = document.getElementById("otherbox2").value;
  var comments = document.forms["eventForm"]["comments"].value;

  var activityTypes = [];
  var checkboxes = document.querySelectorAll('input[type=checkbox]:checked');

  for (var i = 0; i < checkboxes.length; i++)
  {
    if (checkboxes[i].value == "Other") activityTypes.push(document.getElementById("otherbox").value);
    else if (checkboxes[i].value == "hubActivity")
    {
      if (document.getElementById("hubSelect").value == "other") activityTypes.push(document.getElementById("hubBox").value);
      else activityTypes.push(document.getElementById("hubSelect").value);
    }
    else if (checkboxes[i].value == "collaborativeDelivery") activityTypes.push(document.getElementById("collabBox").value);
    else activityTypes.push(checkboxes[i].value);
  }
  params = 'eventName='+eventName+'&eventStartDate='+eventStartDate+'&eventEndDate='+eventEndDate+'&postcode='+postcode+'&eventRegion='+eventRegion+'&inclusivity='+inclusivity+'&activityTypes='+activityTypes+'&comments='+comments;
  ajaxData("POST", "/Staff/EventForm", params);
  setTimeout(5000);
  msg = document.getElementById("msg").innerHTML.split("<br>")[0];
  if (!msg.includes("Error")) document.forms["eventForm"].reset();
  return false;
}

function logout()
{
  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", '/Logout', true); // true is asynchronous
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.onload = function()
  {
    if (xhttp.readyState === 4 && xhttp.status === 200)
    {
      console.log("Log out " + xhttp.responseText);
      if (xhttp.responseText == "successful") setTimeout(redirect, 300, "/Home")
    }
    else console.error(xhttp.statusText);
  };
  xhttp.send();
  return false;
}

function otherSelected(selectbox, idOfTextBox)
{
    if (selectbox.value == "other") document.getElementById(idOfTextBox).style.display = "block";
    else document.getElementById(idOfTextBox).style.display = "none";
}

function actionSelected(selectbox)
{
    if (selectbox.value == "changePassword")
    {
      document.getElementById("accountChangeForm").innerHTML = `
      <b>New password</b>
      <input type='password' id="newpassword" placeholder='Enter your new password here' name='newpassword' onkeyup="checkBoxesMatch('newpassword', 'submitAccountChanges')" required>
      <b>Confirm new password:</b>
      <input type='password' id="checknewpassword" placeholder='Re-Enter your new password here' name='checknewpassword' onkeyup="checkBoxesMatch('newpassword', 'submitAccountChanges')" required>`;
    }
    else if (selectbox.value == "changeEmail")
    {
      document.getElementById("accountChangeForm").innerHTML = `
      <b>New email</b>
      <input type='email' id="newemail" placeholder='Enter your new email here' name='newemail' onkeyup="checkBoxesMatch('newemail', 'submitAccountChanges')" required>
      <b>Confirm New email:</b>
      <input type='email' id="checknewemail" placeholder='Re-Enter your new email here' name='checknewemail' onkeyup="checkBoxesMatch('newemail', 'submitAccountChanges')" required>`;
    }
}

function issueSelected(selectbox)
{
    if (selectbox.value == "forgotUsername")
    {
      document.getElementById("infoRecovery").innerHTML = `
      <b>Enter email address for a username reminder</b>
      <input type='email' placeholder='Enter your email address here' name='email' required>`;
    }
    else if (selectbox.value == "forgotPassword")
    {
      document.getElementById("infoRecovery").innerHTML = `
      <b>Enter username</b>
      <input type='text' placeholder='Enter your username here' name='username' required>
      <b>Enter registered email address</b>
      <input type='email' placeholder='Enter your email address here' name='email' required>`;
    }
}

function checkboxChecked(checkbox, id)
{
  if(checkbox.checked) document.getElementById(id).style.display = "block";
  else document.getElementById(id).style.display = "none";
  if(checkbox.value=="multiDay" && checkbox.checked) document.getElementById("eventTxt").innerHTML = "Event start date";
  else if(checkbox.value=="multiDay" && !checkbox.checked) document.getElementById("eventTxt").innerHTML = "Event date";
}

function radioChecked(selector, id)
{
  if (selector.value == "other")
  {
    document.getElementById(id).style.display = "block";
  }
  else
  {
    document.getElementById(id).style.display = "none";
  }
}

function validateTournamentForm()
{
  return addTournament();
}

//https://developer.mozilla.org/en-US/docs/Web/API/FormData/Using_FormData_Objects Accessed: 08/12/2017
function addTournament()
{
  var form = document.forms.namedItem("tournamentForm");
  formData = new FormData(form);
  try
  {
    var eventName = formData.get("eventName");
  }
  catch (TypeError)
  {
    formData.delete("eventName");
  }

  try
  {
    var eventDate = formData.get("eventDate");
  }
  catch (TypeError)
  {
    formDate.delete("eventDate");
  }

  try
  {
    var postcode = formData.get("postcode");
    //http://html5pattern.com/Postal_Codes (Retrieved 17/11/17)
    if (!postcode.match("^[A-Za-z]{1,2}[0-9Rr][0-9A-Za-z]? [0-9][ABD-HJLNP-UW-Zabd-hjlnp-uw-z]{2}$"))
    {
      document.getElementById("msg").innerHTML = "Must enter valid postcode.";
      return false;
    }
  }
  catch (TypeError)
  {
    formData.delete("postcode");
  }

  if (!((formData.has("eventName") && formData.has("eventDate")) || (formData.has("eventName") && formData.has("postcode")) || (formData.has("eventDate") && formData.has("postcode"))))
  {
    document.getElementById("msg").innerHTML = "At least 2 out 3 bits of event information must be provided!";
    return false;
  }

  if (document.getElementById("otherRadio").checked) formData.set("rugbyOffer", document.getElementById("otherbox").value);
  else formData.set("rugbyOffer", document.querySelector('input[type=radio]:checked').value);
  ajaxData("POST", "/Staff/TournamentForm", formData, true);
  setTimeout(5000);
  msg = document.getElementById("msg").innerHTML.split("<br>")[0];
  if (!msg.includes("Error")) document.forms["tournamentForm"].reset();
  return false;
}

var checkBoxesMatch = function(boxID, buttonID)
{
  var matching = false;

  if (document.getElementById(boxID).value == document.getElementById('check' + boxID).value &&
      document.getElementById(boxID).value != "")
  {
    document.getElementById('check' + boxID).style.border = "4px solid green";
    document.getElementById(buttonID).disabled = false;
  }
  else
  {
    document.getElementById('check' + boxID).style.border = "4px solid red";
    document.getElementById(buttonID).disabled = true;
  }
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
  if (messages.length > 0) console.log(messages);
  for (i=0; i < messages.length;i++)
  {
    if (messages[i] != null)
    {
      console.log(messages[i]);
      ajaxData(messages[i]["method"], messages[i]["action"], messages[i]["params"], messages[i]["storeOffline"]);
    }
  }
}

function ajaxData(method, action, params, handleFileData=false)
{
  var xhttp = new XMLHttpRequest();
  var msg = "";
  xhttp.open(method, action, true); // true is asynchronous
  if (!handleFileData) xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.onload = function()
  {
    if (xhttp.readyState === 4)
    {
      if (xhttp.status === 200)
      {
        msg = xhttp.responseText;
      }
      else if (xhttp.status === 503 || xhttp.status === 0)
      {
        storeOffline(method, action, params, handleFileData);
        msg = "Browser offline data stored for submission when online";
      }
      else
      {
        console.error(xhttp.statusText);
        msg = "Error: other wierd response " + xhttp.status;
      }
      try
      {
        document.getElementById("msg").innerHTML = msg + "<br>"+document.getElementById("msg").innerHTML;
      } catch (e) { }
      console.log(msg);
    }
  };
  xhttp.send(params);
}

function storeOffline(method, action, params, handleFileData)
{
  myStorage = window.localStorage;
  storageItem = JSON.stringify({"action":action, "method":method, "params":params, "handleFileData":handleFileData});
  myStorage.setItem('dataStorage', storageItem);
}

//Adapted from https://ponyfoo.com/articles/backgroundsync Accessed: 1/12/2017
function isOnline ()
{
  var connectionStatus = document.getElementById('connectionStatus');
  if (navigator.onLine)
  {
    resendStoredData();
    connectionStatus.className = "greencircle";
    toggleOnlineOnlyStuff(true);
    console.log("Online");
  }
  else
  {
    connectionStatus.className = "redcircle";
    toggleOnlineOnlyStuff(false);
    console.log("Offline");
  }
}

window.addEventListener('online', isOnline);
window.addEventListener('offline', isOnline);

function toggleOnlineOnlyStuff(status)
{
  if (status) display = "block";
  else display = "none";
  var loginbutton = document.getElementById("login");
  if (loginbutton != null)
  {
    loginbutton.style.display = display;
    var homepagemessage = document.getElementById("homepagemessage");
    if (homepagemessage != null && !status)
    {
      homepagemessage.innerHTML = "Welcome to the Welsh Rugby Union's data collection tool. <br>Unfortunately you only have offline access to this site when logged in.";
    }
    else if (homepagemessage != null && status)
    {
      homepagemessage.innerHTML = "Welcome to the Welsh Rugby Union's data collection tool.";
    }
  }
  var logoutbutton = document.getElementById("logout");
  if (logoutbutton != null) logoutbutton.style.display = display;
  var admindropdown = document.getElementById("adminsection");
  if (admindropdown != null) admindropdown.style.display = display;
  var accountChange = document.getElementById("accountChanges");
  if (accountChange != null) accountChange.style.display = display;
  var submit = document.getElementById("submit");
  if (status && submit != null) submit.textContent = "Submit";
  else if (submit != null) submit.textContent = "Submit when online";
}

//Slider work in progress
function outputUpdate(ratio)
{
  document.getElementById("maleRatio").innerHTML = "Male: " + ratio + "%"
  document.getElementById("femaleRatio").innerHTML = "Female: " + (100 - ratio) + "%"
}
