function start() {
    getSalesperson();
    getSalespersonTotalQuotes();
}

// in progress
function getSalesperson() {
    var supervisor_id = "1";
    $(async () => {
        // Change serviceURL to your own
        var serviceURL = "http://localhost:5000/salesperson/" + supervisor_id;
        document.getElementById("salesperson").innerHTML = "";
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
                for (var salesperson in result) {
                    document.getElementById("salesperson").innerHTML += `<tr>
                  <th scope="row"><img src="https://c.tenor.com/9qZhM0uswAYAAAAd/bully-maguire-dance.gif" width="30"
                    height="30" class="rounded-circle"></th>
                  <td class="fw-bold text-primary"><a href="#"><u>${result[salesperson].first_name} ${result[salesperson].last_name}</u></a></td>
                  <td>${result[salesperson].staff_email}</td>
                  <td class="fw-bold text-danger text-center"><a href="#"><u>${result[salesperson].pending}</u></a></td>
                  <td class="fw-bold text-primary text-center"><a href="#"><u>${result[salesperson].sent}</u></a></td>
                  <td class="fw-bold text-success text-center"><a href="#"><u>${result[salesperson].approved}</u></a></td>
                </tr>`
                }
            } else if (response.status == 404) {
                // No Rows
                document.getElementById("salesperson").innerHTML += `<tr>
                  <th scope="row" class="fw-bold">Nothing to see here...</th>
                </tr>`
                console.log(result.message);
            } else {
                // unexpected outcome, throw the error
                document.getElementById("salesperson").innerHTML += `<tr>
                  <th scope="row" class="fw-bold">Nothing to see here...</th>
                </tr>`
                throw response.status;
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
        } // error
    });
}

function getSalespersonTotalQuotes() {
    var supervisor_id = "1";
    $(async () => {
        // Change serviceURL to your own
        var serviceURL = "http://localhost:5000/supervisor_quotations_numbers/" + supervisor_id;
        document.getElementById("approved").innerHTML = "";
        document.getElementById("pending").innerHTML = "";
        document.getElementById("sent").innerHTML = "";
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
                for (var status in result) {
                    if (result[status].status == 'approved') {
                        document.getElementById("approved").innerHTML = result[status].num;
                    } else if (result[status].status == 'pending') {
                        document.getElementById("pending").innerHTML = result[status].num;
                    } else {
                        document.getElementById("sent").innerHTML = result[status].num;
                    }
                }
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

// TO DOOOO
function getQuotesThatRequireAttention() {
    var supervisor_id = "1";
    $(async () => {
        // Change serviceURL to your own
        var serviceURL = "http://localhost:5000/supervisor_quotations_attention/" + supervisor_id;
        document.getElementById("quotations-for-review").innerHTML = "";
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
                for (var status in result) {
                    // fill up here
                }
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