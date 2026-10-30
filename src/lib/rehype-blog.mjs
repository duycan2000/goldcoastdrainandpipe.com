// Rehype plugin for blog posts:
// - an image alone in a paragraph becomes <figure> with a <figcaption> taken from its title,
//   and gets width/height (from src/data/blog-images.json), lazy loading and async decoding;
// - tables are wrapped in a scrollable container;
// - external links open in a new tab with rel="noopener" (they stay dofollow).
import fs from "node:fs";
import path from "node:path";

const manifestPath = path.resolve("src/data/blog-images.json");

function loadManifest() {
  try { return JSON.parse(fs.readFileSync(manifestPath, "utf8")); } catch { return {}; }
}

const isWs = (n) => n.type === "text" && !n.value.trim();

export default function rehypeBlog() {
  return (tree) => {
    const dims = loadManifest();
    const walk = (node) => {
      if (!node.children) return;
      node.children = node.children.map((child) => {
        // <p><img></p>  ->  <figure><img><figcaption></figure>
        if (child.type === "element" && child.tagName === "p") {
          const kids = child.children.filter((k) => !isWs(k));
          if (kids.length === 1 && kids[0].type === "element" && kids[0].tagName === "img") {
            const img = kids[0];
            const p = img.properties;
            const caption = p.title;
            delete p.title;
            const d = dims[p.src];
            if (d) { p.width = d.w; p.height = d.h; }
            if (/\.webp$/.test(p.src)) {
              p.srcSet = `${p.src.replace(/\.webp$/, "-600.webp")} 600w, ${p.src} 1200w`;
              p.sizes = "(min-width: 1040px) 720px, calc(100vw - 32px)";
            }
            p.loading = "lazy";
            p.decoding = "async";
            const fig = { type: "element", tagName: "figure", properties: { className: ["post-figure"] }, children: [img] };
            if (caption) fig.children.push({ type: "element", tagName: "figcaption", properties: {}, children: [{ type: "text", value: caption }] });
            return fig;
          }
        }
        if (child.type === "element" && child.tagName === "table") {
          return { type: "element", tagName: "div", properties: { className: ["table-wrap"], tabIndex: 0, role: "region", ariaLabel: "Table, scroll sideways on small screens" }, children: [child] };
        }
        if (child.type === "element" && child.tagName === "a") {
          const href = String(child.properties.href || "");
          if (/^https?:\/\//.test(href) && !href.includes("goldcoastdrainandpipe.com")) {
            child.properties.target = "_blank";
            child.properties.rel = ["noopener"];
          }
        }
        walk(child);
        return child;
      });
    };
    walk(tree);
  };
}
