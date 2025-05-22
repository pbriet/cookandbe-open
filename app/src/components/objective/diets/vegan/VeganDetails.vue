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
    <p>Pour vous aider, nous avons mis en place une alimentation végétalienne :</p>
    <ul>
      <li>Excluant les aliments contenant de la chair animale (viande rouge, blanche, poisson, fruits de mer)</li>
      <li>Excluant les aliments contenant des produits d'origine animale (oeuf, lait, miel)</li>
      <li>Contrôlant votre équilibre sur 20 nutriments pour éviter les carences</li>
    </ul>
  </div>
  <p>Avec Cook&amp;Be, engagez-vous sereinement dans l'univers végétal sans risque de carences !</p>

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
  name: "VeganDetails",
  props: [],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
