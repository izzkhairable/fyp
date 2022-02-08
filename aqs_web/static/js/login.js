function login(){

    var email = document.getElementById("email").value;
    var password = document.getElementById("password").value;

    
    $(async () => {
    // Change serviceURL to your own
        var serviceURL = "http://localhost:5000/login?email=" + email + "&password=" + password;
        try {
        const response =
            await fetch(
                serviceURL, {
                  method: 'GET'
              }
          );
        const result = await response.json();
        if (response.status === 200) {
            // success case
            console.log(result)
            console.log('There is success here')
        }
        else if (response.status == 404) {
        // No Rows
            console.log(result.message);
        } else {
        // unexpected outcome, throw the error
            throw response.status;
        }
        } catch (error) {
        // Errors when calling the service; such as network error, 
        // service offline, etc
        console.log('There is a problem retrieving the data, please try again later.<br />' + error);
        } // error
    });
}