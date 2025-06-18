import { defineConfig } from "vite";
import preact from "@preact/preset-vite";
import { resolve } from "path";
import Icons from "unplugin-icons/vite";
import { FileSystemIconLoader } from 'unplugin-icons/loaders';
// https://vite.dev/config/

const icons = Icons({
  compiler: "jsx",
  autoInstall: true,
  jsx: "preact",
  customCollections: {
    "nippy": FileSystemIconLoader("./assets/icons"),
  },
});
export default defineConfig({
  root: resolve(__dirname, "./assets/"),
  base: "/static/",
  publicDir: resolve("./assets/public"),
  assetsDir: "",
  envPrefix: "ENV_",
  build: {
    emptyOutDir: true,
    manifest: "manifest.json",
    outDir: resolve("./dist/"),
    copyPublicDir: true,
    rollupOptions: {
      input: {
        main: "./assets/main.js",
        styles: "./assets/styles.scss",
        new: "./assets/new.scss",
      },
    },
  },
  plugins: [preact(), icons],
});
