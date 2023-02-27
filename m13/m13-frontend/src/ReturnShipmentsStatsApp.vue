<template>
<div>
    <h1>{{ msg }}</h1>
    <div>
        Marketplace:
        <input type="radio" id="zalando" value="zalando" v-model="marketplace" />
        <label for="zalando">zalando</label>
        <input type="radio" id="otto" value="otto" v-model="marketplace" />
        <label for="otto">otto</label>
    </div>
    <Datepicker v-model="dateRange" range :presetRanges="presetRanges" />
    <p v-if="dateRange">
        Datum gewählt: {{ dateRange }}
    </p>
    <p v-else>
        Kein Datum gewählt - Standard: Daten der letzten vier Wochen
    </p>
    <p v-if="marketplace">
        Markplatz gewählt: {{ marketplace }}
    </p>
    <p v-else>
        Kein Markplatz gewählt - Standard: Zalando
    </p>
    <ReturnShipmentsStats msg="Return Shipments Stats" v-if="dateRange" :from-date="computedFrom" :marketplace="marketplace"/>
    <ReturnShipmentsStats msg="Return Shipments Stats" :marketplace="marketplace" v-else />
</div>
</template>

<script>
import ReturnShipmentsStats from './components/ReturnShipmentsStats.vue'
import Datepicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';

import { ref } from 'vue';
import { endOfMonth, endOfYear, startOfMonth, startOfYear, subMonths } from 'date-fns';

export default {
    name: 'ReturnShipmentsStatsApp',
    components: {
        Datepicker,
        ReturnShipmentsStats
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
            msg: 'Return Shipments Stats',
            marketplace: 'zalando'
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

/* remove standard-styles */
input {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  border:none;
  border-radius: 0;
  font-size: 1em;
  width: 100%
}

/* graceful degradation for ie8 */
input[type='checkbox'],
input[type='radio'] {
  width:auto;
  float:left;
  margin-right: .75em;
  background:transparent;
  border:none;
}

input[type='checkbox']:checked,
input[type='checkbox']:not(:checked),
input[type='radio']:checked,
input[type='radio']:not(:checked) {
  background: transparent;
  position: relative;
  visibility: hidden;
  margin:0;
  padding:0;
}

input[type='checkbox'] + label,
input[type='radio'] + label {
  cursor: pointer;
  margin: 0 1em 0 0;
}

input[type='checkbox']:checked + label::before,
input[type='checkbox']:not(:checked) + label::before,
input[type='radio']:checked + label::before,
input[type='radio']:not(:checked) + label::before {
    content:' ';
    display:inline-block;
    width: 17px;
    height:17px;
    position: relative;
    top:4px;
    border: 1px solid #bbb;
    background: white;
    margin-right: 1em;
    box-shadow: inset 0 1px 1px 0 rgba(0,0,0,.1);
}

input[type=radio]:checked + label::before,
input[type=radio]:not(:checked) + label::before {
  border-radius: 30px;
}

input[type='checkbox']:hover  + label::before,
input[type='radio']:hover  + label::before {
  background:#ddd;
  box-shadow: inset 0 0 0 2px white;
}

input[type='checkbox']:checked  + label::before,
input[type='radio']:checked  + label::before {
  background:black;
  box-shadow: inset 0 0 0 2px white;
}
</style>
