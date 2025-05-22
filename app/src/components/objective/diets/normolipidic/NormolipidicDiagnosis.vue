<template>
  <div>
    <ul class="op-list">
      <li class="row">
        <span class="col-12 col-sm-10"> Entrez votre taille actuelle (en cm) </span>
        <span class="col-12 col-sm-2">
          <SmartIntInput
            :modelValue="profile.height"
            @update:modelValue="$emit('update:profile', { ...profile, height: $event })"
            :min="10"
            :max="300"
            placeholder="Exemple: 172"
            :required="true"
          />
        </span>
      </li>

      <li class="row">
        <span class="col-12 col-sm-10"> Entrez votre poids actuel (en kg) </span>
        <span class="col-12 col-sm-2">
          <SmartFloatInput
            :modelValue="profile.weight"
            @update:modelValue="$emit('update:profile', { ...profile, weight: $event })"
            :min="1"
            :max="500"
            placeholder="Exemple: 59"
            :required="true"
          />
        </span>
      </li>
    </ul>
  </div>
</template>

<script>
import SmartIntInput from "@/components/interface/smart_inputs/SmartIntInput.vue";
import SmartFloatInput from "@/components/interface/smart_inputs/SmartFloatInput.vue";

export default {
  name: "NormolipidicDiagnosis",
  props: ["questions", "profile"],
  data: () => ({}),
  mounted() {
    this.$emit("update:isValid", this.isValid);
  },
  watch: {
    isValid() {
      this.$emit("update:isValid", this.isValid);
    },
  },
  computed: {
    isValid() {
      return this.profile.height && this.profile.weight;
    },
  },
  methods: {},
  components: { SmartFloatInput, SmartIntInput },
};
</script>

<style scoped lang="scss"></style>
