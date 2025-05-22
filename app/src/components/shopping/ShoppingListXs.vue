<template>
  <ul>
    <li class="op-hs-5 shopping-item" v-for="item in shoppingCategory.items" :key="item.id" :class="getItemClass(item)">
      <div class="op-table">
        <div class="op-cell" style="width: 100%">
          <!-- Infos -->
          <a
            class="info-icon"
            @click.prevent="onShowDietTagInfos('danger', item.dietExclusions)"
            v-if="item.dietExclusions"
          >
            <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" />
          </a>
          <a
            class="info-icon"
            @click.prevent="onShowDietTagInfos('warning', item.dietWarnings)"
            v-if="item.dietWarnings && !item.dietExclusions"
          >
            <FontAwesomeIcon :icon="['fas', 'info-circle']" />
          </a>

          <!-- Quantity -->
          <span v-if="item.gotIt">
            <span data-ng-include src="'/public/shopping/list_content/shopping_items_list/item_quantity.html'"> </span>
          </span>
          <a @click.prevent="onEditQuantity(item, 'quantity')" class="clickable-text" v-if="!item.gotIt">
            <FontAwesomeIcon :icon="['fas', 'pencil-alt']" class="me-1" />
            <ShoppingItemQuantity :item="item" />
          </a>

          <!-- Name -->
          <a class="clickable-text" v-if="!item.forcedName" @click.prevent="onSelectItem(item)">
            {{ item.food.name }}
          </a>
          <a class="clickable-text" v-if="item.forcedName" @click.prevent="onEditQuantity(item, 'name')">
            {{ item.forcedName }}
          </a>
          <div v-if="item.freezeWarning">
            <small class="col-12" v-for="day in iterItemDays(item)" :key="day.date">
              <span
                ><FontAwesomeIcon :icon="['fas', 'caret-right']" />
                {{ DateTime.fromISO(day.date).setLocale("fr").toFormat("EEEE dd MMMM") }} - {{ day.quantity }} g</span
              >
              <a @click.prevent="onShowFrozenInfos" v-if="day.freeze"
                ><img width="20" src="@/assets/img/shopping/snowflake.png" class="ms-1"
              /></a>
            </small>
          </div>
        </div>

        <!-- Options -->
        <a
          @click.prevent="onToggleItem(shoppingCategory, item)"
          class="clickable-text-btn op-cell item-icon-cell"
          v-if="!item.gotIt"
        >
          <FontAwesomeIcon :icon="['fas', 'minus']" />
        </a>
        <a
          @click.prevent="onToggleItem(shoppingCategory, item)"
          class="clickable-text-btn op-cell item-icon-cell"
          v-if="item.gotIt"
        >
          <FontAwesomeIcon :icon="['fas', 'plus']" />
        </a>
        <a
          @click.prevent="onDeleteCustomItem(shoppingCategory, item)"
          class="clickable-text clickable-text-danger op-cell item-icon-cell"
          v-if="isCustomItem(item)"
        >
          <FontAwesomeIcon :icon="['fas', 'trash']" />
        </a>
      </div>
    </li>
  </ul>
</template>

<script>
import { DateTime } from "luxon";
import ShoppingItemQuantity from "@/components/shopping/ShoppingItemQuantity.vue";

export default {
  name: "ShoppingListXs",
  props: [
    "shoppingCategory",
    "getItemClass",
    "isCustomItem",
    "onEditQuantity",
    "onSelectItem",
    "onToggleItem",
    "onDeleteCustomItem",
    "iterItemDays",
    "onShowFrozenInfos",
    "onShowDietTagInfos",
  ],
  data: () => ({
    DateTime,
  }),
  computed: {},
  methods: {},
  components: { ShoppingItemQuantity },
};
</script>

<style scoped lang="scss"></style>
