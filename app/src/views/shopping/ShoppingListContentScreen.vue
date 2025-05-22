<template>
  <Dialog :open="itemEditorDialog">
    <ItemEditor :shoppingItem="current.editedItem" :focus="current.focus" :onClose="hideItemEditorDialog" />
  </Dialog>

  <Dialog :open="frozenInfosDialog" :closeBtn="true">
    <div class="dialog-title">
      <img src="@/assets/img/shopping/snowflake.png" class="op-icon-dlg" /> Conservation des aliments
    </div>
    <div class="dialog-body">
      <p>Achetés frais, certains aliments se gardent peu de temps au réfrigérateur.</p>
      <p>
        Nous vous conseillons de mettre les aliments marqués d'un flocon au congélateur afin de les préserver plus
        longtemps.
      </p>
      <div class="">
        <div class="fright btn btn-success" @click="hideFrozenInfosDialog">Compris</div>
      </div>
    </div>
  </Dialog>

  <Dialog :open="storageInfosDialog" :closeBtn="true" :onClose="hideStorageInfosDialog">
    <div class="dialog-title">Des articles dans mes placards ?</div>
    <div class="dialog-body">
      <p>
        Certains ingrédients sont des aliments généralement présents dans les placards : huile, farine, sucre, sel, ...
      </p>
      <p>
        Vérifiez qu'il vous en reste, ou cliquez sur
        <b><FontAwesomeIcon :icon="['fas', 'plus']" /> Ajouter à la liste</b> pour penser à les acheter !
      </p>
      <div class="">
        <div class="fright btn btn-success" @click="hideStorageInfosDialog">Compris</div>
      </div>
    </div>
  </Dialog>

  <Dialog :open="emailShoppingListDialog">
    <div class="dialog-title"><FontAwesomeIcon :icon="['fas', 'times']" /> Echec de l'envoi de la liste</div>
    <div class="dialog-body">
      <PleaseWait :until="email.status !== 'sending'" caption="Envoi du mail en cours">
        <p>{{ email.error }}</p>
        <p>Si le problème persiste, contactez-notre équipe.</p>
        <div class="">
          <button
            class="fright btn btn-success"
            @click="hideEmailShoppingListDialog"
            :disabled="email.status === 'sending'"
          >
            Fermer
          </button>
        </div>
      </PleaseWait>
    </div>
  </Dialog>

  <Dialog :open="itemRecipeDialog" :closeBtn="true" :onClose="hideItemRecipeDialog" v-if="current.editedItem">
    <div class="dialog-title">
      <span v-if="!current.editedItem.forcedName">{{ current.editedItem?.food?.name }}</span>
      <span v-if="current.editedItem.forcedName">{{ current.editedItem.forcedName }}</span>
    </div>
    <div class="dialog-body">
      <div class="op-vs">
        <div class="op-table-auto">
          <div class="op-header d-none">
            <div style="width: 110px">&nbsp;</div>
            <div style="width: 150px">Repas</div>
            <div>Recette</div>
            <div style="width: 70px">Quantité</div>
          </div>
          <div class="d-none d-sm-table-row" v-for="dishRecipe in current.editedItem.recipes" :key="dishRecipe.id">
            <div style="width: 110px"><RecipeImg :url="dishRecipe.photo" :disc="true" :hideIcons="true" /></div>
            <div>
              {{ upperFirst(DateTime.fromISO(dishRecipe.date).setLocale("fr").toFormat("EEEE dd MMMM")) }}<br />{{
                dishRecipe.meal
              }}
            </div>
            <div>{{ dishRecipe.name }}</div>
            <div class="text-center"><span v-html="dishRecipe.quantity" /> g</div>
          </div>
          <div class="d-table-row d-sm-none" v-for="dishRecipe in current.editedItem.recipes" :key="dishRecipe.id">
            <div>
              <div class="op-vs-5 op-hs-10">
                <span class="op-font-green-dark"
                  >{{ upperFirst(DateTime.fromISO(dishRecipe.date).setLocale("fr").toFormat("EEEE dd MMMM")) }} -
                  {{ dishRecipe.meal }}</span
                >
                <span class="op-font-grey-dark"> (<span v-html="dishRecipe.quantity" /> g)</span>
              </div>
              <div class="op-vs-5 op-hs-10">{{ dishRecipe.name }}</div>
            </div>
          </div>
        </div>
      </div>
      <div class="">
        <div class="fright btn btn-success" @click="hideItemRecipeDialog">Fermer</div>
      </div>
    </div>
  </Dialog>

  <div class="op-page">
    <div class="op-page-title">
      <h1>
        Ma liste de courses
        <br />
        <small v-if="shoppingList">
          {{ upperFirst(DateTime.fromISO(shoppingList.startDate).setLocale("fr").toFormat("EEEE dd MMMM")) }}
          <span v-show="shoppingList.startDate !== shoppingList.endDate">
            à {{ DateTime.fromISO(shoppingList.endDate).setLocale("fr").toFormat("EEEE dd MMMM") }}
          </span>
        </small>
      </h1>
    </div>

    <span class="clearfix" />

    <div class="op-page-content container-fluid">
      <div class="text-center" v-if="enableFlyMenu" id="shop-btn">
        <a class="btn btn-success op-large" @click="startPurchase">
          <FontAwesomeIcon :icon="['fas', 'shopping-cart']" />
          <span class="btn-text">Commander en ligne</span>
        </a>
      </div>

      <div class="row d-none d-sm-flex" id="gluten-links" v-if="withGluten && ENABLE_SPONSORS">
        <div class="col-12 col-sm-6">
          <div class="info-block" id="afdiag-shopping-list">
            <div class="ext-link-img">
              <a href="http://www.afdiag.fr/dietetique/produits-sans-gluten/" target="_blank">
                <img src="@/assets/img/corp/afdiag-transparent.png" />
              </a>
            </div>
            <span class="clearfix d-lg-none" />
            <div>
              <div class="ext-link-text">
                Quelles marques choisir pour votre alimentation sans gluten ?<br />
                Consultez
                <a href="http://www.afdiag.fr/dietetique/produits-sans-gluten/" target="_blank"> l'AFDIAG </a>
              </div>
            </div>
          </div>
        </div>
        <div class="col-12 col-sm-6">
          <div class="info-block" id="glut-corner-shopping-list">
            <div class="ext-link-img">
              <a href="http://www.glutencorner.com/eshop/" target="_blank">
                <img src="@/assets/img/corp/gluten-corner-transparent.png" />
              </a>
            </div>
            <span class="clearfix d-lg-none" />
            <div>
              <div class="ext-link-text">
                Faites vos courses en ligne sur
                <a href="http://www.glutencorner.com/eshop/" target="_blank"> Gluten Corner </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="text-center">
        <div class="op-link-toolbar">
          <a
            class="op-vs-5"
            @click="sendListByEmail"
            :class="{ 'mail-sending': email.status === 'sending', 'mail-sent': email.status === 'sent' }"
          >
            <div class="op-big-btn">
              <div class="op-row">
                <div class="op-cell">
                  <FontAwesomeIcon :icon="['fas', 'envelope']" />
                </div>
              </div>
              <div class="op-row">
                <div class="op-cell" v-show="email.status !== 'sent' && email.status !== 'sending'">
                  Recevoir par email
                </div>
                <div class="op-cell" v-show="email.status === 'sending'">Envoi en cours...</div>
                <div class="op-cell" v-show="email.status === 'sent'">Envoyé !</div>
              </div>
            </div>
          </a>
          <a class="op-vs-5 d-none d-sm-inline-block" @click="printList">
            <div class="op-big-btn">
              <div class="op-row">
                <div class="op-cell">
                  <FontAwesomeIcon :icon="['fas', 'print']" />
                </div>
              </div>
              <div class="op-row">
                <div class="op-cell">Imprimer</div>
              </div>
            </div>
          </a>
          <a class="op-vs-5" @click="onEditItem(null)">
            <div class="op-big-btn">
              <div class="op-row">
                <div class="op-cell">
                  <FontAwesomeIcon :icon="['fas', 'plus']" />
                </div>
              </div>
              <div class="op-row">
                <div class="op-cell">Ajouter un article</div>
              </div>
            </div>
          </a>
          <a class="op-vs-5 op-font-red" @click="deleteList" :class="{ 'delete-in-progress': deleteInProgress }">
            <div class="op-big-btn">
              <div class="op-row">
                <div class="op-cell">
                  <FontAwesomeIcon :icon="['fas', 'times']" />
                </div>
              </div>
              <div class="op-row">
                <div class="op-cell" v-if="!deleteInProgress">Supprimer</div>
                <div class="op-cell" v-if="deleteInProgress">Suppression...</div>
              </div>
            </div>
          </a>
        </div>
      </div>

      <!-- Infos -->
      <div class="row op-vs d-none d-sm-flex">
        <div class="col-12 col-sm-3 op-vs-5">
          <div class="info-block">
            <div class="info-icon">
              <FontAwesomeIcon :icon="['fas', 'shopping-cart']" />
              {{ nbMissingItems }}
            </div>
            <div>Articles à acheter</div>
          </div>
        </div>
        <div class="col-12 col-sm-3 op-vs-5">
          <div class="info-block">
            <div class="info-icon">
              <FontAwesomeIcon :icon="['fas', 'check']" />
              {{ nbStoredItems }}
            </div>
            <div>
              Dans vos placards
              <a href="" @click.prevent="showStorageInfosDialog">
                <span class="op-font-lg">
                  <FontAwesomeIcon :icon="['fas', 'question-circle']" />
                </span>
              </a>
            </div>
          </div>
        </div>
        <span class="clearfix" />
      </div>

      <PleaseWait :until="shoppingList" caption="Récupération des ingrédients">
        <div class="row">
          <ShoppingItemsList
            :shoppingList="shoppingList"
            filter="list"
            :onEditQuantity="onEditItem"
            :onSelectItem="onSelectItem"
            :onToggleItem="onToggleItem"
            :onDeleteCustomItem="onDeleteCustomItem"
            :onShowFrozenInfos="showFrozenInfosDialog"
            :iterItemDays="iterItemDays"
          />
        </div>
      </PleaseWait>
    </div>
  </div>
</template>

<script>
import API from "@/api.js";
import { ENABLE_FLYMENU, ENABLE_SPONSORS } from "@/config.js";
import { FLY_MENU_URL, FLY_MENU_KEY } from "@/config.js";
import { mapGetters } from "vuex";
import { upperFirst, find } from "lodash";
import { DateTime } from "luxon";
import Dialog from "@/components/interface/Dialog.vue";
import PleaseWait from "@/components/interface/PleaseWait.vue";
import RecipeImg from "@/components/recipe/RecipeImg.vue";
import ItemEditor from "@/components/shopping/ItemEditor.vue";
import ShoppingItemsList from "@/components/shopping/ShoppingItemsList.vue";
import $ from "jquery";

const CATEGORY_OTHER_LABEL = "Autre";

export default {
  name: "ShoppingListContentScreen",
  props: ["shoppingList", "nbMissingItems", "nbStoredItems", "onToggleItem", "onDeleteCustomItem", "iterItemDays"],
  data: () => ({
    ENABLE_SPONSORS,
    enableFlyMenu: ENABLE_FLYMENU,
    emailShoppingListDialog: false,
    itemEditorDialog: false,
    frozenInfosDialog: false,
    storageInfosDialog: false,
    itemRecipeDialog: false,
    deleteInProgress: false,
    current: {},
    email: { status: "not_sent", error: null },
    purchase: { postalCode: "" },
    DateTime,
  }),
  mounted() {
    if (this.enableFlyMenu) {
      this.initFlymenu();
    }
  },
  computed: {
    ...mapGetters({
      user: "user/get",
      userId: "user/id",
    }),
    withGluten() {
      return this.user.objective.key === "gluten_free";
    },
  },
  methods: {
    upperFirst,
    showEmailShoppingListDialog() {
      this.emailShoppingListDialog = true;
    },
    hideEmailShoppingListDialog() {
      this.emailShoppingListDialog = false;
    },
    showFrozenInfosDialog() {
      this.frozenInfosDialog = true;
    },
    hideFrozenInfosDialog() {
      this.frozenInfosDialog = false;
    },
    showStorageInfosDialog() {
      this.storageInfosDialog = true;
    },
    hideStorageInfosDialog() {
      this.storageInfosDialog = false;
    },
    showItemEditorDialog() {
      this.itemEditorDialog = true;
    },
    onSelectItem(item) {
      this.current.editedItem = item;
      this.$nextTick(() => {
        this.itemRecipeDialog = true;
      });
    },
    hideItemRecipeDialog() {
      this.itemRecipeDialog = false;
    },
    createCategoryOther() {
      const categoryOther = {
        foodType: CATEGORY_OTHER_LABEL,
        missingItems: 0,
        items: [],
      };
      this.$emit("update:shoppingList", {
        ...this.shoppingList,
        content: [categoryOther, ...this.shoppingList.content],
      });
      return categoryOther;
    },
    hideItemEditorDialog(success, item, created) {
      this.itemEditorDialog = false;
      // Current item management
      const currentItem = this.current.editedItem;
      this.current.editedItem = null;
      if (!success) {
        // Cancel: no change
        return;
      }
      if (created) {
        // New custom item
        let otherCategory = find(this.shoppingList.content, ["foodType", CATEGORY_OTHER_LABEL]);
        if (!otherCategory) {
          // Creating "Autre" category
          otherCategory = this.createCategoryOther();
        }
        // Adding it manually to the "Autre" category to prevent a full refresh
        otherCategory.items.push(item);
        otherCategory.missingItems += 1;
        return;
      }
      // Modified item
      currentItem.forcedName = item.forcedName;
      currentItem.forcedQuantity = item.forcedQuantity;
    },
    initFlymenu() {
      if ($("#fly-menu-script").length === 0) {
        // Include fly menu js
        const flyMenu = document.createElement("script");
        flyMenu.type = "text/javascript";
        flyMenu.src = FLY_MENU_URL;
        flyMenu.id = "fly-menu-script";
        $("body").append(flyMenu);
      }
    },
    async startPurchase() {
      // Purchase !
      const data = await this.$store.dispatch("shopping/getFlyMenuItems", {
        shoppingListId: this.$route.params.shoppingListId,
      });
      // Calling fly menu
      window.flymenuClearSession();
      window.flyMenuInit({ site_token: FLY_MENU_KEY });
      window.addRecipes({ ingredients: data.ingredients }).then(() => {
        //Affichage du popup FlyMenu
        window.showFlyMenu();
      });
    },
    async sendListByEmail() {
      if (this.email.status === "sent" || this.email.status === "sending") {
        return;
      }
      this.email = { status: "sending", error: null };

      const data = await API.shoppingList.sendByMail(this.userId, this.$route.params.shoppingListId);
      if (data.status === "ok") {
        this.email.status = "sent";
      } else {
        this.email.status = "error";
        this.email.error = data.title;
        this.showEmailShoppingListDialog();
      }
    },
    printList() {
      window.print();
    },
    onEditItem(item, focus) {
      if (!item) {
        item = {
          gotIt: false,
          shoppingList: this.$route.params.shoppingListId,
          forcedName: "",
          forcedQuantity: "",
          id: null,
        };
      }
      if (focus) {
        this.current.focus = focus;
      }
      this.current.editedItem = item;
      this.showItemEditorDialog();
    },
    async deleteList() {
      if (this.deleteInProgress) {
        return;
      }
      this.deleteInProgress = true;
      await API.shoppingList.remove(this.userId, this.$route.params.shoppingListId);
      this.$store.dispatch("shopping/update");
      this.$router.go(-1);
    },
  },
  components: { RecipeImg, Dialog, PleaseWait, ItemEditor, ShoppingItemsList },
};
</script>

<style scoped lang="scss">
@media (min-width: $bootstrap-sm-min) {
  .op-header {
    display: table-header-group !important;
  }
}

.op-link-toolbar {
  @media (min-width: $bootstrap-sm-min) {
    padding-top: 30px;
  }
  a {
    color: $op-color-menu-btn;

    &:hover {
      color: $op-color-menu-btn-hover !important;
      text-decoration: none;
    }
  }

  .mail-sending {
    background-color: rgba($op-color-yellow, 0.2);
    min-width: 117px;
    color: black !important;

    & > div {
      margin: auto;
    }

    &:hover {
      cursor: default !important;
    }
  }

  .mail-sent {
    background-color: rgba($op-color-lime, 0.2);
    min-width: 117px;
    color: black !important;

    & > div {
      margin: auto;
    }

    &:hover {
      cursor: default !important;
    }
  }

  .delete-in-progress {
    background-color: rgba($op-color-red, 0.2);
    min-width: 117px;
    color: black !important;

    & > div {
      margin: auto;
    }

    &:hover {
      cursor: default !important;
    }
  }
}

.info-block {
  padding: 15px;
  width: 100%;
  background-color: $op-color-grey-light;

  .info-icon {
    padding-left: 10px;
    padding-right: 10px;
    font-size: 24px;

    @media (max-width: $bootstrap-xxs-max) {
      display: block;
      width: 100%;
      text-align: center;
      margin-top: 5px;
      margin-bottom: 5px;
    }
    @media (min-width: $bootstrap-xs-min) {
      display: inline;
    }
  }
  & > div {
    display: inline-block;
    vertical-align: middle;
  }
}
.op-page-content {
  padding-top: 0px;
}
#gluten-links {
  background-color: $op-color-grey-light;
  .info-block {
    background-color: $op-color-grey-light;
    text-align: center;
    font-size: 14px;
  }
  img {
    max-height: 80px;
    display: block;
  }
  .ext-link-text {
    margin: auto;
  }
  #afdiag-shopping-list {
    .ext-link-img {
      width: 20%;
    }
    img {
      margin: auto;
    }
    .ext-link-text {
      max-width: 400px;
    }
  }
  #glut-corner-shopping-list {
    .ext-link-img {
      width: 30%;
      min-width: 170px;
    }
    .ext-link-text {
      max-width: 200px;
    }
  }
}

#shop-btn {
  padding-top: 40px;

  @media (min-width: $bootstrap-md-min) {
    float: right;
    padding-right: 30px;
    padding-left: 15px;

    svg {
      font-size: 30px;
    }
    .btn {
      padding: 10px 16px;
    }
    .btn-text {
      font-size: 16px;
      padding-top: 4px;
    }
  }
  span {
    display: inline-block;
    vertical-align: top;
  }
  @media (max-width: $bootstrap-sm-max) {
    svg {
      font-size: 24px;
    }
    .btn-text {
      font-size: 14px;
      padding-top: 2px;
    }
  }
  .btn-text {
    padding-left: 10px;
  }
}
</style>
