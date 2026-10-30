// Cloudflare Worker: serves the static site and handles the lead form at POST /api/lead.
// Leads are stored in this site's D1 database, then forwarded to the Duy SEO platform
// (POST {PLATFORM_URL}/hooks/lead/{SITE_ID}, HMAC-signed with LEAD_SECRET).

const AU_PHONE = /^(?:\+?61|0)[2-478]\d{8}$/;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === "/api/lead") {
      if (request.method !== "POST") return json({ error: "Method not allowed" }, 405);
      return handleLead(request, env, ctx);
    }
    return env.ASSETS.fetch(request);
  },
};

async function handleLead(request, env, ctx) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "Invalid request" }, 400);
  }

  const isTest = request.headers.get("X-Synthetic-Test") === "1" || body.test === true;
  const clean = (v, max) => String(v ?? "").trim().slice(0, max);
  const lead = {
    name: clean(body.name, 80),
    phone: clean(body.phone, 20).replace(/[\s()-]/g, ""),
    email: clean(body.email, 120),
    suburb: clean(body.suburb, 60),
    problem: clean(body.problem, 40),
    urgency: clean(body.urgency, 20),
    message: clean(body.message, 1200),
    page: clean(body.page, 200),
    utm: typeof body.utm === "object" && body.utm ? body.utm : {},
    honeypot: clean(body.honeypot, 200),
    elapsed_ms: Number(body.elapsed_ms) || 0,
    test: isTest,
  };

  if (!isTest) {
    if (lead.name.length < 2 || lead.suburb.length < 2 || !AU_PHONE.test(lead.phone)) {
      return json({ error: "Name, Australian phone number and suburb are required" }, 422);
    }
  }

  // Store locally first so a lead is never lost if forwarding fails.
  if (env.DB) {
    try {
      await env.DB.prepare(
        `INSERT INTO leads (created_at, name, phone, email, suburb, problem, urgency, message, page, utm, honeypot, elapsed_ms, is_test, ip_country)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12, ?13, ?14)`
      ).bind(
        new Date().toISOString(), lead.name, lead.phone, lead.email, lead.suburb, lead.problem, lead.urgency,
        lead.message, lead.page, JSON.stringify(lead.utm), lead.honeypot, lead.elapsed_ms, isTest ? 1 : 0,
        request.cf?.country ?? null
      ).run();
    } catch (err) {
      console.error("D1 insert failed", err);
    }
  }

  ctx.waitUntil(forwardLead(env, lead));
  return json({ ok: true });
}

// Sends the lead to the platform. Signature = hex HMAC-SHA256(LEAD_SECRET, timestamp + "." + rawBody).
async function forwardLead(env, lead) {
  if (!env.PLATFORM_URL || !env.SITE_ID || !env.LEAD_SECRET) return;
  const raw = JSON.stringify({
    name: lead.name,
    phone: lead.phone,
    email: lead.email,
    message: lead.message,
    page: lead.page,
    utm: lead.utm,
    honeypot: lead.honeypot,
    elapsed_ms: lead.elapsed_ms,
    ...(lead.test ? { test: true } : {}),
  });
  const ts = Math.floor(Date.now() / 1000).toString();
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(env.LEAD_SECRET), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${ts}.${raw}`));
  const hex = [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
  try {
    const res = await fetch(`${env.PLATFORM_URL.replace(/\/$/, "")}/hooks/lead/${env.SITE_ID}`, {
      method: "POST",
      headers: { "content-type": "application/json", "X-Timestamp": ts, "X-Signature": hex },
      body: raw,
    });
    if (!res.ok) console.error("Platform rejected lead", res.status);
  } catch (err) {
    console.error("Lead forward failed", err);
  }
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json" } });
}
