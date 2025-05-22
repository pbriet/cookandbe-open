<template>
  <div class="op-page">
    <div class="op-page-title">
      <h1>Emploi du temps</h1>
    </div>
    <ConfigProgression />
    <div class="op-page-content">
      <div id="op-profile-attendance-page">
        <div class="op-info">
          <span class="info-icon">
            <FontAwesomeIcon :icon="['fas', 'home']" />
          </span>
          <p>{{ APP_BRAND_NAME }} vous suggérera uniquement les repas que vous prenez à la maison.</p>
          <p>
            Les apports nutritionnels et quantités seront adaptés au nombre de repas, et à ce que vous mangez à
            l'extérieur.
          </p>
        </div>

        <div class="alert alert-danger" v-if="hasLessThanTwoMeals">
          <span class="alert-icon">
            <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" />
          </span>
          <p>Vous devez manger au moins 2 repas par jour pour pouvoir utiliser l'application.</p>
          <p>
            Si vous souhaitez que certains repas ne soient pas gérés par {{ APP_BRAND_NAME }}, choisissez simplement
            Sandwich, Restaurant ou Self.
          </p>
        </div>

        <ul class="nav nav-pills d-none d-sm-block" id="view-switcher">
          <li :class="{ active: columns.length < 3 }" @click="onSwitchView('weeksplit')">
            <a>Configuration semaine / weekend</a>
          </li>
          <li :class="{ active: columns.length > 3 }" @click="onSwitchView('daily')">
            <a>Configuration jour par jour</a>
          </li>
        </ul>

        <div class="diabete-alert op-vs-10" v-if="diabeteSnackAlert">
          En mode "diabète", les goûters et collations doivent être pris sur l'ensemble de la semaine, ou pas du
          tout.<br />
          Il est important de maintenir une régularité quotidienne dans vos apports.
        </div>

        <!-- Attendance editor popup  -->
        <Dialog id="attendance-editor" :onClose="hideAttendanceEditor" :closeBtn="true" :open="openEditor">
          <AttendanceEditor
            v-if="selected"
            :selectedMeal="selected.meal"
            :selectedColumn="selected.column"
            :allowDoNotEat="selected.allowDoNotEat"
            :changeAttendanceFcn="onChangeAttendance"
          />
        </Dialog>

        <div id="attendances-section">
          <table class="profile-attendances">
            <tr>
              <th></th>
              <th v-for="column in columns" :key="column.name" class="day_title">
                {{ column.name }}
              </th>
            </tr>
            <tr v-for="attendancesMeal in attendancesViewData" :key="attendancesMeal.meal.id">
              <td class="meal-name">{{ attendancesMeal.meal.name }}</td>
              <td
                v-for="attendance in attendancesMeal.days"
                :key="attendance.column"
                class="meal-attendance"
                @click="showAttendanceEditor(attendancesMeal.meal, attendance.column, attendance.places)"
              >
                <div v-for="place in attendance.places" :key="place">
                  <img
                    :src="placeImg(PLACES[place].img)"
                    :class="{ 'multiple-attendance-image': attendance.places.length > 1 }"
                  />
                </div>
              </td>
            </tr>
          </table>
        </div>
        <!--!attendances-section-->

        <div id="attendances-legend" class="op-info d-none d-sm-inline-block" v-if="columns.length <= 2">
          Légende :
          <table>
            <tr v-for="place in PLACES" :key="place.label">
              <td>
                <img :src="placeImg(place.img)" />
              </td>
              <td>
                {{ place.label }}
              </td>
            </tr>
          </table>
        </div>
      </div>
    </div>
    <!-- profile-attendance content -->
    <ConfigToolbar />
  </div>
  <!-- profile-attendance page -->
</template>

<script>
import { APP_BRAND_NAME } from "@/config.js";
import { mapGetters } from "vuex";
import API from "@/api.js";
import { PLACES } from "@/common/static.js";
import ConfigProgression from "@/components/config/ConfigProgression.vue";
import ConfigToolbar from "@/components/config/ConfigToolbar.vue";
import Dialog from "@/components/interface/Dialog.vue";
import AttendanceEditor from "@/components/config/AttendanceEditor.vue";

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

/*
 * View for displaying profile attendances
 */
export default {
  name: "AttendanceConfig",
  props: [],
  data: () => ({
    PLACES,
    APP_BRAND_NAME,
    hasLessThanTwoMeals: false,
    diabeteSnackAlert: false,
    attendances: null,
    columns: [],
    attendancesViewData: [],
    selected: null,
    openEditor: false,
  }),
  mounted() {
    this.reloadAttendances();
  },
  computed: {
    ...mapGetters({
      user: "user/get",
    }),
    withDiabete() {
      return this.user.objective.key === "diabete";
    },
  },
  methods: {
    // Reload the user current DB attendances
    async reloadAttendances() {
      const data = await API.profileAttendance.get(this.user.mainProfileId);
      this.selectBestViewMode(data);
    },
    // Display the modal attendance editor
    showAttendanceEditor(meal, column) {
      let shouldEat = meal.name === "Déjeuner" || meal.name === "Dîner";

      if (meal.name === "Petit déjeuner" && this.withDiabete) {
        shouldEat = true;
      }

      this.selected = { meal, column, allowDoNotEat: !shouldEat };
      this.openEditor = true;
    },
    hideAttendanceEditor() {
      this.openEditor = false;
    },
    // Called by the modal attendance editor to change attendances
    onChangeAttendance(meal, column, attendance) {
      // Ferme le popup
      this.openEditor = false;
      if (this.withDiabete && (meal.name === "Collation" || meal.name === "Goûter")) {
        // With diabete, cannot vary meals during the week
        // Modifications affect all the days
        column = { ...column };
        column.indexes = [0, 1, 2, 3, 4, 5, 6];
        this.diabeteSnackAlert = true;
      }
      // Itère sur tous les jours concernés
      for (let index = 0; index < column.indexes.length; ++index) {
        const dayIndex = column.indexes[index];

        // Si changement, mise à jour en local et signalement à l'interface de sauvegarde
        if (this.attendances["days"][dayIndex][meal.id] != attendance.key) {
          this.attendances["days"][dayIndex][meal.id] = attendance.key;
        }
      }
      // Rafraichissement de la vue
      this.buildAttendancesView(true);
      this.resetMealDayCount();
    },
    save() {
      if (this.hasLessThanTwoMeals) {
        if (!window.confirm("Vous avez parfois moins de 2 repas par jour. Voulez-vous annuler les modifications ?")) {
          return false;
        }
        return true;
      }

      API.profileAttendance.update(this.user.mainProfileId, this.attendances).then(() => {
        this.$store.dispatch("configStage/complete", { stageName: "attendance" });
        this.$store.dispatch("profile/update");
      });
      return true;
    },
    onSwitchView(viewMode) {
      this.setColumns(viewMode);
      this.buildAttendancesView(true);
    },
    setColumns(viewMode) {
      if (viewMode == "daily") {
        this.columns = [ALL_DAYS, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY];
      } else if (viewMode == "weeksplit") {
        this.columns = [WEEK, WEEKEND];
      } else {
        console.log("Uh oh, you shouldn't be here (AttendanceConfig.vue)");
      }
    },
    // From attendances, builds weeksplit / daily view
    buildAttendancesView(applyImmediately) {
      const weekAttendances = [];
      // default to true
      applyImmediately = typeof applyImmediately !== "boolean" ? applyImmediately : true;
      // Iter over meals
      for (let mealIndex = 0; mealIndex < this.attendances["meals"].length; ++mealIndex) {
        const meal = this.attendances["meals"][mealIndex];
        const dayAttendances = [];

        // Iter over displayed columns
        for (let columnIndex = 0; columnIndex < this.columns.length; ++columnIndex) {
          const column = this.columns[columnIndex];
          const mealPlaces = {};

          // Iter over associated attendances
          for (let index = 0; index < column.indexes.length; ++index) {
            const dayIndex = column.indexes[index];
            const attendanceKey = this.attendances["days"][dayIndex][meal.id];

            if (attendanceKey in mealPlaces) {
              mealPlaces[attendanceKey] += 1;
            } else {
              mealPlaces[attendanceKey] = 1;
            }
          }
          dayAttendances.push({ column, places: Object.keys(mealPlaces) });
        }
        weekAttendances.push({ meal, days: dayAttendances });
      }
      if (applyImmediately === true) {
        this.attendancesViewData = weekAttendances;
      }
      return weekAttendances;
    },
    resetMealDayCount() {
      this.hasLessThanTwoMeals = false;
      if (!this.attendancesViewData || !this.attendancesViewData.length) {
        return;
      }
      for (let dayIndex = 0; dayIndex < this.attendances["days"].length; ++dayIndex) {
        let mealDayCount = 0;

        for (let mealIndex = 0; mealIndex < this.attendancesViewData.length; ++mealIndex) {
          const meal = this.attendances["meals"][mealIndex];

          if (this.attendances["days"][dayIndex][meal.id] != "donoteat") {
            mealDayCount += 1;
          }
        }
        if (mealDayCount < 2) {
          this.hasLessThanTwoMeals = true;
          break;
        }
      }
    },
    // Select the view mode displaying less conflicted places
    selectBestViewMode(data) {
      let conflicts = 0;
      this.attendances = data;

      // Checking weeksplit first
      this.setColumns("weeksplit");
      let weekAttendances = this.buildAttendancesView(false);
      for (let mealIndex = 0; mealIndex < weekAttendances.length; ++mealIndex) {
        for (let dayIndex = 0; dayIndex < weekAttendances[mealIndex].days.length; ++dayIndex) {
          if (weekAttendances[mealIndex].days[dayIndex].places.length > 1) {
            conflicts += 1;
          }
        }
      }
      // Choosing view_mode according to conflicts number
      if (conflicts > 0) {
        this.setColumns("daily");
        weekAttendances = this.buildAttendancesView(false);
      }
      this.attendancesViewData = weekAttendances;
      this.resetMealDayCount();
    },
    placeImg(place) {
      return require(`@/assets/img/${place}`);
    },
  },
  beforeRouteLeave(to, from, next) {
    if (this.save()) {
      next();
    }
  },
  components: { ConfigProgression, ConfigToolbar, AttendanceEditor, Dialog },
};
</script>

<style lang="scss">
#op-profile-attendance-page {
  .attendance-editor-title {
    font-weight: bold;
  }

  .diabete-alert {
    color: $op-color-alert-danger;
  }

  #attendances-infos {
    margin: 20px;
  }

  .attendance-editor-infos {
    padding: 15px;
  }

  .attendance-editor-icon {
    width: 32px;
  }

  .attendance-editor-place {
    padding: 10px;
  }

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

  .attendance-editor-button {
    float: left;
    margin: 5px;
    width: 250px;
    text-align: left;
    position: relative;
  }

  .profile-attendances {
    clear: both;
    margin: 20px;
    border-collapse: collapse;
    td {
      border: $op-page-content-border-width solid $op-color-border;
    }
    th {
      text-align: center;
    }
    .meal-single-attendance-image {
      width: 32px;
    }
    .meal-multiple-attendance-image {
      width: 16px;
    }
    .meal-name {
      font-weight: bold;
      padding: 20px;
    }
    .meal-attendance {
      padding: 10px;
      font-size: $op-font-md;
      width: 90px;
      vertical-align: middle;
      text-align: center;
      img {
        width: 32px;
      }
      .multiple-attendance-image {
        width: 16px;
        margin-left: 12%;
        margin-right: 12%;
        float: left;
      }
    }
    .meal-attendance:hover {
      background-color: $op-color-lime;
      color: white;
      cursor: pointer;
    }
  }

  #attendances-section {
    display: inline-block;
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
