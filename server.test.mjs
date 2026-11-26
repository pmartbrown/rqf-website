import assert from "node:assert/strict";
import http from "node:http";
import test from "node:test";
import { createServer, isGone } from "./server.mjs";

function gone(path) {
  return isGone(new URL(path, "https://realquickfunds.com"));
}

test("isGone: homepage query p is gone; other home queries and real pages are not", () => {
  assert.equal(gone("/?p=2348"), true);
  assert.equal(gone("/?p=4395"), true);
  assert.equal(gone("/?p="), true);
  assert.equal(gone("/?p=2545&utm=1"), true);
  assert.equal(gone("/?P=2348"), true);
  assert.equal(gone("/"), false);
  assert.equal(gone("/?utm_source=google"), false);
  assert.equal(gone("/about/?p=1"), false);
  assert.equal(gone("/stack/"), false);
  assert.equal(gone("/sitemap.xml"), false);
  assert.equal(gone("/robots.txt"), false);
  assert.equal(gone("/faq/"), false);
});

test("isGone: shop.php, goods.php, wp-*, productSearch, men-clothing, numbered sitemaps", () => {
  assert.equal(gone("/shop.php"), true);
  assert.equal(gone("/shop.php?y=37812464971100"), true);
  assert.equal(gone("/shop.php?sitemap.xml"), true);
  assert.equal(gone("/goods.php"), true);
  assert.equal(gone("/goods.php?sitemap.xml"), true);
  assert.equal(gone("/wp-content/sitemap317.xml"), true);
  assert.equal(gone("/wp-admin/index.php"), true);
  assert.equal(gone("/productSearch/pictureSearch?id=2453142451100"), true);
  assert.equal(gone("/men-clothing"), true);
  assert.equal(gone("/men-clothing/"), true);
  assert.equal(gone("/sitemap_index.xml"), true);
  assert.equal(gone("/sitemap317.xml"), true);
  assert.equal(gone("/sitemap484.xml"), true);
  assert.equal(gone("/sitemap.xml"), false);
});

test("isGone: casino slugs, including referring leftover", () => {
  assert.equal(gone("/best-casino-odds/"), true);
  assert.equal(gone("/best-casino-odds"), true);
  assert.equal(gone("/best-casino-to-visit-in-canada/"), true);
  assert.equal(gone("/50-free-spins-register-card-canada/"), true);
  assert.equal(gone("/live-bet-casino/"), true);
});

test("HTTP: 410 spam, 200 real pages, 404 unknown, sitemap preserved", async () => {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();
  const get = (p) =>
    new Promise((resolve, reject) => {
      http
        .get({ host: "127.0.0.1", port, path: p, headers: { "cache-control": "no-cache" } }, (res) => {
          const chunks = [];
          res.on("data", (c) => chunks.push(c));
          res.on("end", () =>
            resolve({
              status: res.statusCode,
              robots: res.headers["x-robots-tag"] || "",
              type: res.headers["content-type"] || "",
              body: Buffer.concat(chunks).toString("utf8"),
            }),
          );
        })
        .on("error", reject);
    });

  try {
    const home = await get("/");
    assert.equal(home.status, 200);
    assert.doesNotMatch(home.robots, /noindex/);

    const pQuery = await get("/?p=2348");
    assert.equal(pQuery.status, 410);
    assert.match(pQuery.robots, /noindex/);
    assert.equal(pQuery.body, "Gone");

    const shop = await get("/shop.php?y=1");
    assert.equal(shop.status, 410);
    assert.match(shop.robots, /noindex/);

    const casino = await get("/best-casino-odds/");
    assert.equal(casino.status, 410);

    const sitemap = await get("/sitemap.xml");
    assert.equal(sitemap.status, 200);
    assert.match(sitemap.body, /<urlset/);

    const about = await get("/about/");
    assert.equal(about.status, 200);
    assert.match(about.body, /RealQuick Funds|about/i);

    const unknown = await get("/this-page-does-not-exist-xyz/");
    assert.equal(unknown.status, 404);
    assert.match(unknown.robots, /noindex/);

    const numbered = await get("/sitemap317.xml");
    assert.equal(numbered.status, 410);

    const realIndex = await get("/sitemap_index.xml");
    assert.equal(realIndex.status, 410);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});
