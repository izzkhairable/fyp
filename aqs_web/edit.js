function saveChanges(){
  location.href = "home.html";
}

function getQuotationParts(){
  var quotation_id = window.location.href.split("#")[1];
  $(async() => {           
    // Change serviceURL to your own
    var serviceURL = "http://localhost:5000/quotationParts/" + quotation_id;
    document.getElementById("parts").innerHTML = "";
    try {
        const response =
        await fetch(
        serviceURL, { method: 'GET' }
        );
        const result = await response.json();
        if (response.status === 200) {
            // success case
            for (var part in result) {
              document.getElementById("parts").innerHTML += `<tr>
                <th scope="row"><input type="checkbox"></th>
                <td>10000025</td>
                <td>${result[part].description}</td>
                <td>${result[part].qty}</td>
                <td>${result[part].mfg_pn}</td>
                <td>${result[part].uom}</td>
                <td>$${result[part].price}</td>
                <td>$${result[part].sub_total}</td>
                <td><a href=${result[part].supplier_website} class="link-primary">${result[part].supplier_name} <i class="bi bi-box-arrow-in-up-right"></i></a></td>
                <td>
                  <button type="button" data-bs-toggle="modal" data-bs-target="#edit-parts" class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></button>
                  <button type="button" class="btn btn-outline-secondary"><i class="bi bi-trash-fill"></i></button>
                </td>
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

