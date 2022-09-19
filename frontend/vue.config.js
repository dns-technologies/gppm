module.exports = {
  transpileDependencies: ["vuetify"],
  lintOnSave: false,
  css: {
    extract: process.env.NODE_ENV === "production" ? {
      ignoreOrder: true,
    } : false,
  },
  chainWebpack: (config) => {
    config
      .plugin('html')
      .tap(args => {
        args[0].title = process.env.VUE_APP_NAME
        return args
      });
    config.module
      .rule("vue")
      .use("vue-loader")
      .loader("vue-loader")
      .tap((options) =>
        Object.assign(options, {
          transformAssetUrls: {
            "v-img": ["src", "lazy-src"],
            "v-card": "src",
            "v-card-media": "src",
            "v-responsive": "src",
          },
        }),
      );
  },
};
