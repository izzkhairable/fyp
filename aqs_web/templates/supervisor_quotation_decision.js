function start() {
    if (window.location.href.split("#")[1] == null) {
        alert("You can't access this page without any quotation.")
        location.href = "supervisor_home.html";
    }
    getQuotationParts();
    getQuotationInfo();
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
                console.log(result)
                for (var part in result) {
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
                            <td>$${result[part].total_price/result[part].quantity}</td>
                            <td>$${result[part].total_price}</td>
                            <td>${result[part].remark}</td>
                            <td>
                                <button type="button" data-bs-toggle="modal" onclick="editParts('${result[part].component_no}', '${result[part].remark}')" data-bs-target="#edit-parts" class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></button>
                                <button type="button" class="btn btn-outline-secondary"><i class="bi bi-trash-fill"></i></button>
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
                        <td>$${result[part].total_price/result[part].quantity}</td>
                        <td>$${result[part].total_price}</td>
                        <td>${result[part].remark}</td>
                        <td>
                        <button type="button" data-bs-toggle="modal" onclick="editParts('${result[part].component_no}', '${result[part].remark}')" data-bs-target="#edit-parts" class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></button>
                        <button type="button" class="btn btn-outline-secondary"><i class="bi bi-trash-fill"></i></button>
                        </td>
                    </tr>
                    `
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
                    document.getElementById("approve_button").disabled = false;
                    document.getElementById("reject_button").disabled = false;
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
            } else if (response.status == 404) {
                // No Rows
                console.log(result.message);
                alert("You can't access this page without a valid quotation.")
                location.href = "supervisor_home.html";
            } else {
                // unexpected outcome, throw the error
                throw response.status;
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
            alert("You can't access this page without a valid quotation.")
            location.href = "supervisor_home.html";
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

function editParts(component_no, remark) {
    document.getElementById("editModalLabel").innerHTML = "Edit Part - " + component_no;
    document.getElementById("remark").placeholder = remark;
    document.getElementById("edit-suppliers").innerHTML = `
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
                    document.getElementById("edit-suppliers").innerHTML += `
                    <tr id="${rowid}">
                        <td>
                        $<input type="number" id="price" name="price" value="${crawl_info[unique_supplier].unit_price}" ><br><br>
                        </td>
                        <td>
                        <input type="text" id="supplier" name="supplier" value="${crawl_info[unique_supplier].supplier}"><br><br>
                        </td>
                        <td>
                        <input type="text" id="link" name="link" value="${crawl_info[unique_supplier].url}"><br><br>
                        </td>
                        <td>
                        <input type="number" id="quantity" name="quantity" value="${crawl_info[unique_supplier].qty}"><br><br>
                        </td>
                        <td>
                        <button type="button" onclick="deleteSupplierRow(${rowid})" class="btn btn-sm btn-outline-secondary"><i class="bi bi-trash-fill"></i></button>
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

function addSupplier() {
    var table = document.getElementById("edit-suppliers");
    var rowid = table.rows[table.rows.length - 1].id + 1;
    document.getElementById("edit-suppliers").innerHTML += `
    <tr id="${rowid}">
        <td>
        $<input type="number" id="price" name="price"><br><br>
        </td>
        <td>
        <input type="text" id="supplier" name="supplier"><br><br>
        </td>
        <td>
        <input type="text" id="link" name="link"><br><br>
        </td>
        <td>
        <input type="number" id="quantity" name="quantity"><br><br>
        </td>
        <td>
        <button type="button" onclick="deleteSupplierRow(${rowid})" class="btn btn-sm btn-outline-secondary"><i class="bi bi-trash-fill"></i></button>
        </td>
    </tr>`;
}

function saveEdits() {
    var component_no = document.getElementById("editModalLabel").innerHTML.split(" - ")[1];
    var edited_crawl_info = [];
    var prices = document.getElementsByName("price");
    var suppliers = document.getElementsByName("supplier");
    var quantity = document.getElementsByName("quantity");
    var link = document.getElementsByName("link");
    var table = document.getElementById("edit-suppliers");
    var qty = 0;
    var total_price = 0;
    for (var i = 1, row; row = table.rows[i]; i++) {
        supplier = {}
        supplier["supplier"] = suppliers[i - 1].value;
        supplier["url"] = link[i - 1].value;
        supplier["qty"] = quantity[i - 1].value;
        qty += Number(quantity[i - 1].value);
        supplier['unit_price'] = prices[i - 1].value;
        total_price += Number(quantity[i - 1].value) * Number(prices[i - 1].value);
        edited_crawl_info.push(supplier);
    }
    var unit_price = total_price / qty;
    $(async () => {
        var serviceURL = "http://localhost:5000/updateComponent";
        const data = {
            component_no: component_no,
            edited_crawl_info: JSON.stringify(edited_crawl_info),
            unit_price: unit_price
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
                alert("There is an error saving changes.")
            } else {
                location.reload();
                alert("Successfully saved changes!")
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
        } // error
    });
}

function deleteSupplierRow(rowid) {
    var row = document.getElementById(rowid);
    row.parentNode.removeChild(row);
}