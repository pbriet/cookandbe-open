<template>
  <div class="d-none d-print-block">
    <table>
      <tr>
        <td style="width: 150px">
          <img style="width: 100%" :src="'/' + IMG_BRAND + '/img/logo-greyscale-wide.png'" v-if="ENABLE_LOGO" />
        </td>
        <td style="5px;">Chaque jour des idées repas personnalisées et équilibrées !</td>
        <td style="width: 150px" v-if="ENABLE_PUBLIC_PAYMENT">
          <div class="inscription-section">
            Inscription gratuite sur<br /><b>{{ WWW_HOST }}</b>
          </div>
        </td>
      </tr>
    </table>
  </div>
</template>

<script>
import { WWW_HOST, ENABLE_PUBLIC_PAYMENT, ENABLE_LOGO, IMG_BRAND } from "@/config.js";

export default {
  name: "MainMenuPrint",
  data: () => ({
    WWW_HOST,
    ENABLE_PUBLIC_PAYMENT,
    ENABLE_LOGO,
    IMG_BRAND,
  }),
  computed: {},
  methods: {},
};
</script>

<style scoped lang="scss">
table {
  vertical-align: middle;
  width: 100%;
}

td {
  padding: 5px;
}

.inscription-section {
  text-align: center;
  border: 1px solid #333333;
  border-radius: $op-radius-lg;
  padding: 5px;
}
</style>
