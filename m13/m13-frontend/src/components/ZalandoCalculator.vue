<template>
  <h1>{{ msg }}</h1>
  <table>
    <thead>
      <th>Artikel</th>
      <th>Kategorie</th>
      <th>Herstellungskosten</th>
      <th>VK (Zalando)</th>
      <th>Retourenkosten</th>
      <th>Versandkosten</th>
      <th>8% Provision</th>
      <th>19% MwSt.</th>
      <th>Gemeinkosten</th>
      <th>Gewinn nach Steuern</th>
      <th>Stückzahl Verkauf</th>
      <th>Stückzahl Retoure</th>
    </thead>
    <tr v-for="product in products" v-bind:key="product">
      <td>{{ product.article }}</td>
      <td>{{ product.category_name }}</td>
      <td>{{ product.costs_production }}</td>
      <td>{{ product.vk_zalando }}</td>
      <td>{{ product.return_costs }}</td>
      <td>{{ product.shipping_costs }}</td>
      <td>{{ product.eight_percent_provision }}</td>
      <td>{{ product.nineteen_percent_vat }}</td>
      <td>{{ product.generic_costs }}</td>
      <td>{{ product.profit_after_taxes }}</td>
      <td>{{ product.shipped }}</td>
      <td>{{ product.returned }}</td>
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
      currentPage: 1
    }
  },
  methods: {
      getProducts() {
        fetch(`/api/zalando/finance/products/?page=${this.currentPage}`)
          .then(response => {
            return response.json()
          })
          .then(data => {
            console.log(data);
            this.products.push(...data.results);
          })
          .catch(error => {
            console.log(error)
          })
      },
  },
  // The steps in Vue lifecycle are:
  // - beforeCreate, created,
  // - beforeMount, mounted,
  // - beforeUpdate, updated,
  // - beforeDestroy, destroyed.
  created() {
    // In Server Side Rendering created() is used over mounted() because mounted() is not present in it.
    console.log('App component created');
  },
  mounted() {
    // the mounted hook can be used to run code after the component has finished the initial
    // rendering and created the DOM nodes
    console.log('App component mounted');
    this.getProducts();

    window.onscroll = () => {
      let bottomOfWindow = document.documentElement.scrollTop + window.innerHeight === document.documentElement.offsetHeight;
      if (bottomOfWindow) {
        this.currentPage += 1;
        this.getProducts();
      }
    }

  },
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
