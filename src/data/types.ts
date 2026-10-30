export type Block =
  | { kind: "prose"; id?: string; h2: string; body: string[]; aside?: { title: string; items: string[] } }
  | { kind: "steps"; id?: string; h2: string; intro?: string; items: { h: string; p: string }[] }
  | { kind: "checklist"; id?: string; h2: string; intro?: string; items: string[]; tone?: "warn" | "info" }
  | { kind: "facts"; id?: string; h2: string; intro?: string; items: { term: string; text: string }[] }
  | { kind: "prices"; id?: string; h2: string; intro?: string; rows: { job: string; range: string; typical: string }[]; note: string }
  | { kind: "cards"; id?: string; h2: string; intro?: string; items: { title: string; text: string; icon: string; href?: string }[] }
  | { kind: "callout"; id?: string; title: string; body: string[]; tone?: "warn" | "info" };

export interface Faq { q: string; a: string }

export interface PageData {
  slug: string;
  kind: "service" | "area";
  group: "Money" | "Support" | "Area";
  name: string;            // short label for breadcrumbs and links
  linkText: string;        // text used when other pages link here
  title: string;           // <title>, ≤ 60 characters
  description: string;     // meta description, ≤ 160 characters
  h1: string;
  cta?: string;            // one sentence in the closing call-to-action, using the page keyword
  lede: string;
  points: string[];        // 3 short hero ticks
  problem?: string;        // preselects the form's "What's blocked?"
  serviceType?: string;    // schema.org serviceType
  blocks: Block[];
  faqs: Faq[];
  related: string[];       // slugs
  sources?: string[];      // plain-text source notes shown under the content
}
