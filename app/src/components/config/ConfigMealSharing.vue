<template>
  <div id="op-presence-page" v-if="profiles.length > 1">
    <h2>Partage des repas</h2>

    <div>
      <ul class="nav nav-pills d-none d-sm-block" id="view-switcher">
        <li :class="{ active: columns.length < 3 }" @click.prevent="onSwitchView('weeksplit')">
          <a>Configuration semaine / weekend</a>
        </li>
        <li :class="{ active: columns.length >= 3 }" @click.prevent="onSwitchView('daily')">
          <a>Configuration jour par jour</a>
        </li>
      </ul>

      <div id="presences-section">
        <table class="profile-presences">
          <tr>
            <th></th>
            <th v-for="column in columns" :key="column.name" class="day_title">
              {{ column.name }}
            </th>
          </tr>
          <tr v-for="presencesMeal in presencesViewData" :key="presencesMeal.meal.id">
            <td class="meal-name">{{ presencesMeal.meal.name }}</td>
            <td v-for="presencesDay in presencesMeal.days" class="meal-presence" :key="presencesDay">
              <table>
                <tr
                  v-for="eater in presencesDay.presences"
                  :key="eater.key"
                  :class="{ 'main-meal-presence-eater': eater.isMain, 'external-meal-presence-eater': !eater.isMain }"
                  @click="togglePresence(presencesMeal.meal, presencesDay, eater)"
                >
                  <td><img :src="eaterImg(eater)" /></td>
                  <td>{{ eater.name }}</td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </div>
      <!--!presences-section-->

      <div id="attendances-legend" class="op-info d-none d-sm-inline-block" v-if="columns.length <= 2">
        Légende :
        <table>
          <tr v-for="legendElt in EATER_LEGEND" :key="legendElt.img">
            <td>
              <img :src="legendImg(legendElt)" :style="legendElt.style" />
            </td>
            <td>
              {{ legendElt.caption }}
            </td>
          </tr>
        </table>
      </div>
    </div>
    <!-- if profiles.length > 1 -->
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { size } from "lodash";
import API from "@/api.js";

// Some labels
const ALL_DAYS = { name: "Tous les jours", indexes: [0, 1, 2, 3, 4, 5, 6] };
const MONDAY = { name: "Lundi", indexes: [0] };
const TUESDAY = { name: "Mardi", indexes: [1] };
const WEDNESDAY = { name: "Mercredi", indexes: [2] };
const THURSDAY = { name: "Jeudi", indexes: [3] };
const FRIDAY = { name: "Vendredi", indexes: [4] };
const SATURDAY = { name: "Samedi", indexes: [5] };
const SUNDAY = { name: "Dimanche", indexes: [6] };
const WEEK = { name: "En semaine", indexes: [0, 1, 2, 3, 4] };
const WEEKEND = { name: "Le weekend", indexes: [5, 6] };

export default {
  name: "ConfigMealSharing",
  props: ["profiles"],
  data: () => ({
    EATER_LEGEND: [
      { img: "home", style: { opacity: 0.6 }, caption: "Vous-même" },
      { img: "home", caption: "Partage le repas avec vous" },
      { img: "donoteat", caption: "Ne participe pas au repas" },
    ],
    columns: [],
    dbHomePresences: null,
    presences: null,
    presencesViewData: [],
  }),
  mounted() {
    this.reloadHomePresences();
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
      user: "user/get",
    }),
  },
  watch: {
    profiles() {
      this.reloadHomePresences();
    },
  },
  methods: {
    onSwitchView(viewMode) {
      this.setColumns(viewMode);
      this.buildPresencesView(true);
    },
    setColumns(viewMode) {
      if (viewMode == "daily") {
        this.columns = [ALL_DAYS, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY];
      } else if (viewMode == "weeksplit") {
        this.columns = [WEEK, WEEKEND];
      } else {
        console.log("Uh oh, you shouldn't be here (ConfigMealSharing.vue)");
      }
    },
    save() {
      API.mealSharing.update(this.user.metaPlanningId, this.presences);
    },
    // From presences, builds weeksplit / daily view
    buildPresencesView(applyImmediately) {
      const weekPresences = [];
      // default to true
      applyImmediately = typeof applyImmediately !== "boolean" ? applyImmediately : true;
      // Iter over meals
      for (let mealIndex = 0; mealIndex < this.presences["meals"].length; ++mealIndex) {
        const meal = this.presences["meals"][mealIndex];
        const dayPresences = [];
        let mealEmpty = true;

        // Iter over displayed columns
        for (let columnIndex = 0; columnIndex < this.columns.length; ++columnIndex) {
          const column = this.columns[columnIndex];
          const mealPresence = [];

          // Iter over eaters
          for (let eaterIndex = 0; eaterIndex < this.presences["eaters"].length; ++eaterIndex) {
            const eater = this.presences["eaters"][eaterIndex];
            const eaterPresence = {};

            // Iter over associated presences
            for (let index = 0; index < column.indexes.length; ++index) {
              const dayIndex = column.indexes[index];
              const mealEaters = this.presences["days"][dayIndex][meal.id];

              // No eater at this meal this day
              if (mealEaters === undefined || !(eater.profileId in mealEaters)) {
                continue;
              }

              const presenceKey = mealEaters[eater.profileId];

              if (presenceKey in eaterPresence) {
                eaterPresence[presenceKey] += 1;
              } else {
                eaterPresence[presenceKey] = 1;
              }
            }
            // Counting presences to detect conflicts
            if (size(eaterPresence) === 0) {
              continue;
            } else {
              const eaterDetails = { profileId: eater.profileId, name: eater.name, isMain: eater.isMain };
              if (size(eaterPresence) === 1) {
                eaterDetails.key = Object.keys(eaterPresence)[0];
              } else {
                eaterDetails.key = "conflict";
              }
              mealPresence.push(eaterDetails);
            }
            mealEmpty = false;
          }
          dayPresences.push({ column, presences: mealPresence });
        }
        // Suppression des lignes vides
        if (!mealEmpty) {
          weekPresences.push({ meal, days: dayPresences });
        }
      }
      if (applyImmediately === true) {
        this.presencesViewData = weekPresences;
      }
      return weekPresences;
    },
    // Select the view mode displaying less conflicted places
    selectBestViewMode(data) {
      this.dbHomePresences = data;
      this.presences = this.dbHomePresences;
      let conflicts = 0;
      // Checking weeksplit first
      this.setColumns("weeksplit");
      let weekPresences = this.buildPresencesView(false);
      for (let mealIndex = 0; mealIndex < weekPresences.length; ++mealIndex) {
        for (let dayIndex = 0; dayIndex < weekPresences[mealIndex].days.length; ++dayIndex) {
          for (
            let eaterIndex = 0;
            eaterIndex < weekPresences[mealIndex].days[dayIndex].presences.length;
            ++eaterIndex
          ) {
            if (weekPresences[mealIndex].days[dayIndex].presences[eaterIndex].key == "conflict") {
              conflicts += 1;
            }
          }
        }
      }
      // Choosing view_mode according to conflicts number
      if (conflicts > 0) {
        this.setColumns("daily");
        weekPresences = this.buildPresencesView(false);
      }
      this.presencesViewData = weekPresences;
    },
    // Reload the user current DB presences
    async reloadHomePresences() {
      const data = await API.mealSharing.get(this.user.metaPlanningId);
      this.selectBestViewMode(data);
    },
    // Toggle eater presence
    togglePresence(meal, presencesDay, eater) {
      if (eater.isMain) {
        return;
      }
      let newPresence = "donoteat";
      if (eater.key == "donoteat" || eater.key == "conflict") {
        newPresence = "home";
      }
      // Itère sur tous les jours concernés
      for (let index = 0; index < presencesDay.column.indexes.length; ++index) {
        const dayIndex = presencesDay.column.indexes[index];

        // Filtre sur les colonnes avec repas
        if (this.presences["days"][dayIndex][meal.id] !== undefined) {
          this.presences["days"][dayIndex][meal.id][eater.profileId] = newPresence;
        }
      }
      // Rafraichissement de la vue
      this.buildPresencesView(true);
    },
    eaterImg(eater) {
      return require(`@/assets/img/presence_${eater.key}.png`);
    },
    legendImg(legendElt) {
      return require(`@/assets/img/presence_${legendElt.img}.png`);
    },
  },
  components: {},
};
</script>

<style scoped lang="scss">
#op-presence-page {
  .nav-pills {
    li {
      display: block;
      float: left;
      margin-right: 2px;
      a {
        color: $op-color-text-main;
        border: $op-page-content-border-width solid $op-color-border;
        position: relative;
        display: block;
        padding: 10px 15px;
        border-radius: 4px;
      }
    }
    li.active a,
    a:focus,
    a:hover {
      background-color: $op-color-lime;
      color: white;
    }
    &:after {
      @extend .clearfix;
    }
  }

  #presences-section {
    display: inline-block;
  }

  .profile-presences {
    clear: both;
    border-collapse: collapse;

    td {
      border: $op-page-content-border-width solid $op-color-border;
    }
    th {
      text-align: center;
    }
    .meal-name {
      font-weight: bold;
      padding: 10px;
    }
  }

  .meal-presence {
    padding: 5px;
    font-size: $op-font-md;
    width: 90px;
    vertical-align: middle;
    text-align: center;
    table {
      width: 100%;
    }
    td {
      border: 0px;
      text-align: left;
      margin: 5px;
      padding: 5px;
    }
    img {
      width: 24px;
    }
  }

  .external-meal-presence-eater:hover {
    cursor: pointer;
    background-color: $op-color-lime;
    color: white;
  }

  .main-meal-presence-eater {
    img {
      opacity: 0.6;
    }
    &:hover {
      background-color: none;
      color: default;
      cursor: default;
    }
  }

  .nav {
    margin-bottom: 10px;
  }

  #attendances-legend {
    display: inline-block;
    clear: none;
    width: auto;
    padding: 10px;
    vertical-align: bottom;
    margin-bottom: 26px;
    margin-left: 50px;

    td {
      padding-bottom: 2px;
    }
    img {
      margin-right: 5px;
    }
  }
}
</style>
