<template>
  <div class="recipe-edit-toolbar op-vs">
    <div class="alert alert-danger op-font-lg container-fluid" v-if="errorStatus" v-html="errorStatus" />

    <div class="btn-toolbar center fright" role="toolbar">
      <div class="btn-group me-2">
        <BackButton :defaultHref="{ name: 'Cookbook' }">Retour</BackButton>
      </div>
      <div class="btn-group">
        <button class="btn btn-success" @click="saveRecipe">Sauvegarder</button>
      </div>
    </div>
    <div class="clearfix"></div>
  </div>
</template>

<script>
import BackButton from "@/components/interface/BackButton.vue";

export default {
  name: "RecipeEditToolbar",
  props: ["saveRecipe", "errorStatus"],
  data: () => ({}),
  computed: {},
  methods: {},
  components: { BackButton },
};
</script>

<style scoped lang="scss">
.recipe-edit-toolbar {
  .btn-toolbar {
    margin: auto;
  }
  .recipe-titlte {
    font-size: 22pt;
    word-break: break-all;
  }
  .btn {
    width: 120px;
    margin-bottom: 5px;
  }
}
</style>
