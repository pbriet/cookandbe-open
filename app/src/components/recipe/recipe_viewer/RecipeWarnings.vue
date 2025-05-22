<template>
  <div class="col-12" v-for="warning in recipeWarnings" :key="warning.htmlMessage">
    <div class="alert" :class="{ 'alert-danger': warning.level >= 3, 'alert-warning': warning.level <= 2 }">
      <div class="row">
        <div
          :class="{
            'col-12 col-sm-7 col-md-8': warning.actionUrl && warning.actionCaption,
            'col-12': !(warning.actionUrl && warning.actionCaption),
          }"
        >
          <span class="op-icon-lg me-1">
            <FontAwesomeIcon :icon="warning.icon" />
          </span>
          <span v-html="warning.htmlMessage"></span>
        </div>
        <div class="fright col-12 col-sm-5 col-md-4 text-end" v-if="warning.actionUrl && warning.actionCaption">
          <a class="btn-block" @click="gotoUrl(warning.actionUrl)">
            <FontAwesomeIcon :icon="['far', 'hand-point-right']" />
            {{ warning.actionCaption }}
          </a>
        </div>
      </div>
      <span class="clearfix" />
    </div>
  </div>
</template>

<script>
export default {
  name: "RecipeWarnings",
  props: ["recipeWarnings"],
  data: () => ({}),
  computed: {},
  methods: {
    gotoUrl(url) {
      this.$router.push(url);
    },
  },
  components: {},
};
</script>

<style scoped lang="scss"></style>
