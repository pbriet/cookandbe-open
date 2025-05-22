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
    <p>Pour vous aider, nous avons mis en place une alimentation sans gluten :</p>
    <ul>
      <li>Excluant les aliments et recettes contenant du blé, du seigle, de l'orge ou de l'avoine</li>
      <li>Prévenant des aliments à surveiller car pouvant contenir des traces de gluten ou être contaminés</li>
      <li>Contrôlant votre équilibre sur 30 nutriments pour éviter les carences</li>
    </ul>
  </div>
  <p>Offrez à votre corps une alimentation facile à assimiler, et retrouvez de l'énergie !</p>

  <div class="alert alert-success" id="afdiag">
    <h2>
      <span class="op-icon-dmd col-12 text-center d-sm-none">
        <FontAwesomeIcon :icon="['fas', 'check']" />
      </span>
      <span class="d-none d-sm-inline">
        <FontAwesomeIcon :icon="['fas', 'check']" />
      </span>
      Soutenu par <i>l'AFDIAG</i>
    </h2>
    <div class="d-sm-none text-center">
      <a href="http://www.afdiag.fr" target="_blank">
        <img
          src="@/assets/img/corp/afdiag-transparent.png"
          alt="logo Association Française Des Intolérants Au Gluten"
        />
      </a>
    </div>
    <table>
      <tr>
        <td class="d-none d-sm-table-cell">
          <a href="http://www.afdiag.fr" target="_blank">
            <img
              src="@/assets/img/corp/afdiag-transparent.png"
              alt="logo Association Française Des Intolérants Au Gluten"
            />
          </a>
        </td>
        <td>
          <p>
            <b>L’AFDIAG, Association Française Des Intolérants Au Gluten,</b>
            Association régie par la loi de 1901, est créée en 1989
          </p>
          <div>
            <b>Ses objectifs :</b>
            <ul class="mt-1">
              <li>Informer, aider et défendre les intérêts des intolérants au gluten.</li>
              <li>
                Collaborer avec les professions médicales, les instances gouvernementales, les industriels de
                l’agroalimentaire, les fabricants et distributeurs de produits diététiques sans gluten, les
                professionnels de la restauration etc...
              </li>
              <li>Soutenir la Recherche.</li>
            </ul>
          </div>
          <p>
            Aujourd’hui, l’AFDIAG compte quelques 6 000 familles. Elle fournit une documentation complète sur le régime
            sans gluten et l’intolérance au gluten, organise des colloques médicaux avec des professionnels de santé et
            des rencontres entre adhérents. Elle propose aussi des stages d’éducation nutritionnelle, des adresses de
            restaurants, des ateliers de cuisine etc..
          </p>
          <p>
            Elle délivre le logo « épi de blé barré dans un cercle », apposé sur les produits sans gluten pré-emballés
            et analysés (= inf. à 20mg/kg de gluten). Si vous trouvez ce logo sur un produit, c'est qu'il est bien sans
            gluten.
          </p>
        </td>
      </tr>
    </table>
  </div>

  <h2>
    <span class="op-icon-dmd col-12 text-center d-sm-none">
      <FontAwesomeIcon :icon="['fas', 'check']" />
    </span>
    <span class="d-none d-sm-inline">
      <FontAwesomeIcon :icon="['fas', 'check']" />
    </span>
    Des menus sans gluten recommandés par notre <i>nutritionniste</i>
  </h2>
  <p>
    Nos suggestions s'appuient sur les recommandations officielles des autorités de santé (<b>HAS</b> - Haute Autorité
    de Santé, et <b>ANSES</b> - Agence nationale de sécurité sanitaire de l’alimentation, de l’environnement et du
    travail).
  </p>
  <p>Thierry Poitou, nutritionniste, participe à la configuration des alimentations spécifiques.</p>

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
  name: "GlutenFreeDetails",
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
