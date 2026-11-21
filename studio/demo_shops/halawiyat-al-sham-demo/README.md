# Halawiyat Al-Sham (demo) — your shop's own app

**This app belongs to Halawiyat Al-Sham (demo).** You own it: the files, the content and the name. There is no lock-in and no monthly fee to HVT to keep it running. If you stop working with HVT Innovations, the app keeps working.

## What's in this folder

| Folder / file | What it is |
|---|---|
| `site/` | **The app your customers use.** Plain files. Upload this folder to any web host. |
| `admin/` | The page where you change prices, hours, offers and colours. |
| `data/shop.json` | All your shop information (including your private supplier list and a scrambled copy of your password). |
| `server.py` | A tiny program that shows the app and the admin page on your own computer. |
| `lib/` | Optional connectors (payments, barcode lookup, exchange rates, etc.). |

Private things are never put in `site/`: your password, your supplier list and any keys you add.

## Start it on a computer (3 steps)

1. Install Python 3 (free) from https://www.python.org/downloads/ (Windows: tick "Add python.exe to PATH").
2. Double-click `Start shop app (Mac).command` or `Start shop app (Windows).bat`. (Or type `python3 server.py`.)
3. Open **http://localhost:8080** to see the app, and **http://localhost:8080/admin** to change it. Log in with your owner password.

Forgot the password? In this folder run `python3 server.py --set-password`.

## Put it online so customers can open it on their phones

The app is just the `site/` folder, so it can be hosted for free or very cheaply. One way (checked 26 Sept 2026):

1. Make a free account at **Cloudflare Pages**: https://pages.cloudflare.com/
2. Choose **Create a project → Direct upload**, give it your shop name, and drag the `site/` folder in.
3. You get a link like `https://yourshop.pages.dev`. Put it on your window as a QR code, on receipts, in your WhatsApp status.

When you change something in the admin page, upload the `site/` folder again (same project) and the app updates.

Want your own name, like `www.yourshop.co.uk`? Buy the name from a domain seller (typically a few pounds a year for .co.uk — check the price when you buy), then in Cloudflare Pages choose **Custom domains** and follow the steps.

## How customers add it to their phone

- **iPhone (Safari):** open the link → tap the Share button → **Add to Home Screen**.
- **Android (Chrome):** open the link → tap **Install app** (or the ⋮ menu → **Add to Home screen**).

After the first visit, the app opens even without signal (it shows the last saved prices and hours).

## Honest notes

- Screen words (like "Open now") are translated for the main languages. They have not all been checked by a native speaker yet — tell us if something reads oddly. Your own text (product names, offers) shows exactly as you type it.
- Prices are whatever you enter. The app never changes them.
- The WhatsApp order button just opens WhatsApp with the order typed in. You confirm the order and payment with the customer yourself.
- A Pay button only appears if you paste a payment link from your own Stripe, Square or SumUp account. The money goes straight to you.

Made with HVT Foundry Studio by HVT Innovations (Harrow).
