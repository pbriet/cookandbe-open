<template>
  <h2>
    <span class="op-icon-dmd col-12 text-center d-sm-none">
      <FontAwesomeIcon :icon="['fas', 'user']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['fas', 'user']" />
    </span>
    Les <i>bons nutriments</i> selon votre profil
  </h2>
  <p>Contrôle des apports en glucides, rééquilibrage des graisses, limitation du sel, ...</p>
  <p>Cook&amp;Be s'occupe de tout, en fonction de vos besoins.</p>

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
  name: "CardiovascularDetails",
  props: [],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
