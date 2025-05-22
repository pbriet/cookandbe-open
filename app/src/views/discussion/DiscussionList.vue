<template>
  <Dialog
    id="new-message-dialog"
    :open="showMessageEditor"
    :closeBtn="true"
    :onClose="onHideMessageEditor"
    focusElt=".op-message-title-input"
  >
    <MessageEditor :onSend="onMessageSent" :onCancel="onHideMessageEditor" />
  </Dialog>

  <div id="op-discussion-list" class="op-page">
    <div class="op-page-title">
      <h1>Mes questions</h1>
    </div>
    <div class="op-page-content">
      <!-- Thierry -->
      <div class="op-vs-5">
        <div class="info-block">
          <span class="fleft info-icon">
            <img src="@/assets/img/team/thierry-circle-transparent.png" width="90" />
          </span>
          <h4 class="mt-2">Posez une question à Thierry !</h4>
          <p>
            Thierry est notre nutritionniste adoré.<br />
            Avec son expérience passée en hôpital et en cabinet libéral, il saura trouver la réponse à vos problèmes.
          </p>
          <span class="clearfix" />
        </div>
      </div>

      <!-- Infos -->
      <div class="row op-vs" v-if="quota.maxQuestions > 0">
        <div class="col-12 col-sm-6 op-vs-5">
          <div class="info-block">
            <div class="op-icon-dlg info-icon">{{ quota.maxQuestions }}</div>
            <div>
              questions par mois à notre nutritionniste
              <br class="d-none d-sm-inline" />
              grâce à votre <b>abonnement premium</b>
            </div>
          </div>
        </div>
        <div class="col-12 col-sm-6 op-vs-5">
          <div class="info-block">
            <div class="op-icon-dlg info-icon">{{ quota.questionCount }}</div>
            <div>
              <span v-if="quota.questionCount < 2">question posée</span>
              <span v-if="quota.questionCount > 1">questions posées</span>
              <br class="d-none d-sm-inline" />
              au mois de
              <b>
                {{ DateTime.fromFormat(quota.startDate, "yyyy-MM-dd").setLocale("fr").toFormat("MMMM") }}
              </b>
            </div>
          </div>
        </div>
        <span class="clearfix" />
      </div>

      <div class="section">
        <div class="fright col-12 col-sm-4 col-md-3 op-vs-15" v-if="!displayInfosPanel">
          <div class="btn btn-success fright btn-block" @click="onNewQuestion">
            <FontAwesomeIcon :icon="['fas', 'plus']" /> Nouvelle question
          </div>
        </div>

        <h2>Mes questions</h2>
      </div>

      <div class="alert alert-success text-center" v-if="messageSent">
        <h3><FontAwesomeIcon :icon="['fas', 'info-circle']" /> Votre message a bien été envoyé</h3>
        Un email vous sera envoyé dès qu'un de nos diététiciens vous aura répondu.
      </div>

      <div class="op-vs" v-if="displayInfosPanel">
        <div class="op-info text-center">
          <h3><FontAwesomeIcon :icon="['fas', 'info-circle']" /> Vous n'avez pas encore posé de question !</h3>
          <p>
            Avec l'abonnement <b>premium</b>, posez jusqu'à 5 questions/mois à notre nutritionniste.
            <br />
            Tous les messages que vous envoyez sont confidentiels.
          </p>
          <div class="op-vs">
            <div class="btn btn-success" @click="onNewQuestion">
              <FontAwesomeIcon :icon="['fas', 'plus']" />
              Poser ma première question
            </div>
          </div>
        </div>
      </div>

      <table class="op-table discussions-table">
        <tr
          v-for="discussion in discussions"
          :key="discussion.id"
          :class="getDiscussionClass(discussion)"
          @click="onSelectDiscussion(discussion)"
        >
          <td>
            {{ DateTime.fromISO(discussion.creationDate).toFormat("dd/MM/yyyy") }}
          </td>
          <td class="col-8">({{ discussion.nbMessages }}) &nbsp; {{ upperFirst(discussion.title) }}</td>
          <td class="d-none d-sm-table-cell">
            <span v-if="getNbUnread(discussion) > 0">{{ discussion.nbUnread }}</span>
            <span v-if="getNbUnread(discussion) === 1"> nouveau message</span>
            <span v-if="getNbUnread(discussion) > 1"> nouveaux messages</span>
          </td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script>
import { upperFirst } from "lodash";
import { mapGetters } from "vuex";
import Dialog from "@/components/interface/Dialog.vue";
import MessageEditor from "@/components/discussion/MessageEditor.vue";
import { DateTime } from "luxon";

export default {
  name: "DiscussionList",
  props: [],
  data: () => ({
    messageSent: false,
    showMessageEditor: false,
    DateTime,
  }),
  mounted() {
    this.reset();
  },
  computed: {
    ...mapGetters({
      quota: "discussion/getQuota",
      discussions: "discussion/getDiscussions",
    }),
    displayInfosPanel() {
      return this.discussions.length === 0;
    },
  },
  methods: {
    reset() {
      this.$store.dispatch("discussion/update");
    },
    onSelectDiscussion(discussion) {
      this.$router.push({ name: "DiscussionContent", params: { discussionId: discussion.id } });
    },
    onNewQuestion() {
      this.showMessageEditor = true;
    },
    onMessageSent() {
      this.onHideMessageEditor();
      this.messageSent = true;
      this.reset();
    },
    onHideMessageEditor() {
      this.showMessageEditor = false;
    },
    getNbUnread(discussion) {
      if (discussion.ownerReadDate === null || discussion.lastDate > discussion.ownerReadDate) {
        return discussion.nbUnread;
      }
      return 0;
    },
    getDiscussionClass(discussion) {
      if (this.getNbUnread(discussion) > 0) {
        return "unread-discussion";
      }
      return "";
    },
    upperFirst,
  },
  components: { Dialog, MessageEditor },
};
</script>

<style lang="scss">
#op-discussion-list {
  .discussions-table {
    @include op-table-focus(white, $op-color-grey-dark);
    td {
      padding: 15px;
    }
    p {
      margin: 0px;
    }
  }

  .unread-discussion {
    font-weight: bold;
  }

  .section {
    padding-top: 40px;
    padding-bottom: 10px;

    h2 {
      border-bottom: 1px solid $op-color-border;
      padding-bottom: 5px;
    }
  }

  .info-block {
    padding: 15px;
    width: 100%;
    background-color: $op-color-grey-light;

    .info-icon {
      padding-left: 15px;
      padding-right: 15px;

      @media (max-width: $bootstrap-xxs-max) {
        display: block;
        width: 100%;
        text-align: center;
        margin-top: 5px;
        margin-bottom: 5px;
      }
      @media (min-width: $bootstrap-xs-min) {
        display: inline-block;
      }
    }
    & > div {
      display: inline-block;
    }
  }
}
</style>
