<template>
  <span class="op-tree-combo-page" ref="root">
    <!-- Select2 with bootstrap style -->
    <div class="input-group" :class="{ 'col-md-12': !eraseBtn }">
      <Select2
        :options="options"
        :placeholder="placeholder"
        :settings="{
          templateSelection,
          templateResult,
          multiple,
          minimumResultsForSearch: 0,
          minimumInputLength: 0,
          containerCssClass: 'op-tree-combo-select',
          matcher: treeMatcher,
        }"
        v-model="selection.current"
        theme="bootstrap-5"
      />
      <span class="input-group-btn" v-if="eraseBtn">
        <button @click="selection.current = undefined" class="btn btn-secondary h-100">
          <FontAwesomeIcon :icon="['fas', 'trash']" />
        </button>
      </span>
    </div>

    <table class="col-md-12 op-tree-combo-multiple" v-if="multiple">
      <tr
        v-for="(item, index) in selection.items"
        :key="item.id"
        :class="{ 'item-even': index % 2 == 0, 'item-odd': index % 2 == 1 }"
      >
        <td class="op-tree-combo-delete" @click="onDeleteItem(item)">
          <FontAwesomeIcon :icon="['fas', 'trash']" />
        </td>
        <td>{{ item.name }}</td>
      </tr>
    </table>
  </span>
</template>

<script>
import Select2 from "@/components/interface/Select2.vue";
import $ from "jquery";
import { some, includes, omit } from "lodash";

/*
 * This component adds a dynamic list of comboboxes,
 * to select one object in a tree-like hierarchy
 *
 * If multiple=1, handle multiple list of comboboxes, with some "+"/"-" buttons
 */
export default {
  name: "TreeCombo",
  props: [
    "tree", // List-like tree of serialized objects
    "modelValue", // Selection
    "multiple", // Is 'value' a list of values?
    "placeholder", // Text displayed when nothing is selected
    "onChangeValue", // Raised when one of the values changes
    "onAdd", // with multiple=1, called when one more value is added
    "onRemove", // with multiple=1, called when one more value is removed
    "eraseBtn", // if true, add an erase button to the right
  ],
  data: () => ({
    selection: { current: undefined, items: [] },
    choices: [],
  }),
  mounted() {
    this.resetList();
  },
  computed: {
    currentSelection() {
      return this.selection.current;
    },
    options() {
      return this.choices;
    },
  },
  watch: {
    modelValue: {
      handler() {
        this.resetList();
      },
      deep: true,
    },
    tree: {
      handler() {
        this.resetList();
      },
      deep: true,
    },
    currentSelection: {
      handler() {
        this.onSelect();
      },
      deep: true,
    },
  },
  methods: {
    templateResult(obj) {
      if (!obj.id) return obj.text;

      let classes = "";
      if (obj.level && obj.level >= 1 && obj.level <= 5) {
        classes = `level-${obj.level}`;
      }

      let name = obj.text;
      const currentInput = $(this.$refs.root).find(".select2-search__field").first().val();
      if (currentInput) {
        name = name.replaceAll(new RegExp(currentInput, "ig"), `<span class="fw-bold">$&</span>`);
      }

      return $(`<span class="ms-3 ${classes}">${name}</span>`);
    },
    templateSelection(obj) {
      return obj.text;
    },
    resetList() {
      this.choices = [];
      this.selection.items = [];
      if (!this.tree) {
        return;
      }
      this.initList(this.tree, 1);
    },
    initList(forest, level) {
      for (const tree of forest) {
        // Adding element in select
        tree.level = level;

        // select2 can support tree options using "children", but only with one
        // level of nesting. So we rename "children" and reimplement our own
        // system using treeMatcher
        this.choices.push(omit({ ...tree, subitems: tree.children }, ["children"]));
        // Updating selection
        if (this.multiple) {
          if (includes(this.modelValue, tree.id)) {
            this.selection.items.push(tree);
          }
        } else if (this.modelValue === tree.id && this.selection.current != tree) {
          this.selection.current = tree.id;
        }
        // Recursing in children
        if (tree.children.length) {
          this.initList(tree.children, level + 1);
        }
      }
    },
    itemMatcher(query, item) {
      return (
        item.text.toUpperCase().indexOf(query) != -1 ||
        some(item.subitems || [], (subitem) => this.itemMatcher(query, subitem))
      );
    },
    // See https://select2.org/searching
    treeMatcher(params, data) {
      const query = $.trim(params.term).toUpperCase();
      if (query === "") {
        return data;
      }

      if (this.itemMatcher(query, data)) {
        return data;
      }

      return null;
    },
    onDeleteItem(item) {
      const itemPos = this.selection.items.indexOf(item);
      const modelPos = this.modelValue.indexOf(item.id);

      if (modelPos !== -1) {
        this.selection.items.splice(itemPos, 1);
        this.$emit(
          "update:modelValue",
          this.modelValue.filter((id) => id != item.id)
        );
        this.onRemove && this.onRemove(item);
      }
    },
    onSelect() {
      if (!this.modelValue) {
        return;
      }
      if (this.multiple) {
        const currentSelection =
          this.selection.current && this.choices.filter((c) => c.id == this.selection.current[0])[0];
        if (currentSelection && !includes(this.selection.items, currentSelection)) {
          this.selection.items.push(currentSelection);
          this.$emit("update:modelValue", [...this.modelValue, currentSelection.id]);
          this.onAdd && this.onAdd(this.selection.current[0]);
        }
        this.selection.current = undefined;
      } else {
        if (this.selection.current) {
          this.$emit("update:modelValue", this.selection.current);
        } else {
          this.$emit("update:modelValue", undefined);
        }
        this.onChangeValue && this.onChangeValue(this.selection.current);
      }
    },
  },
  components: { Select2 },
};
</script>

<style lang="scss">
.select2-container {
  /* Override select2 bootstrap-5 theme */
  &.select2-container--bootstrap-5
    .select2-dropdown
    .select2-results__options
    .select2-results__option.select2-results__option--selected,
  &.select2-container--bootstrap-5
    .select2-dropdown
    .select2-results__options
    .select2-results__option[aria-selected="true"] {
    background-color: #428bca !important;
  }

  &.select2-container--bootstrap-5 .select2-dropdown .select2-results__options .select2-results__option {
    padding: 2px 0 !important;
  }

  .level-1 {
    font-size: $op-font-lg;
    color: $op-color-red;
    padding-left: 0px;
  }

  .level-2 {
    font-size: $op-font-md;
    color: $op-color-lime;
    padding-left: 5px;
  }

  .level-3 {
    font-size: $op-font-sm;
    color: $op-color-orange;
    padding-left: 10px;
  }

  .level-4 {
    font-size: $op-font-xs;
    color: $op-color-green;
    padding-left: 15px;
  }

  .level-5 {
    font-size: $op-font-xxs;
    padding-left: 20px;
  }
}

.op-tree-combo-page {
  .input-group {
    margin-top: 0px;
    margin-bottom: 0px;
  }

  .op-tree-combo-multiple {
    padding: 10px;
    text-align: left;
    margin-bottom: 20px;
    width: 100%;

    .op-tree-combo-delete {
      color: $op-color-red;
      padding: 10px;
      width: 30px;
      &:hover {
        cursor: pointer;
      }
    }
    .item-even {
      background-color: #f5f5f5;
    }
    .item-odd {
      background-color: #fff;
    }
  }
}
</style>
