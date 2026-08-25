"""
Tier 1: Feature Coverage Test Suite (16 Features x >=5 Tests = >=80 Tests)
Validates core functionality, DOM landmark hierarchies, component structures,
asset resolution, and direct HTTP endpoints for NutriFresh Eggs.
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


class TestTier1_F01_HeaderNav(E2ETestBase):
    """Feature 1: Global Header & Navigation"""

    def test_f01_01_header_presence_and_container(self):
        pages = ['index.html', 'products.html', 'our-farms.html', 'recipes.html', 'store-locator.html']
        for page in pages:
            dom = self.client.parse_dom(page)
            header = self.assertDOMExists(dom, 'header.site-header', f"Header missing on {page}")
            self.assertTrue(header.find(class_name='header-container') is not None, f"header-container missing on {page}")

    def test_f01_02_brand_logo_link_and_img(self):
        pages = ['index.html', 'products.html', 'our-farms.html', 'recipes.html', 'store-locator.html']
        for page in pages:
            dom = self.client.parse_dom(page)
            logo_img = dom.select_one('.brand-logo-img') or dom.select_one('.brand-logo img') or dom.select_one('.logo-brand img')
            self.assertIsNotNone(logo_img, f"Logo image missing on {page}")
            src = logo_img.get_attr('src')
            self.assertTrue(src.startswith('assets/images/'), f"Logo src invalid on {page}: {src}")
            resp = self.client.get(src)
            self.assertHttpStatus(resp, 200, f"Logo image asset failed to load on {page}: {src}")

    def test_f01_03_desktop_nav_links_structure(self):
        dom = self.client.parse_dom('index.html')
        nav_links = dom.select('.nav-links li a')
        self.assertGreaterEqual(len(nav_links), 4, "Expected at least 4 top nav links on index.html")
        hrefs = [a.get_attr('href') for a in nav_links]
        self.assertIn('index.html', hrefs)
        self.assertIn('products.html', hrefs)
        self.assertIn('our-farms.html', hrefs)
        self.assertIn('store-locator.html', hrefs)

    def test_f01_04_active_page_indicator(self):
        page_active_map = {
            'index.html': 'index.html',
            'products.html': 'products.html',
            'our-farms.html': 'our-farms.html',
            'recipes.html': 'recipes.html',
            'store-locator.html': 'store-locator.html'
        }
        for page, expected_href in page_active_map.items():
            dom = self.client.parse_dom(page)
            active_link = dom.select_one('.nav-links a.active')
            self.assertIsNotNone(active_link, f"Active nav indicator missing on {page}")
            self.assertEqual(active_link.get_attr('href'), expected_href, f"Active nav href mismatch on {page}")

    def test_f01_05_store_cta_button_in_header(self):
        dom = self.client.parse_dom('index.html')
        cta = dom.select_one('.header-right a.btn-primary')
        self.assertIsNotNone(cta, "Header Get Nutrifresh CTA button missing")
        self.assertEqual(cta.get_attr('href'), 'store-locator.html')
        self.assertIn("Get Nutrifresh", cta.text)


class TestTier1_F02_Drawer(E2ETestBase):
    """Feature 2: Slideout Mobile Navigation Drawer"""

    def test_f02_01_drawer_markup_and_overlay(self):
        pages = ['index.html', 'products.html', 'our-farms.html', 'recipes.html', 'store-locator.html']
        for page in pages:
            dom = self.client.parse_dom(page)
            self.assertDOMExists(dom, '.drawer-overlay', f"Drawer overlay missing on {page}")
            self.assertDOMExists(dom, '.slideout-drawer', f"Slideout drawer container missing on {page}")

    def test_f02_02_drawer_trigger_and_close_buttons(self):
        dom = self.client.parse_dom('index.html')
        trigger = self.assertDOMExists(dom, '.drawer-trigger', "Drawer open trigger missing")
        self.assertTrue(trigger.has_attr('aria-label'))
        close_btn = self.assertDOMExists(dom, '.drawer-close', "Drawer close button missing")
        self.assertTrue(close_btn.has_attr('aria-label'))

    def test_f02_03_drawer_navigation_links(self):
        dom = self.client.parse_dom('index.html')
        drawer_links = dom.select('.drawer-nav-list a')
        self.assertGreaterEqual(len(drawer_links), 5, "Expected at least 5 navigation links in mobile drawer")
        hrefs = [a.get_attr('href') for a in drawer_links]
        self.assertIn('index.html', hrefs)
        self.assertIn('products.html', hrefs)
        self.assertIn('our-farms.html', hrefs)
        self.assertIn('store-locator.html', hrefs)

    def test_f02_04_drawer_carton_shortcuts_grid(self):
        dom = self.client.parse_dom('index.html')
        cartons = dom.select('.drawer-carton-item')
        self.assertEqual(len(cartons), 4, "Expected exactly 4 carton shortcuts in mobile drawer")
        for item in cartons:
            img = item.find(tag='img')
            self.assertIsNotNone(img, "Carton shortcut missing image")
            resp = self.client.get(img.get_attr('src'))
            self.assertHttpStatus(resp, 200)

    def test_f02_05_drawer_social_channel_links(self):
        dom = self.client.parse_dom('index.html')
        socials = dom.select('.drawer-social-btn')
        self.assertGreaterEqual(len(socials), 4, "Expected at least 4 social channel buttons in drawer")


class TestTier1_F03_Footer(E2ETestBase):
    """Feature 3: Unified Footer & Legal Modals"""

    def test_f03_01_footer_presence_and_branding(self):
        pages = ['index.html', 'products.html', 'our-farms.html', 'recipes.html', 'store-locator.html']
        for page in pages:
            dom = self.client.parse_dom(page)
            footer = self.assertDOMExists(dom, 'footer.site-footer', f"Footer missing on {page}")
            self.assertTrue(
                "SUREGROW FARMS" in footer.text or "Nutrifresh Eggs" in footer.text,
                f"Footer branding text missing on {page}"
            )

    def test_f03_02_footer_navigation_columns(self):
        dom = self.client.parse_dom('index.html')
        cols = dom.select('.footer-top .footer-col')
        self.assertGreaterEqual(len(cols), 3, "Expected at least 3 footer columns")

    def test_f03_03_footer_newsletter_form(self):
        dom = self.client.parse_dom('index.html')
        form = dom.select_one('.newsletter-form') or dom.select_one('#footerNewsletter')
        self.assertIsNotNone(form, "Newsletter form missing in footer")
        email_input = form.find(tag='input', attr_name='type', attr_val='email')
        self.assertIsNotNone(email_input, "Newsletter email input missing")
        self.assertTrue(email_input.has_attr('required'), "Newsletter email input must be required")

    def test_f03_04_footer_social_links_integrity(self):
        dom = self.client.parse_dom('index.html')
        insta_links = dom.select('a[href*="instagram.com"]')
        self.assertGreaterEqual(len(insta_links), 1, "Instagram link missing in footer or page")
        for link in insta_links:
            self.assertEqual(link.get_attr('target'), '_blank', "External social link must have target='_blank'")
            self.assertTrue('noopener' in link.get_attr('rel', ''), "External social link must have rel='noopener'")

    def test_f03_05_footer_copyright_statement(self):
        pages = ['index.html', 'products.html', 'our-farms.html', 'recipes.html', 'store-locator.html']
        for page in pages:
            dom = self.client.parse_dom(page)
            footer_bottom = self.assertDOMExists(dom, '.footer-bottom', f"footer-bottom missing on {page}")
            self.assertIn("2026", footer_bottom.text, f"Copyright year 2026 missing on {page}")


class TestTier1_F04_Brand(E2ETestBase):
    """Feature 4: Brand Consistency & Favicons"""

    def test_f04_01_meta_charset_and_viewport(self):
        pages = ['index.html', 'products.html', 'our-farms.html', 'recipes.html', 'store-locator.html']
        for page in pages:
            dom = self.client.parse_dom(page)
            charset = dom.select_one('meta[charset]')
            self.assertIsNotNone(charset, f"meta charset missing on {page}")
            viewport = dom.select_one('meta[name="viewport"]')
            self.assertIsNotNone(viewport, f"meta viewport missing on {page}")

    def test_f04_02_document_title_brand_uniformity(self):
        pages = ['index.html', 'products.html', 'our-farms.html', 'recipes.html', 'store-locator.html']
        for page in pages:
            dom = self.client.parse_dom(page)
            title = dom.select_one('title')
            self.assertIsNotNone(title, f"Document title missing on {page}")
            self.assertIn("Nutrifresh Eggs", title.text, f"Nutrifresh Eggs missing in title on {page}")

    def test_f04_03_google_fonts_and_stylesheet_links(self):
        pages = ['index.html', 'products.html', 'our-farms.html', 'recipes.html', 'store-locator.html']
        for page in pages:
            dom = self.client.parse_dom(page)
            css_link = dom.select_one('link[rel="stylesheet"][href="styles.css"]')
            self.assertIsNotNone(css_link, f"styles.css link tag missing on {page}")

    def test_f04_04_brand_color_tokens_in_css(self):
        resp = self.client.get('styles.css')
        self.assertHttpStatus(resp, 200)
        self.assertIn("--primary-yellow", resp.text)
        self.assertIn("#FFB71B", resp.text)
        self.assertIn("--yolk-orange", resp.text)
        self.assertIn("#FF5700", resp.text)
        self.assertIn("--deep-navy", resp.text)

    def test_f04_05_floating_store_cta_presence(self):
        dom = self.client.parse_dom('index.html')
        floating_cta = self.assertDOMExists(dom, '.floating-cta-btn', "Floating CTA button missing on index.html")
        self.assertEqual(floating_cta.get_attr('href'), 'store-locator.html')


class TestTier1_F05_HeroVideo(E2ETestBase):
    """Feature 5: Video Hero Section & Audio Toggle"""

    def test_f05_01_video_element_markup(self):
        dom = self.client.parse_dom('index.html')
        video = self.assertDOMExists(dom, 'video.hero-video', "Hero video element missing")
        self.assertTrue(video.has_attr('autoplay'))
        self.assertTrue(video.has_attr('loop'))
        self.assertTrue(video.has_attr('muted'))
        self.assertTrue(video.has_attr('playsinline'))

    def test_f05_02_video_source_integrity(self):
        dom = self.client.parse_dom('index.html')
        source = dom.select_one('video.hero-video source')
        self.assertIsNotNone(source, "Video source tag missing")
        self.assertEqual(source.get_attr('src'), 'assets/videos/nutrifresh-hero.mp4')
        self.assertEqual(source.get_attr('type'), 'video/mp4')

    def test_f05_03_hero_video_file_serving(self):
        resp = self.client.head('assets/videos/nutrifresh-hero.mp4')
        self.assertHttpStatus(resp, 200)
        self.assertContentType(resp, 'video/mp4')
        self.assertEqual(resp.get_header('accept-ranges'), 'bytes')

    def test_f05_04_curved_svg_headline(self):
        dom = self.client.parse_dom('index.html')
        svg = self.assertDOMExists(dom, 'svg.curved-headline-svg', "Curved SVG headline missing")
        self.assertIn("CHOOSE NUTRIFRESH", svg.text)

    def test_f05_05_sound_toggle_button(self):
        dom = self.client.parse_dom('index.html')
        btn = self.assertDOMExists(dom, '.hero-sound-toggle', "Hero sound toggle button missing")
        self.assertTrue(btn.has_attr('aria-label'))
        self.assertIn("Sound Muted", btn.text)


class TestTier1_F06_FarmIntegrity(E2ETestBase):
    """Feature 6: Farm Integrity & Nutrition Cards"""

    def test_f06_01_four_pillar_farm_path_grid(self):
        dom = self.client.parse_dom('index.html')
        cards = dom.select('.farm-path-section .path-card')
        self.assertEqual(len(cards), 4, "Expected exactly 4 pillar cards in .farm-path-section")

    def test_f06_02_pillar_step_badges(self):
        dom = self.client.parse_dom('index.html')
        badges = dom.select('.path-step-badge')
        self.assertEqual(len(badges), 4)
        badge_texts = [b.text for b in badges]
        self.assertEqual(badge_texts, ['1', '2', '3', '4'])

    def test_f06_03_five_nutrition_fact_cards(self):
        dom = self.client.parse_dom('index.html')
        facts = dom.select('.nutrition-power-section .nutrition-fact-card')
        self.assertEqual(len(facts), 5, "Expected exactly 5 nutrition fact cards")

    def test_f06_04_nutrition_metrics_content(self):
        dom = self.client.parse_dom('index.html')
        facts = dom.select('.nutrition-power-section .nutrition-fact-card')
        stats_text = ' '.join([f.text for f in facts])
        self.assertIn("⅓ Less", stats_text)
        self.assertIn("¼ Less", stats_text)
        self.assertIn("⅔ More", stats_text)
        self.assertIn("3x More", stats_text)
        self.assertIn("7x More", stats_text)

    def test_f06_05_official_brand_card_image(self):
        dom = self.client.parse_dom('index.html')
        brand_card = self.assertDOMExists(dom, '.official-brand-card-img', "Official brand card image missing")
        resp = self.client.get(brand_card.get_attr('src'))
        self.assertHttpStatus(resp, 200)


class TestTier1_F07_ProductCarousel(E2ETestBase):
    """Feature 7: Interactive Product Carousel"""

    def test_f07_01_carousel_track_and_four_cards(self):
        dom = self.client.parse_dom('index.html')
        cards = dom.select('.carousel-track .product-card')
        self.assertEqual(len(cards), 4, "Expected 4 product cards in carousel")

    def test_f07_02_carousel_navigation_controls(self):
        dom = self.client.parse_dom('index.html')
        prev_btn = self.assertDOMExists(dom, '.carousel-prev', "Carousel prev button missing")
        next_btn = self.assertDOMExists(dom, '.carousel-next', "Carousel next button missing")
        self.assertTrue(prev_btn.has_attr('aria-label'))
        self.assertTrue(next_btn.has_attr('aria-label'))

    def test_f07_03_product_card_badges(self):
        dom = self.client.parse_dom('index.html')
        cards = dom.select('.carousel-track .product-card')
        badges = [c.find(class_name='product-card-badge').text for c in cards if c.find(class_name='product-card-badge')]
        self.assertEqual(len(badges), 4)
        self.assertIn("Signature Heritage", badges)
        self.assertIn("Customer Favorite", badges)
        self.assertIn("USDA Organic", badges)
        self.assertIn("Everyday Classic", badges)

    def test_f07_04_product_card_ratings_and_stars(self):
        dom = self.client.parse_dom('index.html')
        ratings = dom.select('.carousel-track .product-rating')
        self.assertEqual(len(ratings), 4)
        for r in ratings:
            self.assertIn("★★★★★", r.text)

    def test_f07_05_product_card_action_buttons(self):
        dom = self.client.parse_dom('index.html')
        cards = dom.select('.carousel-track .product-card')
        for card in cards:
            store_btn = card.find(class_name='btn-primary')
            self.assertIsNotNone(store_btn)
            self.assertEqual(store_btn.get_attr('href'), 'store-locator.html')
            details_btn = card.find(class_name='btn-outline')
            self.assertIsNotNone(details_btn)
            self.assertTrue(details_btn.get_attr('href').startswith('products.html#'))


class TestTier1_F08_YolkSlider(E2ETestBase):
    """Feature 8: 15-Grade Dynamic Yolk Slider"""

    def test_f08_01_slider_input_element(self):
        dom = self.client.parse_dom('index.html')
        slider = self.assertDOMExists(dom, '#yolkGradeSlider', "Yolk grade slider input missing")
        self.assertEqual(slider.get_attr('type'), 'range')
        self.assertEqual(slider.get_attr('min'), '1')
        self.assertEqual(slider.get_attr('max'), '15')
        self.assertEqual(slider.get_attr('value'), '15')
        self.assertEqual(slider.get_attr('step'), '1')

    def test_f08_02_dynamic_yolk_dome_visual(self):
        dom = self.client.parse_dom('index.html')
        self.assertDOMExists(dom, '.egg-white-base', "Egg white base element missing")
        self.assertDOMExists(dom, '.dynamic-yolk-dome', "Dynamic yolk dome element missing")

    def test_f08_03_yolk_grade_pill_display(self):
        dom = self.client.parse_dom('index.html')
        val_span = self.assertDOMExists(dom, '#yolkGradeValue', "Yolk grade value span missing")
        self.assertEqual(val_span.text, "15")

    def test_f08_04_yolk_info_panel_titles(self):
        dom = self.client.parse_dom('index.html')
        title = self.assertDOMExists(dom, '#yolkGradeTitle', "Yolk grade title missing")
        self.assertIn("Grade 15", title.text)
        desc = self.assertDOMExists(dom, '#yolkGradeDescription', "Yolk grade description missing")
        self.assertIn("sunset amber", desc.text.lower())

    def test_f08_05_side_by_side_photo_comparison(self):
        dom = self.client.parse_dom('index.html')
        comp_img = self.assertDOMExists(dom, '.yolk-real-comparison img', "Yolk comparison image missing")
        resp = self.client.get(comp_img.get_attr('src'))
        self.assertHttpStatus(resp, 200)


class TestTier1_F09_StatsCounter(E2ETestBase):
    """Feature 9: Animated Stats Counters"""

    def test_f09_01_stats_grid_presence(self):
        dom = self.client.parse_dom('index.html')
        self.assertDOMExists(dom, '.stats-counter-section .stats-grid', "Stats grid missing")

    def test_f09_02_data_target_attributes(self):
        dom = self.client.parse_dom('index.html')
        counters = dom.select('.stat-counter-num')
        self.assertEqual(len(counters), 4, "Expected 4 stat counters")
        targets = [c.get_attr('data-target') for c in counters]
        self.assertEqual(targets, ['75', '21.8', '100', '850'])

    def test_f09_03_stats_metric_labels(self):
        dom = self.client.parse_dom('index.html')
        titles = [t.text for t in dom.select('.stat-title')]
        self.assertEqual(len(titles), 4)
        self.assertIn("Small Family Farms", titles)
        self.assertIn("Pasture Per Hen", titles)
        self.assertIn("Hormone & Antibiotic Free", titles)
        self.assertIn("Acres of Open Green Land", titles)

    def test_f09_04_decimal_target_support(self):
        dom = self.client.parse_dom('index.html')
        pasture_counter = dom.select_one('.stat-counter-num[data-target="21.8"]')
        self.assertIsNotNone(pasture_counter, "Decimal target 21.8 counter missing")

    def test_f09_05_initial_counter_zero_display(self):
        dom = self.client.parse_dom('index.html')
        for c in dom.select('.stat-counter-num'):
            self.assertEqual(c.text, "0", "Initial counter text must be 0 before observer animation")


class TestTier1_F10_RecipeTeasers(E2ETestBase):
    """Feature 10: Home Recipe Teasers & Reviews"""

    def test_f10_01_reviews_cloud_cards(self):
        dom = self.client.parse_dom('index.html')
        reviews = dom.select('.reviews-grid .review-card')
        self.assertEqual(len(reviews), 3, "Expected 3 review cards in review cloud")

    def test_f10_02_review_authors_and_citations(self):
        dom = self.client.parse_dom('index.html')
        reviews = dom.select('.reviews-grid .review-card')
        authors = [r.find(class_name='reviewer-info').find(tag='h4').text for r in reviews]
        self.assertIn("Chef Marcus W.", authors)
        self.assertIn("Sarah Jenkins", authors)
        self.assertIn("David Ross", authors)

    def test_f10_03_home_recipe_teasers_three_cards(self):
        dom = self.client.parse_dom('index.html')
        teasers = dom.select('.recipes-section .recipe-card')
        self.assertEqual(len(teasers), 3, "Expected 3 recipe teasers on home page")

    def test_f10_04_recipe_teaser_time_badges(self):
        dom = self.client.parse_dom('index.html')
        badges = dom.select('.recipes-section .recipe-time-badge')
        self.assertEqual(len(badges), 3)
        times = [b.text for b in badges]
        self.assertIn("⏱ 10 Mins", times)
        self.assertIn("⏱ 20 Mins", times)
        self.assertIn("⏱ 25 Mins", times)

    def test_f10_05_recipe_teaser_images_serving(self):
        dom = self.client.parse_dom('index.html')
        images = dom.select('.recipes-section .recipe-img-holder img')
        for img in images:
            resp = self.client.get(img.get_attr('src'))
            self.assertHttpStatus(resp, 200)


class TestTier1_F11_ProductsShowcase(E2ETestBase):
    """Feature 11: Products Showcase & Nutrition"""

    def test_f11_01_products_page_hero_h1(self):
        dom = self.client.parse_dom('products.html')
        h1 = self.assertDOMExists(dom, '.page-hero h1', "Products page H1 missing")
        self.assertEqual(h1.text, "Our Signature Cartons")

    def test_f11_02_four_carton_sections(self):
        dom = self.client.parse_dom('products.html')
        sections = dom.select('.product-detail-card')
        self.assertEqual(len(sections), 4, "Expected 4 product detail sections")
        ids = [s.get_id() for s in sections]
        self.assertEqual(ids, ['heritage', 'pasture', 'organic', 'freerange'])

    def test_f11_03_nutrition_pill_grids(self):
        dom = self.client.parse_dom('products.html')
        sections = dom.select('.product-detail-card')
        for s in sections:
            pills = s.find_all(class_name='nutrition-pill')
            self.assertEqual(len(pills), 4, f"Expected 4 nutrition pills in section {s.get_id()}")

    def test_f11_04_carton_images_loading(self):
        dom = self.client.parse_dom('products.html')
        images = dom.select('.product-detail-img-wrap img')
        self.assertEqual(len(images), 4)
        for img in images:
            resp = self.client.get(img.get_attr('src'))
            self.assertHttpStatus(resp, 200)

    def test_f11_05_find_in_store_buttons(self):
        dom = self.client.parse_dom('products.html')
        buy_links = dom.select('.product-detail-card a[href="store-locator.html"]')
        self.assertGreaterEqual(len(buy_links), 4, "Every carton section must have a store locator CTA")


class TestTier1_F12_OurFarmsStory(E2ETestBase):
    """Feature 12: Our Farms Storytelling & Standards"""

    def test_f12_01_page_hero_and_mission(self):
        dom = self.client.parse_dom('our-farms.html')
        h1 = self.assertDOMExists(dom, '.page-hero h1')
        self.assertEqual(h1.text, "Farming with Integrity")
        self.assertIn("SUREGROW FARMS", dom.select_one('.page-hero').text)

    def test_f12_02_farm_story_blocks_presence(self):
        dom = self.client.parse_dom('our-farms.html')
        blocks = dom.select('.farm-story-block')
        self.assertGreaterEqual(len(blocks), 2, "Expected at least 2 farm storytelling blocks")

    def test_f12_03_farm_badge_boxes(self):
        dom = self.client.parse_dom('our-farms.html')
        badges = dom.select('.farm-badge-box')
        self.assertEqual(len(badges), 2)
        badge_text = ' '.join([b.text for b in badges])
        self.assertIn("Only Female Hens", badge_text)
        self.assertIn("100% Vegetarian Feed", badge_text)

    def test_f12_04_farm_photography_assets(self):
        dom = self.client.parse_dom('our-farms.html')
        images = dom.select('.farm-story-block img')
        self.assertGreaterEqual(len(images), 2)
        for img in images:
            resp = self.client.get(img.get_attr('src'))
            self.assertHttpStatus(resp, 200)

    def test_f12_05_nutrition_highlights_on_our_farms(self):
        dom = self.client.parse_dom('our-farms.html')
        facts = dom.select('.nutrition-facts-grid .nutrition-fact-card')
        self.assertEqual(len(facts), 5, "Expected 5 nutrition fact cards on our-farms.html")


class TestTier1_F13_RecipesFilter(E2ETestBase):
    """Feature 13: Recipes Filtering & Search"""

    def test_f13_01_filter_tabs_bar_structure(self):
        dom = self.client.parse_dom('recipes.html')
        btns = dom.select('.recipe-filter-btn')
        self.assertEqual(len(btns), 4, "Expected 4 recipe filter tab buttons")
        filters = [b.get_attr('data-filter') for b in btns]
        self.assertEqual(filters, ['all', 'brunch', 'quick', 'baking'])

    def test_f13_02_initial_active_tab(self):
        dom = self.client.parse_dom('recipes.html')
        active_btn = dom.select_one('.recipe-filter-btn.active')
        self.assertIsNotNone(active_btn, "Active recipe filter button missing")
        self.assertEqual(active_btn.get_attr('data-filter'), 'all')

    def test_f13_03_six_recipe_cards_in_grid(self):
        dom = self.client.parse_dom('recipes.html')
        cards = dom.select('#recipeCardsGrid .recipe-card')
        self.assertEqual(len(cards), 6, "Expected exactly 6 recipe cards in recipes.html")

    def test_f13_04_recipe_card_categories(self):
        dom = self.client.parse_dom('recipes.html')
        cards = dom.select('#recipeCardsGrid .recipe-card')
        cats = [c.get_attr('data-category') for c in cards]
        self.assertEqual(cats.count('brunch'), 2)
        self.assertEqual(cats.count('quick'), 2)
        self.assertEqual(cats.count('baking'), 2)

    def test_f13_05_recipe_card_images_and_time_badges(self):
        dom = self.client.parse_dom('recipes.html')
        cards = dom.select('#recipeCardsGrid .recipe-card')
        self.assertEqual(len(cards), 6)
        for card in cards:
            img = card.find(tag='img')
            self.assertIsNotNone(img, "Recipe card missing image element")
            self.assertTrue(img.has_attr('src'), "Recipe card image missing src")
            self.assertTrue(img.has_attr('alt'), "Recipe card image missing alt text")
            time_badge = card.find(class_name='recipe-time-badge')
            self.assertIsNotNone(time_badge, "Recipe card missing time badge")


class TestTier1_F14_RecipeModal(E2ETestBase):
    """Feature 14: Interactive Recipe Modal"""

    def test_f14_01_modal_overlay_and_content_container(self):
        dom = self.client.parse_dom('recipes.html')
        self.assertDOMExists(dom, '#recipeModalOverlay', "Recipe modal overlay missing")
        self.assertDOMExists(dom, '#recipeModalContent', "Recipe modal content injection container missing")

    def test_f14_02_modal_close_button(self):
        dom = self.client.parse_dom('recipes.html')
        close_btn = self.assertDOMExists(dom, '#closeRecipeModal', "Recipe modal close button missing")
        self.assertIn("✕", close_btn.text)

    def test_f14_03_six_recipe_open_buttons(self):
        dom = self.client.parse_dom('recipes.html')
        open_btns = dom.select('.open-recipe-modal')
        self.assertEqual(len(open_btns), 6, "Expected 6 recipe modal trigger buttons")
        recipes = [b.get_attr('data-recipe') for b in open_btns]
        self.assertEqual(recipes, ['benedict', 'tacos', 'shakshuka', 'curd', 'tartine', 'omelette'])

    def test_f14_04_appjs_contains_all_six_recipe_objects(self):
        resp = self.client.get('app.js')
        self.assertHttpStatus(resp, 200)
        for r_id in ['benedict', 'tacos', 'shakshuka', 'curd', 'tartine', 'omelette']:
            self.assertIn(f"{r_id}:", resp.text, f"Recipe database key {r_id} missing in app.js")

    def test_f14_05_recipe_database_ingredients_and_steps_fields(self):
        resp = self.client.get('app.js')
        self.assertIn("ingredients:", resp.text)
        self.assertIn("steps:", resp.text)
        self.assertIn("Nutrifresh Heritage Breed eggs", resp.text)


class TestTier1_F15_StoreLocator(E2ETestBase):
    """Feature 15: Store Locator Search & Map"""

    def test_f15_01_search_input_and_button(self):
        dom = self.client.parse_dom('store-locator.html')
        inp = self.assertDOMExists(dom, '#storeSearchInput', "Store search input missing")
        self.assertDOMExists(dom, '#storeSearchBtn', "Store search button missing")

    def test_f15_02_store_carton_filter_pills(self):
        dom = self.client.parse_dom('store-locator.html')
        filters = dom.select('.locator-filters .filter-btn')
        self.assertEqual(len(filters), 4, "Expected 4 carton filter buttons in store locator")
        filter_texts = [f.text for f in filters]
        self.assertIn("All Cartons", filter_texts)
        self.assertIn("Heritage Amber", filter_texts)
        self.assertIn("Pasture Raised", filter_texts)
        self.assertIn("Organic Free Range", filter_texts)

    def test_f15_03_store_results_list_container(self):
        dom = self.client.parse_dom('store-locator.html')
        self.assertDOMExists(dom, '#storeResultsList', "Store results container missing")

    def test_f15_04_interactive_svg_map_element(self):
        dom = self.client.parse_dom('store-locator.html')
        svg = self.assertDOMExists(dom, 'svg.map-svg-mockup', "Interactive SVG map missing")
        self.assertEqual(svg.get_attr('viewbox'), '0 0 800 600')

    def test_f15_05_five_map_pins_with_numbers(self):
        dom = self.client.parse_dom('store-locator.html')
        pins = dom.select('svg.map-svg-mockup .map-pin')
        self.assertEqual(len(pins), 5, "Expected 5 store map pins on SVG map")


class TestTier1_F16_ServerStreaming(E2ETestBase):
    """Feature 16: Local Server HTTP & Video Streaming"""

    def test_f16_01_root_path_index_serving(self):
        resp = self.client.get('/')
        self.assertHttpStatus(resp, 200)
        self.assertContentType(resp, 'text/html')
        self.assertIn("<!DOCTYPE html>", resp.text)

    def test_f16_02_all_core_html_routes(self):
        pages = ['index.html', 'products.html', 'our-farms.html', 'recipes.html', 'store-locator.html']
        for page in pages:
            resp = self.client.get(page)
            self.assertHttpStatus(resp, 200, f"Failed to get {page}")
            self.assertContentType(resp, 'text/html')

    def test_f16_03_static_assets_mime_types(self):
        css_resp = self.client.get('styles.css')
        self.assertHttpStatus(css_resp, 200)
        self.assertContentType(css_resp, 'text/css')

        js_resp = self.client.get('app.js')
        self.assertHttpStatus(js_resp, 200)
        self.assertContentType(js_resp, 'application/javascript')

    def test_f16_04_http206_byte_range_streaming(self):
        resp = self.client.get_byte_range('assets/videos/nutrifresh-hero.mp4', 0, 1023)
        self.assertHttpStatus(resp, 206)
        self.assertContentType(resp, 'video/mp4')
        self.assertEqual(len(resp.body), 1024)
        self.assertTrue(resp.content_range.startswith('bytes 0-1023/'))

    def test_f16_05_http404_on_nonexistent_route(self):
        resp = self.client.get('nonexistent-page-test-404.html')
        self.assertHttpStatus(resp, 404)


class TestTier1_F17_BecomeAFarmer(E2ETestBase):
    """Feature 17: Become a Farmer Page & Application Workflow"""

    def test_f17_01_farmer_page_loads_cleanly(self):
        resp = self.client.get('become-a-farmer.html')
        self.assertHttpStatus(resp, 200)
        dom = self.client.parse_dom('become-a-farmer.html')
        h1 = self.assertDOMExists(dom, '.farmer-hero-content h1')
        self.assertIn("become a happy egg farmer", h1.text.lower())

    def test_f17_02_farmer_pillars_and_cards(self):
        dom = self.client.parse_dom('become-a-farmer.html')
        cards = dom.select('.farmer-card')
        self.assertEqual(len(cards), 4, "Expected 4 farmer highlights cards")
        pillars = dom.select('.pillar-col')
        self.assertEqual(len(pillars), 3, "Expected 3 core pillars")

    def test_f17_03_farmer_application_form_elements(self):
        dom = self.client.parse_dom('become-a-farmer.html')
        form = self.assertDOMExists(dom, '#farmerApplicationForm')
        self.assertIsNotNone(form)
        self.assertIsNotNone(dom.select_one('#btnExistingFarmer'))
        self.assertIsNotNone(dom.select_one('#btnNewFarmer'))
        self.assertIsNotNone(dom.select_one('#newFarmerChecklist'))

    def test_f17_04_farmer_faqs_accordion(self):
        dom = self.client.parse_dom('become-a-farmer.html')
        faqs = dom.select('.faq-accordion-item')
        self.assertEqual(len(faqs), 5, "Expected 5 FAQ accordion items on become-a-farmer.html")


class TestTier1_F18_OrderOnline(E2ETestBase):
    """Feature 18: Order Online Cart & Dual Checkout"""

    def test_f18_01_order_online_page_loads(self):
        resp = self.client.get('order-online.html')
        self.assertHttpStatus(resp, 200)
        dom = self.client.parse_dom('order-online.html')
        h1 = self.assertDOMExists(dom, '.order-hero-section h1')
        self.assertIn("order nutrifresh eggs online", h1.text.lower())

    def test_f18_02_product_selection_cards(self):
        dom = self.client.parse_dom('order-online.html')
        products = dom.select('.order-item-card')
        self.assertEqual(len(products), 4, "Expected 4 order item carton cards")

    def test_f18_03_cart_sidebar_and_checkout_buttons(self):
        dom = self.client.parse_dom('order-online.html')
        self.assertIsNotNone(dom.select_one('#cartStickyBox'))
        self.assertIsNotNone(dom.select_one('#btnOrderWhatsApp'))
        self.assertIsNotNone(dom.select_one('#btnPayOnline'))
        self.assertIsNotNone(dom.select_one('#paymentGatewayModal'))


if __name__ == '__main__':
    unittest.main()

