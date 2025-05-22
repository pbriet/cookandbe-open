import { isArray } from "lodash";

function makeDefer() {
  const d = {};
  d.promise = new Promise((resolve, reject) => {
    d.resolve = resolve;
    d.reject = reject;
  });
  return d;
}

export default {
  namespaced: true,
  state: {
    // Used to remember the page to redirect after a successfull login
    loginRedirectPage: null,
    // Used to generate unique defer ids
    _op_defer_counter: 1,
    // Used to store defers being used currently in services
    _op_defer_dict: {},
  },
  mutations: {
    setLoginRedirectPage(state, view) {
      if (view && view.name == "SignIn") {
        // setLoginRedirectPage will usually be called several times for each
        // requests that failed once the session has expired. Since the first
        // failing request will trigger a redirection to SignIn, all other calls
        // will call setLoginRedirectPage with 'SignIn' as parameter. We ignore
        // this value in order to keep the original url.
        return;
      }
      state.loginRedirectPage = view;
    },
  },
  actions: {
    /*
	  Creates a defer related to a service attribute

	  @param attribute: reference to the service attribute
	*/
    promiseAttr({ state, rootState }, { getAttribute }) {
      const attribute = getAttribute(rootState);
      if (attribute === null || attribute === undefined) {
        console.error("ERROR: bad service attribute");
        return;
      }
      const defer = makeDefer();

      if (attribute._op_defer_id !== undefined) {
        console.warn("WARNING: service attribute already has a defer, overwriting it");
        delete state._op_defer_dict[attribute._op_defer_id];
      }
      attribute._op_defer_id = state._op_defer_counter++;
      attribute.$promise = defer.promise;
      state._op_defer_dict[attribute._op_defer_id] = defer;
      return defer.promise;
    },
    /*
	  Resolves a defer related to a service attribute and remove it

	  @param attribute: reference to the service attribute
	  @param data: any object, will be passed to the success callback
	*/
    resolveAttr({ state, rootState }, { getAttribute, data }) {
      const attribute = getAttribute(rootState);
      if (!attribute._op_defer_id) {
        console.error("ERROR: bad service attribute");
        return;
      }
      const defer = state._op_defer_dict[attribute._op_defer_id];
      if (isArray(data) !== isArray(attribute)) {
        console.error("ERROR: storing invalid data format in attribute");
        return;
      }
      for (const field of Object.keys(data)) {
        attribute[field] = data[field];
      }
      defer.resolve(data);
      delete state._op_defer_dict[attribute._op_defer_id];
      delete attribute._op_defer_id;
    },
    /*
	  Completely manages the update of a service attribute through an API query

	  @param attribute: reference to the service attribute
	  @param apiQuery: API function used to retrieve the updated attribute data
	  @param queryArg: object passed in argument to the API function
	  @param transformFcn: optional function used to change the result of the query before storing it in the attribute
	  @param callback: optional function called after the attribute update
	*/
    updateAttr({ dispatch }, { getAttribute, apiQuery, queryArg, transformFcn, callback }) {
      const promise = dispatch("promiseAttr", { getAttribute });
      if (queryArg === undefined) {
        queryArg = [];
      }

      apiQuery(...queryArg).then((data) => {
        if (transformFcn) {
          data = transformFcn(data);
        }
        dispatch("resolveAttr", { getAttribute, data });
        if (callback) {
          callback();
        }
      });
      return promise;
    },
    // Retrieves and clears the view to load after a successfull login
    popLoginRedirectPage({ commit, state }) {
      if (state.loginRedirectPage === null) {
        return { name: "UserHome" };
      }

      const view = { ...state.loginRedirectPage };
      commit("setLoginRedirectPage", null);
      return view;
    },
  },
};
