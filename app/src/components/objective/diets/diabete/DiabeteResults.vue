<template>
  <div class="diagnose-section">
    <span class="diagnose-icon op-font-lime">
      <FontAwesomeIcon :icon="['fas', 'chart-line']" />
    </span>
    <div class="diagnose-text">
      <p>Vous avez indiqué <b>souffrir de diabète de type 2</b>.</p>
      <p>Nous activons le <b>contrôle des glucides</b> :</p>
      <ul>
        <li>Diminution globale des apports en glucide au profit des protéines</li>
        <li>Stabilité d'un jour à l'autre pour un même repas</li>
        <li>Pour éviter les pics : répartition régulière des apports glucidiques à chaque repas</li>
      </ul>
    </div>
  </div>

  <div v-if="diagnosticResults.other.overweight" class="diagnose-section">
    <span class="diagnose-icon op-font-orange">
      <FontAwesomeIcon :icon="['fas', 'weight']" />
    </span>
    <div class="diagnose-text">
      <p>
        Vous êtes en <b>surpoids</b>.<br />
        La perte de quelques kilos permet de mieux réguler la glycémie
      </p>
      <p>Nous activons un <b>contrôle calorique léger</b> pour vous aider à perdre du poids en douceur</p>
    </div>
  </div>

  <div class="diagnose-section">
    <span class="diagnose-icon op-font-red">
      <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" />
    </span>
    <div class="diagnose-text">
      <p>Si vous souffrez de diabète de type 1, ou d'un diabète de type 2 avancé, <b>contactez un médecin</b>.</p>
      <p>L'alimentation proposée par Cook&amp;Be est adaptée au prédiabète et diabète léger de type 2</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "DiabeteResults",
  props: ["diagnosticResults"],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
