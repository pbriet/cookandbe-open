<template>
  <div :class="bannerClass">
    <div class="full-h op-page-banner-background"></div>
  </div>
</template>

<script>
export default {
  name: "Banner",
  props: ["banner"],
  computed: {
    bannerClass() {
      return `op-page-banner-${this.banner}`;
    },
  },
};
</script>

<style scoped lang="scss">
$op-page-banner-height: 600px;
$op-page-banner-homepage-height: 600px;
$op-page-banner-gradient-height: 150px;

.op-page-banner {
  width: 100%;
  height: 100%;
  z-index: 0;
  position: fixed;
  overflow: hidden;

  @media print {
    display: none;
  }

  .op-page-banner-background {
    z-index: -1;
    position: fixed;
    width: 100%;
    background-size: cover;
    background-repeat: no-repeat;
    background-position: 50%;
    background-image: url("~@/assets/img/banners/default_blured.jpg");
  }

  .op-page-banner-fade {
    z-index: 0;
    position: fixed;
    width: 100%;
    height: $op-page-banner-gradient-height;
    margin-top: $op-page-banner-height - $op-page-banner-gradient-height;
    background: linear-gradient(to bottom, transparent, $op-color-margin);
  }
}

.op-page-banner-homepage {
  @extend .op-page-banner;
  height: $op-page-banner-homepage-height;

  .op-page-banner-background-mobile {
    display: none !important;
  }

  .op-page-banner-background-desktop {
    display: block !important;
    height: $op-page-banner-homepage-height !important;
    background-image: url(/img/banners/homepage.jpg);

    @media (min-width: $bootstrap-lg-min) {
      background-size: 100% auto;
    }
    @media (max-width: $bootstrap-md-max) {
      background-size: auto 100%;
    }
  }

  .op-page-banner-fade {
    display: inherit !important;
    margin-top: $op-page-banner-homepage-height - $op-page-banner-gradient-height;
  }
}

.op-page-banner-default {
  @extend .op-page-banner;
  .op-page-banner-background {
    @media (min-width: $bootstrap-sm-min) {
      background-image: url("~@/assets/img/banners/default_blured.jpg");
    }
  }
}

.op-page-banner-homepage {
  @extend .op-page-banner;
  .op-page-banner-background {
    @media (min-width: $bootstrap-sm-min) {
      background-image: url("~@/assets/img/banners/default.jpg");
    }
  }
}

.op-page-banner-recipe {
  @extend .op-page-banner;
  .op-page-banner-background {
    @media (min-width: $bootstrap-sm-min) {
      background-image: url("~@/assets/img/banners/recipe.jpg");
    }
  }
}

.op-page-banner-article {
  @extend .op-page-banner;
  .op-page-banner-background {
    @media (min-width: $bootstrap-sm-min) {
      background-image: url("~@/assets/img/banners/article.jpg");
    }
  }
}

.op-page-banner-planning {
  @extend .op-page-banner;
  .op-page-banner-background {
    @media (min-width: $bootstrap-sm-min) {
      background-image: url("~@/assets/img/banners/planning.jpg");
    }
  }
}

.op-page-banner-error {
  @extend .op-page-banner;
  .op-page-banner-background {
    @media (min-width: $bootstrap-sm-min) {
      background-image: url("~@/assets/img/banners/error.jpg");
    }
  }
}

.op-page-banner-medical {
  @extend .op-page-banner;
  .op-page-banner-background {
    @media (min-width: $bootstrap-sm-min) {
      background-image: url("~@/assets/img/banners/medical.jpg");
    }
  }
}

.op-page-banner-profile {
  @extend .op-page-banner;
  .op-page-banner-background {
    @media (min-width: $bootstrap-sm-min) {
      background-image: url("~@/assets/img/banners/profile.jpg");
    }
  }
}

.op-page-banner-shopping {
  @extend .op-page-banner;
  .op-page-banner-background {
    @media (min-width: $bootstrap-sm-min) {
      background-image: url("~@/assets/img/banners/shopping.jpg");
    }
  }
}

.op-page-banner-team {
  @extend .op-page-banner;
  .op-page-banner-background {
    @media (min-width: $bootstrap-sm-min) {
      background-image: url("~@/assets/img/banners/team.jpg");
    }
  }
}
</style>
