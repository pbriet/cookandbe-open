import { includes, find, each } from "lodash";
import { ENABLE_PUBLIC_PAYMENT } from "@/config.js";
import { INDICATOR_GROUPS } from "@/_data.js";
import API from "@/api.js";

/*
 * Caching of diets
 */
export default {
  namespaced: true,
  state: {
    diets: null,
    tariffs: null,
    nutrientPacks: [],
    nbEnabledPacks: 0,
    packsPerNutrient: {},
    dietExclusions: [],
    dietWarnings: [],
  },
  getters: {
    getDiets(state) {
      return state.diets;
    },
    getNutrientPacks(state) {
      return state.nutrientPacks;
    },
    getPacksPerNutrient(state) {
      return state.packsPerNutrient;
    },
    getNbEnabledPacks(state) {
      return state.nbEnabledPacks;
    },
    getDietExclusions(state) {
      return state.dietExclusions;
    },
    getDietWarnings(state) {
      return state.dietWarnings;
    },
    dietById: (state) => (id) => {
      return find(state.diets, ["id", id]);
    },
    dietByKey: (state) => (key) => {
      return find(state.diets, ["key", key]);
    },
    levelTariff: (state) => (level) => {
      return state.tariffs[level];
    },
    levelLowestTariff: (state, getters) => (level, withoutDiscount) => {
      const values = getters.levelTariff(level);
      let res = 0;
      each(values, (value) => {
        if (res === 0 || value.afterDiscount < res) {
          if (withoutDiscount) {
            res = value.monthlyCost;
          } else {
            res = value.afterDiscount;
          }
        }
      });
      return res;
    },
    levelLowestTariffs: (state, getters) => (withoutDiscount) => {
      const res = {};
      each(Object.keys(state.tariffs), (level) => {
        res[level] = getters.levelLowestTariff(level, withoutDiscount);
      });
      return res;
    },
    // Returns the discount on this level for the current user
    levelDiscount: (state) => (level) => {
      let res = 0;
      for (const monthTariff of Object.values(state.tariffs[level] || {})) {
        if (monthTariff.discount > 0) {
          res = monthTariff.discount;
        }
      }
      return res;
    },
    excludedDishtypes(state, _, __, rootGetters) {
      const user = rootGetters["user/get"];
      if (user.objective.key === "gluten_free") {
        return ["Pain"];
      } else if (user.objective.key === "vegan") {
        return ["Fromage"];
      }
      return [];
    },
    isExcludedDishtype: (state, getters) => (dishTypeName) => {
      return includes(getters.excludedDishtypes, dishTypeName);
    },
  },
  mutations: {},
  actions: {
    loadPublic({ dispatch }) {
      if (ENABLE_PUBLIC_PAYMENT) {
        return Promise.all([dispatch("loadDiets"), dispatch("loadTariffs")]);
      } else {
        return Promise.all([dispatch("loadDiets")]);
      }
    },
    loadConnected({ dispatch }) {
      const promises = [
        dispatch("loadDiets"),
        dispatch("loadNutrientPacks"),
        dispatch("updateDietExclusions"),
        dispatch("updateDietWarnings"),
      ];

      if (ENABLE_PUBLIC_PAYMENT) {
        promises.push(dispatch("loadTariffs"));
      }
      return Promise.all(promises);
    },
    loadDiets({ state }) {
      return API.diets().then((diets) => {
        state.diets = diets;
        return diets;
      });
    },
    loadTariffs({ state }) {
      return API.tariffs().then((data) => {
        state.tariffs = data;
        return data;
      });
    },
    loadNutrientPacks({ state, rootGetters }) {
      return API.user.nutrientPacks(rootGetters["user/id"]).then(({ data }) => {
        state.nbEnabledPacks = 0;

        for (let y = 0; y < data.length; y++) {
          const pack = data[y];
          pack.indicatorsPerGroup = [];

          if (pack.enabled) {
            state.nbEnabledPacks += 1;
          }

          for (let i = 0; i < INDICATOR_GROUPS.length; i++) {
            const indicators = [];
            const group = INDICATOR_GROUPS[i];

            for (let j = 0; j < group.indicators.length; j++) {
              const key = group.indicators[j];
              if (pack.nutrients[key]) {
                indicators.push(pack.nutrients[key]);
              }
            }

            if (indicators.length) {
              pack.indicatorsPerGroup.push({ title: group.title, nutrients: indicators });
            }
          }

          for (let nutrientKey in pack.nutrients) {
            if (!state.packsPerNutrient[nutrientKey]) {
              state.packsPerNutrient[nutrientKey] = [];
            }
            state.packsPerNutrient[nutrientKey].push(pack);
          }
          state.nutrientPacks.push(pack);
        }
        return state.nutrientPacks;
      });
    },
    enablePack({ state, rootGetters }, { packKey, enabled }) {
      for (let i = 0; i < state.nutrientPacks.length; i++) {
        if (state.nutrientPacks[i].key == packKey) {
          state.nutrientPacks.enabled = enabled;
        }
      }
      const userId = rootGetters["user/id"];
      API.user.enableNutrientPack(userId, { packKey, enable: enabled });

      if (enabled) {
        state.nbEnabledPacks += 1;
      } else {
        state.nbEnabledPacks -= 1;
      }
    },
    updateDietExclusions({ rootGetters, dispatch }) {
      const user = rootGetters["user/get"];
      if (!user) {
        return Promise.resolve(true);
      }
      return dispatch(
        "system/updateAttr",
        {
          getAttribute: (rootState) => rootState.diet.dietExclusions,
          apiQuery: API.diet.excludedFoodtags,
          queryArg: [user.objective.id],
        },
        { root: true }
      );
    },
    updateDietWarnings({ rootGetters, dispatch }) {
      const user = rootGetters["user/get"];
      if (!user) {
        return Promise.resolve(true);
      }
      return dispatch(
        "system/updateAttr",
        {
          getAttribute: (rootState) => rootState.diet.dietWarnings,
          apiQuery: API.diet.forewarnedFoodtags,
          queryArg: [user.objective.id],
        },
        { root: true }
      );
    },
    async subscribeToDiet({ dispatch, rootGetters }, { dietId, parameters }) {
      const userId = rootGetters["user/id"];
      await API.user.subscribeToDiet(userId, dietId, { parameters });
      await dispatch("updateDietExclusions");
      await dispatch("updateDietWarnings");
    },
  },
};
