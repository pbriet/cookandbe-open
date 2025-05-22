<template>
  <div v-if="diagnosticResults.questions.snacking === 0" class="diagnose-section">
    <span class="diagnose-icon op-font-lime">
      <FontAwesomeIcon :icon="['fas', 'apple-alt']" />
    </span>
    <div class="diagnose-text">
      <p>Vous avez indiqué <b>ne pas avoir tendance à grignotter régulièrement</b>.</p>
      <p>
        Nous activons pour vous le mode <b>gourmand</b>, qui diminue les quantités et vous permet de faire des petits
        écarts plus souvent.
      </p>
    </div>
  </div>

  <div v-if="diagnosticResults.questions.snacking === 1" class="diagnose-section">
    <span class="diagnose-icon op-font-lime">
      <FontAwesomeIcon :icon="['fas', 'apple-alt']" />
    </span>
    <div class="diagnose-text">
      <p>Vous avez indiqué <b>avoir tendance à grignotter régulièrement</b>.</p>
      <p>Nous activons pour vous le mode <b>générosité</b>.</p>
      <p>Nous vous proposerons des plats copieux et équilibrés, de sorte que vous n'ayez pas de fringale.</p>
    </div>
  </div>

  <div
    v-if="diagnosticResults.questions.dietPast > 0 || diagnosticResults.questions.genetic === 1"
    class="diagnose-section"
  >
    <span class="diagnose-icon op-font-lime">
      <FontAwesomeIcon :icon="['fas', 'weight']" />
    </span>
    <div class="diagnose-text">
      <div v-if="diagnosticResults.questions.dietPast > 0">
        <p>Vous avez indiqué <b>avoir déjà suivi des régimes restrictifs</b>.</p>
        <p>Le corps s'habitue malheureusement aux régimes fortement hypocaloriques.</p>
      </div>
      <div v-if="diagnosticResults.questions.genetic === 1">
        <p>
          Vous avez <span v-if="diagnosticResults.questions.dietPast > 0">également</span> indiqué une tendance
          familiale au surpoids.
        </p>
      </div>
      <p>
        Nous activons le mode <b>métabolisme difficile</b> : un régime moins calorique que la moyenne, et un
        réajustement dans le temps.
      </p>
    </div>
  </div>

  <div v-if="diagnosticResults.other.objectiveNonReasonable" class="diagnose-section">
    <span class="diagnose-icon op-font-orange">
      <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" />
    </span>
    <div class="diagnose-text">
      <p>
        Votre objectif de <b>{{ diagnosticResults.other.originalObjective }}kg</b> est considéré comme
        <b>non-raisonnable</b> (IMC trop bas, ou perte trop forte)
      </p>
      <p>
        Nous vous proposons de commencer avec un objectif de <b>{{ diagnosticResults.params.objective }}kg</b>.
      </p>
      <p>Une fois ce poids atteint, vous pourrez diminuer votre objectif.</p>
    </div>
  </div>

  <div class="diagnose-section">
    <span class="diagnose-icon op-font-lime">
      <FontAwesomeIcon :icon="['far', 'hourglass']" />
    </span>
    <div class="diagnose-text">
      <p>
        Nous estimons que l'objectif de <b>{{ diagnosticResults.params.objective }}kg</b> peut être atteint pour le
        <b>{{ DateTime.fromISO(diagnosticResults.other.estimatedDate).setLocale("fr").toFormat("dd MMMM yyyy") }}</b>
      </p>
    </div>
  </div>
</template>

<script>
import { DateTime } from "luxon";

export default {
  name: "SlimResults",
  props: ["diagnosticResults"],
  data: () => ({
    DateTime,
  }),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
