<template>
  <div :class="{ 'op-page-public': configMode, 'op-page': !configMode }">
    <div class="op-page-title" :class="{ container: configMode }">
      <h1>Vos caractéristiques</h1>
    </div>
    <ConfigProgression />
    <div class="op-page-content" :class="{ container: configMode }">
      <div id="user-profile-config">
        <div class="op-info">
          <span class="info-icon">
            <FontAwesomeIcon :icon="['fas', 'user']" />
          </span>
          <div class="info-text">
            <p>
              Les plannings de repas proposés par {{ APP_BRAND_NAME }} vous apportent la juste quantité de calories,
              vitamines et minéraux.
            </p>
            <p>Ces apports sont calculés à partir de votre taille, poids et activité sportive.</p>
          </div>
        </div>

        <ProfileEditor :title="profile?.nickname" v-if="profile" v-model="profile" :mustBeComplete="true" />
      </div>
    </div>
    <ConfigToolbar />
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { APP_BRAND_NAME } from "@/config.js";
import ConfigProgression from "@/components/config/ConfigProgression.vue";
import ConfigToolbar from "@/components/config/ConfigToolbar.vue";
import ProfileEditor from "@/components/config/ProfileEditor.vue";
import API from "@/api.js";

/*
 * View for displaying the main user profiler
 */
export default {
  name: "UserProfileConfig",
  props: [],
  data: () => ({
    APP_BRAND_NAME,
    profile: null,
  }),
  mounted() {
    this.profile = this.profileFromStore;
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
      profileFromStore: "profile/getMainProfile",
      configMode: "configStage/configMode",
    }),
  },
  watch: {
    profileFromStore(newProfile) {
      if (!this.profile) {
        this.profile = newProfile;
      }
    },
  },
  methods: {
    save() {
      if (!this.profile.nickname) {
        this.profile.nickname = "Anonyme";
      }
      if (this.profile.height < 30) {
        this.profile.height = null;
      } else {
        this.profile.height = Math.round(this.profile.height);
      }
      API.profile.update(this.userId, this.profile.id, this.profile).then(() => {
        this.$store.dispatch("profile/update");
        this.$store.dispatch("configStage/complete", { stageName: "user_profile" });
      });
    },
  },
  beforeRouteLeave(to, from, next) {
    this.save();
    next();
  },
  components: {
    ConfigProgression,
    ConfigToolbar,
    ProfileEditor,
  },
};
</script>

<style scoped lang="scss"></style>
