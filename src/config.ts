// Site-wide settings. Change these values here only; every page reads from this file.
export const SITE = {
  brand: "Gold Coast Drain & Pipe",
  domain: "goldcoastdrainandpipe.com",
  url: "https://goldcoastdrainandpipe.com",
  // TODO: replace with the Twilio 1800 number once purchased.
  phoneDisplay: "1800 XXX XXX",
  phoneHref: "", // e.g. "+611800123456"
  email: "hello@goldcoastdrainandpipe.com",
  // TODO: the person or business that operates the referral service (shown in the footer disclosure).
  operator: "Duy Digital",
  city: "Gold Coast",
  state: "QLD",
  // Date of the last real content change. Update when you edit page copy; used as <lastmod> in the sitemap.
  contentUpdated: "2026-10-29",
  // Set to true once real, attributable tenant reviews exist.
  showReviews: false,
};

export const PROBLEMS = [
  { id: "toilet", href: "/blocked-toilet-gold-coast", label: "Blocked toilet", hint: "Won't flush, rising water or overflowing", icon: "toilet" },
  { id: "sewer", href: "/blocked-sewer-tree-roots-gold-coast", label: "Sewer or outside drain overflowing", hint: "Gully grate lifting, sewage smell, water pooling", icon: "sewer" },
  { id: "shower", href: "/blocked-sink-shower-drains-gold-coast", label: "Shower, sink or basin", hint: "Slow draining or standing water", icon: "sink" },
  { id: "stormwater", href: "/blocked-stormwater-drains-gold-coast", label: "Stormwater or downpipe", hint: "Yard flooding or pits overflowing in rain", icon: "rain" },
  { id: "recurring", href: "/pipe-relining-gold-coast", label: "Keeps coming back", hint: "Tree roots or a cracked pipe, may need relining", icon: "roots" },
  { id: "unsure", href: "/cctv-drain-inspection-gold-coast", label: "Not sure what's blocked", hint: "A CCTV camera finds the cause", icon: "camera" },
] as const;

// Suburbs that have their own page.
export const AREA_LINKS: Record<string, string> = {
  Coomera: "/blocked-drains-coomera",
  Southport: "/blocked-drains-southport",
  Robina: "/blocked-drains-robina",
  Nerang: "/blocked-drains-nerang",
  Helensvale: "/blocked-drains-helensvale",
};

export const AREAS = {
  "Northern Gold Coast": ["Coomera", "Upper Coomera", "Pimpama", "Ormeau", "Helensvale", "Oxenford", "Hope Island", "Coombabah", "Runaway Bay", "Paradise Point"],
  "Central Gold Coast": ["Southport", "Labrador", "Arundel", "Ashmore", "Benowa", "Bundall", "Surfers Paradise", "Broadbeach", "Mermaid Beach", "Nerang", "Carrara", "Robina", "Varsity Lakes", "Mudgeeraba", "Worongary"],
  "Southern Gold Coast": ["Burleigh Heads", "Miami", "Palm Beach", "Currumbin", "Elanora", "Tugun", "Bilinga", "Coolangatta"],
};

export const ALL_SUBURBS = Object.values(AREAS).flat().sort();
