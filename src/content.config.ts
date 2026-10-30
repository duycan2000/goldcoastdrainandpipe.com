import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

// Blog posts live in src/content/blog/*.md. One file = one post at /blog/<file-name>.
const blog = defineCollection({
  loader: glob({ pattern: "*.md", base: "./src/content/blog" }),
  schema: z.object({
    title: z.string().max(60),              // SEO <title>
    h1: z.string(),
    description: z.string().max(160),
    focusKeyword: z.string(),
    secondaryKeywords: z.array(z.string()).default([]),
    published: z.coerce.date(),
    updated: z.coerce.date(),
    image: z.string(),                      // /blog/<slug>/cover.webp (a cover.jpg of the same name is used for social cards)
    imageAlt: z.string(),
    money: z.string(),                      // slug of the service page this post supports ("" = home page)
    moneyAnchor: z.string(),
    problem: z.string().optional(),         // preselects the lead form
    excerpt: z.string(),
    takeaways: z.array(z.string()),
    faqs: z.array(z.object({ q: z.string(), a: z.string() })).default([]),
    sources: z.array(z.object({ title: z.string(), url: z.string().url() })).default([]),
    related: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
