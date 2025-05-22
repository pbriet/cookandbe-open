<template>
  <div id="connect-signup">
    <!-- Connection in progress -->
    <PleaseWait v-if="connecting" caption="Authentification en cours" />

    <!-- Login/Signup form -->
    <div v-show="!connecting">
      <div class="alert alert-danger" v-if="error.title">
        <div style="font-weight: bold">{{ error.title }}</div>
        <div>{{ error.details }}</div>
      </div>

      <div v-show="signupMode">
        <div class="row signup-choices w-100">
          <div class="col-12 col-md-6 signup-mode">
            <form class="form" role="form" @submit.prevent="submitManual">
              <div class="form-group signup-input-group col-12">
                <div class="input-group">
                  <span class="input-group-text">
                    <FontAwesomeIcon :icon="['fas', 'at']" fixed-width />
                  </span>
                  <!-- Do not set autofocus dynamically: it breaks the scroll -->
                  <input
                    class="form-control"
                    placeholder="Email"
                    ref="signupEmailInput"
                    id="signup-email-input"
                    name="email"
                    v-model="connectionData.usermail"
                    type="text"
                    autocomplete="on"
                    required
                  />
                </div>
              </div>
              <div class="form-group signup-input-group col-12">
                <div class="input-group">
                  <span class="input-group-text">
                    <FontAwesomeIcon :icon="['fas', 'user']" fixed-width />
                  </span>
                  <input
                    class="form-control"
                    v-model="connectionData.firstName"
                    id="signup-name-input"
                    placeholder="Pseudo"
                    name="name"
                    type="text"
                    autocomplete="on"
                    required
                  />
                </div>
              </div>
              <div class="form-group signup-input-group col-12">
                <div class="input-group">
                  <span class="input-group-text">
                    <FontAwesomeIcon :icon="['fas', 'lock']" fixed-width />
                  </span>
                  <input
                    class="form-control"
                    placeholder="Mot de passe"
                    ref="signupPasswordInput"
                    id="signup-password-input"
                    name="password"
                    v-model="connectionData.password"
                    autocomplete="on"
                    type="password"
                    required
                  />
                </div>
              </div>

              <div class="col-12 op-font-lg cgu op-vs">
                <CheckBox :checked="cguAcceptedEmail" :onChange="toggleCguEmail" caption="J'ai lu et accepte les" />
                <a class="cgu-link" href="" @click.prevent="showTerms">conditions générales</a>
              </div>

              <div class="form-group">
                <div class="col-12">
                  <button type="submit" class="btn btn-success btn-block op-vs-10">S'inscrire</button>
                </div>
              </div>

              <div class="col-12 op-font-lg cgu op-vs text-end">
                <a class="" href="" @click.prevent="showLogin">Vous êtes déjà inscrit ?</a>
              </div>
            </form>
          </div>
          <!-- col-md-5 -->
        </div>
        <!-- row -->
      </div>
      <!-- signup-mode -->

      <div v-show="!signupMode">
        <div class="row connect-choices">
          <div class="col-12 connect-mode">
            <div class="col-12 op-font-lg connect-caption op-vs-10">Entrez votre email / mot de passe</div>

            <form class="form row" role="form" @submit.prevent="submitManual">
              <div class="form-group col signup-input-group col-12 col-md-5">
                <!-- Do not set autofocus dynamically: it breaks the scroll -->
                <div class="input-group">
                  <span class="input-group-text">
                    <FontAwesomeIcon :icon="['fas', 'at']" fixed-width />
                  </span>
                  <input
                    class="form-control"
                    placeholder="Email"
                    ref="loginEmailInput"
                    id="login-email-input"
                    name="email"
                    v-model="connectionData.usermail"
                    type="text"
                    autocomplete="on"
                  />
                </div>
              </div>
              <div class="form-group col signup-input-group col-12 col-md-5">
                <div class="input-group">
                  <span class="input-group-text">
                    <FontAwesomeIcon :icon="['fas', 'lock']" fixed-width />
                  </span>
                  <input
                    class="form-control"
                    placeholder="Mot de passe"
                    ref="loginPasswordInput"
                    id="login-password-input"
                    name="password"
                    v-model="connectionData.password"
                    autocomplete="on"
                    type="password"
                  />
                </div>
                <div id="login-password-reset">
                  <a @click.prevent="onForgotPassword" href="">Mot de passe oublié ?</a>
                </div>
              </div>

              <div class="form-group col">
                <div class="col-12 col-md-2">
                  <button type="submit" class="connect-btn btn btn-success">Connexion</button>
                </div>
              </div>
            </form>
          </div>
          <!-- col-md-6 -->
        </div>
        <!-- row -->
      </div>
      <!-- connect-mode -->
    </div>
  </div>
</template>

<script>
import { ENABLE_FACEBOOK } from "@/config.js";
import PleaseWait from "@/components/interface/PleaseWait.vue";
import CheckBox from "@/components/interface/CheckBox.vue";

export default {
  name: "ConnectSignup",
  props: [
    "signupMode",
    "onForgotPassword",
    "onManualConnect",
    "onFbConnect",
    "onConnectionSuccess",
    "autofocusSignupEmailInput",
  ],
  data: () => ({
    cguAcceptedEmail: false,
    cguAcceptedFb: false,
    connectionData: {
      usermail: "",
      password: "",
      firstName: "",
    },
    connecting: false,
    error: {},
  }),
  mounted() {
    if (this.autofocusSignupEmailInput) {
      this.$refs.signupEmailInput.focus();
    }
  },
  computed: {
    isFacebookEnabled() {
      return !this.$store.getters["user/isFacebookDisabled"] && ENABLE_FACEBOOK;
    },
  },
  methods: {
    reset() {
      this.connecting = false;
      this.error = {};
    },
    toggleCguEmail() {
      this.cguAcceptedEmail = !this.cguAcceptedEmail;
    },
    toggleCguFb() {
      this.cguAcceptedFb = !this.cguAcceptedFb;
    },
    showTerms() {
      this.$store.commit("dialog/showSignupTerms");
    },
    showLogin() {
      this.$store.commit("dialog/showLoginPopup");
      setTimeout(() => {
        this.$refs.loginEmailInput.focus();
      }, 500);
    },
    /*
     * Check that the CGU have been accepted. Show popup otherwise
     */
    checkCgu(cguAccepted) {
      if (!this.signupMode || cguAccepted) {
        return true;
      }
      this.error = {
        title: "Vous devez accepter les conditions",
        details: "Merci de lire les conditions et de cocher la case",
      };
      return false;
    },
    /*
     * Manually submitting user/password
     */
    async submitManual() {
      if (!this.checkCgu(this.cguAcceptedEmail)) {
        return;
      }
      this.fixAutocompleteAngularBug();
      // Copying because content might be reinitialized through onStartConnection -> v-If -> v-Model
      const usermail = this.connectionData.usermail;
      const password = this.connectionData.password;
      const firstName = this.connectionData.firstName;

      this.onStartConnection();
      const res = await this.onManualConnect(usermail, password, firstName);
      this.handleConnectionResult(res);
    },
    /*
     * Connect using facebook
     */
    facebookConnect() {
      if (!this.checkCgu(this.cguAcceptedFb)) {
        return;
      }
      this.onStartConnection();
      // Frontend-only : ask user for authorization using the facebook SDK
      window.FB.login(
        async (response) => {
          if (response.status === "connected") {
            // User has accepted to share his data, go go go
            const res = await this.onFbConnect();
            this.handleConnectionResult(res);
          } else {
            // User refused to share his data
            this.error = {
              title: "Connexion Facebook échouée",
              details: "Vous n'avez pas autorisé l'accès à votre compte",
            };
            this.onEndConnection();
          }
        },
        { scope: "public_profile,email" }
      ); // Asking for public infos and email
    },
    /*
     * From the server response, do the right thing :
     * - if login/signup was successful, initialize the app and redirect to userhome
     * - otherwise, display error messages
     */
    handleConnectionResult(result) {
      if (result.connected) {
        this.onConnectionSuccess().then(this.reset);
      } else {
        // Failure
        this.error.title = "Connexion impossible";
        if (result.data.details) {
          this.error.details = result.data.details;
        }
        this.onEndConnection();
      }
    },

    onStartConnection() {
      // Clean error messages
      this.error = {};
      // Activate the please-wait
      this.connecting = true;
    },

    onEndConnection() {
      // Stop the please-wait;
      this.connecting = false;
    },

    /*
     * On FF and IE, autocomplete and autofill don't raise a "change" event
     * The ng-model is then not synchronized with the content (the input are filled,
     * but the ngModel is empty)
     * We fix that by retrieving manually with JQuery the field values
     */
    fixAutocompleteAngularBug() {
      if (this.signupMode) {
        this.connectionData.usermail = this.$refs.signupEmailInput.value;
        this.connectionData.password = this.$refs.signupPasswordInput.value;
      } else {
        this.connectionData.usermail = this.$refs.loginEmailInput.value;
        this.connectionData.password = this.$refs.loginPasswordInput.value;
      }
    },
  },
  components: { PleaseWait, CheckBox },
};
</script>

<style scoped lang="scss">
#connect-signup {
  display: block;
  text-align: center;

  #login-password-reset {
    margin-left: 33px;
    a {
      text-align: left;
      padding: 10px;
      display: table-cell;
    }
  }

  .signup-input-group {
    display: table;
    border-collapse: separate;
  }

  .signup-mode form {
    margin-top: 20px;
    margin-bottom: 10px;
  }

  @media (min-width: $bootstrap-md-min) {
    .signup-choices {
      display: table;
      .signup-mode {
        float: none;
        display: table-cell;
        vertical-align: top;
      }
    }
    .fb-empty {
      height: 115px;
    }
    .signup-separator {
      & > div {
        display: table;
      }
      & > div > div {
        display: table-row;
      }
      & > div > div > div {
        display: table-cell;
      }

      .signup-separator-line {
        width: 1px;
        margin: auto;
        height: 150px;
        border-left: 1px solid $op-color-grey-dark;
      }

      .signup-separator-text {
        padding: 5px;
      }
    }
  }

  @media (max-width: $bootstrap-sm-max) {
    .signup-separator {
      & > div {
        display: table;
        width: 100%;
        table-layout: fixed;
        text-align: center;
      }
      & > div > div {
        display: table-cell;
      }
      & > div > div:first-child {
        width: 45%;
      }
      & > div > div:last-child {
        width: 45%;
      }

      .signup-separator-line {
        height: 1px;
        margin: auto;
        width: 100%;
        border-top: 1px solid $op-color-grey-dark;
        padding-bottom: 3px;
      }

      .signup-separator-text {
        padding: 5px;
      }
    }
  }

  #facebook-connect {
    clear: both;
    text-align: center;

    h4 {
      display: inline;
      margin-right: 20px;
      vertical-align: middle;
    }
    .facebook-connect-btn {
      height: 40px;
      border-radius: 4px;
      font-family: Helvetica, Arial;
      font-size: 16px;
      background-color: #3b579d;
      color: white;
      border: none;
      max-width: 400px;

      svg {
        width: 24px;
        height: 24px;
      }

      td:nth-of-type(1) {
        padding: 8px;
      }

      td:nth-of-type(2) {
        padding-left: 17px;
        padding: 8px;
        padding-right: 17px;
        p {
          margin-bottom: 8px;
        }
      }
    }
  }
}

.cgu {
  text-align: left;

  @media (max-width: $bootstrap-xxs-max) {
    .cgu-link {
      padding-left: 30px;
      padding-top: 10px;
      display: inline-block;
    }
  }
}
</style>

<style lang="scss">
#connect-signup {
  .cgu {
    .op-checkbox {
      float: left;
      width: auto;
      .op-checkbox-caption {
        width: auto;
      }
    }
  }
}
</style>
