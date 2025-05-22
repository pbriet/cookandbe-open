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

  <div v-if="diagnosticResults.params.lowTrigly === 1" class="diagnose-section">
    <span class="diagnose-icon op-font-lime">
      <FontAwesomeIcon :icon="['fas', 'chart-line']" />
    </span>
    <div class="diagnose-text">
      <p>Vous avez indiqué <b>souffrir de diabète</b>.</p>
      <p>Nous activons le <b>contrôle des glucides</b> :</p>
      <ul>
        <li>Diminution globale des apports en glucide au profit des protéines</li>
        <li>Stabilité d'un jour à l'autre pour un même repas</li>
        <li>Limitation de l'index glycémique avec plafonnement à 70% de glucides par repas</li>
      </ul>
    </div>
  </div>

  <div v-if="diagnosticResults.params.controlledK === 1" class="diagnose-section">
    <span class="diagnose-icon op-font-lime">K</span>
    <div class="diagnose-text">
      <p>Vous avez indiqué suivre <b>un traitement anti-coagulant</b>.</p>
      <p>Pour ne pas perturber votre traitement, nous activons le <b>contrôle des apports en Vitamine K</b>.</p>
      <p>La vitamine K possède un rôle primordial dans la régulation de la coagulation.</p>
    </div>
  </div>

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
</template>

<script>
export default {
  name: "CardiovascularResults",
  props: ["diagnosticResults"],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
