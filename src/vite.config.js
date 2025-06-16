import { defineConfig } from 'vite'
import preact from '@preact/preset-vite'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  root: resolve(__dirname, "./assets/"),
  base: "/static/",
  publicDir: resolve("./assets/public"),
  assetsDir: "",
  
  build: {
    emptyOutDir: true,
    manifest: "manifest.json",
    outDir: resolve("./dist/"),
    copyPublicDir: true,
    rollupOptions: {
      input: {
        main: "./assets/main.js",
        styles: "./assets/styles.scss"
      }
    }
  },
  plugins: [preact()],
})
