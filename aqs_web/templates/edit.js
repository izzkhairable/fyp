function saveChanges(){
  location.href = "salesperson_home.html";
}

function start(){
  getQuotationParts();
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
            console.log(result)
            for (var part in result) {
              if (result[part].is_bom == 1){
                document.getElementById("parts").innerHTML += `<th style="background-color:#F9E79F;" colspan="9">${result[part].description}</th>`
              }
              else if (result[part].is_bom == 0 && result[part].level == "0.1") {
                document.getElementById("parts").innerHTML += `<tr style="background-color:#5DADE2;">
                <th scope="row"><input type="checkbox"></th>
                <td>${result[part].component_no}</td>
                <td>${result[part].uom}</td>
                <td>${result[part].description}</td>
                <td>${result[part].quantity}</td>
                <td>$${result[part].total_price/result[part].quantity}</td>
                <td>$${result[part].total_price}</td>
                <td>${result[part].remark}</td>
                <td>
                  <button type="button" data-bs-toggle="modal" data-bs-target="#edit-parts" class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></button>
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
                <td>$${result[part].total_price/result[part].quantity}</td>
                <td>$${result[part].total_price}</td>
                <td>${result[part].remark}</td>
                <td>
                  <button type="button" data-bs-toggle="modal" onclick="editParts('${result[part].component_no}', '${result[part].remark}', '${result[part].crawl_info}')" data-bs-target="#edit-parts" class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></button>
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

function editParts(component_no, remark, crawl_info){
  document.getElementById("editModalLabel").innerHTML = "Edit Part - " + component_no;
  console.log(remark)
  console.log(crawl_info);
}
