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

  // Pre-selectors for date range
  $('#bigBangButton').on('click', function () {
    $( "#from" ).val('2021-08-01');
    $( "#to" ).val(new Date().toISOString().slice(0, 10));
    update();
  });
  $('#twelveMonthsButton').on('click', function () {
    var startDate = new Date();
    startDate.setFullYear(startDate.getFullYear() - 1);
    $( "#from" ).val(startDate.toISOString().slice(0, 10));
    $( "#to" ).val(new Date().toISOString().slice(0, 10));
    update();
  });
  $('#sixMonthsButton').on('click', function () {
    var startDate = new Date();
    startDate.setMonth(startDate.getMonth() - 6);
    $( "#from" ).val(startDate.toISOString().slice(0, 10));
    $( "#to" ).val(new Date().toISOString().slice(0, 10));
    update();
  });
  $('#threeMonthsButton').on('click', function () {
    var startDate = new Date();
    startDate.setMonth(startDate.getMonth() - 3);
    $( "#from" ).val(startDate.toISOString().slice(0, 10));
    $( "#to" ).val(new Date().toISOString().slice(0, 10));
    update();
  });
  $('#oneMonthButton').on('click', function () {
    var startDate = new Date();
    startDate.setMonth(startDate.getMonth() - 1);
    $( "#from" ).val(startDate.toISOString().slice(0, 10));
    $( "#to" ).val(new Date().toISOString().slice(0, 10));
    update();
  });
  $('#thisMonthButton').on('click', function () {
    var today = new Date();
    // Add one hour extra here to overcome stupid local timezone issue
    var startDate = new Date(today.getFullYear(), today.getMonth(), 1, 1);
    $( "#from" ).val(startDate.toISOString().slice(0, 10));
    $( "#to" ).val(new Date().toISOString().slice(0, 10));
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
                  <th class="column-xl">VK</th>
                  <th class="column-l">Retourenkosten</th>
                  <th class="column-l">Versandkosten</th>
                  <th class="column-l">Provision</th>
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
              <td class="column-xl"><span title="Original Eintrag 'production_costs' aus der DB">` + article.costs_production + `</span></td>
              <td class="column-xl"><span title="Reported Preis vom Marktplatz">` + article.vk_zalando + `</span></td>
              <td class="column-l"><span title="Wert aus der Marktplatz Configuration (DB)">` + article.return_costs + `</span></td>
              <td class="column-l"><span title="Wert aus der Marktplatz Configuration (DB)">` + article.shipping_costs + `</span></td>
              <td class="column-l"><span title="Reported vom Marktplatz pai_fee + payment_service_fee">` + article.provision + `</span></td>
              <td class="column-l"><span title="self.price * self.vat_in_percent / 100">` + article.nineteen_percent_vat + `</span></td>
              <td class="column-l"><span title="self.price * self.generic_costs_in_percent / 100">` + article.generic_costs + `</span></td>
              <td class="column-xl"><span title=" self.price
                - self.production_costs
                - self.shipping_costs
                - self.provision_amount
                - self.vat_amount
                - self.generic_costs_amount">` + article.profit_after_taxes + `</span></td>
              <td class="column-l"><span title="Anzahl Zeilen aus der DB welche 'Sale' sind(DB) => self.shipped">` + article.shipped + `</span></td>
              <td class="column-l"><span title="Anzahl Zeilen aus der DB welche nicht 'Sale' sind(DB) => self.returned">` + article.returned + `</span></td>
              <td class="column-xl"><span title="
result = self.profit_after_taxes * (self.shipped - self.returned)
if result < 0:
    return Decimal('0.00')
return result
              ">` + article.total_revenue + `</span></td>
              <td class="column-xl"><span title="
return self.returned * (
    self.shipping_costs + self.return_costs + self.generic_costs_amount
)
              ">` + article.total_return_costs + `</span></td>
              <td class="column-xl"><span title="return self.price * self.shipped">` + article.sales + `</span></td>
              <td class="diff"><span title="return self.total_revenue - self.total_return_costs">` + article.total_diff + `</span></td>
            </tr>
          `);
        });
      });

      // Calculate sums (displayed in the title)
      $.each( data, function( category, value ) {
        total_sales += parseFloat(value.stats.sales);
        total_diff += parseFloat(value.stats.total_diff);
      });

      // Click on category header toggles articles table
      $('.category-header').on('click', function () {
        $( this ).next('.category-body').toggleClass('closed');
      });

      // Highlight all negative values as BIG FAT RED
      $(".diff").colorize();
      $(".diffHeader").colorizeHeader()

      // Make article tables sortable (every column)
      $(".tablesorter").tablesorter();

      // Round total sums (listed on top of the page)
      $("#absolute_sales").text(total_sales.toFixed(2));
      $("#absolute_diff").text(total_diff.toFixed(2));
    });
  }

  update(from, to);

});
