<template>
  <div id="food-search-page">
    <div id="food-search-bar" class="input-group">
      <span class="input-group-text">
        <slot></slot>
      </span>
      <input
        v-model="keyword"
        @input="() => searchFood()"
        class="form-control"
        type="text"
        placeholder="Entrez un nom d'ingrédient"
        style="height: 35px"
      />
      <button @click="onResetSearch" class="btn btn-secondary food-search-clear-button">
        <FontAwesomeIcon :icon="['fas', 'trash']" />
      </button>
    </div>

    <div class="col-md-12 food-search-results" v-show="keyword && keyword.length">
      <a href="" v-if="foodTypeSelected" @click.prevent="() => searchFood()"> &lt; toutes catégories </a>
      <ul>
        <li v-for="typeDetails in foodSearchResults.types" :key="typeDetails.type.id">
          <a href="" @click.prevent="filterSearch(typeDetails.type.id)">
            >> {{ typeDetails.type.name }}
            <span style="font-weight: bold">({{ typeDetails.nbFood }}) </span>
          </a>
        </li>
      </ul>
      <ul>
        <li class="food-search-item" v-for="food in foodSearchResults.foods" :key="food.id" @click="clickFood(food)">
          {{ food.name }}
        </li>
      </ul>
      <div>{{ searchErrorStatus }}</div>
    </div>
  </div>
</template>

<script>
import API from "@/api.js";

/*
 * This component adds a text input for a keyword
 * It generates an Ajax search in the food database
 *
 * It takes in input two arguments : the image to display side-by-side with each food entry
 *                                   the function to call when the image is clicked (food_id is given as argument)
 */
export default {
  name: "FoodSearch",
  props: ["defaultKeyword", "disabledOnly", "showDisabled", "clearOnClick", "onClickFood"],
  data() {
    return {
      foodSearchResults: [],
      foodTypeSelected: false, // Has the user selected a food type in his search?
      searchErrorStatus: "",
      keyword: this.defaultKeyword,
    };
  },
  mounted() {
    if (this.keyword) {
      this.searchFood();
    }
  },
  computed: {},
  methods: {
    /*
     * Search for some foods given a keyword
     */
    searchFood(typeId) {
      if (!this.keyword || this.keyword.length === 0) {
        // No keyword submitted
        this.foodTypeSelected = false;
        this.foodSearchResults = [];
        this.searchErrorStatus = "";
        return;
      }

      let requestParams = {};
      if (typeId === undefined) {
        // No filter on food type
        this.foodTypeSelected = false;
      } else {
        // Filtering on a given food type
        requestParams.type_id = typeId;
        this.foodTypeSelected = true;
      }
      requestParams.disabled_only = false;
      if (this.disabledOnly == "1") {
        requestParams.disabled_only = true;
      }
      requestParams.show_disabled = false;
      if (this.showDisabled) {
        requestParams.show_disabled = true;
      }
      // Calls the API to search foods given a keyword
      API.foodSearch(this.keyword, requestParams)
        .then((data) => {
          this.foodSearchResults = data;
          if (data.count > data.foods.length) {
            this.searchErrorStatus = "...";
          } else if (data.empty) {
            this.searchErrorStatus = "Aucun aliment ne correspond à ce mot-clé";
          } else {
            // All good
            this.searchErrorStatus = "";
          }
        })
        .catch(() => {
          this.searchErrorStatus = "Erreur";
        });
    },
    /*
     * Filter food search with a specific food type
     */
    filterSearch(typeId) {
      this.searchFood(typeId);
    },
    /*
     * When clicking on a food
     */
    clickFood(food) {
      this.onClickFood(food);
      if (this.clearOnClick !== false) {
        this.onResetSearch();
      } else {
        for (let i = 0; i < this.foodSearchResults.foods.length; ++i) {
          if (this.foodSearchResults.foods[i].id == food.id) {
            this.foodSearchResults.foods.splice(i, 1);
          }
        }
      }
    },
    onResetSearch() {
      this.foodSearchResults = [];
      this.keyword = "";
    },
  },
  components: {},
};
</script>

<style scoped lang="scss">
#food-search-page {
  #food-search-bar {
    // Stick the results to the search bar
    margin-bottom: 0px;
  }

  .food-search-results {
    position: absolute;
    z-index: 10;
    max-height: 300px;
    width: 90%;
    overflow: scroll;
    overflow-x: hidden;
    overflow-y: auto;

    margin-bottom: 20px;
    background-color: white;
    border: 1px solid #ddd;
    box-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);

    .food-search-item:hover {
      background-color: #3875d7;
      color: #fff;
      cursor: pointer;
    }

    ul {
      list-style-type: none;
      padding-left: 0px;

      a {
        cursor: pointer;
        text-decoration: underline;
      }
    }
  }
}
</style>
