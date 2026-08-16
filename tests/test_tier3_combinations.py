"""
Tier 3: Cross-Feature Combination & Deep Integration Tests (16 Tests)
Validates deep links, state preservation, cross-page metric consistency,
simultaneous filters, and streaming under simulated user interaction.
"""

import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from tests.test_helper import E2ETestBase, DOMQueryEngine, JSSimulator
except ImportError:
    from test_helper import E2ETestBase, DOMQueryEngine, JSSimulator


class TestTier3_Combinations(E2ETestBase):
    """Tier 3: Cross-Feature Combinations & State Transitions"""

    def test_t3_01_carousel_details_deep_link_to_products_heritage(self):
        """Carousel 'Details' on Heritage card deep links to products.html#heritage"""
        dom_home = self.client.parse_dom('index.html')
        card = dom_home.select_one('.carousel-track .product-card')
        details_link = card.find(class_name='btn-outline')
        self.assertEqual(details_link.get_attr('href'), 'products.html#heritage')

        dom_prod = self.client.parse_dom('products.html')
        heritage_target = dom_prod.select_one('#heritage')
        self.assertIsNotNone(heritage_target, "Target #heritage must exist on products.html")
        self.assertIn("Heritage", heritage_target.text)
        self.assertIn("Grade 15", heritage_target.text)

    def test_t3_02_yolk_slider_to_store_locator_cta_handoff(self):
        """Yolk slider Grade 15 tier aligns with store locator carton availability"""
        tier_info = JSSimulator.get_yolk_tier_info(15)
        self.assertIn("Grade 15", tier_info['title'])

        dom_store = self.client.parse_dom('store-locator.html')
        self.assertDOMExists(dom_store, '#storeSearchInput')

        sample_stores = [
            {'name': 'Whole Foods Market', 'address': '450 Natural Grove Way', 'city': 'Austin, TX 78701', 'dist': '0.8 miles', 'stock': 'In Stock (All Cartons)'}
        ]
        results = JSSimulator.filter_stores_by_carton(sample_stores, 'Heritage Amber')
        self.assertEqual(len(results), 1)

    def test_t3_03_home_recipe_teaser_to_recipe_modal_flow(self):
        """Home recipe teasers align with recipes directory and modal structures"""
        dom_home = self.client.parse_dom('index.html')
        teasers = dom_home.select('.recipes-section .recipe-card')
        self.assertEqual(len(teasers), 3)

        dom_recipes = self.client.parse_dom('recipes.html')
        cards = dom_recipes.select('#recipeCardsGrid .recipe-card')
        self.assertEqual(len(cards), 6)

    def test_t3_04_store_locator_filter_plus_search_combination(self):
        """Filter by 'Heritage Amber' carton and search '78701'"""
        sample_stores = [
            {'name': 'Whole Foods Market', 'address': '450 Natural Grove Way', 'city': 'Austin, TX 78701', 'dist': '0.8 miles', 'stock': 'In Stock (All Cartons)'},
            {'name': 'Sprouts Farmers Market', 'address': '1280 Green Valley Rd', 'city': 'Austin, TX 78704', 'dist': '1.4 miles', 'stock': 'In Stock (Heritage & Pasture)'},
            {'name': 'Kroger Fresh Market', 'address': '2100 Farmcrest Blvd', 'city': 'Austin, TX 78745', 'dist': '2.1 miles', 'stock': 'In Stock (Organic Free Range)'},
            {'name': 'Target Supercenter', 'address': '500 E Stassney Ln', 'city': 'Austin, TX 78745', 'dist': '3.5 miles', 'stock': 'In Stock (Pasture Raised)'},
            {'name': 'Trader Joe’s Market', 'address': '2805 Bee Caves Rd', 'city': 'Austin, TX 78746', 'dist': '4.2 miles', 'stock': 'In Stock (Heritage Amber)'}
        ]
        carton_filtered = JSSimulator.filter_stores_by_carton(sample_stores, 'Heritage Amber')
        self.assertEqual(len(carton_filtered), 3)

        search_filtered = JSSimulator.search_stores(carton_filtered, '78701')
        self.assertEqual(len(search_filtered), 1)
        self.assertEqual(search_filtered[0]['name'], 'Whole Foods Market')

    def test_t3_05_mobile_drawer_open_and_carton_shortcut_navigation(self):
        """Drawer carton shortcut for Pasture Raised jumps to products.html#pasture"""
        dom_home = self.client.parse_dom('index.html')
        pasture_shortcut = dom_home.select_one('.drawer-cartons-grid a[href="products.html#pasture"]')
        self.assertIsNotNone(pasture_shortcut)

        dom_prod = self.client.parse_dom('products.html')
        section = dom_prod.select_one('#pasture')
        self.assertIsNotNone(section)
        self.assertIn("Pasture", section.text)

    def test_t3_06_video_sound_toggle_and_hero_cta_interaction(self):
        """Video sound toggle does not disrupt hero CTA destination"""
        dom_home = self.client.parse_dom('index.html')
        toggle = dom_home.select_one('.hero-sound-toggle')
        cta = dom_home.select_one('.hero-actions a.btn-primary') or dom_home.select_one('.hero-video-section a.btn-primary')
        self.assertIsNotNone(toggle)
        self.assertIsNotNone(cta)
        self.assertEqual(cta.get_attr('href'), 'store-locator.html')

    def test_t3_07_recipes_category_tab_plus_detail_modal_open(self):
        """Filter by 'Weekend Brunch' tab and verify Benedict modal data"""
        sample_recipes = [
            {'id': 'benedict', 'title': 'Sunset Amber Eggs Benedict', 'category': 'brunch'},
            {'id': 'tacos', 'title': 'Pasture Breakfast Tacos', 'category': 'quick'},
            {'id': 'shakshuka', 'title': 'Cast-Iron Farm Shakshuka', 'category': 'brunch'}
        ]
        brunch = JSSimulator.filter_recipes(sample_recipes, 'brunch')
        self.assertEqual(len(brunch), 2)
        benedict = [r for r in brunch if r['id'] == 'benedict'][0]

        resp = self.client.get('app.js')
        self.assertIn("Sunset Amber Eggs Benedict", resp.text)
        self.assertIn("4 Nutrifresh Heritage Breed eggs", resp.text)

    def test_t3_08_store_map_pin_selection_and_store_card_sync(self):
        """5 SVG map pins align with the 5 sample store records"""
        dom_store = self.client.parse_dom('store-locator.html')
        pins = dom_store.select('svg.map-svg-mockup .map-pin')
        self.assertEqual(len(pins), 5)
        for i, pin in enumerate(pins, 1):
            num_text = pin.find(tag='text')
            self.assertEqual(num_text.text, str(i))

    def test_t3_09_footer_newsletter_submit_and_page_stability(self):
        """Newsletter form onsubmit has event.preventDefault() and confirmation message"""
        resp = self.client.get('app.js')
        self.assertIn("e.preventDefault()", resp.text)
        self.assertIn("Welcome to the flock", resp.text)

    def test_t3_10_stats_counter_scroll_plus_brand_card_render(self):
        """Stats counter targets and brand card image load together on index.html"""
        dom_home = self.client.parse_dom('index.html')
        brand_card = dom_home.select_one('.official-brand-card-img')
        resp = self.client.get(brand_card.get_attr('src'))
        self.assertHttpStatus(resp, 200)

        counters = dom_home.select('.stat-counter-num')
        self.assertEqual(len(counters), 4)

    def test_t3_11_products_nutrition_pill_consistency_with_yolk_slider(self):
        """Heritage nutrition pill on products.html specifies Grade 15 matching yolk slider"""
        dom_prod = self.client.parse_dom('products.html')
        heritage_section = dom_prod.select_one('#heritage')
        self.assertIn("Grade 15", heritage_section.text)

        tier_info = JSSimulator.get_yolk_tier_info(15)
        self.assertIn("Grade 15", tier_info['title'])

    def test_t3_12_our_farms_welfare_metrics_match_home_stats(self):
        """21.8 sq ft metric on our-farms.html matches data-target='21.8' on index.html"""
        dom_farms = self.client.parse_dom('our-farms.html')
        self.assertIn("21.8", dom_farms.root.text)

        dom_home = self.client.parse_dom('index.html')
        counter = dom_home.select_one('.stat-counter-num[data-target="21.8"]')
        self.assertIsNotNone(counter)

    def test_t3_13_recipe_modal_close_restores_body_scroll_for_drawer(self):
        """Closing recipe modal sets body.style.overflow = '' enabling drawer usage"""
        resp = self.client.get('app.js')
        self.assertIn("document.body.style.overflow = ''", resp.text)

    def test_t3_14_all_pages_header_and_footer_uniform_navigation(self):
        """All 5 core pages have consistent primary navigation targets"""
        pages = ['index.html', 'products.html', 'our-farms.html', 'recipes.html', 'store-locator.html']
        for page in pages:
            dom = self.client.parse_dom(page)
            top_links = [a.get_attr('href') for a in dom.select('header .nav-links a')]
            self.assertIn('products.html', top_links)
            self.assertIn('our-farms.html', top_links)
            self.assertIn('store-locator.html', top_links)

    def test_t3_15_video_streaming_under_simulated_range_scrubbing(self):
        """Rapid successive range requests simulate video seeking without error"""
        ranges = [
            (0, 1023),
            (1024, 2047),
            (50000, 60000),
            (200000, 300000),
            (1000000, 1500000)
        ]
        for start, end in ranges:
            resp = self.client.get_byte_range('assets/videos/nutrifresh-hero.mp4', start, end)
            self.assertHttpStatus(resp, 206)
            self.assertEqual(len(resp.body), end - start + 1)

    def test_t3_16_floating_cta_presence_and_viewport_consistency(self):
        """Floating CTA exists across index.html, products.html, and our-farms.html"""
        for page in ['index.html', 'products.html', 'our-farms.html']:
            dom = self.client.parse_dom(page)
            cta = self.assertDOMExists(dom, '.floating-cta-btn', f"Floating CTA missing on {page}")
            self.assertEqual(cta.get_attr('href'), 'store-locator.html')


if __name__ == '__main__':
    unittest.main()
