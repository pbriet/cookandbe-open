<template>
  <h2>
    <span class="op-icon-dmd col-12 text-center d-sm-none">
      <FontAwesomeIcon :icon="['fas', 'user']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['fas', 'user']" />
    </span>
    Une alimentation <i>pauvre en sel</i>, avec les <i>bons nutriments</i>
  </h2>
  <p>
    L'excès de sel favorise l'hypertension.<br />
    Le premier réflexe alimentaire chez la personne hypertendue est donc de limiter ses apports en sel.
  </p>
  <div>
    <p>Cook&amp;Be vous propose une alimentation adaptée à votre profil :</p>
    <ul>
      <li>Limitation des apports en sodium</li>
      <li>Contrôle des calories et de l'équilibre nutritionnel</li>
      <li>Apports en vitamines et minéraux</li>
    </ul>
  </div>
  <p>Suivez simplement nos idées repas, et améliorez votre santé.</p>

  <h2>
    <span class="op-icon-dmd col-12 text-center d-sm-none">
      <FontAwesomeIcon :icon="['fas', 'utensils']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['fas', 'utensils']" />
    </span>
    Laissez une place au <i>plaisir</i> de manger
  </h2>
  <p>Avec Cook&amp;Be, vous avez le droit de vous faire plaisir !</p>
  <p>Indiquez ce que vous souhaitez manger et Cook&amp;Be rééquilibrera les autres plats de la journée.</p>
  <p>Vous pouvez même inclure vos propres recettes.</p>

  <h2>
    <span class="op-icon-dmd col-12 text-center d-sm-none">
      <FontAwesomeIcon :icon="['fas', 'weight']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['fas', 'weight']" />
    </span>
    Maitrisez votre poids
  </h2>
  <p>Chez les personnes présentant un surpoids, la perte de quelques kilos permet de diminuer la tension artérielle.</p>
  <p>Si vous êtes en surpoids, Cook&amp;Be vous propose des suggestions adaptées pour une perte de poids en douceur.</p>

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
  name: "HypertensionDetails",
  props: [],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
