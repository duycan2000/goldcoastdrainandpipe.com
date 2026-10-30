import { defineConfig } from "astro/config";
import rehypeBlog from "./src/lib/rehype-blog.mjs";

export default defineConfig({
  site: "https://goldcoastdrainandpipe.com",
  output: "static",
  trailingSlash: "never",
  build: { format: "file", inlineStylesheets: "always" },
  markdown: { rehypePlugins: [rehypeBlog] },
});
