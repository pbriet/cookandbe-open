<template>
  <GoogleChart class="op-ratio-pie-chart" type="PieChart" :data="data" :options="options" :style="style" />
</template>

<script>
import GoogleChart from "@/components/interface/GoogleChart.vue";
import { GCHART_COLORS } from "@/common/static.js";
import { mapGetters } from "vuex";

/*
 * Displays a pie chart of profile ratios (family)
 */
export default {
  name: "RatioPieChart",
  props: ["width", "height", "ratios"],
  computed: {
    ...mapGetters({
      profiles: "profile/getProfiles",
    }),
    style() {
      const style = {};
      if (this.width) style["width"] = this.width;
      if (this.height) style["height"] = this.height;
      return style;
    },
    options() {
      return {
        colors: GCHART_COLORS,
        chartArea: { top: 0, height: 180, left: 0 },
        legend: "none",
        pieSliceText: "label",
        tooltip: { trigger: "none" },
      };
    },
    data() {
      const rows = [];
      for (const profile of this.profiles) {
        let ratio = profile.ratio;
        if (this.ratios) {
          if (!this.ratios[profile.id]) {
            continue;
          }
          ratio = this.ratios[profile.id];
        }
        rows.push({ c: [{ v: profile.nickname }, { v: ratio }] });
      }

      return [
        [
          { id: "profile", label: "Personne", type: "string" },
          { id: "ratio", label: "Part", type: "number" },
        ],
        ...rows,
      ];
    },
  },
  components: { GoogleChart },
};
</script>

<style lang="scss">
.op-ratio-pie-chart {
  div div {
    width: inherit !important;
    overflow: hidden; // Ugly fix of Google chart weird behaviour
  }
}
</style>
