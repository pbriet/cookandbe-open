<template>
  <div class="op-page">
    <div class="alert alert-danger" id="alert-no-cookies">
      <div class="row">
        <div class="col-12">
          <table>
            <tr>
              <td class="d-none d-sm-table-cell">
                <span class="op-icon-dxxl">
                  <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" />
                </span>
              </td>
              <td>
                Votre navigateur désactive l'utilisation des <i>cookies</i>.<br />
                Malheureusement, ces petites bêtes sont essentielles pour faire fonctionner le site !<br /><br />
                Merci de les activer et de rafraichir la page :)
                <br /><br />
                Comment faire ? Allez voir sur
                <a href="http://www.accepterlescookies.com/" target="_blank">http://www.accepterlescookies.com/</a>
              </td>
            </tr>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "CookiesAlert",
  props: [],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
