var supervisor_id = document.getElementById('staff_id').value;

function start() {
    getAllQuotations();
    checkForFilters();
}

function getAllQuotations() {
    $(async () => {
        // Change serviceURL to your own
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
                for (var quotation in result) {
                    document.getElementById("quotations").innerHTML += `<tr>`;
                    document.getElementById("quotations").innerHTML += `
                  <th scope="row"><input type="checkbox"></th>
                  <td><a href="supervisor_quotation#${result[quotation].quotation_no}" class="link-primary"><u>${result[quotation].quotation_no}</u></a></td>
                  <td>${result[quotation].company_name}</td>
                  <td>${result[quotation].first_name} ${result[quotation].last_name}</td>
                  <td>${result[quotation].rfq_date}</td>
                  <td id="status_${result[quotation].quotation_no}"></td>
                </tr>`;
                    if (result[quotation].status == "rejected") {
                        document.getElementById("status_" + result[quotation].quotation_no).className = "text-danger";
                        document.getElementById("status_" + result[quotation].quotation_no).innerHTML = "Need Amendment";
                    } else if (result[quotation].status == "approved") {
                        document.getElementById("status_" + result[quotation].quotation_no).className = "text-success";
                        document.getElementById("status_" + result[quotation].quotation_no).innerHTML = "Sent to Customer";
                    } else if (result[quotation].status == "sent") {
                        document.getElementById("status_" + result[quotation].quotation_no).className = "text-primary";
                        document.getElementById("status_" + result[quotation].quotation_no).innerHTML = "Pending Approval";
                    } else if (result[quotation].status == "draft") {
                        document.getElementById("status_" + result[quotation].quotation_no).className = "text-secondary";
                        document.getElementById("status_" + result[quotation].quotation_no).innerHTML = "Draft";
                    } else if (result[quotation].status == "win") {
                        document.getElementById("status_" + result[quotation].quotation_no).className = "text-success fw-bold";
                        document.getElementById("status_" + result[quotation].quotation_no).innerHTML = "Win";
                    } else {
                        document.getElementById("status_" + result[quotation].quotation_no).className = "text-danger fw-bold";
                        document.getElementById("status_" + result[quotation].quotation_no).innerHTML = "Loss";
                    }
                }
                checkForFilters();
                if (document.getElementById("myInput").value != "") {
                    filter();
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

// Filter table
function filter() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("myTable");
    tr = table.getElementsByTagName("tr");
    condition = document.getElementById("filter_condition").value;
    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[condition];
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

function showPendingOnly() {
    switch_check = document.getElementById("pending-only-check").checked
    if (switch_check == true) {
        var table, tr, td, i, txtValue;
        table = document.getElementById("myTable");
        tr = table.getElementsByTagName("tr");
        for (i = 0; i < tr.length; i++) {
            var td = tr[i].getElementsByTagName("td")[4];
            if (td) {
                txtValue = td.textContent || td.innerText;
                if (txtValue == "Pending Approval") {
                    tr[i].style.display = "";
                } else {
                    document.getElementById("myTable").deleteRow(i);
                }
            }
        }
        filter_check = document.getElementById("myInput");
        if (filter_check != "") {
            filter()
        }
    } else {
        getAllQuotations();
    }
}

// check for filters, did they come here from clicking on another page?
function checkForFilters() {
    redirect_filters = window.location.href.split("#")[1];
    if (redirect_filters != undefined) {
        filter_conditions = redirect_filters.split('&');
        filter_name = decodeURI(filter_conditions[0].split('=')[1]);
        filter_status = decodeURI(filter_conditions[1].split('=')[1]);
        var table, tr, i, txtValue1, txtValue2;
        table = document.getElementById("myTable");
        tr = table.getElementsByTagName("tr");
        for (i = 0; i < tr.length; i++) {
            var td_con1 = tr[i].getElementsByTagName("td")[2];
            var td_con2 = tr[i].getElementsByTagName("td")[4];
            if (td_con1) {
                txtValue1 = td_con1.textContent || td_con1.innerText;
                txtValue2 = td_con2.textContent || td_con2.innerText;
                if (txtValue1 + txtValue2 == filter_name + filter_status) {
                    tr[i].style.display = "";
                } else {
                    document.getElementById("myTable").deleteRow(i);
                }
            }
        }
    }
}