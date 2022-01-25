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
                    document.getElementById("salesperson").innerHTML += `<tr class="text-center">
                  <th scope="row"><img src="https://c.tenor.com/9qZhM0uswAYAAAAd/bully-maguire-dance.gif" width="30"
                    height="30" class="rounded-circle"></th>
                  <td>${result[salesperson].staff_name}</td>
                  <td>${result[salesperson].email}</td>
                  <td class="fw-bold text-danger">${result[salesperson].amendment}</td>
                  <td class="fw-bold text-primary">${result[salesperson].pending}</td>
                  <td class="fw-bold text-success">${result[salesperson].sended}</td>
                </tr>`
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

// in progress
function getSalespersonTotalQuotes() {
    var supervisor_id = "1";
    $(async () => {
        // Change serviceURL to your own
        var serviceURL = "http://localhost:5000/salesperson_under_supervisor_quotations/" + supervisor_id;
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
                  <th scope="row"><img src="https://c.tenor.com/9qZhM0uswAYAAAAd/bully-maguire-dance.gif" width="100"
                    height="100" class="rounded-circle"></th>
                  <td>${result[salesperson].name}</td>
                  <td>${result[salesperson].email}</td>
                  <td>${result[salesperson].amendment}</td>
                  <td>${result[salesperson].pending}</td>
                  <td>$${result[salesperson].sended}</td>
                </tr>`
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