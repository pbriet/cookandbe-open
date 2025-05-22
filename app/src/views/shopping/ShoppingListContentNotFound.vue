<template>
  <div class="op-page">
    <div class="op-page-title">
      <h1>Cette liste de courses a été supprimée</h1>
    </div>

    <div class="op-page-content">
      Désolé, cette liste de courses n'est plus accessible.<br /><br />
      <router-link class="btn btn-success" :to="{ name: 'Shopping' }">Retour</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "ShoppingListContentNotFound",
  props: [],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
