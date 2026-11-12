// Server-side Tiqets click counter: /go/tiqets?u=<tiqets url>&p=<page path>
//
// Every Tiqets link click goes through here (webflow-sync.js swaps the href
// just before the click), so we count clicks on our own server, where cookie
// banners and ad blockers can't hide them. Then we 302 to Tiqets with the
// exact URL the page built (partner id, tq_campaign with the Google click id).
//
// Storage: Upstash Redis over its REST API (KV_REST_API_URL / KV_REST_API_TOKEN,
// injected by the Vercel Marketplace integration). Without it the click is
// still logged to the function log and the visitor is still redirected.
//
// Keys, per UTC day (kept 400 days):
//   tqc:<day>        hash  total, ad, organic, bot, page:<path>, pl:<placement>
//   tqc:<day>:ids    set   distinct Google click ids that clicked (gclid/gbraid/wbraid)
//   tqc:<day>:log    list  one JSON line per click, for joining to Google Ads campaigns

const FALLBACK = 'https://www.tiqets.com/';
const TTL_SECONDS = 400 * 24 * 3600;
const BOT_RE = /bot|crawl|spider|slurp|preview|facebookexternalhit|headless|lighthouse|pingdom|monitor/i;

export function safeTarget(raw) {
  if (!raw || typeof raw !== 'string') return null;
  let url;
  try {
    url = new URL(raw);
  } catch {
    return null;
  }
  if (url.protocol !== 'https:') return null;
  const host = url.hostname.toLowerCase();
  if (host !== 'tiqets.com' && !host.endsWith('.tiqets.com')) return null;
  return url;
}

// tq_campaign is "<placement>" or "<placement>--<gclid|gbraid|wbraid>-<id>".
export function parseCampaign(url) {
  const tq = (url && url.searchParams.get('tq_campaign')) || '';
  const m = tq.match(/^(.*?)--(gclid|gbraid|wbraid)-(.+)$/);
  if (m) return { placement: m[1] || '', clickType: m[2], clickId: m[3] };
  return { placement: tq, clickType: null, clickId: null };
}

export function cleanPath(p) {
  if (!p || typeof p !== 'string') return '';
  const path = p.split(/[?#]/)[0].slice(0, 200);
  return path.startsWith('/') ? path : '';
}

export function buildEvent(req, target, now = new Date()) {
  const q = req.query || {};
  const ua = String((req.headers && req.headers['user-agent']) || '');
  const { placement, clickType, clickId } = parseCampaign(target);
  return {
    ts: now.toISOString(),
    day: now.toISOString().slice(0, 10),
    page: cleanPath(q.p),
    placement: placement.slice(0, 100),
    clickType,
    clickId: clickId ? clickId.slice(0, 200) : null,
    bot: BOT_RE.test(ua),
  };
}

export function redisCommands(ev) {
  const key = `tqc:${ev.day}`;
  const cmds = [];
  if (ev.bot) {
    cmds.push(['HINCRBY', key, 'bot', '1']);
  } else {
    cmds.push(['HINCRBY', key, 'total', '1']);
    cmds.push(['HINCRBY', key, ev.clickId ? 'ad' : 'organic', '1']);
    if (ev.page) cmds.push(['HINCRBY', key, `page:${ev.page}`, '1']);
    if (ev.placement) cmds.push(['HINCRBY', key, `pl:${ev.placement}`, '1']);
    if (ev.clickId) {
      cmds.push(['SADD', `${key}:ids`, `${ev.clickType}:${ev.clickId}`]);
      cmds.push(['EXPIRE', `${key}:ids`, String(TTL_SECONDS)]);
    }
    cmds.push(['RPUSH', `${key}:log`, JSON.stringify(ev)]);
    cmds.push(['EXPIRE', `${key}:log`, String(TTL_SECONDS)]);
  }
  cmds.push(['EXPIRE', key, String(TTL_SECONDS)]);
  return cmds;
}

async function record(ev) {
  const base = process.env.KV_REST_API_URL;
  const token = process.env.KV_REST_API_TOKEN;
  if (!base || !token) return false;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 1500);
  try {
    const res = await fetch(`${base.replace(/\/$/, '')}/pipeline`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(redisCommands(ev)),
      signal: ctrl.signal,
    });
    return res.ok;
  } finally {
    clearTimeout(timer);
  }
}

export default async function handler(req, res) {
  const target = safeTarget((req.query || {}).u);
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  res.setHeader('Referrer-Policy', 'origin');

  if (!target) {
    res.statusCode = 302;
    res.setHeader('Location', FALLBACK);
    return res.end();
  }

  const ev = buildEvent(req, target);
  // "stored" shows in the log line whether Redis took the click
  // (false = KV env vars missing or Redis returned an error).
  let stored = false;
  try {
    stored = await record(ev);
  } catch (err) {
    console.error('tiqets_click store failed:', err && err.message);
  }
  console.log('tiqets_click', JSON.stringify({ ...ev, stored }));

  res.statusCode = 302;
  res.setHeader('Location', target.toString());
  return res.end();
}
