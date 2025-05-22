<template>
  <Dialog :open="showDialog" :closeBtn="true" :onClose="hideUpdatePopup">
    <div class="dialog-title">Entrez une nouvelle valeur (en {{ metric?.unit }})</div>
    <div class="dialog-body">
      <SmartFloatInput v-if="allowFloat" v-model="newValue" :min="minValue" :max="maxValue" :formControl="false" />
      <SmartIntInput v-if="!allowFloat" v-model="newValue" :min="minValue" :max="maxValue" :formControl="false" />
      <button class="btn btn-success update-value-btn" @click="updateValue">Mettre à jour</button>
    </div>
  </Dialog>

  <div v-if="values.length <= 1" class="parameter-chart-solo-value">
    <span class="badge bg-secondary op-font-md">
      <span v-if="values.length === 1">{{ values[0][1] }} {{ metric.unit }}</span>
      <span v-if="values.length === 0">Non connu</span>
    </span>
    <a href="" @click.prevent="showUpdatePopup" v-show="withUpdate">(mettre à jour)</a>
  </div>

  <div v-if="values.length > 1" class="parameter-chart-multiple-values">
    <GoogleChart type="AreaChart" :data="chartData" :options="chartOptions" :style="cssStyle" />
    <div class="multiple-update-section">
      <span class="badge bg-secondary op-font-md">{{ values[values.length - 1][1] }} {{ metric.unit }}</span>
      <button class="btn btn-secondary op-font-md" @click="showUpdatePopup" v-show="withUpdate">Mettre à jour</button>
    </div>
  </div>
</template>

<script>
import { GCHART_COLORS } from "@/common/static.js";
import { addDays } from "@/common/dates.js";
import Dialog from "@/components/interface/Dialog.vue";
import GoogleChart from "@/components/interface/GoogleChart.vue";
import SmartFloatInput from "@/components/interface/smart_inputs/SmartFloatInput.vue";
import SmartIntInput from "@/components/interface/smart_inputs/SmartIntInput.vue";
import API from "@/api.js";
import { mapGetters } from "vuex";

export default {
  name: "ParameterChart",
  props: [
    "profileId", // Which profile
    "metricKey", // Parameter key
    "width", // Default: 230px
    "height", // Default: 150px
    "nbDays", // Number of days  ('auto' == will calculate a reasonable time window)
    "withUpdate", // Show a update button/link
    "allowFloat", // When updating, allowing float values ?
    "minValueDiff", // If set, what is the minimum interval between min and max Y
    "onUpdate",
    "minValue",
    "maxValue",
  ],
  data: () => ({
    showDialog: false,
    newValue: null,
    chartData: [],
    chartOptions: {},
    values: [],
    metric: null,
  }),
  mounted() {
    if (this.profileId) this.init();
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
    }),
    cssStyle() {
      return {
        width: this.width || "230",
        height: this.height || "150",
      };
    },
  },
  watch: {
    profileId(newProfileId) {
      if (newProfileId) this.init();
    },
  },
  methods: {
    showUpdatePopup() {
      this.showDialog = true;
    },
    hideUpdatePopup() {
      this.showDialog = false;
    },
    init() {
      this.newValue = null;
      const postArgs = { key: this.metricKey };
      if (this.nbDays === "auto") {
        postArgs["auto_time_window"] = true;
      } else if (this.nbDays) {
        postArgs["min_date"] = addDays(new Date(), -this.nbDays);
      }
      API.profile.metricHistory(this.userId, this.profileId, postArgs).then(this.onMetricsRetrieved);
    },
    onMetricsRetrieved(data) {
      this.values = data.values;
      this.metric = data.metric;
      if (this.values.length > 1) {
        this.chartData = [this.buildCols(data), ...this.buildRows(data)];
        this.chartOptions = this.buildOptions(data);
      }
    },
    buildCols(data) {
      return [
        {
          id: "date",
          label: "Date",
          type: "date",
          p: {},
        },
        {
          id: "value",
          label: data.metric.name,
          type: "number",
          p: {},
        },
      ];
    },
    buildRows(data) {
      const res = [];
      for (let i = 0; i < data.values.length; i++) {
        const rowValues = [];
        for (let j = 0; j < 2; j++) {
          // Date and value
          let value = data.values[i][j];
          if (j === 0) {
            // date needs to be parsed
            value = new Date(value);
          }
          rowValues.push({ v: value });
        }
        res.push({ c: rowValues });
      }
      return res;
    },
    buildOptions(data) {
      // Retrieving all the dates, that will be xticks
      const xticks = [];
      const values = [];
      for (let i = 0; i < data.values.length; i++) {
        values.push(data.values[i][1]);
        xticks.push(new Date(data.values[i][0]));
      }
      const res = {
        hAxis: {
          ticks: xticks,
          gridlines: { count: 0 },
          format: "dd MMMM",
        },
        vAxis: {
          textStyle: { fontSize: 11, fontName: "Arial" },
        },
        colors: GCHART_COLORS,
        pointSize: 5,
        legend: {
          position: "none",
        },
        tooltip: { textStyle: { fontSize: 12 } },
        chartArea: { width: "75%", height: "80%", top: "10" },
      };
      if (this.minValueDiff) {
        const minDiff = parseFloat(this.minValueDiff);
        const min = Math.min(values);
        const max = Math.max(values);
        if (max - min < minDiff) {
          const forcedMin = (min + max) / 2 - minDiff / 2;
          const forcedMax = (min + max) / 2 + minDiff / 2;
          res["vAxis"]["viewWindow"] = { min: forcedMin, max: forcedMax };
        }
      }
      return res;
    },
    async updateValue() {
      this.showDialog = false;
      if (this.newValue != null) {
        const metrics = { [this.metricKey]: this.newValue };
        await API.profile.updateMetrics(this.userId, this.profileId, { metrics });
        this.$store.dispatch("profile/update").then(() => this.onUpdate && this.onUpdate());
        this.init();
      }
    },
  },
  components: { Dialog, SmartFloatInput, SmartIntInput, GoogleChart },
};
</script>

<style scoped lang="scss">
.parameter-chart-solo-value {
  margin-top: 5px;
  a {
    margin-left: 5px;
  }
}
.parameter-chart-multiple-values {
  .label {
    vertical-align: bottom;
  }
  .btn {
    float: right;
    padding: 2px 5px 2px 5px;
  }
  .multiple-update-section {
    margin-top: 10px;
  }
}
.update-value-btn {
  padding: 3px 10px 3px 10px;
  margin-left: 5px;
}
</style>
