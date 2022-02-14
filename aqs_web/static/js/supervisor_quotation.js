function start() {
    if (window.location.href.split("#")[1] == null) {
        alert("You can't access this page without any quotation.")
        location.href = "supervisor_home";
    }
    getQuotationInfo();
}

function getQuotationInfo() {
    var supervisor_id = 1;
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
                document.getElementById("markup-value").value = result[0].markup_pct;
                document.getElementById("quotation-name").innerHTML = quotation_no + " - " + result[0].company_name;
                document.getElementById("quotation_no").innerHTML = quotation_no + `<i class="bi bi-box-arrow-in-up-right"></i>`;
                document.getElementById("comments").innerHTML = result[0].comment;
                document.getElementById("point-of-contact").innerHTML = result[0].first_name + " " + result[0].last_name +
                    `
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

                getQuotationParts();

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

function getSupervisorName(supervisor_id) {
    $(async () => {
        // Change serviceURL to your own
        var serviceURL = "http://localhost:5000/supervisorInfo/" + supervisor_id;
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
                document.getElementById('in-charge').innerHTML = result[0].first_name + " " + result[0].last_name;
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
                var markup = document.getElementById("markup-value").value/100 + 1;
                var total_quotation_price = 0;
                for (var part in result) {
                    if (result[part].remark == null) {
                        result[part].remark = "No remarks";
                    }
                    total_price = parseFloat((result[part].total_price * markup).toFixed(2));
                    total_quotation_price += total_price
                    if (result[part].is_bom == 1) {
                        document.getElementById("parts").innerHTML += `<th style="background-color:#F9E79F;" colspan="9">${result[part].description}</th>`
                    } else if (result[part].is_bom == 0 && result[part].level == "0.1") {
                        document.getElementById("parts").innerHTML += `
                        <tr style="background-color:#5DADE2;">
                            <th scope="row"><input type="checkbox"></th>
                            <td>${result[part].component_no}</td>
                            <td>${result[part].uom}</td>
                            <td>${result[part].description}</td>
                            <td>${result[part].quantity}</td>
                            <td>$${(result[part].unit_price * markup).toFixed(2)}</td>
                            <td>${total_price}</td>
                            <td>${result[part].remark}</td>
                            <td>
                                <button type="button" data-bs-toggle="modal" onclick="viewParts('${result[part].id}', '${result[part].remark}')" data-bs-target="#view-parts" class="btn btn-outline-secondary"><i class="bi bi-eye"></i></button>
                            </td>
                        </tr>
                        `
                    } else {
                        document.getElementById("parts").innerHTML += `<tr>
                        <th scope="row"><input type="checkbox"></th>
                        <td>${result[part].component_no}</td>
                        <td>${result[part].uom}</td>
                        <td>${result[part].description}</td>
                        <td>${result[part].quantity}</td>
                        <td>$${(result[part].unit_price * markup).toFixed(2)}</td>
                        <td>$${(result[part].total_price * markup).toFixed(2)}</td>
                        <td>${result[part].remark}</td>
                        <td>
                        <button type="button" data-bs-toggle="modal" onclick="viewParts('${result[part].id}', '${result[part].remark}')" data-bs-target="#view-parts" class="btn btn-outline-secondary"><i class="bi bi-eye"></i></button>
                        </td>
                    </tr>
                    `
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
                </tr>`
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
    </tr>`
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
function checkQuotationRights(supervisor_id, quotation_no) {
    $(async () => {
        // Change serviceURL to your own
        var serviceURL = "http://localhost:5000/supervisorCheck/" + supervisor_id + "/" + quotation_no;
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