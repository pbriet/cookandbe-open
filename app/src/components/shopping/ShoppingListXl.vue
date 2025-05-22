<template>
  <div class="op-table">
    <div class="shopping-item op-row" v-for="item in shoppingCategory.items" :key="item.id" :class="getItemClass(item)">
      <!-- Quantity -->
      <div class="op-cell item-quantity">
        <span class="op-table" v-if="item.gotIt">
          <span class="op-cell">
            <ShoppingItemQuantity :item="item" />
          </span>
          <span class="item-icon-cell op-cell">&nbsp;</span>
        </span>
        <a class="clickable-text op-table" @click.prevent="onEditQuantity(item, 'quantity')" v-if="!item.gotIt">
          <span class="op-cell">
            <ShoppingItemQuantity :item="item" />
          </span>
          <span class="item-icon-cell op-cell"><FontAwesomeIcon :icon="['fas', 'pencil-alt']" /></span>
        </a>
      </div>

      <!-- Name -->
      <div class="item-name op-cell">
        <div class="op-table">
          <a
            class="op-cell item-icon-cell info-icon"
            @click.prevent="onShowDietTagInfos('danger', item.dietExclusions)"
            v-if="item.dietExclusions"
          >
            <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" />
          </a>
          <a
            class="op-cell item-icon-cell info-icon"
            @click.prevent="onShowDietTagInfos('warning', item.dietWarnings)"
            v-if="item.dietWarnings && !item.dietExclusions"
          >
            <FontAwesomeIcon :icon="['fas', 'info-circle']" />
          </a>
          <div class="op-cell">
            <a class="op-table clickable-text" v-if="!item.forcedName" @click.prevent="onSelectItem(item)">
              <span class="op-cell">{{ item.food.name }}</span>
            </a>
            <a class="op-table clickable-text" v-if="item.forcedName" @click.prevent="onEditQuantity(item, 'name')">
              <span class="op-cell">{{ item.forcedName }}</span>
            </a>
          </div>
        </div>
        <small v-if="item.freezeWarning">
          <div class="op-hs-15" v-for="day in iterItemDays(item)" :key="day.date">
            <span
              ><FontAwesomeIcon :icon="['fas', 'caret-right']" />
              {{ DateTime.fromISO(day.date).setLocale("fr").toFormat("EEEE dd MMMM") }} - {{ day.quantity }} g</span
            >
            <a @click.prevent="onShowFrozenInfos" v-if="day.freeze"
              ><img width="20" src="@/assets/img/shopping/snowflake.png" class="ms-1"
            /></a>
          </div>
        </small>
      </div>

      <!-- Options -->
      <div class="op-cell text-end item-options">
        <a @click.prevent="onToggleItem(shoppingCategory, item)" class="clickable-text-btn">
          <span v-if="!item.gotIt">
            <FontAwesomeIcon :icon="['fas', 'minus']" class="me-1" />
            <span class="d-none d-sm-inline">Retirer</span>
          </span>
          <span v-if="item.gotIt">
            <FontAwesomeIcon :icon="['fas', 'plus']" class="me-1" />
            <span class="d-none d-sm-inline">Ajouter</span>
          </span>
        </a>
      </div>
      <div class="op-cell text-end item-options" v-if="isCustomItem(item)">
        <a
          @click.prevent="onDeleteCustomItem(shoppingCategory, item)"
          class="clickable-text clickable-text-danger text-nowrap"
        >
          <FontAwesomeIcon :icon="['fas', 'trash']" class="me-1" />
          <span class="d-none d-sm-inline">Supprimer</span>
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import { DateTime } from "luxon";
import ShoppingItemQuantity from "@/components/shopping/ShoppingItemQuantity.vue";

export default {
  name: "ShoppingListXl",
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
