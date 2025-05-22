<template>
  <!-- Are you sure to disable your account ? -->
  <Dialog id="disable-account-modal" class="info in" :open="showDialog">
    <div class="dialog-title">Confirmer la désactivation</div>
    <div class="dialog-body">
      <h3>Pourquoi voulez-vous nous quitter ?</h3>
      <p>Dites-nous ce que vous pensez vraiment de {{ APP_BRAND_NAME }}, soyez sans pitié !</p>
      <textarea v-model="disabledInfos.whyLeavingUs"></textarea>
      <div class="alert alert-danger" v-if="disabledInfos.pleaseLeaveAMessage">
        Merci de nous laisser quelques mots avant de partir !
      </div>
      <button type="button" class="btn btn-danger me-1" @click="confirmDisableAccount">Désactiver</button>
      <button type="button" class="btn btn-secondary" @click="doNotDisableAccount">Annuler</button>
    </div>
  </Dialog>

  <div id="user-settings" class="op-page">
    <div class="op-page-title">
      <h1>Paramètres</h1>
    </div>
    <div class="op-page-content hp-lg">
      <h2>Informations utilisateur</h2>
      <div class="row">
        <div class="d-none d-sm-block col-sm-6 offset-sm-6" style="position: absolute">
          <div class="text-center op-font-grey-light op-vs">
            <span class="section-icon">
              <FontAwesomeIcon :icon="['fas', 'user']" />
            </span>
          </div>
        </div>
        <form class="form col-12 col-sm-6 op-vs" role="form" id="user-settings-form" @submit.prevent="saveSettings">
          <div class="row op-vs-5">
            <div class="col-3">Prénom</div>
            <div class="col-9">
              <input class="form-control" v-model="userData.firstName" placeholder="Prénom" type="text" required />
            </div>
          </div>
          <div class="row op-vs-5">
            <div class="col-3">Nom</div>
            <div class="col-9">
              <input class="form-control" v-model="userData.lastName" placeholder="Nom" type="text" required />
            </div>
          </div>
          <div class="row op-vs-5" v-if="settingsData.content && !haveSettingsChanged">
            <div class="col-12">
              <div
                class="alert"
                :class="{
                  'alert-danger': settingsData.status === 'error',
                  'alert-success': settingsData.status === 'ok',
                }"
              >
                {{ settingsData.content }}
              </div>
            </div>
          </div>
          <div class="row op-vs-20">
            <div class="col-6 offset-3">
              <button
                class="btn btn-success btn-block"
                id="save-settings-btn"
                type="submit"
                :disabled="!haveSettingsChanged"
              >
                Enregistrer
              </button>
            </div>
          </div>
        </form>
      </div>

      <div v-if="ENABLE_PASSWORD_CHANGE">
        <h2>Changement de mot de passe</h2>
        <div class="row">
          <div class="d-none d-sm-block col-sm-6 offset-sm-6" style="position: absolute">
            <div class="text-center op-font-grey-light op-vs">
              <span class="section-icon">
                <FontAwesomeIcon :icon="['fas', 'lock']" />
              </span>
            </div>
          </div>
          <form class="form col-12 col-sm-6 op-vs" role="form" id="ser-password-form" @submit.prevent="changePassword">
            <div class="row op-vs-5">
              <div class="col-3">Ancien</div>
              <div class="col-9">
                <input
                  class="form-control"
                  v-model="passwordData.oldPassword"
                  placeholder="Ancien mot de passe"
                  type="password"
                  required
                />
              </div>
            </div>
            <div class="row op-vs-5">
              <div class="col-3">Nouveau</div>
              <div class="col-9">
                <input
                  class="form-control"
                  v-model="passwordData.newPassword"
                  placeholder="Nouveau mot de passe"
                  type="password"
                  required
                />
              </div>
            </div>
            <div class="row op-vs-5" v-if="passwordData.content && !isPasswordChanging">
              <div class="col-12">
                <div
                  class="alert"
                  :class="{
                    'alert-danger': passwordData.status === 'error',
                    'alert-success': passwordData.status === 'ok',
                  }"
                >
                  {{ passwordData.content }}
                </div>
              </div>
            </div>
            <div class="row op-vs-20">
              <div class="col-6 offset-3">
                <button
                  class="btn btn-success btn-block"
                  id="change-password-btn"
                  type="submit"
                  :disabled="!isPasswordChangeReady"
                >
                  Changer
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>

      <h2 v-if="ENABLE_EMAILS">Gestion des emails</h2>
      <div class="row">
        <div class="d-none d-sm-block col-sm-6 offset-sm-6" style="position: absolute">
          <div class="text-center op-font-grey-light op-vs">
            <span class="section-icon">
              <FontAwesomeIcon :icon="['fas', 'envelope']" />
            </span>
          </div>
        </div>
        <div class="col-12 col-sm-6 op-vs" v-if="!emailOptionsData.enabled">
          <div class="row op-vs-5">
            <div class="col-12">
              <p>Votre compte est <b>désactivé</b>.</p>
              <p>Vous devez le réactiver pour pouvoir bénéficier du service.</p>
            </div>
          </div>
        </div>
        <div class="col-12 op-vs" v-if="emailOptionsData.enabled">
          <div class="row op-vs-5" v-if="ENABLE_NEWSLETTER">
            <div
              class="col-12 col-sm-3 col-md-2"
              :class="{ 'op-font-green': emailOptionsData.newsletter, 'op-font-red': !emailOptionsData.newsletter }"
            >
              <CheckBox v-model="emailOptionsData.newsletter" caption="Newsletter" />
            </div>
            <div class="col-12 col-sm-9 col-md-10">
              Recevez chaque semaine les recettes du moment, et les nouvelles fonctionnalités de
              {{ APP_BRAND_NAME }}
            </div>
          </div>
          <div class="row op-vs-5">
            <div
              class="col-12 col-sm-3 col-md-2"
              :class="{ 'op-font-green': emailOptionsData.suggestion, 'op-font-red': !emailOptionsData.suggestion }"
            >
              <CheckBox v-model="emailOptionsData.suggestion" caption="Suggestions de repas" />
            </div>
            <div class="col-12 col-sm-9 col-md-10">Recevez des idées repas 3 jours par semaine</div>
          </div>
          <div class="row op-vs-5">
            <div
              class="col-12 col-sm-3 col-md-2"
              :class="{ 'op-font-green': emailOptionsData.daily, 'op-font-red': !emailOptionsData.daily }"
            >
              <CheckBox v-model="emailOptionsData.daily" caption="Rappels quotidiens" />
            </div>
            <div class="col-12 col-sm-9 col-md-10">Recevez un rappel quotidien de vos plats planifiés</div>
          </div>
          <div class="row op-vs-5">
            <div
              class="col-12 col-sm-3 col-md-2"
              :class="{
                'op-font-green': emailOptionsData.notifications,
                'op-font-red': !emailOptionsData.notifications,
              }"
            >
              <CheckBox v-model="emailOptionsData.notifications" caption="Notifications" />
            </div>
            <div class="col-12 col-sm-9 col-md-10">Soyez alerté lorsque quelque chose se passe sur votre compte</div>
          </div>
          <div class="row op-vs-5" v-if="emailOptionsData.message && !haveMailOptionsChanged">
            <div class="col-12">
              <div class="alert alert-success">
                {{ emailOptionsData.message }}
              </div>
            </div>
          </div>
        </div>
        <div class="col-12 col-sm-6" v-if="emailOptionsData.enabled">
          <div class="row op-vs-20">
            <div class="col-6 offset-3">
              <button class="btn btn-success btn-block" @click="saveEmailOptions" :disabled="!haveMailOptionsChanged">
                Enregistrer
              </button>
            </div>
          </div>
        </div>
      </div>

      <h2 v-if="ENABLE_UNSUBSCRIBE">Désactivation du compte utilisateur</h2>
      <div class="row">
        <div class="d-none d-sm-block col-sm-6 offset-sm-6" style="position: absolute">
          <div class="text-center op-font-grey-light op-vs">
            <span class="section-icon">
              <FontAwesomeIcon :icon="['fas', 'power-off']" />
            </span>
          </div>
        </div>
        <div class="col-12 op-vs">
          <div class="row op-vs-5">
            <div class="col-12" v-if="emailOptionsData.enabled">
              <p>En désactivant votre compte, vous ne recevrez plus d'emails de notre part.</p>
              <p>Pour le réactiver, vous devrez revenir dans les paramètres et cliquez sur "Réactiver".</p>
            </div>
            <div class="col-12" v-if="!emailOptionsData.enabled">
              <p>Votre compte est <b>désactivé</b>. Vous ne recevez plus aucun emails.</p>
              <p>Cliquez sur "réactiver" pour restaurer le service.</p>
            </div>
          </div>
        </div>
        <div class="col-12 col-sm-6">
          <div class="row op-vs-20">
            <div class="col-6 offset-3">
              <button class="btn btn-success btn-block" @click="reenableAccount" v-if="!emailOptionsData.enabled">
                Réactiver
              </button>
              <button class="btn btn-danger btn-block" @click="disableAccount" v-if="emailOptionsData.enabled">
                Désactiver
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- op-page-content -->
  </div>
  <!-- user-settings -->
</template>

<script>
import { mapGetters } from "vuex";
import { APP_BRAND_NAME, ENABLE_EMAILS, ENABLE_PASSWORD_CHANGE, ENABLE_UNSUBSCRIBE, ENABLE_NEWSLETTER } from "@/config.js";
import API from "@/api.js";
import Dialog from "@/components/interface/Dialog.vue";
import CheckBox from "@/components/interface/CheckBox.vue";

/*
 * View for settings page
 */
export default {
  name: "Settings",
  props: [],
  data() {
    return {
      APP_BRAND_NAME,
      ENABLE_EMAILS,
      ENABLE_NEWSLETTER,
      ENABLE_PASSWORD_CHANGE,
      ENABLE_UNSUBSCRIBE,
      showDialog: false,
      userData: {
        firstName: "",
        lastName: "",
      },
      disabledInfos: {
        pleaseLeaveAMessage: false,
        whyLeavingUs: "",
      },
      passwordData: {
        oldPassword: "",
        newPassword: "",
        status: null,
      },
      settingsData: {
        content: "",
        status: null,
      },
      emailOptionsData: {
        enabled: false,
        newsletter: true,
        suggestion: true,
        daily: true,
        notifications: true,
        message: "",
      },
      emailOptions: {
        enabled: false,
        newsletter: true,
        suggestion: true,
        daily: true,
        notifications: true,
        message: "",
      },
    };
  },
  mounted() {
    this.init();
  },
  computed: {
    ...mapGetters({
      user: "user/get",
    }),
    haveSettingsChanged() {
      return this.user.firstName != this.userData.firstName || this.user.lastName != this.userData.lastName;
    },
    isPasswordChanging() {
      return (
        (this.passwordData.oldPassword && this.passwordData.oldPassword.length > 0) ||
        (this.passwordData.newPassword && this.passwordData.newPassword.length > 0)
      );
    },
    isPasswordChangeReady() {
      return (
        this.passwordData.oldPassword &&
        this.passwordData.oldPassword.length > 0 &&
        this.passwordData.newPassword &&
        this.passwordData.newPassword.length > 0
      );
    },
    haveMailOptionsChanged() {
      return (
        this.emailOptionsData &&
        (this.emailOptionsData.daily != this.emailOptions.daily ||
          this.emailOptionsData.suggestion != this.emailOptions.suggestion ||
          this.emailOptionsData.newsletter != this.emailOptions.newsletter ||
          this.emailOptionsData.notifications != this.emailOptions.notifications)
      );
    },
  },
  watch: {
    haveSettingsChanged(newValue) {
      if (newValue) {
        this.settingsData.content = "";
      }
    },
    isPasswordChanging(newValue) {
      if (newValue) {
        this.passwordData.content = "";
      }
    },
    haveMailOptionsChanged(newValue) {
      if (newValue) {
        this.emailOptionsData.message = "";
      }
    },
  },
  methods: {
    /*
     * Initializes the signup form values
     */
    init() {
      this.userData = { firstName: this.user.firstName, lastName: this.user.lastName };
      this.disabledInfos = {
        pleaseLeaveAMessage: false,
        whyLeavingUs: "",
      };
      this.passwordData = { oldPassword: "", newPassword: "", status: null };
      this.settingsData = { content: "", status: null };
      API.user.emailOptions(this.user.id).then((data) => {
        this.emailOptions = data;
        this.emailOptionsData = { ...data };
      });
    },
    confirmDisableAccount() {
      this.disabledInfos.pleaseLeaveAMessage = false;
      if (!this.disabledInfos.whyLeavingUs) {
        this.disabledInfos.pleaseLeaveAMessage = true;
        return;
      }
      const args = {
        enabled: false,
        whyLeavingUs: this.disabledInfos.whyLeavingUs,
      };
      API.user.setEmailOptions(this.user.id, args).then(this.init);
      this.showDialog = false;
    },
    disableAccount() {
      this.showDialog = true;
    },
    doNotDisableAccount() {
      this.showDialog = false;
    },
    reenableAccount() {
      API.user.setEmailOptions(this.user.id, { enabled: true }).then(this.init);
    },
    async saveSettings() {
      this.$store.commit("user/setUserFullname", this.userData);
      this.settingsData = await API.user.changeSettings(this.user.id, this.userData);
    },
    async changePassword() {
      this.passwordData = await API.user.changePassword(this.user.id, this.passwordData);
    },
    async saveEmailOptions() {
      if (
        !this.emailOptionsData.newsletter &&
        !this.emailOptionsData.daily &&
        !this.emailOptionsData.suggestion &&
        !this.emailOptionsData.notifications
      ) {
        return this.disableAccount();
      }
      await API.user.setEmailOptions(this.user.id, this.emailOptionsData);
      this.emailOptionsData.message = "Vos informations ont été mises à jour";
      this.emailOptions = { ...this.emailOptions, ...this.emailOptionsData };
    },
  },
  components: { CheckBox, Dialog },
};
</script>

<style scoped lang="scss">
#disable-account-modal {
  textarea {
    display: block;
    width: 100%;
    height: 100px;
    margin-bottom: 20px;
    margin-top: 10px;
  }
  h4 {
    margin-top: 30px;
  }
}

#user-settings {
  h2 {
    @extend .op-title-underlined;
  }
}

.section-icon {
  font-size: 100px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}
</style>
