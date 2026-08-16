# Project: NutriFresh Eggs Multi-Page Website

## Architecture
- **Architecture Type**: Modern, semantic multi-page static web application (HTML5, CSS3, vanilla JavaScript ES6+).
- **Design Language**: Faithful adaptation of Happy Egg brand identity:
  - Colors: Sunny Yellow (`#FFB71B`), Rich Yolk Amber (`#FF5700`), Deep Navy (`#081C30` / `#1A365D`), Eggshell Cream (`#FFFBF2` / `#FFFDF9`), Forest Green accents (`#2D6A4F`).
  - Typography: Poppins (headings), Inter (body/nutrition), Caveat (handwritten organic accents).
  - Geometry: Pill-shaped action buttons, 3D carton-style CTA buttons, organic curved wave SVG section dividers, morphing yolk dome representations.
- **Core Pages**:
  1. `index.html` (Home)
  2. `products.html` (Products Showcase)
  3. `our-farms.html` (Our Farms & Ethical Standards)
  4. `recipes.html` (Recipe Directory & Modal Detail)
  5. `store-locator.html` (Retail Store Finder & Interactive Map)
- **Shared Assets & Utilities**:
  - `styles.css` (Universal design system, variables, responsive grid, animations)
  - `app.js` (Modular vanilla JS component initialization)
  - `server.py` (Custom HTTP server with byte-range video streaming support)
  - `assets/` (Images, icons, fonts, and video files)

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Global Header & Navigation | Sticky header with scrolled state, brand logo, nav links (`index.html`, `products.html`, `our-farms.html`, `recipes.html`, `store-locator.html`), and "Find in Store" pill CTA. | M1 | Survey / Req R2 |
| 2 | Slideout Mobile Navigation Drawer | Hamburger trigger, slideout drawer, carton thumbnail shortcuts, social links, ESC and close-button dismiss. | M1 | Survey / Req R2 |
| 3 | Unified Footer & Legal Modals | Standardized Suregrow Farms footer, newsletter subscription, working modal/action bindings for legal links (no dead `#` anchors). | M1 | Survey / Req R1 |
| 4 | Brand Consistency & Favicons | Standardized logo references, favicon link tag `<link rel="icon">` on all pages, floating store CTA. | M1 | Survey / Req R1 |
| 5 | Hero Video Section & Audio Toggle | Preserved looping video `assets/videos/nutrifresh-hero.mp4`, audio mute/unmute toggle, fallback poster, hero CTAs. | M2 | Survey / Req R1 |
| 6 | Farm Integrity & Nutrition Cards | 4-pillar farm highlights, nutrition powerhouse grid, responsive layout. | M2 | Survey / Req R1 |
| 7 | Interactive Product Carousel | 4-card carton slider (Heritage, Pasture-Raised, Organic, Free-Range), responsive card count, navigation arrows. | M2 | Survey / Req R1 |
| 8 | 15-Grade Dynamic Yolk Slider | Interactive range slider (grades 1-15), dynamic RGB gradient and shadow computation, tier text descriptions. | M2 | Survey / Req R1 |
| 9 | Animated Stats Counters | IntersectionObserver-triggered animated count-up with decimal support for ethical farming metrics. | M2 | Survey / Req R1 |
| 10 | Home Recipe Teasers & Reviews | Curated recipe teaser cards routing directly to `recipes.html`, animated review quotes cloud. | M2 | Survey / Req R1 |
| 11 | Products Showcase & Deep Dives | 4 product detail sections (`#heritage`, `#pasture`, `#organic`, `#freerange`) with high-res carton imagery. | M3 | Survey / Req R1 |
| 12 | Nutritional Facts & Yolk Comparison | Nutritional facts tables, comparison pill tags, yolk quality breakdown, and "Where to Buy" direct links. | M3 | Survey / Req R1 |
| 13 | Our Farms Storytelling & Pasture Standards | Narrative on 21.8 sq ft outdoor space per bird, year-round pasture rotation, tree shade, and happy hen care. | M4 | Survey / Req R1 |
| 14 | Farmer Spotlights & Sustainability | Family farmer profile highlights, regenerative agriculture practices, organic feed integrity. | M4 | Survey / Req R1 |
| 15 | Recipe Directory & Category Filtering | Multi-category tab filtering (All, Brunch, Quick & Easy, Baking) with active button states and card transitions. | M5 | Survey / Req R1 |
| 16 | Recipe Search & Discovery | Real-time text search filter for recipes by title, ingredient, or prep time. | M5 | Survey / Req R1 |
| 17 | Interactive Recipe Modal Viewer | Dynamic modal popup with full recipe image, prep/cook time, difficulty, interactive ingredient checklist, and instructions. | M5 | Survey / Req R1 |
| 18 | Recipe Asset Paths Normalization | Fix broken image references in `recipes.html` and `app.js` with valid disk assets. | M5 | Survey / Defect |
| 19 | Store Locator Retail Search | ZIP code and City search input filtering sample supermarket and grocery store records with mock distance and hours. | M6 | Survey / Req R1 |
| 20 | Store Locator Carton Filters | Interactive filter buttons for carton types (All, Heritage, Pasture, Organic, Free-Range) dynamically updating store results. | M6 | Survey / Req R1 |
| 21 | Interactive Store Map View | Interactive SVG map with selectable pins, hover tooltips, and store card highlight synchronization. | M6 | Survey / Req R1 |
| 22 | Comprehensive E2E Test Suite | 4-tier automated test suite (Tiers 1-4) validating routing, assets, server HTTP 200/206, forms, and UI states. | E2E Track | Req R3 / Pattern |
| 23 | Adversarial Coverage Hardening | Tier 5 white-box stress testing, DOM edge cases, viewport extremes, and keyboard navigation. | M7 | Pattern |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2E | E2E Testing Suite Track | Test harness, test runners, Tiers 1-4 requirement-driven test cases, publishing `TEST_READY.md`. | none | IN_PROGRESS |
| M1 | Global Shell, Navigation & Design System | Standardize header nav (`recipes.html`), slideout drawer, footer branding, favicons, floating CTA, zero dead links. | none | IN_PROGRESS |
| M2 | Home Page High-Impact Polish | Hero video preservation, audio toggle, product carousel, 15-grade yolk slider, stats counters, recipe routing. | M1 | PLANNED |
| M3 | Products Page Showcase & Nutrition | Products showcase (`#heritage`, `#pasture`, `#organic`, `#freerange`), nutrition comparison, carton previews, buy CTAs. | M1 | PLANNED |
| M4 | Our Farms Storytelling & Standards | Ethical pasture standards (21.8 sq ft/bird), happy hen care, farmer spotlights, sustainability narrative. | M1 | PLANNED |
| M5 | Recipes Directory, Search & Modal | Image path fixes, category filter tabs, live search input, dynamic recipe modal with interactive ingredient checkboxes. | M1 | PLANNED |
| M6 | Store Locator Search & Map | ZIP/city search, carton filter buttons binding, store listing with distance/hours, interactive SVG map pins. | M1 | PLANNED |
| M7 | Final Milestone: E2E Pass & Tier 5 Hardening | Pass 100% E2E test suite (Tiers 1-4), Tier 5 adversarial testing, clean console audit, and local server run verification. | E2E, M1-M6 | PLANNED |

## Interface Contracts
### HTML Header Contract
- Top nav item "Recipes" must point to `recipes.html` on all 5 pages.
- Header must include `.header-nav`, `.drawer-toggle`, `.nav-cta` routing to `store-locator.html`.
- Mobile drawer `#navDrawer` must include navigation links, carton shortcuts, and close button `#drawerClose`.

### HTML Footer Contract
- All pages must use the standardized Suregrow Farms footer format with newsletter form `#footerNewsletter` and legal links triggering informative modal `#legalModal` or working routes.

### JavaScript Component Contract (`app.js`)
- `initHeader()`: Attaches scroll listener to `.header-nav`.
- `initDrawer()`: Manages `.drawer-toggle`, `#navDrawer`, `#drawerClose`, and `#drawerOverlay`.
- `initVideoHero()`: Controls `#heroVideo`, `#videoSoundBtn` without altering video source.
- `initProductCarousel()`: Controls `.carton-carousel`, `.carousel-prev`, `.carousel-next`.
- `initYolkSlider()`: Controls `#yolkRangeInput`, `.dynamic-yolk-dome`, `.yolk-grade-num`, `.yolk-desc`.
- `initStatsCounter()`: Observes `.stat-number` with data targets.
- `initRecipes()`: Manages `.filter-btn`, `#recipeSearchInput`, `.recipe-card`, `#recipeModalOverlay`.
- `initStoreLocator()`: Manages `#storeSearchInput`, `#storeSearchBtn`, `.locator-filters .filter-btn`, `.store-item`, `.map-pin`.
- `initLegalModals()`: Handles `#legalModal` display for privacy/terms/accessibility.

## Code Layout
- `index.html` — Home Page
- `products.html` — Products Page
- `our-farms.html` — Our Farms Page
- `recipes.html` — Recipes Page
- `store-locator.html` — Store Locator Page
- `styles.css` — Global Stylesheet
- `app.js` — Core JavaScript Logic
- `server.py` — Local HTTP Server (Port 3000)
- `assets/` — Images, SVGs, Videos (`assets/videos/nutrifresh-hero.mp4`)
- `tests/` — Automated E2E Test Suite & Runners
