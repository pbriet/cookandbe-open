<template>
  <div v-if="level == 0">
    <div class="row">
      <div class="col-12 col-md-4">
        <img src="@/assets/img/home/planning.png" />
      </div>
      <div class="col-12 col-md-8 premium-details">
        <b>Planificateur de repas</b>
        <p>Idées repas personnalisées</p>
      </div>
    </div>
    <div class="row">
      <div class="col-12 col-md-4">
        <img src="@/assets/img/home/shopping_list.png" />
      </div>
      <div class="col-12 col-md-8 premium-details">
        <b>Liste de courses en 1 clic</b>
        <p>Sur smartphone ou à imprimer</p>
      </div>
    </div>
  </div>
  <div v-if="level == 1">
    <div class="row">
      <div class="col-12 col-md-4">
        <img src="@/assets/img/home/planning-and-list.png" />
      </div>
      <div class="col-12 col-md-8 premium-details">
        <b>Planificateur et liste de courses</b>
        <p>Des menus sur mesure quel que soit votre profil</p>
      </div>
    </div>
    <div class="row">
      <div class="col-12 col-md-4">
        <img src="@/assets/img/team/thierry-circle.jpg" />
      </div>
      <div class="col-12 col-md-8 premium-details">
        <b>Nutritionniste en ligne</b>
        <p>A votre disposition pour répondre à vos questions</p>
      </div>
    </div>
  </div>
  <div v-if="level == 2">
    <div class="row">
      <div class="col-12 col-md-4">
        <img src="@/assets/img/home/planning-and-list.png" />
      </div>
      <div class="col-12 col-md-8 premium-details">
        <b>Planificateur et liste de courses</b>
        <p>Personnalisation illimitée</p>
      </div>
    </div>
    <div class="row">
      <div class="col-12 col-md-4">
        <img src="@/assets/img/team/thierry-circle.jpg" />
      </div>
      <div class="col-12 col-md-8 premium-details">
        <b>Nutritionniste en ligne</b>
        <p>A votre disposition pour répondre à vos questions</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Level",
  props: ["level"],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
