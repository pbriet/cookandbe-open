import API from "@/api.js";
import { stringToDate } from "@/common/dates.js";
import { each } from "lodash";

export default {
  namespaced: true,
  state: {
    listHistory: {},
    availableDays: {},
  },
  mutations: {},
  getters: {
    getListHistory(state) {
      return state.listHistory;
    },
    getAvailableDays(state) {
      return state.availableDays;
    },
    // Returns the number of shopping lists with endDate >= date
    nbShoppingListsAfterDate: (state) => (date) => {
      let res = 0;
      each(state.listHistory.lists, (l) => {
        const listEndDate = new Date(l.endDate);
        if (listEndDate >= date) {
          res = res + 1;
        }
      });
      return res;
    },
  },
  actions: {
    update({ dispatch, rootGetters }) {
      const userId = rootGetters["user/id"];
      dispatch(
        "system/updateAttr",
        {
          getAttribute: (rootState) => rootState.shopping.listHistory,
          apiQuery: API.shoppingList.history,
          queryArg: [userId],
        },
        { root: true }
      );
      dispatch(
        "system/updateAttr",
        {
          getAttribute: (rootState) => rootState.shopping.availableDays,
          apiQuery: API.shoppingList.availableDays,
          queryArg: [userId],
          transformFcn(data) {
            if (data.startDate) {
              data.startDate = stringToDate(data.startDate);
            }
            if (data.endDate) {
              data.endDate = stringToDate(data.endDate);
            }
            return data;
          },
        },
        { root: true }
      );
    },
    async getFlyMenuItems({ rootGetters }, { shoppingListId }) {
      const userId = rootGetters["user/id"];
      const data = await API.shoppingList.flyMenuItems(userId, shoppingListId);
      return data;
    },
  },
};
