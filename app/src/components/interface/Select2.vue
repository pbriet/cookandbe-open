<template>
  <select ref="select"></select>
</template>

<script>
import $ from "jquery";
import axios from "axios";
import { generateCancelToken } from "@/api.js";
import { isUndefined } from "lodash";
import "select2/dist/js/select2.full";
import "select2/dist/css/select2.min.css";

// Load language file
// There is probably a better way, but standart import does not work at the moment
$.fn.select2.amd.define("select2/i18n/fr", [], require("select2/src/js/select2/i18n/fr"));

export default {
  name: "Select2",
  props: {
    modelValue: {},
    options: {},
    placeholder: {},
    settings: {},
    query: {},
    onSelecting: {},
    preventSelect: {},
    theme: {
      default: "classic",
    },
  },
  data: () => ({}),
  mounted() {
    this.initOptions(this.options);

    const select = $(this.$refs.select);
    select
      .on("select2:unselect", () => {
        this.$emit("update:modelValue", select.val());
      })
      .on("select2:selecting", async (e) => {
        const choice = e.params.args.data;
        if (this.preventSelect && this.preventSelect(choice)) {
          e.preventDefault();
        }
        this.onSelecting && this.onSelecting(choice, $(this.$refs.select));
      })
      .on("select2:select", (e) => {
        this.$emit("update:modelValue", select.val());
        this.$emit("select", e.params.data);
      })
      .on("select2:open", () => {
        this.$emit("select2:open");
      });
  },
  beforeUnmount() {
    $(this.$refs.select).select2("destroy");
  },
  computed: {},
  watch: {
    options: {
      handler(newOptions) {
        this.initOptions(newOptions);
      },
      deep: true,
    },
    modelValue: {
      handler(newModelValue) {
        this.setValue(newModelValue);
      },
      deep: true,
    },
    disabled(newValue) {
      const select = $(this.$refs.select);
      select.prop("disabled", !newValue);
    },
  },
  methods: {
    setValue(value) {
      const select = $(this.$refs.select);
      if (value instanceof Array) {
        select.val([...value]);
      } else {
        select.val([value]);
      }
      select.trigger("change");
    },
    initOptions(data) {
      const select = $(this.$refs.select);
      select.empty();

      let ajax;
      if (this.query)
        ajax = {
          transport: (params, success, failure) => {
            const [cancelToken, abort] = generateCancelToken();
            this.query(params.data, cancelToken)
              .then(success)
              .catch((err) => {
                if (!axios.isCancel(err)) {
                  failure(err);
                }
              });
            return { abort };
          },
        };

      select.select2({
        data,
        placeholder: this.placeholder,
        theme: this.theme,
        ajax,
        language: "fr",
        ...this.settings,
      });
      if (!isUndefined(this.modelValue)) {
        this.setValue(this.modelValue);
      }
    },
  },
  components: {},
};
</script>

<style lang="scss"></style>
