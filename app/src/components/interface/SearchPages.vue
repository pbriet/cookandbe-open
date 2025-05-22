<template>
  <div class="op-search-pages-panel">
    <ul class="pagination op-search-pages-list" v-show="pages.length > 1">
      <li :class="{ disabled: index < 1 }" class="page-item">
        <a class="page-link" v-if="!pageBaseUrl" href="" @click.prevent="onPreviousPage">&laquo;</a>
        <router-link class="page-link" v-if="pageBaseUrl && index >= 1" :to="`${pageBaseUrl}/${index - 1}`"
          >&laquo;</router-link
        >
      </li>
      <li
        class="op-search-pages-item page-item"
        v-for="page in pages"
        :key="page.index"
        :class="{ active: page.index == index }"
      >
        <router-link class="page-link" v-if="pageBaseUrl" :to="`${pageBaseUrl}/{page.index}`">
          {{ page.index + 1 }}
        </router-link>
        <a class="page-link" v-if="!pageBaseUrl" href="" @click.prevent="changePage(page)">
          {{ page.index + 1 }}
        </a>
      </li>
      <li :class="{ disabled: index >= pages.length - 1 }" class="page-item">
        <a class="page-link" v-if="!pageBaseUrl" href="" @click.prevent="onNextPage">&raquo;</a>
        <router-link
          class="page-link"
          v-if="pageBaseUrl && index < pages.length - 1"
          :to="`${pageBaseUrl}/${index + 1}`"
          >&raquo;</router-link
        >
      </li>
    </ul>
  </div>
</template>

<script>
/*
 * Displays all page numbers in a row
 */
export default {
  name: "SearchPages",
  props: [
    "offset",
    "count",
    "resultsPerPage",
    "pageBaseUrl", // href will contain pageBaseUrl/<page_nb>
    "onChangePage", // if pageBaseUrl is not defined, calling this function
  ],
  data: () => ({
    index: 0,
    pages: [],
  }),
  mounted() {
    this.updatePagesFromCount(this.count);
  },
  watch: {
    offset(newOffset) {
      this.updateIndexFromOffset(newOffset);
    },
    count(newCount) {
      this.updatePagesFromCount(newCount);
    },
  },
  computed: {},
  methods: {
    updateIndexFromOffset(offset) {
      if (!offset) {
        offset = 0;
      }
      for (let i = 0; i < this.pages.length; ++i) {
        const page = this.pages[i];

        if (offset >= page.offset && offset <= page.offset + parseInt(this.resultsPerPage)) {
          this.index = i;
        }
      }
    },
    updatePagesFromCount(count) {
      const pages = [];
      for (let i = 0; i * this.resultsPerPage < count; ++i) {
        pages.push({ offset: i * this.resultsPerPage, index: i });
      }
      this.pages = pages;
      this.updateIndexFromOffset(this.offset);
    },
    onPreviousPage() {
      if (this.index > 0) {
        this.changePage(this.pages[this.index - 1]);
      }
    },
    onNextPage() {
      if (this.index < this.pages.length - 1) {
        this.changePage(this.pages[this.index + 1]);
      }
    },
    changePage(page) {
      this.index = page.index;
      this.onChangePage(page);
    },
  },
  components: {},
};
</script>

<style scoped lang="scss">
.op-search-pages-panel {
  display: flex;
  justify-content: center;
  width: 100%;

  .op-search-pages-list {
    margin-top: 1rem;
    .selected {
      font-weight: bold;
    }
  }
}
</style>
