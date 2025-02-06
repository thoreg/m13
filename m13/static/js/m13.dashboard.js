
$(function() {

  function update() {
    var startDate = new Date();
    startDate.setFullYear(startDate.getFullYear() - 1);
    // const fromDate = startDate.toISOString().slice(0, 10);
    // const toDate = new Date().toISOString().slice(0, 10);

    let fromDate = $( "#from" ).val();
    let toDate = $( "#to" ).val();

    if (!fromDate) {
      fromDate = '2023-01-01';
      $( "#from" ).val(fromDate)
    }

    if (!toDate) {
      toDate = new Date().toISOString().slice(0, 10)
      $( "#to" ).val(toDate);
    }

    updateTop5ProfitableArticles(fromDate, toDate);
    updateTop5Categories(fromDate, toDate)
    updateTopSales(fromDate, toDate);
    updateTopReturns(fromDate, toDate);
  }

  /***************************************************************************
   *
   * TOP 13 SALES
   *
   ***************************************************************************/
  function updateTopSales (from, to) {
    let dataTop13 = [];
    let url = `/api/sales-stats/top13/sales?from=${from}&to=${to}`;

    $.getJSON(url, function( data ) {
      $.each( data.results, function( idx, value) {
        dataTop13.push(value);
      });

      // Prepare data for Chart.js
      const labels = dataTop13.map(item => item.category_name + ' - ' + item.sku);
      const shippedQuantities = dataTop13.map(item => item.shipped);

      let chartStatus = Chart.getChart("top13shipped");
      if (chartStatus != undefined) {
        chartStatus.destroy();
      }
      // Get the context of the canvas element we want to select
      const ctx = document.getElementById('top13shipped').getContext('2d');

      // Create the chart
      const top13shipped = new Chart(ctx, {
          type: 'bar',
          data: {
              labels: labels,
              datasets: [{
                  label: 'Top 13 verkaufte Artikel (nach SKU sortiert)',
                  data: shippedQuantities,
                  backgroundColor: 'rgba(75, 192, 192, 0.2)',
                  borderColor: 'rgba(75, 192, 192, 1)',
                  borderWidth: 2
              }]
          },
          options: {
              indexAxis: 'y',
              responsive: true,
              legend: {
                  display: false
              }
          }
      });
    });
  }

  /***************************************************************************
   *
   * TOP 13 RETURN
   *
   ***************************************************************************/
  function updateTopReturns (from, to) {
    let dataTop13return = [];
    let url = `/api/sales-stats/top13/return?from=${from}&to=${to}`;

    $.getJSON(url, function( data ) {
      $.each( data.results, function( idx, value) {
        dataTop13return.push(value);
      });

      // Prepare data for Chart.js
      const returnedLabels = dataTop13return.map(item => item.category_name + ' - ' + item.sku);
      const returnedQuantities = dataTop13return.map(item => item.returned);

      let chartStatus = Chart.getChart("top13returned");
      if (chartStatus != undefined) {
        chartStatus.destroy();
      }
      // Get the context of the canvas element we want to select
      const ctxReturned = document.getElementById('top13returned').getContext('2d');

      // Create the chart
      const top13returned = new Chart(ctxReturned, {
          type: 'bar',
          data: {
              labels: returnedLabels,
              datasets: [{
                  label: 'Top 13 retournierte Artikel (nach SKU sortiert)',
                  data: returnedQuantities,
                  backgroundColor: 'rgba(188, 24, 24, 0.2)',
                  borderColor: 'rgb(137, 3, 3)',
                  borderWidth: 2
              }]
          },
          options: {
              indexAxis: 'y',
              responsive: true,
              legend: {
                  display: false
              }
          }
      });
    });
  }

  /***************************************************************************
   *
   * TOP 5 profitable articles
   *
   ***************************************************************************/
  function updateTop5ProfitableArticles(fromDate, toDate) {
    const marketplace = 'zalando';
    let url3 = `/api/v2/core/return-shipments-stats/?marketplace=${marketplace}`
    url3 += `&start=${fromDate}&end=${toDate}`;

    let resultTop5profit = []

    $.getJSON(url3, function( data ) {
      $.each( data, function(category, articles) {
        $.each( articles.content, function(idx, article) {
          resultTop5profit.push([article.article_number, article.total_diff])
        });
      });

      // Sort the array based on the numeric value of the second element
      const sortedData = resultTop5profit.sort((a, b) => {
        // Convert string numbers to actual numbers for comparison
        // ascending
        // return parseFloat(a[1]) - parseFloat(b[1]);
        // descending
        return parseFloat(b[1]) - parseFloat(a[1]);
      })
      const top5profit = sortedData.slice(0, 5);

      // Prepare data for Chart.js
      const top5profitSkus = top5profit.map(item => item[0]);
      const top5profitValues = top5profit.map(item => item[1]);

      let chartStatus = Chart.getChart("top5profitBySku");
      if (chartStatus != undefined) {
        chartStatus.destroy();
      }
      // Get the context of the canvas element we want to select
      const ctxTop5profit = document.getElementById('top5profitBySku').getContext('2d');

      // Create the chart
      const top5profitChart = new Chart(ctxTop5profit, {
          type: 'bar',
          data: {
              labels: top5profitSkus,
              datasets: [{
                  label: 'Top 5 Artikel mit dem meisten Gewinn (nach SKU sortiert)',
                  data: top5profitValues,
                  backgroundColor: 'rgba(75, 192, 192, 0.2)',
                  borderColor: 'rgba(75, 192, 192, 1)',
                  borderWidth: 2
              }]
          },
          options: {
              responsive: true,
              legend: {
                  display: false
              }
          }
      });
    });
  }

  /********************************************************************
   *
   * Top 5 favourite categories based on sold items
   *
   ********************************************************************/
  function updateTop5Categories(fromDate, toDate) {
    const marketplace = 'zalando';
    let url4 = `/api/v2/core/return-shipments-stats/?marketplace=${marketplace}`
    url4 += `&start=${fromDate}&end=${toDate}`;

    let resultAllCategories = {};
    $.getJSON(url4, function( data ) {
      $.each(data, function(category, articles) {
        let shippedByCategory = 0;
        $.each(articles.content, function(idx, article) {
          shippedByCategory += article.shipped;
        });
        resultAllCategories[category] = shippedByCategory;

      });

      // Convert object to array of [key, value] pairs, then sort by value in descending order
      let sortedItems = Object.entries(resultAllCategories).sort((a, b) => b[1] - a[1]);

      // Slice the array to get top 5 items
      let top5Items = sortedItems.slice(0, 5);

      // Prepare data for Chart.js
      const top5categories = top5Items.map(item => item[0]);
      const top5categoriesValues = top5Items.map(item => item[1]);

      let chartStatus = Chart.getChart("top5category");
      if (chartStatus != undefined) {
        chartStatus.destroy();
      }
      // Get the context of the canvas element we want to select
      const ctxTop5categoriesValues = document.getElementById('top5category').getContext('2d');

      // Create the chart
      const top5categoryChart = new Chart(ctxTop5categoriesValues, {
          type: 'doughnut',
          data: {
              labels: top5categories,
              datasets: [{
                  label: 'Top 5 beliebteste Kategorien (nach verkauften Einheiten pro Kategorie)',
                  data: top5categoriesValues,
                  borderWidth: 2,
                  backgroundColor: ["#f1c40f", "#f39c12", "#d35400", "#27ae60", "#3498db"],
              }]
          },
          options: {
              responsive: true,
              legend: {
                  display: false
              }
          }
      });
    });
  }

  /********************************************************************
  *
  * DateRange
  *
  ********************************************************************/
  var dateFormat = "yy-mm-dd",
  from = $( "#from" )
    .datepicker({
      changeMonth: true,
      changeYear: true,
      dateFormat: "yy-mm-dd",
      defaultDate: "+1w",
      changeMonth: true,
      numberOfMonths: 3
    })
    .on( "change", function() {
      to.datepicker( "option", "minDate", getDate( this ) );
    }),
  to = $( "#to" ).datepicker({
    changeMonth: true,
    changeYear: true,
    dateFormat: "yy-mm-dd",
    defaultDate: "+1w",
    changeMonth: true,
    numberOfMonths: 3
  })
  .on( "change", function() {
    from.datepicker( "option", "maxDate", getDate( this ) );
  });

  function getDate( element ) {
    var date;
    try {
      date = $.datepicker.parseDate( dateFormat, element.value );
    } catch( error ) {
      date = null;
      console.log("error :(");
      console.log(error);
    }
    return date;
  }

  // let marketplace = $("input[name='marketplace']:checked").val();
  // if (!marketplace) {
  //   marketplace = 'zalando';
  // }

  update();

  $( "#updateButton" ).on( "click", function() {
    update();
  });

});
