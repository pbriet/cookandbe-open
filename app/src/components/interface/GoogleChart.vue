<template>
  <div ref="chart" :style="style"></div>
</template>

<script>
import { GoogleCharts } from "google-charts";
import { debounce } from "lodash";

let googleChartsPromise = null;
function onGoogleChartsLoaded() {
  return new Promise((resolve) => {
    if (googleChartsPromise) {
      googleChartsPromise.then(() => {
        GoogleCharts.api.charts.setOnLoadCallback(resolve);
      });
    } else {
      googleChartsPromise = GoogleCharts.load(() => {
        GoogleCharts.api.charts.setOnLoadCallback(resolve);
      });
    }
  });
}

export default {
  name: "GoogleChart",
  props: ["type", "data", "options", "style"],
  data: () => ({
    chart: null,
  }),
  computed: {},
  mounted() {
    onGoogleChartsLoaded().then(() => {
      this.chart = new GoogleCharts.api.visualization[this.type](this.$refs.chart);
      this.drawChart();
    });
    this.redrawOnResize = debounce(this.drawChart, 100);
    window.addEventListener("resize", this.redrawOnResize);
  },
  watch: {
    data: {
      deep: true,
      handler() {
        this.drawChart();
      },
    },
    options: {
      deep: true,
      handler() {
        this.drawChart();
      },
    },
  },
  methods: {
    drawChart() {
      if (!this.chart) return;
      const data = GoogleCharts.api.visualization.arrayToDataTable(this.data);
      this.chart.draw(data, this.options);
    },
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.redrawOnResize);
    if (this.chart) {
      this.chart.clearChart();
    }
  },
};
</script>
