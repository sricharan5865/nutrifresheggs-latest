#!/usr/bin/env python3
"""
NutriFresh Eggs E2E Test Suite - Master Test Runner
Executes Tiers 1-4 automated test suites with colorized CLI reporting,
tier summaries, JSON export, and strict exit code semantics.
"""

import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import time
import argparse
import unittest
import json
import urllib.request

# Ensure workspace root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from tests.test_helper import E2EHTTPClient, DEFAULT_BASE_URL
import tests.test_tier1_features as tier1_module
import tests.test_tier2_boundaries as tier2_module
import tests.test_tier3_combinations as tier3_module
import tests.test_tier4_scenarios as tier4_module


# ANSI Color Codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


class CustomTestResult(unittest.TextTestResult):
    """Custom TestResult collecting detailed per-test outcomes."""
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.records = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append({
            'test': str(test),
            'status': 'PASS',
            'error': None
        })

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.records.append({
            'test': str(test),
            'status': 'FAIL',
            'error': self._exc_info_to_string(err, test)
        })

    def addError(self, test, err):
        super().addError(test, err)
        self.records.append({
            'test': str(test),
            'status': 'ERROR',
            'error': self._exc_info_to_string(err, test)
        })


def run_suite(suite: unittest.TestSuite, failfast: bool = False) -> tuple[unittest.TestResult, float]:
    """Runs a TestSuite with CustomTestResult."""
    runner = unittest.TextTestRunner(
        resultclass=CustomTestResult,
        verbosity=1,
        failfast=failfast,
        stream=open(os.devnull, 'w', encoding='utf-8')
    )
    start_time = time.time()
    result = runner.run(suite)
    elapsed = time.time() - start_time
    return result, elapsed


def main():
    parser = argparse.ArgumentParser(description="NutriFresh Eggs E2E Test Suite Runner")
    parser.add_argument("--tier", choices=["1", "2", "3", "4", "all"], default="all", help="Test tier to execute")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL of local HTTP server")
    parser.add_argument("--json", dest="json_path", help="Path to write JSON test report")
    parser.add_argument("--failfast", action="store_true", help="Stop on first failure")
    args = parser.parse_args()

    os.environ['NUTRIFRESH_BASE_URL'] = args.base_url

    print(f"\n{BOLD}{CYAN}========================================================================{RESET}")
    print(f"{BOLD}{CYAN}      NutriFresh Eggs Multi-Page Web App - E2E Test Suite Harness      {RESET}")
    print(f"{BOLD}{CYAN}========================================================================{RESET}")
    print(f"Target Server : {args.base_url}")
    print(f"Execution Tier: {args.tier.upper()}")
    print(f"Fail-Fast     : {'Enabled' if args.failfast else 'Disabled'}\n")

    # 1. Pre-flight server health check
    print(f"[*] Checking local server liveness at {args.base_url}...")
    client = E2EHTTPClient(args.base_url)
    if not client.check_server_liveness():
        print(f"\n{RED}[ERROR] Local server is unreachable at {args.base_url}.{RESET}")
        print(f"Please start the server with: {BOLD}python server.py{RESET}\n")
        sys.exit(2)
    print(f"{GREEN}[OK] Local server is active and responding (HTTP 200).{RESET}\n")

    # 2. Build test suites by tier
    loader = unittest.TestLoader()
    tier_suites = {}

    if args.tier in ('1', 'all'):
        tier_suites['Tier 1: Feature Coverage'] = loader.loadTestsFromModule(tier1_module)
    if args.tier in ('2', 'all'):
        tier_suites['Tier 2: Boundaries & Corners'] = loader.loadTestsFromModule(tier2_module)
    if args.tier in ('3', 'all'):
        tier_suites['Tier 3: Cross-Feature Combos'] = loader.loadTestsFromModule(tier3_module)
    if args.tier in ('4', 'all'):
        tier_suites['Tier 4: Real-World Scenarios'] = loader.loadTestsFromModule(tier4_module)

    tier_results = []
    all_passed = True
    total_run = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_time = 0.0
    all_records = []

    print(f"{BOLD}Executing Test Tiers:{RESET}")
    print("-" * 72)

    for tier_name, suite in tier_suites.items():
        count = suite.countTestCases()
        print(f"[*] Running {tier_name} ({count} test cases)... ", end="", flush=True)
        result, elapsed = run_suite(suite, failfast=args.failfast)
        total_time += elapsed

        run_count = result.testsRun
        fail_count = len(result.failures)
        err_count = len(result.errors)
        pass_count = run_count - fail_count - err_count

        total_run += run_count
        total_passed += pass_count
        total_failed += fail_count
        total_errors += err_count
        all_records.extend(result.records)

        if fail_count == 0 and err_count == 0:
            print(f"{GREEN}{BOLD}PASSED{RESET} ({pass_count}/{run_count}) [{elapsed:.2f}s]")
        else:
            print(f"{RED}{BOLD}FAILED{RESET} ({pass_count} passed, {fail_count} failed, {err_count} errors) [{elapsed:.2f}s]")
            all_passed = False

        tier_results.append({
            'tier': tier_name,
            'total': run_count,
            'passed': pass_count,
            'failed': fail_count,
            'errors': err_count,
            'elapsed_sec': round(elapsed, 3),
            'failures': [{'test': str(t), 'trace': err} for t, err in result.failures],
            'errors_list': [{'test': str(t), 'trace': err} for t, err in result.errors]
        })

        if args.failfast and not all_passed:
            break

    # 3. Summary Dashboard Table
    print("\n" + "=" * 72)
    print(f"{BOLD}{'Tier Name':<32} | {'Total':<6} | {'Passed':<6} | {'Failed':<6} | {'Time':<6}{RESET}")
    print("-" * 72)
    for tr in tier_results:
        status_color = GREEN if (tr['failed'] == 0 and tr['errors'] == 0) else RED
        print(f"{tr['tier']:<32} | {tr['total']:<6} | {GREEN}{tr['passed']:<6}{RESET} | {status_color}{tr['failed'] + tr['errors']:<6}{RESET} | {tr['elapsed_sec']:.2f}s")
    print("-" * 72)
    overall_color = GREEN if all_passed else RED
    print(f"{BOLD}{'GRAND TOTAL':<32} | {total_run:<6} | {GREEN}{total_passed:<6}{RESET} | {overall_color}{total_failed + total_errors:<6}{RESET} | {total_time:.2f}s")
    print("=" * 72 + "\n")

    # 4. Failure details if any
    if not all_passed:
        print(f"{RED}{BOLD}Detailed Failures / Errors:{RESET}")
        for tr in tier_results:
            for f in tr['failures']:
                print(f"\n{RED}[FAIL] {f['test']}{RESET}")
                print(f['trace'])
            for e in tr['errors_list']:
                print(f"\n{YELLOW}[ERROR] {e['test']}{RESET}")
                print(e['trace'])
        print()

    # 5. Export JSON report if requested
    if args.json_path:
        report_data = {
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'base_url': args.base_url,
            'summary': {
                'total': total_run,
                'passed': total_passed,
                'failed': total_failed,
                'errors': total_errors,
                'elapsed_sec': round(total_time, 3),
                'success': all_passed
            },
            'tiers': tier_results,
            'test_records': all_records
        }
        with open(args.json_path, 'w', encoding='utf-8') as jf:
            json.dump(report_data, jf, indent=2)
        print(f"[*] JSON report saved to: {args.json_path}")

    # 6. Exit code
    if all_passed:
        print(f"{GREEN}{BOLD}✔ ALL {total_run} E2E TESTS PASSED CLEANLY (100% PASS RATE).{RESET}\n")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}✘ TEST SUITE FAILED WITH {total_failed + total_errors} FAILURES/ERRORS.{RESET}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
