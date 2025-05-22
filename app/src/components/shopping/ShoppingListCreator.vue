<template>
  <div class="op-shopping-list-creator">
    <h3 class="dialog-title" v-if="availableDays.plannedDates.length === 0">
      <FontAwesomeIcon :icon="['fas', 'info-circle']" /> Vous n'avez aucun jour planifié
    </h3>
    <h3 class="dialog-title" v-if="availableDays.plannedDates.length > 0">
      <FontAwesomeIcon :icon="['fas', 'plus']" /> Nouvelle liste de courses
    </h3>
    <div class="dialog-body">
      <div>
        <div v-if="!availableDays.plannedDates.length > 0">
          <!-- <h3 class="col-12 op-vs"><FontAwesomeIcon :icon="['fas', 'info-circle']" /> Vous n'avez aucun jour planifié</h3> -->

          <p class="col-12">Pour créer une liste de courses, planifiez de nouvelles journées !</p>

          <div class="col-12 op-vs">
            <div class="fright">
              <router-link class="btn btn-success" :to="{ name: 'Calendar', params: { fromDay: getLastPlannedDay } }">
                <FontAwesomeIcon :icon="['fas', 'calendar-alt']" /> Planifier mes repas
              </router-link>
            </div>
          </div>
        </div>

        <div v-if="availableDays.plannedDates.length > 0">
          <div class="row">
            <div class="op-font-lg col-4">De</div>
            <div class="op-font-lg col-8">
              <DateChoice
                v-model="selectedDates.startDate"
                :minDate="availableDays.startDate"
                :maxDate="selectedDates.endDate"
              />
            </div>
          </div>
          <div class="row">
            <div class="op-font-lg col-4">Jusqu'à</div>
            <div class="op-font-lg col-8">
              <DateChoice
                v-model="selectedDates.endDate"
                :minDate="selectedDates.startDate"
                :maxDate="availableDays.endDate"
              />
            </div>
          </div>

          <div class="row justify-content-end op-vs" v-if="!warnOneDay || getNbDaysSelection > 1">
            <div class="col-12 col-sm-4 op-vs-5" v-if="onCancel">
              <button class="col-12 btn btn-secondary" @click="cancelShoppingList">Annuler</button>
            </div>
            <div class="col-12 col-sm-8 op-vs-5">
              <button class="container-fluid btn btn-success btn-block" @click="createShoppingList">
                Créer ma liste ({{ getNbDaysSelection }} jour<span v-if="getNbDaysSelection > 1">s</span>)
              </button>
            </div>
          </div>

          <div class="op-vs" v-if="getNbDaysSelection == 1 && warnOneDay">
            <div class="alert alert-warning">
              <h4>Vous n'avez planifié qu'un seul jour</h4>
              Ajoutez d'autre jours, et créez une seule liste de courses
              <div class="row justify-content-end">
                <div class="col-12 col-sm-4 op-vs-10">
                  <button class="container-fluid btn btn-warning btn-block" @click="createShoppingList">
                    Créer ma liste
                  </button>
                </div>
                <div class="col-12 col-sm-8 op-vs-10" v-if="onCancel">
                  <button class="col-12 btn btn-secondary" @click="cancelShoppingList">
                    Continuer la planification
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <span class="clearfix" />

        <div class="alert alert-danger" v-if="errorMessage">
          {{ errorMessage }}
        </div>
      </div>
    </div>
    <span class="clearfix" />
  </div>
</template>

<script>
import DateChoice from "@/components/interface/DateChoice.vue";
import API from "@/api.js";
import { addDays, dateDaysDifference } from "@/common/dates.js";
import { mapGetters } from "vuex";

const SHOPPING_ERROR_MESSAGE = {
  contains_days_in_shopping_list:
    "Impossible de créer une liste qui en inclut une autre.\nSupprimez la liste existante avant, ou bien modifiez les dates.",
};

export default {
  name: "ShoppingListCreator",
  props: ["onCancel", "warnOneDay"],
  data() {
    return {
      selectedDates: {},
      errorMessage: "",
    };
  },
  mounted() {
    this.onAvailableDaysChange();
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
      availableDays: "shopping/getAvailableDays",
      planificationStatus: "planning/getPlanificationStatus",
    }),
    getLastPlannedDay() {
      if (!this.planificationStatus || !this.planificationStatus.suggestedTo) {
        return addDays(new Date(), 1).toDateString();
      }
      return this.planificationStatus.suggestedTo;
    },
    getNbDaysSelection() {
      return dateDaysDifference(this.selectedDates.endDate, this.selectedDates.startDate) + 1;
    },
  },
  watch: {
    availableDays: {
      handler() {
        this.onAvailableDaysChange();
      },
      deep: true,
    },
  },
  methods: {
    cancelShoppingList() {
      this.onCancel();
    },
    onAvailableDaysChange() {
      if (this.availableDays.startDate) {
        Object.assign(this.selectedDates, this.availableDays);
      }
    },
    async createShoppingList() {
      this.errorMessage = "";
      const data = await API.shoppingList.buildNew(this.userId, {
        startDate: this.selectedDates.startDate.toDateString(),
        endDate: this.selectedDates.endDate.toDateString(),
      });
      if (data.status === "failed") {
        this.errorMessage = SHOPPING_ERROR_MESSAGE[data.error];
        return;
      }
      this.$store.dispatch("shopping/update");
      this.$router.push({ name: "ShoppingListContent", params: { shoppingListId: data.shoppingListId } });
    },
  },
  components: { DateChoice },
};
</script>

<style scoped lang="scss">
.op-shopping-list-creator {
  .alert {
    margin-bottom: 0px;
    margin-top: 20px;
  }
}
</style>
