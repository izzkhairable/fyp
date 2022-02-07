function start() {
    getTopSalesperson();
    getSalespersonTotalQuotes();
    getWinLoss();
    document.addEventListener('DOMContentLoaded', dashboardData('month'));
}

function getSalespersonTotalQuotes() {
    var supervisor_id = "1";
    $(async () => {
        // Change serviceURL to your own
        var getSalespersonTotalQuotes = "http://localhost:5000/supervisorQuotationNumbers/" + supervisor_id;
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
                  <td class="fw-bold text-primary"><a href="salesperson_profile#id=${result[salesperson].id}"><u>${result[salesperson].first_name} ${result[salesperson].last_name}</u></a></td>
                  <td class="fw-bold text-success text-center"><a href="supervisor_view_quotes#salesperson=${result[salesperson].first_name} ${result[salesperson].last_name}&status=Win"><u>${result[salesperson].win_no}</u></a></td>
                  <td class="fw-bold text-danger text-center"><a href="supervisor_view_quotes#salesperson=${result[salesperson].first_name} ${result[salesperson].last_name}&status=Loss"><u>${result[salesperson].loss_no}</u></a></td>
                  <td id="${result[salesperson].id}-profit" class="fw-bold text-center"></td>
                </tr>`
                    var profit = result[salesperson].earned - result[salesperson].lost;
                    if (profit < 0) {
                        document.getElementById(`${result[salesperson].id}-profit`).className += " text-danger";
                        document.getElementById(`${result[salesperson].id}-profit`).innerHTML = "-$" + Math.abs(profit);
                    } else {
                        document.getElementById(`${result[salesperson].id}-profit`).className += " text-success";
                        document.getElementById(`${result[salesperson].id}-profit`).innerHTML = "$" + profit;
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

function getWinLoss() {
    var supervisor_id = "1";
    $(async () => {
        // Change serviceURL to your own
        var getWinLoss = "http://localhost:5000/supervisorWinLossAmount/" + supervisor_id;
        try {
            const response =
                await fetch(
                    getWinLoss, {
                        method: 'GET'
                    }
                );
            const result = await response.json();
            if (response.status === 200) {
                // success case
                for (var month in result) {
                    if (result[month].status == 'win') {
                        document.getElementById("job-win").innerHTML = "$" + result[month].total;
                    } else {
                        document.getElementById("job-loss").innerHTML = "$" + result[month].total;
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

function dashboardData(filter) {
    var return_dict = {};
    var supervisor_id = "1";
    $(async () => {
        // Change serviceURL to your own
        var getDashboardData = "http://localhost:5000/supervisorDashboard/" + supervisor_id;
        try {
            const response =
                await fetch(
                    getDashboardData, {
                        method: 'GET'
                    }
                );
            const result = await response.json();
            if (response.status === 200) {
                // success case
                if (filter == "month") {
                    // do for the last 6 months only
                    start_month = result[0].rfq_month;
                    year = result[0].rfq_year;
                    end_month = start_month - 6;
                    for (i = end_month; i < start_month; i++) {
                        if (i < 0) {
                            return_dict[(year - 1) + "-" + (i + 13)] = {
                                profit: 0,
                                job_wins: 0,
                                job_loss: 0,
                                no_of_quotations: 0,
                                quotations_done_on_time: 0
                            }
                        } else {
                            return_dict[(year) + "-" + (i + 1)] = {
                                profit: 0,
                                job_wins: 0,
                                job_loss: 0,
                                no_of_quotations: 0,
                                quotations_done_on_time: 0
                            }
                        }
                    }
                } else {
                    // do for the past 6 years only
                    start_year = result[0].rfq_year;
                    end_year = start_year - 6;
                    for (i = start_year; i > end_year; i--) {
                        return_dict[i] = {
                            profit: 0,
                            job_wins: 0,
                            job_loss: 0,
                            no_of_quotations: 0,
                            quotations_done_on_time: 0
                        }
                    }
                }
                for (var row in result) {
                    if (filter == "month") {
                        // for month
                        filter_month = result[row].rfq_year + "-" + result[row].rfq_month;
                        if (filter_month in return_dict) {
                            if (result[row].status == "win") {
                                return_dict[filter_month]['profit'] += result[row].revenue;
                                return_dict[filter_month]['job_wins'] += result[row].no_of_quotations;
                                return_dict[filter_month]['no_of_quotations'] += result[row].no_of_quotations;
                                return_dict[filter_month]['quotations_done_on_time'] += result[row].on_time;
                            } else {
                                return_dict[filter_month]['profit'] -= result[row].revenue;
                                return_dict[filter_month]['job_loss'] += result[row].no_of_quotations;
                                return_dict[filter_month]['no_of_quotations'] += result[row].no_of_quotations;
                            }
                        }
                    } else {
                        // for year
                        filter_year = result[row].rfq_year;
                        if (filter_year in return_dict) {
                            if (result[row].status == "win") {
                                return_dict[filter_year]['profit'] += result[row].revenue;
                                return_dict[filter_year]['job_wins'] += result[row].no_of_quotations;
                                return_dict[filter_year]['no_of_quotations'] += result[row].no_of_quotations;
                                return_dict[filter_year]['quotations_done_on_time'] += result[row].on_time;
                            } else {
                                return_dict[filter_year]['profit'] -= result[row].revenue;
                                return_dict[filter_year]['job_loss'] += result[row].no_of_quotations;
                                return_dict[filter_year]['no_of_quotations'] += result[row].no_of_quotations;
                            }
                        }
                    }
                }
                generateGraphs(return_dict);
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

function generateGraphs(data) {
    results = data;
    date_range = [];
    profit = [];
    no_of_quotations = [];
    job_loss = [];
    job_wins = [];
    quotations_done_on_time = [];
    late_quotations = [];
    for (key in results) {
        date_range.push(key);
        profit.push([key, results[key]['profit']]);
        no_of_quotations.push(key, results[key]['no_of_quotations']);
        job_loss.push(results[key]['job_loss']);
        job_wins.push(results[key]['job_wins']);
        quotations_done_on_time.push(results[key]['quotations_done_on_time']);
        late_quotations.push(results[key]['job_wins'] - results[key]['quotations_done_on_time']);
    }

    console.log(data)

    // top chart
    Highcharts.chart('job-profit-chart', {
        title: {
            text: ""
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

        xAxis: {
            type: 'category'
        },

        series: [{
            name: 'Profit',
            data: profit,
            color: 'green',
            negativeColor: 'red'
        }]
    });

    // words for the bottom graphs
    filterText = "Showing the past 6 years";
    filterCondition = document.getElementById("date-filter-value").textContent;
    if (filterCondition == "Monthly") {
        filterText = "Showing the past 6 months";
    }

    // for overall win rate
    win_sum = job_wins.reduce(function (a, b) {
        return a + b;
    }, 0);
    loss_sum = job_loss.reduce(function (a, b) {
        return a + b;
    }, 0);


    win_rate = win_sum / (loss_sum + win_sum) * 100;
    document.getElementById('win-rate').innerHTML = win_rate.toFixed(2);

    // bottom left chart
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
            text: filterText
        },

        credits: {
            enabled: false
        },

        colors: ['red', 'green'],

        legend: {
            align: 'right',
            x: -30,
            verticalAlign: 'top',
            y: -10,
            floating: true,
            backgroundColor: Highcharts.defaultOptions.legend.backgroundColor || 'white',
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
            title: {
                text: ''
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
            categories: date_range
        },

        series: [{
            name: 'Loss',
            data: job_loss
        }, {
            name: 'Win',
            data: job_wins
        }]
    });

    // calculate late

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
            text: filterText
        },

        credits: {
            enabled: false
        },

        colors: ['green', 'red'],

        // things that might change due to dynamic output
        xAxis: {
            categories: date_range
        },

        yAxis: {
            title: {
                text: ''
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
            data: quotations_done_on_time

        }, {
            name: 'Late',
            data: late_quotations
        }]
    });
}