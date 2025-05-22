<template>
  <h2>
    <span class="col-12 op-icon-dmd text-center d-sm-none">
      <FontAwesomeIcon :icon="['fas', 'balance-scale']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['fas', 'balance-scale']" />
    </span>

    Les bons apports <i>protéiniques</i> pour chaque jour
  </h2>
  <p>Vous souhaitez manger végétarien mais vous vous demandez comment manger suffisamment de protéines ?</p>
  <p>Cook&amp;Be s'en occupe pour vous ! Nos suggestions respectent les apports recommandés de l'ANSES</p>

  <h2>
    <span class="op-icon-dmd col-12 text-center d-sm-none">
      <FontAwesomeIcon :icon="['fas', 'heart']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['fas', 'heart']" />
    </span>
    Vitamine B12, Calcium, Fer, ... évitez les <i>carences</i>
  </h2>
  <p>
    Le principe de Cook&amp;Be est simple : nous vous proposons des idées de menus végétariens pour chaque jour de la
    semaine. Et pas au hasard ! Nous nous adaptons à votre profil (taille et poids notamment), et vous assurons les bons
    apports sur les nutriments essentiels.
  </p>
  <p>Et c'est 100% transparent !</p>

  <h2>
    <span class="op-icon-dmd col-12 text-center d-sm-none">
      <FontAwesomeIcon :icon="['far', 'thumbs-up']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['far', 'thumbs-up']" />
    </span>
    Mangez <i>ce que vous voulez</i> !
  </h2>
  <p>Sur Cook&amp;Be, vous pouvez choisir la recette que vous voulez. Et même indiquer la votre !</p>
  <p>
    Nous adaptons alors nos autres suggestions pour toujours maintenir un équilibre nutritionnel sur la journée/semaine.
  </p>

  <h2>
    <span class="op-icon-dmd col-12 text-center d-sm-none">
      <FontAwesomeIcon :icon="['fas', 'utensils']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['fas', 'utensils']" />
    </span>
    Découvrez des recettes <i>gourmandes</i>, rapides et originales.
  </h2>
  <p>Cook&amp;Be, c'est aussi et surtout une application pour avoir la fameuse "idée repas" !</p>
  <p>
    Chaque semaine, vous obtenez de nouvelles <a :href="WWW_HOST + '/recettes'">recettes</a> savoureuses pour varier enfin vos plats
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
    Nos suggestions de menus végétariens s'appuient sur les recommandations officielles des autorités de santé (<b
      >HAS</b
    >
    - Haute Autorité de Santé, et <b>ANSES</b> - Agence nationale de sécurité sanitaire de l’alimentation, de
    l’environnement et du travail).
  </p>
  <p>Thierry Poitou, nutritionniste, encadre la mise en place des alimentations.</p>

  <h2>
    <span class="op-icon-dmd col-12 text-center d-sm-none">
      <FontAwesomeIcon :icon="['far', 'thumbs-up']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['far', 'thumbs-up']" />
    </span>
    Des recommandations en toute <i>transparence</i>
  </h2>
  <div>
    <p>Retrouvez toutes les informations sur le fonctionnement de Cook&amp;Be :</p>
    <ul>
      <li>L'application : <a :href="WWW_HOST + '/how'">Comment ça marche</a></li>
      <li>Le rééquilibrage alimentaire : <a :href="WWW_HOST + '/nutrition'">Cook&amp;Be et la nutrition personnalisée</a></li>
    </ul>
  </div>
</template>

<script>
import { WWW_HOST } from "@/config.js";

export default {
  name: "VegetarianDetails",
  props: [],
  data: () => ({
    WWW_HOST,
  }),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
