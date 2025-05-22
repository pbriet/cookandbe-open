<template>
  <Dialog
    ref="dietDetailsDialog"
    :open="showDietDetails"
    :closeBtn="true"
    :onClose="onCloseDetailsDialog"
    maxWidth="750px"
  >
    <div class="dialog-title">{{ selectedDiet?.title }}</div>
    <div class="dialog-body op-diet-page" v-if="selectedDiet">
      <DietDetails :diet="selectedDiet.key" />

      <div class="op-vs w-100 d-flex pe-4">
        <button class="btn btn-success ms-auto col-6 col-sm-4 col-md-3" @click="onCloseDetailsDialog">Ok</button>
      </div>
    </div>
  </Dialog>

  <div class="op-diet-selector">
    <div v-if="!hasSelectedDiet">
      <div v-if="!linkMode">
        <button
          class="btn btn-secondary op-font-xl op-diet-btn"
          v-for="diet in displayedDiets"
          :key="diet.key"
          v-show="!subscriptionLevelLimit || diet.minSubscriptionLevel <= subscriptionLevelLimit"
          @click="onSelectDiet(diet)"
        >
          <div class="op-diet-img">
            <img :src="dietImage(diet)" />
          </div>
          <h3 class="op-diet-title" :class="{ 'op-diet-title-beta': !diet.enabled }">
            Menu {{ diet.title.toLowerCase() }}
            <div class="op-font-xl" v-if="!diet.enabled">
              <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" />
              Beta
            </div>
          </h3>
        </button>
      </div>
      <div v-if="linkMode">
        <router-link
          class="btn btn-secondary op-font-xl op-diet-btn"
          v-for="diet in displayedDiets"
          :key="diet.key"
          v-show="!subscriptionLevelLimit || diet.minSubscriptionLevel <= subscriptionLevelLimit"
          :to="`/menus/${diet.urlKey}`"
        >
          <div class="op-diet-img">
            <img :src="dietImage(diet)" />
          </div>
          <h3 class="op-diet-title">
            Menu {{ diet.title.toLowerCase() }}
            <div class="op-font-red op-font-xl" v-if="!diet.enabled">
              <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" /> Beta
            </div>
            &nbsp; <FontAwesomeIcon :icon="['fas', 'chevron-right']" />
          </h3>
        </router-link>
      </div>

      <span class="clearfix" />

      <div class="col-12" v-if="displayShowMore">
        <a href="" class="btn btn-secondary fright" @click.prevent="showMoreClick">
          <FontAwesomeIcon :icon="['fas', 'plus']" /> Voir plus de menus
        </a>
      </div>

      <span class="clearfix" />
    </div>

    <div v-if="hasSelectedDiet" class="row px-3">
      <div class="col-12 col-sm-7 col-md-5 op-font-xl op-diet-card">
        <div class="op-diet-img">
          <img :src="dietImage(selectedDiet)" />
        </div>
        <div class="op-diet-title">{{ selectedDiet.title }}</div>
      </div>

      <div class="col-12 col-sm-5 col-md-7 op-vs fright op-diet-advantages ms-auto">
        <h4 class="op-vs-5">"{{ selectedDiet.title }}", c'est :</h4>

        <DietSummary :diet="selectedDiet.key" />

        <a class="col-12 op-vs" @click.prevent="showMoreInfos">
          <FontAwesomeIcon :icon="['fas', 'info-circle']" /> Envie de plus d'informations ? Cliquez ici !
        </a>

        <span class="clearfix" />
      </div>
    </div>
  </div>
</template>

<script>
import Dialog from "@/components/interface/Dialog.vue";
import DietDetails from "@/components/objective/diets/DietDetails.vue";
import DietSummary from "@/components/objective/diets/DietSummary.vue";

export default {
  name: "DietSelector",
  props: [
    "diets",
    "selectedDiet",
    "subscriptionLevelLimit",
    "linkMode", // Prevent normal selection action by moving to diet page
  ],
  data: () => ({
    showDietDetails: false,
    displayShowMore: false,
    displayedDiets: [],
    activatedSubscriptionLevel: null,
  }),
  mounted() {
    this.reset();
  },
  computed: {
    hasSelectedDiet() {
      return this.selectedDiet !== undefined && this.selectedDiet !== null;
    },
  },
  watch: {
    diets(newDiets, oldDiets) {
      if (newDiets && !oldDiets) {
        this.reset();
      }
    },
  },
  methods: {
    reset() {
      this.updateDisplayedDiets();
    },
    updateDisplayedDiets() {
      this.displayShowMore = false;
      this.displayedDiets = [];
      if (!this.diets) {
        return;
      }
      for (const diet of this.diets) {
        if (this.displayShowMore && !diet.defaultDisplay) {
          // Some diets are not displayed by default (you must click on "show more")
          return;
        }
        this.displayedDiets.push(diet);
      }
      this.displayShowMore = false;
    },
    showMoreClick() {
      this.updateDisplayedDiets();
    },
    onSelectDiet(diet) {
      this.$emit("update:selectedDiet", diet);
    },
    dietImage(diet) {
      return require(`@/assets/img/objectives/header/${diet.key}.jpg`);
    },
    showMoreInfos() {
      this.showDietDetails = true;
    },
    onCloseDetailsDialog() {
      this.showDietDetails = false;
    },
  },
  components: { Dialog, DietDetails, DietSummary },
};
</script>

<style scoped lang="scss">
.op-diet-selector {
  .op-diet-title-beta {
    background-color: rgba($op-color-red, 0.8);
  }
}
</style>
