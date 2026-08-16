# E2E Test Infra: NutriFresh Eggs Multi-Page Website

## Test Philosophy
- **Opaque-box, requirement-driven**: Tests derive strictly from `ORIGINAL_REQUEST.md` and user specifications, evaluating the application as real users and automated clients do over HTTP.
- **Methodology**: Category-Partition + Boundary Value Analysis (BVA) + Pairwise Combinatorial Testing + Real-World Workload Testing.
- **Independence**: Test verification mechanisms do not assume or modify internal code representations.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 | Tier 2 | Tier 3 |
|---|---------|---------------------|:------:|:------:|:------:|
| 1 | Global Header & Navigation | ORIGINAL_REQUEST §R2 | 5 | 5 | ✓ |
| 2 | Mobile Navigation Drawer | ORIGINAL_REQUEST §R2 | 5 | 5 | ✓ |
| 3 | Unified Footer & Legal Modals | ORIGINAL_REQUEST §R1, §R2 | 5 | 5 | ✓ |
| 4 | Brand Consistency & Favicons | ORIGINAL_REQUEST §R1, §R3 | 5 | 5 | ✓ |
| 5 | Video Hero Section & Audio Toggle | ORIGINAL_REQUEST §R1, §Constraint | 5 | 5 | ✓ |
| 6 | Farm Integrity & Nutrition Cards | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ |
| 7 | Interactive Product Carousel | ORIGINAL_REQUEST §R1, §R2 | 5 | 5 | ✓ |
| 8 | 15-Grade Dynamic Yolk Slider | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ |
| 9 | Animated Stats Counters | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ |
| 10 | Home Recipe Teasers & Reviews | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ |
| 11 | Products Showcase & Nutrition | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ |
| 12 | Our Farms Storytelling & Standards | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ |
| 13 | Recipes Filtering & Search | ORIGINAL_REQUEST §R1, §R2 | 5 | 5 | ✓ |
| 14 | Interactive Recipe Modal | ORIGINAL_REQUEST §R1, §R2 | 5 | 5 | ✓ |
| 15 | Store Locator Search & Map | ORIGINAL_REQUEST §R1, §R2 | 5 | 5 | ✓ |
| 16 | Local Server HTTP & Video Streaming | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ |

## Test Architecture
- **Test Runner**:
  - Location: `tests/run_all.py` (and discoverable via `python -m unittest discover -s tests`)
  - Invocation: `python tests/run_all.py`
  - Pass/Fail Semantics: Exit code 0 on 100% pass, non-zero exit code on any failure, with detailed error diagnostics.
- **Directory Layout**:
  - `tests/`
    - `run_all.py`: Master test runner with colorized reporting and tier breakdowns
    - `test_helper.py`: Common HTTP client, HTML parser, DOM traversal, and asset validation utilities
    - `test_tier1_features.py`: >=80 Tier 1 Feature Coverage tests (>=5 tests across all 16 features)
    - `test_tier2_boundaries.py`: >=80 Tier 2 Boundary & Corner Case tests
    - `test_tier3_combinations.py`: >=16 Tier 3 Cross-Feature Combination tests
    - `test_tier4_scenarios.py`: >=6 Tier 4 Real-World Application User Journey tests

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Consumer Journey: Home Discovery to Store Purchase | Hero, Carousel, Yolk Slider, Store Finder, Map Pins | High |
| 2 | Culinary Flow: Recipe Search, Filter, Modal Checklist to Where-to-Buy | Search, Tabs, Modal, Ingredient Checks, Locator | High |
| 3 | Mobile Visitor Experience: Drawer Navigation, Responsive Inspection | Hamburger, Drawer, Page Transitions, Viewport Layout | Medium |
| 4 | Brand Deep-Dive: Storytelling, Pasture Standards & Nutritional Proof | Our Farms, 21.8 sq ft metrics, Farmer Spotlight, Nutrition Table | Medium |
| 5 | Video Asset Streaming & HTTP Protocol Conformance | Video Hero, Byte-Range HTTP 206, Content-Types, Asset Caching | Medium |
| 6 | Robustness & Error Recovery Journey | Invalid Zip, Out-of-Bounds Slider, Rapid Tab Switch, Empty Search | High |

## Coverage Thresholds
- Tier 1: ≥5 test cases per feature (16 features × 5 = ≥80 tests)
- Tier 2: ≥5 test cases per feature (16 features × 5 = ≥80 tests)
- Tier 3: ≥16 cross-feature pairwise interaction test cases
- Tier 4: ≥6 complete real-world application user journey scenarios
- **Total Suite Minimum**: ≥182 automated test cases
