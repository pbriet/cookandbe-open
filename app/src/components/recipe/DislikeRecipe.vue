<template>
  <PleaseWait v-if="dislikeState === 'please_wait'" />

  <div id="dislike-recipe-panel" v-if="dislikeState == 'dislike'">
    <!-- Disliking an element -->
    <div class="inline-radio-btns" v-if="profiles.length > 1">
      <h4>Qui n'aime pas cette recette ?</h4>
      <RadioBtn v-model="selected.profile" :value="profile" v-for="profile in profiles" :key="profile.id">
        <ProfileLogo :sex="profile.sex" /> {{ profile.nickname }}
      </RadioBtn>
    </div>
    <br />

    <h4>Vous n'aimez pas :</h4>

    <div v-if="recipeDetails && recipeDetails.ingredients.length == 1" class="fulline-radio-btns">
      <RadioBtn v-model="selected.disliked" value="recipe">
        <FontAwesomeIcon :icon="['far', 'thumbs-down']" /> {{ recipeDetails.ingredients[0].name }} (mangé(e) seul(e))
      </RadioBtn>
      <RadioBtn v-model="selected.disliked" value="ingredient" :onClick="selectUniqueIngredient">
        <FontAwesomeIcon :icon="['far', 'thumbs-down']" /> {{ recipeDetails.ingredients[0].name }} (dans toutes les
        recettes)
      </RadioBtn>
    </div>

    <div v-if="recipeDetails && recipeDetails.ingredients.length > 1" class="inline-radio-btns">
      <RadioBtn v-model="selected.disliked" value="recipe">
        <FontAwesomeIcon :icon="['fas', 'birthday-cake']" /> La recette
      </RadioBtn>
      <RadioBtn v-model="selected.disliked" value="ingredient">
        <FontAwesomeIcon :icon="['far', 'lemon']" /> Un ingrédient
      </RadioBtn>
    </div>
    <br />

    <div
      v-if="recipeDetails && recipeDetails.ingredients.length > 1 && selected.disliked === 'ingredient'"
      class="fulline-radio-btns"
    >
      <h4>Sélectionnez l'ingrédient :</h4>

      <RadioBtn
        v-model="selected.ingredient"
        :value="ingredient"
        v-for="ingredient in recipeDetails.ingredients"
        :key="`${ingredient.name}-${ingredient.foodId}`"
        :onClick="() => onSelectIngredient(ingredient)"
      >
        <FontAwesomeIcon :icon="['far', 'thumbs-down']" class="me-1" />{{ ingredient.name }}
      </RadioBtn>
    </div>

    <div
      v-if="selected.disliked == 'ingredient' && selected.ingredient && foodTags.length > 1"
      class="fulline-radio-btns"
    >
      <h4>Pour finir, précisez ce que vous n'aimez pas :</h4>

      <RadioBtn
        v-model="selected.foodTag"
        :value="foodTag"
        v-for="foodTag in foodTags"
        :key="foodTag.id"
        :onClick="onSelectFoodtag"
      >
        <FontAwesomeIcon :icon="['far', 'thumbs-down']" />
        {{ foodTag.name }}
      </RadioBtn>
    </div>

    <div v-if="tooManyDisliked" class="alert alert-danger">
      L'ensemble de vos goûts (tous membres du foyer confondus) vous empêche d'accéder à plus de 2 recettes sur 3.<br />
      Pour assurer votre équilibre, nous n'avons pas pu exclure l'aliment "{{ selected.foodTag.name }}".
    </div>

    <div v-if="noFoodTag" class="alert alert-danger">
      Il n'est pas possible de supprimer cet ingrédient.<br />
      Contactez-nous pour + d'informations.
    </div>

    <div class="dislike-final-btns">
      <button class="btn btn-warning me-2" @click="onCancel">
        <FontAwesomeIcon :icon="['fas', 'arrow-left']" />
        Annuler
      </button>

      <button
        class="btn btn-success"
        :disabled="selected.disliked !== 'recipe' && !selected.foodTag"
        @click="validDislike"
      >
        <FontAwesomeIcon :icon="['fas', 'check']" />
        Valider
      </button>
    </div>
    <!-- dislike-final-btns -->
  </div>
  <!-- dislike-recipe-panel -->
</template>

<script>
import API from "@/api.js";
import { mapGetters } from "vuex";
import PleaseWait from "@/components/interface/PleaseWait.vue";
import RadioBtn from "@/components/interface/RadioBtn.vue";
import ProfileLogo from "@/components/interface/ProfileLogo.vue";
import $ from "jquery";

/*
 * This component displays a panel with multiple buttons :
 * - 1 to dislike the recipe
 * - N to dislike the ingredients
 *
 * + the selection of the profile who dislike it
 */
export default {
  name: "DislikeRecipe",
  props: [
    "recipe",
    "onFinished", // When the user has either disliked something or cancelled
  ],
  data: () => ({
    dislikeState: "dislike",
    selected: { profile: null, disliked: null },
    recipeDetails: null,
    noFoodTag: false,
    tooManyDisliked: false,
    foodTags: [],
  }),
  mounted() {
    this.init(this.recipe);
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
      profiles: "profile/getProfiles",
    }),
  },
  watch: {
    profiles(newProfiles) {
      if (!this.profiles && newProfiles) {
        this.selected.profile = newProfiles[0];
      }
    },
    recipe: {
      handler(newRecipe) {
        // When tree is initialized, or changes, update the data
        if (newRecipe) {
          this.init(newRecipe);
        }
      },
      deep: true,
    },
  },
  methods: {
    scrollToBottom() {
      setTimeout(() => {
        const div = $("#recipe-selection-dialog"); // Quite ugly, because we're not supposed to know the id there !
        div.stop().animate({ scrollTop: div[0].scrollHeight }, 800);
      }, 100);
    },
    async init(recipe) {
      this.dislikeState = "dislike";

      this.selected = { profile: null, disliked: null };
      if (this.profiles) {
        this.selected.profile = this.profiles[0];
      }

      this.recipeDetails = await this.$store.dispatch("recipe/getRecipe", { recipeId: recipe.id });
    },
    onSelectFoodtag() {
      this.tooManyDisliked = false;
      this.scrollToBottom();
    },
    async onSelectIngredient(ingredient) {
      this.noFoodTag = false;
      this.tooManyDisliked = false;
      const data = await API.foodTags({ food_id: ingredient.foodId, dislikable_only: true });
      // More than one foodTag matching this foodId, asking the user which one he dislikes
      this.foodTags = data;

      if (data.length <= 1) {
        if (data.length === 0) {
          this.noFoodTag = true;
        }
        this.selected.foodTag = data[0];
      }
      this.scrollToBottom();
    },
    selectUniqueIngredient() {
      this.selected.ingredient = this.recipeDetails.ingredients[0];
      this.onSelectIngredient(this.selected.ingredient);
      this.scrollToBottom();
    },
    async dislikeFoodTag() {
      const data = await this.$store.dispatch("taste/add", {
        profileId: this.selected.profile.id,
        foodTag: this.selected.foodTag,
        fondness: -5,
        setPlanningExpired: false,
      });
      if (data.status === "error") {
        return false;
      }
      if (data.status === "too_many_disliked") {
        this.tooManyDisliked = true;
        this.dislikeState = "dislike";
        return false;
      }
      return true;
    },
    async dislikeRecipe() {
      return await API.profile.dislikeRecipe(this.userId, this.selected.profile.id, { recipeId: this.recipe.id });
    },
    async validDislike() {
      this.dislikeState = "please_wait";
      let res;
      if (this.selected.disliked === "ingredient") {
        res = await this.dislikeFoodTag();
      } else if (this.selected.disliked === "recipe") {
        res = await this.dislikeRecipe();
      }
      if (res) {
        this.onFinished(true);
      }
    },
    onCancel() {
      this.onFinished(false);
    },
  },
  components: { PleaseWait, RadioBtn, ProfileLogo },
};
</script>

<style scoped lang="scss">
#dislike-recipe-panel {
  margin-top: 20px;
  padding-left: 15px;

  .dislike-details {
    font-weight: bold;
    margin-bottom: 3px;
  }
  .dislike-final-btns {
    margin-top: 20px;
    font-weight: bold;
  }

  .inline-radio-btns {
    .radio-btn {
      margin-right: 10px;
    }
  }

  .fulline-radio-btns {
    .radio-btn {
      display: block;
      width: 85%;
      margin-bottom: 10px;
      text-align: left;
      span {
        margin-right: 5px;
      }
    }
  }

  .profile-icon {
    font-size: inherit;
    line-height: inherit;
    display: inline;
  }
}
</style>
