<template>
  <ZalandoCalculator msg="Zalando Calculator"/>
</template>

<script>
import ZalandoCalculator from './components/ZalandoCalculator.vue'

export default {
  name: 'App',
  components: {
    ZalandoCalculator
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
