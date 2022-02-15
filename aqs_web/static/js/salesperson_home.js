function start(){
    document.getElementById("quotations").innerHTML = ``
    get_quotations();
}

function get_quotations() {
  $(async() => {           
  // Change serviceURL to your own
  var serviceURL = "http://localhost:5000/quotations";
  
  try {
      const response =
      await fetch(
      serviceURL, { method: 'GET' }
      );
      const result = await response.json();
      if (response.status === 200) {
          // success case
          for (var quotation in result) {
              if (result[quotation].first_name + " " + result[quotation].last_name == document.getElementById("username").innerHTML) {
                var button = `<td><button type="button" class="btn btn-warning btn-sm">Pending</button></td>`;
                if (result[quotation].status == 'sent'){
                    button = `<td><button type="button" class="btn btn-success btn-sm">Sent</button></td>`
                }
                if (result[quotation].status == 'requires_editing') {
                    button = `<td><button type="button" class="btn btn-danger btn-sm">Requires Editing</button></td>`
                }
                document.getElementById("quotations").innerHTML +=
                `<tr>
                    <th scope="row"><input type="checkbox"></th>
                    <td><a href="edit#${result[quotation].quotation_no}" class="link-primary">${result[quotation].quotation_no} <i class="bi bi-box-arrow-in-up-right"></i></a></td>
                    <td>${result[quotation].company}</td>
                    <td>${result[quotation].rfq_date}</td>
                    ${button}
                    <td>
                        <button type="button" class="btn btn-outline-secondary"><i class="bi bi-trash-fill"></i></button>
                    </td>
                </tr>`
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

function insert(){
    $(async() => {           
    // Change serviceURL to your own
    var account_id = localStorage.getItem("account_id");

    var serviceURL = "http://localhost:5000/insert";
    var today = new Date();
    const data = {
        //key(database):
        quotation_id: "69",
        customer_email: "darkdrium_1994@hotmail.com",
        assigned_staff_email: "darrenho.2019@scis.smu.edu.sg",
        rfq_date: today,
        status: "pending"
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
            alert("An enrollment request under this course has already been created.")
            }
            else {
                alert("An enrollment request for this class has been successfully created!")
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