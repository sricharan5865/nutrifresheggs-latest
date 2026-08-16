"""
Tier 4: Real-World Application User Journey Scenario Tests (6 Scenarios)
Validates end-to-end multi-step user workflows across the complete NutriFresh Eggs website.
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


class TestTier4_Scenarios(E2ETestBase):
    """End-to-End Real-World Application Scenarios"""

    def test_scenario_01_consumer_discovery_to_store_purchase(self):
        """Scenario 1: Consumer Discovery to Store Purchase Journey
        Hero -> Product Carousel -> Yolk Slider -> Store Locator -> Map Pin
        """
        # Step 1: Land on Home Page and inspect Hero
        dom_home = self.client.parse_dom('index.html')
        hero_video = self.assertDOMExists(dom_home, 'video.hero-video')
        self.assertEqual(hero_video.get_attr('poster'), 'assets/images/hens-pasture.jpg')
        curved_svg = self.assertDOMExists(dom_home, 'svg.curved-headline-svg')
        self.assertIn("CHOOSE NUTRIFRESH", curved_svg.text)

        # Step 2: Carousel interaction - Heritage card inspection
        heritage_card = dom_home.select_one('.carousel-track .product-card:nth-child(1)') or dom_home.select_one('.carousel-track .product-card')
        self.assertIn("Heritage Amber Yolks", heritage_card.text)
        self.assertIn("21.8 Sq Ft / Hen", heritage_card.text)

        # Step 3: Yolk Slider interaction across grades 1 -> 7 -> 15
        r1, g1, b1 = JSSimulator.calculate_yolk_rgb(1)
        tier1 = JSSimulator.get_yolk_tier_info(1)
        self.assertIn("Grade 1", tier1['title'])

        r7, g7, b7 = JSSimulator.calculate_yolk_rgb(7)
        tier7 = JSSimulator.get_yolk_tier_info(7)
        self.assertIn("Grade 5", tier7['title'])

        r15, g15, b15 = JSSimulator.calculate_yolk_rgb(15)
        tier15 = JSSimulator.get_yolk_tier_info(15)
        self.assertIn("Grade 15", tier15['title'])
        self.assertEqual((r15, g15, b15), (255, 85, 10))

        # Step 4: Click 'Find Store' CTA and navigate to store-locator.html
        dom_store = self.client.parse_dom('store-locator.html')
        search_input = self.assertDOMExists(dom_store, '#storeSearchInput')
        search_btn = self.assertDOMExists(dom_store, '#storeSearchBtn')

        # Step 5: Search for ZIP 78701 and verify store results
        sample_stores = [
            {'name': 'Whole Foods Market', 'address': '450 Natural Grove Way', 'city': 'Austin, TX 78701', 'dist': '0.8 miles', 'stock': 'In Stock (All Cartons)'},
            {'name': 'Sprouts Farmers Market', 'address': '1280 Green Valley Rd', 'city': 'Austin, TX 78704', 'dist': '1.4 miles', 'stock': 'In Stock (Heritage & Pasture)'},
            {'name': 'Kroger Fresh Market', 'address': '2100 Farmcrest Blvd', 'city': 'Austin, TX 78745', 'dist': '2.1 miles', 'stock': 'In Stock (Organic Free Range)'},
            {'name': 'Target Supercenter', 'address': '500 E Stassney Ln', 'city': 'Austin, TX 78745', 'dist': '3.5 miles', 'stock': 'In Stock (Pasture Raised)'},
            {'name': 'Trader Joe’s Market', 'address': '2805 Bee Caves Rd', 'city': 'Austin, TX 78746', 'dist': '4.2 miles', 'stock': 'In Stock (Heritage Amber)'}
        ]
        results_78701 = JSSimulator.search_stores(sample_stores, '78701')
        self.assertEqual(len(results_78701), 1)
        self.assertEqual(results_78701[0]['name'], 'Whole Foods Market')
        self.assertIn('0.8 miles', results_78701[0]['dist'])

        # Verify Map Pin 1 exists on SVG map
        pin1 = dom_store.select_one('svg.map-svg-mockup .map-pin')
        self.assertIsNotNone(pin1)

    def test_scenario_02_farm_kitchen_culinary_workflow(self):
        """Scenario 2: Farm Kitchen Culinary Workflow
        Recipes Directory -> Filter Brunch -> Modal Detail -> Checklist -> Store Locator
        """
        # Step 1: Visit recipes.html
        dom_recipes = self.client.parse_dom('recipes.html')
        h1 = self.assertDOMExists(dom_recipes, '.page-hero h1')
        self.assertEqual(h1.text, "Chef-Tested Egg Recipes")

        # Step 2: Filter by 'Weekend Brunch'
        all_cards = dom_recipes.select('#recipeCardsGrid .recipe-card')
        self.assertEqual(len(all_cards), 6)
        brunch_cards = [c for c in all_cards if c.get_attr('data-category') == 'brunch']
        self.assertEqual(len(brunch_cards), 2)

        # Step 3: Select 'Sunset Amber Eggs Benedict' and inspect modal trigger
        benedict_card = [c for c in brunch_cards if 'Benedict' in c.text][0]
        btn = benedict_card.find(class_name='open-recipe-modal')
        self.assertIsNotNone(btn)
        self.assertEqual(btn.get_attr('data-recipe'), 'benedict')

        # Step 4: Verify recipe database content in app.js for benedict
        resp_js = self.client.get('app.js')
        self.assertIn("Sunset Amber Eggs Benedict", resp_js.text)
        self.assertIn("4 Nutrifresh Heritage Breed eggs", resp_js.text)
        self.assertIn("In a blender or heatproof bowl", resp_js.text)

        # Step 5: Filter by 'Quick 15-Min' and select Breakfast Tacos
        quick_cards = [c for c in all_cards if c.get_attr('data-category') == 'quick']
        self.assertEqual(len(quick_cards), 2)
        tacos_card = [c for c in quick_cards if 'Tacos' in c.text][0]
        self.assertEqual(tacos_card.find(class_name='open-recipe-modal').get_attr('data-recipe'), 'tacos')

        # Step 6: Route to store locator to buy eggs
        dom_store = self.client.parse_dom('store-locator.html')
        self.assertDOMExists(dom_store, '#storeSearchInput')

    def test_scenario_03_mobile_visitor_responsive_experience(self):
        """Scenario 3: Mobile Visitor Responsive Experience
        Mobile Viewport (375px) -> Drawer -> Products -> Our Farms -> Floating CTA
        """
        # Step 1: Arrive on Home Page
        dom_home = self.client.parse_dom('index.html')
        drawer_trigger = self.assertDOMExists(dom_home, '.drawer-trigger')
        self.assertTrue(drawer_trigger.has_attr('aria-label'))

        # Step 2: Inspect Drawer panel structure
        drawer_overlay = self.assertDOMExists(dom_home, '.drawer-overlay')
        drawer = self.assertDOMExists(dom_home, '.slideout-drawer')
        close_btn = self.assertDOMExists(dom_home, '.drawer-close')

        # Step 3: Follow drawer link to products.html
        dom_prod = self.client.parse_dom('products.html')
        sections = dom_prod.select('.product-detail-card')
        self.assertEqual(len(sections), 4)

        # Step 4: Follow drawer link to our-farms.html
        dom_farms = self.client.parse_dom('our-farms.html')
        h1_farms = self.assertDOMExists(dom_farms, '.page-hero h1')
        self.assertEqual(h1_farms.text, "Farming with Integrity")

        # Step 5: Verify floating 'Get Nutrifresh' CTA is available on mobile
        floating_cta = self.assertDOMExists(dom_farms, '.floating-cta-btn')
        self.assertEqual(floating_cta.get_attr('href'), 'store-locator.html')

    def test_scenario_04_brand_due_diligence_and_nutrition(self):
        """Scenario 4: Brand Due-Diligence & Nutritional Verification
        Our Farms -> Pasture Standards -> Nutrition Facts -> Products -> Newsletter
        """
        # Step 1: Visit our-farms.html to check pasture space standard
        dom_farms = self.client.parse_dom('our-farms.html')
        self.assertIn("SUREGROW FARMS", dom_farms.root.text)

        # Step 2: Verify zero hormones guarantee
        self.assertIn("Zero Hormones", dom_farms.root.text)
        self.assertIn("100% Vegetarian Feed", dom_farms.root.text)

        # Step 3: Verify 5 science-backed nutrition fact cards
        facts = dom_farms.select('.nutrition-fact-card')
        self.assertEqual(len(facts), 5)
        fact_texts = [f.text for f in facts]
        self.assertTrue(any("⅓ Less" in t for t in fact_texts))
        self.assertTrue(any("7x More" in t for t in fact_texts))

        # Step 4: Navigate to products.html and check pasture-raised section
        dom_prod = self.client.parse_dom('products.html')
        pasture_section = self.assertDOMExists(dom_prod, '#pasture')
        self.assertIn("21.8 Sq Ft", pasture_section.text)

        # Step 5: Subscribe to newsletter in footer
        form = dom_prod.select_one('.newsletter-form') or dom_prod.select_one('footer form')
        if not form:
            dom_home = self.client.parse_dom('index.html')
            form = dom_home.select_one('.newsletter-form')
        self.assertIsNotNone(form, "Newsletter form must be present in footer")

    def test_scenario_05_video_asset_streaming_and_http_conformance(self):
        """Scenario 5: Video Asset Streaming & HTTP Protocol Conformance Audit
        HTML <video> -> HEAD request -> Range 0-1023 -> Range 500000-1000000 -> Poster Image 200
        """
        # Step 1: Extract video element on home page
        dom_home = self.client.parse_dom('index.html')
        source = self.assertDOMExists(dom_home, 'video.hero-video source')
        video_src = source.get_attr('src')
        self.assertEqual(video_src, 'assets/videos/nutrifresh-hero.mp4')

        # Step 2: HEAD request for video headers
        head_resp = self.client.head(video_src)
        self.assertHttpStatus(head_resp, 200)
        self.assertContentType(head_resp, 'video/mp4')
        self.assertEqual(head_resp.get_header('accept-ranges'), 'bytes')
        total_size = head_resp.content_length
        self.assertGreater(total_size, 5000000)

        # Step 3: Request first 1024 bytes (Range 0-1023)
        chunk1 = self.client.get_byte_range(video_src, 0, 1023)
        self.assertHttpStatus(chunk1, 206)
        self.assertEqual(len(chunk1.body), 1024)
        self.assertEqual(chunk1.content_range, f"bytes 0-1023/{total_size}")

        # Step 4: Request middle segment (Range 500000-1000000)
        chunk2 = self.client.get_byte_range(video_src, 500000, 1000000)
        self.assertHttpStatus(chunk2, 206)
        self.assertEqual(len(chunk2.body), 500001)
        self.assertEqual(chunk2.content_range, f"bytes 500000-1000000/{total_size}")

        # Step 5: Verify fallback poster image loads with HTTP 200
        poster_resp = self.client.get('assets/images/hens-pasture.jpg')
        self.assertHttpStatus(poster_resp, 200)
        self.assertContentType(poster_resp, 'image/jpeg')

    def test_scenario_06_robustness_and_adversarial_error_recovery(self):
        """Scenario 6: Robustness & Adversarial Error Recovery Journey
        Invalid ZIP -> Out-of-Bounds Slider -> Rapid Filter Toggles -> Missing Recipe Modal Guard
        """
        # Step 1: Store locator with non-existent zip returns empty result
        sample_stores = [
            {'name': 'Whole Foods Market', 'address': '450 Natural Grove Way', 'city': 'Austin, TX 78701', 'dist': '0.8 miles', 'stock': 'In Stock (All Cartons)'}
        ]
        empty_res = JSSimulator.search_stores(sample_stores, '99999')
        self.assertEqual(len(empty_res), 0)

        # Step 2: Out-of-bounds yolk slider values clamp gracefully
        r_neg, g_neg, b_neg = JSSimulator.calculate_yolk_rgb(-100)
        r_min, g_min, b_min = JSSimulator.calculate_yolk_rgb(1)
        self.assertEqual((r_neg, g_neg, b_neg), (r_min, g_min, b_min))

        r_over, g_over, b_over = JSSimulator.calculate_yolk_rgb(500)
        r_max, g_max, b_max = JSSimulator.calculate_yolk_rgb(15)
        self.assertEqual((r_over, g_over, b_over), (r_max, g_max, b_max))

        # Step 3: Rapid recipe filter cycling keeps card set stable
        sample_recipes = [
            {'title': 'R1', 'category': 'brunch'},
            {'title': 'R2', 'category': 'quick'},
            {'title': 'R3', 'category': 'baking'}
        ]
        res1 = JSSimulator.filter_recipes(sample_recipes, 'brunch')
        res2 = JSSimulator.filter_recipes(sample_recipes, 'quick')
        res3 = JSSimulator.filter_recipes(sample_recipes, 'baking')
        res_all = JSSimulator.filter_recipes(sample_recipes, 'all')
        self.assertEqual(len(res1), 1)
        self.assertEqual(len(res2), 1)
        self.assertEqual(len(res3), 1)
        self.assertEqual(len(res_all), 3)

        # Step 4: Missing recipe ID guard in app.js prevents unhandled crash
        resp_js = self.client.get('app.js')
        self.assertIn("if (!recipe || !modalContent || !modalOverlay) return;", resp_js.text)


if __name__ == '__main__':
    unittest.main()
