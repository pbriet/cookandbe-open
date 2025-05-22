import { isEmpty } from "lodash";
import API from "@/api.js";

export default {
  namespaced: true,
  state: {
    profileTastes: {},
    profileTastesLoaded: false,
    userProfiles: {},
  },
  getters: {
    getProfileTastesLoaded(state) {
      return state.profileTastesLoaded;
    },
  },
  mutations: {},
  actions: {
    init({ state, dispatch, rootGetters }) {
      const promises = [];
      state.userProfiles = rootGetters["profile/getProfiles"];
      for (let i = 0; i < state.userProfiles.length; ++i) {
        const profileId = state.userProfiles[i].id;
        state.profileTastes[profileId] = [];
        promises.push(dispatch("get", profileId));
      }
      return Promise.all(promises).then(() => {
        state.profileTastesLoaded = true;
      });
    },
    getMain({ dispatch, rootGetters }) {
      const user = rootGetters["user/get"];
      return dispatch("get", user.mainProfileId);
    },
    get({ state, dispatch }, profileId) {
      if (!isEmpty(state.profileTastes[profileId])) {
        return Promise.resolve(state.profileTastes[profileId]);
      }
      return dispatch(
        "system/updateAttr",
        {
          getAttribute: (rootState) => rootState.taste.profileTastes[profileId],
          apiQuery: API.tastes,
          queryArg: [profileId, "food_tag"],
        },
        { root: true }
      );
    },
    async add({ state, dispatch }, { profileId, foodTag, fondness, setPlanningExpired }) {
      await dispatch("get", profileId);
      const taste = {
        fondness,
        foodTag: foodTag.id,
        profile: profileId,
        setPlanningExpired,
      };
      // Creates the taste server side
      const data = await API.taste.save(taste);
      if (!data.status) {
        data.foodTag = foodTag;
        state.profileTastes[profileId].push(data);
      }
      return data;
    },
    async del({ state }, { profileId, tasteId }) {
      await API.taste.remove(tasteId);
      state.profileTastes[profileId] = state.profileTastes[profileId].filter((taste) => taste.id != tasteId);
    },
  },
};
