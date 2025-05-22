<template>
  <div class="col-12 recipe-viewer-instructions ps-0">
    <ConditionalH2 :when="!printMode"><span>Mode de préparation :</span></ConditionalH2>
    <ul itemprop="recipeInstructions">
      <li v-if="instructions.length === 0">
        <span v-html="getHtmlDefaultInstruction" />
      </li>
      <li v-for="instruction in sortedInstructions" :key="instruction.id">
        <span v-html="getHtmlInstruction(instruction)" />
      </li>
    </ul>
  </div>
</template>

<script>
import { sortBy } from "lodash";
import { DEFAULT_RECIPE_INSTRUCTION } from "@/common/static.js";
import { textToHtml } from "@/common/string.js";
import ConditionalH2 from "@/components/interface/conditional_headers/ConditionalH2.vue";

export default {
  name: "Instructions",
  props: ["printMode", "instructions"],
  data: () => ({}),
  computed: {
    sortedInstructions() {
      return sortBy(this.instructions, (instruction) => instruction.id);
    },
    getHtmlDefaultInstruction() {
      return textToHtml(DEFAULT_RECIPE_INSTRUCTION);
    },
  },
  methods: {
    getHtmlInstruction(instruction) {
      return textToHtml(instruction.text);
    },
  },
  components: { ConditionalH2 },
};
</script>

<style scoped lang="scss">
.recipe-viewer-instructions {
  clear: both;
  font-size: 9pt;

  ul {
    list-style-type: decimal;
  }
}
</style>
