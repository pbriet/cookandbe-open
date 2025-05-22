<template>
  <div id="config-progression-bar" class="d-none d-sm-block container" v-if="configMode">
    <div class="row bs-wizard">
      <div v-for="step in steps" :class="`col-${colSize} bs-wizard-step ${step.status}`" :key="step.name">
        <div class="text-center bs-wizard-stepnum">{{ step.name }}</div>
        <div class="progress"><div class="progress-bar"></div></div>
        <router-link :to="step.route" class="bs-wizard-dot"></router-link>
        <div class="bs-wizard-info text-center">{{ step.description }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  name: "ConfigProgression",
  computed: {
    colSize() {
      return 12 / this.steps.length;
    },
    ...mapGetters({
      configMode: "configStage/configMode",
      steps: "configStage/configSteps",
    }),
  },
};
</script>

<style scoped lang="scss">
/*
 * Adapted from bootsnipp
 */

/* Form Wizard */
.bs-wizard {
  padding: 0 0 10px 0;
  .bs-wizard-step {
    padding: 0;
    position: relative;
  }
}
.bs-wizard > .bs-wizard-step + .bs-wizard-step {
}
.bs-wizard > .bs-wizard-step .bs-wizard-stepnum {
  color: #595959;
  font-size: 16px;
  margin-bottom: 5px;
}
.bs-wizard > .bs-wizard-step .bs-wizard-info {
  color: #999;
  font-size: 14px;
}
.bs-wizard > .bs-wizard-step > .bs-wizard-dot {
  position: absolute;
  width: 30px;
  height: 30px;
  display: block;
  background-color: lighten($op-color-lime, 20%);
  top: 45px;
  left: 50%;
  margin-top: -15px;
  margin-left: -15px;
  border-radius: $op-radius-infinity;
}
.bs-wizard > .bs-wizard-step > .bs-wizard-dot:after {
  content: " ";
  width: 14px;
  height: 14px;
  border-radius: $op-radius-infinity;
  position: absolute;
  top: 8px;
  left: 8px;
}
.bs-wizard > .bs-wizard-step > .progress {
  position: relative;
  border-radius: 0px;
  height: 8px;
  box-shadow: none;
  margin: 20px 0;
}
.bs-wizard > .bs-wizard-step > .progress > .progress-bar {
  width: 0px;
  box-shadow: none;
  background-color: lighten($op-color-lime, 20%);
}
.bs-wizard > .bs-wizard-step.complete > .progress > .progress-bar {
  width: 100%;
}
.bs-wizard > .bs-wizard-step.active > .progress > .progress-bar {
  width: 50%;
}
.bs-wizard > .bs-wizard-step:first-child.active > .progress > .progress-bar {
  width: 0%;
}
.bs-wizard > .bs-wizard-step:last-child.active > .progress > .progress-bar {
  width: 100%;
}
.bs-wizard > .bs-wizard-step.disabled > .bs-wizard-dot {
  background-color: #d5d5d5;
}
.bs-wizard > .bs-wizard-step.disabled > .bs-wizard-dot:after {
  opacity: 0;
}
.bs-wizard > .bs-wizard-step.active > .bs-wizard-dot:after {
  background-color: darken($op-color-lime, 5%);
}
.bs-wizard > .bs-wizard-step:first-child > .progress {
  left: 50%;
  width: 50%;
}
.bs-wizard > .bs-wizard-step:last-child > .progress {
  width: 50%;
}
.bs-wizard > .bs-wizard-step.disabled a.bs-wizard-dot {
  pointer-events: none;
}

/*
 * Pure Cook&Be
 */

#config-progression-bar {
  .progress {
    background-color: #d5d5d5;
  }
  background-color: lighten($op-color-lime, 50%);
  padding: 10px;
  margin-top: 0px;
  margin-bottom: 0px;
  word-break: break-word;
  color: white;

  p,
  h1,
  h2,
  h3,
  h4,
  h5,
  a {
    color: white;
  }
}
</style>
