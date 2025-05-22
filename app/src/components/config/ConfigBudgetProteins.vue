<template>
  <PleaseWait v-if="!habitsLoaded" />
  <div class="row" v-if="habitsLoaded">
    <div class="col-12 col-lg-6">
      <div v-if="enableTime">
        <h3>Votre temps en cuisine</h3>

        <div
          v-for="speedInfo in speedInfos"
          :key="speedInfo.value"
          class="btn"
          @click="select('speed', speedInfo.value)"
          :class="{ 'btn-info': speedInfo.value == values.speed, 'btn-secondary': speedInfo.value != values.speed }"
        >
          <span :class="{ opacity70: speedInfo.value == 1, opacity85: speedInfo.value == 2 }">
            <FontAwesomeIcon :icon="['far', 'clock']" />
          </span>
          {{ speedInfo.text }}
        </div>
      </div>

      <h3>Votre budget</h3>

      <div
        v-for="budgetInfo in budgetInfos"
        :key="budgetInfo.value"
        class="btn"
        @click="select('budget', budgetInfo.value)"
        :class="{ 'btn-info': budgetInfo.value == values.budget, 'btn-secondary': budgetInfo.value != values.budget }"
      >
        <span v-for="n in budgetInfo.value" :key="n">
          <FontAwesomeIcon :icon="['fas', 'euro-sign']" />
        </span>
        <span style="margin-left: 5px"></span>{{ budgetInfo.text }}
      </div>
    </div>
    <!-- col-12 -->

    <div class="col-12 col-lg-6">
      <h3>Vos préférences alimentaires</h3>

      <div v-if="isVegan">
        <div class="meat-empty" style="display: inline-block">
          <img class="op-hs" src="~@/assets/img/forbidden.png" style="opacity: 0.7; width: 90px" />
        </div>
        <div class="fish-empty" style="display: inline-block">
          <img class="op-hs" src="~@/assets/img/forbidden.png" style="opacity: 0.7; width: 90px" />
        </div>
        <div class="op-vs-5">Désactivé pour l'alimentation végétarienne</div>
      </div>

      <div class="meat-fish-section" v-if="!isVegan">
        <ImgSelector
          selectedCls="meat-full"
          notSelectedCls="meat-empty"
          :value="values.meat"
          @update:value="$emit('update:values', { ...values, meat: $event })"
          v-if="!isVegan"
          :captions="['Peu de viande', 'Viande ~1 fois par jour', 'Beaucoup de viande']"
        />
      </div>

      <div class="meat-fish-section op-vs" v-if="!isVegan">
        <ImgSelector
          selectedCls="fish-full"
          notSelectedCls="fish-empty"
          :value="values.fish"
          @update:value="$emit('update:values', { ...values, fish: $event })"
          :captions="['Peu de poisson', 'Poisson ~2 fois par semaine', 'Beaucoup de poisson']"
        />
      </div>
    </div>
    <!-- col-12 -->
  </div>
  <!-- row -->

  <div id="warning-section">
    <div :class="`alert alert-${warning.class}`" v-if="warning.text" v-html="warning.text"></div>
  </div>
</template>

<script>
import PleaseWait from "@/components/interface/PleaseWait.vue";
import ImgSelector from "@/components/interface/ImgSelector.vue";
import { mapGetters } from "vuex";
import { isEmpty } from "lodash";
import API from "@/api.js";

export default {
  name: "ConfigBudgetProteins",
  props: ["enableTime", "warning", "values"],
  data: () => ({
    speedInfos: [
      { value: 1, text: "Express" },
      { value: 2, text: "Rapide" },
      { value: 3, text: "Normal" },
    ],

    budgetInfos: [
      { value: 1, text: "Budget serré" },
      { value: 2, text: "Budget contrôlé" },
      { value: 3, text: "Budget souple" },
    ],
  }),
  mounted() {
    this.$emit("update:warning", {});
    API.userHabits.getBudgetProteins(this.userId).then((data) => {
      // Speed is not stored in the user profile
      this.$emit("update:values", { ...data, speed: 2 });
    });
  },
  computed: {
    habitsLoaded() {
      return !isEmpty(this.values);
    },
    ...mapGetters({
      userId: "user/id",
    }),
    isVegan() {
      return this.$store.getters["user/getObjectiveDetails"].key == "vegetarian";
    },
  },
  watch: {
    values(newValues, oldValues) {
      // Don't need to call API when values is set for the first time using getBudgetProteins
      if (!isEmpty(oldValues)) {
        this.sendToServer();
      }
    },
  },
  methods: {
    /*
     * select a budget/time value
     */
    select(configName, value) {
      this.$emit("update:values", { ...this.values, [configName]: value });
    },
    sendToServer() {
      if (!this.checkValidity()) {
        return;
      }
      API.userHabits.setBudgetProteins(this.userId, this.values);
    },
    /*
     * After a modification, check validity of values values
     */
    checkValidity() {
      if (this.values.budget == 1 && (this.values.meat > 2 || this.values.fish > 2)) {
        this.$emit("update:warning", {
          text: "Malheureusement, les protéines animales coûtent chers !<br/>Merci de sélectionner un budget serré OU la présence forte de viandes/poissons",
          blocking: true,
          class: "danger",
        });
        return false;
      }
      if (this.values.meat == 1 && this.values.fish == 1) {
        this.$emit("update:warning", {
          text: "L'alimentation sera composée de peu de viande et poisson, mais sans exclusion<br/>(pour choisir une alimentation végétarienne, rendez-vous dans l'onglet \"Alimentation\" une fois l'inscription terminée)",
          blocking: false,
          class: "default",
        });
      }

      if (this.values.meat == 3 && this.values.fish == 3) {
        this.$emit("update:warning", {
          text: "La quantité de protéines sera augmentée dans la limite de l'équilibre alimentaire",
          blocking: false,
          class: "default",
        });
      }
      return true;
    },
  },
  components: { PleaseWait, ImgSelector },
};
</script>

<style scoped lang="scss">
.col-12 {
  text-align: center;
}
.opacity70 {
  opacity: 0.7;
}
.opacity85 {
  opacity: 0.85;
}
.btn {
  width: 150px;
  margin-right: 3px;
}

.meat-fish-section {
  margin-top: 10px;
}

#warning-section {
  margin-top: 30px;

  .alert {
    text-align: center;
    font-weight: bold;
  }
}
.meat-empty {
  background: url("~@/assets/img/config/meat-empty.png") 30px no-repeat;
  background-size: 45px 35px;
}
.fish-empty {
  background: url("~@/assets/img/config/fish-empty.png") 5px no-repeat;
  background-size: 70px 35px;
}
</style>
