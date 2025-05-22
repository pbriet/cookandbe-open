<template>
  <div class="op-page">
    <div class="op-page-title">
      <h1>Vos goûts</h1>
    </div>
    <ConfigProgression />
    <div class="op-page-content">
      <div id="tastes-page">
        <div class="op-info">
          <span class="info-icon">
            <FontAwesomeIcon :icon="['far', 'thumbs-down']" />
          </span>
          <div class="info-text">
            <p>Précisez les aliments que vous ne souhaitez pas voir apparaître dans votre planning de repas.</p>
            <p>Ne mangez que ce que vous aimez !</p>
          </div>
        </div>

        <div class="profile-row row mx-1">
          <div v-for="profile in profiles" :key="profile.id" class="col-md-4">
            <div class="user-details" v-if="profiles.length > 1">
              <ProfileLogo :sex="profile.sex" :noColor="true" />
              <span class="user-name">{{ profile.nickname }}</span>
            </div>
            <ConfigTastesEditor v-if="profileTastesLoaded" :profileId="profile.id" />
          </div>
        </div>
        <!-- profile-row -->
      </div>
    </div>
    <!-- tastes-content -->
    <ConfigToolbar />
  </div>
  <!-- tastes-page -->
</template>

<script>
import { mapGetters } from "vuex";
import ConfigProgression from "@/components/config/ConfigProgression.vue";
import ConfigToolbar from "@/components/config/ConfigToolbar.vue";
import ProfileLogo from "@/components/interface/ProfileLogo.vue";
import ConfigTastesEditor from "@/components/config/ConfigTastesEditor.vue";

export default {
  name: "TastesConfig",
  props: [],
  data: () => ({}),
  computed: {
    ...mapGetters({
      profiles: "profile/getProfiles",
      profileTastesLoaded: "taste/getProfileTastesLoaded",
    }),
  },
  methods: {
    save() {
      this.$store.dispatch("configStage/complete", { stageName: "tastes" });
    },
  },
  beforeRouteLeave(to, from, next) {
    this.save();
    next();
  },
  components: { ConfigToolbar, ConfigProgression, ProfileLogo, ConfigTastesEditor },
};
</script>

<style lang="scss">
#tastes-page {
  .profile-row {
    margin-top: 15px;
    margin-bottom: 15px;

    .user-details {
      margin-bottom: 20px;

      .profile-icon {
        line-height: $op-font-dlg;
        font-size: $op-font-dlg;
        display: inline-block;
        vertical-align: bottom;
      }

      .user-name {
        font-size: $op-font-lg;
        font-weight: bold;
        margin-left: 5px;
        display: inline-block;
        vertical-align: bottom;
      }
    }
  }
}
</style>
