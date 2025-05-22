<template>
  <h2>
    <span class="op-icon-dmd col-12 text-center d-sm-none">
      <FontAwesomeIcon :icon="['fas', 'heart']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['fas', 'heart']" />
    </span>
    La <i>nutrition</i> au service de <i>votre santé</i>
  </h2>
  <p>Cook&amp;Be vous propose chaque jour des repas parfaitement sains et équilibrés, avec les bonnes quantités.</p>
  <div>
    <p>Pour vous aider, nous avons mis en place une alimentation "d'épargne digestive" :</p>
    <ul>
      <li>Réduction des apports en lipides</li>
      <li>Exclusion d'aliments durs à digérer</li>
      <li>Le tout en respectant les bons équilibres et apports</li>
    </ul>
  </div>
  <p>Votre estomac va enfin pouvoir respirer ! Et vous aussi.</p>

  <h2>
    <span class="op-icon-dmd col-12 text-center d-sm-none">
      <FontAwesomeIcon :icon="['fas', 'apple-alt']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['fas', 'apple-alt']" />
    </span>
    Des recettes à base <i>d'aliments digestes</i>
  </h2>
  <p>Nous vous proposons des recettes qui limitent les problèmes de flatulences ou d'inconfort digestif.</p>
  <p>Ne soyez plus fatigué entre les repas et améliorez votre sommeil.</p>
  <p>
    Chaque personne réagit différemment aux aliments. Vous avez peut-être repéré certains aliments que vous avez du mal
    à digérer.<br />
    Ajoutez-les dans la liste des aliments que vous ne voulez pas trouver dans vos recettes
  </p>

  <h2>
    <span class="op-icon-dmd col-12 text-center d-sm-none">
      <FontAwesomeIcon :icon="['fas', 'check']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['fas', 'check']" />
    </span>
    Recommandé par notre <i>nutritionniste</i>
  </h2>
  <p>
    Nos suggestions s'appuient sur les recommandations officielles des autorités de santé (<b>HAS</b> - Haute Autorité
    de Santé, et <b>ANSES</b> - Agence nationale de sécurité sanitaire de l’alimentation, de l’environnement et du
    travail).
  </p>
  <p>Thierry Poitou, nutritionniste, participe à la configuration des alimentations spécifiques.</p>
</template>

<script>
export default {
  name: "EasyDigestDetails",
  props: [],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
