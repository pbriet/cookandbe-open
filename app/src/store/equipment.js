import API from "@/api.js";

export default {
  namespaced: true,
  state: {
    ustensils: [],
    categories: [],
    userUstensils: [],
  },
  getters: {
    getCategories(state) {
      return state.categories;
    },
    getUstensils(state) {
      return state.ustensils;
    },
  },
  mutations: {},
  actions: {
    update({ state, dispatch, rootGetters }) {
      state.userUstensils = rootGetters["user/get"].ustensils;
      dispatch(
        "system/updateAttr",
        {
          getAttribute: (rootState) => rootState.equipment.ustensils,
          apiQuery: API.ustensils,
        },
        { root: true }
      );
      dispatch(
        "system/updateAttr",
        {
          getAttribute: (rootState) => rootState.equipment.categories,
          apiQuery: API.ustensilCategories,
        },
        { root: true }
      );
    },
  },
};
