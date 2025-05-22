<template>
  <div
    ref="modal"
    :class="`modal ${noFade ? '' : 'fade'}`"
    :id="id"
    role="dialog"
    data-bs-keyboard="false"
    data-bs-backdrop="static"
    tabindex="-1"
  >
    <div class="modal-dialog" :style="maxWidth ? `max-width: ${maxWidth}; width: 100%; padding: 5px;` : ''">
      <div class="modal-content">
        <div class="btn btn-sm btn-danger op-btn-close" @click="onCloseBtn" v-if="closeBtn">
          <FontAwesomeIcon :icon="['fas', 'times']" />
        </div>
        <slot></slot>
        <span class="clearfix" />
      </div>
    </div>
    <span class="clearfix" />
  </div>
</template>

<script>
import $ from "jquery";
import { Modal } from "bootstrap";

/*
 * Dialog window with some content
 */
export default {
  name: "Dialog",
  props: [
    "id",
    "open",
    "closeBtn",
    "onClose",
    "onShow",
    "focusElt",
    "maxWidth",
    "noFade", // Fade animation can make content such as google charts behave strangely. It is sometimes better to disable it
  ],
  mounted() {
    this.$refs.modal.addEventListener("shown.bs.modal", () => {
      this.focusElt && $(this.$refs.modal).find(this.focusElt).focus();
      this.onShow && this.onShow();
    });
    this.modal = new Modal(this.$refs.modal);
  },
  computed: {},
  methods: {
    onCloseBtn() {
      this.onClose && this.onClose();
    },
  },
  watch: {
    open(newOpen, oldOpen) {
      if (!oldOpen && newOpen) {
        this.modal.show();
      } else if (oldOpen && !newOpen) {
        this.modal.hide();
      }
    },
  },
  beforeUnmount() {
    this.modal.hide();
  },
};
</script>

<style lang="scss">
.modal {
  $modal-corner-radius: 7px;

  overflow-y: auto;
  /* Fix bug: le backdrop de boost n'arrive pas à occuper tout l'écran en hauteur quand il y a un scroll */
  background-color: rgba(0, 0, 0, 0.5);

  .modal-backdrop {
    display: none;
  }

  .dialog-title {
    @extend .op-font-quicksand;

    font-size: 26px !important;
    padding: 15px 40px !important;
    margin: 0px !important;
    text-align: center;
    background-color: rgba($op-color-lime, 0.9);
    word-break: break-word;
    color: white;
    border-top-left-radius: $modal-corner-radius;
    border-top-right-radius: $modal-corner-radius;
  }

  .dialog-title-danger {
    @extend .dialog-title;

    background-color: rgba($op-color-red, 0.9) !important;
  }

  .dialog-title-warning {
    @extend .dialog-title;

    background-color: rgba($op-color-orange, 0.9) !important;
  }

  .dialog-body {
    background-color: white;
    padding: 15px;
    border-bottom-left-radius: $modal-corner-radius;
    border-bottom-right-radius: $modal-corner-radius;

    &:after {
      @extend .clearfix;
    }
  }

  .modal-footer {
    padding: 10px;

    .btn {
      float: right;
    }
  }

  .op-btn-close {
    position: absolute;
    right: 0px;
    border-radius: 0px;
    padding: 5px 12px !important;
    border-top-right-radius: $modal-corner-radius;
  }
}

.modal-open {
  overflow: auto;
}
</style>
