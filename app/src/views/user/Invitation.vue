<template>
  <div id="invitation-page" class="op-page-public">
    <div class="add-person-form invitation-panel card">
      <div class="card-body">
        <legend class="card-title"><FontAwesomeIcon :icon="['fas', 'globe-europe']" /> Invitation privée</legend>
        <br />
        <p class="mt-4">Pour valider votre invitation, merci de renseigner les informations suivantes.</p>
        <br />
        <div class="alert alert-danger fade show" v-show="errorMessage" id="error_message">
          <div class="error_message_title">{{ errorMessage?.title }}</div>
          {{ errorMessage?.content }}
        </div>
        <form class="form" role="form" id="signup-form" @submit.prevent.stop="validateInvite">
          Entrez votre prénom :<br />
          <input class="form-control" v-model="firstName" placeholder="Prénom" type="text" required autofocus />
          <br />
          Choisissez un mot de passe :<br />
          <input class="form-control" v-model="password" placeholder="Mot de passe" type="password" required />
          <div class="cgu op-vs">
            <div class="op-font-lg d-flex">
              <span><CheckBox :modelValue="cguAccepted" :onChange="toggleCgu" caption="J'ai lu et accepte les" /></span>
              <a class="cgu-link" href="" @click.prevent="showTerms">conditions générales</a>
            </div>
            <br />
            <div class="op-font-md">
              <CheckBox
                :modelValue="aminogramAccepted"
                :onChange="toggleAminogram"
                caption="J'accepte que des échanges de données entre Cook&Be et Aminogram (Biody Coach / Biody Xpert) puissent avoir lieu"
              />
            </div>
          </div>

          <br />
          <br />
          <button class="btn btn-lg btn-success btn-block" id="submit-btn" type="submit">
            {{ buttonLoading ? "Inscription en cours..." : "Valider" }}
          </button>
        </form>
      </div>
    </div>
  </div>
  <!-- invitation_page -->
</template>

<script>
import API from "@/api.js";
import CheckBox from "@/components/interface/CheckBox.vue";

export default {
  name: "Invitation",
  props: [],
  data: () => ({
    errorMessage: null,
    firstName: "",
    password: "",
    cguAccepted: false,
    aminogramAccepted: false,
    buttonLoading: false,
  }),
  computed: {
    inviteKey() {
      return this.$route.params.inviteKey;
    },
  },
  methods: {
    toggleCgu() {
      this.cguAccepted = !this.cguAccepted;
    },
    toggleAminogram() {
      this.aminogramAccepted = !this.aminogramAccepted;
    },
    showTerms() {
      this.$store.commit("dialog/showSignupTerms");
    },
    async validateInvite() {
      this.errorMessage = null;

      if (!this.cguAccepted) {
        this.errorMessage = { content: "Vous devez accepter les conditions pour créer un compte." };
        return;
      }

      if (!this.aminogramAccepted) {
        this.errorMessage = {
          content: "Vous devez accepter l'échange de données avec l'entreprise Aminogram afin de créer un compte.",
        };
        return;
      }

      this.buttonLoading = true;
      const data = await API.validateInvite({
        key: this.inviteKey,
        firstName: this.firstName,
        password: this.password,
      });

      if (data.status === "ok") {
        this.$store.commit("user/setLoggedIn", data.user);
        await this.$store.dispatch("services/init", true);
        if (data.dietKey) {
          this.$router.push({ name: "DietChoice", params: { diet: data.dietKey } });
        } else {
          this.$router.push({ name: "DietChoice" });
        }
      } else {
        this.errorMessage = { title: data.title, content: data.content };
        this.buttonLoading = false;
      }
    },
  },
  components: { CheckBox },
};
</script>

<style scoped lang="scss">
#invitation-page {
  .invitation-panel {
    width: 70%;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
    margin-top: 100px;
  }
}
</style>
