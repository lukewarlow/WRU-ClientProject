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
    else
    {
      console.error(xhttp.statusText);
    }
  };
  xhttp.send(params);
  return false;
}

//https://dzone.com/articles/use-regex-test-password Accessed 21/11/2017
function validateAddStaffForm()
{
  var password = document.forms["addstaff"]["password"].value;

  if(password.length > 8)
  {
    if(password.match(/^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])$/) != null)
    {
      addStaff();
    }
    else
    {
      alert("Password needs to contain at least 1 lower and upper case letter. And 1 number.");
    }
  }
  else
  {
    alert("Password needs to be at least 8 Characters long.");
  }
  return false;
}

function validateLoginForm()
{
  var password = document.forms["addstaff"]["password"].value;

  if(password.length > 8)
  {
    if(password.match(/^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])$/) != null)
    {
      loginTest();
    }
    else
    {
      alert("Passwords contain at least 1 lower and upper case letter. And 1 number.");
    }
  }
  else
  {
    alert("Passwords are at least 8 Characters long.");
  }
  return false;
}

function loginTest()
{
  var username = document.forms["login"]["username"].value;
  var password = document.forms["login"]["password"].value;
  document.forms["login"].reset();
  params = 'username='+username+'&password='+password;
  var xhttp = new XMLHttpRequest();
  xhttp.open("POST", '/Login', true); // true is asynchronous
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.onload = function()
  {
    if (xhttp.readyState === 4 && xhttp.status === 200)
    {
      console.log(xhttp.responseText);
      alert(xhttp.responseText);
    }
    else
    {
      console.error(xhttp.statusText);
    }
  };
  xhttp.send(params);
  return false;
}
