function saveChanges(){
  location.href = "home.html";
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
            console.log(result[1]["Concats"].split(','))
            for (var part in result) {
              document.getElementById("parts").innerHTML += `<tr>
                <th scope="row"><input type="checkbox"></th>
                <td>${result[part].component_no}</td>
                <td>${result[part].uom}</td>
                <td>${result[part].description}</td>
                <td>${result[part].quantity}</td>
                <td>$${result[part].total_price}</td>
                <td>${result[part].is_drawing}</td>
                <td>${result[part].drawing_no}</td>
                <td>${result[part].set_no}</td>
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

