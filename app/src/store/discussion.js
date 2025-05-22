import API from "@/api.js";

export default {
  namespaced: true,
  state: {
    discussions: [],
    quota: {},
  },
  getters: {
    getDiscussions(state) {
      return state.discussions;
    },
    getQuota(state) {
      return state.quota;
    },
    nbUnread(state, getters, rootState, rootGetters) {
      let nbUnread = 0;
      const userId = rootGetters["user/id"];
      for (let i = 0; i < state.discussions.length; ++i) {
        const discussion = state.discussions[i];
        if (
          (rootGetters["user/isDietician"] && !discussion.dietician) ||
          (userId === discussion.dietician &&
            (!discussion.DieticianReadDate || discussion.lastDate > discussion.dieticianReadDate))
        ) {
          nbUnread += 1;
        }
        if (
          userId === discussion.owner &&
          discussion.lastDate &&
          (!discussion.ownerReadDate || discussion.lastDate > discussion.ownerReadDate)
        ) {
          nbUnread += 1;
        }
      }
      return nbUnread;
    },
  },
  mutations: {},
  actions: {
    update({ dispatch, rootGetters }) {
      const userId = rootGetters["user/id"];
      dispatch(
        "system/updateAttr",
        {
          getAttribute: (rootState) => rootState.discussion.discussions,
          apiQuery: API.discussions,
          queryArg: [userId],
        },
        { root: true }
      );
      dispatch(
        "system/updateAttr",
        {
          getAttribute: (rootState) => rootState.discussion.quota,
          apiQuery: API.user.questionQuota,
          queryArg: [userId],
        },
        { root: true }
      );
    },
  },
};
