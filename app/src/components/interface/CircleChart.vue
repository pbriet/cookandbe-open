<template>
  <div class="circle-chart">
    <div class="circlechart_and_text">
      <div ref="chart" :data-percent="percent"></div>
      <div class="epc-text" :class="valueClass">
        <FontAwesomeIcon v-if="faClass" :icon="['fas', faClass]" />
        <span v-if="displayMode === 'percentage'">{{ percent }}%</span>
        <span v-if="displayMode === 'max'">
          <span v-if="percent <= 100">OK</span>
          <span v-if="percent > 100">+ {{ percent - 100 }}%</span>
        </span>
      </div>
    </div>
    <div class="epc-caption">
      <slot></slot>
    </div>
  </div>
</template>

<script>
import EasyPieChart from "easy-pie-chart";

export default {
  name: "CircleChart",
  props: [
    "percent",
    "barColor",
    "faClass", // Fontawesome icon to display, if so
    "displayMode", // Either 'percentage', or 'max'
    "valueClass", // Class for text displaying value (% or OK)
  ],
  mounted() {
    new EasyPieChart(this.$refs.chart, this.options);
  },
  computed: {
    options() {
      return {
        barColor: this.barColor || "#7AB231",
        trackColor: "#e5e5e5",
        scaleColor: false,
        size: 80,
        lineWidth: 10,
      };
    },
  },
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss">
.circle-chart {
  display: inline-block;

  .circlechart_and_text {
    width: 80px;
    height: 80px;
    text-align: center;
    margin: auto;

    .epc-text {
      position: relative;
      top: -69%;
      font-size: $op-font-lg;
      font-weight: bold;
    }
  }

  .epc-caption {
    clear: both;
    font-weight: bold;
    text-align: center;
  }
}
</style>
