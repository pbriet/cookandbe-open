<template>
  <div class="smart-shopping-block">
    <DayPlannerRecipe
      :dishTypesById="dishTypes"
      :onAddRecipe="onSetRecipe"
      :onNotNow="onNotNow"
      :onDislike="onDislike"
      :onReplace="showReplacePopup"
      :onDeleteRecipe="deleteDish"
      :selection="selection"
      :considerAllValidated="true"
      :showValidateBtn="true"
      :onValidate="onLockRecipe"
      v-if="current.state === 'suggest'"
      :showDetails="true"
      :preventEdition="dayStatus.shoppingListId"
    />
    <DislikeRecipe
      :recipe="selection.recipe"
      :onFinished="onDislikeFinished"
      v-if="profileTastesLoaded && current.state === 'dislike'"
    />
  </div>
</template>

<script>
import DayPlannerRecipe from "@/components/planning/DayPlannerRecipe.vue";
import { mapGetters } from "vuex";
import DislikeRecipe from "@/components/recipe/DislikeRecipe.vue";

export default {
  name: "SelectionBlock",
  props: [
    "dishTypes",
    "onNotNow",
    "selection",
    "current",
    "dayStatus",
    "onDislike",
    "onDislikeFinished",
    "onLockRecipe",
    "showReplacePopup",
    "deleteDish",
  ],
  data: () => ({}),
  computed: {
    ...mapGetters({
      profileTastesLoaded: "taste/getProfileTastesLoaded",
    }),
  },
  methods: {
    onSetRecipe() {},
  },
  components: { DayPlannerRecipe, DislikeRecipe },
};
</script>

<style scoped lang="scss"></style>
