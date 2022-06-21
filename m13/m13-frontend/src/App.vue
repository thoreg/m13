<template>
<div>
  <h1>{{ msg }}</h1>
  <Datepicker v-model="dateRange" range :presetRanges="presetRanges" />
  <p>
    Selected Date Range: {{ dateRange }}
  </p>
  <p>
    {{ getProductDataByDateRange }}
  </p>

  <ZalandoCalculator msg="Zalando Calculator"/>
</div>
</template>

<script>
import ZalandoCalculator from './components/ZalandoCalculator.vue'
import Datepicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';

import { ref } from 'vue';
import { endOfMonth, endOfYear, startOfMonth, startOfYear, subMonths } from 'date-fns';

export default {
  name: 'App',
  components: {
    Datepicker,
    ZalandoCalculator
  },
  setup() {
    const date = ref();

    const presetRanges = ref([
      {
        label: 'This month',
        range: [startOfMonth(new Date()), endOfMonth(new Date())]
      },
      {
        label: 'Last month',
        range: [startOfMonth(subMonths(new Date(), 1)), endOfMonth(subMonths(new Date(), 1))],
      },
      {
        label: 'Last 3 months',
        range: [startOfMonth(subMonths(new Date(), 3)), endOfMonth(new Date())],
      },
      {
        label: 'This year',
        range: [startOfYear(new Date()), endOfYear(new Date())]
      },
    ]);

    return {
      date,
      presetRanges,
    }
  },
  data() {
    return {
      dateRange: '',
      msg: 'Zalando Calculator'
    }
  },
  computed: {
    getProductDataByDateRange() {
      console.log(`date picked - from: ${this.dateRange[0]} to: ${this.dateRange[1]}`);
      return 0;
    }
  }
}
</script>

<style>
#app {
  font-family: monospace;
  text-align: center;
  color: #2c3e50;
  margin-top: 10px;
}
</style>
