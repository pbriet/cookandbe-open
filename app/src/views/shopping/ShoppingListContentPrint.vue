<template>
  <h1>
    Liste de courses
    <small v-if="nbMissingItems > 1">({{ nbMissingItems }} articles)</small>
    <small v-if="nbMissingItems < 2">({{ nbMissingItems }} article)</small>
    <br />
    <small>
      {{ upperFirst(DateTime.fromISO(shoppingList.startDate).setLocale("fr").toFormat("EEEE d MMMM")) }}
      <span v-show="shoppingList.startDate !== shoppingList.endDate">
        à {{ DateTime.fromISO(shoppingList.endDate).setLocale("fr").toFormat("EEEE d MMMM") }}
      </span>
    </small>
  </h1>

  <div class="print-list-content">
    <div class="print-list-column" v-for="(column, index) in printColumns.filter((c) => c.length > 0)" :key="index">
      <div
        class="print-list-category"
        v-for="category in column.filter((c) => c.missingItems > 0)"
        :key="category.foodType"
      >
        <h4>
          {{ category.foodType }}
          <small>({{ category.missingItems }} article<span v-if="category.missingItems > 1">s</span>)</small>
        </h4>
        <ul>
          <li v-for="item in category.items.filter((i) => !i.gotIt)" :key="item.id">
            <span class="fleft">
              <span style="margin-left: -13px" v-if="item.dietExclusions">
                <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" class="me-1" />
              </span>
              <span style="margin-left: -13px" v-if="item.dietWarnings && !item.dietExclusions">
                <FontAwesomeIcon :icon="['fas', 'info-circle']" class="me-1" />
              </span>
              <span v-if="item.forcedName">{{ item.forcedName }}</span>
              <span v-if="!item.forcedName">{{ item.food.name }}</span>
            </span>

            <span class="fright">
              <span v-if="!item.forcedQuantity">
                <span v-html="conversionClean(item.conversion, item.food.name)"></span>
                <span v-if="item.basicConversion">
                  (<span v-html="item.basicConversion.htmlValue"></span> {{ item.basicConversion.unit }})
                </span>
              </span>
              <span v-if="item.forcedQuantity"> {{ item.forcedQuantity }} </span>
            </span>

            <div class="fleft w-100" v-if="item.freezeDate">
              <div class="col-12" v-for="day in iterItemDays(item)" :key="day.date">
                <small
                  ><FontAwesomeIcon :icon="['fas', 'caret-right']" />
                  {{ DateTime.fromISO(day.date).setLocale("fr").toFormat("EEEE dd MMMM") }} -
                  {{ day.quantity }} g</small
                >
                <img width="10" src="@/assets/img/shopping/snowflake.png" class="ms-1" />
              </div>
            </div>

            <span class="clearfix" />
          </li>
        </ul>
      </div>
    </div>
  </div>

  <div class="print-list-legend" v-if="mustPrintLegend">
    <div class="op-font-lg">Légende</div>
    <div>
      <FontAwesomeIcon :icon="['fas', 'info-circle']" /> Vérifiez sur l'emballage l'absence de :
      <b>{{ printWarningTags.join(", ") }}</b>
    </div>
    <div>
      <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" /> Articles à exclure de votre alimentation car contenant
      :
      <b>{{ printExclusionTags.join(", ") }}</b>
    </div>
  </div>
</template>

<script>
import { DateTime } from "luxon";
import { upperFirst } from "lodash";
import { conversionClean } from "@/common/filters.js";

const NB_COLUMNS = 2;
const CATEGORY_HEADER_SIZE = 3;

export default {
  name: "ShoppingListContentPrint",
  props: ["shoppingList", "nbMissingItems", "iterItemDays"],
  data: () => ({
    DateTime,
  }),
  computed: {
    printColumns() {
      const columnSizes = [];
      const columns = [];
      for (let c = 0; c < NB_COLUMNS; ++c) {
        columns.push([]);
        columnSizes.push(0);
      }
      for (const category of this.shoppingList.content) {
        const nbItems = category.items.filter((item) => !item.gotIt).length;
        const nextColumn = this.getSmallestColumn(columnSizes);
        columns[nextColumn].push(category);
        columnSizes[nextColumn] += nbItems + CATEGORY_HEADER_SIZE;
      }
      return columns;
    },
    mustPrintLegend() {
      return this.printWarningTags.length !== 0 || this.printExclusionTags.length !== 0;
    },
    printExclusionTags() {
      const exclusionTags = [];
      if (!this.shoppingList) {
        return exclusionTags;
      }
      for (const category of this.shoppingList.content) {
        for (const item of category.items) {
          if (item.dietExclusions) {
            for (const dietExclusion of item.dietExclusions) {
              if (exclusionTags.indexOf(dietExclusion) < 0) {
                exclusionTags.push(dietExclusion);
              }
            }
          }
        }
      }
      return exclusionTags;
    },
    printWarningTags() {
      const warningTags = [];
      if (!this.shoppingList) {
        return warningTags;
      }
      for (const category of this.shoppingList.content) {
        for (const item of category.items) {
          if (item.dietWarnings) {
            for (const dietWarning of item.dietWarnings) {
              if (warningTags.indexOf(dietWarning) < 0) {
                warningTags.push(dietWarning);
              }
            }
          }
        }
      }
      return warningTags;
    },
  },
  methods: {
    upperFirst,
    conversionClean,
    getSmallestColumn(columnSizes) {
      let indexMin = 0;
      let sizeMin = columnSizes[0];
      for (let c = 1; c < columnSizes.length; ++c) {
        if (columnSizes[c] < sizeMin) {
          indexMin = c;
          sizeMin = columnSizes[c];
        }
      }
      return indexMin;
    },
  },
  components: {},
};
</script>

<style scoped lang="scss">
.print-list-content {
  display: table !important;
  table-layout: fixed;
  width: 100%;
}

.print-list-column {
  display: table-cell;
  padding: 10px;
}

.print-list-column + .print-list-column {
  border-left: $op-page-content-border-width solid $op-color-border;
}

.print-list-category {
  width: 100%;
  clear: both;
}

ul {
  list-style: none;
  padding-left: 15px;
}

li {
  font-size: $op-font-xxs;
  &:after {
    @extend .clearfix;
  }
}

.print-list-legend {
  margin: 15px;
  padding: 15px;
  border-radius: $op-radius-md;
  border: 1px solid black;
}
</style>
