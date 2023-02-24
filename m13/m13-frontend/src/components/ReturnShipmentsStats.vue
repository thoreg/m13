<template>
    <div>
    <section class="overview">
      <div class="header" v-bind:style="{ 'background-color': statusColor(getAbsoluteDiff) }">
        _absolute_sales: {{ getAbsoluteSales }}
        _absolute_diff: {{ getAbsoluteDiff }}
      </div>
    </section>
    <section>
      <article class="category closed" v-for="(value, category) in products" :key="category">
        <div class="category-header" @click="toggleCategory($event)">
          <table class="category-overview">
            <tr>
              <td class="column-xxl">{{ value.name }}</td>
              <td class="column-l">Verkauf Stk: {{ value.stats.shipped }}</td>
              <td class="column-l">Retoure Stk: {{ value.stats.returned }}</td>
              <td class="column-xxl">Gewinn (Verkäufe): {{ value.stats.total_revenue }}</td>
              <td class="column-xxl">Verlust (Retouren): {{ value.stats.total_return_costs }}</td>
              <td class="column-xxl">Umsatz: {{ value.stats.sales }}</td>
              <td class="column-l" v-bind:style="{ 'background-color': statusColor(value.stats.total_diff) }">
                Differenz: {{ value.stats.total_diff }}
              </td>
            </tr>
          </table>
        </div>
        <div class="category-body">
          <table>
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
            <tr v-for="article in value.content" v-bind:key="article">
              <td class="column-xl">{{ article.article_number }}</td>
              <td class="column-xl">{{ article.category }}</td>
              <td class="column-xl">{{ article.costs_production }}</td>
              <td class="column-xl">{{ article.vk_zalando }}</td>
              <td class="column-l">{{ article.return_costs }}</td>
              <td class="column-l">{{ article.shipping_costs }}</td>
              <td class="column-l">{{ article.eight_percent_provision }}</td>
              <td class="column-l">{{ article.nineteen_percent_vat }}</td>
              <td class="column-l">{{ article.generic_costs }}</td>
              <td class="column-xl">{{ article.profit_after_taxes }}</td>
              <td class="column-l">{{ article.shipped }}</td>
              <td class="column-l">{{ article.returned }}</td>
              <td class="column-xl">{{ article.total_revenue }}</td>
              <td class="column-xl">{{ article.total_return_costs }}</td>
              <td class="column-xl">{{ article.sales }}</td>
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
    name: 'ReturnShipmentsStats',
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
            const baseUrl = '/api/v2/core/return-shipments-stats/?marketplace=zalando';
            let url = '';
            if (this.fromDate) {
                url = `${baseUrl}&start=${this.fromDate}`;
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
                    if (el.tagName === tag) {
                        return el;
                    }
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
    },  // end 'methods()'
    // We can not reference 'data' within (itself) data section -> data which is based on data
    // belongs to the 'computed' section (no self reference with 'this' within data() section)
    computed: {
        getAbsoluteDiff() {
            let absoluteDiff = 0;
            for (const product in this.products) {
                absoluteDiff += parseFloat(this.products[product].stats.total_diff);
            }
            absoluteDiff = Math.round((absoluteDiff + Number.EPSILON) * 1000) / 1000;
            return absoluteDiff;
        },
        getAbsoluteSales() {
            let absoluteSales = 0;
            for (const product in this.products) {
                absoluteSales += parseFloat(this.products[product].stats.sales);
            }
            absoluteSales = Math.round((absoluteSales + Number.EPSILON) * 1000) / 1000;
            return absoluteSales;
        }
    },
    // The steps in Vue lifecycle are:
    // - beforeCreate, created,
    // - beforeMount, mounted,
    // - beforeUpdate, updated,
    // - beforeDestroy, destroyed.
    created() {
        // In Server Side Rendering created() is used over mounted() because mounted() is not
        // present in it.
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
