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

      <li class="row">
        <span class="col-12 col-sm-10">
          Faites-vous de l'hypertension, suivez-vous un traitement contre l'hypertension,<br />
          ou votre médecin vous a-t-il conseillé de manger moins salé ?
        </span>
        <span class="col-3 col-sm-1 fright">
          <Radio
            :required="true"
            :modelValue="questions.hypertension"
            @update:modelValue="$emit('update:questions', { ...questions, hypertension: $event })"
            :value="1"
            caption="Oui"
            :noHover="true"
            group="hyposodic"
          />
        </span>
        <span class="col-3 col-sm-1 fright">
          <Radio
            :required="true"
            :modelValue="questions.hypertension"
            @update:modelValue="$emit('update:questions', { ...questions, hypertension: $event })"
            :value="0"
            caption="Non"
            :noHover="true"
            group="hyposodic"
          />
        </span>
      </li>

      <li class="row">
        <span class="col-12 col-sm-10">
          Avez-vous un excès de triglycérides dans le sang (voir dernière prise de sang),<br />
          ou votre médecin vous a-t-il indiqué que vous faisiez du diabète ou du pré-diabète ou une intolérance aux
          glucides ?
        </span>
        <span class="col-3 col-sm-1 fright">
          <Radio
            :required="true"
            :modelValue="questions.diabete"
            @update:modelValue="$emit('update:questions', { ...questions, diabete: $event })"
            :value="1"
            caption="Oui"
            :noHover="true"
            group="lowTrigly"
          />
        </span>
        <span class="col-3 col-sm-1 fright">
          <Radio
            :required="true"
            :modelValue="questions.diabete"
            @update:modelValue="$emit('update:questions', { ...questions, diabete: $event })"
            :value="0"
            caption="Non"
            :noHover="true"
            group="lowTrigly"
          />
        </span>
      </li>

      <li class="row">
        <span class="col-12 col-sm-10">
          Votre médecin vous a-t-il demandé de surveiller vos apports en vitamine K du fait d’un traitement
          anti-coagulant à base d'antivitamine K ?
        </span>
        <span class="col-3 col-sm-1 fright">
          <Radio
            :required="true"
            :modelValue="questions.anticoagul"
            @update:modelValue="$emit('update:questions', { ...questions, anticoagul: $event })"
            :value="1"
            caption="Oui"
            :noHover="true"
            group="controlledK"
          />
        </span>
        <span class="col-3 col-sm-1 fright">
          <Radio
            :required="true"
            :modelValue="questions.anticoagul"
            @update:modelValue="$emit('update:questions', { ...questions, anticoagul: $event })"
            :value="0"
            caption="Non"
            :noHover="true"
            group="controlledK"
          />
        </span>
      </li>
    </ul>
  </div>
</template>

<script>
import SmartIntInput from "@/components/interface/smart_inputs/SmartIntInput.vue";
import SmartFloatInput from "@/components/interface/smart_inputs/SmartFloatInput.vue";
import Radio from "@/components/interface/Radio.vue";

export default {
  name: "CardiovascularDiagnosis",
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
        this.questions.hypertension != null &&
        this.questions.diabete != null &&
        this.questions.anticoagul != null
      );
    },
  },
  methods: {},
  components: { SmartIntInput, SmartFloatInput, Radio },
};
</script>

<style scoped lang="scss"></style>
