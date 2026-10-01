# Week of 14–20 Sep 2026 — one product, two apps

Parent: #29 TRK-018. Policy: LOCK.md + security/E2E.md. PUBLIC_DNS=off. No App Store binary this week. No Sign in with Apple this week (#8 still needs Team ID in Keychain).

One product = Pianomanuel hub. Website stays `site/index.html`. Web app is the PWA chrome. iOS this week is Add to Home Screen + a WKWebView wrapper you open in Xcode on the Mac.

## Day map

| Day | Date | Surface | Done when |
|---|---|---|---|
| 1 Mon | 14 Sep | Plan + `site/app.html` shell | You can open app.html and reach Window / Shop / Board / iOS |
| 2 Tue | 15 Sep | PWA install path | manifest + sw.js list the app shell; Add to Home Screen steps on `site/ios.html` |
| 3 Wed | 16 Sep | Wire existing pages | app.html links only compiled `site/` pages; no :8080 as live |
| 4 Thu | 17 Sep | iOS wrapper source | `ios/PianomanuelHub/` opens in Xcode; loads bundled `site/index.html` |
| 5 Fri | 18 Sep | Security pass | no secrets in HTML; CSP/robots still on; SIWA still stub |
| 6 Sat | 19 Sep | Test | scene iframe loads; PWA cache does not cache Mental Canvas |
| 7 Sun | 20 Sep | Hold | App Store, public HTTPS, SIWA — next week only if #8 and a host exist |

## What this week is not

- Not a second MASTER database.
- Not a public pianomanuel.com cutover.
- Not deleting Drive Health / Seed workbooks.
- Not building SIWA against a missing Team ID.

## How to test without putting the build back on `~/Sites`

From a throwaway folder that you delete after:

```bash
git clone --depth 1 nina.v@example.com:pianomanuel/ManuelOps.git /tmp/mo && cd /tmp/mo/site && python3 -m http.server 8765
```

Open http://127.0.0.1:8765/app.html then throw `/tmp/mo` away. That is a test checkout, not a mirror.
