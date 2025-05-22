import { isFunction } from "lodash";
import { BASE_URL, ENABLE_DISCUSSION } from "@/config.js";
import { h } from "vue";
import { RouterView, createRouter, createWebHistory } from "vue-router";
import SignIn from "@/views/user/SignIn.vue";
import Logout from "@/views/user/Logout.vue"
import Invitation from "@/views/user/Invitation.vue";
import Expired from "@/views/objective/Expired.vue";
import CriticalError from "@/views/system/CriticalError.vue";
import PermissionDenied from "@/views/system/PermissionDenied.vue";
import NoSuchPage from "@/views/system/NoSuchPage.vue";
import WrongToken from "@/views/user/WrongToken.vue";
import UserHome from "@/views/user/UserHome.vue";
import Calendar from "@/views/planning/Calendar.vue";
import DayPlanner from "@/views/planning/DayPlanner.vue";
import DayView from "@/views/planning/DayView.vue";
import RecipeView from "@/views/recipe/RecipeView.vue";
import RecipeEditor from "@/views/recipe/RecipeEditor.vue";
import Shopping from "@/views/shopping/Shopping.vue";
import ShoppingListContent from "@/views/shopping/ShoppingListContent.vue";
import Cookbook from "@/views/recipe/cookbook/Cookbook.vue";
import CookbookSearch from "@/views/recipe/cookbook/CookbookSearch.vue";
import MyAccount from "@/views/objective/MyAccount.vue";
import Config from "@/views/config/Config.vue";
import UserProfileConfig from "@/views/config/UserProfileConfig.vue";
import AttendanceConfig from "@/views/config/AttendanceConfig.vue";
import Preconfiguration from "@/views/config/Preconfiguration.vue";
import FamilyConfig from "@/views/config/FamilyConfig.vue";
import EquipmentConfig from "@/views/config/EquipmentConfig.vue";
import HabitsConfig from "@/views/config/HabitsConfig.vue";
import TastesConfig from "@/views/config/TastesConfig.vue";
import OtherConfig from "@/views/config/OtherConfig.vue";
import Settings from "@/views/user/Settings.vue";
import SignUp from "@/views/tunnel/SignUp.vue";
import PaymentChoice from "@/views/tunnel/PaymentChoice.vue";
import PaymentStatus from "@/views/tunnel/PaymentStatus.vue";
import PremiumChoice from "@/views/tunnel/PremiumChoice.vue";
import DietChoice from "@/views/tunnel/DietChoice.vue";
import DiscussionList from "@/views/discussion/DiscussionList.vue";
import DiscussionContent from "@/views/discussion/DiscussionContent.vue";
import store from "@/store/index.js";

/*
 * CUSTOM ATTRIBUTES :
 * requiresAuth (default true)
 *        - Whether the user need to be logged in to access this page or not
 *
 * redirectIfLogged (default null)
 *        - if defined, if the user access this page and is logged in, he's redirected to this url
 *
 * noIndex (default: false if public, true if not public)
 *        - if set to true, bots may index the content of this page. Otherwise, a meta tag says not to.
 */
let routes = [
  {
    path: "",
    redirect: { name: "UserHome" },
  },
  {
    path: "/signup/:diet?",
    name: "SignUp",
    component: SignUp,
    meta: {
      title: "Inscription",
      noIndex: true,
      requiresAuth: false,
      redirectIfLogged(params) {
        return { name: "DietChoice", params: params.diet ? { diet: params.diet } : null };
      },
    },
  },
  {
    path: "/invitation/:inviteKey",
    name: "Invitation",
    component: Invitation,
    meta: { title: "Invitation", requiresAuth: false, redirectIfLogged: { name: "UserHome" } },
  },
  {
    path: "/diet_choice/:diet?",
    name: "DietChoice",
    component: DietChoice,
    meta: { title: "Choix de l'alimentation" },
  },
  {
    path: "/premium_choice",
    name: "PremiumChoice",
    component: PremiumChoice,
    meta: { title: "Choix de l'abonnement" },
  },
  {
    path: "/payment_choice/:level?",
    name: "PaymentChoice",
    component: PaymentChoice,
    meta: { title: "Choix du paiement" },
  },
  {
    path: "/payment_status/:status",
    name: "PaymentStatus",
    component: PaymentStatus,
    meta: { title: "Paiement" },
  },
  {
    path: "/userhome",
    name: "UserHome",
    component: UserHome,
    meta: { title: "Tableau de bord" },
  },
  {
    path: "/signin/:reason?",
    name: "SignIn",
    component: SignIn,
    meta: { title: "Connexion", noIndex: true, requiresAuth: false, redirectIfLogged: { name: "UserHome" } },
  },
  {
    path: "/logout",
    name: "Logout",
    component: Logout,
    meta: { title: "Logout", noIndex: true, requiresAuth: false },
  },
  {
    path: "/permission_denied",
    name: "PermissionDenied",
    component: PermissionDenied,
    meta: { title: "Droits insuffisants", noIndex: true, requiresAuth: false },
  },
  {
    path: "/expired",
    name: "Expired",
    component: Expired,
    meta: { title: "Abonnement terminé" },
  },
  {
    path: "/critical_error",
    name: "CriticalError",
    component: CriticalError,
    meta: { title: "Erreur", noIndex: true, requiresAuth: false },
  },
  {
    path: "/no_such_page",
    name: "NoSuchPage",
    component: NoSuchPage,
    meta: { title: "Cette page n'existe plus", noIndex: true, requiresAuth: false },
  },
  {
    path: "/wrong_token",
    name: "WrongToken",
    component: WrongToken,
    meta: { title: "Connexion impossible", requiresAuth: false },
  },
  {
    path: "/calendar/:fromDay?",
    name: "Calendar",
    component: Calendar,
  },
  {
    path: "/day_planner/:day?",
    name: "DayPlanner",
    component: DayPlanner,
  },
  {
    path: "/day/:day/:meal?",
    name: "DayView",
    component: DayView,
  },
  {
    path: "/recettes/recette-:recipeKey",
    name: "RecipeView",
    component: RecipeView,
  },
  {
    path: "/recettes/:recipeId/edit",
    name: "RecipeEditor",
    component: RecipeEditor,
    meta: { title: "Edition d'une recette" },
  },
  {
    path: "/shopping_list",
    component: { render: () => h(RouterView) },
    children: [
      {
        path: "",
        name: "Shopping",
        component: Shopping,
        meta: { title: "Liste de courses" },
      },
      {
        path: ":shoppingListId",
        name: "ShoppingListContent",
        component: ShoppingListContent,
        meta: { title: "Liste de courses" },
      },
    ],
  },
  {
    path: "/carnet/:tab?",
    name: "Cookbook",
    component: Cookbook,
    meta: { title: "Carnet de recettes", description: "Vos recettes préférées" },
  },
  {
    path: "/carnet/ajouter",
    name: "CookbookSearch",
    component: CookbookSearch,
    meta: { title: "Carnet de recettes", description: "Vos recettes préférées" },
  },
  {
    path: "/my_account",
    name: "MyAccount",
    component: MyAccount,
    meta: { title: "Mon compte" },
  },
  {
    path: "/config",
    component: { render: () => h(RouterView) },
    children: [
      {
        path: "",
        name: "Config",
        component: Config,
        meta: { title: "Configuration" },
      },
      {
        path: "user_profile",
        name: "UserProfileConfig",
        component: UserProfileConfig,
        meta: { title: "Configuration du profil" },
      },
      {
        path: "attendance",
        name: "AttendanceConfig",
        component: AttendanceConfig,
        meta: { title: "Configuration des présences" },
      },
      {
        path: "family",
        name: "FamilyConfig",
        component: FamilyConfig,
        meta: { title: "Configuration du foyer" },
      },
      {
        path: "equipment",
        name: "EquipmentConfig",
        component: EquipmentConfig,
        meta: { title: "Configuration de l'équipement" },
      },
      {
        path: "habits",
        name: "HabitsConfig",
        component: HabitsConfig,
        meta: { title: "Configuration des habitudes" },
      },
      {
        path: "tastes/:profileId?",
        name: "TastesConfig",
        component: TastesConfig,
        meta: { title: "Configuration des goûts" },
      },
      {
        path: "other",
        name: "OtherConfig",
        component: OtherConfig,
        meta: { title: "Configuration divers" },
      },
    ],
  },
  {
    path: "/preconfiguration",
    name: "Preconfiguration",
    component: Preconfiguration,
    meta: { title: "Configuration rapide" },
  },
  {
    path: "/settings",
    name: "Settings",
    component: Settings,
    meta: { title: "Paramètres utilisateur" },
  },
];

if (ENABLE_DISCUSSION) {
  routes = [
    ...routes,
    ...[
      {
        path: "/discussion",
        component: { render: () => h(RouterView) },
        children: [
          {
            path: "",
            name: "DiscussionList",
            component: DiscussionList,
            meta: { title: "Discussions" },
          },
          {
            path: ":discussionId",
            name: "DiscussionContent",
            component: DiscussionContent,
            meta: { title: "Discussion" },
          },
        ],
      },
    ],
  ];
}

// Page not found
routes.push({ path: "/:pathMatch(.*)*", redirect: { path: "/" } });

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

function applyRouteMeta(to) {
  // Resetting title and metadata
  store.commit("meta/reset");
  // Apply the custom parameters defined on this route
  if (to.meta.title) {
    store.commit("meta/setTitle", to.meta.title);
  }
  if (to.meta.description) {
    store.commit("meta/setDescription", to.meta.description);
  }
  if (to.meta.keywords) {
    store.commit("meta/setKeywords", to.meta.keywords);
  }
  if (to.meta.noIndex || (to.meta.requiresAuth ?? true)) {
    store.commit("meta/setNoIndex");
  }
}

router.beforeEach((to, _, next) => {
  // Start after whenInitialized has resolved to make sure user/isLoggedIn is set
  store.state.services.whenInitialized.promise.then(() => {
    const isLoggedIn = store.getters["user/isLoggedIn"];
    if (to.matched.some((route) => route.meta.requiresAuth ?? true) && !isLoggedIn) {
      if (to.query["autologin_token"]) {
        next({ name: "WrongToken" });
      } else {
        store.commit("system/setLoginRedirectPage", to);
        next({ name: "SignIn", params: { reason: "required" } });
      }
    } else if (to.meta.redirectIfLogged && isLoggedIn) {
      const redirectIfLogged = to.meta.redirectIfLogged;
      const newRoute = isFunction(redirectIfLogged) ? redirectIfLogged(to.params) : redirectIfLogged;
      if (newRoute) {
        next({ ...newRoute, replace: true });
      } else {
        next();
      }
      applyRouteMeta(to);
    } else {
      next();
      applyRouteMeta(to);
    }
  });
});

const history = [];

router.afterEach((to, from, failure) => {
  if (failure) {
    return;
  }
  // Saving previous path
  if (history.length === 0 || history[history.length - 1] != to.fullPath) {
    history.push(to.fullPath);
    // Google Analytics activation
    if (store.getters["analytics/ENABLE_GOOGLE_ANALYTICS"]) {
      window.ga("send", "pageview", { page: to.fullPath });
    }
  }

  // Scrolls to top of page after each route change
  window.scrollTo({
    top: 0,
    left: 0,
    behavior: "instant",
  });
});

// Returns the previous url the user was
export function previousUrl() {
  if (history.length <= 1) {
    return null;
  }
  return BASE_URL + history[history.length - 2];
}

export function goBack(defaultUrl, nb = 1) {
  if (history.length > nb) {
    router.push(history[history.length - nb - 1]);
  } else if (defaultUrl) {
    router.push(defaultUrl);
  } else {
    router.go(-1);
  }
}

export default router;
