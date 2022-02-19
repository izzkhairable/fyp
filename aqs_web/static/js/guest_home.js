function start() {
    getSalesperson();
    getSalespersonTotalQuotes();
}

function getSalesperson() {
    $(async () => {
        // Change serviceURL to your own
        var getSalesperson = "http://localhost:5000/salesperson/";
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
                for (var salesperson in result) {
                    document.getElementById("salesperson").innerHTML += `<tr>
                  <th scope="row"><img src="https://c.tenor.com/9qZhM0uswAYAAAAd/bully-maguire-dance.gif" width="30"
                    height="30" class="rounded-circle"></th>
                  <td class="fw-bold text-primary"><a href="profile#id=${result[salesperson].id}"><u>${result[salesperson].first_name} ${result[salesperson].last_name}</u></a></td>
                  <td>${result[salesperson].staff_email}</td>
                  <td class="fw-bold text-danger text-center"><a href="search#salesperson=${result[salesperson].first_name} ${result[salesperson].last_name}&status=Need Amendment"><u>${result[salesperson].rejected}</u></a></td>
                  <td class="fw-bold text-primary text-center"><a href="search#salesperson=${result[salesperson].first_name} ${result[salesperson].last_name}&status=Pending Approval"><u>${result[salesperson].sent}</u></a></td>
                  <td class="fw-bold text-success text-center"><a href="search#salesperson=${result[salesperson].first_name} ${result[salesperson].last_name}&status=Sent to Customer"><u>${result[salesperson].approved}</u></a></td>
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
    $(async () => {
        // Change serviceURL to your own
        var getSalespersonTotalQuotes = "http://localhost:5000/quotationNumbers/";
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
                var draft = 0
                for (var status in result) {
                    if (result[status].status == 'approved') {
                        document.getElementById("approved").innerHTML = result[status].num;
                        var approved = result[status].num;
                    } else if (result[status].status == 'sent') {
                        document.getElementById("sent").innerHTML = result[status].num;
                        var sent = result[status].num;;
                    } else if (result[status].status == 'rejected') {
                        document.getElementById("rejected").innerHTML = result[status].num;
                        var rejected = result[status].num;
                    } else if (result[status].status == 'draft' || result[status].status == 'scraped') {
                        draft += result[status].num;
                    }
                }
                document.getElementById("draft").innerHTML = draft;
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
                        colors: ['blue', 'red', 'green', 'grey']
                    };

                    var chart = new google.visualization.PieChart(document.getElementById('dashboard-chart'));
                    chart.draw(data, options);
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