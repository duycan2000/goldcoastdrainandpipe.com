import { SITE } from "../config";
import { PAGES } from "../data/pages";
import { getPosts, postUrl, isoDate } from "../lib/blog";

// Indexable pages only, home first, then money, support and suburb pages.
// /partner (noindex) and the 404 page are left out on purpose.
const ORDER = { Money: 1, Support: 2, Area: 3 } as const;

export async function GET() {
  const content = [...PAGES].sort((a, b) => ORDER[a.group] - ORDER[b.group]).map((p) => `/${p.slug}`);
  const posts = await getPosts();
  const latestPost = posts.reduce((m, p) => (isoDate(p.data.updated) > m ? isoDate(p.data.updated) : m), SITE.contentUpdated);
  // [path, lastmod]: posts use their own "updated" date from the Markdown front matter.
  const entries: [string, string][] = [
    ...["/", ...content].map((p) => [p, SITE.contentUpdated] as [string, string]),
    ["/blog", latestPost],
    ...posts.map((p) => [postUrl(p), isoDate(p.data.updated)] as [string, string]),
    ...["/about", "/contact", "/privacy", "/terms"].map((p) => [p, SITE.contentUpdated] as [string, string]),
  ];
  const urls = entries
    .map(([p, d]) => `  <url>\n    <loc>${new URL(p, SITE.url).toString()}</loc>\n    <lastmod>${d}</lastmod>\n  </url>`)
    .join("\n");
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`, {
    headers: { "content-type": "application/xml" },
  });
}
