<template>
  <div id="ustensils-editor">
    <div class="row ustensil-category-panel" v-for="category in ustensilCategories" :key="category.id">
      <div class="col-12">
        <h3>{{ category.name }}</h3>
      </div>
      <div
        v-for="ustensil in ustensils"
        :key="ustensil.id"
        v-show="category.id == ustensil.category"
        class="ustensil-item btn"
        @click="toggleUstensil(ustensil)"
        :disabled="ustensil.modifying"
        :class="{ 'btn-info': ustensil.selected, 'btn-secondary': !ustensil.selected }"
      >
        <FontAwesomeIcon :icon="['fas', 'check']" v-if="ustensil.selected" />
        <FontAwesomeIcon :icon="['fas', 'times']" v-if="!ustensil.selected" />
        {{ ustensil.name }}
      </div>
    </div>
    <div class="clearfix" />
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { includes } from "lodash";

/*
 * Component for displaying the user ustensils
 */
export default {
  name: "EquipmentEditor",
  props: ["userUstensils", "onToggleUstensil"],
  data: () => ({
    ustensils: [],
  }),
  mounted() {
    this.initUstensils();
  },
  watch: {
    userUstensils: {
      handler() {
        this.initUstensils();
      },
      deep: true,
    },
  },
  computed: {
    ...mapGetters({
      ustensilCategories: "equipment/getCategories",
      allUstensils: "equipment/getUstensils",
    }),
  },
  methods: {
    initUstensils() {
      this.ustensils = [];
      if (!this.userUstensils) {
        return;
      }
      for (let i = 0; i < this.allUstensils.length; ++i) {
        const ustensil = this.allUstensils[i];
        const userUstensil = {
          id: ustensil.id,
          name: ustensil.name,
          selected: includes(this.userUstensils, ustensil.id),
          category: ustensil.category,
          modifying: false,
        };
        this.ustensils.push(userUstensil);
      }
    },
    toggleUstensil(ustensil) {
      ustensil.modifying = true;
      ustensil.selected = !ustensil.selected;
      this.onToggleUstensil(ustensil, ustensil.selected).then(() => {
        ustensil.modifying = false;
      });
    },
  },
  components: {},
};
</script>

<style scoped lang="scss">
#ustensils-editor {
  $ustensil-button-width: 200px;
  $ustensil-margin-width: 2px;
  $ustensil-button-area-width: 206px;

  .ustensil-item {
    width: $ustensil-button-width;
    margin: $ustensil-margin-width;
    text-align: left;
    display: inline-block;
  }

  .ustensil-category-panel {
    margin: auto;

    @media (max-width: 480px) {
      max-width: $ustensil-button-area-width;
    }
    @media (min-width: 480px) and (max-width: 720px) {
      max-width: $ustensil-button-area-width * 2;
    }
    @media (min-width: 720px) and (max-width: 960px) {
      max-width: $ustensil-button-area-width * 3;
    }
    @media (min-width: 960px) {
      max-width: $ustensil-button-area-width * 4;
    }
  }

  .ustensil-selected {
    background-color: #65c47f;
  }

  .svg-inline--fa {
    width: 0.8em;
  }
}
</style>
