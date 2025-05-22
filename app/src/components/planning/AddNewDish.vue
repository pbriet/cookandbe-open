<template>
  <div class="add-new-dish">
    <div class="dialog-title">Choix du plat à ajouter</div>
    <div class="dialog-body">
      <div class="col-12 col-sm-4" v-for="dishType in dishTypes" :key="dishType.id">
        <div class="dish-type-option container-fluid text-center" @click="addNewDish(dishType)">
          <FontAwesomeIcon :icon="['fas', 'plus']" />
          <span>{{ dishType.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { each } from "lodash";
import API from "@/api.js";

/*
 * This component displays options for the creation of a new dish, and creates one
 */
export default {
  name: "AddNewDish",
  props: ["mealslot", "onCreated"],
  data: () => ({
    dishTypes: [],
  }),
  mounted() {
    this.reset(this.mealslot);
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
      isExcludedDishtype: "diet/isExcludedDishtype",
    }),
  },
  watch: {
    mealslot: {
      handler(newValue) {
        // When mealslot is initialized, or changes, update the data
        if (newValue) {
          this.reset(newValue);
        }
      },
      deep: true,
    },
  },
  methods: {
    async reset(mealslot) {
      const data = await API.dishType.fromMealType(mealslot.mealSlot.mealType.id);
      this.dishTypes = [];
      each(data.dishTypes, (dt) => {
        if (this.isExcludedDishtype(dt.name)) {
          return;
        }
        this.dishTypes.push(dt);
      });
    },
    async addNewDish(dishType) {
      await API.userDay.addDish(this.userId, this.mealslot.mealSlot.id, { dishTypeId: dishType.id });
      this.onCreated(dishType.id);
    },
  },
  components: {},
};
</script>

<style lang="scss">
.add-new-dish {
  color: $op-color-text-main;

  $line_height: 30px;

  .dish-type-option {
    height: 2 * $line_height;
    border: $op-page-content-border-width solid $op-color-border;
    margin-bottom: 10px;

    svg {
      margin-right: 5px;
      font-size: $op-font-xl;
    }

    & > span {
      line-height: $line_height;
    }
  }

  .dish-type-option:hover {
    cursor: pointer;
    background-color: $op-color-lime;
    color: white;
  }
}
</style>
