<template>
  <div class="day-indicators" :class="classes">
    <div class="row">
      <div class="d-none d-md-block">
        <div class="indicators-title">
          <ProfileLogo v-if="profile" :sex="profile.sex" :style="{ display: 'inline' }" />
          {{ getTitle }}
        </div>
        <i class="all-recipes-text">
          Les informations ci-dessous sont calculées en incluant l'ensemble des suggestions<br />(y compris les repas
          masqués)
        </i>

        <ul class="short-indicators">
          <li>
            <FontAwesomeIcon :icon="['fas', 'chart-pie']" />
            <div>
              <div class="d-inline-flex">
                {{ Math.round(indicators.nutrients.currentDayCalories) }} kcal
                <span class="why-calories ms-1" @click="showWhyCalories">
                  <FontAwesomeIcon :icon="['fas', 'question-circle']" />
                </span>
              </div>
            </div>
          </li>

          <li>
            <FontAwesomeIcon :icon="['far', 'clock']" />
            <div>{{ upperFirst(RECIPE_SPEED_OPTIONS_DICT[indicators.avgDuration]) }}</div>
          </li>

          <li>
            <FontAwesomeIcon :icon="['fas', 'euro-sign']" />
            <div>{{ RECIPE_PRICE_OPTIONS_DICT[indicators.avgPrice] }}</div>
          </li>
        </ul>
      </div>

      <div id="list-nb_indicators">
        <div
          :class="`nb_indicators category-${category}`"
          v-for="category in INDICATORS_CATEGORIES"
          :key="category"
          v-show="getLength(indicators.nutrients[category]) > 0"
          @click="showIndicators(category)"
        >
          <div class="badge">
            {{ getLength(indicators.nutrients[category]) }}
          </div>
          <div class="indicator-name">
            {{ INDICATOR_CATEGORIES_NAMES[category] }}
          </div>
          <span class="fa-search">
            <FontAwesomeIcon :icon="['fas', 'search']" />
          </span>
        </div>
      </div>
    </div>
  </div>

  <!-- Indicators details popup -->
  <Dialog
    :id="`indicators-dialog-${mode}`"
    class="indicators-dialog"
    :open="showIndicatorsDialog"
    :onClose="hideIndicators"
    :closeBtn="true"
  >
    <div class="dialog-title">
      {{ INDICATOR_CATEGORIES_NAMES[selectedCategory] }}
    </div>
    <div class="dialog-body">
      <div v-if="selectedCategory == 'disabledKo'" class="op-font-lg">
        <div class="text-center">
          <span class="op-font-dxl">
            <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" />
          </span>
        </div>
        <br />
        {{ APP_BRAND_NAME }} réalise ses suggestions sur la base des principaux macro-nutriments uniquement.<br /><br />

        Il est
        <u
          ><b>très difficile de suivre une alimentation <i>parfaite</i></b></u
        >
        selon les recommandations de l'ANSES.<br /><br />

        <b>Pourquoi ?</b>
        <ul>
          <li>Une alimentation <i>parfaite</i> nécessite une consommation régulière d'abats et de poissons.</li>
          <li>
            Certains nutriments se stockent sur de longues durées, et sont parfois assimilés hors du cadre alimentaire
            (la vitamine D se sécrète grâce à une exposition au soleil)
          </li>
          <li>Une telle alimentation est souvent trop restrictive au quotidien</li>
        </ul>

        Néanmoins, vous avez la possibilité d'activer le contrôle de certains nutriments ci-dessous dans la section
        <router-link :to="{ name: 'MyAccount' }">Alimentation</router-link>.<br /><br />

        <span class="op-font-xl">
          <FontAwesomeIcon :icon="['fas', 'user-md']" />
        </span>
        En cas de doute, parlez en à votre médecin.<br />
        <br />

        <router-link :to="{ name: 'MyAccount' }" class="btn btn-success go-to-my-account-btn">
          Paramétrer le contrôle des nutriments
        </router-link>
        <hr />
      </div>

      <div v-if="selectedCategory == 'ko'" id="why-unbalanced" class="op-font-lg">
        <div class="text-center">
          <span class="op-font-dxl">
            <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" />
          </span>
        </div>
        <br />
        Votre configuration actuelle <u><b>ne permet pas un équilibre optimal.</b></u
        ><br /><br />

        <b>Pourquoi ?</b><br /><br />Plusieurs raisons peuvent en être à l'origine :<br />
        <div class="op-raw-table">
          <div>
            <FontAwesomeIcon :icon="['far', 'clock']" class="me-2" />
            <span>Vos contraintes de <b>temps</b> ou de <b>budget</b> sont trop fortes.</span>
          </div>
          <div>
            <FontAwesomeIcon :icon="['fas', 'wrench']" />
            <span>La <b>structure</b> de vos repas ne permet pas un bon équilibre.</span>
          </div>
          <div>
            <FontAwesomeIcon :icon="['fas', 'check']" />
            <span
              >Vous avez <b>imposé</b> trop de recettes déséquilibrées ou bien vous mangez <b>trop souvent</b> à
              l'extérieur.</span
            >
          </div>
          <div>
            <FontAwesomeIcon :icon="['far', 'thumbs-down']" />
            <span
              >Vous êtes peut-être trop <b>difficile</b>. Certains aliments sont essentiels à un régime équilibré.</span
            >
          </div>
          <div>
            <FontAwesomeIcon :icon="['fas', 'fire']" />
            <span
              >Vous avez activé <b>trop de contraintes nutritionnelles</b>. Dans les faits, suivre l'intégralité des
              recommandations est extrêmement difficile.</span
            >
          </div>
        </div>
        <br />
        <span class="op-font-xl">
          <FontAwesomeIcon :icon="['fas', 'user-md']" />
        </span>
        En cas de doute, contactez votre médecin
      </div>

      <div v-for="group in INDICATOR_GROUPS" class="indicator-group" :key="group.title">
        <div class="indicator-group-title" v-if="group.indicators.length > 0 && selectedCategory == 'ok'">
          {{ group.title }}
        </div>

        <div v-for="key in this.groupIndicators(group)" :key="key" class="indicator-element">
          <h3>
            {{ INDICATOR_TITLE[element(key).key] }}
          </h3>

          <input type="checkbox" class="read-more-state" :id="`read-more-${element(key).key}`" />
          <div v-if="INDICATOR_DESCRIPTION[element(key).key]" class="indicator-description read-more-wrap">
            {{ truncate(INDICATOR_DESCRIPTION[element(key).key], { length: 200, omission: "" }) }}
            <label
              class="read-more-trigger"
              :for="`read-more-${element(key).key}`"
              v-if="INDICATOR_DESCRIPTION[element(key).key].length > 200"
            ></label>
            <span class="read-more-target">
              {{ truncate(INDICATOR_DESCRIPTION[element(key).key].substring(200), { length: 5000 }) }}
            </span>
          </div>

          <div v-if="element(key).type === 'min_max'">
            <svg height="110px" :width="`${BAR_LENGTH}px`">
              <g>
                <polyline
                  v-if="element(key).daily"
                  fill="none"
                  stroke="#333"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  :points="`${graphes[key].dailyArrow.x1},35 ${graphes[key].dailyArrow.x2},45 ${graphes[key].dailyArrow.x3},35`"
                />
                <text
                  v-if="element(key).daily"
                  :x="`${graphes[key].dailyArrow.x2}`"
                  y="0"
                  fill="#333"
                  text-anchor="middle"
                >
                  <tspan dy="1.2em">{{ element(key).daily.strValue }}&nbsp;{{ element(key).daily.unit }}</tspan>
                  <tspan :x="`${graphes[key].dailyArrow.x2}`" dy="1.2em">
                    {{ upperFirst(DateTime.fromJSDate(currentDate).setLocale("fr").toFormat("EEEE")) }}
                  </tspan>
                </text>

                <line
                  v-for="bar in graphes[key].bars"
                  :key="`${bar.x1},${bar.x2}`"
                  y1="55"
                  y2="55"
                  :x1="`${bar.x1}`"
                  :x2="`${bar.x2}`"
                  :style="`stroke-width: 20px;stroke: ${bar.color}`"
                ></line>

                <text
                  v-if="element(key).weekly.min"
                  :x="`${graphes[key].greenBar.x1 - 5}`"
                  y="59"
                  fill="#FFF"
                  font-size="10"
                  text-anchor="end"
                >
                  &lt; {{ element(key).weekly.min }}
                </text>
                <text
                  v-if="element(key).weekly.max"
                  :x="`${graphes[key].greenBar.x2 + 5}`"
                  y="59"
                  fill="#FFF"
                  font-size="10"
                  text-anchor="start"
                >
                  {{ element(key).weekly.max }} +
                </text>

                <polyline
                  v-if="element(key).weekly"
                  fill="none"
                  stroke="#333"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  :points="`${graphes[key].weeklyArrow.x1},75 ${graphes[key].weeklyArrow.x2},65 ${graphes[key].weeklyArrow.x3},75`"
                />
                <text
                  v-if="element(key).weekly"
                  :x="`${graphes[key].weeklyArrow.x2}`"
                  y="77"
                  fill="#333"
                  text-anchor="middle"
                  font-size="12"
                >
                  <tspan dy="1.2em">Moyenne semaine</tspan>
                  <tspan :x="`${graphes[key].weeklyArrow.x2}`" dy="1.2em">
                    {{ element(key).weekly.strValue }}&nbsp;{{ element(key).weekly.unit }}
                    / jour
                  </tspan>
                </text>
              </g>
            </svg>

            <div
              class="limit-value"
              v-if="element(key).daily && element(key).daily.flag == 'nearly' && element(key).daily.percentDiff > 1"
            >
              <FontAwesomeIcon :icon="['fas', 'info-circle']" /> Les apports quotidiens sont limites mais acceptables
            </div>
            <div class="limit-value" v-if="element(key).weekly.flag == 'nearly' && element(key).weekly.percentDiff > 1">
              <FontAwesomeIcon :icon="['fas', 'info-circle']" /> La moyenne semaine est limite mais acceptable
            </div>

            <div
              class="pack-can-be-enabled"
              v-if="selectedCategory == 'disabledKo' && packsPerNutrient[element(key).key]?.length"
            >
              Ce nutriment peut être contrôlé en activant
              <span v-if="packsPerNutrient[element(key).key].length > 1">l'un des packs suivants</span>
              <span v-if="packsPerNutrient[element(key).key].length == 1">le pack suivant</span> :
              <ul>
                <li v-for="pack in packsPerNutrient[element(key).key]" :key="pack.id">
                  {{ pack.title }}
                </li>
              </ul>
            </div>

            <div
              class="disabled-unbalanced-what-to-do"
              v-if="INDICATOR_WHAT_TO_DO[element(key).key] && selectedCategory == 'disabledKo'"
            >
              {{ INDICATOR_WHAT_TO_DO[element(key).key] }}
            </div>
          </div>
        </div>
      </div>

      <hr />

      <div class="op-font-xs">
        Certains apports en nutriments sont lissés sur une semaine. Vous pouvez par exemple avoir un léger excès
        d'apport en sel sur un jour, mais sans excès en moyenne.
      </div>

      <table class="op-vs-10" style="display: block">
        <tr v-for="(legend, barColor) in BAR_LEGEND" :key="barColor">
          <td>
            <svg height="20px" width="20px">
              <line y1="10" y2="10" x1="0" x2="20" :style="`stroke-width: 20px; stroke: ${barColor}`"></line>
            </svg>
          </td>
          <td>&nbsp;{{ legend }}</td>
        </tr>
      </table>
    </div>
    <!-- dialog-body -->
  </Dialog>
</template>

<script>
import { mapGetters } from "vuex";
import { DateTime } from "luxon";
import { upperFirst, truncate } from "lodash";
import { APP_BRAND_NAME } from "@/config.js";
import { RECIPE_PRICE_OPTIONS_DICT, RECIPE_SPEED_OPTIONS_DICT } from "@/common/static.js";
import { INDICATOR_TITLE, INDICATOR_DESCRIPTION, INDICATOR_GROUPS, INDICATOR_WHAT_TO_DO } from "@/_data.js";
import Dialog from "@/components/interface/Dialog.vue";
import ProfileLogo from "@/components/interface/ProfileLogo.vue";

const BAR_GREEN = "#7ab231";
const BAR_RED = "#E6787E";
const BAR_GREY = "#999";

/*
 * This component displays indicators of a day being filled
 */
export default {
  name: "DayIndicators",
  props: ["indicators", "mode", "currentDate", "showWhyCalories", "classes"],
  data: () => ({
    DateTime,
    selectedCategory: null,
    showIndicatorsDialog: false,
    INDICATORS_CATEGORIES: ["ok", "ko", "disabledKo"],
    INDICATOR_CATEGORIES_NAMES: {
      ok: "Indicateurs équilibrés",
      ko: "Indicateurs déséquilibrés",
      disabledKo: "Nutriments à surveiller",
    },
    INDICATOR_TITLE,
    INDICATOR_DESCRIPTION,
    INDICATOR_GROUPS,
    INDICATOR_WHAT_TO_DO,
    RECIPE_PRICE_OPTIONS_DICT,
    RECIPE_SPEED_OPTIONS_DICT,
    BAR_GREEN,
    BAR_RED,
    BAR_GREY,
    BAR_LEGEND: {
      [BAR_GREEN]: "Valeur recommandée",
      [BAR_GREY]: "Valeur tolérée pour une journée",
      [BAR_RED]: "Valeur trop faible / trop élevée",
    },
    BAR_LENGTH: 400,
    APP_BRAND_NAME,
  }),
  mounted() {
    const currentWidth = window.innerWidth;
    if (currentWidth < 450) {
      this.BAR_LENGTH = currentWidth - 50;
    } else {
      this.BAR_LENGTH = 400;
    }
  },
  computed: {
    ...mapGetters({
      user: "user/get",
      profile: "profile/getMainProfile",
      packsPerNutrient: "diet/getPacksPerNutrient",
    }),
    getTitle() {
      if (!this.user) {
        return "";
      }
      return this.user.name;
    },
    graphes() {
      const res = {};
      for (const group of this.INDICATOR_GROUPS) {
        for (const key of group.indicators) {
          const element = this.indicators.nutrients[this.selectedCategory][key];
          if (element) {
            res[key] = this.getIndicatorGraph(element);
          }
        }
      }
      return res;
    },
  },
  methods: {
    upperFirst,
    truncate,
    element(key) {
      if (!this.selectedCategory) return null;
      return this.indicators.nutrients[this.selectedCategory][key];
    },
    groupIndicators(group) {
      return group.indicators.filter((key) => this.element(key));
    },
    showIndicators(category) {
      this.selectedCategory = category;
      this.showIndicatorsDialog = true;
    },
    hideIndicators() {
      this.showIndicatorsDialog = false;
    },
    getLength(obj) {
      return Object.keys(obj).length;
    },
    getIndicatorGraph(element) {
      const bars = [];
      let greenBar = null;

      const BAR_LENGTH = this.BAR_LENGTH;

      let startX = 0;
      let maxX = 0;

      let maxWeekDayValue = element.weekly.value;
      if (element.daily && element.daily.value > maxWeekDayValue) {
        maxWeekDayValue = element.daily.value;
      }

      // Calculating max X value
      if (element.daily && element.daily.max) {
        maxX = element.daily.max * 1.2;
      } else if (element.weekly.max) {
        maxX = element.weekly.max * 1.2;
      }
      if (maxWeekDayValue > maxX * 0.9) {
        maxX = maxWeekDayValue * 1.2;
      }
      if (maxX > maxWeekDayValue * 3) {
        maxX = maxWeekDayValue * 3;
      }
      if (maxX < element.weekly.min) {
        maxX = element.weekly.min * 1.2;
      }

      // Hard minimum
      if (element.daily && element.daily.min) {
        const redUntil = BAR_LENGTH * (element.daily.min / maxX);
        // Has a minimum to reach
        bars.push({
          x1: startX,
          x2: redUntil,
          color: this.BAR_RED,
        });
        startX = redUntil;
      }

      // Soft minimum
      if (element.weekly.min) {
        let color = this.BAR_GREY;
        if (!element.daily || !element.daily.min) {
          color = this.BAR_RED;
        }

        const warnUntil = BAR_LENGTH * (element.weekly.min / maxX);
        bars.push({
          x1: startX,
          x2: warnUntil,
          color,
        });
        startX = warnUntil;
      }

      if (!element.weekly.max) {
        // Green until the end
        greenBar = {
          x1: startX,
          x2: BAR_LENGTH,
          size: BAR_LENGTH - startX,
          color: this.BAR_GREEN,
        };
        bars.push(greenBar);
      } else {
        // Green until weekly max
        const endOfGreen = BAR_LENGTH * (element.weekly.max / maxX);
        greenBar = {
          x1: startX,
          x2: endOfGreen,
          size: endOfGreen - startX,
          color: this.BAR_GREEN,
        };
        bars.push(greenBar);
        startX = endOfGreen;

        if (element.daily && element.daily.max) {
          // Warning zone then red zone
          const warnUntil = BAR_LENGTH * (element.daily.max / maxX);
          bars.push({
            x1: startX,
            x2: warnUntil,
            color: this.BAR_GREY,
          });
          bars.push({
            x1: warnUntil,
            x2: BAR_LENGTH,
            color: this.BAR_RED,
          });
        } else {
          // Red zone until the end
          bars.push({
            x1: startX,
            x2: BAR_LENGTH,
            color: this.BAR_RED,
          });
        }
      }

      const res = { bars, greenBar };

      if (element.weekly) {
        res["weeklyArrow"] = {
          x1: (BAR_LENGTH * element.weekly.value) / maxX - 5,
          x2: (BAR_LENGTH * element.weekly.value) / maxX,
          x3: (BAR_LENGTH * element.weekly.value) / maxX + 5,
        };
      }

      if (element.daily) {
        res["dailyArrow"] = {
          x1: (BAR_LENGTH * element.daily.value) / maxX - 5,
          x2: (BAR_LENGTH * element.daily.value) / maxX,
          x3: (BAR_LENGTH * element.daily.value) / maxX + 5,
        };
      }

      return res;
    },
  },
  components: { ProfileLogo, Dialog },
};
</script>

<style lang="scss">
$nb-indicators-categories: 5;
$indicators-picto-length: math.div(100%, $nb-indicators-categories);

.day-indicators {
  display: block;
  text-align: center;

  .indicators-title {
    padding: 10px;
    font-size: $op-font-xl;

    .profile-icon {
      display: inline;
      font-size: $op-font-xxl;
      line-height: $op-font-xxl;
      vertical-align: middle;
    }
  }

  .all-recipes-text {
    display: block;
    padding-bottom: 10px;
  }

  .week-indicators-legend {
    text-align: right;
    margin-right: 5px;
  }

  .short-indicators {
    font-size: 14px;
    margin: auto;
    margin-bottom: 50px;
    width: 165px;
    padding-left: 15px;
    .why-calories {
      cursor: pointer;
      &:hover {
        color: $op-color-alert-ok;
      }
    }
    li {
      text-align: left;
      list-style-type: none;
      padding-top: 20px;
      display: table;
      & div {
        display: table-cell;
        vertical-align: middle;
      }

      & > svg {
        font-size: 44px;
        width: 55px;
        margin-right: 10px;
      }
    }
  }
  .why-calories svg {
    cursor: pointer;
    font-size: 14px;
    &:hover {
      color: $op-color-alert-ok;
    }
  }

  #list-nb_indicators {
    text-align: center;
    margin-bottom: 20px;

    .nb_indicators {
      display: inline-block;
      text-align: center;
      padding: 10px;
      margin: 5px 10px;
      width: 150px;
      color: white;
      border-radius: 10px;

      &:hover {
        cursor: pointer;
        opacity: 0.7;
        .fa-search {
          transition: all 0.2s ease-in-out;
          color: black;
        }
        transition: all 0.2s ease-in-out;
      }

      &.category-ok {
        background-color: $op-color-lime;
        .badge {
          color: darken($op-color-lime, 10%);
        }
      }

      &.category-ko {
        background-color: $op-color-red;
        .badge {
          color: darken($op-color-red, 10%);
        }
      }

      &.category-disabledKo {
        background-color: $op-color-orange;
        .badge {
          color: darken($op-color-orange, 10%);
        }
      }

      .indicator-name {
        font-weight: bold;
        font-size: 16px;
        margin: 7px 0px;
      }

      .fa-search {
        font-size: 24px;
      }

      .badge {
        border-radius: 50px;
        background-color: white;
        height: 35px;
        width: 35px;
        padding-top: 9px;
        padding-left: 0;
        padding-right: 0;
        font-size: 18px;
      }
    }
  }
}

.indicators-dialog {
  .dialog-body {
    text-align: left;
  }
  .go-to-my-account-btn {
    display: block;
    margin: auto;
    width: 270px;
  }
  hr {
    border-top: 3px solid #ccc;
  }
  @media (max-width: $bootstrap-sm-min) {
    .modal-dialog {
      width: 95%;
    }
  }
  @media (min-width: $bootstrap-sm-min) {
    .modal-dialog {
      min-width: $bootstrap-sm-min;
    }
  }
  .indicator-group-title {
    background: linear-gradient(to right, $op-color-lime, #fff);
    color: white;
    font-weight: bold;
    font-size: $op-font-xl;
    margin: 0px -15px 30px -15px;
    padding: 7px 15px;
    width: 50%;
  }
  @media (max-width: $bootstrap-sm-min) {
    .indicator-group-title {
      width: 100%;
    }
  }
  .indicator-group:not(:first-of-type) .indicator-group-title {
    margin-top: 50px;
  }
  .indicator-description {
    font-style: italic;
  }

  .read-more-state:checked ~ .read-more-wrap .read-more-target {
    opacity: 1;
    font-size: inherit;
    max-height: 999em;
  }
  .read-more-state {
    display: none;
  }

  .read-more-trigger:before {
    content: "Voir plus";
    font-weight: bold;
  }

  .read-more-target {
    opacity: 0;
    max-height: 0;
    font-size: 0;
    transition: 0.25s ease;
  }

  .read-more-state:checked ~ .read-more-wrap .read-more-trigger {
    display: none;
  }

  .read-more-trigger {
    cursor: pointer;
    display: inline-block;
    padding: 0 0.5em;
    color: #666;
    font-size: 0.9em;
    line-height: 2;
    border: 1px solid #ddd;
    border-radius: 0.25em;
  }

  .pack-can-be-enabled {
    color: $op-color-lime;
  }
  .disabled-unbalanced-what-to-do {
    color: $op-color-red;
  }
  .pack-can-be-enabled,
  .disabled-unbalanced-what-to-do {
    margin-top: 5px;
    font-weight: bold;
  }
  .limit-value {
    font-style: italic;
  }
}

.indicators-dialog .dialog-body {
  text-align: left;
}
</style>
