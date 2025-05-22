module.exports = {
  devServer: {
    disableHostCheck: true, // This is necessary to make it work with docker-compose & nginx-proxy
  },
  css: {
    loaderOptions: {
      sass: {
        prependData: `
          @use 'sass:math';
          @import "@/assets/css/base.scss";
        `,
      },
    },
  },
};
