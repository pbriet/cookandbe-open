<template>
  <div class="op-recipe-stats-content" v-show="recipeNutrients">
    <div>
      <h2 class="col-12">Informations nutritionnelles</h2>

      <div class="clearfix"></div>

      <div class="center-block" ref="piechart">
        <GoogleChart type="PieChart" :data="data" :options="options" v-if="consistentData && displayChart" />
      </div>

      <div class="nutrient-details">
        <h3 class="col-12">
          Apports pour
          <span v-if="ratio && mainProfile">
            {{ mainProfile.nickname }}
          </span>
          <span v-if="!ratio">1 personne moyenne</span>
        </h3>
        <div class="nutrient-table op-table-auto col-12 op-vs op-hs-0">
          <div v-for="stat in nutrientStats" :key="stat.name">
            <div>{{ upperFirst(stat.name) }}</div>
            <div v-if="stat.value">{{ stat.value.toFixed(1) }} {{ stat.unit }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="clearfix"></div>
  </div>
</template>

<script>
import GoogleChart from "@/components/interface/GoogleChart.vue";
import { mapGetters } from "vuex";
import { each, upperFirst } from "lodash";
import $ from "jquery";

/*
 * This components displays a recipe with the correct ratio
 */
export default {
  name: "RecipeStats",
  props: ["recipe", "ratio", "width", "padding"],
  data() {
    const legendHeight = 20;
    const width = this.width || 0;
    return {
      chartWidth: width,
      chartHeight: width + legendHeight,
      legendHeight,
      recipeNutrients: null,
      displayChart: false,
    };
  },
  mounted() {
    this.reset(this.recipe);
  },
  computed: {
    ...mapGetters({
      mainProfile: "profile/getMainProfile",
    }),
    nutrientStats() {
      const nutrientKeys = [
        "energiekilocalories",
        "proteines",
        "glucides",
        "lipides",
        "acidesgrassatures",
        "fibres",
        "added_sugar",
        "calcium",
        "sodium",
        "vitaminec",
        "fer",
        "magnesium",
      ];
      const rows = [{ name: "", value: "", unit: "" }];
      each(nutrientKeys, (nutrientKey) => {
        each(this.recipeNutrients, (stat) => {
          if (stat.nutrient && nutrientKey === stat.nutrient.key) {
            rows.push({ name: stat.nutrient.shortName, value: stat.value, unit: stat.nutrient.unit });
          }
        });
      });
      return rows;
    },
    nutrientKeys() {
      return ["proteines", "glucides", "lipides"];
    },
    data() {
      const rows = [];
      each(this.nutrientKeys, (nutrientKey) => {
        each(this.recipeNutrients, (stat) => {
          if (stat.nutrient && nutrientKey === stat.nutrient.key) {
            rows.push({ c: [{ v: stat.nutrient.shortName }, { v: stat.value }] });
          }
        });
      });
      return [
        [
          { id: "nutrient", label: "Nutriment", type: "string" },
          { id: "ratio", label: "Proportion", type: "number" },
        ],
        ...rows,
      ];
    },
    options() {
      const piechartPadding = this.padding || 15;
      return {
        slices: {
          0: { color: "#d9534f" },
          1: { color: "#7AB231" },
          2: { color: "#f4c741" },
        },
        chartArea: {
          left: piechartPadding,
          right: piechartPadding,
          top: piechartPadding,
          bottom: piechartPadding,
          width: this.chartWidth - 2 * piechartPadding,
          height: this.chartWidth - 2 * piechartPadding,
        },
        width: this.chartWidth,
        height: this.chartWidth + this.legendHeight,
        legend: { position: "bottom", alignment: "center", maxLines: this.nutrientKeys.length },
        pieSliceText: "percentage",
        tooltip: { trigger: "none" },
        enableInteractivity: false,
        backgroundColor: "transparent",
      };
    },
    consistentData() {
      return this.data.length == this.nutrientKeys.length + 1;
    },
  },
  watch: {
    recipe(recipe) {
      if (!recipe) {
        this.displayChart = false;
        return;
      }
      this.reset(recipe);
    },
  },
  methods: {
    upperFirst,
    async reset(recipe) {
      if (!recipe || !recipe.id) {
        return;
      }
      this.recipeNutrients = await this.$store.dispatch("recipe/getNutrients", {
        recipeId: recipe.id,
        ratio: this.ratio,
      });
      // Redrawing the chart can make it look off, it is safer to
      // remove it from DOM and redisplay it when everything is ready
      this.$nextTick(() => {
        this.displayChart = true;
        this.$nextTick(() => {
          this.loadStats();
        });
      });
    },
    loadStats() {
      // Chart size
      this.chartWidth = this.width || parseInt($(this.$refs.piechart).width());
      this.chartHeight = this.chartWidth + this.legendHeight;
    },
  },
  components: { GoogleChart },
};
</script>

<style scoped lang="scss">
.op-recipe-stats-content {
  .center-block {
    display: flex;
    justify-content: center;
    > div {
      max-width: 100%;
    }
  }

  .nutrient-details {
    margin-top: 20px;
    h3 {
      font-weight: bold;
      font-size: inherit !important;
    }
  }
  h2 {
    font-size: 24px !important;
  }
}
</style>
