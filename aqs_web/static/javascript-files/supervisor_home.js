function start() {
    getSalesperson();
    getSalespersonTotalQuotes();
    getQuotesThatRequireAttention();
}

function getSalesperson() {
    var supervisor_id = "1";
    $(async () => {
        // Change serviceURL to your own
        var getSalesperson = "http://localhost:5000/salesperson/" + supervisor_id;
        document.getElementById("salesperson").innerHTML = "";
        try {
            const response =
                await fetch(
                    getSalesperson, {
                        method: 'GET'
                    }
                );
            const result = await response.json();
            if (response.status === 200) {
                // success case
                console.log(result)
                for (var salesperson in result) {
                    document.getElementById("salesperson").innerHTML += `<tr>
                  <th scope="row"><img src="https://c.tenor.com/9qZhM0uswAYAAAAd/bully-maguire-dance.gif" width="30"
                    height="30" class="rounded-circle"></th>
                  <td class="fw-bold text-primary"><a href="#"><u>${result[salesperson].first_name} ${result[salesperson].last_name}</u></a></td>
                  <td>${result[salesperson].staff_email}</td>
                  <td class="fw-bold text-danger text-center"><a href="#"><u>${result[salesperson].rejected}</u></a></td>
                  <td class="fw-bold text-primary text-center"><a href="#"><u>${result[salesperson].sent}</u></a></td>
                  <td class="fw-bold text-success text-center"><a href="#"><u>${result[salesperson].approved}</u></a></td>
                </tr>`
                }
            } else if (response.status == 404) {
                // No Rows
                document.getElementById("salesperson").innerHTML += `<tr>
                  <th scope="row" class="fw-bold">Nothing to see here...</th>
                </tr>`
                console.log(result.message);
            } else {
                // unexpected outcome, throw the error
                document.getElementById("salesperson").innerHTML += `<tr>
                  <th scope="row" class="fw-bold">Nothing to see here...</th>
                </tr>`
                throw response.status;
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
        } // error
    });
}

function getSalespersonTotalQuotes() {
    var supervisor_id = "1";
    $(async () => {
        // Change serviceURL to your own
        var getSalespersonTotalQuotes = "http://localhost:5000/supervisorQuotationNumbers/" + supervisor_id;
        document.getElementById("approved").innerHTML = "";
        document.getElementById("draft").innerHTML = "";
        document.getElementById("sent").innerHTML = "";
        document.getElementById("rejected").innerHTML = "";
        try {
            const response =
                await fetch(
                    getSalespersonTotalQuotes, {
                        method: 'GET'
                    }
                );
            const result = await response.json();
            if (response.status === 200) {
                // success case
                console.log(result)
                for (var status in result) {
                    if (result[status].status == 'approved') {
                        document.getElementById("approved").innerHTML = result[status].num;
                        var approved = result[status].num;
                    } else if (result[status].status == 'sent') {
                        document.getElementById("sent").innerHTML = result[status].num;
                        var sent = result[status].num;
                    } else if (result[status].status == 'draft') {
                        document.getElementById("draft").innerHTML = result[status].num;
                        var draft = result[status].num;
                    } else if (result[status].status == 'rejected') {
                        document.getElementById("rejected").innerHTML = result[status].num;
                        var rejected = result[status].num
                    }
                }
                google.charts.load("current", {
                    packages: ["corechart"]
                });
                google.charts.setOnLoadCallback(drawChart);
                
                function drawChart() {
                    
                    var data = google.visualization.arrayToDataTable([
                        ['Status', 'Number'],
                        ['Pending Review', sent],
                        ['Need Amendments', rejected],
                        ['Approved', approved],
                        ['Draft', draft]
                    ]);
                
                    var options = {
                        pieHole: 0.9,
                        height: 200,
                        width: 500,
                        colors: ['blue','red','green','grey']
                    };
                
                    var chart = new google.visualization.PieChart(document.getElementById('dashboard-chart'));
                    chart.draw(data, options);
                    console.log("yoyoyo");
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

// TO DOOOO
function getQuotesThatRequireAttention() {
    var supervisor_id = "1";
    $(async () => {
        // Change serviceURL to your own
        var getQuotesThatRequireAttention = "http://localhost:5000/supervisorQuotationAttention/" + supervisor_id;
        document.getElementById("quotations-for-review").innerHTML = "";
        try {
            const response =
                await fetch(
                    getQuotesThatRequireAttention, {
                        method: 'GET'
                    }
                );
            const result = await response.json();
            if (response.status === 200) {
                // success case
                console.log(result)
                for (var quotation in result) {
                    document.getElementById("quotations-for-review").innerHTML += `
                    <div class="container rounded" style="background-color:rgb(0, 191, 255, 0.2);">
                        <span class="text-primary"><a href="supervisor_quotation_decision#${result[quotation].quotation_no}"><u>${result[quotation].quotation_no}</u></a></span><br>
                        ${result[quotation].company_name}<br>
                        ${result[quotation].rfq_date}<br>
                        Assigned to: ${result[quotation].first_name} ${result[quotation].last_name}
                    </div>
                    <br>`;
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
