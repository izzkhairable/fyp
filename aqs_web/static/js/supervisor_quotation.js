var supervisor_id = document.getElementById('staff_id').value;

function start() {
    if (window.location.href.split("#")[1] == null) {
        alert("You can't access this page without any quotation.")
        location.href = "supervisor_home";
    }
    getQuotationInfo();
}

function getQuotationInfo() {
    var quotation_no = window.location.href.split("#")[1];
    $(async () => {
        // Change serviceURL to your own
        var serviceURL = "http://localhost:5000/quotationInfo/" + quotation_no;
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
                document.getElementById("quotation-name").innerHTML = quotation_no + " - " + result[0].company_name;
                document.getElementById("quotation_no").innerHTML = quotation_no + `<i class="bi bi-box-arrow-in-up-right"></i>`;
                document.getElementById("comments").innerHTML = result[0].comment;
                document.getElementById("point-of-contact").innerHTML =
                    `<a class='link-primary fw-bold' href='profile#id=${result[0].assigned_staff}'><u>` + result[0].first_name + " " + result[0].last_name +
                    `</u></a>
                <a href=""><i class="bi bi-telephone"></i></a>
                <a href="mailto:${result[0].staff_email}"><i class="bi bi-envelope"></i></a>
                `;
                if (result[0].comment != null) {
                    document.getElementById("comments").innerHTML = result[0].comment;
                } else {
                    document.getElementById("comments").innerHTML = "No comments.";
                }
                if (result[0].supervisor != null) {
                    getSupervisorName(result[0].supervisor);
                } else {
                    document.getElementById('in-charge').innerHTML = "No In-Charge.";
                }

                var quotation_status = document.getElementById("quotation_status");
                if (result[0].status == "draft") {
                    quotation_status.className = "btn btn-secondary float-right";
                    quotation_status.innerHTML = "Draft";
                } else if (result[0].status == "approved") {
                    quotation_status.className = "btn btn-success float-right";
                    quotation_status.innerHTML = "Approved";
                } else if (result[0].status == "sent") {
                    quotation_status.className = "btn btn-warning float-right";
                    quotation_status.innerHTML = "Pending Approval";

                    checkQuotationRights(supervisor_id, quotation_no);

                } else if (result[0].status == "rejected") {
                    quotation_status.className = "btn btn-danger float-right";
                    quotation_status.innerHTML = "Rejected";
                } else if (result[0].status == "loss") {
                    quotation_status.className = "btn btn-danger float-right";
                    quotation_status.innerHTML = "Job Loss";
                } else if (result[0].status == "win") {
                    quotation_status.className = "btn btn-success float-right";
                    quotation_status.innerHTML = "Job Won";
                }

                document.getElementById("quotation_no_modal").innerHTML = quotation_no + " from " + result[0].first_name + " " + result[0].last_name;
                document.getElementById("labour").value = result[0].labour_cost;
                document.getElementById("labour-hours").value = result[0].labour_no_of_hours;
                document.getElementById("total-labour-cost").value = result[0].labour_cost * result[0].labour_no_of_hours;
                document.getElementById("testing-cost").value = result[0].testing_cost;
                document.getElementById("markup").value = result[0].markup_pct;
                document.getElementById("labour-remarks").value = result[0].remark;
                calculateLabourCost()
                getQuotationParts();

            } else if (response.status == 404) {
                // No Rows
                console.log(result.message);
                alert("No such quotation exist.")
                location.href = "home";
            } else {
                // unexpected outcome, throw the error
                throw response.status;
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
            alert("The server is current down, please try again later.")
            location.href = "home";
        } // error
    });
}

function getSupervisorName(sup_id) {
    $(async () => {
        // Change serviceURL to your own
        var serviceURL = "http://localhost:5000/supervisorInfo/" + sup_id;
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
                document.getElementById('in-charge').innerHTML = `<a class='fw-bold link-primary' href='profile#id=${sup_id}'><u>` + result[0].first_name + " " + result[0].last_name + `</u></a>`;
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

function getQuotationParts() {
    var quotation_no = window.location.href.split("#")[1];
    document.getElementById("page-name").innerHTML = quotation_no;
    $(async () => {
        // Change serviceURL to your own
        var serviceURL = "http://localhost:5000/quotationParts/" + quotation_no;
        document.getElementById("parts").innerHTML = "";
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
                var markup = document.getElementById("markup").value / 100 + 1;
                var total_quotation_price = 0;
                for (var part in result) {
                    if (result[part].remark == null) {
                        result[part].remark = "No remarks";
                    }
                    total_price = parseFloat((result[part].total_price * markup).toFixed(2));
                    total_quotation_price += total_price
                    if (result[part].is_bom == 1) {
                        document.getElementById("parts").innerHTML += `<tr colspan="9" class="fw-bold">
                            <td></td>
                            <td>${result[part].component_no}</td>
                            <td>${result[part].lvl}</td>
                            <td>${result[part].uom}</td>
                            <td>${result[part].description}</td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td>${result[part].remark}</td>
                            <td>
                            </td>
                        </tr>`;
                    } else if (result[part].is_bom == 0 && result[part].level == "0.1") {
                        // loose item
                        document.getElementById("parts").innerHTML += `<tr>
                        <th scope="row"></th>
                        <td>${result[part].component_no}</td>
                        <td>${result[part].lvl}</td>
                        <td>${result[part].uom}</td>
                        <td>${result[part].description}</td>
                        <td>${result[part].quantity}</td>
                        <td>$${(result[part].unit_price * markup).toFixed(2)}</td>
                        <td>$${(result[part].total_price * markup).toFixed(2)}</td>
                        <td>${result[part].remark}</td>
                        <td>
                            <button type="button" data-bs-toggle="modal" onclick="viewParts('${result[part].id}', '${result[part].remark}')" data-bs-target="#view-parts" class="btn btn-outline-secondary"><i class="bi bi-eye"></i></button>
                        </td>
                    </tr>`;
                    } else {
                        document.getElementById("parts").innerHTML += `<tr>
                            <th scope="row"></th>
                            <td>${result[part].component_no}</td>
                            <td>${result[part].lvl}</td>
                            <td>${result[part].uom}</td>
                            <td>${result[part].description}</td>
                            <td>${result[part].quantity}</td>
                            <td>$${(result[part].unit_price * markup).toFixed(2)}</td>
                            <td>$${(result[part].total_price * markup).toFixed(2)}</td>
                            <td>${result[part].remark}</td>
                            <td>
                                <button type="button" data-bs-toggle="modal" onclick="viewParts('${result[part].id}', '${result[part].remark}')" data-bs-target="#view-parts" class="btn btn-outline-secondary"><i class="bi bi-eye"></i></button>
                            </td>
                        </tr>`;
                    }
                }
                document.getElementById("parts").innerHTML += `
                <tr>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td colspan="3">
                        Total: <b>$${total_quotation_price.toFixed(2)}</b>
                    </td>
                </tr>`;
                calculateTotalOverallCost(total_quotation_price);
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

function viewParts(component_no, remark) {
    document.getElementById("viewModalLabel").innerHTML = "View Part - " + component_no;
    document.getElementById("remark").placeholder = remark;
    document.getElementById("view-suppliers").innerHTML = `
    <tr>
        <th scope="col">Unit Price</th>
        <th scope="col">Supplier</th>
        <th scope="col">Link</th>   
        <th scope="col">Quantity</th>
    </tr>`;
    $(async () => {
        // Change serviceURL to your own
        var serviceURL = "http://localhost:5000/partinfo/" + component_no;

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
                var crawl_info = JSON.parse(result[0]['crawl_info'])
                var rowid = 0;
                for (var unique_supplier in crawl_info) {
                    rowid++;
                    document.getElementById("view-suppliers").innerHTML += `
                    <tr id="${rowid}">
                        <td>
                        $<input type="number" id="price" name="price" value="${crawl_info[unique_supplier].unit_price}" disabled><br><br>
                        </td>
                        <td>
                        <input type="text" id="supplier" name="supplier" value="${crawl_info[unique_supplier].supplier}" disabled><br><br>
                        </td>
                        <td>
                        <input type="text" id="link" name="link" value="${crawl_info[unique_supplier].url}" disabled><br><br>
                        </td>
                        <td>
                        <input type="number" id="quantity" name="quantity" value="${crawl_info[unique_supplier].qty}" disabled><br><br>
                        </td>
                    </tr>`;
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

function quotationDecision(decision) {
    var rejection_reason = document.getElementById("rejectionReason").value;
    if (decision == "approved") {
        rejection_reason = null;
    } else if (decision == "rejected") {
        if (rejection_reason == "") {
            rejection_reason = null;
        }
    }
    var quotation_no = window.location.href.split("#")[1];
    $(async () => {
        var serviceURL = "http://localhost:5000/supervisorQuotationDecision";
        const data = {
            status: decision,
            comment: rejection_reason,
            quotation_no: quotation_no
        };

        try {
            const response =
                await fetch(
                    serviceURL, {
                        method: 'POST',
                        body: JSON.stringify(data),
                        headers: {
                            Accept: 'application/json',
                            'Content-Type': 'application/json',
                        }
                    }
                );
            const result = await response.json();
            if (response.status === 500) {
                alert("There is an error submitting. Please try again.")
            } else {
                location.reload();
                alert("Quotation successfully " + decision + "!")
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
        } // error
    });
}

// check if this quotation is meant for this supervisor's approval
function checkQuotationRights(sup_id, quotation_no) {
    $(async () => {
        // Change serviceURL to your own
        var serviceURL = "http://localhost:5000/supervisorCheck/" + sup_id + "/" + quotation_no;
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
                if (Object.keys(result).length == 1) {
                    document.getElementById("approve_button").disabled = false;
                    document.getElementById("reject_button").disabled = false;
                    document.getElementById("approve_click").setAttribute("onclick", "quotationDecision('approved')");
                    document.getElementById("reject_click").setAttribute("onclick", "quotationDecision('rejected')");
                } else {
                    alert("You don't have the rights to approve/reject this quotation.")
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
            console.log('There is a problem with the check, please try again later.<br />' + error);
            alert("The server is current down, please try again later.")
            location.href = "supervisor_home";
        } // error
    });
}

// Filter table
function filterComponents() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("componentSearch");
    filter = input.value.toUpperCase();
    table = document.getElementById("componentsTable");
    tr = table.getElementsByTagName("tr");
    condition = document.getElementById("filter_components").value;
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

// Calculate labour costs
function calculateLabourCost() {
    var labour_cost = document.getElementById("labour").value;
    var labour_hour = document.getElementById("labour-hours").value;
    var total_labour_cost = labour_cost * labour_hour;
    document.getElementById("total-labour-cost").value = total_labour_cost;
}

function calculateTotalOverallCost(total_quotation_price) {
    var total_labour_cost = parseFloat(document.getElementById("total-labour-cost").value);
    var testing_cost = parseFloat(document.getElementById("testing-cost").value);
    var total_overall_cost = total_quotation_price + total_labour_cost + testing_cost;
    document.getElementById('overall-cost').value = total_overall_cost;
}