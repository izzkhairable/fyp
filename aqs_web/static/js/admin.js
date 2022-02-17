function allReasons(){
    $(async () => {
        // Change serviceURL to your own
        var serviceURL = "http://localhost:5000/rejectionReasons/";
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

            } else if (response.status == 404) {
                // No Rows
                console.log(result.message);
                alert("No such quotation exist.")
                location.href = "supervisor_home";
            } else {
                // unexpected outcome, throw the error
                throw response.status;
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
            alert("The server is current down, please try again later.")
            location.href = "supervisor_home";
        } // error
    });
}


function addReasons()


function delReasons()