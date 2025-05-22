export default {
  namespaced: true,
  state: {
    signupTerms: false,
    loginPopup: false,
    maintenanceModal: false,
    premiumModal: false,
    tutorialOverlay: false,
    whyCalories: false,
  },
  getters: {
    signupTerms(state) {
      return state.signupTerms;
    },
    loginPopup(state) {
      return state.loginPopup;
    },
    maintenanceModal(state) {
      return state.maintenanceModal;
    },
    premiumModal(state) {
      return state.premiumModal;
    },
    tutorialOverlay(state) {
      return state.tutorialOverlay;
    },
    whyCalories(state) {
      return state.whyCalories;
    },
  },
  mutations: {
    showSignupTerms(state) {
      state.signupTerms = true;
    },
    hideSignupTerms(state) {
      state.signupTerms = false;
    },
    showLoginPopup(state) {
      state.loginPopup = true;
    },
    hideLoginPopup(state) {
      state.loginPopup = false;
    },
    showMaintenanceModal(state) {
      state.maintenanceModal = true;
    },
    hideMaintenanceModal(state) {
      state.maintenanceModal = false;
    },
    showPremiumModal(state) {
      state.premiumModal = true;
    },
    hidePremiumModal(state) {
      state.premiumModal = false;
    },
    showTutorialOverlay(state) {
      state.tutorialOverlay = true;
    },
    hideTutorialOverlay(state) {
      state.tutorialOverlay = false;
    },
    showWhyCalories(state) {
      state.whyCalories = true;
    },
    hideWhyCalories(state) {
      state.whyCalories = false;
    },
  },
  actions: {},
};
