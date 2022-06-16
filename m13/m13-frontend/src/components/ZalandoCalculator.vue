<template>
  <h1>{{ msg }}</h1>
  <section>
    <article class="category" :class="categoryClasses" v-for="category in categories" v-bind:key="category">
      <div class="category-header" @click="toggleCategory">
        <table class="category-overview">
          <tr>
            <td class="column-l">{{ category.name }}</td>
            <td class="column-l">Verkauf Stk: {{ category.stats.shipped }}</td>
            <td class="column-l">Retoure Stk: {{ category.stats.returned }}</td>
            <td class="column-xxl">Gewinn (Verkäufe): {{ category.stats.total_revenue }}</td>
            <td class="column-xxl">Verlust (Retouren): {{ category.stats.total_return_costs }}</td>
            <td class="column-l">Differenz: {{ category.stats.total_diff }}</td>
          </tr>
        </table>
      </div>
      <div class="category-body">
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
            <th>Gewinn an Verkäufen</th>
            <th>Verlust an Retouren</th>
            <th>Differenz</th>
          </thead>
          <tr v-for="article in category.content" v-bind:key="article">
            <td>{{ article.article }}</td>
            <td>{{ article.category_name }}</td>
            <td>{{ article.costs_production }}</td>
            <td>{{ article.vk_zalando }}</td>
            <td>{{ article.return_costs }}</td>
            <td>{{ article.shipping_costs }}</td>
            <td>{{ article.eight_percent_provision }}</td>
            <td>{{ article.nineteen_percent_vat }}</td>
            <td>{{ article.generic_costs }}</td>
            <td>{{ article.profit_after_taxes }}</td>
            <td>{{ article.shipped }}</td>
            <td>{{ article.returned }}</td>
            <td>{{ article.total_revenue }}</td>
            <td>{{ article.total_return_costs }}</td>
            <td>{{ article.total_diff }}</td>
          </tr>
        </table>
      </div>
    </article>
  </section>
  <hr style="margin: 5em 0;">
  <h2>_original_table</h2>
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
      <th>Gewinn an Verkäufen</th>
      <th>Verlust an Retouren</th>
      <th>Differenz</th>
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
      <td>{{ product.total_revenue }}</td>
      <td>{{ product.total_return_costs }}</td>
      <td>{{ product.total_diff }}</td>
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
      currentPage: 1,
      categories: {},
      isOpen: true,
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
            for(let i=0; i < data.results.length; i++) {
              const entry = data.results[i];
              console.log(entry);
              if (entry.category_name != 'N/A') {
                if (entry.category_name in this.categories) {
                  this.categories[entry.category_name].content.push(entry)
                } else {
                  this.categories[entry.category_name] = {
                    name: entry.category_name,
                    stats: {
                      shipped: 0,
                      returned: 0,
                      canceled: 0,
                      total_revenue: 0,
                      total_return_costs: 0,
                      total_diff: 0,
                    },
                    content: [entry]
                  }
                }
                this.categories[entry.category_name].stats.shipped += entry.shipped;
                this.categories[entry.category_name].stats.returned += entry.returned;
                this.categories[entry.category_name].stats.canceled += entry.canceled;
                this.categories[entry.category_name].stats.total_revenue += entry.total_revenue;
                // Crazy Moves to round floats in javascript
                this.categories[entry.category_name].stats.total_revenue = Math.round(
                  (this.categories[entry.category_name].stats.total_revenue + Number.EPSILON) * 1000) / 1000;
                this.categories[entry.category_name].stats.total_return_costs += entry.total_return_costs;
                this.categories[entry.category_name].stats.total_return_costs = Math.round(
                  (this.categories[entry.category_name].stats.total_return_costs + Number.EPSILON) * 1000) / 1000;
                this.categories[entry.category_name].stats.total_diff += entry.total_diff;
                this.categories[entry.category_name].stats.total_diff = Math.round(
                  (this.categories[entry.category_name].stats.total_diff + Number.EPSILON) * 1000) / 1000;
              }
            }
          })
          .catch(error => {
            console.log(error)
          })
      },
      toggleCategory() {
        this.isOpen = !this.isOpen
      }
  },
  // We can not reference 'data' within (itself) data section -> data which is based on data belongs
  // to the 'computed' section (no self reference with 'this' within data() section)
  computed: {
      categoryClasses() {
        return {
          'is-closed': this.isOpen
        }
      }
  },
  // The steps in Vue lifecycle are:
  // - beforeCreate, created,
  // - beforeMount, mounted,
  // - beforeUpdate, updated,
  // - beforeDestroy, destroyed.
  created() {
    // In Server Side Rendering created() is used over mounted() because mounted() is not present in it.
    // console.log('App component created');
  },
  mounted() {
    // the mounted hook can be used to run code after the component has finished the initial
    // rendering and created the DOM nodes
    // console.log('App component mounted');
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

.category-header {
  text-align: left;
  font-weight: bold;
  font-size: 1.3em;
  cursor: pointer;
}

.category-body {
  padding: 0;
  max-height: 100em;
  overflow: hidden;
  transition: 0.3s ease all;
}
.is-closed .category-body {
  max-height: 0;
}

.column-s {
  min-width: 12em;
}
.column-m {
  min-width: 10em;
}
.column-l {
  min-width: 12em;
}
.column-xl {
  min-width: 14em;
}
.column-xxl {
  min-width: 18em;
}
</style>
