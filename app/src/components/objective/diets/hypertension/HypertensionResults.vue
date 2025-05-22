<template>
  <div v-if="diagnosticResults.params.hyposodic === 1" class="diagnose-section">
    <span class="diagnose-icon op-font-lime">
      <FontAwesomeIcon :icon="['fas', 'tachometer-alt']" />
    </span>
    <div class="diagnose-text">
      <p>Vous avez indiqué <b>souffrir d'hypertension</b>.</p>
      <p>Nous activons pour vous le <b>contrôle des apports en sel</b> (max. 2.4g par jour).</p>
    </div>
  </div>

  <div v-if="diagnosticResults.other.overweight" class="diagnose-section">
    <span class="diagnose-icon op-font-orange">
      <FontAwesomeIcon :icon="['fas', 'weight']" />
    </span>
    <div class="diagnose-text">
      <p>
        Vous êtes en <b>surpoids</b>.<br />
        La perte de quelques kilos permet de diminuer la tension artérielle.
      </p>
      <p>Nous activons un <b>contrôle calorique léger</b> pour vous aider à perdre du poids en douceur</p>
    </div>
  </div>

  <div class="diagnose-section">
    <span class="diagnose-icon op-font-red">
      <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" />
    </span>
    <div class="diagnose-text">
      <p>Si vous souffrez également de diabète ou de cholestérol, <b>contactez un médecin</b>.</p>
      <p>L'alimentation proposée par Cook&amp;Be est uniquement adaptée à un problème d'hypertension.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "HypertensionResults",
  props: ["diagnosticResults"],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
