# CLAUDE.md — Project & Brand Context for Dan Marc Llanes Portfolio

## 1. Project Overview
This repository contains the single-page personal portfolio and client solutions website (`index.html`) for **Dan Marc Llanes**. It serves an international audience of small business owners (SMBs), hotel/short-term rental hosts, and clinics/healthcare practitioners, alongside prospective beta testers for Dan's mobile apps.

---

## 2. Core Identity & Positioning Rules
When editing copy, metadata, or UI labels across this project, strictly adhere to these positioning guidelines:

* **Name & Role:** **Dan Marc Llanes** — *Solopreneur | AI Builder & App Developer for Small Businesses, Hotels & Rentals, and Clinics*[cite: 1].
* **Language & Tone:** **100% International English** (non-technical, outcome-focused, plain English). Never use Tagalog/local slang (e.g., avoid *utang*, *sari-sari*, *staycation*) or heavy corporate engineering jargon.
* **Call to Action Wording:** Say **"free consultation"** (short labels: "Consult"), never "audit", in all visible copy. Internal code names (`#audit-form`, `/api/audit`, `cta: 'audit'`) stay as they are.
* **Skill Priority:** Lead with **AI Building** (approval-first AI assistants, voice-to-note logging, document/catalog search, 24/7 FAQ helpers) first, followed by **App Development** (offline-first mobile & web apps)[cite: 1].
* **Experience Framing:**
  * Highlight **solo execution** for **LlanesLab** and the **5-App Product Venture**.
  * Mention **3 years of Data Engineering experience within enterprise teams** naturally as proof of data accuracy and clean reporting—do not over-highlight corporate titles or list specific former employer names[cite: 1, 2].
* **Audience Ordering:** Always order target industries and service items as:
  1. Retail Shops & Small Businesses (SMBs)
  2. Hotels, Resorts & Short-Term Rentals
  3. Clinics & Healthcare Practitioners *(always placed last)*

---

## 3. Two-Pillar Architecture
The site is structured around two distinct pillars under Dan's personal brand:

### Pillar 1: LlanesLab (Solo B2B Client Practice)
Custom AI helpers, booking workflows, internal dashboards, and offline-first apps built solo for SMBs, rentals, and clinics[cite: 1].
* **Important Domain Distinction:** Keep **Hotel & Short-Term Rental Bookings** (date-based check-in/out, room availability, double-booking prevention, deposits) separate from **Clinic & Appointment Scheduling** (slot-based booking, patient intake forms, no-show reminders, digital charting).
* **Selected Client Work:**
  1. Shop Operations & Inventory Dashboards[cite: 1]
  2. Delivery & Logistics Mobile App[cite: 1]
  3. AI Search Helpers for Real Estate & Interior Design[cite: 1]
  4. AI Clinical Notes & Digital Charting Tools for Doctors *(always listed last)*[cite: 1]

### Pillar 2: 5-App Product Venture (Built Solo from Scratch)
Do **not** invent unverified user counts, download numbers, or revenue claims. Maintain exact platform availability statuses:

| App | Category | iOS (Apple App Store) | Android (Google Play) |
| :--- | :--- | :--- | :--- |
| **Kalamooo** | Offline-First POS, Stock & Credit Ledger | Live | Live |
| **Folingoo** | AI English Speaking Coach | Live | Open Beta |
| **Roostart** | Stress-Free Habit Tracker | Live | Open Beta |
| **Owolot** | AI-Assisted Budget & Bill Planner | Live | Open Beta |
| **Otaroo** | 3-Second Food Journal & AI Meal Guide | Open Beta | Open Beta |

---

## 4. Contact & Conversion Details
* **Location:** Taguig City, Metro Manila, Philippines (Available Worldwide & Remote)[cite: 1]
* **Primary Email (Free Consultations & App Beta Invites):** `dandigital1688@gmail.com`
* **Secondary Email:** `llanesdanmarc@gmail.com`[cite: 1]
* **Phone / WhatsApp / Viber:** `(+63) 965-817-4121`[cite: 1]
* **Website:** `https://danmarcllanes.vercel.app` (canonical URL and share tags in `<head>`; link-preview image `public/og.jpg`, 1200×630, regenerate if the headline changes)
* **LinkedIn:** `https://linkedin.com/in/dan-marc-llanes-729416243`[cite: 1]
* **GitHub:** `https://github.com/dmarcllanes`[cite: 1]
* **Credentials:** AWS Certified Cloud Practitioner | BS in Information Technology (Jose Rizal University)[cite: 2]

---

## 5. Technical & UI Architecture (`index.html`)
* **Single-File Portable Setup:** Pure HTML5, Tailwind CSS (CDN), and vanilla ES6+ JavaScript with zero build step required.
* **Visual Theme:** Blue theme — deep navy canvas (`#060A14` / `#0C1322`, borders `#1E2B45`) with primary blue (`#3B82F6`; `#2563EB` for solid buttons with white text, `#60A5FA` for accent text), electric sky (`#38BDF8`), and emerald (`#10B981`, "Live" badges) accents. Each app in the 5-app previewer keeps its own brand colour. **Nebula background:** the fixed `.space` layer on `#04060F` holds five soft nebula clouds (blue top-left, violet/magenta right, teal bottom-left, magenta bottom-right, faint indigo centre) placed toward the screen edges so the centre where text sits stays dark. Clouds drift slowly using transform only, and the `.neb-wrap` shifts up slightly on scroll. Stars are two static CSS dot layers (one gently fades in and out). No canvas, no Milky Way band, no per-frame drawing; readability comes first. **Celestial objects** (inline SVG in `.space`, transform/opacity only): an original small starship with a flickering engine trail and blinking nav lights that crosses every ~40s, a violet-magenta ringed planet half off-screen bottom-right, a teal cratered moon top-left (hidden on mobile), a tiny orange planet top-right, slowly tumbling asteroids, and an occasional comet. Planets move up a little faster than the nebula on scroll (depth). The ship and comet are hidden for reduced motion. Keep these at the screen edges and small; never use a ship or object from an existing film, game or franchise. Cards stay solid navy for readability. Thin glowing dividers sit between sections. **No grid-line backgrounds.** Typography uses `Plus Jakarta Sans` (display), `Inter` (body), and `JetBrains Mono` (badges/metrics).
* **Editorial Layer:** Large tight-tracked headlines with one outlined phrase (`.text-outline`), numbered section heads `(01)`–`(06)` with a rule line, a crossed double marquee band under the hero, a stats strip (only verifiable numbers from this file), mascot "stickers" using the real app icons (`ICONS` in the script, filled into `img[data-icon]`), client-work cards with CSS mini-mockup thumbnails, and an oversized outlined name wordmark in the footer. Scroll & action effects are JS-added (content stays visible without JS) and all are off for reduced motion: staggered card reveals, section rule lines that draw in, stats that count up, a top reading-progress bar, a header that firms up on scroll, a slight parallax on the top glows, card hover glow (desktop), and a tap ripple on buttons. Keep them transform/opacity only.
* **Top Announcement Banner:** A nebula-tinted "NOW" signal ticker above the nav (`.topbar`; blue, violet and magenta glows on `#070818`, violet bottom edge): a fixed slanted blue-violet-pink "NOW" tag with a pulsing dot, then scrolling items, each led by a colour-coded mono tag (FREE green, LIVE blue, BETA amber, ASK violet, BASED grey), `//` separators, faded edges, a light sweep along the bottom edge, and a sliding underline on hover. It pauses on hover. Items: free consultation, Kalamooo live on both stores, Folingoo, Roostart & Owolot live on the App Store, Otaroo in open beta, "Ask Dan's AI assistant" (opens the chat), and location. The content appears twice (the second copy is `aria-hidden` + `inert`) for a seamless loop, so **edit both copies**. Its app statuses must match Section 3.
* **Builder Portrait:** The About section uses Dan's photo (`assets/me.png`) with the background removed, embedded as a 640px WebP data URI, on a blue gradient card with stickers. The nav avatar is a 96px face crop of the same photo, and the favicon is a circular crop of the same face. The favicon is embedded in `<head>` as a 64px PNG plus a 180px Apple touch icon, and also saved as `public/favicon.ico` for crawlers. If `assets/me.png` changes, regenerate all of them.
* **App Icons & Store Badges:** App icons are the real shipped iOS icons, embedded as 192px WebP data URIs. Store badges use the real Apple and Google Play logos with a "Live on" / "Open Beta on" line; keep them non-linked until real store URLs are provided.
* **3D & Mobile-First Rules:**
  * Desktop (`pointer: fine`): 3D perspective tilt (`perspective(1200px)`), dynamic cursor specular glare, and Z-depth floating badges (`translateZ`).
  * Mobile (`pointer: coarse` / `< 768px`): Disable hover-dependent 3D mouse tracking in favor of tactile spring-press feedback, `48px+` touch targets, sticky bottom navigation dock, and zero horizontal overflow.
* **Interactive Modules to Preserve:**
  1. **Hero Live AI Agent Demo (approval-first):** Mode switcher (*Shop*, *Rental*, *Clinic*). Keep the card compact. For each, an incoming request triggers an AI agent shown as a compact horizontal pipeline of 4 tool steps (e.g. Voice → Catalog → Stock → Ledger) with a one-line caption for the current step. It then shows a short draft marked "Not saved yet" with Approve / Edit / Reject. Data lives in the `SIM` object (`steps` + `output`). The hero positioning is custom AI assistants and AI agents that fit into the business workflow; anything important waits for approval.
  2. **LlanesLab Interactive Diagnostic & Admin Time-Saved Calculator:** Problem selector + weekly hours slider that pre-fills the free consultation form.
  3. **5-App Interactive Phone Screen Previewer & Beta Invite Modal:** Tabbed mobile screen mockups and one-click `mailto:` / copy-template beta signup wired to `dandigital1688@gmail.com`.
  4. **Click-for-Details Sheet:** Service, industry, client-work and app cards stay light; tapping one opens a details sheet (bottom sheet on mobile with swipe-down close, right drawer on desktop). Content lives in the `DETAILS` / `APP_MORE` objects in the script. Each sheet ends in a CTA that pre-fills the consultation form or opens the beta modal. Deep links use `#more-<key>` and the browser Back button closes the sheet. Stay single-page; add separate pages only for SEO case studies later.
  5. **"Ask about Dan" Chatbot:** Floating launcher with Dan's face (above the mobile dock), a full-screen panel on mobile and a 390px panel on desktop. Live answers come from `POST /api/chat` in `main.py` (Claude via the Anthropic SDK, grounded only in `chat_knowledge.py`). With no API key, no server, or a `file:` page, it answers from the offline `FAQ` in the script; app statuses come from `APPS`. **Keep `chat_knowledge.py` and the offline `FAQ` in sync with Sections 2–4.** The bot must never invent prices, timelines, user counts or employer names.

---

## 6. Editing & Verification Checklist
Before committing any changes to `index.html`:
1. Confirm zero Tagalog words or local-only terms remain.
2. Verify Clinics/Healthcare sections remain ordered after Retail/SMBs and Hotels/Rentals.
3. Verify App Store / Google Play Live vs. Open Beta badges match Section 3 above.
4. Test responsive layout at `375px` (mobile) and `1280px` (desktop) to ensure no horizontal scroll and working interactive modals/calculators.