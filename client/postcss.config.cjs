module.exports = {
  plugins: {
  // Do not load Tailwind as a PostCSS plugin here to avoid the
  // "PostCSS plugin has moved" runtime error. The project uses the
  // Vite integration (`@tailwindcss/vite`) configured in
  // `astro.config.mjs` which runs Tailwind separately.
  autoprefixer: {},
  },
};
