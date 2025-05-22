<template>
  <h2>
    <span class="op-icon-dmd col-12 text-center d-sm-none">
      <FontAwesomeIcon :icon="['far', 'clock']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['far', 'clock']" />
    </span>
    Gagnez du <i>temps</i> et ayez toujours des <i>idées de menus</i> équilibrés pour votre semaine !
  </h2>

  <div>
    <p>Cook&amp;Be vous accompagne dans un rééquilibrage alimentaire au quotidien :</p>
    <ul>
      <li>Il vous propose des idées de menus que vous aimez</li>
      <li>Il prépare votre liste de courses</li>
      <li>Il vous envoie chaque jour les <a :href="WWW_HOST + '/recettes'">recettes</a> avec les bonnes quantités</li>
    </ul>
  </div>
  <p>Réussissez votre rééquilibrage alimentaire avec Cook&amp;Be !</p>

  <h2>
    <span class="op-icon-dmd col-12 text-center d-sm-none">
      <FontAwesomeIcon :icon="['fas', 'child']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['fas', 'child']" />
    </span>
    Retrouvez <i>dynamisme</i> et <i>santé</i>
  </h2>

  <p>Les chercheurs le disent : tout vient du ventre !</p>
  <div>
    Avec Cook&amp;Be, vous êtes sûrs d'avoir des menus équilibrés avec les bons apports en nutriments pour une
    alimentation saine.<br />
    <p>Tous nos réglages sont basés sur des recommandations officielles :</p>
    <ul>
      <li>Les apports caloriques pour ne pas prendre de poids</li>
      <li>L'équilibre glucides-lipides-protéines, pour être en forme du matin au soir</li>
      <li>Les vitamines et minéraux, pour vos os, vos yeux, ... tout votre corps !</li>
    </ul>
  </div>

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
  <p>Avec Cook&amp;Be et ses menus équilibrés, vous avez un véritable atout santé dans votre poche !</p>
</template>

<script>
import { WWW_HOST } from "@/config.js";

export default {
  name: "BalancedDetails",
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
