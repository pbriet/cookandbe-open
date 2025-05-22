<template>
  <div class="op-block-image" ref="root">
    <div>
      <div class="op-block-image-overlay">
        <!-- This content will be displayed over the image -->
        <div
          :style="iconStyle"
          class="d-flex align-items-center justify-content-center overlay-icon-top-left op-font-bg-red"
          v-if="warningIcon && disc && !hideIcons"
        >
          <FontAwesomeIcon :icon="warningIcon" />
        </div>
        <div
          :style="iconStyle"
          class="d-flex align-items-center justify-content-center overlay-icon-top-right op-font-bg-female"
          v-if="fondnessIcon && disc && !hideIcons"
        >
          <FontAwesomeIcon :icon="fondnessIcon" />
        </div>
        <div class="overlay-table" :class="{ disc: disc }">
          <slot></slot>
        </div>
      </div>
      <div ref="content" class="op-block-image-body" :class="{ disc: disc, border: withBorder }">
        <img ref="img" itemprop="image" :src="getSrc" :title="getTitle" :alt="`Photo recette : ${getTitle || ''}`" />
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import $ from "jquery";

import {
  IMG_BRAND,
} from "@/config.js";

/*
 * This component displays a recipe image
 */
export default {
  name: "RecipeImg",
  props: ["recipe", "url", "withBorder", "title", "disc", "hideIcons"],
  data() {
    return {
      iconStyle: { display: "none" },
      fondnessIcon: null,
    };
  },
  mounted() {
    this.reset(this.recipe);
    this.$refs.img.onload = this.computeImgSize;
    window.addEventListener("resize", this.computeImgSize);
  },
  computed: {
    ...mapGetters({
      isLoggedIn: "user/isLoggedIn",
      isDisliked: "recipeFilter/isDisliked",
      getWarnings: "recipeFilter/getWarnings",
    }),
    ratio() {
      if (this.disc) {
        return 1;
      } else {
        return 1.6; // Rapport largeur / hauteur
      }
    },
    getTitle() {
      if (this.title) {
        return this.title;
      }
      return this.recipe?.name;
    },
    getSrc() {
      if (this.url) {
        return this.url;
      }
      const recipe = this.recipe;
      if (!recipe || recipe.photo === undefined) {
        return undefined;
      } else if (recipe.photo === null) {
        return '/' + IMG_BRAND + '/img/unavailable.png';
      }
      return recipe.photo;
    },
    warningIcon() {
      const warnings = this.$store.getters["recipeFilter/getWarnings"](this.recipe?.id);
      if (warnings?.length > 0) {
        return warnings[0].icon;
      }
      return null;
    },
  },
  watch: {
    recipe: {
      handler(newRecipe) {
        this.reset(newRecipe);
      },
      deep: true,
    },
    url() {
      this.computeImgSize();
    },
  },
  methods: {
    ...mapActions({
      computeRecipeWarnings: "recipeFilter/computeRecipeWarnings",
    }),
    reset(recipe) {
      this.fondnessIcon = null;
      if (!recipe || !recipe.id) {
        this.iconStyle = { display: "none" };
        return;
      }
      if (!this.isLoggedIn) {
        return;
      }

      this.computeRecipeWarnings({ recipeId: recipe.id });
      if (this.isDisliked(recipe.id)) {
        this.fondnessIcon = ["far", "thumbs-down"];
      }
    },
    computeImgSize() {
      const root = $(this.$refs.root);
      if (root.width() <= 0 || root.height() <= 0) {
        if (root.height() <= 0) {
          setTimeout(this.computeImgSize, 100);
        }
        // Patch preventing the bootstrap modal to crunch the picture
        return;
      }
      // Retrieving sizes
      const currentWidth = root.width();
      let targetWidth = 0;
      let targetHeight = 0;
      if (this.disc) {
        // Round image
        targetHeight = currentWidth;
        targetWidth = currentWidth;
      } else {
        // Rectangle image
        targetHeight = Math.floor(currentWidth / this.ratio);
        targetWidth = currentWidth;
      }
      // Create new offscreen image to test native size
      const nativeImage = new Image();
      nativeImage.src = this.getSrc;
      // Get accurate native size
      const nativeWidth = nativeImage.width;
      const nativeRatio = nativeWidth / nativeImage.height;

      // Jim 15/09/2015: these 2 lines are breaking the image size when resizing the browser...
      // root.css('width', targetWidth);
      // root.css('height', targetHeight);
      // Setting new sizes
      const content = $(this.$refs.content);
      content.css("width", targetWidth);
      content.css("height", targetHeight);
      this.iconStyle = { "font-size": targetWidth / 6 + "px" };

      const img = $(this.$refs.img);
      if (nativeRatio > this.ratio) {
        // Image is too wide, fitting the height
        const widthDifference = targetWidth - targetHeight * nativeRatio;
        img.css("height", targetHeight);
        img.css("width", Math.floor(targetHeight * nativeRatio));
        img.css("margin-left", widthDifference / 2);
      } else {
        // Image is too high, fitting the width
        const heightDifference = targetHeight - targetWidth / nativeRatio;
        img.css("width", targetWidth);
        img.css("height", Math.floor(targetWidth / nativeRatio));
        img.css("margin-top", heightDifference / 2);
      }
    },
  },
  components: {},
};
</script>

<style lang="scss">
.op-block-image {
  position: relative;
  display: block;
  margin: auto;
  padding: 0px;
  clear: both;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;

  .op-block-image-body {
    position: relative;
    z-index: 0;
    padding: 0px;
    margin: 0px;
    overflow: hidden;

    img {
      width: 100%;
    }
  }

  .disc {
    border-radius: $op-radius-infinity;
  }

  .border {
    border: $op-recipe-border-width solid $op-color-border;
  }

  .op-block-image-overlay {
    z-index: 10;
    position: absolute;
    width: 100%;
    height: 100%;
  }

  &:after {
    @extend .clearfix;
  }
}
a .op-block-image {
  &:hover {
    opacity: 0.7;
  }
}
</style>
