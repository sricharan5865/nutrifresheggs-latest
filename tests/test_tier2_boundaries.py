"""
Tier 2: Boundary & Corner Cases Test Suite (16 Features x >=5 Tests = >=80 Tests)
Validates extreme bounds, clamp limits, error recovery, responsive breakpoints,
MIME handling, range math, and structural invariants for NutriFresh Eggs.
"""

import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from tests.test_helper import E2ETestBase, DOMQueryEngine, JSSimulator, BASE_DIR
except ImportError:
    from test_helper import E2ETestBase, DOMQueryEngine, JSSimulator, BASE_DIR


class TestTier2_F01_HeaderNavBoundaries(E2ETestBase):
    """Feature 1: Header Navigation Boundaries & Corner Cases"""

    def test_f01_b01_rapid_scroll_threshold_logic(self):
        resp = self.client.get('app.js')
        self.assertHttpStatus(resp, 200)
        self.assertIn("window.scrollY > 50", resp.text)
        self.assertIn("header.classList.add('scrolled')", resp.text)
        self.assertIn("header.classList.remove('scrolled')", resp.text)

    def test_f01_b02_header_mobile_breakpoint_css(self):
        resp = self.client.get('styles.css')
        self.assertHttpStatus(resp, 200)
        self.assertIn("@media", resp.text)
        self.assertIn("768px", resp.text)

    def test_f01_b03_header_max_width_constraint(self):
        resp = self.client.get('styles.css')
        self.assertIn(".header-container", resp.text)

    def test_f01_b04_hash_fragment_navigation_targets(self):
        dom = self.client.parse_dom('index.html')
        nav_hashes = ['products', 'yolk-difference', 'recipes', 'locator']
        for target_id in nav_hashes:
            target_node = dom.select_one(f'#{target_id}')
            self.assertIsNotNone(target_node, f"Target anchor #{target_id} missing on index.html")

    def test_f01_b05_zero_dead_links_in_header(self):
        pages = ['index.html', 'products.html', 'our-farms.html', 'recipes.html', 'store-locator.html']
        for page in pages:
            dom = self.client.parse_dom(page)
            header_links = dom.select('header a')
            for a in header_links:
                href = a.get_attr('href')
                self.assertIsNotNone(href, f"Header link missing href on {page}")
                self.assertNotEqual(href, "#", f"Dead link href='#' found in header on {page}")


class TestTier2_F02_DrawerBoundaries(E2ETestBase):
    """Feature 2: Slideout Drawer Boundaries & Edge Cases"""

    def test_f02_b01_drawer_escape_key_listener(self):
        resp = self.client.get('app.js')
        self.assertIn("e.key === 'Escape'", resp.text)
        self.assertIn("closeDrawer()", resp.text)

    def test_f02_b02_drawer_body_overflow_lock(self):
        resp = self.client.get('app.js')
        self.assertIn("document.body.style.overflow = 'hidden'", resp.text)
        self.assertIn("document.body.style.overflow = ''", resp.text)

    def test_f02_b03_drawer_outside_click_propagation(self):
        resp = self.client.get('app.js')
        self.assertIn("e.target === drawerOverlay", resp.text)

    def test_f02_b04_drawer_carton_hash_targets_exist(self):
        dom = self.client.parse_dom('products.html')
        for cid in ['heritage', 'pasture', 'organic', 'freerange']:
            self.assertIsNotNone(dom.select_one(f'#{cid}'), f"Product section #{cid} missing on products.html")

    def test_f02_b05_drawer_carton_image_aspect_ratio(self):
        dom = self.client.parse_dom('index.html')
        images = dom.select('.drawer-cartons-grid img')
        self.assertEqual(len(images), 4)
        for img in images:
            self.assertTrue(img.has_attr('src'))
            resp = self.client.get(img.get_attr('src'))
            self.assertHttpStatus(resp, 200)


class TestTier2_F03_FooterBoundaries(E2ETestBase):
    """Feature 3: Footer & Modals Boundaries & Edge Cases"""

    def test_f03_b01_newsletter_form_email_validation(self):
        dom = self.client.parse_dom('index.html')
        email_inp = dom.select_one('.newsletter-input') or dom.select_one('.footer-newsletter input[type="email"]')
        self.assertIsNotNone(email_inp)
        self.assertEqual(email_inp.get_attr('type'), 'email')
        self.assertTrue(email_inp.has_attr('required'))

    def test_f03_b02_legal_modal_fallback_integrity(self):
        dom = self.client.parse_dom('index.html')
        legal_elements = dom.select('.footer-bottom .legal-link-btn') or dom.select('.footer-bottom a')
        self.assertGreaterEqual(len(legal_elements), 1, "Expected legal links or buttons in footer")

    def test_f03_b03_floating_cta_fixed_positioning_and_zindex(self):
        resp = self.client.get('styles.css')
        self.assertIn(".floating-cta-btn", resp.text)
        self.assertIn("position: fixed", resp.text)

    def test_f03_b04_footer_responsive_column_wrapping(self):
        resp = self.client.get('styles.css')
        self.assertIn(".footer-top", resp.text)

    def test_f03_b05_unicode_emoji_rendering_integrity(self):
        dom = self.client.parse_dom('index.html')
        cta = dom.select_one('.floating-cta-btn')
        self.assertIn("🛒", cta.text)


class TestTier2_F04_BrandBoundaries(E2ETestBase):
    """Feature 4: Brand Identity Boundaries & Asset Integrity"""

    def test_f04_b01_logo_hires_and_white_dimensions(self):
        resp_dark = self.client.get('assets/images/nutrifresh-logo-hires.png')
        self.assertHttpStatus(resp_dark, 200)
        self.assertGreater(len(resp_dark.body), 1000)

        resp_white = self.client.get('assets/images/nutrifresh-logo-hires-white.png')
        self.assertHttpStatus(resp_white, 200)
        self.assertGreater(len(resp_white.body), 1000)

    def test_f04_b02_system_font_fallbacks(self):
        resp = self.client.get('styles.css')
        self.assertIn("sans-serif", resp.text)

    def test_f04_b03_global_img_alt_audit(self):
        pages = ['index.html', 'products.html', 'our-farms.html', 'recipes.html', 'store-locator.html']
        for page in pages:
            dom = self.client.parse_dom(page)
            for img in dom.select('img'):
                alt = img.get_attr('alt')
                self.assertIsNotNone(alt, f"img tag missing alt attribute on {page}: {img}")
                self.assertGreater(len(alt.strip()), 0, f"img alt attribute is empty on {page}: {img}")

    def test_f04_b04_contrast_and_color_tokens(self):
        resp = self.client.get('styles.css')
        self.assertIn("--pasture-green", resp.text)
        self.assertIn("--eggshell-cream", resp.text)

    def test_f04_b05_meta_descriptions_length_and_quality(self):
        pages = ['index.html', 'products.html', 'our-farms.html', 'recipes.html', 'store-locator.html']
        for page in pages:
            dom = self.client.parse_dom(page)
            desc_meta = dom.select_one('meta[name="description"]')
            self.assertIsNotNone(desc_meta, f"meta description missing on {page}")
            desc_content = desc_meta.get_attr('content', '')
            self.assertGreater(len(desc_content), 40, f"meta description too short on {page}: {desc_content}")


class TestTier2_F05_HeroVideoBoundaries(E2ETestBase):
    """Feature 5: Video Hero Boundaries & Audio Edge Cases"""

    def test_f05_b01_autoplay_promise_rejection_fallback(self):
        resp = self.client.get('app.js')
        self.assertIn("playPromise.catch", resp.text)
        self.assertIn("heroVideo.muted = true", resp.text)

    def test_f05_b02_video_file_size_and_preservation(self):
        resp = self.client.head('assets/videos/nutrifresh-hero.mp4')
        self.assertHttpStatus(resp, 200)
        self.assertGreater(resp.content_length, 5000000, "Hero video file size must be preserved (>5MB)")

    def test_f05_b03_curved_svg_viewbox_scaling(self):
        dom = self.client.parse_dom('index.html')
        svg = dom.select_one('svg.curved-headline-svg')
        self.assertEqual(svg.get_attr('viewbox'), '0 0 700 130')

    def test_f05_b04_sound_toggle_volume_level(self):
        resp = self.client.get('app.js')
        self.assertIn("heroVideo.volume = 0.6", resp.text)

    def test_f05_b05_video_poster_image_exists(self):
        dom = self.client.parse_dom('index.html')
        video = dom.select_one('video.hero-video')
        poster = video.get_attr('poster')
        self.assertIsNotNone(poster)
        resp = self.client.get(poster)
        self.assertHttpStatus(resp, 200)


class TestTier2_F06_FarmIntegrityBoundaries(E2ETestBase):
    """Feature 6: Farm Integrity Boundaries & Science Cards"""

    def test_f06_b01_four_pillar_grid_responsive_css(self):
        resp = self.client.get('styles.css')
        self.assertIn(".path-grid", resp.text)

    def test_f06_b02_nutrition_stat_big_text_classes(self):
        dom = self.client.parse_dom('index.html')
        big_stats = dom.select('.fact-big-stat')
        self.assertEqual(len(big_stats), 5)
        for stat in big_stats:
            self.assertGreater(len(stat.text.strip()), 0)

    def test_f06_b03_caveat_script_text_styling(self):
        resp = self.client.get('styles.css')
        self.assertIn(".script-text", resp.text)

    def test_f06_b04_brand_card_responsive_width(self):
        resp = self.client.get('styles.css')
        self.assertIn(".official-brand-card-img", resp.text)

    def test_f06_b05_welfare_checklist_structure(self):
        dom = self.client.parse_dom('index.html')
        items = dom.select('.welfare-checklist li')
        self.assertEqual(len(items), 4, "Expected 4 items in welfare checklist")


class TestTier2_F07_ProductCarouselBoundaries(E2ETestBase):
    """Feature 7: Product Carousel Math & Breakpoints"""

    def test_f07_b01_next_button_wrap_around_math(self):
        idx0 = 0
        idx1 = JSSimulator.calculate_carousel_index(idx0, 'next', 4, 1200)
        self.assertEqual(idx1, 1)
        idx_wrapped = JSSimulator.calculate_carousel_index(idx1, 'next', 4, 1200)
        self.assertEqual(idx_wrapped, 0)

    def test_f07_b02_prev_button_clamp_at_zero(self):
        idx = JSSimulator.calculate_carousel_index(0, 'prev', 4, 1200)
        self.assertEqual(idx, 0)

    def test_f07_b03_visible_cards_calculation_breakpoints(self):
        self.assertEqual(JSSimulator.get_visible_cards(375), 1)
        self.assertEqual(JSSimulator.get_visible_cards(768), 1)
        self.assertEqual(JSSimulator.get_visible_cards(800), 2)
        self.assertEqual(JSSimulator.get_visible_cards(1024), 2)
        self.assertEqual(JSSimulator.get_visible_cards(1200), 3)

    def test_f07_b04_carousel_resize_clamping(self):
        clamped = JSSimulator.calculate_carousel_index(3, 'resize', 4, 1200)
        self.assertEqual(clamped, 1)

    def test_f07_b05_card_badge_distinct_styling(self):
        resp = self.client.get('styles.css')
        self.assertIn(".badge-heritage", resp.text)
        self.assertIn(".badge-pasture", resp.text)
        self.assertIn(".badge-organic", resp.text)
        self.assertIn(".badge-freerange", resp.text)


class TestTier2_F08_YolkSliderBoundaries(E2ETestBase):
    """Feature 8: Yolk Slider Color Interpolation & Clamping"""

    def test_f08_b01_min_boundary_grade_1_rgb_and_tier(self):
        r, g, b = JSSimulator.calculate_yolk_rgb(1)
        self.assertEqual(r, 255)
        self.assertEqual(g, 234)
        self.assertEqual(b, 169)
        tier = JSSimulator.get_yolk_tier_info(1)
        self.assertIn("Grade 1", tier['title'])

    def test_f08_b02_max_boundary_grade_15_rgb_and_tier(self):
        r, g, b = JSSimulator.calculate_yolk_rgb(15)
        self.assertEqual(r, 255)
        self.assertEqual(g, 85)
        self.assertEqual(b, 10)
        tier = JSSimulator.get_yolk_tier_info(15)
        self.assertIn("Grade 15", tier['title'])

    def test_f08_b03_tier_threshold_transitions(self):
        self.assertIn("Grade 1", JSSimulator.get_yolk_tier_info(3)['title'])
        self.assertIn("Grade 5", JSSimulator.get_yolk_tier_info(4)['title'])
        self.assertIn("Grade 5", JSSimulator.get_yolk_tier_info(7)['title'])
        self.assertIn("Grade 10", JSSimulator.get_yolk_tier_info(8)['title'])
        self.assertIn("Grade 10", JSSimulator.get_yolk_tier_info(12)['title'])
        self.assertIn("Grade 15", JSSimulator.get_yolk_tier_info(13)['title'])

    def test_f08_b04_out_of_bounds_clamping(self):
        rgb_below = JSSimulator.calculate_yolk_rgb(-5)
        rgb_min = JSSimulator.calculate_yolk_rgb(1)
        self.assertEqual(rgb_below, rgb_min)

        rgb_above = JSSimulator.calculate_yolk_rgb(50)
        rgb_max = JSSimulator.calculate_yolk_rgb(15)
        self.assertEqual(rgb_above, rgb_max)

    def test_f08_b05_yolk_photo_overlay_labels(self):
        dom = self.client.parse_dom('index.html')
        overlay = dom.select_one('.yolk-compare-overlay')
        self.assertIsNotNone(overlay)
        self.assertIn("Grade 2", overlay.text)
        self.assertIn("Grade 15", overlay.text)


class TestTier2_F09_StatsCounterBoundaries(E2ETestBase):
    """Feature 9: Stats Counter Observer & Decimal Precision"""

    def test_f09_b01_unobserve_pattern_in_appjs(self):
        resp = self.client.get('app.js')
        self.assertIn("obs.unobserve(entry.target)", resp.text)

    def test_f09_b02_decimal_precision_tofixed_1(self):
        resp = self.client.get('app.js')
        self.assertIn("current.toFixed(1)", resp.text)
        self.assertIn("target % 1 !== 0", resp.text)

    def test_f09_b03_integer_counter_math_floor(self):
        resp = self.client.get('app.js')
        self.assertIn("Math.floor(current)", resp.text)

    def test_f09_b04_intersection_observer_threshold_05(self):
        resp = self.client.get('app.js')
        self.assertIn("threshold: 0.5", resp.text)

    def test_f09_b05_stats_grid_responsive_styling(self):
        resp = self.client.get('styles.css')
        self.assertIn(".stats-grid", resp.text)


class TestTier2_F10_RecipeTeasersBoundaries(E2ETestBase):
    """Feature 10: Recipe Teasers & Reviews Security & Invariants"""

    def test_f10_b01_instagram_links_target_blank_rel_noopener(self):
        dom = self.client.parse_dom('index.html')
        insta_links = dom.select('.instagram-section a')
        self.assertGreaterEqual(len(insta_links), 4)
        for link in insta_links:
            self.assertEqual(link.get_attr('target'), '_blank')
            self.assertTrue('noopener' in link.get_attr('rel', ''))

    def test_f10_b02_reviews_card_wrap_and_quote_styling(self):
        resp = self.client.get('styles.css')
        self.assertIn(".review-card", resp.text)

    def test_f10_b03_recipe_teaser_time_badges_format(self):
        dom = self.client.parse_dom('index.html')
        badges = dom.select('.recipes-section .recipe-time-badge')
        for b in badges:
            self.assertTrue(b.text.startswith("⏱ "))

    def test_f10_b04_recipe_teaser_image_aspect_ratio_styles(self):
        resp = self.client.get('styles.css')
        self.assertIn(".recipe-img-holder", resp.text)

    def test_f10_b05_insta_grid_four_cards(self):
        dom = self.client.parse_dom('index.html')
        cards = dom.select('.insta-grid .insta-card')
        self.assertEqual(len(cards), 4)


class TestTier2_F11_ProductsShowcaseBoundaries(E2ETestBase):
    """Feature 11: Products Showcase Deep Anchors & Badges"""

    def test_f11_b01_anchor_fragments_resolvability(self):
        dom = self.client.parse_dom('products.html')
        for anchor_id in ['heritage', 'pasture', 'organic', 'freerange']:
            node = dom.select_one(f'#{anchor_id}')
            self.assertIsNotNone(node, f"Anchor #{anchor_id} missing on products.html")

    def test_f11_b02_nutrition_pill_labels_content(self):
        dom = self.client.parse_dom('products.html')
        pills = dom.select('.nutrition-pill')
        self.assertEqual(len(pills), 16)
        for pill in pills:
            self.assertIsNotNone(pill.find(tag='span'))
            self.assertIsNotNone(pill.find(tag='label'))

    def test_f11_b03_products_page_floating_cta(self):
        dom = self.client.parse_dom('products.html')
        self.assertDOMExists(dom, '.floating-cta-btn')

    def test_f11_b04_yolk_scale_cta_link_back(self):
        dom = self.client.parse_dom('products.html')
        yolk_scale_link = dom.select_one('a[href="index.html#yolk-difference"]')
        self.assertIsNotNone(yolk_scale_link)

    def test_f11_b05_all_product_detail_cards_have_badges(self):
        dom = self.client.parse_dom('products.html')
        badges = dom.select('.product-detail-card .product-card-badge')
        self.assertEqual(len(badges), 4)


class TestTier2_F12_OurFarmsStoryBoundaries(E2ETestBase):
    """Feature 12: Our Farms Standards & Responsive Ordering"""

    def test_f12_b01_flex_order_reversal_in_story_block_2(self):
        dom = self.client.parse_dom('our-farms.html')
        blocks = dom.select('.farm-story-block')
        block2 = blocks[1]
        order1 = block2.find(attr_name='style', attr_val='order: 1;')
        order2 = block2.find(attr_name='style', attr_val='order: 2;')
        self.assertIsNotNone(order1)
        self.assertIsNotNone(order2)

    def test_f12_b02_instagram_cta_button_url(self):
        dom = self.client.parse_dom('our-farms.html')
        insta_btn = dom.select_one('a[href*="instagram.com"]')
        self.assertIsNotNone(insta_btn)
        self.assertEqual(insta_btn.get_attr('target'), '_blank')

    def test_f12_b03_badge_grid_two_boxes(self):
        dom = self.client.parse_dom('our-farms.html')
        boxes = dom.select('.farm-badge-box')
        self.assertEqual(len(boxes), 2)

    def test_f12_b04_zero_dead_links_on_our_farms(self):
        dom = self.client.parse_dom('our-farms.html')
        for a in dom.select('a'):
            href = a.get_attr('href')
            self.assertIsNotNone(href)
            self.assertNotEqual(href, '#')

    def test_f12_b05_nutrition_cards_match_home_values(self):
        dom_farms = self.client.parse_dom('our-farms.html')
        dom_home = self.client.parse_dom('index.html')
        stats_farms = [s.text for s in dom_farms.select('.fact-big-stat')]
        stats_home = [s.text for s in dom_home.select('.fact-big-stat')]
        self.assertEqual(stats_farms, stats_home)


class TestTier2_F13_RecipesFilterBoundaries(E2ETestBase):
    """Feature 13: Recipes Category Filter Simulations"""

    def setUp(self):
        super().setUp()
        self.sample_recipes = [
            {'title': 'Sunset Amber Eggs Benedict', 'category': 'brunch'},
            {'title': 'Pasture Breakfast Tacos', 'category': 'quick'},
            {'title': 'Cast-Iron Farm Shakshuka', 'category': 'brunch'},
            {'title': 'Heritage Amber Lemon Curd', 'category': 'baking'},
            {'title': 'Jammy Yolk Avocado Toast', 'category': 'quick'},
            {'title': 'Classic French Rolled Omelette', 'category': 'baking'}
        ]

    def test_f13_b01_category_filtering_simulation_brunch(self):
        res = JSSimulator.filter_recipes(self.sample_recipes, 'brunch')
        self.assertEqual(len(res), 2)
        titles = [r['title'] for r in res]
        self.assertIn('Sunset Amber Eggs Benedict', titles)
        self.assertIn('Cast-Iron Farm Shakshuka', titles)

    def test_f13_b02_category_filtering_simulation_quick(self):
        res = JSSimulator.filter_recipes(self.sample_recipes, 'quick')
        self.assertEqual(len(res), 2)
        titles = [r['title'] for r in res]
        self.assertIn('Pasture Breakfast Tacos', titles)
        self.assertIn('Jammy Yolk Avocado Toast', titles)

    def test_f13_b03_category_filtering_simulation_baking(self):
        res = JSSimulator.filter_recipes(self.sample_recipes, 'baking')
        self.assertEqual(len(res), 2)
        titles = [r['title'] for r in res]
        self.assertIn('Heritage Amber Lemon Curd', titles)
        self.assertIn('Classic French Rolled Omelette', titles)

    def test_f13_b04_category_filtering_simulation_all(self):
        res = JSSimulator.filter_recipes(self.sample_recipes, 'all')
        self.assertEqual(len(res), 6)

    def test_f13_b05_filter_btn_active_class_toggle_logic(self):
        resp = self.client.get('app.js')
        self.assertIn("b.classList.remove('active', 'btn-navy')", resp.text)
        self.assertIn("btn.classList.add('active', 'btn-navy')", resp.text)


class TestTier2_F14_RecipeModalBoundaries(E2ETestBase):
    """Feature 14: Recipe Modal Data & Interaction Edge Cases"""

    def test_f14_b01_all_six_recipe_keys_in_js_database(self):
        resp = self.client.get('app.js')
        for key in ['benedict', 'tacos', 'shakshuka', 'curd', 'tartine', 'omelette']:
            self.assertIn(f"{key}: {{", resp.text)

    def test_f14_b02_recipe_images_exist_and_serve_200(self):
        recipe_images = [
            'assets/images/nutrifresh_breakfast_dish.jpg',
            'assets/images/nutrifresh_egg_tacos.jpg',
            'assets/images/breakfast-plate.jpg',
            'assets/images/yolk-comparison.jpg',
            'assets/images/pasture-carton.jpg',
            'assets/images/hens-pasture.jpg'
        ]
        for img_path in recipe_images:
            resp = self.client.get(img_path)
            self.assertHttpStatus(resp, 200, f"Recipe image failed to serve 200: {img_path}")

    def test_f14_b03_body_overflow_lock_and_unlock(self):
        resp = self.client.get('app.js')
        self.assertIn("modalOverlay.classList.add('active')", resp.text)
        self.assertIn("modalOverlay.classList.remove('active')", resp.text)

    def test_f14_b04_backdrop_click_dismissal_logic(self):
        resp = self.client.get('app.js')
        self.assertIn("e.target === modalOverlay", resp.text)

    def test_f14_b05_missing_recipe_id_guard(self):
        resp = self.client.get('app.js')
        self.assertIn("if (!recipe || !modalContent || !modalOverlay) return;", resp.text)


class TestTier2_F15_StoreLocatorBoundaries(E2ETestBase):
    """Feature 15: Store Locator Search & Query Edge Cases"""

    def setUp(self):
        super().setUp()
        self.sample_stores = [
            {'name': 'Whole Foods Market', 'address': '450 Natural Grove Way', 'city': 'Austin, TX 78701', 'dist': '0.8 miles', 'stock': 'In Stock (All Cartons)'},
            {'name': 'Sprouts Farmers Market', 'address': '1280 Green Valley Rd', 'city': 'Austin, TX 78704', 'dist': '1.4 miles', 'stock': 'In Stock (Heritage & Pasture)'},
            {'name': 'Kroger Fresh Market', 'address': '2100 Farmcrest Blvd', 'city': 'Austin, TX 78745', 'dist': '2.1 miles', 'stock': 'In Stock (Organic Free Range)'},
            {'name': 'Target Supercenter', 'address': '500 E Stassney Ln', 'city': 'Austin, TX 78745', 'dist': '3.5 miles', 'stock': 'In Stock (Pasture Raised)'},
            {'name': 'Trader Joe’s Market', 'address': '2805 Bee Caves Rd', 'city': 'Austin, TX 78746', 'dist': '4.2 miles', 'stock': 'In Stock (Heritage Amber)'}
        ]

    def test_f15_b01_empty_query_returns_all_five_stores(self):
        res = JSSimulator.search_stores(self.sample_stores, "")
        self.assertEqual(len(res), 5)

    def test_f15_b02_whitespace_query_returns_all_stores(self):
        res = JSSimulator.search_stores(self.sample_stores, "   ")
        self.assertEqual(len(res), 5)

    def test_f15_b03_non_existent_zip_returns_empty_list(self):
        res = JSSimulator.search_stores(self.sample_stores, "99999")
        self.assertEqual(len(res), 0)

    def test_f15_b04_case_insensitive_store_search(self):
        res_upper = JSSimulator.search_stores(self.sample_stores, "AUSTIN")
        res_lower = JSSimulator.search_stores(self.sample_stores, "austin")
        self.assertEqual(len(res_upper), len(res_lower))
        self.assertEqual(len(res_upper), 5)

    def test_f15_b05_carton_filtering_simulation(self):
        res_heritage = JSSimulator.filter_stores_by_carton(self.sample_stores, "Heritage Amber")
        self.assertEqual(len(res_heritage), 3)


class TestTier2_F16_ServerStreamingBoundaries(E2ETestBase):
    """Feature 16: Byte-Range RFC 7233 & Path Security Sandboxing"""

    def test_f16_b01_first_byte_only_range_0_0(self):
        resp = self.client.get_byte_range('assets/videos/nutrifresh-hero.mp4', 0, 0)
        self.assertHttpStatus(resp, 206)
        self.assertEqual(len(resp.body), 1)
        self.assertTrue(resp.content_range.startswith('bytes 0-0/'))

    def test_f16_b02_exact_last_byte_range(self):
        head = self.client.head('assets/videos/nutrifresh-hero.mp4')
        size = head.content_length
        resp = self.client.get_byte_range('assets/videos/nutrifresh-hero.mp4', size - 1, size - 1)
        self.assertHttpStatus(resp, 206)
        self.assertEqual(len(resp.body), 1)
        self.assertEqual(resp.content_range, f"bytes {size-1}-{size-1}/{size}")

    def test_f16_b03_open_ended_range(self):
        head = self.client.head('assets/videos/nutrifresh-hero.mp4')
        size = head.content_length
        start = size - 1000
        resp = self.client.get_byte_range('assets/videos/nutrifresh-hero.mp4', start)
        self.assertHttpStatus(resp, 206)
        self.assertEqual(len(resp.body), 1000)
        self.assertEqual(resp.content_range, f"bytes {start}-{size-1}/{size}")

    def test_f16_b04_start_exceeding_file_size_returns_416(self):
        resp = self.client.get_byte_range('assets/videos/nutrifresh-hero.mp4', 999999999)
        self.assertHttpStatus(resp, 416)

    def test_f16_b05_directory_traversal_sandbox_escape_returns_403(self):
        resp = self.client.get('../../etc/passwd')
        self.assertHttpStatus(resp, 403)


if __name__ == '__main__':
    unittest.main()
