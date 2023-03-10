$(function() {
  let fromDate = '';
  let toDate = '';

  $.fn.colorize = function () {
    return this.each(function() {
      var $this = $(this);
      var number = $this.text();
      if (number.startsWith("-")) {
        $this.addClass("minus");
      }
    });
  };

  $.fn.colorizeHeader = function () {
    return this.each(function() {
      var $this = $(this);
      var number = $this.text().replace("Differenz: ", "");
      if (number.startsWith("-")) {
        $this.addClass("minus");
      }
    });
  };

  const dateFormat = "yy-mm-dd";

  var from = $( "#from" )
    .datepicker({
      dateFormat: "yy-mm-dd",
      defaultDate: -30,
    })
    .on( "change", function() {
      to.datepicker( "option", "minDate", getDate( this ) );
      update();
    });

  var to = $( "#to" )
    .datepicker({
      dateFormat: "yy-mm-dd",
      defaultDate: null // today
    })
    .on( "change", function() {
      from.datepicker( "option", "maxDate", getDate( this ) );
      update();
    });

  function getDate( element ) {
    var date;
    try {
      date = $.datepicker.parseDate( dateFormat, element.value );
    } catch( error ) {
      date = null;
    }
    return date;
  }

  $("input[name='marketplace']").change(function () {
    console.log('marketplace changed');
    update();
  });

  function update() {
    // reset the result table
    $("#returnShipmentCalculatorOranUtanClaus").html('');
    let total_sales = 0;
    let total_diff = 0;

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

    let marketplace = $("input[name='marketplace']:checked").val();
    if (!marketplace) {
      marketplace = 'zalando';
    }

    let url = `/api/v2/core/return-shipments-stats/?marketplace=${marketplace}`
    url += `&start=${fromDate}&end=${toDate}`;
    console.log(`url: ${url}`);

    $.getJSON(url, function( data ) {
      // Build up one table per category
      $.each( data, function( category, value ) {
        $("#returnShipmentCalculatorOranUtanClaus").append(`
          <article class="category">
            <div class="category-header">
              <table class="category-overview">
                <tr>
                  <td class="column-xxl"> ` + value.name + `</td>
                  <td class="column-l">Verkauf Stk: ` + value.stats.shipped + ` </td>
                  <td class="column-l">Retoure Stk: ` + value.stats.returned + ` </td>
                  <td class="column-xxl">Gewinn (Verkäufe): ` + value.stats.total_revenue + ` </td>
                  <td class="column-xxl">Verlust (Retouren): ` + value.stats.total_return_costs + ` </td>
                  <td class="column-xxl">Umsatz: ` + value.stats.sales + ` </td>
                  <td class="column-l diffHeader">Differenz: ` + value.stats.total_diff + ` </td>
                </tr>
              </table>
            </div>
            <div class="category-body closed">
              <table class="tablesorter">
                <thead>
                  <th class="column-xl">Artikel</th>
                  <th class="column-xl">Kategorie</th>
                  <th class="column-xl">Herstellungskosten</th>
                  <th class="column-xl">VK (Zalando)</th>
                  <th class="column-l">Retourenkosten</th>
                  <th class="column-l">Versandkosten</th>
                  <th class="column-l">8% Provision</th>
                  <th class="column-l">19% MwSt.</th>
                  <th class="column-l">Gemeinkosten</th>
                  <th class="column-xl">Gewinn nach Steuern</th>
                  <th class="column-l">Verkauf Stk</th>
                  <th class="column-l">Retoure Stk</th>
                  <th class="column-xl">Gewinn (Verkäufe)</th>
                  <th class="column-xl">Verlust (Retouren)</th>
                  <th class="column-xl">Umsatz</th>
                  <th class="column-xl">Differenz</th>
                </thead>
                <tbody id=` + value.name.replace(/\s/g, "").replace(/\(/g, "").replace(/\)/g, "") + `>
                </tbody>
              </table>
            </div>
          </article>`
        )
      });

      // Fill rows (articles) into each category table
      $.each( data, function( category, value ) {
        $.each( value.content, function( k, article) {
          $("#" + article.category.replace(/\s/g, "").replace(/\(/g, "").replace(/\)/g, "")).append(`
            <tr>
              <td class="column-xl">` + article.article_number + `</td>
              <td class="column-xl">` + article.category + `</td>
              <td class="column-xl">` + article.costs_production + `</td>
              <td class="column-xl">` + article.vk_zalando + `</td>
              <td class="column-l">` + article.return_costs + `</td>
              <td class="column-l">` + article.shipping_costs + `</td>
              <td class="column-l">` + article.eight_percent_provision + `</td>
              <td class="column-l">` + article.nineteen_percent_vat + `</td>
              <td class="column-l">` + article.generic_costs + `</td>
              <td class="column-xl">` + article.profit_after_taxes + `</td>
              <td class="column-l">` + article.shipped + `</td>
              <td class="column-l">` + article.returned + `</td>
              <td class="column-xl">` + article.total_revenue + `</td>
              <td class="column-xl">` + article.total_return_costs + `</td>
              <td class="column-xl">` + article.sales + `</td>
              <td class="diff">` + article.total_diff + `</td>
            </tr>
          `);
        });
      });

      // Calculate sums (displayed in the title)
      $.each( data, function( category, value ) {
        total_sales += parseFloat(value.stats.sales);
        total_diff += parseFloat(value.stats.total_diff);
      });

      $('.category-header').on('click', function () {
        $( this ).next('.category-body').toggleClass('closed');
      });

      $(".diff").colorize();
      $(".diffHeader").colorizeHeader()
      $(".tablesorter").tablesorter();

      $("#absolute_sales").text(total_sales.toFixed(2));
      $("#absolute_diff").text(total_diff.toFixed(2));
    });
  }

  update(from, to);

});