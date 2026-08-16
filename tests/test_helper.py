"""
NutriFresh Eggs E2E Test Suite - Core Test Helper
Provides HTTP test client, HTML DOM parser, query engine, asset crawler,
and JavaScript logic simulators for pure Python 3 standard library E2E testing.
"""

import os
import sys
import re
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import http.client
from html.parser import HTMLParser
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEFAULT_BASE_URL = os.environ.get('NUTRIFRESH_BASE_URL', 'http://127.0.0.1:3000')


# ============================================================================
# 1. DOM Tree Model & HTML Parser
# ============================================================================

class DOMNode:
    """Represents an HTML element node in the parsed document tree."""
    def __init__(self, tag: str, attrs: dict, parent: 'DOMNode' = None):
        self.tag = tag.lower()
        self.attrs = {k.lower(): v for k, v in attrs.items()}
        self.parent = parent
        self.children: list['DOMNode'] = []
        self.text_chunks: list[str] = []
        self.is_self_closing = False

    @property
    def text(self) -> str:
        """Returns the concatenated textual content of this node and all descendants."""
        chunks = list(self.text_chunks)
        for child in self.children:
            chunks.append(child.text)
        return ' '.join(' '.join(chunks).split())

    def get_attr(self, name: str, default: str = None) -> str:
        return self.attrs.get(name.lower(), default)

    def has_attr(self, name: str) -> bool:
        return name.lower() in self.attrs

    def has_class(self, class_name: str) -> bool:
        classes = self.attrs.get('class', '').split()
        return class_name in classes

    def get_id(self) -> str:
        return self.attrs.get('id', '')

    def find_all(self, tag: str = None, class_name: str = None, id_name: str = None,
                 attr_name: str = None, attr_val: str = None) -> list['DOMNode']:
        """Recursively finds all matching DOM nodes."""
        results = []
        matches = True

        if tag and self.tag != tag.lower():
            matches = False
        if class_name and not self.has_class(class_name):
            matches = False
        if id_name and self.get_id() != id_name:
            matches = False
        if attr_name:
            if attr_val is not None:
                if self.get_attr(attr_name) != attr_val:
                    matches = False
            else:
                if not self.has_attr(attr_name):
                    matches = False

        if matches and self.tag != 'document_root':
            results.append(self)

        for child in self.children:
            results.extend(child.find_all(tag, class_name, id_name, attr_name, attr_val))

        return results

    def find(self, tag: str = None, class_name: str = None, id_name: str = None,
             attr_name: str = None, attr_val: str = None) -> 'DOMNode':
        matches = self.find_all(tag, class_name, id_name, attr_name, attr_val)
        return matches[0] if matches else None

    def __repr__(self):
        class_str = f" class='{self.get_attr('class')}'" if self.has_attr('class') else ""
        id_str = f" id='{self.get_id()}'" if self.get_id() else ""
        return f"<{self.tag}{id_str}{class_str}>"


class SimpleDOMParser(HTMLParser):
    """HTMLParser that builds a hierarchical DOMNode tree."""
    SELF_CLOSING_TAGS = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr',
        'circle', 'rect', 'path', 'line', 'polygon', 'polyline', 'stop', 'use'
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = DOMNode('document_root', {})
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        node = DOMNode(tag, attr_dict, parent=self.current)
        self.current.children.append(node)
        if tag.lower() not in self.SELF_CLOSING_TAGS:
            self.current = node
        else:
            node.is_self_closing = True

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in self.SELF_CLOSING_TAGS:
            return
        curr = self.current
        while curr and curr.tag != 'document_root':
            if curr.tag == tag_lower:
                self.current = curr.parent if curr.parent else self.root
                return
            curr = curr.parent

    def handle_data(self, data):
        if data.strip():
            self.current.text_chunks.append(data.strip())


class DOMQueryEngine:
    """CSS-like query selector wrapper over parsed DOMNode tree."""
    def __init__(self, root: DOMNode):
        self.root = root

    @classmethod
    def parse_html(cls, html_content: str) -> 'DOMQueryEngine':
        parser = SimpleDOMParser()
        parser.feed(html_content)
        return cls(parser.root)

    def select(self, selector: str) -> list[DOMNode]:
        """Supports single, compound, and descendant CSS selectors."""
        selector = selector.strip()
        parts = selector.split()
        if not parts:
            return []

        current_nodes = [self.root]
        for part in parts:
            next_nodes = []
            for node in current_nodes:
                next_nodes.extend(self._match_single_selector(node, part))
            current_nodes = next_nodes
        return current_nodes

    def select_one(self, selector: str) -> DOMNode:
        results = self.select(selector)
        return results[0] if results else None

    def _match_single_selector(self, parent: DOMNode, selector: str) -> list[DOMNode]:
        tag = None
        id_name = None
        classes = []
        attr_filters = []

        attr_matches = re.findall(r'\[([a-zA-Z0-9_\-]+)(?:([*^$]?=)["\']?([^"\'\]]*)["\']?)?\]', selector)
        for attr_name, op, attr_val in attr_matches:
            attr_filters.append((attr_name.lower(), op, attr_val))

        clean_selector = re.sub(r'\[[^\]]+\]', '', selector)

        if '#' in clean_selector:
            parts = clean_selector.split('#', 1)
            token = parts[0]
            rest = parts[1]
            if '.' in rest:
                id_name, class_part = rest.split('.', 1)
                classes.extend([c for c in class_part.split('.') if c])
            else:
                id_name = rest
            clean_selector = token

        if '.' in clean_selector:
            parts = clean_selector.split('.')
            if parts[0]:
                tag = parts[0]
            classes.extend([c for c in parts[1:] if c])
        elif clean_selector:
            tag = clean_selector

        all_candidates = parent.find_all()
        matched = []
        for cand in all_candidates:
            if tag and cand.tag != tag.lower():
                continue
            if id_name and cand.get_id() != id_name:
                continue
            if classes and not all(cand.has_class(c) for c in classes):
                continue

            attr_ok = True
            for a_name, a_op, a_val in attr_filters:
                if not cand.has_attr(a_name):
                    attr_ok = False
                    break
                actual_val = cand.get_attr(a_name, '')
                if not a_op:
                    continue
                if a_op == '=' and actual_val != a_val:
                    attr_ok = False
                    break
                elif a_op == '*=' and a_val not in actual_val:
                    attr_ok = False
                    break
                elif a_op == '^=' and not actual_val.startswith(a_val):
                    attr_ok = False
                    break
                elif a_op == '$=' and not actual_val.endswith(a_val):
                    attr_ok = False
                    break

            if attr_ok:
                matched.append(cand)
        return matched


# ============================================================================
# 2. HTTP Client & Streaming Response Wrapper
# ============================================================================

class HTTPResponseWrapper:
    """Encapsulates HTTP response data, headers, and status code."""
    def __init__(self, status: int, headers: dict, body: bytes, url: str, total_file_size: int = None):
        self.status = status
        self.headers = {k.lower(): v for k, v in headers.items()}
        self.body = body
        self.url = url
        self._total_file_size = total_file_size

    @property
    def text(self) -> str:
        return self.body.decode('utf-8', errors='replace')

    def get_header(self, name: str, default: str = None) -> str:
        return self.headers.get(name.lower(), default)

    @property
    def content_type(self) -> str:
        return self.get_header('content-type', '')

    @property
    def content_length(self) -> int:
        if self._total_file_size is not None:
            return self._total_file_size
        cl = self.get_header('content-length')
        return int(cl) if cl and cl.isdigit() else len(self.body)

    @property
    def content_range(self) -> str:
        return self.get_header('content-range', '')


class E2EHTTPClient:
    """Robust HTTP client for E2E testing against the local NutriFresh web server."""
    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = 4.0):
        if 'localhost' in base_url:
            base_url = base_url.replace('localhost', '127.0.0.1')
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def check_server_liveness(self) -> bool:
        """Verifies if the local server is reachable and active."""
        try:
            req = urllib.request.Request(self.base_url, headers={'Connection': 'close'}, method='GET')
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.status in (200, 301, 302)
        except Exception:
            return False

    def get(self, path: str = "", headers: dict = None) -> HTTPResponseWrapper:
        """Executes a GET request."""
        clean_path = path if path.startswith('http') else f"{self.base_url}/{path.lstrip('/')}"
        req_headers = {'Connection': 'close'}
        if headers:
            req_headers.update(headers)
        req = urllib.request.Request(clean_path, headers=req_headers, method='GET')

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                status = resp.status
                resp_headers = dict(resp.headers)
                body = resp.read()
                return HTTPResponseWrapper(status, resp_headers, body, clean_path)
        except urllib.error.HTTPError as e:
            resp_headers = dict(e.headers)
            body = e.read() if hasattr(e, 'read') else b""
            return HTTPResponseWrapper(e.code, resp_headers, body, clean_path)
        except Exception as e:
            return HTTPResponseWrapper(500, {}, str(e).encode('utf-8'), clean_path)

    def head(self, path: str = "", headers: dict = None) -> HTTPResponseWrapper:
        """Efficiently inspects resource headers using a 1-byte range request."""
        clean_path = path if path.startswith('http') else f"{self.base_url}/{path.lstrip('/')}"
        range_resp = self.get_byte_range(path, 0, 0)
        if range_resp.status == 206:
            total_size = None
            cr = range_resp.content_range
            if '/' in cr:
                size_str = cr.split('/')[-1]
                if size_str.isdigit():
                    total_size = int(size_str)
            return HTTPResponseWrapper(200, range_resp.headers, b"", clean_path, total_file_size=total_size)
        elif range_resp.status == 200:
            return HTTPResponseWrapper(200, range_resp.headers, b"", clean_path)
        else:
            return range_resp

    def get_byte_range(self, path: str, start: int, end: int = None) -> HTTPResponseWrapper:
        """Requests byte-range partial content (HTTP 206) using RFC 7233 Range header."""
        range_val = f"bytes={start}-{end if end is not None else ''}"
        return self.get(path, headers={'Range': range_val, 'Connection': 'close'})

    def parse_dom(self, path: str = "") -> DOMQueryEngine:
        """Fetches an HTML page and returns a DOMQueryEngine instance."""
        resp = self.get(path)
        return DOMQueryEngine.parse_html(resp.text)


# ============================================================================
# 3. JavaScript Logic Simulation Engine
# ============================================================================

class JSSimulator:
    """Pure Python simulation of client-side math and state transitions in app.js."""

    @staticmethod
    def calculate_yolk_rgb(val: int) -> tuple[int, int, int]:
        clamped_val = max(1, min(15, val))
        r = 255
        g = max(70, round(245 - (clamped_val / 15.0) * 160.0))
        b = max(10, round(180 - (clamped_val / 15.0) * 170.0))
        return (r, g, b)

    @staticmethod
    def get_yolk_tier_info(val: int) -> dict:
        nearest = 1
        if val >= 13:
            nearest = 15
        elif val >= 8:
            nearest = 10
        elif val >= 4:
            nearest = 5
        else:
            nearest = 1

        yolk_database = {
            1: {
                'title': 'Grade 1: Conventional Caged',
                'desc': 'Pale yellow, flat yolk from caged environments. Low in natural carotenoids, lutein, and omega-3 nutrients.'
            },
            5: {
                'title': 'Grade 5: Standard Cage-Free',
                'desc': 'Moderate yellow with basic roundness. Lacks rich natural outdoor foraging benefits and daily sunshine.'
            },
            10: {
                'title': 'Grade 10: Standard Free-Range',
                'desc': 'Warm golden yellow with improved dome plumpness from outdoor access and balanced grains.'
            },
            15: {
                'title': 'Grade 15: Nutrifresh Heritage Sunset Amber',
                'desc': 'Deep glowing sunset amber with a plump, creamy, rich dome. Packed with 6x Vitamin D, Xanthophylls, and rich velvety taste!'
            }
        }
        return yolk_database[nearest]

    @staticmethod
    def get_visible_cards(viewport_width: int) -> int:
        if viewport_width <= 768:
            return 1
        if viewport_width <= 1024:
            return 2
        return 3

    @staticmethod
    def calculate_carousel_index(current_idx: int, action: str, total_cards: int = 4,
                                  viewport_width: int = 1200) -> int:
        visible = JSSimulator.get_visible_cards(viewport_width)
        max_index = max(0, total_cards - visible)

        if action == 'next':
            if current_idx < max_index:
                return current_idx + 1
            else:
                return 0
        elif action == 'prev':
            return max(0, current_idx - 1)
        elif action == 'resize':
            return min(max_index, max(0, current_idx))
        return current_idx

    @staticmethod
    def filter_recipes(recipes_list: list[dict], filter_category: str) -> list[dict]:
        if filter_category == 'all':
            return recipes_list
        return [r for r in recipes_list if r.get('category') == filter_category]

    @staticmethod
    def search_stores(stores_list: list[dict], query: str = "") -> list[dict]:
        q = query.strip().lower()
        if not q:
            return stores_list
        return [
            s for s in stores_list
            if q in s['name'].lower() or q in s['city'].lower() or q in s['address'].lower()
        ]

    @staticmethod
    def filter_stores_by_carton(stores_list: list[dict], carton_filter: str) -> list[dict]:
        if carton_filter == 'All Cartons':
            return stores_list
        tag_map = {
            'Heritage Amber': ['All Cartons', 'Heritage & Pasture', 'Heritage Amber'],
            'Pasture Raised': ['All Cartons', 'Heritage & Pasture', 'Pasture Raised'],
            'Organic Free Range': ['All Cartons', 'Organic Free Range']
        }
        allowed = tag_map.get(carton_filter, [])
        return [s for s in stores_list if any(a in s['stock'] for a in allowed)]


# ============================================================================
# 4. Standard Base Test Case Class
# ============================================================================

class E2ETestBase(unittest.TestCase):
    """Base test class providing common fixtures, assertion helpers, and client."""
    client: E2EHTTPClient = None

    @classmethod
    def setUpClass(cls):
        cls.client = E2EHTTPClient(DEFAULT_BASE_URL)

    def assertHttpStatus(self, response: HTTPResponseWrapper, expected_status: int, msg: str = None):
        self.assertEqual(
            response.status, expected_status,
            msg or f"Expected HTTP {expected_status} for {response.url}, got {response.status}"
        )

    def assertContentType(self, response: HTTPResponseWrapper, expected_type_prefix: str):
        ct = response.content_type
        self.assertTrue(
            ct.startswith(expected_type_prefix),
            f"Expected Content-Type starting with '{expected_type_prefix}', got '{ct}' for {response.url}"
        )

    def assertDOMExists(self, dom: DOMQueryEngine, selector: str, msg: str = None):
        node = dom.select_one(selector)
        self.assertIsNotNone(node, msg or f"Expected DOM element matching '{selector}' to exist")
        return node

    def assertDOMCount(self, dom: DOMQueryEngine, selector: str, expected_count: int, msg: str = None):
        nodes = dom.select(selector)
        self.assertEqual(
            len(nodes), expected_count,
            msg or f"Expected {expected_count} elements matching '{selector}', found {len(nodes)}"
        )
        return nodes
