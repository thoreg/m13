<template>
<div>
  <h1>{{ msg }}</h1>
  <Datepicker v-model="dateRange" range :presetRanges="presetRanges" />
  <p v-if="dateRange">
    Datum gewählt: {{ dateRange }}
  </p>
  <p v-else>
    Kein Datum gewählt - Standard: Daten der letzten vier Wochen
  </p>
  <ZalandoCalculatorV1 msg="Zalando Calculator V1" v-if="dateRange" :from-date="computedFrom"/>
  <ZalandoCalculatorV1 msg="Zalando Calculator V1" v-else />
</div>
</template>

<script>
import ZalandoCalculatorV1 from './components/ZalandoCalculatorV1.vue'
import Datepicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';

import { ref } from 'vue';
import { endOfMonth, endOfYear, startOfMonth, startOfYear, subMonths } from 'date-fns';

export default {
  name: 'App',
  components: {
    Datepicker,
    ZalandoCalculatorV1
  },
  setup() {
    const date = ref();
    const presetRanges = ref([
      {
        label: 'Dieser Monat',
        range: [startOfMonth(new Date()), endOfMonth(new Date())]
      },
      {
        label: 'Letzter Monat',
        range: [startOfMonth(subMonths(new Date(), 1)), endOfMonth(subMonths(new Date(), 1))],
      },
      {
        label: 'Letzten 3 Monate',
        range: [startOfMonth(subMonths(new Date(), 3)), endOfMonth(new Date())],
      },
      {
        label: 'Dieses Jahr',
        range: [startOfYear(new Date()), endOfYear(new Date())]
      },
      {
        label: 'Anbeginn der Zeit',
        range: [new Date('2021-06-01T00:00:00'), endOfYear(new Date())]
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
      msg: 'Zalando Calculator V1'
    }
  },
  computed: {
    computedFrom() {
      if (this.dateRange) {
        return this.dateRange[0].toISOString().substring(0, 10);
      }
      return null;
    },
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
