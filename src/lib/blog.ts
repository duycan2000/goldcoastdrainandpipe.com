import { getCollection, type CollectionEntry } from "astro:content";

export type Post = CollectionEntry<"blog">;

export async function getPosts(): Promise<Post[]> {
  const posts = await getCollection("blog", (p) => !p.data.draft);
  return posts.sort((a, b) => b.data.published.getTime() - a.data.published.getTime() || a.data.title.localeCompare(b.data.title));
}

export const postUrl = (p: Post) => `/blog/${p.id}`;

export function readingMinutes(p: Post) {
  const words = (p.body ?? "").split(/\s+/).filter(Boolean).length
    + p.data.takeaways.join(" ").split(/\s+/).length
    + p.data.faqs.map((f) => f.q + " " + f.a).join(" ").split(/\s+/).length;
  return Math.max(1, Math.round(words / 230));
}

export const fmtDate = (d: Date) => d.toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric", timeZone: "Australia/Brisbane" });
export const isoDate = (d: Date) => d.toISOString().slice(0, 10);

// Topic label shown on cards, from the service page the post supports.
export function topicOf(p: Post) {
  if (p.data.money.includes("relining")) return "Pipe relining";
  if (p.data.money.includes("cctv")) return "CCTV inspection";
  return "Blocked drains";
}

// srcset for a 1200px WebP that has a 600px sibling (name-600.webp), made by scripts/blog_images.py
export const srcset = (src: string) => `${src.replace(/\.webp$/, "-600.webp")} 600w, ${src} 1200w`;
