import { find, findIndex } from "lodash";
import router from "@/router";
import { startTutorial } from "@/tutorial.js";
import API from "@/api.js";
import { ENABLE_DIET_CHOICE_AT_LOGIN } from '@/config.js'

let FAST_STEPS = [
  { name: "Vous", description: "Votre profil", route: { name: "UserProfileConfig" } },
  { name: "Vos préférences", description: "Temps, budget, goûts", route: { name: "Preconfiguration" } },
];

if (ENABLE_DIET_CHOICE_AT_LOGIN) {
  FAST_STEPS.unshift(
    { name: "Alimentation", description: "Votre alimentation", route: { name: "DietChoice" } }
  )
}

/*
 * Store managing the configuration stages that have been completed or not
 */
export default {
  namespaced: true,
  state: {
    stages: [],
    expired: false,
    stats: { nbCompleted: 0, nbIncomplete: 0, completion: 0 },
  },
  mutations: {},
  getters: {
    getStats(state) {
      return state.stats;
    },
    getStages(state) {
      return state.stages;
    },
    configMode(state, getters, rootState) {
      return rootState.route.query?.config_completion;
    },
    configSteps(_, getters, rootState) {
      let steps = [];
      if (!getters.configMode) {
        return steps;
      }

      // Steps depends on configuration mode
      if (getters.configMode === "fast") {
        steps = FAST_STEPS;
      }

      // Locating current step
      const iCurrentStep = findIndex(steps, ["route.name", rootState.route.name]);

      // Initializing status for steps
      for (let i = 0; i < steps.length; i++) {
        const step = steps[i];
        if (i == iCurrentStep) {
          step.status = "active";
        } else if (i > iCurrentStep) {
          step.status = "disabled";
        } else {
          step.status = "complete";
        }
        step.route.query = { config_completion: getters.configMode };
      }

      return steps;
    },
  },
  actions: {
    update({ state, dispatch, rootGetters }) {
      const userId = rootGetters["user/id"];
      dispatch(
        "system/updateAttr",
        {
          getAttribute: (rootState) => rootState.configStage.stages,
          apiQuery: API.configStage,
          queryArg: [userId],
          transformFcn(data) {
            state.stats.nbCompleted = 0;
            state.expired = false;
            for (let index = 0; index < data.length; ++index) {
              const stage = data[index];
              stage.skip = stage.status === "filled";
              if (stage.status !== "empty") {
                state.stats.nbCompleted += 1;
              }
              if (stage.status === "expired") {
                state.expired = true;
              }
            }
            state.stats.completion = Math.round((100 * state.stats.nbCompleted) / data.length);
            state.stats.nbIncomplete = data.length - state.stats.nbCompleted;
            return data;
          },
        },
        { root: true }
      );
      return state.stages.$promise;
    },
    /*
     * Complete a config stage
     */
    async complete({ dispatch, rootGetters }, { stageName, callback, modifyMetaplanning = false }) {
      if (!rootGetters["user/isLoggedIn"]) {
        console.log("completion cancelled because user is not logged in anymore");
        return;
      }
      await API.completeStage(rootGetters["user/id"], { stageKey: stageName, modifyMetaplanning });
      dispatch("update");
      callback && callback();
    },
    nextConfig({ getters }) {
      if (getters.configSteps[getters.configSteps.length - 1].status == "active") {
        // Configuration complete !
        router.push({ name: "Calendar" });
        setTimeout(() => {
          startTutorial("menuTutorial");
        }, 500);
        return;
      }
      const nextStep = find(getters.configSteps, ["status", "disabled"]);
      router.push(nextStep.route);
    },
    /*
     * If this is a brand new user (no completion), redirects to configuration completion
     * Else redirect to my account
     */
    redirectAfterSubscriptionModification({ state, dispatch }) {
      console.log('redirectAfterSubscriptionModification')
      if (state.stats.completion === 0) {
        console.log('moveToConfigCompletion')
        dispatch("moveToConfigCompletion");
      } else {
        console.log('to my account')
        router.push({ name: "MyAccount" });
      }
    },
    moveToConfigCompletion() {
      console.log('moveToConfigCompletion')
      router.push({ name: "UserProfileConfig", query: { config_completion: "fast" } });
    },
  },
};
