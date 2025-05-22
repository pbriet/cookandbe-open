import { ENABLE_GOOGLE_ANALYTICS } from "@/config.js";

export default {
  namespaced: true,
  state: {
    ENABLE_GOOGLE_ANALYTICS,
  },
  mutations: {
    disableGoogleAnalytics(state) {
      state.ENABLE_GOOGLE_ANALYTICS = false;
    },
  },
  getters: {
    ENABLE_GOOGLE_ANALYTICS(state) {
      return state.ENABLE_GOOGLE_ANALYTICS;
    },
  },
  actions: {
    sendEvent({ state }, { category, action, label, value }) {
      if (!state.ENABLE_GOOGLE_ANALYTICS) {
        return;
      }
      window.ga("send", "event", category, action, label, value);
    },
  },
};
