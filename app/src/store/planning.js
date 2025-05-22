import API from "@/api.js";

export default {
  namespaced: true,
  state: {
    planificationStatus: {},
  },
  getters: {
    getPlanificationStatus(state) {
      return state.planificationStatus;
    },
  },
  actions: {
    update({ dispatch, rootGetters }) {
      const userId = rootGetters["user/id"];
      dispatch(
        "system/updateAttr",
        {
          getAttribute: (rootState) => rootState.planning.planificationStatus,
          apiQuery: API.user.planificationStatus,
          queryArg: [userId],
        },
        { root: true }
      );
    },
  },
};
