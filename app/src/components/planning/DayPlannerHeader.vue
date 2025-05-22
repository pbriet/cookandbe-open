<template>
  <div
    class="alert alert-warning op-font-lg op-day-planner-header"
    v-if="dayStatus && dayStatus.metaplanningChanged && !dayStatus.shoppingListId && dayStatus.validated"
  >
    <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" /> Ces suggestions ne prennent pas en compte vos récentes
    modifications de la configuration.
    <div class="col-12 op-vs-10">
      <button class="btn btn-secondary fright" @click="updateFromMeta">Mettre à jour</button>
    </div>
    <span class="clearfix" />
  </div>

  <div class="op-info" v-if="dayStatus && dayStatus.shoppingListId">
    <span class="info-icon">
      <FontAwesomeIcon :icon="['fas', 'info-circle']" />
    </span>
    <p style="display: inline-block">
      Cette journée est incluse dans une liste de courses.<br />
      Supprimer la liste pour la modifier à nouveau.
    </p>
    <div class="op-vs-5 fright col-12 col-sm-4" style="display: inline-block">
      <router-link
        class="btn btn-secondary fright"
        :to="{ name: 'ShoppingListContent', params: { shoppingListId: dayStatus.shoppingListId } }"
      >
        <FontAwesomeIcon :icon="['fas', 'shopping-basket']" />
        Voir la liste de courses
      </router-link>
    </div>
    <span class="clearfix" />
  </div>
</template>

<script>
export default {
  name: "DayPlannerHeader",
  props: ["dayStatus", "date", "onSkipDay", "onMoveToNextDay", "onModifyMeals", "updateFromMeta"],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss">
.op-day-planner-header {
  margin-left: 10px;
  display: block;

  .shopping-list-btn {
    margin-bottom: 5px;
    width: 100%;
  }
}
</style>
