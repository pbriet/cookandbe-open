<template>
  <div class="tastes-editor">
    <div class="input-group input-group-sm dislike-add">
      <span class="input-group-text">
        <FontAwesomeIcon :icon="['far', 'thumbs-down']" />
      </span>
      <div class="dislike-searchbar form-control">
        <Select2
          ref="searchbar"
          placeholder="Entrez un aliment"
          :settings="{
            multiple: true, // Affiche un champ de recherche au lieu d'un combo
            query: querySearchFoodTag, // Requête de contenu en fonction de la recherche en cours
            minimumInputLength: 3, // Ne cherche pas avant d'avoir au moins 2 caractères
            templateSelection: formatFoodTag, // Formattage des éléments déjà sélectionnés (non utilisés)
            templateResult: formatFoodTag, // Formattage des éléments dans la liste déroulante
            width: '100%',
          }"
          :onSelecting="(event) => onSelectDislike(event)"
          :query="querySearchFoodTag"
          :disabled="addingTaste"
        />
      </div>
    </div>
    <!-- dislike-add -->
    <div class="alert alert-danger" v-if="tooManyDisliked">
      L'ensemble de vos goûts (tous membres du foyer confondus) vous empêche d'accéder à plus de 2 recettes sur 3.<br />
      Pour assurer votre équilibre, nous n'avons pas pu rajouter "{{ tooManyDisliked.name }}" dans la liste.
    </div>
    <ul v-if="profile" class="profile-tastes">
      <li v-for="taste in dislikes" :key="taste.id">
        {{ taste.foodTag.name }}
        <img src="@/assets/img/close_icon.gif" style="width: 16px; cursor: pointer" @click="onDeleteTaste(taste.id)" />
      </li>
      <li v-if="addingTaste">(ajout en cours...)</li>
    </ul>
  </div>
</template>

<script>
import $ from "jquery";
import { mapGetters } from "vuex";
import { partition, find } from "lodash";
import Select2 from "@/components/interface/Select2.vue";
import API from "@/api.js";

/*
 * Component for displaying the user objective
 */
export default {
  name: "ConfigTastesEditor",
  props: ["profileId"],
  data: () => ({
    profile: null,
    tooManyDisliked: false,
    addingTaste: false,
    likes: [],
    dislikes: [],
  }),
  mounted() {
    this.loadProfile(this.profiles);
  },
  computed: {
    ...mapGetters({ profiles: "profile/getProfiles" }),
  },
  watch: {
    profiles(newProfiles) {
      if (!this.profile && newProfiles) {
        this.loadProfile(newProfiles);
      }
    },
  },
  methods: {
    loadProfile(profiles) {
      if (!profiles) {
        return;
      }
      const profile = find(profiles, ["id", this.profileId]);
      if (!profile) {
        console.error("failure profile id !", this.profileId);
        return;
      }

      this.profile = profile;
      this.$store.dispatch("taste/get", this.profileId).then((tastes) => {
        [this.dislikes, this.likes] = partition(tastes, (taste) => taste.fondness < 0);
      });
      API.restrictedFoods(this.profileId).then((restrictions) => {
        this.restrictions = restrictions;
      });
      this.addingTaste = false;
    },
    formatFoodTag(tag) {
      return tag.name;
    },
    async querySearchFoodTag(params, cancelToken) {
      const data = await API.foodTagSearch(params.term, {}, { cancelToken });
      const results = [];
      // Suppression des foodtags déjà présents dans les likes/dislikes/restrictions
      for (const foodTag of data.foodTags) {
        if (!this.tagAlreadyUsed(foodTag.id)) {
          foodTag.text = foodTag.name;
          results.push(foodTag);
        }
      }
      return { results };
    },
    tagAlreadyUsed(foodTagId) {
      let index;
      for (index = 0; index < this.likes.length; ++index) {
        if (this.likes[index].foodTag.id == foodTagId) {
          return true;
        }
      }
      for (index = 0; index < this.dislikes.length; ++index) {
        if (this.dislikes[index].foodTag.id == foodTagId) {
          return true;
        }
      }
      for (index = 0; index < this.restrictions.length; ++index) {
        if (this.restrictions[index].foodTag.id == foodTagId) {
          return true;
        }
      }
      return false;
    },
    async onDeleteTaste(tasteId) {
      await this.$store.dispatch("taste/del", { profileId: this.profileId, tasteId });
      this.tooManyDisliked = false;
      this.likes = this.likes.filter((liked) => liked.id != tasteId);
      this.dislikes = this.dislikes.filter((disliked) => disliked.id != tasteId);
    },
    onSelectDislike(foodTag) {
      this.onAddTaste(this.profile, foodTag, -5);
      setTimeout(() => {
        const select2 = $(this.$refs.searchbar.$refs.select);
        select2.empty();
        select2.val([]);
      }, 100);
    },
    async onAddTaste(profile, foodTag, fondness) {
      this.tooManyDisliked = false;
      if (this.tagAlreadyUsed(foodTag.id)) {
        return;
      }
      this.addingTaste = true;
      const data = await this.$store.dispatch("taste/add", {
        profileId: profile.id,
        foodTag,
        fondness,
        setPlanningExpired: true,
      });
      this.addingTaste = false;

      if (data.status === "error") {
        console.error("Error while adding taste");
        return;
      }
      if (data.status === "too_many_disliked") {
        this.tooManyDisliked = foodTag;
        return;
      }
      // Remplacement de l'id du foodTag par l'objet
      if (fondness > 0) {
        this.likes.push(data);
      } else {
        this.dislikes.push(data);
      }
    },
  },
  components: { Select2 },
};
</script>

<style lang="scss">
.tastes-editor {
  display: block;

  .dislike-add {
    li.select2-search-choice {
      display: none;
    }
  }

  .dislike-add,
  .dislike-searchbar {
    height: 42px;
  }

  .profile-tastes {
    padding-left: 10px;
    padding-right: 10px;
    padding-top: 5px;
    padding-bottom: 5px;
    margin-top: 10px;
    border: solid 1px $op-color-border;
    list-style: none;
    height: 150px;
    overflow: auto; // Srollbar if needed
  }
}
</style>
