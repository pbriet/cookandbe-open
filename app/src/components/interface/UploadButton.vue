<template>
  <div class="op-upload-img">
    <input ref="uploadInput" type="file" @change="onImageSelected" class="d-none" />
    <button @click="uploadImage" v-show="!showPleaseWait" class="btn btn-secondary">
      <span class="op-icon-xl">
        <FontAwesomeIcon :icon="getIcon" />
      </span>
      {{ text }}
    </button>
    <img src="~@/assets/img/please-wait.gif" v-show="showPleaseWait" />
  </div>
</template>

<script>
/*
 * This component adds a button to upload an image, and calls
 * an API function given in argument
 */
export default {
  name: "UploadButton",
  props: ["onUpload", "text", "showPleaseWait", "icon"],
  data: () => ({}),
  computed: {
    getIcon() {
      return this.icon || ["fas", "upload"];
    },
  },
  methods: {
    uploadImage() {
      this.$refs.uploadInput.click();
    },
    onImageSelected(e) {
      const reader = new FileReader();
      reader.readAsDataURL(e.target.files[0]);
      reader.onload = (imgData) => {
        this.onUpload(imgData.target.result);
      };
    },
  },
  components: {},
};
</script>

<style scoped lang="scss"></style>
