import { APP_BRAND_NAME, ENABLE_LOGO, IMG_BRAND} from "@/config.js";

/*
 * Store managing the profiles of the current user
 */
export default {
  namespaced: true,
  state: {
    title: null,
    ogType: null,
    ogImage: null,
    ogImageWidth: null,
    ogImageHeight: null,
    description: null,
    robotsInfos: null,
    statusCode: null,
    keywords: null,
  },
  getters: {
    title(state) {
      if (!state.title) return APP_BRAND_NAME;
      return state.title + " - " + APP_BRAND_NAME;
    },
    keywords(state) {
      return state.keywords;
    },
    ogTitle(state) {
      return state.title;
    },
    ogType(state) {
      return state.ogType;
    },
    ogImage(state) {
      return state.ogImage;
    },
    ogImageWidth(state) {
      return state.ogImageWidth;
    },
    ogImageHeight(state) {
      return state.ogImageHeight;
    },
    statusCode(state) {
      return state.statusCode;
    },
    description(state) {
      return state.description;
    },
    robotsInfos(state) {
      return state.robotsInfos;
    },
  },
  mutations: {
    reset(state) {
      state.title = "Rééquilibrage alimentaire avec menus personnalisés pour la semaine";
      state.description =
        "Pour un rééquilibrage alimentaire avec des menus équilibrés, menus végétariens, menus sans gluten pour toute la semaine ! Nos menus s’adaptent à vos contraintes et à vos besoins";
      state.keywords = "menus semaine, rééquilibrage alimentaire, planification, idées repas, équilibre";
      state.ogType = "website";
      if (ENABLE_LOGO) {
        state.ogImage = '/' + IMG_BRAND + '/img/logo1.jpg';
      } else {
        state.ogImage = "";
      }
      state.ogImageWidth = null;
      state.ogImageHeight = null;
      state.robotsInfos = "";
      state.statusCode = 200;
    },
    set404(state) {
      state.title = "Cette page n'existe plus";
      state.description = "Cette page n'existe plus";
      state.keywords = "";
      state.ogType = "website";
      state.ogImage = null;
      state.robotsInfos = "noindex";
      state.statusCode = 404;
    },
    setOgImage(state, value) {
      state.ogImage = value;
      if (!value) {
        return;
      }
      // Loading the image to retrieve width / height
      const img = new Image();
      img.onload = () => {
        // setTimeout forces img to update, so that header really contains width and height
        setTimeout(() => {
          state.ogImageWidth = img.naturalWidth;
          state.ogImageHeight = img.naturalHeight;
        });
      };
      img.src = value; // TODO: vérifier que cela marche en staging/prod
    },
    setDescription(state, value) {
      state.description = value;
    },
    setKeywords(state, value) {
      state.keywords = value;
    },
    setTitle(state, value) {
      state.title = value;
    },
    setOgType(state, value) {
      state.ogType = value;
    },
    setNoIndex(state) {
      state.robotsInfos = "noindex";
    },
  },
  actions: {},
};
