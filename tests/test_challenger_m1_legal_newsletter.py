"""
Adversarial Stress Testing Suite for Milestone 1
Target: Legal Modal and Newsletter Validation Systems
Author: Challenger M1_2
"""

import os
import sys
import re
import json
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

from tests.test_helper import parse_html, DOMNode

HTML_FILES = [
    'index.html',
    'products.html',
    'our-farms.html',
    'recipes.html',
    'store-locator.html'
]

class TestNewsletterValidationBattery(unittest.TestCase):
    """Adversarial stress testing of email validation regex & submission flow."""

    def setUp(self):
        # Extract the exact regex used in app.js
        app_js_path = os.path.join(BASE_DIR, 'app.js')
        with open(app_js_path, 'r', encoding='utf-8') as f:
            self.app_js_content = f.read()

        match = re.search(r'const\s+emailRegex\s*=\s*(/[^/]+/);', self.app_js_content)
        self.assertIsNotNone(match, "Could not find emailRegex in app.js")
        regex_literal = match.group(1)
        # Convert JS regex literal /pattern/ to Python re pattern
        pattern = regex_literal.strip('/')
        self.email_regex = re.compile(pattern)

    def test_01_valid_email_battery(self):
        """Test battery of diverse valid email formats."""
        valid_emails = [
            "user@example.com",
            "first.last@domain.co.uk",
            "name+tag@sub.domain.org",
            "farmer_joe123@suregrowfarms.com",
            "customer-support@nutrifresheggs.net",
            "eggs.order-123@store.market.com",
            "123456@numericlocal.com",
            "a@b.cd",
            "very.long.email.address.with.many.dots@deeply.nested.domain.example.com",
            "sunrise.breakfast_club+2026@eggs-direct.farm"
        ]
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(
                    bool(self.email_regex.search(email)),
                    f"Valid email '{email}' failed regex check"
                )

    def test_02_invalid_email_missing_at_battery(self):
        """Test invalid emails missing the @ symbol."""
        invalid_no_at = [
            "plainaddress",
            "user.domain.com",
            "www.nutrifresheggs.com",
            "customer#domain.com"
        ]
        for email in invalid_no_at:
            with self.subTest(email=email):
                self.assertFalse(
                    bool(self.email_regex.search(email)),
                    f"Invalid email '{email}' (missing @) incorrectly passed regex"
                )

    def test_03_invalid_email_missing_domain_or_tld(self):
        """Test invalid emails missing domain or dot/TLD."""
        invalid_domains = [
            "user@",
            "@domain.com",
            "user@domain",
            "user@domain.",
            "user@.com",
            "@",
            "@."
        ]
        for email in invalid_domains:
            with self.subTest(email=email):
                self.assertFalse(
                    bool(self.email_regex.search(email)),
                    f"Invalid email '{email}' (malformed domain/TLD) incorrectly passed regex"
                )

    def test_04_invalid_email_whitespace_and_special(self):
        """Test invalid emails with whitespace or multiple @ symbols."""
        invalid_whitespace = [
            "user @example.com",
            "user@ example.com",
            "user@example .com",
            "user@example. com",
            "user name@domain.com",
            "user\t@domain.com",
            "user\n@domain.com",
            "user@@example.com",
            "user@name@domain.com"
        ]
        for email in invalid_whitespace:
            with self.subTest(email=email):
                self.assertFalse(
                    bool(self.email_regex.search(email)),
                    f"Invalid email with whitespace/multiple @ '{email}' incorrectly passed regex"
                )

    def test_05_xss_injection_payloads(self):
        """Test XSS injection strings against email validation regex."""
        xss_payloads = [
            "<script>alert(1)</script>",
            "\"><script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "user<script>@domain.com",
            "javascript:alert(1)@domain.com",  # Note: contains colon and invalid TLD without dot
            "onclick=alert(1)@test.com",        # Note: local part has no whitespace, but let's test how DOM handles it
            "payload@<script>alert(1)</script>.com",
            "'\"><svg/onload=confirm(1)>@domain.com"
        ]
        for payload in xss_payloads:
            with self.subTest(payload=payload):
                # If script tags contain spaces, angle brackets, or illegal chars:
                if " " in payload or "<" in payload or ">" in payload:
                    self.assertFalse(
                        bool(self.email_regex.search(payload)),
                        f"XSS payload '{payload}' incorrectly passed email regex"
                    )

    def test_06_simulated_form_validation_flow(self):
        """Simulate initNewsletter validation states: empty input, invalid format, success."""
        def simulate_submit(email_str):
            email = email_str.strip() if email_str else ''
            if not email:
                return {
                    "status": "error_empty",
                    "msg": "Please enter an email address.",
                    "storage_saved": False
                }
            if not bool(self.email_regex.search(email)):
                return {
                    "status": "error_invalid",
                    "msg": "Please enter a valid email address (e.g. name@domain.com).",
                    "storage_saved": False
                }
            return {
                "status": "success",
                "msg": "Welcome to the flock!",
                "storage_saved": True,
                "saved_email": email
            }

        # 1. Empty string
        res_empty = simulate_submit("")
        self.assertEqual(res_empty["status"], "error_empty")
        self.assertFalse(res_empty["storage_saved"])

        # 2. Whitespace string
        res_spaces = simulate_submit("   \t  ")
        self.assertEqual(res_spaces["status"], "error_empty")
        self.assertFalse(res_spaces["storage_saved"])

        # 3. Invalid email
        res_bad = simulate_submit("notanemail")
        self.assertEqual(res_bad["status"], "error_invalid")
        self.assertFalse(res_bad["storage_saved"])

        # 4. Valid email with leading/trailing spaces (properly trimmed)
        res_valid = simulate_submit("  fresh.eggs@nutrifresh.com  ")
        self.assertEqual(res_valid["status"], "success")
        self.assertTrue(res_valid["storage_saved"])
        self.assertEqual(res_valid["saved_email"], "fresh.eggs@nutrifresh.com")


class TestLegalModalStructureAcrossAllPages(unittest.TestCase):
    """Stress test the presence, IDs, tab panels, and ARIA markup of #legalModal across all 5 HTML files."""

    def test_01_legal_modal_presence_in_all_5_html_files(self):
        """Verify #legalModal exists in all 5 HTML files."""
        for filename in HTML_FILES:
            filepath = os.path.join(BASE_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            dom = parse_html(content)
            modal = dom.find_all(id_name='legalModal')
            self.assertEqual(
                len(modal), 1,
                f"File {filename} must have exactly one element with id='legalModal'"
            )
            modal_node = modal[0]
            self.assertEqual(modal_node.get_attr('role'), 'dialog')
            self.assertEqual(modal_node.get_attr('aria-modal'), 'true')
            self.assertEqual(modal_node.get_attr('aria-labelledby'), 'legalModalTitle')

    def test_02_all_4_tabs_and_panels_present(self):
        """Verify all 4 tabs (privacy, terms, accessibility, cookies) and panels exist in all 5 files."""
        expected_tabs = ['privacy', 'terms', 'accessibility', 'cookies']
        expected_panels = ['tabPanelPrivacy', 'tabPanelTerms', 'tabPanelAccessibility', 'tabPanelCookies']

        for filename in HTML_FILES:
            filepath = os.path.join(BASE_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            dom = parse_html(content)

            # Check tab buttons
            tab_buttons = dom.find_all(class_name='legal-tab-btn')
            self.assertEqual(
                len(tab_buttons), 4,
                f"File {filename} should have 4 legal-tab-btn buttons, found {len(tab_buttons)}"
            )

            found_tabs = [btn.get_attr('data-tab') for btn in tab_buttons]
            self.assertEqual(
                found_tabs, expected_tabs,
                f"File {filename} tab data-tab values do not match expected: {found_tabs} vs {expected_tabs}"
            )

            # Check tab panels
            tab_panels = dom.find_all(class_name='legal-tab-panel')
            self.assertEqual(
                len(tab_panels), 4,
                f"File {filename} should have 4 legal-tab-panel divs, found {len(tab_panels)}"
            )

            found_panel_ids = [p.get_id() for p in tab_panels]
            self.assertEqual(
                found_panel_ids, expected_panels,
                f"File {filename} panel IDs do not match expected: {found_panel_ids} vs {expected_panels}"
            )

            # Verify close buttons
            close_btn = dom.find_all(id_name='closeLegalModal')
            dismiss_btn = dom.find_all(id_name='dismissLegalModalBtn')
            self.assertEqual(len(close_btn), 1, f"File {filename} missing #closeLegalModal")
            self.assertEqual(len(dismiss_btn), 1, f"File {filename} missing #dismissLegalModalBtn")


class TestFooterLegalTriggerButtons(unittest.TestCase):
    """Stress test footer legal buttons and their data-legal-tab attributes."""

    def test_01_footer_legal_links_and_tabs(self):
        """Verify all footer legal links have valid data-legal-tab targeting valid panels."""
        valid_tabs = {'privacy', 'terms', 'accessibility', 'cookies'}

        for filename in HTML_FILES:
            filepath = os.path.join(BASE_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            dom = parse_html(content)

            # Find footer legal buttons
            footer_legal_links = dom.find_all(class_name='legal-link-btn')
            self.assertGreaterEqual(
                len(footer_legal_links), 4,
                f"File {filename} footer should have at least 4 legal link buttons, found {len(footer_legal_links)}"
            )

            found_tabs = set()
            for btn in footer_legal_links:
                tab_target = btn.get_attr('data-legal-tab')
                self.assertIsNotNone(
                    tab_target,
                    f"File {filename} legal button missing data-legal-tab: {btn.attrs}"
                )
                self.assertIn(
                    tab_target, valid_tabs,
                    f"File {filename} data-legal-tab '{tab_target}' is not a valid legal tab"
                )
                found_tabs.add(tab_target)

            self.assertEqual(
                found_tabs, valid_tabs,
                f"File {filename} does not have footer triggers for all 4 legal tabs. Found: {found_tabs}"
            )

    def test_02_zero_dead_links_in_footer(self):
        """Verify footer contains zero dead href='#' links."""
        for filename in HTML_FILES:
            filepath = os.path.join(BASE_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            dom = parse_html(content)

            footer = dom.find_all(tag='footer')
            self.assertTrue(len(footer) >= 1, f"File {filename} missing <footer>")
            footer_node = footer[0]

            links = footer_node.find_all(tag='a')
            for link in links:
                href = link.get_attr('href', '')
                # Dead links are href="#" without modal id or empty href
                self.assertNotEqual(
                    href, '#',
                    f"File {filename} footer contains dead link href='#': {link.attrs}"
                )
                self.assertNotEqual(
                    href, '',
                    f"File {filename} footer contains empty href='': {link.attrs}"
                )


class TestCSSModalAnimationsAndZIndex(unittest.TestCase):
    """Stress test CSS classes, z-index layering, animations, and modal responsiveness."""

    def setUp(self):
        css_path = os.path.join(BASE_DIR, 'styles.css')
        with open(css_path, 'r', encoding='utf-8') as f:
            self.css_content = f.read()

    def test_01_z_index_hierarchy(self):
        """Verify z-index layering: modal (3000) > drawer (2001) > drawer overlay (2000) > header (1000) > floating cta (990)."""
        header_z = re.search(r'\.site-header\s*\{[^}]*z-index:\s*(\d+)', self.css_content)
        drawer_overlay_z = re.search(r'\.drawer-overlay\s*\{[^}]*z-index:\s*(\d+)', self.css_content)
        drawer_z = re.search(r'\.slideout-drawer\s*\{[^}]*z-index:\s*(\d+)', self.css_content)
        modal_z = re.search(r'\.legal-modal-overlay\s*\{[^}]*z-index:\s*(\d+)', self.css_content)
        floating_cta_z = re.search(r'\.floating-cta-btn[^{]*\{[^}]*z-index:\s*(\d+)', self.css_content)

        self.assertIsNotNone(header_z, "Could not find z-index for .site-header")
        self.assertIsNotNone(drawer_overlay_z, "Could not find z-index for .drawer-overlay")
        self.assertIsNotNone(drawer_z, "Could not find z-index for .slideout-drawer")
        self.assertIsNotNone(modal_z, "Could not find z-index for .legal-modal-overlay")
        self.assertIsNotNone(floating_cta_z, "Could not find z-index for .floating-cta-btn")

        val_header = int(header_z.group(1))
        val_drawer_overlay = int(drawer_overlay_z.group(1))
        val_drawer = int(drawer_z.group(1))
        val_modal = int(modal_z.group(1))
        val_floating_cta = int(floating_cta_z.group(1))

        self.assertEqual(val_header, 1000)
        self.assertEqual(val_drawer_overlay, 2000)
        self.assertEqual(val_drawer, 2001)
        self.assertEqual(val_modal, 3000)
        self.assertEqual(val_floating_cta, 990)

        # Hierarchy verification
        self.assertGreater(val_modal, val_drawer, "Modal z-index must be higher than slideout drawer")
        self.assertGreater(val_modal, val_drawer_overlay, "Modal z-index must be higher than drawer overlay")
        self.assertGreater(val_modal, val_header, "Modal z-index must be higher than header")
        self.assertGreater(val_drawer, val_header, "Drawer z-index must be higher than header")
        self.assertGreater(val_header, val_floating_cta, "Header z-index must be higher than floating CTA")

    def test_02_modal_animations_and_classes(self):
        """Verify modal animation transitions and keyframes exist in styles.css."""
        self.assertIn('.legal-modal-overlay', self.css_content)
        self.assertIn('.legal-modal-overlay.active', self.css_content)
        self.assertIn('.legal-modal-card', self.css_content)
        self.assertIn('.legal-modal-overlay.active .legal-modal-card', self.css_content)
        self.assertIn('@keyframes legalFadeIn', self.css_content)
        self.assertIn('.legal-tab-panel.active', self.css_content)

    def test_03_modal_card_responsiveness_and_scroll(self):
        """Verify .legal-modal-card has max-height, max-width, and .legal-modal-body has overflow-y: auto."""
        self.assertRegex(self.css_content, r'\.legal-modal-card\s*\{[^}]*max-height:\s*88vh')
        self.assertRegex(self.css_content, r'\.legal-modal-card\s*\{[^}]*max-width:\s*820px')
        self.assertRegex(self.css_content, r'\.legal-modal-body\s*\{[^}]*overflow-y:\s*auto')


class TestCookiePreferenceStorageKeysAndDefaults(unittest.TestCase):
    """Stress test cookie preference storage keys, defaults, and app.js handlers."""

    def setUp(self):
        app_js_path = os.path.join(BASE_DIR, 'app.js')
        with open(app_js_path, 'r', encoding='utf-8') as f:
            self.app_js_content = f.read()

    def test_01_cookie_storage_key_and_schema(self):
        """Verify localStorage cookie preference key name and schema serialization."""
        self.assertIn("localStorage.getItem('nutrifresh_cookies')", self.app_js_content)
        self.assertIn("localStorage.setItem('nutrifresh_cookies'", self.app_js_content)
        
        # Verify JSON structure contains essential: true, analytics, marketing, savedAt
        self.assertIn("essential: true", self.app_js_content)
        self.assertIn("analytics", self.app_js_content)
        self.assertIn("marketing", self.app_js_content)
        self.assertIn("savedAt: new Date().toISOString()", self.app_js_content)

    def test_02_html_cookie_toggle_elements_and_defaults(self):
        """Verify cookie toggle checkboxes exist in all 5 HTML files with proper IDs and default checked state."""
        for filename in HTML_FILES:
            filepath = os.path.join(BASE_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            dom = parse_html(content)

            an_input = dom.find_all(id_name='cookieAnalyticsToggle')
            mk_input = dom.find_all(id_name='cookieMarketingToggle')
            save_btn = dom.find_all(id_name='saveCookiePreferencesBtn')
            accept_btn = dom.find_all(id_name='acceptAllCookiesBtn')
            feedback_el = dom.find_all(id_name='cookieFeedbackMsg')

            self.assertEqual(len(an_input), 1, f"File {filename} missing #cookieAnalyticsToggle")
            self.assertEqual(len(mk_input), 1, f"File {filename} missing #cookieMarketingToggle")
            self.assertEqual(len(save_btn), 1, f"File {filename} missing #saveCookiePreferencesBtn")
            self.assertEqual(len(accept_btn), 1, f"File {filename} missing #acceptAllCookiesBtn")
            self.assertEqual(len(feedback_el), 1, f"File {filename} missing #cookieFeedbackMsg")

            # Check defaults
            self.assertTrue(an_input[0].has_attr('checked'), f"File {filename} cookieAnalyticsToggle should default to checked")
            self.assertTrue(mk_input[0].has_attr('checked'), f"File {filename} cookieMarketingToggle should default to checked")

    def test_03_cookie_preference_simulation(self):
        """Simulate saving and loading cookie preferences in JSON format."""
        def save_cookies(analytics: bool, marketing: bool):
            return json.dumps({
                "essential": True,
                "analytics": analytics,
                "marketing": marketing,
                "savedAt": "2026-08-16T14:00:00.000Z"
            })

        # Save customized preferences
        prefs_json = save_cookies(analytics=False, marketing=True)
        parsed = json.loads(prefs_json)

        self.assertTrue(parsed["essential"])
        self.assertFalse(parsed["analytics"])
        self.assertTrue(parsed["marketing"])
        self.assertIn("savedAt", parsed)

        # Accept all
        all_json = save_cookies(analytics=True, marketing=True)
        all_parsed = json.loads(all_json)
        self.assertTrue(all_parsed["essential"])
        self.assertTrue(all_parsed["analytics"])
        self.assertTrue(all_parsed["marketing"])


if __name__ == '__main__':
    unittest.main()
