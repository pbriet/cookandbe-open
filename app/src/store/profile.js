import { find } from "lodash";
import API from "@/api.js";

/*
 * Store managing the profiles of the current user
 */
export default {
  namespaced: true,
  state: {
    profiles: null,
    mainProfile: null,
    eaters: null,
  },
  getters: {
    getProfiles(state) {
      return state.profiles;
    },
    getMainProfile(state) {
      return state.mainProfile;
    },
    getEaterById: (state) => (id) => {
      return find(state.eaters, ["id", id]);
    },
  },
  mutations: {},
  actions: {
    async update({ state, rootGetters }) {
      const userId = rootGetters["user/id"];
      state.eaters = await API.eaters(userId);
      let mainProfile;
      return API.profiles(userId).then((profiles) => {
        state.profiles = profiles;
        for (const profile of state.profiles) {
          if (profile.isMainProfile) {
            mainProfile = profile;
            break;
          }
        }
        state.mainProfile = mainProfile;
        if (!state.mainProfile) {
          console.error("error : no main profile");
          throw new Error("No main profile found");
        }
      });
    },
  },
};
