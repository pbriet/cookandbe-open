<template>
  <div id="op-main-config-page" class="op-page">
    <div class="op-page-title">
      <h1>Mon profil</h1>
    </div>

    <div class="op-page-content">
      <div class="row" v-if="configStats.completion < 100" id="profile-completion-section">
        <div class="col-12 text-center">
          <CircleChart displayMode="percentage" :percent="configStats.completion">
            <b>
              <FontAwesomeIcon :icon="['fas', 'user']" />
              <span v-if="configStats.completion < 60"> Profil incomplet</span>
              <span v-if="configStats.completion >= 60"> Profil presque complet !</span>
            </b>
          </CircleChart>
          <div class="please-complete-text">
            Configurez davantage votre profil pour obtenir des suggestions de repas vraiment sur mesure !
          </div>
        </div>
      </div>

      <div class="row row-cols-2">
        <div v-for="stage in configStages" class="config_stage col-12 col-sm-6" :key="stage.order">
          <div class="text-center op-vs-20">
            <h2 class="d-flex align-items-center justify-content-center">
              <span v-if="stage.status === 'filled'" class="filled-section pb-1 pe-1">
                <FontAwesomeIcon :icon="['fas', 'check']" />
              </span>
              <span v-if="stage.status !== 'filled'" class="pe-1">
                <span class="badge">!</span>
              </span>
              {{ stage.name }}
            </h2>
            {{ stage.description }}
            <br /><br />
            <router-link class="op-big-btn btn btn-secondary" :to="`/config/${stage.key}/`">
              <span class="op-icon-dlg">
                <FontAwesomeIcon :icon="stagesIcons[stage.key]" />
              </span>
              <span v-if="stage.status === 'filled'"> Modifier </span>
              <span v-if="stage.status !== 'filled'"> Compléter </span>
            </router-link>
            <!-- op-big-btn -->
          </div>
          <!-- col-12 -->
        </div>
        <!-- stage -->
      </div>
      <!-- row -->
    </div>
    <!-- Objective content -->
  </div>
  <!-- Objective page -->
</template>

<script>
import { mapGetters } from "vuex";
import { orderBy } from "lodash";
import { CONFIG_STAGE_ICONS } from "@/common/static.js";
import CircleChart from "@/components/interface/CircleChart.vue";

/*
 * View for config main page
 */
export default {
  name: "Config",
  props: [],
  data: () => ({
    stagesIcons: CONFIG_STAGE_ICONS,
  }),
  computed: {
    ...mapGetters({
      configStats: "configStage/getStats",
    }),
    configStages() {
      return orderBy(this.$store.getters["configStage/getStages"], "order");
    },
  },
  components: { CircleChart },
};
</script>

<style scoped lang="scss">
#op-main-config-page {
  #profile-completion-section {
    b {
      font-size: $op-font-lg;
      padding-bottom: 5px;
      padding-top: 5px;
      display: block;
    }
    padding-bottom: 30px;
  }

  h2 {
    border-bottom: 1px solid $op-color-border;
  }
  .filled-section {
    color: $op-color-lime;
  }
  .badge {
    background-color: $op-color-notification-bg;
    font-size: $op-font-xl;
    line-height: $op-font-xl;
    padding: 3px 10px;
    vertical-align: top;
    margin-top: 5px;
    border-radius: 20px;
    font-weight: normal;
  }
  .not-filled-section {
    color: $op-color-red;
  }
  .config_stage {
    display: inline;
  }

  .op-big-btn {
    height: 50px;
    line-height: 50px;
    width: 190px;
    margin: auto;
    span {
      vertical-align: middle;
    }
    svg {
      padding-right: 5px;
    }
  }
}
</style>
