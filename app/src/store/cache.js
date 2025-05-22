import API from "@/api.js";
import { find, includes } from "lodash";

/*
 * Caching of many static objects :
 * - dishTypes
 * - mealPlaces
 */
export default {
  namespaced: true,
  state: {
    dishTypes: null,
    mealPlaces: null,
    locations: null,
    nutrients: null,
    nutrientCategories: null,
  },
  getters: {
    dishTypeById: (state) => (id) => {
      return find(state.dishTypes, ["id", id]);
    },
    /*
     * Returns a dictionary {dishTypeId : dishType}
     */
    getDishTypesDict(state) {
      var res = {};
      for (var i = 0; i < state.dishTypes.length; i++) {
        res[state.dishTypes[i].id] = state.dishTypes[i];
      }
      return res;
    },
    getDishTypes: (state) => (filterIds, singleAttr) => {
      const res = [];
      for (let dishType of state.dishTypes || []) {
        if (!filterIds || includes(filterIds, dishType.id)) {
          if (!singleAttr) {
            res.push(dishType);
          } else {
            res.push(dishType[singleAttr]);
          }
        }
      }
      return res;
    },
    getLocations(state) {
      const formatLocation = (location) => {
        // text is needed by select2
        return { ...location, text: location.name, children: location.children.map(formatLocation) };
      };

      return state.locations.map(formatLocation);
    },
  },
  mutations: {},
  actions: {
    load({ dispatch }) {
      return Promise.all([
        dispatch("loadDishtypes"),
        dispatch("loadMealplaces"),
        dispatch("loadLocations"),
        dispatch("loadNutrients"),
      ]);
    },
    async loadDishtypesIfNot({ state, dispatch }) {
      if (state.dishTypes === null) {
        await dispatch("loadDishtypes");
      }
    },
    loadDishtypes({ state }) {
      return API.dishTypes().then((dishTypes) => {
        state.dishTypes = dishTypes;
      });
    },
    loadMealplaces({ state }) {
      return API.mealPlaces().then((mealPlaces) => {
        state.mealPlaces = mealPlaces;
      });
    },
    loadLocations({ state }) {
      return API.locations().then((locations) => {
        state.locations = locations;
      });
    },
    loadNutrients({ state }) {
      return Promise.all([
        API.nutrients().then((nutrients) => {
          state.nutrients = nutrients;
        }),
        API.nutrientCategories().then((nutrientCategories) => {
          state.nutrientCategories = nutrientCategories;
        }),
      ]);
    },
  },
};
