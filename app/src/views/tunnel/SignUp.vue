<template>
  <div id="signup-page" :class="isLoggedIn ? 'op-page' : 'op-page-public'">
    <div class="op-page-title container">
      <h1>Inscription</h1>
    </div>
    <div class="op-page-content container">
      <div id="op-signup-form" class="col-12">
        <div class="manual-signup">
          <h2 class="d-flex align-items-center">
            <span class="signup_logo">
              <FontAwesomeIcon :icon="['fas', 'globe-europe']" />
            </span>
            Inscription gratuite
          </h2>

          <ConnectSignup
            :signupMode="true"
            :onManualConnect="onManualSignup"
            :onConnectionSuccess="onSignupSuccess"
            :onFbConnect="onFacebookSignup"
            :autofocusSignupEmailInput="true"
          />

          <!-- Layout -->
          <div style="clear: both"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import ConnectSignup from "@/components/user/ConnectSignup";

/*
 * Controller for signup page
 */
export default {
  name: "Signup",
  props: [],
  computed: {
    ...mapGetters({
      isLoggedIn: "user/isLoggedIn",
    }),
  },
  methods: {
    ...mapActions({
      sendEvent: "analytics/sendEvent",
    }),
    gotoDietChoice() {
      if (this.$route.params.diet) {
        // There is a diet pre-selected
        this.$router.push({ name: "DietChoice", params: { diet: this.$route.params.diet } });
      } else {
        // No diet pre-selected
        this.$router.push({ name: "DietChoice" });
      }
    },
    async onSignupSuccess() {
      this.sendEvent({ category: "flow", action: "success", label: "signup" });
      // Authentication successful
      await this.$store.dispatch("services/init", true);
      this.gotoDietChoice();
    },
    async onManualSignup(email, password, firstName) {
      this.sendEvent({ category: "flow", action: "click", label: "manual_signup" });
      return await this.$store.dispatch("user/createAccount", {
        email: email.toLowerCase(),
        firstName: firstName,
        password: password,
      });
    },
    async onFacebookSignup() {
      this.sendEvent({ category: "flow", action: "click", label: "facebook_signup" });
      return await this.$store.dispatch("user/createAccountFromFacebook");
    },
  },
  components: {
    ConnectSignup,
  },
};
</script>

<style scoped lang="scss">
#signup-page {
  .signup-panel {
    width: 700px;
    margin-left: auto;
    margin-right: auto;
    margin-top: 100px;

    #manual-signup {
      form {
        display: inline-block;
        width: 100%;
        margin-top: 20px;
        margin-bottom: 10px;
      }
      #signup_logo {
        color: $op-color-button;
      }
      #signup_btn {
        padding: 0px;
      }
    }
  }
}

.op-signup-btn-xl {
  @extend .op-font-xxl;
  border-radius: $op-radius-lg;
  padding: 10px 25px;
  margin: 10px;
}

#op-signup-form {
  .manual-signup {
    form {
      display: inline-block;
      width: 100%;
      margin-bottom: 10px;
    }
    .signup_logo {
      display: flex;
      align-items: center;
      margin-right: 10px;
    }
    .signup_btn {
      padding: 0px;
    }
    .special-offer {
      color: $op-color-green;
    }
  }
  .diet-profile-fields {
    margin-top: 20px;
    padding-left: 20px;
    font-size: $op-font-lg;
    text-align: left;
    td {
      margin-top: 2px;
    }
  }
  .starnote {
    font-size: $op-font-sm;
    color: $op-color-red;
  }
}
</style>
