<template>
  <div>
    <div @mouseleave="mouseover.value = null">
      <span
        v-for="index in 3"
        :key="index"
        @mouseover="mouseover.value = index - 1"
        @click="selectValue(index)"
        :class="
          (index <= value && !mouseover.value && mouseover.value != 0) || index - 1 <= mouseover.value
            ? selectedCls
            : notSelectedCls
        "
      >
      </span>
    </div>
    <div>
      {{ getCaption }}
    </div>
  </div>
</template>

<script>
export default {
  name: "ImgSelector",
  props: ["selectedCls", "notSelectedCls", "value", "captions"],
  data: () => ({
    mouseover: {},
  }),
  computed: {
    getCaption() {
      let pos = 0;
      if (this.mouseover.value !== null && this.mouseover.value !== undefined) {
        pos = this.mouseover.value;
      } else {
        pos = this.value - 1;
      }
      return this.captions[pos];
    },
  },
  methods: {
    selectValue(value) {
      this.$emit("update:value", value);
    },
  },
  components: {},
};
</script>

<style scoped lang="scss">
.meat-full {
  background: url("~@/assets/img/config/meat-full.png") 30px no-repeat;
  background-size: 45px 35px;
}
.meat-empty {
  background: url("~@/assets/img/config/meat-empty.png") 30px no-repeat;
  background-size: 45px 35px;
}

.fish-full {
  background: url("~@/assets/img/config/fish-full.png") 5px no-repeat;
  background-size: 70px 35px;
}
.fish-empty {
  background: url("~@/assets/img/config/fish-empty.png") 5px no-repeat;
  background-size: 70px 35px;
}

span {
  display: inline-block;
  width: 90px;
  height: 40px;
  text-align: center;
  &:hover {
    cursor: pointer;
  }
}
</style>
