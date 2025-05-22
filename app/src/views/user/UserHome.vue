<template>
  <div id="userhome-page" class="op-page" v-if="user">
    <div class="userhome-content">
      <!-- Left column -->
      <div class="col-12 col-lg-6">
        <div class="card">
          <div class="card-header">Résumé</div>

          <div class="card-body">
            <!-- Action buttons -->
            <div class="container">
              <div class="row">
                <div class="col-12 col-sm-4 op-vs">
                  <router-link
                    class="op-big-btn btn w-100"
                    :to="{ name: 'Config' }"
                    :class="stageCompletion < 100 ? 'btn-warning' : 'btn-secondary'"
                  >
                    <div class="op-cell-xs op-cell-sm op-row-md op-row-lg">
                      <span class="op-cell-md op-cell-lg op-icon-dlg">
                        <FontAwesomeIcon :icon="['fas', 'user']" />
                      </span>
                    </div>
                    <div class="op-cell-xs op-cell-sm op-row-md op-row-lg">
                      <div class="op-cell-md op-cell-lg">
                        <span class="op-icon-dlg">{{ stageCompletion }}%</span>
                      </div>
                    </div>
                    <div class="op-cell-xs op-cell-sm op-row-md op-row-lg">
                      <div class="op-cell-md op-cell-lg op-font-lg">
                        <span v-if="stageCompletion >= 100"
                          >Profil<br class="d-sm-none" />
                          complété</span
                        >
                        <span v-if="stageCompletion < 100"
                          >Profil<br class="d-sm-none" />
                          incomplet</span
                        >
                        <span class="d-none d-sm-block"><br class="d-block" />&nbsp;</span>
                      </div>
                    </div>
                  </router-link>
                </div>

                <div class="col-12 col-sm-4 op-vs">
                  <router-link
                    class="op-big-btn btn w-100"
                    :to="{ name: 'Calendar', params: { fromDay: planificationStatus.plannedTo || '' } }"
                    :class="getLastPlannedDay < idealLastPlannedDay ? 'btn-warning' : 'btn-secondary'"
                  >
                    <div class="op-cell-xs op-cell-sm op-row-md op-row-lg">
                      <span class="op-cell-md op-cell-lg op-icon-dlg">
                        <FontAwesomeIcon :icon="['fas', 'calendar-alt']" />
                      </span>
                    </div>
                    <div class="op-cell-xs op-cell-sm op-row-md op-row-lg">
                      <div class="op-cell-md op-cell-lg">
                        <span class="op-icon-dlg" v-if="!planificationStatus.plannedTo">--/--</span>
                        <span class="op-icon-dlg" v-if="planificationStatus.plannedTo">{{
                          DateTime.fromFormat(planificationStatus.plannedTo, "yyyy-MM-dd").toFormat("dd/MM")
                        }}</span>
                      </div>
                    </div>
                    <div class="op-cell-xs op-cell-sm op-row-md op-row-lg">
                      <div class="op-cell-md op-cell-lg op-font-lg">
                        <span v-if="!planificationStatus.plannedTo">Aucun jour<br />planifié</span>
                        <span v-if="planificationStatus.plannedTo">Dernier jour<br />planifié</span>
                      </div>
                    </div>
                  </router-link>
                </div>

                <div class="col-12 col-sm-4 op-vs">
                  <router-link
                    class="op-big-btn btn w-100"
                    :to="{ name: 'Shopping' }"
                    :class="availableDays.plannedDates.length > 0 ? 'btn-warning' : 'btn-secondary'"
                  >
                    <div class="op-cell-xs op-cell-sm op-row-md op-row-lg">
                      <span class="op-cell-md op-cell-lg op-icon-dlg">
                        <FontAwesomeIcon :icon="['fas', 'shopping-basket']" />
                      </span>
                    </div>
                    <div class="op-cell-xs op-cell-sm op-row-md op-row-lg">
                      <div class="op-cell-md op-cell-lg">
                        <span class="op-icon-dlg">{{ availableDays.plannedDates.length }}</span>
                      </div>
                    </div>
                    <div class="op-cell-xs op-cell-sm op-row-md op-row-lg">
                      <div class="op-cell-md op-cell-lg op-font-lg">
                        <span v-if="availableDays.plannedDates.length > 1">Jours</span>
                        <span v-if="availableDays.plannedDates.length <= 1">Jour</span>
                        à inclure<br />dans votre liste
                      </div>
                    </div>
                  </router-link>
                </div>
              </div>
            </div>

            <!-- Objective -->
            <div class="userhome-section">
              <h3>
                <FontAwesomeIcon :icon="['fas', 'bullseye']" />
                Votre alimentation
              </h3>
              <div v-show="objective">
                <b>{{ objective.title }}</b>
                <span v-if="ENABLE_DIET_CHOICE">
                  (<router-link :to="{ name: 'MyAccount' }">changer mon alimentation</router-link>)
                </span>
              </div>
              <div v-show="!objective">
                <b>Aucune alimentation sélectionnée</b>
                <span v-if="ENABLE_DIET_CHOICE">
                  (<router-link :to="{ name: 'MyAccount' }">choisir une alimentation</router-link>)
                </span>
              </div>
              Votre IMC : <b>{{ mainProfile?.imc }} </b>
              <span> ({{ imcDescription }})</span>

              <ul class="diet-rule-list">
                <li v-for="rule in DIET_INFOS[objective.key].rules" :key="rule">
                  <FontAwesomeIcon :icon="['fas', 'check']" /> {{ rule }}
                </li>
              </ul>
            </div>

            <!-- Advices -->
            <div class="userhome-section">
              <h3><FontAwesomeIcon :icon="['fas', 'info-circle']" /> Vos conseils personnalisés</h3>
              <ul>
                <li v-for="advice in DIET_INFOS[objective.key].advices" :key="advice">
                  {{ advice }}
                </li>
              </ul>
            </div>

            <!-- Graphics -->
            <div class="userhome-section">
              <h3><FontAwesomeIcon :icon="['fas', 'chart-line']" /> Votre poids</h3>
              <ParameterChart
                v-if="mainProfile"
                :profileId="mainProfile.id"
                metricKey="weight"
                width="100%"
                height="130px"
                :withUpdate="true"
                :minValueDiff="5"
                :allowFloat="true"
                :minValue="10"
                :maxValue="500"
                nbDays="auto"
              />
            </div>

            <!-- Statistics -->
            <div class="userhome-section">
              <h3><FontAwesomeIcon :icon="['fas', 'chart-pie']" /> Vos statistiques</h3>
              <div class="op-raw-table col-md-12">
                <div class="op-raw-row">
                  <div class="op-raw-cell">Nombre de jours planifiés</div>
                  <div class="op-raw-cell userhome-stat-value">{{ userStats?.nbPlannedDays }}</div>
                </div>
                <!-- <div class="op-raw-row">
					 <div class="op-raw-cell">Nombre de recettes cuisinées</div>
					 <div class="op-raw-cell userhome-stat-value">{{ user_stats.cooked_recipes }}</div>
					 </div> -->
                <div class="op-raw-row">
                  <div class="op-raw-cell">Nombre de recettes créées</div>
                  <div class="op-raw-cell userhome-stat-value">{{ userStats?.createdRecipes }}</div>
                </div>
                <div class="op-raw-row">
                  <div class="op-raw-cell">Nombre de recettes publiées</div>
                  <div class="op-raw-cell userhome-stat-value">{{ userStats?.publishedRecipes }}</div>
                </div>
              </div>
            </div>

            <!-- Meal sharing -->
            <div class="userhome-section" v-if="profiles && profiles.length > 1">
              <h3><FontAwesomeIcon :icon="['fas', 'utensils']" /> Qui mange quoi ?</h3>
              Pour chaque plat préparé, voici les proportions à respecter.<br /><br />
              <RatioPieChart width="100%" height="215px" />
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- userhome-content -->
  </div>
</template>

<script>
import { ENABLE_DIET_CHOICE } from "@/config.js";
import { DIET_INFOS } from "@/common/static.js";
import { addDays, stringToDate } from "@/common/dates.js";
import { DateTime } from "luxon";
import { mapGetters } from "vuex";
import ParameterChart from "@/components/objective/ParameterChart.vue";
import RatioPieChart from "@/components/user/RatioPieChart.vue";

/*
 * View for user home page
 */
export default {
  name: "UserHome",
  props: [],
  data: () => ({
    ENABLE_DIET_CHOICE,
    DIET_INFOS,
    idealLastPlannedDay: addDays(new Date(), 1),
    userStats: null,
    DateTime,
  }),
  mounted() {
    this.$store.dispatch("user/getStats").then((userStats) => {
      this.userStats = userStats;
    });
  },
  computed: {
    user() {
      return this.$store.getters["user/get"];
    },
    objective() {
      if (!this.user) {
        return null;
      }
      return this.$store.getters["user/get"].objective;
    },
    stageCompletion() {
      if (!this.user) {
        return null;
      }
      return this.$store.getters["configStage/getStats"].completion;
    },
    getLastPlannedDay() {
      if (!this.user) {
        return null;
      }
      if (!this.planificationStatus || !this.planificationStatus.plannedTo) {
        return undefined;
      }
      return stringToDate(this.planificationStatus.plannedTo);
    },
    imcDescription() {
      if (!this.user) {
        return null;
      }
      const imc = this.mainProfile?.imc;
      if (!imc) return "";
      if (imc < 18.5) return "maigreur";
      else if (imc >= 18.5 && imc <= 25) return "normal";
      else return "surpoids";
    },
    ...mapGetters({
      profiles: "profile/getProfiles",
      mainProfile: "profile/getMainProfile",
      planificationStatus: "planning/getPlanificationStatus",
      availableDays: "shopping/getAvailableDays",
    }),
  },
  methods: {},
  components: { ParameterChart, RatioPieChart },
};
</script>

<style scoped lang="scss">
#userhome-page {
  .userhome-content {
    margin: auto;
    height: 100%;
    width: 100%;
    min-height: 500px;
    position: relative;

    &:after {
      @extend .clearfix;
    }
  }

  .card-header {
    font-size: 16px;
  }

  .userhome-section {
    width: 100%;
    clear: both;
    padding: 15px;

    h3 {
      margin-top: 10px;
      display: flex;
      align-items: center;
      svg {
        margin-right: 7px;
      }
    }
    ul {
      padding-left: 20px;
    }
    &:after {
      @extend .clearfix;
    }
  }

  .userhome-poll {
    padding: 0;
    .card {
      border: none;
    }
  }

  .userhome-section + .userhome-section {
    border-top: $op-page-content-border-width solid $op-color-border;
    margin-top: 5px;
  }

  .diet-rule-list {
    padding-top: 10px;
    padding-left: 4px !important;
    list-style-type: none;

    li > svg {
      padding-right: 1px;
    }
  }

  .userhome-stat-value {
    font-weight: bold;
  }

  .card-body {
    padding: 0px;
  }
}
</style>
