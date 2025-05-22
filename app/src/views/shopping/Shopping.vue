<template>
  <div id="op-shopping-list-main" class="op-page">
    <div class="op-page-title">
      <h1>Mes listes de courses</h1>
    </div>

    <div class="op-page-content">
      <div class="new-shopping-list op-vs">
        <ShoppingListCreator />
        <span class="clearfix" />
      </div>

      <div v-if="history.lists.length">
        <h3>Ma dernière liste</h3>

        <table class="op-table shopping-lists-history">
          <tr @click="onSelectShoppingList(history.lists[0])">
            <td class="d-none d-sm-table-cell">
              Créée le {{ DateTime.fromISO(history.lists[0].creationDate).toFormat("dd/MM/yyyy") }}
            </td>
            <td>
              <p v-if="history.lists[0].startDate == history.lists[0].endDate">
                Le
                {{ DateTime.fromISO(history.lists[0].startDate).setLocale("fr").toFormat("EEEE d MMMM") }}
              </p>
              <p v-if="history.lists[0].startDate != history.lists[0].endDate">
                Du
                {{ DateTime.fromISO(history.lists[0].startDate).setLocale("fr").toFormat("EEEE d MMMM") }}
                au
                {{ DateTime.fromISO(history.lists[0].endDate).setLocale("fr").toFormat("EEEE d MMMM") }}
              </p>
            </td>
            <td>
              {{ getNbListDays(history.lists[0]) }}
              jour<span v-if="getNbListDays(history.lists[0]) > 1">s</span>
            </td>
            <td>
              {{ history.lists[0].nbItems }}
              article<span v-if="history.lists[0].nbItems > 1">s</span>
            </td>
          </tr>
        </table>
      </div>

      <div v-if="history.lists.length > 1">
        <h3>Listes précédentes</h3>

        <table class="op-table shopping-lists-history">
          <tr
            v-for="shoppingList in tail(history.lists)"
            :key="shoppingList.id"
            @click="onSelectShoppingList(shoppingList)"
          >
            <td class="d-none d-sm-table-cell">
              Créée le {{ DateTime.fromISO(shoppingList.creationDate).toFormat("dd/MM/yyyy") }}
            </td>
            <td>
              <p v-if="shoppingList.startDate == shoppingList.endDate">
                Le {{ DateTime.fromISO(shoppingList.startDate).setLocale("fr").toFormat("EEEE d MMMM") }}
              </p>
              <p v-if="shoppingList.startDate != shoppingList.endDate">
                Du {{ DateTime.fromISO(shoppingList.startDate).setLocale("fr").toFormat("EEEE d MMMM") }} au
                {{ DateTime.fromISO(shoppingList.endDate).setLocale("fr").toFormat("EEEE d MMMM") }}
              </p>
            </td>
            <td>
              {{ getNbListDays(shoppingList) }}
              jour<span v-if="getNbListDays(shoppingList) > 1">s</span>
            </td>
            <td>
              {{ shoppingList.nbItems }}
              article<span v-if="shoppingList.nbItems > 1">s</span>
            </td>
          </tr>
        </table>
      </div>
      <!-- v-if lists.length -->
    </div>
    <!-- op-page-content -->
  </div>
  <!-- op-shopping-list-main -->
</template>

<script>
import { DateTime } from "luxon";
import { dateDaysDifference } from "@/common/dates.js";
import ShoppingListCreator from "@/components/shopping/ShoppingListCreator.vue";
import { mapGetters } from "vuex";
import { tail } from "lodash";

export default {
  name: "Shopping",
  props: [],
  data: () => ({
    DateTime,
  }),
  computed: {
    ...mapGetters({
      history: "shopping/getListHistory",
    }),
  },
  methods: {
    tail,
    onSelectShoppingList(shoppingList) {
      this.$router.push({ name: "ShoppingListContent", params: { shoppingListId: shoppingList.id } });
    },
    getNbListDays(shoppingList) {
      return dateDaysDifference(shoppingList.startDate, shoppingList.endDate) + 1;
    },
  },
  components: { ShoppingListCreator },
};
</script>

<style lang="scss">
#op-shopping-list-main {
  .shopping-lists-history {
    @include op-table-focus(white, $op-color-grey-dark);
    td {
      padding: 15px;
    }
    p {
      margin: 0px;
    }
  }

  .new-shopping-list {
    width: 100%;
    background-color: $op-color-grey-light;

    .op-shopping-list-creator {
      max-width: 450px;
      margin: auto;
      display: block;
    }
  }
}
</style>
