<template>
  <div class="op-please-wait">
    <div class="please-wait-table" v-if="waiting">
      <div>
        <img src="~@/assets/img/please-wait.gif" />
        <div class="please-wait-caption">{{ caption }}</div>
      </div>
    </div>
    <span class="clearfix" />
    <div v-if="!waiting">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: "PleaseWait",
  props: {
    until: {},
    caption: {
      default: "Chargement en cours...",
    },
  },
  computed: {
    waiting() {
      return this.until === undefined || this.until === null || this.until === false;
    },
  },
};
</script>

<style scoped lang="scss">
.op-please-wait {
  .please-wait-table {
    width: 100%;
    height: 100%;
    padding: 15px;
    display: table;

    & > div {
      display: table-cell;
      height: 100%;
      text-align: center;
      vertical-align: middle;
    }

    .please-wait-caption {
      padding-top: 10px;
    }

    img {
      width: 200px;
    }
  }
}
</style>
