<template>
  <Dialog
    id="add-message-dialog"
    :open="showMessageEditor"
    :closeBtn="true"
    :onClose="onHideMessageEditor"
    focus-elt=".op-message-content-input"
  >
    <MessageEditor
      :onSend="onMessageSent"
      :onCancel="onMessageCancelled"
      v-if="discussion"
      :discussionId="discussion.id"
    />
  </Dialog>

  <div class="op-page op-discussion-content">
    <div class="op-page-title">
      <h1>{{ upperFirst(discussion?.title) }}</h1>
    </div>
    <div class="op-page-content">
      <BackButton class="fright" :forcedHref="{ name: 'DiscussionList' }">
        <FontAwesomeIcon :icon="['fas', 'chevron-left']" /> Retour
      </BackButton>

      <div class="op-vs-10" v-for="message in discussion?.messages || []" :key="message.id">
        <div
          class="col-11 col-sm-10 col-md-8 col-lg-7 op-vs"
          v-if="message"
          :class="{
            'op-dietician-message': isDieticianMessage(message),
            'op-user-message': !isDieticianMessage(message),
          }"
        >
          <div class="op-message-header">
            {{ message.authorName }} - le
            {{ DateTime.fromISO(message.date).setLocale("fr").toFormat("dd/MM/yyyy") }}
          </div>
          <div v-html="getHtmlContent(message.content)"></div>
        </div>
        <span class="clearfix" />
      </div>

      <div class="text-center op-vs" v-if="discussion">
        <h4 v-if="isClosed">
          Discussion terminée le
          {{ DateTime.fromISO(discussion.closeDate).setLocale("fr").toFormat("dd/MM/yyyy") }}
        </h4>
        <button type="button" class="btn btn-success" v-if="canSendMessage" @click="onAddMessage">
          <FontAwesomeIcon :icon="['fas', 'plus']" /> Nouveau message
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { upperFirst } from "lodash";
import Dialog from "@/components/interface/Dialog.vue";
import MessageEditor from "@/components/discussion/MessageEditor.vue";
import BackButton from "@/components/interface/BackButton.vue";
import { DateTime } from "luxon";
import API from "@/api.js";

export default {
  name: "DiscussionContent",
  props: [],
  data: () => ({
    discussion: null,
    showMessageEditor: false,
    DateTime,
  }),
  mounted() {
    this.reset();
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
    }),
    isClosed() {
      return !this.discussion || this.discussion.closeDate !== null;
    },
    canSendMessage() {
      if (this.isClosed) {
        return false;
      }
      return this.isOwner || this.isDietician;
    },
    isOwner() {
      return this.discussion && this.userId === this.discussion.owner;
    },
    isDietician() {
      return this.discussion && this.userId === this.discussion.dietician;
    },
  },
  methods: {
    upperFirst,
    async reset() {
      this.discussion = await API.discussion.get(this.$route.params.discussionId);
      this.updateReadStatus();
    },
    async updateReadStatus() {
      // Only a dietician or the discussion owner car mark a message as read
      if (this.userId !== this.discussion.owner && this.userId !== this.discussion.dietician) {
        // This user cannot change read status
        return;
      }
      const data = await API.discussion.read(this.discussion.id, {
        discussionId: this.discussion.id,
        userId: this.userId,
      });
      this.discussion.ownerReadDate = data.ownerReadDate;
      this.discussion.dieticianReadDate = data.dieticianReadDate;
    },
    isDieticianMessage(message) {
      return message.author != this.discussion.owner;
    },
    getHtmlContent(text) {
      let res = text.replace(/(?:\r\n|\r|\n)/g, "<br />");
      res = res.replace(/(<br \/>)+/g, "<br /><br />");
      return res;
    },
    onAddMessage() {
      this.showMessageEditor = true;
    },
    onMessageSent() {
      this.onHideMessageEditor();
      this.reset();
    },
    onMessageCancelled() {
      this.onHideMessageEditor();
    },
    onHideMessageEditor() {
      this.showMessageEditor = false;
    },
  },
  components: { Dialog, MessageEditor, BackButton },
};
</script>

<style scoped lang="scss">
.op-discussion-content {
  .op-message {
    border-radius: $op-radius-md;
    border: 1px solid $op-color-border;
    text-align: justify;
  }

  .op-user-message {
    @extend .op-message;

    float: left;
    border-color: $op-color-border;
    background-color: $op-color-grey-light;
  }

  .op-dietician-message {
    @extend .op-message;

    float: right;
    border-color: $op-color-lime;
    background-color: $op-color-green-light;
  }

  .op-message-header {
    font-style: italic;
    font-size: smaller;
    padding-bottom: 10px;
  }
}
</style>
