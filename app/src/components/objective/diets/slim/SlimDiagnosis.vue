<template>
  <div class="row">
    <div class="col-12 col-sm-4">
      Entrez votre taille actuelle (en cm) :<br />
      <SmartIntInput
        :modelValue="profile.height"
        @update:modelValue="$emit('update:profile', { ...profile, height: $event })"
        :min="10"
        :max="300"
        placeholder="Exemple: 172"
        :required="true"
      />
      <br />

      Entrez votre poids actuel :<br />
      <SmartFloatInput
        :modelValue="profile.weight"
        @update:modelValue="$emit('update:profile', { ...profile, weight: $event })"
        :min="1"
        :max="500"
        placeholder="Exemple: 59"
        :required="true"
      /><br />

      Entrez le poids que vous souhaiteriez avoir :<br />
      <SmartFloatInput
        :modelValue="questions.objective"
        @update:modelValue="$emit('update:questions', { ...questions, objective: $event })"
        :min="1"
        :max="500"
        placeholder="Votre objectif (kg)"
        :required="true"
      />
    </div>
  </div>
  <br />

  Avez-vous tendance à grignoter souvent ?<br />
  <Radio
    :required="true"
    :modelValue="questions.snacking"
    @update:modelValue="$emit('update:questions', { ...questions, snacking: $event })"
    :value="1"
    caption="oui"
  />
  <Radio
    :required="true"
    :modelValue="questions.snacking"
    @update:modelValue="$emit('update:questions', { ...questions, snacking: $event })"
    :value="0"
    caption="non"
  />
  <br />

  Avez-vous déja suivi des régimes minceurs ?<br />
  <Radio
    :required="true"
    :modelValue="questions.dietPast"
    @update:modelValue="$emit('update:questions', { ...questions, dietPast: $event })"
    :value="0"
    caption="non"
  />
  <Radio
    :required="true"
    :modelValue="questions.dietPast"
    @update:modelValue="$emit('update:questions', { ...questions, dietPast: $event })"
    :value="1"
    caption="moins de 5 fois"
  />
  <Radio
    :required="true"
    :modelValue="questions.dietPast"
    @update:modelValue="$emit('update:questions', { ...questions, dietPast: $event })"
    :value="5"
    caption="de 5 à 10 fois"
  />
  <Radio
    :required="true"
    :modelValue="questions.dietPast"
    @update:modelValue="$emit('update:questions', { ...questions, dietPast: $event })"
    :value="10"
    caption="plus de 10 fois"
  />
  <br />

  Dans votre famille (parents, frères/soeurs, oncles, tantes), y a-t-il une tendance au surpoids ou à l'obésité ?<br />
  <Radio
    :required="true"
    :modelValue="questions.genetic"
    @update:modelValue="$emit('update:questions', { ...questions, genetic: $event })"
    :value="1"
    caption="oui"
  />
  <Radio
    :required="true"
    :modelValue="questions.genetic"
    @update:modelValue="$emit('update:questions', { ...questions, genetic: $event })"
    :value="0"
    caption="non"
  />
</template>

<script>
import SmartIntInput from "@/components/interface/smart_inputs/SmartIntInput.vue";
import SmartFloatInput from "@/components/interface/smart_inputs/SmartFloatInput.vue";
import Radio from "@/components/interface/Radio.vue";

export default {
  name: "SlimDiagnosis",
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
      return (
        this.profile.height &&
        this.profile.weight &&
        this.questions.objective &&
        this.questions.snacking != null &&
        this.questions.dietPast != null &&
        this.questions.genetic != null
      );
    },
  },
  methods: {},
  components: { SmartIntInput, SmartFloatInput, Radio },
};
</script>

<style scoped lang="scss"></style>
