import { SECURE_MODE, ENABLE_DIET_CHOICE_AT_LOGIN } from "@/config.js";
import router from "@/router/index.js";
import API from "@/api.js";
import { setAuthTokens, clearAuthTokens } from "axios-jwt";

/*
 * Store managing the user logged in
 */
export default {
  namespaced: true,
  state: {
    user: null,
    stats: null,
    promoCode: null,
    facebookStatus: null,
  },
  mutations: {
    /*
     * Set the user info
     */
    setLoggedIn(state, data) {
      state.user = {};
      for (let attr in data) {
        if (attr == "username") {
          state.user["name"] = data[attr];
        } else if (attr == "userid") {
          state.user["id"] = data[attr];
        } else if (attr.substr(0, 2) == "is" && !SECURE_MODE) {
          state.user[attr] = false;
        } else {
          state.user[attr] = data[attr];
        }
      }
    },
    /*
     * Unset the user info. Drop JWT token
     */
    logout(state) {
      state.user = null;
      clearAuthTokens();
    },
    resetStats(state) {
      state.stats = null;
    },
    setPromoCode(state, value) {
      state.promoCode = value;
    },
    setUserFullname(state, { firstName, lastName }) {
      state.user.firstName = firstName;
      state.user.lastName = lastName;
    },
  },
  actions: {
    /*
     * Signup using user/password
     */
    async createAccount({ dispatch, state }, { email, firstName, password, proKey }) {
      const response = await API.signup({ email, firstName, password, proKey, promoCode: state.promoCode });
      if (response.data.status === "ok") {
        dispatch("onSuccessLogin", response);
        return {
          connected: true,
        };
      }
      return {
        connected: false,
        data: response.data,
      };
    },

    /*
     * On successful login : save JWT tokens & load user data
     */
    async onSuccessLogin({ commit, dispatch }, response) {
      // Save JWT token
      setAuthTokens({
        accessToken: response.data.access,
        refreshToken: response.data.refresh,
      });
      // Commit logged-in user details
      const currentUser = await API.currentUser();
      commit("setLoggedIn", currentUser);

      if (ENABLE_DIET_CHOICE_AT_LOGIN && ! currentUser.dietChangedAt) {
        // No diet has ever been selected
        // Ugly patch.
        // There is a conflict between this redirection, and the automatic redirection done by "redirectIfLogged"
        // In VueX router
        // By delaying the "router.push" significantly, this route will be the last one intepreted
        setTimeout(function() {
          router.push({ name: "DietChoice", query: { config_completion: "fast" } });
        }, 2000)
      }
      else if (currentUser.justExpired) {
        router.push({ name: "Expired" });
      } else {
        const loginRedirectPage = await dispatch("system/popLoginRedirectPage", '', { root: true });
        router.push(loginRedirectPage);
      }
    },
    /*
     * Standard login function
     */
    async login({ commit, dispatch }, args) {
      var response;
      try {
        response = await API.login(args);
      } catch (e) {
        return {
          connected: false,
          data: e.response.data,
        };
      }
      const status = response.status;
      if (status == 200) {
        dispatch("onSuccessLogin", response);
        return {
          connected: true,
        };
      }
      commit("logout");
      return {
        connected: false,
        data: response.data,
      };
    },
    /*
     * Update the user data by retrieving them from servers
     */
    async load({ commit, dispatch }) {
      // Autologin token in GET args ?
      const token = new URLSearchParams(location.search).get("autologin_token");
      if (token) {
        const response = await API.autologin({ token });
        if (response.data.status == "ok") {
          dispatch("onSuccessLogin", response);
        } else {
          router.push({ name: "WrongToken" });
        }
      }
      const currentUser = await API.currentUser();
      if (currentUser.status == "logged in") {
        commit("setLoggedIn", currentUser);
      } else {
        commit("logout");
      }
    },
    /*
     * Retrieve user stats from server
     */
    async getStats({ state }) {
      if (!state.user.id) {
        return null;
      }
      if (state.stats !== null) {
        return state.stats;
      }
      state.stats = {};
      state.stats = await API.user.stats(state.user.id);
      return state.stats;
    },
    /*
     * Signup using facebook
     */
    async createAccountFromFacebook({ dispatch, state }) {
      await dispatch("loadFbStatus");
      const response = await API.facebook_signup({
        access_token: state.facebookStatus.accessToken,
        promo_code: state.promoCode,
      });
      if (response.data.status === "ok") {
        dispatch("onSuccessLogin", response);
        return {
          connected: true,
        };
      }
      return {
        connected: false,
        data: response.data,
      };
    },
    /*
     * Login using facebook
     */
    async loginFromFacebook({ dispatch }) {
      await dispatch("loadFbStatus");
      return await dispatch("serverFacebookLogin");
    },
    /*
     * Retrieve from facebook his current status on our app
     */
    loadFbStatus({ state }, force) {
      return new Promise((resolve) => {
        if (!force && state.facebookStatus && state.facebookStatus.accessToken) {
          resolve(state.facebookStatus);
        }

        state.facebookStatus = {};
        window.FB.getLoginStatus((response) => {
          state.facebookStatus = { ...state.facebookStatus, ...response.authResponse };
          resolve(state.facebookStatus);
        });
      });
    },
    /*
     * Ask the server to login from a facebook token
     */
    async serverFacebookLogin({ state, commit, dispatch }) {
      var response;
      try {
        response = await API.facebook_login({ fbInputToken: state.facebookStatus.accessToken });
      } catch (e) {
        return {
          connected: false,
          data: e.response.data,
        };
      }
      const status = response.status;
      if (status == 200) {
        dispatch("onSuccessLogin", response);
        return {
          connected: true,
        };
      }
      commit("logout");
      return {
        connected: false,
        data: response.data,
      };
    },
    toggleUstensil({ state }, { ustensil, selected }) {
      if (selected) {
        state.user.ustensils.push(ustensil.id);
        return API.user.addUstensil(state.user.id, { ustensilId: ustensil.id });
      } else {
        const pos = state.user.ustensils.indexOf(ustensil.id);
        state.user.ustensils.splice(pos, 1);
        return API.user.removeUstensil(state.user.id, { ustensilId: ustensil.id });
      }
    },
    activateObjective({ state, dispatch }, { objective, parameters }) {
      state.user.objective = objective;
      return dispatch("diet/subscribeToDiet", { dietId: objective.id, parameters }, { root: true });
    },
  },
  getters: {
    get(state) {
      return state.user;
    },
    id(state) {
      if (!state.user) {
        return null;
      }
      return state.user.id;
    },
    isLoggedIn(state) {
      return state.user !== null;
    },
    /*
     * Returns true if user is less than 24h old
     */
    recentlyJoined(state) {
      const joinedAt = new Date(state.user.creationDate);
      const now = new Date();
      const seconds = Math.floor(now - joinedAt);
      if (seconds / 3600000 < 24) {
        return true;
      }
      return false;
    },
    /*
     * Returns the currently activated user objective
     */
    getObjectiveDetails(state, _, __, rootGetters) {
      const objectiveId = state.user.objective.id;
      if (objectiveId) {
        return rootGetters["diet/dietById"](objectiveId);
      }
      return null;
    },
    isAdmin(state) {
      return state.user && state.user.isAdmin;
    },
    isReviewer(state) {
      return state.user && state.user.isReviewer;
    },
    isOperator(state) {
      return state.user && state.user.isOperator;
    },
    isDeveloper(state) {
      return state.user && state.user.isDeveloper;
    },
    isAuthor(state) {
      return state.user && state.user.isAuthor;
    },
    isDietician(state) {
      return state.user && state.user.isDietician;
    },
    isFacebookDisabled() {
      return typeof window.FB === "undefined" || window.FB === undefined || window.FB === null;
    },
  },
};
