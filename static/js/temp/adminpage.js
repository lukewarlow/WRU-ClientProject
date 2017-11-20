function loadName() {
  var firstName = document.forms["addstaff"]["firstName"].value;
  var surname = document.forms["addstaff"]["surname"].value;
  var dateofbirth = document.forms["addstaff"]["dateofbirth"].value;
  var homeLocation = document.forms["addstaff"]["homeLocation"].value;
  var username = document.forms["addstaff"]["username"].value;
  var password = document.forms["addstaff"]["password"].value;
  params = 'firstName='+firstName+'&surname='+surname+'&dateofbirth='+dateofbirth+'&homeLocation='+homeLocation+'&username='+username+'&password='+password;
  var xhttp = new XMLHttpRequest();
  xhttp.open("POST", '/admin', true); // true is asynchronous
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.onload = function() {
    if (xhttp.readyState === 4 && xhttp.status === 200) {
      console.log(xhttp.responseText);
      document.getElementById("txt").innerHTML = xhttp.responseText;
    } else {
      console.error(xhttp.statusText);
    }
  };
  xhttp.send(params);
  return false;
}
