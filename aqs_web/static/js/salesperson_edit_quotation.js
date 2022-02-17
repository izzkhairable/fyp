function start(){
  getQuotationInfo();
}

// Gets all components and BOMs info
function getQuotationParts(){
  var quotation_no = window.location.href.split("#")[1];
  $(async() => {           
    // Change serviceURL to your own
    var serviceURL = "http://localhost:5000/quotationParts/" + quotation_no;
    document.getElementById("parts").innerHTML = "";
    try {
        const response =
        await fetch(
        serviceURL, { method: 'GET' }
        );
        const result = await response.json();
        if (response.status === 200) {
            // success case
            var markup = document.getElementById("markup").value/100 + 1;
            for (var part in result) {
              // BOM
              if (result[part].is_bom == 1){
                document.getElementById("parts").innerHTML += `<tr colspan="9">
                  <td><input type="checkbox" name="deleteList" value="${result[part].id}"></td>
                  <td>${result[part].component_no}</td>
                  <td>${result[part].lvl}</td>
                  <td>${result[part].uom}</td>
                  <td>${result[part].description}</td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td>${result[part].remark}</td>
                  <td>
                    <button type="button" data-bs-toggle="modal" onclick="editBom('${result[part].id}', '${result[part].component_no}', '${result[part].uom}', '${result[part].description}', '${result[part].remark}')" data-bs-target="#edit-bom" class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></button>
                    <button type="button" class="btn btn-outline-secondary" data-bs-toggle="modal" data-bs-target="#confirm-delete" onclick="displayConfirmDeleteModal('${result[part].id}', '${quotation_no}', '${result[part].component_no}')"><i class="bi bi-trash-fill"></i></button>
                    <button type="button" class="btn btn-outline-secondary" data-bs-toggle="modal" data-bs-target="#add-component-under-bom" onclick="insertComponentUnderBom('${result[part].id}', '${quotation_no}', '${result[part].component_no}')"><i class="bi bi-plus-lg"></i></button>
                  </td>
                </tr>`
              }
              // loose item
              else if (result[part].is_bom == 0 && result[part].level == "0.1") {
                document.getElementById("parts").innerHTML += `<tr>
                <th scope="row"><input type="checkbox" name="deleteList" value="${result[part].id}"></th>
                <td>${result[part].component_no}</td>
                <td>${result[part].lvl}</td>
                <td>${result[part].uom}</td>
                <td>${result[part].description}</td>
                <td>${result[part].quantity}</td>
                <td>$${(result[part].unit_price * markup).toFixed(2)}</td>
                <td>$${(result[part].total_price * markup).toFixed(2)}</td>
                <td>${result[part].remark}</td>
                <td>
                  <button type="button" data-bs-toggle="modal" onclick="editParts('${result[part].id}', '${result[part].component_no}', '${result[part].remark}')" data-bs-target="#edit-parts" class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></button>
                  <button type="button" class="btn btn-outline-secondary" data-bs-toggle="modal" data-bs-target="#confirm-delete" onclick="displayConfirmDeleteModal('${result[part].id}', '${quotation_no}', '${result[part].component_no}')"><i class="bi bi-trash-fill"></i></button>
                </td>
              </tr>
              `
              }
              // components under bom
              else {
                document.getElementById("parts").innerHTML += `<tr>
                <th scope="row"><input type="checkbox" name="deleteList" value="${result[part].id}"></th>
                <td>${result[part].component_no}</td>
                <td>${result[part].lvl}</td>
                <td>${result[part].uom}</td>
                <td>${result[part].description}</td>
                <td>${result[part].quantity}</td>
                <td>$${(result[part].unit_price * markup).toFixed(2)}</td>
                <td>$${(result[part].total_price * markup).toFixed(2)}</td>
                <td>${result[part].remark}</td>
                <td>
                  <button type="button" data-bs-toggle="modal" onclick="editParts('${result[part].id}', '${result[part].component_no}', '${result[part].remark}')" data-bs-target="#edit-parts" class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></button>
                  <button type="button" class="btn btn-outline-secondary" data-bs-toggle="modal" data-bs-target="#confirm-delete" onclick="displayConfirmDeleteModal('${result[part].id}', '${quotation_no}', '${result[part].component_no}')"><i class="bi bi-trash-fill"></i></button>
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

// Gets the quotation info
function getQuotationInfo(){
  var quotation_no = window.location.href.split("#")[1];
  $(async() => {           
    // Change serviceURL to your own
    var serviceURL = "http://localhost:5000/quotationInfo/" + quotation_no;
    document.getElementById("parts").innerHTML = "";
    try {
        const response =
        await fetch(
        serviceURL, { method: 'GET' }
        );
        const result = await response.json();
        if (response.status === 200) {
            // success case
            getQuotationParts();
            document.getElementById("quotation-no-for-cost-update").value = quotation_no;
            document.getElementById("quotation-name").innerHTML = quotation_no + " - " + result[0].company_name;
            document.getElementById("comments").innerHTML = result[0].comment;
            document.getElementById("point-of-contact").innerHTML = result[0].first_name + " " + result[0].last_name;
            document.getElementById("comments").value = result[0].comment;
            document.getElementById("labour").value = result[0].labour_cost;
            document.getElementById("labour-hours").value = result[0].labour_no_of_hours;
            document.getElementById("total-labour-cost").value = result[0].labour_cost * result[0].labour_no_of_hours;
            document.getElementById("testing-cost").value = result[0].testing_cost;
            document.getElementById("markup").value = result[0].markup_pct;
            document.getElementById("labour-remarks").value = result[0].remark;
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

// Saves edits done to the quotation
function saveQuotationEdits(){
  var quotation_no = window.location.href.split("#")[1];
  var comments = document.getElementById("edit-comments").value;
  $(async() => {           
    var serviceURL = "http://localhost:5000/updateQuotationInfo";
    const data = {
      quotation_no: quotation_no,
      comments: comments
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
            alert("There is an error saving changes.")
            }
            else {
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

// Updates additional costs
function updateAdditionalCosts(){
  var quotation_no = document.getElementById("quotation-no-for-cost-update").value;
  var labour_cost = document.getElementById("labour").value;
  var labour_hours = document.getElementById("labour-hours").value;
  var testing_cost = document.getElementById("testing-cost").value;
  var markup = document.getElementById("markup").value;
  var labour_remarks = document.getElementById("labour-remarks").value;
  $(async() => {           
    var serviceURL = "http://localhost:5000/updateLabourCost";
    const data = {
      quotation_no: quotation_no,
      labour_cost: labour_cost,
      labour_hours,
      testing_cost,
      markup: markup,
      labour_remarks: labour_remarks
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
            alert("There is an error saving changes.")
            }
            else {
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

// Edit components
function editParts(id, component_no, remark){
  document.getElementById("editModalLabel").innerHTML = "Edit Part - " + component_no;
  document.getElementById("edit-parts-id").value = id;
  document.getElementById("remark").value = remark;
  document.getElementById("edit-suppliers").innerHTML = `                    <tr>
  <th scope="col">Unit Price</th>
  <th scope="col">Supplier</th>
  <th scope="col">Link</th>
  <th scope="col">Quantity</th>
</tr>`
  $(async() => {           
    // Change serviceURL to your own
    var serviceURL = "http://localhost:5000/partinfo/" + id;
    
    try {
        const response =
        await fetch(
        serviceURL, { method: 'GET' }
        );
        const result = await response.json();
        if (response.status === 200) {
            // success case
            var crawl_info = JSON.parse(result[0]['crawl_info'])
            var rowid = 0;
            for (var unique_supplier in crawl_info){
              rowid ++;
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

// Updates the edit Bom modal based on the selected BOM
function editBom(id, component_no, uom, description, remark){
  document.getElementById("editBomModalLabel").innerHTML = "Edit BOM - " + component_no;
  document.getElementById("edit-bom-id").value = id;
  document.getElementById("bom-component-no").value = component_no;
  document.getElementById("bom-uom").value = uom;
  document.getElementById("bom-description").value = description;
  document.getElementById("bom-remark").value = remark;
}

// Add supplier row to the component edit modal
function addSupplier(){
  var table = document.getElementById("edit-suppliers");
  var rowid = table.rows[table.rows.length - 1].id + 1;
  document.getElementById("edit-suppliers").innerHTML += `              <tr id="${rowid}">
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

// Saves editing done to components
function saveEdits(){
  var id = document.getElementById("edit-parts-id").value;
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
    supplier["supplier"] = suppliers[i-1].value;
    supplier["url"] = link[i-1].value;
    supplier["qty"] = quantity[i-1].value;
    qty += Number(quantity[i-1].value);
    supplier['unit_price'] = prices[i-1].value;
    total_price += Number(quantity[i-1].value) * Number(prices[i-1].value);
    edited_crawl_info.push(supplier);
  }
  var unit_price = total_price / qty;
  $(async() => {           
    var serviceURL = "http://localhost:5000/updateComponent";
    const data = {
        id: id,
        edited_crawl_info: JSON.stringify(edited_crawl_info),
        unit_price: unit_price,
        qty: qty
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
            alert("There is an error saving changes.")
            }
            else {
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

// Saves editing done to BOMs
function saveBomEdits(){
  var id = document.getElementById("edit-bom-id").value;
  var component_no = document.getElementById("bom-component-no").value;
  var uom = document.getElementById("bom-uom").value;
  var description = document.getElementById("bom-description").value;
  var remark = document.getElementById("bom-remark").value;

  $(async() => {           
    var serviceURL = "http://localhost:5000/updateBomInfo";
    const data = {
        id: id,
        component_no: component_no,
        uom: uom,
        description: description,
        remark: remark
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
            alert("There is an error saving changes.")
            }
            else {
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

function deleteSupplierRow(rowid){
  var row = document.getElementById(rowid);
  row.parentNode.removeChild(row);
}

// Deletes the selected component
function deleteComponent(){
  var id = document.getElementById("delete-component-id").value;
  var quotation_no = document.getElementById("delete-component-quotation-no").value;
  $(async() => {           
    var serviceURL = "http://localhost:5000/deleteComponent";
    const data = {
        id: id,
        quotation_no: quotation_no
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
            alert("There is an error deleting.")
            }
            else {
              location.reload();
                alert("Successfully deleted!")
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
                } // error
    });
}

// Updates the insert component modal to show the component_no of the BOM
function insertComponentUnderBom(id, quotation_no, component_no){
  document.getElementById("addComponentUnderBomLabel").innerHTML = "Add Component Under " + component_no;
  document.getElementById("add-component-under-bom-id").value = id;
  document.getElementById("add-component-under-bom-quotation-no").value = quotation_no;
}

// Adds component under a specific BOM
function addComponentUnderBom(){
  var id = document.getElementById("add-component-under-bom-id").value;
  var quotation_no = document.getElementById("add-component-under-bom-quotation-no").value;
  var component_no = document.getElementById("new-component-no-under-bom").value;
  var uom = document.getElementById("new-uom-under-bom").value;
  var description = document.getElementById("new-description-under-bom").value;
  var is_bom = document.querySelector('input[name="new-is-bom?-under-bom"]:checked').value;

  $(async() => {           
    var serviceURL = "http://localhost:5000/insertComponentUnderBom";
    const data = {
        id: id,
        quotation_no: quotation_no,
        component_no: component_no,
        uom: uom,
        description: description,
        is_bom: is_bom
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
            alert("There is an error adding a new component.")
            }
            else {
              location.reload();
                alert("Successfully added a new component!")
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
                } // error
    });
}

// Adds component to the database
function addComponent(){
  var quotation_no = window.location.href.split("#")[1];
  var component_no = document.getElementById("new-component-no").value;
  var uom = document.getElementById("new-uom").value;
  var description = document.getElementById("new-description").value;
  var is_bom = document.querySelector('input[name="new-is-bom?"]:checked').value;

  $(async() => {           
    var serviceURL = "http://localhost:5000/insertComponent";
    const data = {
        quotation_no: quotation_no,
        component_no: component_no,
        uom: uom,
        description: description,
        is_bom: is_bom
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
            alert("There is an error adding a new component.")
            }
            else {
              location.reload();
                alert("Successfully added a new component!")
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
                } // error
    });
}

// Display the modal to confirm delete
function displayConfirmDeleteModal(id, quotation_no, component_no){
  document.getElementById("delete-component-id").value = id;
  document.getElementById("delete-component-quotation-no").value = quotation_no;
  document.getElementById("confirm-delete-label").innerHTML = "Are you sure you want to delete <b>" + component_no + "</b>?";
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

// Calculates total labour cost and updates it
function calculateLabourCost(){
  var labour_cost = document.getElementById("labour").value;
  var labour_hour = document.getElementById("labour-hours").value;
  var total_labour_cost = labour_cost * labour_hour;
  document.getElementById("total-labour-cost").value = total_labour_cost;
}

// Changes status of quotation to 'sent'
function submitForReview(){
  var quotation_no = window.location.href.split("#")[1];
  $(async() => {           
    var serviceURL = "http://localhost:5000/submitForReview";
    const data = {
      quotation_no: quotation_no,
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
            alert("There is an error sending quotation for review.")
            }
            else {
              location.reload();
                alert("Successfully sent quotation for review!")
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
                } // error
    });
}

// Delete multiple components based on checkboxes selected
function deleteMultipleComponents(){
  var quotation_no = window.location.href.split("#")[1];
  var selected = document.querySelectorAll('input[name="deleteList"]:checked');
  var selectList = [];
  for (var i=0; i<selected.length; i++) {
    if (selected[i].value != "") {
      selectList.push(selected[i].value);
    }
  }
  console.log(selectList);
  $(async() => {           
    var serviceURL = "http://localhost:5000/deleteMultipleComponents";
    const data = {
        quotation_no: quotation_no,
        selectList
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
            alert("There is an error deleting the selected components.")
            }
            else {
              location.reload();
                alert("Successfully deleted the selected components!")
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
                } // error
    });
}

// Checks all checkboxes for deleting
function checkAllBoxes(source){
  var deleteList = document.getElementsByName("deleteList");
  for (var i=0; i<deleteList.length; i++){
    deleteList[i].checked = source.checked;
  }
}

// Check if any checkboxes are selected
function checkIfCheckboxSelected(){
  var selected = document.querySelectorAll('input[name="deleteList"]:checked');
  if (selected.length == 0) {
    document.getElementById("confirm-multiple-delete-label").innerHTML = "You did not select any components.";
    document.getElementById("confirm-multiple-delete-footer").innerHTML = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`;
  }
  else {
    document.getElementById("confirm-multiple-delete-label").innerHTML = "Are you sure you want to delete the selected components?"
    document.getElementById("confirm-multiple-delete-footer").innerHTML = `<button type="button" class="btn btn-primary" onclick="deleteMultipleComponents()">Yes</button>
    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">No</button>`;
  }
}