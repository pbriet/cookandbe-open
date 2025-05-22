<template>
  <div class="op-message-editor">
    <div v-if="!discussionId && quota.maxQuestions === 0">
      <h3 class="dialog-title">Envie de poser une question à notre nutritionniste ?</h3>
      <div class="dialog-body">
        <h4 class="op-font-green mt-2">Passez à l'abonnement premium aujourd'hui !</h4>
        <p class="mb-2">À partir de {{ premiumLowestTariff }}&euro;/mois, bénéficiez de:</p>
        <ul>
          <li>L'accès à <b>toutes les alimentations</b></li>
          <li>Jusqu'à <b>5 questions/mois</b> traitées par un nutritionniste professionnel</li>
          <li>Un suivi personnalisé par emails</li>
        </ul>
        <div class="row flex-row-reverse">
          <div class="col-6 col-sm-4">
            <div class="btn btn-secondary btn-block" @click="onCancelMessage">Fermer</div>
          </div>
          <div class="col-6 col-sm-4">
            <router-link class="btn btn-success btn-block" :to="{ name: 'PremiumChoice', query: { level: 1 } }">
              Voir plus de détails
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!discussionId && quota.maxQuestions > 0 && quota.questionCount >= quota.maxQuestions">
      <h3 class="dialog-title">Vous avez déjà posé vos {{ quota.maxQuestions }} questions ce mois-ci !</h3>
      <div class="dialog-body">
        <p class="op-vs">
          Mais pas de panique, votre quota sera remis à zéro à la fin du mois de
          {{ DateTime.fromFormat(quota.endDate, "yyyy-MM-dd").setLocale("fr").toFormat("MMMM") }}
        </p>
        <div class="btn btn-secondary fright" @click="onCancelMessage">Patienter</div>
      </div>
    </div>

    <PleaseWait
      :until="!sending"
      v-if="discussionId || (quota.maxQuestions > 0 && quota.questionCount < quota.maxQuestions)"
    >
      <h3 class="dialog-title" v-if="!discussionId">Votre question</h3>
      <h3 class="dialog-title" v-if="discussionId">Message</h3>

      <div class="dialog-body">
        <input
          class="form-control op-message-title-input"
          v-if="!discussionId && discussion"
          placeholder="Saisissez votre question"
          type="text"
          v-model="discussion.title"
          maxlength="150"
          size="150"
        />

        <h3 v-if="!discussionId">Dites-nous en plus <small class="op-font-grey">(facultatif)</small></h3>
        <textarea class="form-control op-message-content-input" v-if="message" v-model="message.content"></textarea>

        <div class="row op-vs flex-row-reverse">
          <div class="col-6 col-sm-4 col-md-3">
            <button type="button" class="btn btn-secondary btn-block" @click="onCancelMessage">Annuler</button>
          </div>
          <div class="col-6 col-sm-4 col-md-3">
            <button type="button" class="btn btn-success btn-block" @click="onSendMessage" :disabled="!canSendMessage">
              Envoyer
            </button>
          </div>
        </div>
        <span class="clearfix" />
      </div>
    </PleaseWait>
  </div>
</template>

<script>
import PleaseWait from "@/components/interface/PleaseWait.vue";
import { mapGetters } from "vuex";
import { DateTime } from "luxon";
import API from "@/api.js";

export default {
  name: "MessageEditor",
  props: ["messageId", "discussionId", "onSend", "onCancel"],
  data: () => ({
    sending: false,
    discussion: null,
    message: null,
    DateTime,
  }),
  mounted() {
    this.reset();
  },
  computed: {
    ...mapGetters({
      quota: "discussion/getQuota",
      userId: "user/id",
    }),
    premiumLowestTariff() {
      return this.$store.getters["diet/levelLowestTariff"](1);
    },
    canSendMessage() {
      if (this.discussionId) {
        if (!this.message?.content) {
          return false;
        }
      } else {
        if (!this.discussion?.title) {
          return false;
        }
      }
      return true;
    },
  },
  methods: {
    async reset() {
      if (this.discussionId) {
        this.discussion = await API.discussion.get(this.discussionId);
      } else {
        this.discussion = { title: "" };
      }
      if (this.messageId) {
        this.message = await API.message.get(this.messageId);
      } else {
        this.message = this.createMessage();
      }
    },
    createMessage() {
      return {
        author: this.userId,
        content: "",
        date: null,
        discussion: null,
      };
    },
    onSendMessage() {
      this.sending = true;
      this.message.date = new Date();
      if (this.discussionId) {
        this.message.discussion = this.discussionId;
        this.sendMessage();
      } else {
        this.createDiscussion(this.sendMessage);
      }
    },
    async sendMessage() {
      if (!this.message.content) {
        this.onMessageSent();
        return;
      }
      if (this.message.id) {
        await API.message.update(this.message.id, this.message);
      } else {
        await API.message.save(this.message);
      }
      this.onMessageSent();
    },
    onMessageSent() {
      this.onSend && this.onSend();
      this.reset();
      this.sending = false;
    },
    async createDiscussion(callback) {
      const discussion = {
        owner: this.userId,
        title: this.discussion.title,
        closed: false,
        dietician: null,
      };
      const data = await API.discussion.save(discussion);
      this.message.discussion = data.id;
      callback && callback();
      return discussion;
    },
    onCancelMessage() {
      this.onCancel && this.onCancel();
    },
  },
  components: { PleaseWait },
};
</script>

<style scoped lang="scss">
textarea {
  margin-top: 5px;
  width: 100%;
  height: 100px;
}
</style>
