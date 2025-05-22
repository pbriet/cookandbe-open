function boolEnv(key) {
  const value = process.env[key].toLowerCase();
  if (value != "true" && value != "false") {
    console.error("Invalid env var", key, ", expected boolean, got", process.env[key]);
    return process.env[key];
  }
  return value == "true";
}


export const ENABLE_CONTACT = boolEnv("VUE_APP_ENABLE_CONTACT");
export const ENABLE_DIET_CHOICE = boolEnv("VUE_APP_ENABLE_DIET_CHOICE");
export const ENABLE_DIET_CHOICE_AT_LOGIN = boolEnv("VUE_APP_ENABLE_DIET_CHOICE_AT_LOGIN");
export const ENABLE_DIET_DIAGNOSIS_RESULTS = boolEnv("VUE_APP_ENABLE_DIET_DIAGNOSIS_RESULTS");
export const ENABLE_DIET_FORCE_SLIM_DIAGNOSIS = boolEnv("VUE_APP_ENABLE_DIET_FORCE_SLIM_DIAGNOSIS");
export const ENABLE_DISCUSSION = boolEnv("VUE_APP_ENABLE_DISCUSSION");
export const ENABLE_EMAILS = boolEnv("VUE_APP_ENABLE_EMAILS");
export const ENABLE_FACEBOOK = boolEnv("VUE_APP_ENABLE_FACEBOOK");
export const ENABLE_FLYMENU = boolEnv("VUE_APP_ENABLE_FLYMENU");
export const ENABLE_GOOGLE_ANALYTICS = boolEnv("VUE_APP_ENABLE_GOOGLE_ANALYTICS");
export const ENABLE_LEGAL = boolEnv("VUE_APP_ENABLE_LEGAL");
export const ENABLE_LOGO = boolEnv("VUE_APP_ENABLE_LOGO");
export const ENABLE_NEWSLETTER = boolEnv("VUE_APP_ENABLE_NEWSLETTER");
export const ENABLE_NUTRIENT_PACKS = boolEnv("VUE_APP_ENABLE_NUTRIENT_PACKS");
export const ENABLE_PASSWORD_CHANGE = boolEnv("VUE_APP_ENABLE_PASSWORD_CHANGE");
export const ENABLE_PUBLIC_PAGES = boolEnv("VUE_APP_ENABLE_PUBLIC_PAGES");
export const ENABLE_PUBLIC_PAYMENT = boolEnv("VUE_APP_ENABLE_PUBLIC_PAYMENT");
export const ENABLE_SENTRY = boolEnv("VUE_APP_ENABLE_SENTRY");
export const ENABLE_SPONSORS = boolEnv("VUE_APP_ENABLE_SPONSORS");
export const ENABLE_UNSUBSCRIBE = boolEnv("VUE_APP_ENABLE_UNSUBSCRIBE");


export const APP_ONLY = boolEnv("VUE_APP_APP_ONLY");
export const DEBUG = boolEnv("VUE_APP_DEBUG");
export const WWW_HOST = process.env.VUE_APP_WWW_HOST;
export const LOGOUT_REDIRECT_URL = process.env.VUE_APP_LOGOUT_REDIRECT_URL;
export const API_HOST = process.env.VUE_APP_API_HOST;
export const BASE_URL = process.env.VUE_APP_BASE_URL;
export const FACEBOOK_APP_ID = process.env.VUE_APP_FACEBOOK_APP_ID;
export const SECURE_MODE = boolEnv("VUE_APP_SECURE_MODE");
export const FLY_MENU_URL = process.env.VUE_APP_FLY_MENU_URL;
export const FLY_MENU_KEY = process.env.VUE_APP_FLY_MENU_KEY;
export const APP_BRAND_NAME = process.env.VUE_APP_BRAND_NAME;
export const IMG_BRAND = process.env.VUE_APP_IMG_BRAND;