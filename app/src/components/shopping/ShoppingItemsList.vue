<template>
  <Dialog :open="foodTagDangerDialog" :closeBtn="true" :onClose="hideFoodTagDangerDialog">
    <div class="dialog-title-danger">
      <span class="op-icon-dlg"><FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" /></span> {{ currentTag.name }}
    </div>
    <div class="dialog-body">
      <p>
        Les aliments marqué du symbole
        <span class="op-font-red"><FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" /></span> sont à exclure de
        votre alimentation.
      </p>
      <p>
        Si vous avez récemment changé votre alimentation, nous vous conseillons d'actualiser vos idées repas afin que
        les propositions en tiennent compte.
      </p>
      <p>
        Si vous avez forcé des recettes contenant des aliments à exclure, demandez d'autres suggestions à la place ou
        achetez des aliments de substitution.
      </p>
      <div class="">
        <div class="fright btn btn-danger" @click="hideFoodTagDangerDialog">Compris</div>
      </div>
    </div>
  </Dialog>

  <Dialog :open="foodTagWarningDialog" :closeBtn="true" :onClose="hideFoodTagWarningDialog">
    <div class="dialog-title-warning">
      <span class="op-icon-dlg"><FontAwesomeIcon :icon="['fas', 'info-circle']" /></span> {{ currentTag.name }}
    </div>
    <div class="dialog-body">
      <p>
        Les articles marqués du symbole
        <span class="op-font-orange"><FontAwesomeIcon :icon="['fas', 'info-circle']" /></span> sont compatibles avec
        votre alimentation. Cependant certains producteurs peuvent les laisser entrer en contact ou les mélanger avec
        d'autres produits.
      </p>
      <p>
        En faisant vos courses, vérifiez bien sur l'étiquette de cet article
        <span class="op-font-orange">l'absence de {{ currentTag.name }}</span
        >.
      </p>
      <div class="">
        <div class="fright btn btn-warning" @click="hideFoodTagWarningDialog">Compris</div>
      </div>
    </div>
  </Dialog>

  <div class="op-shopping-items-list row d-block me-0 pe-0">
    <div
      class="col-12 col-md-6 shopping-category fleft"
      v-for="shoppingCategory in shoppingList.content.filter((c) => c.items.length > 0)"
      :key="shoppingCategory.foodType"
    >
      <div class="col-12 shopping-category-title fleft" :style="buildCategoryStyle(shoppingCategory)">
        <h3>
          {{ shoppingCategory.foodType }}
          <br class="d-sm-none" />
          <small v-if="nbCategoryItems(shoppingCategory) === 0">(aucun article dans la liste)</small>
          <small v-if="nbCategoryItems(shoppingCategory) === 1">(1 article dans la liste)</small>
          <small v-if="nbCategoryItems(shoppingCategory) > 1"
            >({{ nbCategoryItems(shoppingCategory) }} articles dans la liste)</small
          >
        </h3>
      </div>
      <span class="clearfix" />
      <div class="d-sm-none">
        <ShoppingListXs
          :shoppingCategory="shoppingCategory"
          :getItemClass="getItemClass"
          :isCustomItem="isCustomItem"
          :onEditQuantity="onEditQuantity"
          :onSelectItem="onSelectItem"
          :onToggleItem="toggleItem"
          :onDeleteCustomItem="onDeleteCustomItem"
          :onShowFrozenInfos="onShowFrozenInfos"
          :iterItemDays="iterItemDays"
          :onShowDietTagInfos="onShowDietTagInfos"
        />
      </div>
      <div class="d-none d-sm-block">
        <ShoppingListXl
          :shoppingCategory="shoppingCategory"
          :getItemClass="getItemClass"
          :isCustomItem="isCustomItem"
          :onEditQuantity="onEditQuantity"
          :onSelectItem="onSelectItem"
          :onToggleItem="toggleItem"
          :onDeleteCustomItem="onDeleteCustomItem"
          :onShowFrozenInfos="onShowFrozenInfos"
          :iterItemDays="iterItemDays"
          :onShowDietTagInfos="onShowDietTagInfos"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import ShoppingListXs from "@/components/shopping/ShoppingListXs.vue";
import ShoppingListXl from "@/components/shopping/ShoppingListXl.vue";
import Dialog from "@/components/interface/Dialog.vue";
import API from "@/api.js";

// For background colors
const CATEGORY_DEFAULT_COLOR = "128, 128, 0, 0.11";

const CATEGORIES_COLOR = {
  Autre: "128, 128, 0, 0.11",
  "Viande et charcuterie": "255, 0, 0, 0.11",
  "Fruits et légumes": "50, 255, 0, 0.18",
  "Poissons et fruits de mer": "0, 0, 255, 0.11",
  Surgelés: "0, 240, 255, 0.22",
  "Rayon frais": "168, 0, 255, 0.11",
  "Produits laitiers": "255, 250, 220, 0.80",
  "Pain et viennoiserie": "255, 150, 0, 0.20",
  Conserves: "0, 0, 128, 0.11",
  Boissons: "0, 215, 170, 0.20",
  "Soupes et potages": "100, 150, 50, 0.22",
  "Produits bébés": "128, 0, 128, 0.11",
  "Petit déjeuner et boissons chaudes": "255, 200, 0, 0.20",
  "Gateaux et confiseries": "255, 0, 144, 0.17",
  "Pâtes, riz et féculents": "255, 255, 0, 0.22",
  "Epicerie sucrée": "128, 0, 128, 0.14",
  "Condiments et sauces": "222, 0, 51, 0.15",
  Epicerie: "22, 0, 72, 0.15",
  "Rayon diététique": "70, 154, 0, 0.20",
  Cuisine: "0, 0, 0, 0.10",
};

export default {
  name: "ShoppingItemsList",
  props: [
    "shoppingList",
    "filter",
    "onEditQuantity",
    "onSelectItem",
    "onToggleItem",
    "onDeleteCustomItem",
    "onShowFrozenInfos",
    "iterItemDays",
  ],
  data: () => ({
    delay: 0,
    currentTag: {},
    foodTagDangerDialog: false,
    foodTagWarningDialog: false,
  }),
  computed: {
    displayStock() {
      return this.filter === "stock";
    },
    ...mapGetters({
      user: "user/get",
    }),
  },
  methods: {
    nbCategoryItems(category) {
      if (this.displayStock) {
        return category.items.length - category.missingItems;
      } else {
        return category.missingItems;
      }
    },
    isCustomItem(item) {
      return item.forcedName;
    },
    toggleItem(shoppingCategory, item) {
      item.movingStart = true;
      setTimeout(() => {
        item.movingStart = false;
        if (item.gotIt) {
          shoppingCategory.missingItems += 1;
        } else {
          shoppingCategory.missingItems -= 1;
        }
        API.shoppingList.toggleItem(this.user.id, item.id);
        item.gotIt = !item.gotIt;
        this.onToggleItem && this.onToggleItem(item);
        item.movingEnd = true;
        setTimeout(function () {
          item.movingEnd = false;
        }, 500);
      }, 500);
    },
    getItemClass(item) {
      const classes = [];
      if (item.dietExclusions) {
        classes.push("item-excluded");
      } else if (item.dietWarnings) {
        classes.push("item-forewarned");
      }
      if (!item.gotIt) {
        classes.push("item-enabled");
      }
      if (item.gotIt) {
        classes.push("item-disabled");
      }
      if (item.movingStart) {
        classes.push("moving-start");
      }
      if (item.movingEnd) {
        classes.push("moving-end");
      }
      return classes.join(" ");
    },
    buildCategoryStyle(shoppingCategory) {
      if (!shoppingCategory.cssStyle) {
        let color = CATEGORY_DEFAULT_COLOR;
        if (CATEGORIES_COLOR[shoppingCategory.foodType]) {
          color = CATEGORIES_COLOR[shoppingCategory.foodType];
        } else {
          console.log("Warning: no color for shopping category '" + shoppingCategory.foodType + "'");
        }
        shoppingCategory.cssStyle = { "background-color": "rgba(" + color + ")" };
      }
      return shoppingCategory.cssStyle;
    },
    onShowDietTagInfos(tagType, tagIds) {
      this.currentTag.type = tagType;
      this.currentTag.name = tagIds.join(", ");
      if (tagType == "danger") {
        this.foodTagDangerDialog = true;
      } else {
        this.foodTagWarningDialog = true;
      }
    },
    hideFoodTagDangerDialog() {
      this.foodTagDangerDialog = false;
    },
    hideFoodTagWarningDialog() {
      this.foodTagWarningDialog = false;
    },
  },
  components: { ShoppingListXs, ShoppingListXl, Dialog },
};
</script>

<style lang="scss">
.op-shopping-items-list {
  .shopping-category {
  }

  .shopping-category {
    @media (max-width: $bootstrap-xs-max) {
      padding-left: 5px !important;
      padding-right: 5px !important;
    }
  }

  .item-quantity {
    @media (max-width: $bootstrap-xs-max) {
      text-align: left;
      width: 100%;
    }
    @media (min-width: $bootstrap-sm-min) {
      text-align: right;
      width: 200px;
    }
  }

  .item-name {
    width: 100%;
    padding: 2px 0px;

    small {
      width: 100%;
    }
  }

  ul {
    padding-left: 0px;
    list-style: none;
    clear: both;
  }

  .shopping-item {
    padding-top: 2px;
    padding-bottom: 2px;
    &:after {
      @extend .clearfix;
    }

    @media (max-width: $bootstrap-xs-max) {
      font-size: $op-font-lg;
    }
    @media (min-width: $bootstrap-sm-min) {
      font-size: $op-font-md;
    }

    &.item-enabled,
    &.item-enabled > .op-cell {
      border-bottom: 1px solid #f0f0f0;
    }
    &.item-disabled,
    &.item-disabled > .op-cell {
      border-bottom: 1px solid #ffffff;
    }
  }

  .shopping-item.item-enabled {
    background-color: #ffffff;
    color: $op-color-text-main;
    a {
      color: $op-color-text-main;
    }
  }
  .shopping-item.item-disabled {
    background-color: #f0f0f0;
    color: $op-color-text-soft;
    a {
      color: $op-color-text-soft;
    }
  }
  .shopping-item.item-forewarned {
    @extend .op-font-orange;
    .info-icon {
      @extend .op-font-orange;
    }
    .clickable-text {
      @extend .clickable-text-warning;
    }
    .clickable-text-btn {
      border-color: $op-color-orange;
      @extend .clickable-text-warning;
    }
  }
  .shopping-item.item-excluded {
    @extend .op-font-red;
    .info-icon {
      @extend .op-font-red;
    }
    .clickable-text {
      @extend .clickable-text-danger;
    }
    .clickable-text-btn {
      border-color: $op-color-red;
      @extend .clickable-text-danger;
    }
  }

  .moving-start {
    animation: opFlipOutX 0.5s linear;
    -webkit-animation: opFlipOutX 0.5s linear;
  }

  .moving-end {
    animation: opFlipInX 0.5s linear;
    -webkit-animation: opFlipInX 0.5s linear;
  }

  .item-icon-cell {
    text-align: center;
    vertical-align: middle;

    @media (max-width: $bootstrap-xs-max) {
      width: 45px;
      font-size: $op-font-xl;
    }
    @media (min-width: $bootstrap-sm-min) {
      width: 35px;
      font-size: $op-font-md;
    }
  }

  .item-options {
    width: 80px;
  }
  .item-options-admin {
    width: 95px;
  }
  .clickable-text {
    padding: 3px 7px;
    border-radius: $op-radius-md;

    &:hover {
      text-decoration: none;
      background-color: $op-color-grey-dark !important;
      border: none;
      cursor: pointer;
      color: white !important;

      .gram-equivalent {
        color: $op-color-grey-light !important;
      }
    }
  }

  .clickable-text-btn {
    @extend .clickable-text;
    border: 1px solid $op-color-border;
    background-color: white;

    &:hover {
      border: 1px solid transparent;
    }
  }

  .clickable-text-danger {
    color: $op-color-red !important;

    &:hover {
      background-color: $op-color-red !important;
      color: white !important;
    }
  }

  .clickable-text-warning {
    color: $op-color-orange !important;

    &:hover {
      background-color: $op-color-orange !important;
      color: white !important;
    }
  }

  .gram-equivalent {
    color: $op-color-grey-dark;
    white-space: nowrap;
  }

  .empty-list {
  }

  .frozen-shopping-item {
    height: 25px;
    margin: -5px 0px -5px 7px;
  }
}
</style>
