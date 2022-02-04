function start() {
    getAllQuotations();
}

function getAllQuotations() {
    $(async () => {
        // Change serviceURL to your own
        var supervisor_id = 1;
        var serviceURL = "http://localhost:5000/supervisorAllQuotations/" + supervisor_id;
        document.getElementById("quotations").innerHTML = "";
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
                for (var quotation in result) {
                    document.getElementById("quotations").innerHTML += `<tr>`;
                    document.getElementById("quotations").innerHTML += `
                  <th scope="row"><input type="checkbox"></th>
                  <td><a href="supervisor_quotation_decision#${result[quotation].quotation_no}" class="link-primary"><u>${result[quotation].quotation_no}</u></a></td>
                  <td>${result[quotation].company_name}</td>
                  <td>${result[quotation].first_name} ${result[quotation].last_name}</td>
                  <td>${result[quotation].rfq_date}</td>
                  <td id="status_${result[quotation].quotation_no}"></td>
                </tr>`;
                    if (result[quotation].status == "rejected") {
                        document.getElementById("status_"+result[quotation].quotation_no).className = "text-danger";
                        document.getElementById("status_"+result[quotation].quotation_no).innerHTML = "Need Amendment";
                    }
                    else if (result[quotation].status == "approved") {
                        document.getElementById("status_"+result[quotation].quotation_no).className = "text-success";
                        document.getElementById("status_"+result[quotation].quotation_no).innerHTML = "Sent to Customer";
                    }
                    else if (result[quotation].status == "sent") {
                        document.getElementById("status_"+result[quotation].quotation_no).className = "text-primary";
                        document.getElementById("status_"+result[quotation].quotation_no).innerHTML = "Pending Approval";
                    }
                    else if (result[quotation].status == "draft") {
                        document.getElementById("status_"+result[quotation].quotation_no).className = "text-secondary";
                        document.getElementById("status_"+result[quotation].quotation_no).innerHTML = "Draft";
                    }
                    else if (result[quotation].status == "win") {
                        document.getElementById("status_"+result[quotation].quotation_no).className = "text-success fw-bold";
                        document.getElementById("status_"+result[quotation].quotation_no).innerHTML = "Win";
                    }
                    else {
                        document.getElementById("status_"+result[quotation].quotation_no).className = "text-danger fw-bold";
                        document.getElementById("status_"+result[quotation].quotation_no).innerHTML = "Loss";
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