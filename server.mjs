/**
 * Origin server for realquickfunds.com.
 *
 * Render static sites cannot return 410 for /?p= (index.html already exists)
 * or match query strings. This server 410s leftover spam and otherwise
 * serves the existing static files.
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = path.dirname(fileURLToPath(import.meta.url));

const GONE_PATHS = new Set([
  "/50-free-spins-register-card-canada/",
  "/best-canada-online-live-casino/",
  "/best-casino-odds/",
  "/best-casino-to-visit-in-canada/",
  "/best-no-deposit-bonus-canada/",
  "/best-online-slot-games-to-win-real-money/",
  "/best-slots-to-win/",
  "/best-spin-games-to-win-money/",
  "/biggest-gambling-companies/",
  "/biggest-gambling-sites/",
  "/bingo-games-canada/",
  "/canada-casino-list/",
  "/cherry-gold-casino-review-and-free-chips-bonus/",
  "/cities-in-canada-with-casinos/",
  "/codere-casino-no-deposit-bonus-codes-for-free-spins-2026/",
  "/free-canada-casino-games/",
  "/las-vegas-usa-casino-review-and-free-chips-bonus/",
  "/latest-online-canada-casinos/",
  "/live-bet-casino/",
  "/live-roulette-sites/",
  "/low-wager-casinos/",
  "/men-clothing",
  "/men-clothing/",
  "/new-free-spins-no-deposit-casino/",
  "/online-casino-wins/",
  "/online-gambling-in-nc-canada/",
  "/phone-casino-games/",
  "/plovdiv-casino-no-deposit-bonus-codes-for-free-spins-2026/",
  "/roulette-real-money-online/",
  "/safe-online-gambling/",
  "/slot-machines-games/",
  "/slot-machines-real-money/",
  "/slots-sign-up-offer/",
  "/the-star-casino-review-and-free-chips-bonus/",
  "/top-canada-online-casino/",
  "/top-slot-games/",
  "/sitemap_index.xml",
]);

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".xml": "application/xml; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".webp": "image/webp",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".map": "application/json",
};

export function isGone(url) {
  const u = typeof url === "string" ? new URL(url, "https://realquickfunds.com") : url;
  let pathname = u.pathname || "/";
  try {
    pathname = decodeURIComponent(pathname);
  } catch {
    // keep the raw path
  }
  if (pathname.length > 1 && pathname.endsWith("/")) {
    // keep trailing slash for exact set membership; also try trimmed below
  }
  const pathLower = pathname.toLowerCase();

  if (
    (pathname === "/" || pathname === "") &&
    [...u.searchParams.keys()].some((k) => k.toLowerCase() === "p")
  ) {
    return true;
  }
  if (pathLower === "/shop.php" || pathLower.startsWith("/shop.php")) return true;
  if (pathLower === "/goods.php" || pathLower.startsWith("/goods.php")) return true;
  if (
    pathLower.startsWith("/wp-content/") ||
    pathLower.startsWith("/wp-admin/") ||
    pathLower.startsWith("/wp-includes/")
  ) {
    return true;
  }
  if (pathLower.startsWith("/productsearch")) return true;
  if (pathLower.endsWith(".php") || pathLower.includes(".php/")) return true;
  if (/^\/sitemap\d+\.xml$/i.test(pathname)) return true;
  if (GONE_PATHS.has(pathname) || GONE_PATHS.has(pathLower)) return true;
  if (pathname.length > 1 && pathname.endsWith("/") && GONE_PATHS.has(pathname.slice(0, -1))) {
    return true;
  }
  if (GONE_PATHS.has(pathname + "/")) return true;
  return false;
}

export function goneHeaders() {
  return {
    "content-type": "text/plain; charset=utf-8",
    "x-robots-tag": "noindex, nofollow",
    "cache-control": "public, max-age=3600",
  };
}

function isSafeSegment(seg) {
  return seg !== "" && seg !== "." && seg !== ".." && !seg.startsWith(".");
}

export function resolveStatic(urlPath) {
  let decoded;
  try {
    decoded = decodeURIComponent(urlPath.split("?")[0] || "/");
  } catch {
    return null;
  }
  if (!decoded.startsWith("/")) decoded = "/" + decoded;
  const parts = decoded.split("/").filter(Boolean);
  if (!parts.every(isSafeSegment)) return null;
  const abs = path.resolve(ROOT, ...parts);
  const rel = path.relative(ROOT, abs);
  if (rel.startsWith("..") || path.isAbsolute(rel)) return null;
  if (fs.existsSync(abs) && fs.statSync(abs).isFile()) return abs;
  const asIndex = path.resolve(ROOT, ...parts, "index.html");
  const relIndex = path.relative(ROOT, asIndex);
  if (relIndex.startsWith("..") || path.isAbsolute(relIndex)) return null;
  if (fs.existsSync(asIndex) && fs.statSync(asIndex).isFile()) return asIndex;
  return null;
}

function send(res, status, headers, body) {
  res.writeHead(status, headers);
  res.end(body);
}

export function handleRequest(req, res) {
  const host = req.headers.host || "realquickfunds.com";
  let url;
  try {
    url = new URL(req.url || "/", `https://${host}`);
  } catch {
    send(res, 400, { "content-type": "text/plain; charset=utf-8" }, "Bad Request");
    return;
  }

  if (isGone(url)) {
    send(res, 410, goneHeaders(), "Gone");
    return;
  }

  if (req.method !== "GET" && req.method !== "HEAD") {
    send(res, 405, { allow: "GET, HEAD" }, "Method Not Allowed");
    return;
  }

  const file = resolveStatic(url.pathname);
  if (file) {
    const ext = path.extname(file).toLowerCase();
    const headers = {
      "content-type": MIME[ext] || "application/octet-stream",
      "cache-control": ext === ".html" ? "public, max-age=0, s-maxage=300" : "public, max-age=86400",
      "x-content-type-options": "nosniff",
    };
    if (req.method === "HEAD") {
      send(res, 200, headers, "");
      return;
    }
    res.writeHead(200, headers);
    fs.createReadStream(file).pipe(res);
    return;
  }

  const notFound = path.join(ROOT, "404.html");
  const body = fs.existsSync(notFound) ? fs.readFileSync(notFound) : "Not Found";
  send(
    res,
    404,
    {
      "content-type": "text/html; charset=utf-8",
      "x-robots-tag": "noindex",
      "cache-control": "public, max-age=300",
    },
    req.method === "HEAD" ? "" : body,
  );
}

export function createServer() {
  return http.createServer(handleRequest);
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const port = Number(process.env.PORT) || 3000;
  createServer().listen(port, "0.0.0.0", () => {
    console.log(`rqf-website listening on ${port}`);
  });
}
