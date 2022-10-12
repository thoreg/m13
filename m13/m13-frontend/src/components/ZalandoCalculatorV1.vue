<template>
  <div>
  <section class="overview">
    <div class="header" v-bind:style="{ 'background-color': statusColor(getAbsoluteDiff) }">
      _absolute_diff: {{ getAbsoluteDiff }}
    </div>
  </section>
  <section>
    <article class="category closed" v-for="(value, category) in products" :key="category">
      <div class="category-header" @click="toggleCategory($event)">
        <table class="category-overview">
          <tr>
            <td class="column-l">{{ value.name }}</td>
            <td class="column-l">Verkauf Stk: {{ value.stats.shipped }}</td>
            <td class="column-l">Retoure Stk: {{ value.stats.returned }}</td>
            <td class="column-xxl">Gewinn (Verkäufe): {{ value.stats.total_revenue }}</td>
            <td class="column-xxl">Verlust (Retouren): {{ value.stats.total_return_costs }}</td>
            <td class="column-l" v-bind:style="{ 'background-color': statusColor(value.stats.total_diff) }">
              Differenz: {{ value.stats.total_diff }}
            </td>
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
            <th>Verkauf Stk</th>
            <th>Retoure Stk</th>
            <th>Gewinn (Verkäufe)</th>
            <th>Verlust (Retouren)</th>
            <th>Differenz</th>
          </thead>
          <tr v-for="article in value.content" v-bind:key="article">
            <td>{{ article.article_number }}</td>
            <td>{{ article.category }}</td>
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
            <td v-bind:style="{ 'background-color': statusColor(article.total_diff) }">{{ article.total_diff }}</td>
          </tr>
        </table>
      </div>
    </article>
  </section>
</div>
</template>

<script>
export default {
  name: 'ZalandoCalculatorV1',
  props: {
    msg: String,
    fromDate: String,
  },
  watch: {
    fromDate: {
      immediate: true,
      handler(val, oldVal) {
        console.log(`fromDate changed: ${oldVal} -> ${val}`);
        console.log(`FROM: ${this.fromDate}`);
        this.fetchAllProducts();
      },
    },
  },
  data() {
    return {
      products: {},
      absolute: {
        diff: 0
      }
    }
  },
  methods: {
      statusColor(value) {
        if (value < 0) {
          return 'red'
        }
      },
      fetchAllProducts() {
        const baseUrl = '/api/v1/zalando/finance/products';
        let url = '';
        if (this.fromDate) {
          url = `${baseUrl}/?start=${this.fromDate}`;
        } else {
          url = `${baseUrl}`
        }
        console.log(`fetching url ${url} ...`);
        fetch(url)
        .then(response => {
          return response.json()
        })
        .then(data => {
          this.products = data;
          // Sort the skus within the category
          for(const idx in this.products) {
            const product = this.products[idx];
            product.content.sort((a, b) => {
              var keyA = a.article_number, keyB = b.article_number;
              if (keyA < keyB) {
                return -1;
              }
              if (keyA > keyB) {
                return 1;
              }
              return 0;
            });
          }
          // Sort the categories by name
          this.products = Object.keys(this.products)
            .sort()
            .reduce((accumulator, key) => {
              accumulator[key] = this.products[key];
              return accumulator;
            }, {});
        })
        .catch(error => {
          console.log(error)
        })
      },
      toggleCategory(event) {
        // Find the surrounding article and toggle 'closed' class
        // Everything is closed on initial page load
        function findUpTag(el, tag) {
          while (el.parentNode) {
          el = el.parentNode;
          if (el.tagName === tag)
            return el;
          }
          return null;
        }
        let product = findUpTag(event.target, "ARTICLE");
        if (product) {
          const isClosed = product.classList.contains('closed');
          if(!isClosed) {
            product.classList.add('closed');
          } else {
            product.classList.remove('closed');
          }
        }
      },
  },
  // We can not reference 'data' within (itself) data section -> data which is based on data belongs
  // to the 'computed' section (no self reference with 'this' within data() section)
  computed: {
      getAbsoluteDiff() {
        let absoluteDiff = 0;
        for (const product in this.products) {
          absoluteDiff += parseFloat(this.products[product].stats.total_diff);
        }
        absoluteDiff = Math.round((absoluteDiff + Number.EPSILON) * 1000) / 1000;
        return absoluteDiff;
      }
  },
  // The steps in Vue lifecycle are:
  // - beforeCreate, created,
  // - beforeMount, mounted,
  // - beforeUpdate, updated,
  // - beforeDestroy, destroyed.
  created() {
    // In Server Side Rendering created() is used over mounted() because mounted() is not present in it.
    // console.log('V1 component created');
  },
  mounted() {
    // the mounted hook can be used to run code after the component has finished the initial
    // rendering and created the DOM nodes
    // console.log('V1 component mounted');
    this.fetchAllProducts();
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
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
.closed .category-body {
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
.overview .header {
  text-align: right;
  padding: 2em;
  font-weight: bold;
}
</style>
