<template>
  <ShoppingListContentNotFound v-if="notFound" />

  <div id="shopping-list-screen" class="d-print-none" v-if="!notFound">
    <ShoppingListContentScreen
      v-model:shoppingList="shoppingList"
      :nbMissingItems="nbMissingItems"
      :nbStoredItems="nbStoredItems"
      :onToggleItem="onToggleItem"
      :onDeleteCustomItem="onDeleteCustomItem"
      :iterItemDays="iterItemDays"
    />
  </div>

  <!-- Version imprimable -->
  <div id="shopping-list-print" class="d-none d-print-block">
    <PleaseWait v-if="!shoppingList" />
    <ShoppingListContentPrint
      v-if="shoppingList"
      :shoppingList="shoppingList"
      :nbMissingItems="nbMissingItems"
      :iterItemDays="iterItemDays"
    />
  </div>
</template>

<script>
import API from "@/api.js";
import { mapGetters } from "vuex";
import PleaseWait from "@/components/interface/PleaseWait.vue";
import ShoppingListContentNotFound from "./ShoppingListContentNotFound.vue";
import ShoppingListContentScreen from "./ShoppingListContentScreen.vue";
import ShoppingListContentPrint from "./ShoppingListContentPrint.vue";

export default {
  name: "ShoppingListContent",
  props: [],
  data: () => ({
    shoppingList: null,
    notFound: false,
    nbMissingItems: 0,
    nbStoredItems: 0,
  }),
  mounted() {
    this.reset();
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
    }),
  },
  methods: {
    reset() {
      this.updateShoppingList();
    },
    async updateShoppingList() {
      const shoppingListId = this.$route.params.shoppingListId;
      try {
        this.shoppingList = await API.shoppingList.get(this.userId, shoppingListId);
        this.updateItemCounts();
      } catch {
        this.notFound = true;
      }
    },
    onDeleteCustomItem(shoppingCategory, item) {
      API.shoppingItem.remove(item.id);
      if (!item.gotIt) {
        shoppingCategory.missingItems -= 1;
      }
      for (let i = 0; i < shoppingCategory.items.length; ++i) {
        if (shoppingCategory.items[i].id === item.id) {
          shoppingCategory.items.splice(i, 1);
          break;
        }
      }
    },
    onToggleItem(item) {
      if (item.gotIt) {
        this.nbMissingItems -= 1;
        this.nbStoredItems += 1;
      } else {
        this.nbMissingItems += 1;
        this.nbStoredItems -= 1;
      }
    },
    updateItemCounts() {
      let missing = 0;
      let stored = 0;
      for (const category of this.shoppingList.content) {
        missing += category.missingItems;
        stored += category.items.length - category.missingItems;
      }
      this.nbMissingItems = missing;
      this.nbStoredItems = stored;
    },
    iterItemDays(item) {
      const itemDays = [];
      let lastDay = { date: null };

      if (item.recipes) {
        for (const recipe of item.recipes) {
          if (recipe.date != lastDay.date) {
            lastDay = {
              date: recipe.date,
              quantity: recipe.quantity,
              freeze: recipe.date >= item.freezeDate,
              recipes: [],
            };
            itemDays.push(lastDay);
          } else {
            lastDay.quantity += recipe.quantity;
          }
          lastDay.recipes.push(recipe);
        }
      }
      return itemDays;
    },
  },
  components: { ShoppingListContentNotFound, ShoppingListContentScreen, ShoppingListContentPrint, PleaseWait },
};
</script>

<style scoped lang="scss"></style>
