<template>
  <div class="op-item-editor">
    <div class="dialog-title">{{ title }}</div>
    <div class="dialog-body">
      <div v-if="!isCustom && shoppingItem">
        <p>
          Quantité nécessaire pour préparer vos recettes:
          <b><span v-html="shoppingItem.conversion.htmlValue" /> {{ shoppingItem.conversion.unit }}</b>
          <span v-if="shoppingItem.basicConversion">
            (<span v-html="shoppingItem.basicConversion.htmlValue" /> {{ shoppingItem.basicConversion.unit }})
          </span>
        </p>
      </div>

      <!-- Editor -->
      <div class="row">
        <div class="col-12 col-sm-7 op-vs-5">
          <div class="btn-block input-group">
            <span v-show="!isCustom"
              >Entrez la nouvelle quantité pour: <b>{{ title }}</b></span
            >
            <input
              v-show="isCustom"
              ref="itemNameInput"
              id="item-name-input"
              class="form-control w-100"
              placeholder="Nom"
              v-model="item.forcedName"
            />
          </div>
        </div>
        <div class="col-12 col-sm-5 op-vs-5">
          <div class="input-group">
            <input
              class="form-control"
              ref="itemQuantityInput"
              id="item-quantity-input"
              placeholder="Quantité"
              v-model="item.forcedQuantity"
            />
            <span class="input-group-btn" v-if="!isNew">
              <button class="btn btn-secondary" @click="onResetQuantity">
                <FontAwesomeIcon :icon="['fas', 'sync']" />
              </button>
            </span>
          </div>
        </div>
      </div>

      <!-- Toolbar -->
      <div class="row justify-content-end">
        <div class="col-12 col-sm-4 fright op-vs">
          <button type="button" class="btn btn-success btn-block" @click="onSave" :disabled="isDisabled">Ok</button>
        </div>
        <div class="col-12 col-sm-4 fright op-vs">
          <button type="button" class="btn btn-secondary btn-block" @click="onCancel">Annuler</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { isEmpty } from "lodash";
import API from "@/api.js";

export default {
  name: "ItemEditor",
  props: ["focus", "shoppingItem", "onClose"],
  data: () => ({
    item: {},
  }),
  mounted() {
    this.reset();
  },
  watch: {
    shoppingItem(newValue) {
      if (newValue) {
        this.reset();
      }
    },
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
    }),
    isNew() {
      if (!this.shoppingItem) return false;
      return this.shoppingItem.id === null;
    },
    isCustom() {
      if (!this.shoppingItem) return false;
      return this.isNew || this.shoppingItem.forcedName;
    },
    title() {
      if (!this.shoppingItem) return "";
      if (this.isNew) {
        return "Ajouter un article";
      } else {
        return this.shoppingItem.forcedName || this.shoppingItem.food.name;
      }
    },
    isDisabled() {
      if (!this.item || isEmpty(this.item)) {
        return true;
      }
      if (this.isCustom && !this.item.forcedName) {
        return true;
      }
      return !this.item.forcedQuantity;
    },
  },
  methods: {
    reset() {
      if (!this.shoppingItem) {
        return;
      }
      this.item = { ...this.shoppingItem };
      // Forced quantity
      let forcedQuantity = this.shoppingItem.forcedQuantity;
      if (!this.isNew && !forcedQuantity) {
        forcedQuantity = this.computeDefaultQuantity(this.shoppingItem);
      }
      this.item.forcedQuantity = forcedQuantity;
      this.resetFocus();
    },
    resetFocus() {
      if (this.isNew || this.focus === "name") {
        setTimeout(() => {
          this.$refs.itemNameInput.focus();
        }, 500);
      } else {
        setTimeout(() => {
          this.$refs.itemQuantityInput.focus();
        }, 500);
      }
    },
    onResetQuantity() {
      if (this.isCustom) {
        this.item.forcedQuantity = this.shoppingItem.forcedQuantity;
      } else {
        this.item.forcedQuantity = this.computeDefaultQuantity(this.shoppingItem);
      }
    },
    computeDefaultQuantity(item) {
      if (this.isCustom) {
        return item.forcedQuantity;
      }
      let defaultQuantity = item.conversion.value + " " + item.conversion.unit;
      if (item.basicConversion && item.basicConversion.value) {
        defaultQuantity += " (" + item.basicConversion.value + " " + item.basicConversion.unit + ")";
      }
      return defaultQuantity;
    },
    async onSave() {
      if (!this.isCustom && this.item.forcedQuantity === this.computeDefaultQuantity(this.shoppingItem)) {
        this.item.forcedQuantity = null;
      }
      if (
        this.isNew ||
        this.item.forcedQuantity != this.shoppingItem.forcedQuantity ||
        this.item.forcedName != this.shoppingItem.forcedName
      ) {
        // Some changes -> update or create
        if (this.item.id) {
          API.shoppingItem.force(this.item.id, {
            userId: this.userId,
            quantity: this.item.forcedQuantity,
            name: this.item.forcedName,
          });
        } else {
          this.item = await API.shoppingItem.save({ ...this.item, userId: this.userId });
        }
      }
      this.onClose(true, this.item, this.isNew);
    },
    onCancel() {
      this.reset();
      this.onClose(false, null, false);
    },
  },
  components: {},
};
</script>

<style scoped lang="scss"></style>
