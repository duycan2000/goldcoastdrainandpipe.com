# Gold Coast Drain & Pipe (R&R site #1)

Astro static site + Cloudflare Worker (static assets + `/api/lead`).

## Before going live
1. `src/config.ts`: set `phoneDisplay` and `phoneHref` (Twilio 1800 number), `email`, `operator`.
2. Buy the domain `goldcoastdrainandpipe.com` (Cloudflare Registrar) and set up Email Routing for the address in `email`.
3. Create the D1 database and apply the schema:
   ```
   npx wrangler d1 create gcdp-leads        # copy the id into wrangler.jsonc
   npx wrangler d1 execute gcdp-leads --remote --file=schema.sql
   ```
4. Add the site in the Duy SEO platform (R&R → Portfolio), then fill `PLATFORM_URL` and `SITE_ID` in `wrangler.jsonc` and set the secret:
   ```
   npx wrangler secret put LEAD_SECRET      # the site's lead_secret from the platform
   ```
5. In the platform, set `form_test_url` to `https://goldcoastdrainandpipe.com/api/lead`.

## Commands
```
npm install
npm run dev        # http://localhost:4321
npm run build      # outputs dist/
npm run deploy     # build + wrangler deploy
```

## Lead flow
Form → `POST /api/lead` (Worker) → validates AU phone, stores in D1 → forwards to
`{PLATFORM_URL}/hooks/lead/{SITE_ID}` with `X-Timestamp` and
`X-Signature = hex HMAC-SHA256(LEAD_SECRET, timestamp + "." + rawBody)`.
Requests with `X-Synthetic-Test: 1` are stored and forwarded with `test: true`.

## Pages
- Home: `src/pages/index.astro`
- Service and suburb pages: one template (`src/layouts/ServicePage.astro`), content in `src/data/pages.ts`.
  To add a page, add an entry to `PAGES`; the route, sitemap, footer links and schema follow automatically.
- About, Contact, Partner (noindex), Privacy, Terms: `src/pages/*.astro`.
- Shared prices live at the top of `src/data/pages.ts` (`P`), so one edit updates every page.

## Cloning to another city
Copy the project, change `src/config.ts` (brand, domain, phone, AREAS, AREA_LINKS) and rewrite
`src/data/pages.ts` for the new city. Rewrite the copy rather than search-and-replace the city name.

## Blog (Guides)
- Posts are Markdown files in `src/content/blog/`. The file name is the URL: `pipe-relining-cost.md` → `/blog/pipe-relining-cost`.
- Front matter holds the SEO title (≤ 60 chars), meta description (≤ 160), focus and secondary keywords, cover image,
  key takeaways, FAQs (rendered with FAQPage schema), sources and related posts. The build fails if a field is missing or too long.
- `money` links the post to the service page it supports. That page then lists the post under "Guides on this topic".
- Illustrations are drawn in `scripts/blog_images.py` and rendered to `public/blog/<slug>/` (WebP, 600px copies and a JPG cover
  for social cards). Run `python3 scripts/blog_images.py` after editing them. Replace with real job photos when you have them.
- A Markdown image with a title becomes a figure with a caption: `![alt text](/blog/slug/image.webp "Caption")`.
- When you publish or update a post, change `updated` in its front matter; the sitemap uses it as `<lastmod>`.
