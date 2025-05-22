<template>
  <div class="op-page">
    <div class="op-page-title">
      <h1>Votre foyer</h1>
    </div>
    <ConfigProgression />
    <div class="op-page-content">
      <div id="family-page">
        <div class="op-info">
          <span class="info-icon">
            <FontAwesomeIcon :icon="['fas', 'users']" />
          </span>
          <p>
            Renseignez quelles sont les personnes de votre foyer, et vous pourrez les rajouter aux repas afin d'adapter
            les quantités.
          </p>
        </div>

        <ul class="family-profile-list">
          <li class="family-profile col-md-4 col-sm-6 col-12" v-for="profile in profiles || []" :key="profile.id">
            <button
              class="btn btn-secondary btn-lg"
              role="button"
              @click="changeProfile(profile)"
              :class="{ active: isCurrentProfile(profile) }"
            >
              <!-- details -->
              <table>
                <tr>
                  <td>
                    <!-- avatar -->
                    <div class="family-profile-logo">
                      <ProfileLogo :sex="profile.sex" />
                    </div>
                  </td>
                  <td>
                    <div>
                      <FontAwesomeIcon v-if="profile.isMainProfile" :icon="['fas', 'star']" />
                      {{ profile.nickname }}
                      <small v-show="profile.birthDate">{{ ageFromBirth(profile.birthDate) }} ans</small>
                    </div>
                    <!-- tags -->
                    <div class="family-profile-tags">
                      <span class="badge bg-danger me-1" v-if="!profile.height">Taille inconnue</span>
                      <span class="badge bg-secondary me-1" v-if="profile.height">{{ profile.height }}cm</span>
                      <span class="badge bg-danger" v-if="!profile.weight">Poids inconnu</span>
                      <span class="badge bg-secondary" v-if="profile.weight">{{ profile.weight }}kg</span>
                    </div>
                  </td>
                  <td></td>
                </tr>
              </table>
            </button>
          </li>
          <li class="family-profile align-top">
            <button
              class="btn btn-secondary btn-lg"
              role="button"
              @click="changeProfile(newProfile)"
              :class="{ active: isCurrentProfile(newProfile) }"
            >
              <span class="family-add-profile">
                <FontAwesomeIcon :icon="['fas', 'plus']" />
              </span>
              Ajouter
            </button>
          </li>
        </ul>

        <div class="ratio-pie-chart" v-if="!currentProfile && profiles?.length > 1">
          <h3><FontAwesomeIcon :icon="['fas', 'utensils']" /> Qui mange quoi ?</h3>
          <RatioPieChart width="250px" />
        </div>

        <div class="family-profile-editor">
          <ProfileEditor
            :title="currentProfile.nickname"
            defaultTitle="Nouveau profil"
            btnCaption="Enregistrer"
            v-model="currentProfile"
            v-if="currentProfile && currentProfile.creator"
            :onSave="onSaveProfile"
            :onCancel="onCancelProfile"
            :onDelete="onDeleteProfile"
          />
        </div>
      </div>
      <ConfigMealSharing v-if="profiles" ref="mealSharing" :profiles="profiles" />
    </div>
    <!-- family content -->
    <ConfigToolbar />
  </div>
  <!-- family page -->
</template>

<script>
import { mapGetters } from "vuex";
import { ageFromBirth } from "@/common/dates.js";
import ConfigToolbar from "@/components/config/ConfigToolbar.vue";
import ConfigProgression from "@/components/config/ConfigProgression.vue";
import ProfileEditor from "@/components/config/ProfileEditor.vue";
import ConfigMealSharing from "@/components/config/ConfigMealSharing.vue";
import RatioPieChart from "@/components/user/RatioPieChart.vue";
import ProfileLogo from "@/components/interface/ProfileLogo.vue";

export default {
  name: "FamilyConfig",
  props: [],
  data: () => ({
    currentProfile: null,
    newProfile: null,
  }),
  mounted() {
    this.resetNewProfile();
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
      profiles: "profile/getProfiles",
    }),
    isProfileCreationInProgress() {
      return this.currentProfile && !this.currentProfile.id;
    },
  },
  methods: {
    ageFromBirth,
    resetCurrentProfile() {
      this.currentProfile = null;
    },
    changeProfile(profile) {
      if (this.isProfileCreationInProgress && !profile.id) {
        this.resetCurrentProfile();
        return;
      }
      this.currentProfile = profile;
    },
    isCurrentProfile(profile) {
      return this.currentProfile && this.currentProfile.id == profile.id;
    },
    resetNewProfile() {
      this.newProfile = { creator: this.userId };
    },
    onCancelProfile() {
      this.resetCurrentProfile();
    },
    onDeleteProfile() {
      this.resetCurrentProfile();
    },
    onSaveProfile() {
      this.resetCurrentProfile();
      this.resetNewProfile();
    },
    save() {
      if (!this.isProfileCreationOk()) {
        return false;
      }
      this.$store.dispatch("configStage/complete", { stageName: "family" });
      this.$store.dispatch("profile/update");
      return true;
    },
    isProfileCreationOk() {
      if (this.isProfileCreationInProgress) {
        let label = "nouveau profil";
        if (this.newProfile.nickname) {
          label = "profil de " + this.newProfile.nickname;
        }
        if (
          !window.confirm("Vous n'avez pas enregistré le " + label + ". Voulez-vous abandonner les modifications ?")
        ) {
          return false;
        }
      }
      return true;
    },
  },
  beforeRouteLeave(to, from, next) {
    this.$refs.mealSharing?.save();
    if (this.save()) {
      next();
    }
  },
  components: { ConfigToolbar, ConfigProgression, ProfileEditor, RatioPieChart, ProfileLogo, ConfigMealSharing },
};
</script>

<style lang="scss">
#family-page {
  .family-profile-list {
    padding: 0px;
  }

  .family-profile {
    display: inline-block;
    padding: 10px;

    & > button {
      width: 100%;
    }

    table {
      display: table-cell;
      width: 100%;
      text-align: left;
      white-space: initial;
    }

    .family-profile-logo {
      margin-right: 10px;
      margin-top: 10px;
    }

    small {
      color: $op-color-text-soft;
    }
  }

  .profile-icon {
    float: left;
    margin-bottom: 10px;
    text-align: center;
  }

  .family-profile-tags {
    float: left;

    span {
      font-size: $op-font-sm;
      font-weight: normal;
    }
  }

  .family-add-profile {
    font-size: $op-font-xxl;
  }

  .family-profile-editor {
    margin-top: 20px;
  }

  .ratio-pie-chart {
    clear: both;
    text-align: left;
    padding: 10px;
    op-ratio-pie-chart {
      display: inline-block;
    }
  }
}
</style>
