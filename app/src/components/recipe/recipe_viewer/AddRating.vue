<template>
  <div class="rate-recipe-section col-12" v-if="rating.sentToServer">
    <span class="op-icon-xl">
      <FontAwesomeIcon :icon="['fas', 'check']" />
    </span>
    Merci, votre avis sera pris en compte
    <span v-if="rating.comment">après validation par notre équipe.</span>
    <span v-if="!rating.comment">d'ici quelques minutes.</span>
  </div>
  <div class="rate-recipe-section col-12" v-if="rating.existing?.rated">
    <div>Vous avez évalué cette recette <RatingStars :value="rating.existing.rating" /></div>
    <div v-if="!rating.existing.moderatedAt">Votre commentaire est en attente de modération par notre équipe</div>
  </div>

  <div
    class="rate-recipe-section col-12"
    id="rate-action"
    v-if="isLoggedIn && rating.existing && !rating.existing.rated && !rating.sentToServer"
  >
    <ConditionalH2 :when="!printMode"><span>Donnez votre avis !</span></ConditionalH2>
    Note :
    <div class="stars" @mouseleave="$emit('update:mouseover', null)">
      <div
        class="op-icon-xl"
        v-for="i in [1, 2, 3, 4, 5]"
        :key="i"
        @mouseover="$emit('update:mouseover', i)"
        @click="setRating(i)"
      >
        <FontAwesomeIcon
          :icon="[(rating.value >= i && !rating.mouseover) || rating.mouseover >= i ? 'fas' : 'far', 'star']"
        />
      </div>
    </div>
    ({{ getRatingDescription }})<br />
    Commentaire (optionnel) :<br />
    <textarea :value="comment" @input="$emit('update:comment', $event.target.value)" class="col-12" />
    <br />
    <div v-if="rating.comment" class="warning-comment col-12">
      Attention, les quantités des ingrédients de la recette varient selon les personnes.<br />
      <span class="dont-do-that">
        <FontAwesomeIcon :icon="['fas', 'times']" /> "j'ai mis 3 pommes au lieu de 2"<br />
      </span>
      <span class="do-this"> <FontAwesomeIcon :icon="['fas', 'check']" /> "j'ai mis plus de pommes" </span>
    </div>

    <span class="clearfix" />

    <div class="row op-vs-10">
      <div class="col-12">
        <button class="btn btn-secondary fright" @click="rateRecipe" :disabled="!rating.value">Valider mon avis</button>
      </div>
    </div>

    <span class="clearfix" />
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { RATING_DESCRIPTION } from "@/common/static.js";
import RatingStars from "@/components/interface/RatingStars.vue";
import ConditionalH2 from "@/components/interface/conditional_headers/ConditionalH2.vue";

export default {
  name: "AddRating",
  props: ["rating", "printMode", "setRating", "rateRecipe", "comment", "mouseover"],
  data: () => ({}),
  computed: {
    ...mapGetters({
      isLoggedIn: "user/isLoggedIn",
    }),
    getRatingDescription() {
      let value = this.mouseover;
      if (!value) {
        value = this.rating.value;
      }
      return RATING_DESCRIPTION[value];
    },
  },
  methods: {},
  components: { RatingStars, ConditionalH2 },
};
</script>

<style lang="scss">
.rate-recipe-section {
  h2 {
    margin-bottom: 10px;
  }
  background-color: #eeeeee;
  padding-top: 5px;
  padding-bottom: 5px;

  .stars {
    display: inline-block;
    margin-left: 5px;
    svg {
      cursor: pointer;
    }
  }
  textarea {
    margin-top: 5px;
    height: 100px;
  }
  .btn {
    margin-top: 5px;
    margin-bottom: 5px;
  }
  .warning-comment {
    float: left;
    padding-top: 5px;
    svg {
      font-weight: bold;
    }
    .dont-do-that {
      color: $op-color-alert-danger;
    }
    .do-this {
      color: $op-color-alert-ok;
    }
  }
}
</style>
