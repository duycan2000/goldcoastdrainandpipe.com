-- D1 schema for this site's lead store.
CREATE TABLE IF NOT EXISTS leads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  name TEXT,
  phone TEXT,
  email TEXT,
  suburb TEXT,
  problem TEXT,
  urgency TEXT,
  message TEXT,
  page TEXT,
  utm TEXT,
  honeypot TEXT,
  elapsed_ms INTEGER,
  is_test INTEGER NOT NULL DEFAULT 0,
  ip_country TEXT
);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads (created_at);
