function start() {
    getTopSalesperson();
    getSalespersonTotalQuotes();
    document.addEventListener('DOMContentLoaded', generateGraphs());
}

function getSalespersonTotalQuotes() {
    var supervisor_id = "1";
    $(async () => {
        // Change serviceURL to your own
        var getSalespersonTotalQuotes = "http://localhost:5000/supervisorQuotationNumbers/" + supervisor_id;
        document.getElementById("approved").innerHTML = "";
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
                    } else if (result[status].status == 'sent') {
                        document.getElementById("sent").innerHTML = result[status].num;
                    } else {
                        document.getElementById("rejected").innerHTML = result[status].num;
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

function getTopSalesperson() {
    var supervisor_id = "1";
    $(async () => {
        // Change serviceURL to your own
        var getTopSalesperson = "http://localhost:5000/supervisorTopSalesperson/" + supervisor_id;
        try {
            const response =
                await fetch(
                    getTopSalesperson, {
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
                  <td class="fw-bold text-primary"><a href="salesperson_home#id=${result[salesperson].id}"><u>${result[salesperson].first_name} ${result[salesperson].last_name}</u></a></td>
                  <td class="fw-bold text-success text-center"><a href="supervisor_view_quotes#salesperson=${result[salesperson].first_name} ${result[salesperson].last_name}&status=Win"><u>${result[salesperson].win}</u></a></td>
                  <td class="fw-bold text-danger text-center"><a href="supervisor_view_quotes#salesperson=${result[salesperson].first_name} ${result[salesperson].last_name}&status=Loss"><u>${result[salesperson].loss}</u></a></td>
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

function generateGraphs() {
    // top left chart
    Highcharts.chart('job-profit-chart', 
    {
        title: {
            text:""
        },

        credits: {
            enabled: false
        },
        

        // things that might change due to filter
        yAxis: {
            title: {
                text: ''
            },
            labels: {
                format: '${value}',
            },
            stackLabels: {
                enabled: true,
                style: {
                    fontWeight: 'bold',
                    color: ( // theme
                        Highcharts.defaultOptions.title.style &&
                        Highcharts.defaultOptions.title.style.color
                    ) || 'gray'
                }
            }
        },
        plotOptions: {
            series: {
                pointStart: 2010
            }
        },
        
        series: [{
            name: 'Profit',
            data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
        }],
        
    });

    // top right chart
    Highcharts.chart('job-win-loss-stacked-bar', {
        chart: {
            type: 'column'
        },

        title: {
            text: ''
        },

        subtitle: {
            align: 'left',
            y: 0,
            text: 'Showing the past 6 months'
        },
        
        credits: {
            enabled: false
        },

        colors: ['red','green'],

        legend: {
            align: 'right',
            x: -30,
            verticalAlign: 'top',
            y: -10,
            floating: true,
            backgroundColor:
                Highcharts.defaultOptions.legend.backgroundColor || 'white',
            borderColor: '#CCC',
            borderWidth: 1,
            shadow: false
        },

        plotOptions: {
            column: {
                stacking: 'normal',
                dataLabels: {
                    enabled: true
                }
            }
        },

        // things that might change due to dynamic output
        yAxis: {
            min: 0,
            max: 10,
            title: {
                text: ''
            },
            labels: {
                format: '{value}0 %',
            },
            stackLabels: {
                enabled: true,
                style: {
                    fontWeight: 'bold',
                    color: ( // theme
                        Highcharts.defaultOptions.title.style &&
                        Highcharts.defaultOptions.title.style.color
                    ) || 'gray'
                }
            }
        },

        xAxis: {
            categories: ['October','November', 'December', 'January', 'February', 'March']
        },

        series: [{
            name: 'Loss',
            data: [5, 3, 4, 7, 2, 1]
        }, {
            name: 'Win',
            data: [2, 2, 3, 2, 1, 10]
        }]
    });

    // bottom right
    Highcharts.chart('fulfilled-quotations-bar', {
        chart: {
            type: 'column'
        },

        title: {
            text: ''
        },

        subtitle: {
            align: 'left',
            y: 0,
            text: 'Showing the past 6 months'
        },

        credits: {
            enabled: false
        },

        colors: ['green','red'],

        // things that might change due to dynamic output
        xAxis: {
            categories: ['October','November', 'December', 'January', 'February', 'March']
        },

        yAxis: {
            min: 0,
            max: 10,
            title: {
                text: ''
            },
            labels: {
                format: '{value}0 %',
            },
            stackLabels: {
                align: 'left',
                enabled: true,
                style: {
                    fontWeight: 'bold',
                    color: ( // theme
                        Highcharts.defaultOptions.title.style &&
                        Highcharts.defaultOptions.title.style.color
                    ) || 'gray'
                }
            }
        },

        series: [{
            name: 'On Time',
            data: [49.9, 71.5, 106.4, 129.2, 144.0, 176.0]
    
        }, {
            name: 'Late',
            data: [83.6, 78.8, 98.5, 93.4, 106.0, 84.5]
        }]
    });
}
