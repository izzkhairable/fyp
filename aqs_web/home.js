function test() {
  $(async() => {           
  // Change serviceURL to your own
  var serviceURL = "http://localhost:5000/test";

  try {
      const response =
      await fetch(
      serviceURL, { method: 'GET' }
      );
      const result = await response.json();
      if (response.status === 200) {
          // success case
          console.log(result);
          console.log(result[0]["status"])
          
          } else if (response.status == 404) {
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

function insert(){
    $(async() => {           
    // Change serviceURL to your own
    var account_id = localStorage.getItem("account_id");

    var serviceURL = "http://localhost:5000/insert";
    var today = new Date();
    const data = {
        //key(database):
        quotation_id: "69",
        customer_email: "darkdrium_1994@hotmail.com",
        assigned_staff_email: "darrenho.2019@scis.smu.edu.sg",
        rfq_date: today,
        status: "pending"
    };

    try {
        const response =
        await fetch(
        serviceURL, { method: 'POST', body: JSON.stringify(data), headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            }}
        );
        const result = await response.json();
        if (response.status === 500) {
            alert("An enrollment request under this course has already been created.")
            }
            else {
                alert("An enrollment request for this class has been successfully created!")
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
                } // error
    });
}