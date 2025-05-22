<template>
  <div v-if="diagnosticResults.params.normolipidic === 1" class="diagnose-section">
    <span class="diagnose-icon op-font-lime">
      <FontAwesomeIcon :icon="['fas', 'chart-pie']" />
    </span>
    <div class="diagnose-text">
      <p>Pour limiter tout risque de problèmes cardiaques, nous activons un <b>rééquilibrage des graisses</b>.</p>
      <p>Les graisses mono-insaturées (dont Omega3 et Omega6) sont favorisées au détriment des graisses saturées.</p>
      <p>Nous activons également le <b>contrôle du cholestérol alimentaire</b>.</p>
    </div>
  </div>

  <div v-if="diagnosticResults.other.overweight" class="diagnose-section">
    <span class="diagnose-icon op-font-orange">
      <FontAwesomeIcon :icon="['fas', 'weight']" />
    </span>
    <div class="diagnose-text">
      <p>
        Vous êtes en <b>surpoids</b>.<br />
        La perte de quelques kilos permet de faire baisser le taux de cholestérol.
      </p>
      <p>Nous activons un <b>contrôle calorique léger</b> pour vous aider à perdre du poids en douceur</p>
    </div>
  </div>

  <div class="diagnose-section">
    <span class="diagnose-icon op-font-red">
      <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" />
    </span>
    <div class="diagnose-text">
      <p>Si vous souffrez également de diabète ou d'hypertension, <b>contactez un médecin</b>.</p>
      <p>L'alimentation proposée par Cook&amp;Be est adaptée aux hypercholestérolémies légères</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "NormolipidicResults",
  props: ["diagnosticResults"],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
