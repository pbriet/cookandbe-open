function defer() {
  const d = {};
  d.promise = new Promise((resolve, reject) => {
    d.resolve = resolve;
    d.reject = reject;
  });
  return d;
}

/*
 * Store managing the initialization of other stores
 */
export default {
  namespaced: true,
  state: {
    whenInitialized: defer(),
  },
  getters: {},
  mutations: {},
  actions: {
    /*
     * Function to load uservoice and activate the required elements on the new page
     */
    loadUservoice({ rootGetters }) {
      const user = rootGetters["user/get"];
      const UserVoice = window.UserVoice || [];

      // Set colors
      UserVoice.push([
        "set",
        {
          accent_color: "#6aba2e",
          trigger_color: "white",
          trigger_background_color: "#e23a39",
        },
      ]);

      // Identify the user and pass traits
      // To enable, replace sample data with actual user traits and uncomment the line
      UserVoice.push([
        "identify",
        {
          email: user.email, // User’s email address
          name: user.name, // User’s real name
          //created_at: 1364406966, // Unix timestamp for the date the user signed up
          id: user.id, // Optional: Unique id of the user (if set, this should not change)
        },
      ]);

      // Autoprompt for Satisfaction and SmartVote (only displayed under certain conditions)
      UserVoice.push(["autoprompt", {}]);
    },
    /*
     * Loads all the services.
     * Return a promise  "when everything is loaded"
     */
    init({ state, dispatch, rootGetters }, reset) {
      if (reset) {
        state.whenInitialized = defer();
      }
      dispatch("user/load", null, { root: true }).then(() => {
        if (!rootGetters["user/isLoggedIn"]) {
          // Not logged in : only initialize the diet service
          dispatch("diet/loadPublic", null, { root: true }).then(state.whenInitialized.resolve);
          return;
        }
        // Logged in : initialize all the services
        // Asynchronous :
        dispatch("profile/update", null, { root: true }).then(() => {
          dispatch("taste/init", null, { root: true }).then(() => {
            dispatch("taste/getMain", null, { root: true }).then((tastes) => {
              dispatch("recipeFilter/init", tastes, { root: true });
            });
          });
        });
        dispatch("shopping/update", null, { root: true });
        dispatch("planning/update", null, { root: true });
        dispatch("equipment/update", null, { root: true });
        dispatch("discussion/update", null, { root: true });
        dispatch("cookbook/update", null, { root: true });
        // Must be loaded before any routing ("synchronous") :
        const promises = [
          dispatch("configStage/update", null, { root: true }),
          dispatch("cache/load", null, { root: true }),
          dispatch("diet/loadConnected", null, { root: true }),
        ];
        Promise.all(promises).then(() => {
          dispatch("loadUservoice");
          state.whenInitialized.resolve();
        });
      });
      return state.whenInitialized.promise;
    },
  },
};
