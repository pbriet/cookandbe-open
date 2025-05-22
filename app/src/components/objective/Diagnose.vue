<template>
  <form class="form" name="diagnostic_form" role="form">
    <div class="alert alert-danger" v-if="errorMessage">
      {{ errorMessage }}
    </div>
    <DietDiagnosis
      :diet="diet.selected.key"
      :questions="questions"
      @update:questions="$emit('update:questions', $event)"
      :profile="profile"
      @update:profile="$emit('update:profile', $event)"
      @update:isValid="isValid = $event"
    />
    <div class="col-12 row flex-row-reverse op-vs">
      <div class="col-6 col-sm-4 col-md-3">
        <button type="button" class="btn btn-success col-12" @click="submitDiagnostic" :disabled="!isValid">
          <span>
            <FontAwesomeIcon :icon="['fas', 'check']" />
            Valider
          </span>
        </button>
      </div>
      <div class="fright col-6 col-sm-4 col-md-3">
        <BackButton class="col-12" :likeNavigatorBack="true">Retour</BackButton>
      </div>
    </div>
  </form>
</template>

<script>
import BackButton from "@/components/interface/BackButton.vue";
import DietDiagnosis from "@/components/objective/diets/DietDiagnosis.vue";
import { ENABLE_DIET_FORCE_SLIM_DIAGNOSIS } from '@/config.js'

export default {
  name: "Diagnose",
  props: ["diet", "errorMessage", "submitDiagnostic", "questions", "profile"],
  data: () => ({
    isValid: false,
  }),
  computed: {
    dietKey () {
      if (ENABLE_DIET_FORCE_SLIM_DIAGNOSIS) {
        return "slim";
      }
      return this.diet.selected.key;
    }
  },
  methods: {},
  components: { BackButton, DietDiagnosis },
};
</script>

<style scoped lang="scss"></style>
