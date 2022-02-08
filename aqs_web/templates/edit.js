function start(){
  getQuotationInfo();
}

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
              if (result[part].is_bom == 1){
                document.getElementById("parts").innerHTML += `<tr style="background-color:#F9E79F;" colspan="9">
                  <th></th>
                  <th>${result[part].component_no}</th>
                  <th>${result[part].uom}</th>
                  <th>${result[part].description}</th>
                  <th></th>
                  <th></th>
                  <th></th>
                  <th>${result[part].remark}</th>
                  <th>
                    <button type="button" data-bs-toggle="modal" onclick="editBom('${result[part].id}', '${result[part].component_no}', '${result[part].uom}', '${result[part].description}', '${result[part].remark}')" data-bs-target="#edit-bom" class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></button>
                    <button type="button" class="btn btn-outline-secondary"><i class="bi bi-trash-fill"></i></button>
                    <button type="button" class="btn btn-outline-secondary"><i class="bi bi-plus-lg"></i></button>
                  </th>
                </tr>`
              }
              else if (result[part].is_bom == 0 && result[part].level == "0.1") {
                document.getElementById("parts").innerHTML += `<tr style="background-color:#5DADE2;">
                <th scope="row"><input type="checkbox"></th>
                <td>${result[part].component_no}</td>
                <td>${result[part].uom}</td>
                <td>${result[part].description}</td>
                <td>${result[part].quantity}</td>
                <td>$${(result[part].unit_price * markup).toFixed(2)}</td>
                <td>$${(result[part].total_price * markup).toFixed(2)}</td>
                <td>${result[part].remark}</td>
                <td>
                  <button type="button" data-bs-toggle="modal" onclick="editParts('${result[part].id}', '${result[part].component_no}', '${result[part].remark}')" data-bs-target="#edit-parts" class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></button>
                  <button type="button" class="btn btn-outline-secondary"><i class="bi bi-trash-fill"></i></button>
                </td>
              </tr>
              `
              }
              else {
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
                  <button type="button" data-bs-toggle="modal" onclick="editParts('${result[part].id}', '${result[part].component_no}', '${result[part].remark}')" data-bs-target="#edit-parts" class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></button>
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
            document.getElementById("labour").value = result[0].labour_cost;
            document.getElementById("markup").value = result[0].markup_pct;
            document.getElementById("labour-remarks").value = result[0].labour_cost_description;
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

function updateAdditionalCosts(){
  var quotation_no = document.getElementById("quotation-no-for-cost-update").value;
  var labour_cost = document.getElementById("labour").value;
  var markup = document.getElementById("markup").value;
  var labour_remarks = document.getElementById("labour-remarks").value;
  $(async() => {           
    var serviceURL = "http://localhost:5000/updateLabourCost";
    const data = {
      quotation_no: quotation_no,
      labour_cost: labour_cost,
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

function editParts(id, component_no, remark){
  document.getElementById("editModalLabel").innerHTML = "Edit Part - " + id;
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

function editBom(id, component_no, uom, description, remark){
  document.getElementById("editBomModalLabel").innerHTML = "Edit BOM - " + id;
  document.getElementById("bom-component-no").value = component_no;
  document.getElementById("bom-uom").value = uom;
  document.getElementById("bom-description").value = description;
  document.getElementById("bom-remark").value = remark;
}

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

function saveEdits(){
  var id = document.getElementById("editModalLabel").innerHTML.split(" - ")[1];
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

function saveBomEdits(){
  var id = document.getElementById("editBomModalLabel").innerHTML.split(" - ")[1];
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