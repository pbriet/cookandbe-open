<template>
  <div class="col-md-12 op-profile-editor">
    <legend v-show="getTitle || modelValue.isMainProfile">
      {{ getTitle }}
      <span style="float: right" v-if="modelValue.isMainProfile">
        <FontAwesomeIcon :icon="['fas', 'star']" />
        Profil principal
      </span>
      <div style="clear: both"></div>
    </legend>

    <div class="profile-editor-content">
      <div class="alert alert-danger fade show" v-if="errorMessage" id="error_message">
        <div class="error_message_title">{{ errorMessage.title }}</div>
        {{ errorMessage.content }}
      </div>
      <div class="alert alert-danger" v-if="isTooYoung">
        Les enfants de moins de 2 ans ne peuvent être inclus dans le cadre d'une alimentation familiale.
      </div>

      <!-- All fields -->
      <form class="form" name="profile_editor_form" ref="profileEditorForm" role="form">
        <div class="profile-editor-table">
          <!-- Pseudonyme -->
          <div class="profile-editor-row">
            <div class="d-none d-sm-block col-sm-4">Nom</div>
            <div class="col-12 col-sm-8">
              <input
                class="form-control"
                :value="modelValue.nickname"
                @input="$emit('update:modelValue', { ...modelValue, nickname: $event.target.value })"
                placeholder="Nom"
                type="text"
                :class="{ 'op-invalid-input': !modelValue.nickname }"
                required
                autofocus
              />
            </div>
          </div>

          <!-- Birthdate -->
          <div class="profile-editor-row">
            <div class="col-12 col-sm-4">Date de naissance</div>
            <div class="col-12 col-sm-8">
              <DatePicker
                :modelValue="modelValue.birthDate"
                @update:modelValue="$emit('update:modelValue', { ...modelValue, birthDate: $event })"
                :showInvalidFields="true"
                form="profile-editor-form"
                :required="true"
              />
            </div>
          </div>

          <!-- Sex -->
          <div class="profile-editor-row">
            <div class="d-none d-sm-block col-sm-4">Sexe</div>
            <div class="col-12 col-sm-8">
              <Radio
                :required="true"
                :modelValue="modelValue.sex"
                @update:modelValue="$emit('update:modelValue', { ...modelValue, sex: $event })"
                value="female"
                caption="Femme"
                group="sex"
              />
              <Radio
                :required="true"
                :modelValue="modelValue.sex"
                @update:modelValue="$emit('update:modelValue', { ...modelValue, sex: $event })"
                value="male"
                caption="Homme"
                group="sex"
              />
            </div>
          </div>

          <!-- Size -->
          <div class="profile-editor-row">
            <div class="col-12 col-sm-4">Taille (cm)</div>
            <div class="col-12 col-sm-8">
              <SmartIntInput
                :modelValue="modelValue.height"
                @update:modelValue="$emit('update:modelValue', { ...modelValue, height: $event })"
                :min="10"
                :max="300"
                placeholder="Taille (cm)"
                :required="mustBeComplete"
              />
            </div>
          </div>

          <!-- Weight -->
          <div class="profile-editor-row">
            <div class="col-12 col-sm-4">Poids (kg)</div>
            <div class="col-12 col-sm-8">
              <SmartFloatInput
                :modelValue="modelValue.weight"
                @update:modelValue="$emit('update:modelValue', { ...modelValue, weight: $event })"
                :min="1"
                :max="500"
                placeholder="Poids (kg)"
                :required="mustBeComplete"
              />
            </div>
          </div>

          <!-- Sport -->
          <ProfileNapField
            :modelValue="modelValue.workScore"
            @update:modelValue="$emit('update:modelValue', { ...modelValue, workScore: $event })"
            caption="Activité en journée"
            :mustBeComplete="mustBeComplete"
            :options="WORK_SCORE_OPTIONS"
          />
          <ProfileNapField
            :modelValue="modelValue.movingScore"
            @update:modelValue="$emit('update:modelValue', { ...modelValue, movingScore: $event })"
            caption="Déplacements (marche, vélo)"
            :mustBeComplete="mustBeComplete"
            :options="MOVING_SCORE_OPTIONS"
          />
          <ProfileNapField
            :modelValue="modelValue.sportScore"
            @update:modelValue="$emit('update:modelValue', { ...modelValue, sportScore: $event })"
            caption="Activité sportive"
            :mustBeComplete="mustBeComplete"
            :options="SPORT_SCORE_OPTIONS"
          />

          <div class="profile-editor-toolbar" v-if="btnCaption">
            <button
              class="btn btn-success profile-editor-action me-1"
              :disabled="!profileEditorIsValid"
              :class="{ disabled: operation }"
              @click.prevent="save"
            >
              {{ operation == "saving" ? "En cours..." : btnCaption }}
            </button>
            <div
              type="button"
              class="btn btn-secondary profile-editor-action me-1"
              :class="{ disabled: operation }"
              v-if="onCancel && !modelValue.id"
              @click="onCancel"
            >
              Annuler
            </div>
            <button
              type="button"
              @click="remove"
              class="btn btn-danger profile-editor-action"
              :class="{ disabled: operation }"
              v-if="!modelValue.isMainProfile && modelValue.id"
            >
              <span class="action-icon me-1">
                <FontAwesomeIcon :icon="['fas', 'times']" />
              </span>
              <span class="action-desc">Supprimer ce profil</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { nYearsAgo } from "@/common/dates.js";
import SmartIntInput from "@/components/interface/smart_inputs/SmartIntInput.vue";
import SmartFloatInput from "@/components/interface/smart_inputs/SmartFloatInput.vue";
import DatePicker from "@/components/interface/DatePicker.vue";
import Radio from "@/components/interface/Radio.vue";
import ProfileNapField from "@/components/config/ProfileNapField.vue";
import API from "@/api.js";

/*
 * This component creates a profile editor (form)
 */
export default {
  name: "ProfileEditor",
  props: ["modelValue", "title", "defaultTitle", "mustBeComplete", "btnCaption", "onSave", "onCancel", "onDelete"],
  data: () => ({
    errorMessage: null,
    operation: null,
    nbDislikes: 0,
    WORK_SCORE_OPTIONS: [
      { value: 0, caption: "Plutôt assis" },
      { value: 1, caption: "Plutôt debout" },
      { value: 5, caption: "Plutôt debout avec activité physique importante" },
    ],
    MOVING_SCORE_OPTIONS: [
      { value: 0, caption: "15 min par jour ou moins" },
      { value: 1, caption: "15 à 30 min par jour" },
      { value: 2, caption: "Plus de 30 min par jour" },
    ],
    SPORT_SCORE_OPTIONS: [
      { value: 0, caption: "Moins de 30 min par semaine" },
      { value: 1, caption: "1 heure par semaine" },
      { value: 2, caption: "2 heures par semaine" },
      { value: 3, caption: "3 heures par semaine" },
      { value: 6, caption: "Plus de 3 heures par semaine" },
    ],
  }),
  computed: {
    ...mapGetters({
      userId: "user/id",
    }),
    getTitle() {
      if (this.title) {
        return this.title;
      } else if (this.modelValue && this.modelValue.nickname) {
        return this.modelValue.nickname;
      } else if (this.defaultTitle) {
        return this.defaultTitle;
      } else {
        return "";
      }
    },
    isTooYoung() {
      return this.modelValue.birthDate && new Date(this.modelValue.birthDate) > nYearsAgo(2);
    },
    profileEditorIsValid() {
      return (
        this.modelValue.nickname &&
        this.modelValue.sex &&
        this.modelValue.birthDate &&
        !this.isTooYoung &&
        (!this.mustBeComplete ||
          (this.modelValue.height &&
            this.modelValue.weight &&
            this.modelValue.workScore &&
            this.modelValue.sportScore &&
            this.modelValue.movingScore))
      );
    },
  },
  methods: {
    nYearsAgo,
    /*
     * Ensure that the profile is valid before submitting it to the server
     */
    checkValidity() {
      if (this.modelValue.height < 30) {
        this.errorMessage = {
          title: "Taille trop faible",
          content: "Veuillez indiquer votre taille en centimètres (1.65m = 165cm)",
        };
        return false;
      }
      return true;
    },
    async save() {
      if (!this.checkValidity()) {
        return;
      }
      this.operation = "saving";
      const payload = { ...this.modelValue, height: Math.round(this.modelValue.height) };
      if (this.modelValue.id) {
        await API.profile.update(this.userId, this.modelValue.id, payload);
      } else {
        await API.profile.save(this.userId, payload);
      }

      this.operation = null;
      this.$store.dispatch("profile/update");
      this.onSave && this.onSave();
    },
    async remove() {
      this.operation = "deleting";
      if (!window.confirm(`Etes-vous sûr de vouloir supprimer "${this.modelValue.nickname}" ?`)) {
        return;
      }
      // Removing profile server-side
      await API.profile.remove(this.userId, this.modelValue.id);
      this.operation = null;
      this.$store.dispatch("profile/update");
      this.onDelete && this.onDelete();
    },
  },
  components: { SmartIntInput, SmartFloatInput, DatePicker, Radio, ProfileNapField },
};
</script>

<style lang="scss">
.op-profile-editor {
  clear: both;

  .profile-editor-table {
    display: table;
    max-width: 700px;
    width: 100%;
    margin: auto;

    .profile-editor-row {
      display: table-row;
      line-height: 30px;

      & > div {
        float: left;
      }
    }

    .radio-group {
      margin-bottom: 10px;

      input {
        margin: 10px;
      }
    }
  }

  .form-control {
    transition: none; //  For an extremely weird/unknown reason, the bootstrap default transition
    //  generates a crash on IE11. Be careful if you uncomment this !
    margin-bottom: 10px;
  }

  #error_message {
    margin-top: 30px;
    .error_message_title {
      font-weight: bold;
    }
  }

  .profile-editor-content {
    width: 100%;
    margin-top: 20px;
  }

  .collapsable {
    display: inline-block;
    overflow: hidden;
    height: 0;
    visibility: hidden;
  }

  .collapsable.showMe {
    height: 100%;
    visibility: visible;
  }

  .profile-editor-toolbar {
    text-align: center;
    padding: 10px;

    .profile-editor-action {
      margin: auto;
      display: inline-block;
      width: 175px;
    }
  }

  .profile-editor-options {
    text-align: center;
    font-size: $op-font-lg;

    button {
      .action-icon {
        text-align: center;
        font-size: $op-font-xxl;
        line-height: $op-font-xxl;
      }
      .action-desc {
        text-align: center;
        font-size: $op-font-lg;
      }
    }

    .hero-widget {
      .icon {
        font-size: $op-font-dxl;
        line-height: $op-font-dxl;
      }
      var {
        font-size: $op-font-xxl;
        line-height: $op-font-xxl;
        height: $op-font-xxl;
      }
      label {
        height: $op-font-xxl;
      }
      .options {
        font-size: $op-font-lg;
      }
    }
  }
}
</style>
