<template>
  <h1>{{ msg }}</h1>
  <table>
    <thead>
      <th>Artikel</th>
      <th>Herstellungskosten</th>
      <th>VK (Zalando)</th>
      <th>Retourenkosten</th>
      <th>Versandkosten</th>
      <th>8% Provision</th>
      <th>19% MwSt.</th>
      <th>Gemeinkosten</th>
      <th>Gewinn nach Steuern</th>
      <th>verkaufte Stückzahl</th>
    </thead>
    <tr v-for="product in products" v-bind:key="product">
      <td>{{ product.sku }}</td>
      <td>{{ product.costs_production }}</td>
      <td>{{ product.vk_zalando }}</td>
      <td>{{ product.return_costs }}</td>
      <td>{{ product.shipping_costs }}</td>
      <td>{{ product.eight_percent_provision }}</td>
      <td>{{ product.nineteen_percent_vat }}</td>
      <td>{{ product.generic_costs }}</td>
      <td>{{ product.profit_after_taxes }}</td>
      <td>{{ articleStats(product.sku).shipped }}</td>
    </tr>
  </table>

</template>

<script>
export default {
  name: 'ZalandoCalculator',
  props: {
    msg: String
  },
  data() {
    return {
      products: [],
      articleStats: {}
    }
  },
  created () {
    fetch('http://127.0.0.1:8000/api/zalando/finance/article-stats/')
    .then(response => response.json())
    .then(json => {
      // Map all entries in the list into an object
      // this.articleStats = json // normal array with all the values
      // Object but faulty
      // this.articleStats = Object.fromEntries(json.map(e => Object.values(e)))
      this.articleStats = json.reduce((accumulator, currentValue) => {
        accumulator[currentValue.article_number] = currentValue;
        return accumulator;
      }, {})
      fetch('http://127.0.0.1:8000/api/zalando/finance/products/')
      .then(response => response.json())
      .then(json => {
        this.products = json.results;

        for (var i = 0; i < this.products.length; i++) {
          if (this.products[i].sku in this.articleStats) {
            const sku = this.products[i].sku;
            console.log(`found sku ${sku}`);
            this.products[i].canceled = this.articleStats[sku].canceled;
            this.products[i].returned = this.articleStats[sku].returned;
            this.products[i].shipped = this.articleStats[sku].shipped;
          }
        }
      })
    })

  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
