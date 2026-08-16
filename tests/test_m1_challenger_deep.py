"""
Milestone 1 Adversarial Challenge & Empirical Verification Suite
Author: challenger_m1_1

Tests:
1. Shell Navigation & Link Targets:
   - Crawls all <a> tags in <header>, .slideout-drawer / #navDrawer, and <footer> across all 5 HTML pages.
   - Verifies 100% of internal routes exist on disk.
   - Verifies anchor fragment targets (#sectionId) exist in the target HTML file.
   - Verifies zero dead '#' or empty hrefs.
2. Asset Integrity:
   - Extracts all <img src>, <video poster>, <source src>, <link rel="icon" href> across all 5 HTML files.
   - Verifies all paths exist on disk and are non-empty (>0 bytes).
3. Shell Contract IDs:
   - Verifies #drawerOverlay, #navDrawer, #drawerClose, #menuToggle exist in all 5 HTML files.
4. Favicon Tags:
   - Verifies valid favicon link tag exists in <head> of all 5 HTML files.
5. JavaScript Syntax & Export Integrity:
   - Uses Node.js --check and syntax parsing on app.js and js/main.js.
   - Verifies all required component init functions exist.
6. Live HTTP Request Validation:
   - Fetches all 5 HTML pages and core assets from live server (http://127.0.0.1:3000).
"""

import os
import sys
import re
import urllib.parse
import urllib.request
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
HTML_PAGES = [
    "index.html",
    "products.html",
    "our-farms.html",
    "recipes.html",
    "store-locator.html"
]

class HTMLNode:
    def __init__(self, tag, attrs, parent=None):
        self.tag = tag.lower()
        self.attrs = {k.lower(): v for k, v in attrs}
        self.parent = parent
        self.children = []
        self.text_chunks = []

    def get_attr(self, name, default=None):
        return self.attrs.get(name.lower(), default)

    def has_class(self, cls):
        classes = self.attrs.get("class", "").split()
        return cls in classes

    def get_id(self):
        return self.attrs.get("id", "")

    def find_all(self, tag=None, class_name=None, id_name=None):
        results = []
        match = True
        if tag and self.tag != tag.lower():
            match = False
        if class_name and not self.has_class(class_name):
            match = False
        if id_name and self.get_id() != id_name:
            match = False
        if match and self.tag != "__root__":
            results.append(self)
        for c in self.children:
            results.extend(c.find_all(tag, class_name, id_name))
        return results


class PageParser(HTMLParser):
    SELF_CLOSING = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr',
        'circle', 'rect', 'path', 'line', 'polygon', 'polyline', 'stop', 'use'
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = HTMLNode("__root__", [])
        self.current = self.root
        self.all_ids = set()

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        node_id = attr_dict.get("id") or attr_dict.get("ID")
        if node_id:
            self.all_ids.add(node_id)
        node = HTMLNode(tag, attrs, parent=self.current)
        self.current.children.append(node)
        if tag.lower() not in self.SELF_CLOSING:
            self.current = node

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in self.SELF_CLOSING:
            return
        curr = self.current
        while curr and curr.tag != "__root__":
            if curr.tag == tag_lower:
                self.current = curr.parent if curr.parent else self.root
                return
            curr = curr.parent


def parse_page(page_name):
    path = BASE_DIR / page_name
    assert path.exists(), f"File {page_name} does not exist at {path}"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    parser = PageParser()
    parser.feed(content)
    return parser.root, parser.all_ids, content


class TestM1AdversarialChallenge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doms = {}
        cls.page_ids = {}
        cls.raw_html = {}
        for p in HTML_PAGES:
            root, ids, raw = parse_page(p)
            cls.doms[p] = root
            cls.page_ids[p] = ids
            cls.raw_html[p] = raw

    # -------------------------------------------------------------
    # 1. Crawl all <a> in <header>, .slideout-drawer / #navDrawer, <footer>
    # -------------------------------------------------------------
    def test_c1_01_header_nav_links_validity(self):
        """All <a> tags in <header> across all 5 pages have valid destinations."""
        dead_links = []
        checked_count = 0

        for page_name, dom in self.doms.items():
            headers = dom.find_all(tag="header")
            self.assertTrue(headers, f"{page_name} must have a <header>")
            for h in headers:
                links = h.find_all(tag="a")
                for a in links:
                    href = a.get_attr("href")
                    checked_count += 1
                    self.assertIsNotNone(href, f"Link in {page_name} header is missing href attribute: {a.attrs}")
                    self.assertNotEqual(href.strip(), "#", f"Dead link '#' found in {page_name} header: {a.attrs}")
                    self.assertNotEqual(href.strip(), "", f"Empty link found in {page_name} header: {a.attrs}")

                    # Resolve target
                    if href.startswith("http://") or href.startswith("https://") or href.startswith("tel:") or href.startswith("mailto:"):
                        continue
                    
                    parsed = urllib.parse.urlparse(href)
                    target_file = parsed.path if parsed.path else page_name
                    target_fragment = parsed.fragment

                    # Verify target file exists
                    target_path = BASE_DIR / target_file
                    if not target_path.exists():
                        dead_links.append(f"{page_name} header link '{href}' -> target file '{target_file}' missing on disk")
                        continue

                    # If fragment is specified, verify fragment exists in target file
                    if target_fragment and target_file in self.page_ids:
                        if target_fragment not in self.page_ids[target_file]:
                            dead_links.append(f"{page_name} header link '{href}' -> fragment #{target_fragment} not found in {target_file}")

        self.assertEqual(dead_links, [], f"Dead or broken header links detected: {dead_links}")
        print(f"\n[PASS] Checked {checked_count} header <a> links across all 5 pages. Zero broken links.")

    def test_c1_02_drawer_nav_links_validity(self):
        """All <a> tags in #navDrawer / .slideout-drawer across all 5 pages have valid destinations."""
        dead_links = []
        checked_count = 0

        for page_name, dom in self.doms.items():
            drawers = dom.find_all(class_name="slideout-drawer") + dom.find_all(id_name="navDrawer")
            self.assertTrue(drawers, f"{page_name} must contain .slideout-drawer / #navDrawer")
            
            seen_links = set()
            for drawer in drawers:
                links = drawer.find_all(tag="a")
                for a in links:
                    href = a.get_attr("href")
                    if not href:
                        dead_links.append(f"{page_name} drawer link missing href: {a.attrs}")
                        continue
                    if href in seen_links:
                        continue
                    seen_links.add(href)
                    checked_count += 1

                    self.assertNotEqual(href.strip(), "#", f"Dead link '#' found in {page_name} drawer: {a.attrs}")
                    self.assertNotEqual(href.strip(), "", f"Empty link found in {page_name} drawer: {a.attrs}")

                    if href.startswith("http://") or href.startswith("https://") or href.startswith("tel:") or href.startswith("mailto:"):
                        continue

                    parsed = urllib.parse.urlparse(href)
                    target_file = parsed.path if parsed.path else page_name
                    target_fragment = parsed.fragment

                    target_path = BASE_DIR / target_file
                    if not target_path.exists():
                        dead_links.append(f"{page_name} drawer link '{href}' -> target file '{target_file}' missing on disk")
                        continue

                    if target_fragment and target_file in self.page_ids:
                        if target_fragment not in self.page_ids[target_file]:
                            dead_links.append(f"{page_name} drawer link '{href}' -> fragment #{target_fragment} not found in {target_file}")

        self.assertEqual(dead_links, [], f"Dead or broken drawer links detected: {dead_links}")
        print(f"[PASS] Checked {checked_count} drawer <a> links across all 5 pages. Zero broken links.")

    def test_c1_03_footer_nav_links_validity(self):
        """All <a> tags and legal buttons in <footer> across all 5 pages have valid destinations / triggers."""
        dead_links = []
        checked_count = 0

        for page_name, dom in self.doms.items():
            footers = dom.find_all(tag="footer")
            self.assertTrue(footers, f"{page_name} must have a <footer>")
            for f in footers:
                links = f.find_all(tag="a")
                for a in links:
                    href = a.get_attr("href")
                    checked_count += 1
                    self.assertIsNotNone(href, f"Link in {page_name} footer missing href: {a.attrs}")
                    self.assertNotEqual(href.strip(), "#", f"Dead link '#' found in {page_name} footer: {a.attrs}")
                    self.assertNotEqual(href.strip(), "", f"Empty link found in {page_name} footer: {a.attrs}")

                    if href.startswith("http://") or href.startswith("https://") or href.startswith("tel:") or href.startswith("mailto:"):
                        continue

                    parsed = urllib.parse.urlparse(href)
                    target_file = parsed.path if parsed.path else page_name
                    target_fragment = parsed.fragment

                    target_path = BASE_DIR / target_file
                    if not target_path.exists():
                        dead_links.append(f"{page_name} footer link '{href}' -> target file '{target_file}' missing on disk")
                        continue

                    if target_fragment and target_file in self.page_ids:
                        if target_fragment not in self.page_ids[target_file]:
                            dead_links.append(f"{page_name} footer link '{href}' -> fragment #{target_fragment} not found in {target_file}")

                # Check legal buttons
                legal_btns = f.find_all(tag="button", class_name="legal-link-btn")
                for btn in legal_btns:
                    data_tab = btn.get_attr("data-legal-tab")
                    self.assertIn(data_tab, ["privacy", "terms", "accessibility", "cookies"],
                                  f"Invalid data-legal-tab in {page_name}: {data_tab}")

        self.assertEqual(dead_links, [], f"Dead or broken footer links detected: {dead_links}")
        print(f"[PASS] Checked {checked_count} footer <a> links across all 5 pages. Zero broken links.")

    # -------------------------------------------------------------
    # 2. All <img>, <video>, <source>, <link rel="icon"> assets exist on disk
    # -------------------------------------------------------------
    def test_c1_04_all_image_paths_exist_on_disk(self):
        """Every <img> src across all 5 HTML files exists on disk and is non-empty (>0 bytes)."""
        missing_images = []
        checked_images = 0

        for page_name, dom in self.doms.items():
            imgs = dom.find_all(tag="img")
            for img in imgs:
                src = img.get_attr("src")
                if not src:
                    missing_images.append(f"{page_name}: <img> tag missing src attribute: {img.attrs}")
                    continue
                checked_images += 1
                if src.startswith("data:") or src.startswith("http://") or src.startswith("https://"):
                    continue
                
                clean_src = src.split("?")[0].split("#")[0]
                img_path = BASE_DIR / clean_src
                if not img_path.exists():
                    missing_images.append(f"{page_name}: image not found on disk: '{src}' ({img_path})")
                elif img_path.stat().st_size == 0:
                    missing_images.append(f"{page_name}: image file is 0 bytes: '{src}'")

        self.assertEqual(missing_images, [], f"Broken image assets found: {missing_images}")
        print(f"[PASS] Checked {checked_images} <img> tags across all 5 pages. All exist on disk (>0 bytes).")

    def test_c1_05_all_media_and_icon_paths(self):
        """All video poster, video sources, and favicon icons exist and are non-empty."""
        missing_media = []

        for page_name, dom in self.doms.items():
            # Videos
            videos = dom.find_all(tag="video")
            for v in videos:
                poster = v.get_attr("poster")
                if poster and not poster.startswith("http"):
                    p_path = BASE_DIR / poster
                    if not p_path.exists() or p_path.stat().st_size == 0:
                        missing_media.append(f"{page_name} video poster '{poster}' missing/empty")

            # Sources
            sources = dom.find_all(tag="source")
            for s in sources:
                src = s.get_attr("src")
                if src and not src.startswith("http"):
                    s_path = BASE_DIR / src
                    if not s_path.exists() or s_path.stat().st_size == 0:
                        missing_media.append(f"{page_name} source '{src}' missing/empty")

            # Favicon links
            links = dom.find_all(tag="link")
            for l in links:
                rel = l.get_attr("rel", "")
                if "icon" in rel:
                    href = l.get_attr("href")
                    if href and not href.startswith("http"):
                        f_path = BASE_DIR / href
                        if not f_path.exists() or f_path.stat().st_size == 0:
                            missing_media.append(f"{page_name} favicon '{href}' missing/empty")

        self.assertEqual(missing_media, [], f"Broken media or icon assets: {missing_media}")
        print("[PASS] All video poster, video sources, and favicon icon files verified on disk.")

    # -------------------------------------------------------------
    # 3. Slideout Drawer Contract IDs
    # -------------------------------------------------------------
    def test_c1_06_drawer_contract_ids(self):
        """Contract IDs (#drawerOverlay, #navDrawer, #drawerClose, #menuToggle) exist in all 5 files."""
        for page_name, ids in self.page_ids.items():
            dom = self.doms[page_name]
            self.assertIn("drawerOverlay", ids, f"Missing #drawerOverlay in {page_name}")
            self.assertIn("navDrawer", ids, f"Missing #navDrawer in {page_name}")
            self.assertIn("drawerClose", ids, f"Missing #drawerClose in {page_name}")
            
            # #menuToggle or .drawer-toggle
            has_toggle = ("menuToggle" in ids) or len(dom.find_all(class_name="drawer-toggle")) > 0 or len(dom.find_all(class_name="menu-toggle")) > 0
            self.assertTrue(has_toggle, f"Missing drawer toggle button in {page_name}")

            # Verify drawer carton shortcuts exist
            drawer = dom.find_all(id_name="navDrawer")[0]
            carton_links = drawer.find_all(class_name="drawer-carton-item")
            self.assertEqual(len(carton_links), 4, f"{page_name} drawer must have exactly 4 carton shortcuts")

        print("[PASS] Drawer contract IDs and structure verified across all 5 pages.")

    # -------------------------------------------------------------
    # 4. Favicon Tags in <head>
    # -------------------------------------------------------------
    def test_c1_07_favicon_in_head(self):
        """Favicon tag exists in <head> across all 5 HTML pages."""
        for page_name, raw in self.raw_html.items():
            head_match = re.search(r'<head>(.*?)</head>', raw, re.DOTALL | re.IGNORECASE)
            self.assertIsNotNone(head_match, f"{page_name} is missing a <head> block")
            head_content = head_match.group(1)
            
            favicon_match = re.search(r'<link[^>]+rel=["\'](?:shortcut )?icon["\'][^>]*>', head_content, re.IGNORECASE)
            self.assertIsNotNone(favicon_match, f"{page_name} <head> is missing favicon <link rel='icon'>")

            # Check that href is assets/favicon-icon.png or valid file
            href_match = re.search(r'href=["\']([^"\']+)["\']', favicon_match.group(0))
            self.assertIsNotNone(href_match, f"{page_name} favicon link tag missing href")
            fav_path = BASE_DIR / href_match.group(1)
            self.assertTrue(fav_path.exists(), f"{page_name} favicon file does not exist at {fav_path}")

        print("[PASS] Favicon <link rel='icon'> verified in <head> across all 5 HTML files.")

    # -------------------------------------------------------------
    # 5. JavaScript Syntax & Component Function Checks
    # -------------------------------------------------------------
    def test_c1_08_js_syntax_validation(self):
        """Validate JavaScript syntax of app.js and js/main.js using Node.js."""
        js_files = [BASE_DIR / "app.js", BASE_DIR / "js" / "main.js"]
        for js_file in js_files:
            if not js_file.exists():
                continue
            proc = subprocess.run(
                ["node", "--check", str(js_file)],
                capture_output=True,
                text=True
            )
            self.assertEqual(proc.returncode, 0, f"JS Syntax Error in {js_file.name}:\n{proc.stderr}")

        # Check required component initialization functions in app.js
        with open(BASE_DIR / "app.js", "r", encoding="utf-8") as f:
            app_js = f.read()

        required_funcs = [
            "initHeader",
            "initDrawer",
            "initLegalModals",
            "initNewsletter"
        ]
        for func in required_funcs:
            self.assertIn(func, app_js, f"app.js missing required component function: {func}")

        print("[PASS] JavaScript syntax validation passed cleanly with 0 syntax errors.")

    # -------------------------------------------------------------
    # 6. Global Footer, Legal Modal, & Newsletter Contracts
    # -------------------------------------------------------------
    def test_c1_09_footer_and_legal_modal_contracts(self):
        """Verify unified Suregrow Farms footer, legal modal tabs, and newsletter elements."""
        for page_name, dom in self.doms.items():
            raw = self.raw_html[page_name]
            # Suregrow Farms branding
            self.assertIn("SUREGROW FARMS", raw.upper(), f"{page_name} missing Suregrow Farms footer branding")
            
            # Legal modal
            self.assertIn("legalModal", self.page_ids[page_name], f"{page_name} missing #legalModal")
            self.assertIn("footerNewsletter", self.page_ids[page_name], f"{page_name} missing #footerNewsletter")
            self.assertIn("newsletterEmail", self.page_ids[page_name], f"{page_name} missing #newsletterEmail")

        print("[PASS] Footer, legal modal, and newsletter contract IDs verified across all 5 pages.")

    # -------------------------------------------------------------
    # 7. Live HTTP Status Check on Server
    # -------------------------------------------------------------
    def test_c1_10_live_http_server_endpoints(self):
        """Check all 5 HTML pages, CSS, JS, and key assets respond with HTTP 200 via live server."""
        base_url = "http://127.0.0.1:3000"
        endpoints = [
            "/index.html",
            "/products.html",
            "/our-farms.html",
            "/recipes.html",
            "/store-locator.html",
            "/styles.css",
            "/app.js",
            "/assets/favicon-icon.png",
            "/assets/images/nutrifresh-logo-hires.png",
            "/assets/images/heritage-carton.jpg",
            "/assets/images/pasture-carton.jpg",
            "/assets/images/organic-carton.jpg",
            "/assets/images/freerange-carton.jpg"
        ]

        for ep in endpoints:
            url = f"{base_url}{ep}"
            req = urllib.request.Request(url, headers={"User-Agent": "NutriFreshChallenger/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=3) as resp:
                    self.assertEqual(resp.status, 200, f"Expected 200 for {url}, got {resp.status}")
                    body = resp.read()
                    self.assertGreater(len(body), 0, f"Response for {url} is empty")
            except Exception as e:
                self.fail(f"HTTP request to {url} failed: {e}")

        print(f"[PASS] All {len(endpoints)} live HTTP endpoints returned 200 OK.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
