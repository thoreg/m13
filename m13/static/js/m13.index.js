const ctxOttoNumberOfOrderItems = document.getElementById('ottoNumberOfOrderItemsChart');
const ctxOttoRevenue = document.getElementById('ottoRevenueChart');

const ctxZNumberOfOrderItems = document.getElementById('zNumberOfOrderItemsChart');
const ctxZRevenue = document.getElementById('zRevenueChart');

const ctxEtsyNumberOfOrderItems = document.getElementById('etsyNumberOfOrderItemsChart');
const ctxEtsyRevenue = document.getElementById('etsyRevenueChart');

$(function() {
  $.get('/otto/stats/orderitems', function( data ) {

    const datesOfSent = data.reduce(function(filtered, entry) {
    if (entry.status === 'SENT') {
      filtered.push(entry.month.slice(0, 7));
    }
    return filtered;
    }, []);

    const numberOfSent = data.reduce(function(filtered, entry) {
    if (entry.status === 'SENT') {
      filtered.push(entry.count);
    }
    return filtered;
    }, []);

    const revenueOfSent = data.reduce(function(filtered, entry) {
    if (entry.status === 'SENT') {
      filtered.push(entry.revenue);
    }
    return filtered;
    }, []);

    const numberOfReturned = data.reduce(function(filtered, entry) {
    if (entry.status === 'RETURNED') {
      filtered.push(entry.count * -1);
    }
    return filtered;
    }, []);

    const revenueOfReturned = data.reduce(function(filtered, entry) {
    if (entry.status === 'RETURNED') {
      filtered.push(entry.revenue * -1);
    }
    return filtered;
    }, []);

    const ottoNumberOfOrderItems = new Chart(ctxOttoNumberOfOrderItems, {
    type: 'bar',
    data: {
      labels: datesOfSent,
      datasets: [
      {
        label: 'SENT',
        data: numberOfSent,
        backgroundColor: [
        'rgba(75, 192, 192, 0.2)',
        ],
        borderColor: [
        'rgba(75, 192, 192, 1)',
        ],
        borderWidth: 1
      },
      {
        label: 'RETURNED',
        data: numberOfReturned,
        backgroundColor: [
        'rgba(255, 99, 132, 0.2)',
        ],
        borderColor: [
        'rgba(255, 99, 132, 1)',
        ],
        borderWidth: 1
      }
      ]
    },
    options: {
      scales: {
      x: {
        stacked: true,
      },
      y: {
        beginAtZero: true,
        stacked: true,
      }
      },
      responsive: true,
      plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Number of OrderItems per Month by State'
      }
      }
    }
    });

    const ottoRevenue = new Chart(ctxOttoRevenue, {
    type: 'bar',
    data: {
      labels: datesOfSent,
      datasets: [
      {
        label: 'SENT',
        data: revenueOfSent,
        backgroundColor: [
        'rgba(75, 192, 192, 0.2)',
        ],
        borderColor: [
        'rgba(75, 192, 192, 1)',
        ],
        borderWidth: 1
      },
      {
        label: 'RETURNED',
        data: revenueOfReturned,
        backgroundColor: [
        'rgba(255, 99, 132, 0.2)',
        ],
        borderColor: [
        'rgba(255, 99, 132, 1)',
        ],
        borderWidth: 1
      }
      ]
    },
    options: {
      scales: {
      x: {
        stacked: true,
      },
      y: {
        beginAtZero: true,
        stacked: true,
      }
      },
      responsive: true,
      plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Revenue per Month by State'
      }
      }
    }
    });
  });

  $.get('/z/stats/orderitems', function( data ) {

    const datesOfSent = data.reduce(function(filtered, entry) {
    if (entry.status === 'fulfilled') {
      filtered.push(entry.month.slice(0, 7));
    }
    return filtered;
    }, []);

    const numberOfSent = data.reduce(function(filtered, entry) {
    if (entry.status === 'fulfilled') {
      filtered.push(entry.count);
    }
    return filtered;
    }, []);

    const revenueOfSent = data.reduce(function(filtered, entry) {
    if (entry.status === 'fulfilled') {
      filtered.push(entry.revenue);
    }
    return filtered;
    }, []);

    const numberOfReturned = data.reduce(function(filtered, entry) {
    if (entry.status === 'returned') {
      filtered.push(entry.count * -1);
    }
    return filtered;
    }, []);

    const revenueOfReturned = data.reduce(function(filtered, entry) {
    if (entry.status === 'returned') {
      filtered.push(entry.revenue * -1);
    }
    return filtered;
    }, []);

    const zNumberOfOrderItems = new Chart(ctxZNumberOfOrderItems, {
    type: 'bar',
    data: {
      labels: datesOfSent,
      datasets: [
      {
        label: 'fulfilled',
        data: numberOfSent,
        backgroundColor: [
        'rgba(75, 192, 192, 0.2)',
        ],
        borderColor: [
        'rgba(75, 192, 192, 1)',
        ],
        borderWidth: 1
      },
      {
        label: 'returned',
        data: numberOfReturned,
        backgroundColor: [
        'rgba(255, 99, 132, 0.2)',
        ],
        borderColor: [
        'rgba(255, 99, 132, 1)',
        ],
        borderWidth: 1
      }
      ]
    },
    options: {
      scales: {
      x: {
        stacked: true,
      },
      y: {
        beginAtZero: true,
        stacked: true,
      }
      },
      responsive: true,
      plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Number of OrderItems per Month by State'
      }
      }
    }
    });

    const zRevenue = new Chart(ctxZRevenue, {
    type: 'bar',
    data: {
      labels: datesOfSent,
      datasets: [
      {
        label: 'fulfilled',
        data: revenueOfSent,
        backgroundColor: [
        'rgba(75, 192, 192, 0.2)',
        ],
        borderColor: [
        'rgba(75, 192, 192, 1)',
        ],
        borderWidth: 1
      },
      {
        label: 'returned',
        data: revenueOfReturned,
        backgroundColor: [
        'rgba(255, 99, 132, 0.2)',
        ],
        borderColor: [
        'rgba(255, 99, 132, 1)',
        ],
        borderWidth: 1
      }
      ]
    },
    options: {
      scales: {
      x: {
        stacked: true,
      },
      y: {
        beginAtZero: true,
        stacked: true,
      }
      },
      responsive: true,
      plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Revenue per Month by State'
      }
      }
    }
    });
  });

  $.get('/etsy/stats/orderitems', function( data ) {

    const datesOfSent = data.reduce(function(filtered, entry) {
    if (entry.status === 'COMPLETED') {
      filtered.push(entry.month.slice(0, 7));
    }
    return filtered;
    }, []);

    const numberOfSent = data.reduce(function(filtered, entry) {
    if (entry.status === 'COMPLETED') {
      filtered.push(entry.count);
    }
    return filtered;
    }, []);

    const revenueOfSent = data.reduce(function(filtered, entry) {
    if (entry.status === 'COMPLETED') {
      filtered.push(entry.revenue);
    }
    return filtered;
    }, []);

    const etsyNumberOfOrderItems = new Chart(ctxEtsyNumberOfOrderItems, {
    type: 'bar',
    data: {
      labels: datesOfSent,
      datasets: [
      {
        label: 'COMPLETED',
        data: numberOfSent,
        backgroundColor: [
        'rgba(75, 192, 192, 0.2)',
        ],
        borderColor: [
        'rgba(75, 192, 192, 1)',
        ],
        borderWidth: 1
      }
      ]
    },
    options: {
      scales: {
      x: {
        stacked: true,
      },
      y: {
        beginAtZero: true,
        stacked: true,
      }
      },
      responsive: true,
      plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Number of OrderItems per Month by State'
      }
      }
    }
    });

    const etsyRevenue = new Chart(ctxEtsyRevenue, {
    type: 'bar',
    data: {
      labels: datesOfSent,
      datasets: [
      {
        label: 'COMPLETED',
        data: revenueOfSent,
        backgroundColor: [
        'rgba(75, 192, 192, 0.2)',
        ],
        borderColor: [
        'rgba(75, 192, 192, 1)',
        ],
        borderWidth: 1
      }
      ]
    },
    options: {
      scales: {
      x: {
        stacked: true,
      },
      y: {
        beginAtZero: true,
        stacked: true,
      }
      },
      responsive: true,
      plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Revenue per Month by State'
      }
      }
    }
    });
  });
});
