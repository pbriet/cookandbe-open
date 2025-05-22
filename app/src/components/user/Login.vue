<template>
  <h3 class="dialog-title">{{ title }}</h3>

  <div class="dialog-body">
    <div class="alert alert-danger" v-if="createAccountMsg || message">
      <div v-if="createAccountMsg">{{ createAccountMsg }}</div>
      <router-link v-if="createAccountMsg" :to="{ name: 'SignUp' }" class="btn btn-success op-font-lg">
        <span @click="hidePopup">
          <FontAwesomeIcon :icon="['fas', 'user']" /> Cliquez ici pour créer un nouveau compte
        </span>
      </router-link>
      {{ message }}
    </div>

    <ConnectSignup
      :onForgotPassword="onForgotPassword"
      :onManualConnect="onManualLogin"
      :onFbConnect="onFacebookLogin"
      :usermail="usermail"
      :onConnectionSuccess="onConnectionSuccess"
      v-if="status === 'authentication' && !createAccountMsg"
      ref="connectSignup"
    />

    <!-- Forgot password form -->
    <div v-if="status === 'forgot'">
      <PleaseWait v-if="passwordResetting" caption="Réinitialisation en cours" />
      <div class="row">
        <p class="col-12">
          <span class="op-icon-dmd op-vs">
            <FontAwesomeIcon :icon="['fas', 'envelope']" />
          </span>
          Entrez l'adresse utilisée pour créer votre compte
        </p>
      </div>
      <div class="row">
        <form class="form row" role="form" @submit.prevent="submitForgotPassword">
          <div class="form-group col-12 col-md-8">
            <input
              autofocus
              class="form-control"
              placeholder="Email"
              ref="forgotEmailInput"
              name="email"
              v-model="usermail"
              type="text"
            />
          </div>
          <div class="form-group col-12 col-sm-6 col-md-2">
            <button type="submit" class="btn btn-success btn-block">Envoyer</button>
          </div>
          <div class="form-group col-12 col-sm-6 col-md-2">
            <button type="button" class="btn btn-secondary btn-block" @click="resetLoginData">Retour</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Reset mail sent -->
    <div v-if="status === 'reset_mail'">
      <div class="row">
        <div class="col-sm-2 d-none d-sm-block op-vs text-center">
          <span class="op-icon-dxl">
            <FontAwesomeIcon :icon="['fas', 'inbox']" />
          </span>
        </div>
        <div class="col-12 col-sm-10">
          <p>Un email permettant de changer votre mot de passe a été envoyé à l'adresse :</p>
          <p class="text-center op-font-lg">
            <b>{{ usermail }}</b>
          </p>
          <p>
            La réception du message peut prendre quelques minutes. En cas d'attente prolongée, pensez à vérifier votre
            dossier de spams.
          </p>
          <p v-if="ENABLE_CONTACT">
            Si le problème persiste, n'hésitez pas à
            <a :href="WWW_HOST + '/contact'" @click="hidePopup">nous contacter</a>.
          </p>
          <p>L'équipe {{ APP_BRAND_NAME }}</p>
        </div>
      </div>
      <div class="row flex-row-reverse">
        <div class="col-6 col-sm-4 col-md-3">
          <a class="btn btn-success btn-block" @click="hidePopup">Fermer</a>
        </div>
        <div class="col-6 col-sm-4 col-md-3">
          <a class="btn btn-secondary btn-block" @click="resetLoginData">Retour</a>
        </div>
      </div>
    </div>

    <!-- Reset password form -->
    <div v-if="status === 'reset'">
      <PleaseWait v-if="passwordResetting" caption="Réinitialisation en cours" />
      <div class="alert alert-warning op-vs">
        Choisissez votre nouveau mot de passe puis tapez le à nouveau dans le champ de confirmation
      </div>
      <form class="form" role="form" @submit.prevent="submitResetPassword">
        <div class="row">
          <div class="form-group col-12 col-md-6 col-lg-4">
            <input
              class="form-control"
              ref="resetPasswordInput"
              placeholder="Nouveau mot de passe"
              v-model="password"
              type="password"
              name="password"
            /><br />

            <input
              class="form-control"
              id="reset-confirmation-input"
              placeholder="Confirmer le mot de passe"
              v-model="confirmation"
              type="password"
              name="password"
            />
          </div>
        </div>
        <div class="row op-vs col-12 px-0">
          <div class="w-100 d-flex flex-row-reverse">
            <button type="button" class="btn btn-secondary btn-block" @click="resetLoginData" style="margin-left: 15px">
              Annuler
            </button>
            <button type="submit" class="btn btn-success btn-block">Changer le mot de passe</button>
          </div>
        </div>
      </form>
    </div>

    <span class="clearfix" />
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { APP_BRAND_NAME, ENABLE_CONTACT, WWW_HOST } from "@/config.js";
import API from "@/api.js";
import { SERVER_DOWN_MESSAGE } from "@/common/static.js";
import PleaseWait from "@/components/interface/PleaseWait.vue";
import ConnectSignup from "@/components/user/ConnectSignup";

export default {
  name: "Login",
  props: ["resetCode", "email"],
  data: () => ({
    usermail: "",
    password: "",
    confirmation: "",
    code: "",
    status: "",
    title: "",
    message: "",
    createAccountMsg: "",
    passwordResetting: false,
    APP_BRAND_NAME,
    ENABLE_CONTACT,
    WWW_HOST,
  }),
  mounted() {
    if (this.resetCode) {
      this.changeLoginStatus("reset", "Changement de votre mot de passe", () => this.$refs.resetPasswordInput);
      this.code = this.resetCode;
      this.usermail = this.email;
    } else {
      this.resetLoginData();
    }
  },
  computed: {
    ...mapGetters({
      user: "user/get",
    }),
  },
  methods: {
    changeLoginStatus(status, title, focusElement) {
      this.password = "";
      this.confirmation = "";
      this.code = "";
      this.status = status;
      this.title = title;
      this.message = "";
      focusElement &&
        setTimeout(() => {
          const element = focusElement();
          element && element.focus();
        }, 100);
    },
    async onManualLogin(usermail, password) {
      const res = await this.$store.dispatch("user/login", {
        email: usermail.toLowerCase(),
        password: password,
      });
      this.resetLoginData();
      return res;
    },
    async onFacebookLogin() {
      const data = await this.$store.dispatch("user/loginFromFacebook");
      this.resetLoginData();

      this.createAccountMsg = "";
      if (data.shouldCreateAccount) {
        this.createAccountMsg = data.title;
      }
      return data;
    },
    hidePopup() {
      this.$store.commit("dialog/hideLoginPopup");
    },
    async onConnectionSuccess() {
      // Authentication successful
      await this.$store.dispatch("services/init", true);
      this.hidePopup();
    },
    /*
     * On FF and IE, autocomplete and autofill don't raise a "change" event
     * The ng-model is then not synchronized with the content (the input are filled,
     * but the ngModel is empty)
     * We fix that by retrieving manually with JQuery the field values
     */
    fixAutocompleteAngularBug() {
      this.usermail = this.$refs.forgotEmailInput.value;
    },
    resetLoginData() {
      this.changeLoginStatus(
        "authentication",
        "Connexion au compte utilisateur",
        () => this.$refs.connectSignup && this.$refs.connectSignup.$refs.loginEmailInput
      );
    },
    onForgotPassword() {
      this.usermail = this.$refs.connectSignup.$refs.loginEmailInput.value;
      this.changeLoginStatus("forgot", "Mot de passe oublié", () => this.$refs.forgotEmailInput);
    },
    // Call the API to ask for reset password code
    async submitForgotPassword() {
      this.passwordResetting = true;
      this.fixAutocompleteAngularBug();

      try {
        const data = await API.forgotPassword({ usermail: this.usermail });
        if (data.status === "error") {
          this.message = data.title;
        } else if (data.status === "ok") {
          this.changeLoginStatus("reset_mail", "Changement de votre mot de passe");
        }
      } catch {
        this.message = SERVER_DOWN_MESSAGE;
      }
      this.passwordResetting = false;
    },
    // Call the API to verify reset code
    async submitResetPassword() {
      if (this.password != this.confirmation) {
        this.message = "Les deux mots de passe ne correspondent pas";
        return;
      }
      this.passwordResetting = true;
      try {
        const data = await API.resetPassword({ usermail: this.usermail, code: this.code, password: this.password });
        if (data.status === "error") {
          this.message = data.title;
          this.passwordResetting = false;
        } else if (data.status === "ok") {
          this.passwordResetting = false;
          this.resetLoginData();
          this.$router.push({ name: "SignIn", params: { reason: "renewed" } });
        }
      } catch {
        this.message = SERVER_DOWN_MESSAGE;
        this.passwordResetting = false;
      }
    },
  },
  components: { ConnectSignup, PleaseWait },
};
</script>
