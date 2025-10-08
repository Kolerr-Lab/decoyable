"""
DECOYABLE Comprehensive System Test Suite
Version 1.2.1 Pre-Release Validation

Tests all core features and integrations before release.
"""

import asyncio
import subprocess
import sys
import time
from typing import Dict, List


class DecoyableTestSuite:
    """Comprehensive test suite for DECOYABLE system validation."""

    def __init__(self):
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.results: List[Dict] = []

    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results."""
        self.test_count += 1
        if status == "PASS":
            self.pass_count += 1
            print(f"✅ {test_name}: {details}")
        else:
            self.fail_count += 1
            print(f"❌ {test_name}: {details}")

        self.results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.time()
        })

    async def test_secrets_scanning(self):
        """Test secrets scanning functionality."""
        try:
            from decoyable.scanners.secrets import scan_file
            import tempfile
            import os

            # Create test file with secrets
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write('API_KEY = "AKIAIOSFODNN7EXAMPLE"\n')
                f.write('GITHUB_TOKEN = "ghp_1234567890abcdef1234567890abcdef123"\n')
                test_file = f.name

            try:
                findings = scan_file(test_file)
                if len(findings) >= 2:  # Should find both secrets
                    self.log_test("Secrets Scanning", "PASS", f"Found {len(findings)} secrets")
                else:
                    self.log_test("Secrets Scanning", "FAIL", f"Expected >=2 findings, got {len(findings)}")
            finally:
                os.unlink(test_file)

        except Exception as e:
            self.log_test("Secrets Scanning", "FAIL", str(e))

    async def test_dependency_scanning(self):
        """Test dependency analysis."""
        try:
            from decoyable.scanners.deps import collect_imports_from_dir
            import tempfile
            import os

            # Create test directory with Python files
            with tempfile.TemporaryDirectory() as tmp_dir:
                test_file = os.path.join(tmp_dir, "test.py")
                with open(test_file, 'w') as f:
                    f.write("import os\nimport sys\nfrom pathlib import Path\n")

                imports = collect_imports_from_dir(tmp_dir)
                if "os" in imports and "pathlib" in imports:
                    self.log_test("Dependency Scanning", "PASS", f"Found {len(imports)} imports")
                else:
                    self.log_test("Dependency Scanning", "FAIL", "Missing expected imports")

        except Exception as e:
            self.log_test("Dependency Scanning", "FAIL", str(e))

    async def test_sast_scanning(self):
        """Test Static Application Security Testing."""
        try:
            from decoyable.scanners.sast import scan_sast

            # Test SAST scanning on current directory
            result = scan_sast(".")

            if result and "vulnerabilities" in result:
                vuln_count = len(result["vulnerabilities"])
                self.log_test("SAST Scanning", "PASS", f"Found {vuln_count} vulnerabilities")
            else:
                self.log_test("SAST Scanning", "FAIL", "No SAST results")

        except Exception as e:
            self.log_test("SAST Scanning", "FAIL", str(e))

    async def test_ai_analysis(self):
        """Test AI-powered threat analysis."""
        try:
            from decoyable.defense.llm_analysis import analyze_attack_with_llm

            test_attack = {
                "ip_address": "192.168.1.100",
                "method": "POST",
                "path": "/api/login",
                "user_agent": "sqlmap/1.6.5",
                "body": "username=admin&password=' OR '1'='1"
            }

            result = await analyze_attack_with_llm(test_attack)

            if result and "attack_type" in result:
                self.log_test("AI Analysis", "PASS", f"Detected attack: {result['attack_type']}")
            else:
                self.log_test("AI Analysis", "SKIP", "AI analysis not available or no attack detected")

        except Exception as e:
            self.log_test("AI Analysis", "SKIP", f"AI analysis not available: {str(e)}")

    async def test_honeypot_functionality(self):
        """Test honeypot defense mechanisms."""
        try:
            from decoyable.core.honeypot_service import HoneypotService
            from decoyable.core.registry import get_service_registry
            from decoyable.core.config import Settings

            # Set up registry
            registry = get_service_registry()
            config = Settings()
            registry.register_instance("config", config)

            # Test honeypot service initialization
            honeypot = HoneypotService(registry)
            self.log_test("Honeypot Service", "PASS", "Honeypot service initialized successfully")

        except Exception as e:
            self.log_test("Honeypot Functionality", "FAIL", str(e))

    def test_cli_commands(self):
        """Test CLI command functionality."""
        try:
            # Test help command by importing and calling main function directly
            import sys
            sys.path.insert(0, '.')
            from main import main
            import io
            from contextlib import redirect_stdout

            help_output = io.StringIO()
            try:
                with redirect_stdout(help_output):
                    result = main(['--help'])
            except SystemExit as e:
                result = e.code

            if result == 0 and 'usage:' in help_output.getvalue().lower():
                self.log_test("CLI Help Command", "PASS", "Help command executed successfully")
            else:
                usage_found = 'usage:' in help_output.getvalue().lower()
                self.log_test("CLI Help Command", "FAIL", f"Help command failed: return_code={result}, usage_found={usage_found}")

            # Test version command
            version_output = io.StringIO()
            try:
                with redirect_stdout(version_output):
                    result = main(['--version'])
            except SystemExit as e:
                result = e.code

            if result == 0:
                self.log_test("CLI Version Command", "PASS", "Version command executed successfully")
            else:
                self.log_test("CLI Version Command", "SKIP", "Version command not available")

        except Exception as e:
            self.log_test("CLI Commands", "FAIL", str(e))

    async def test_database_operations(self):
        """Test database functionality."""
        try:
            from decoyable.database import store_scan_result, get_scan_results

            # Store a test result
            scan_id = store_scan_result('test_scan', '.', 'completed', results={'test': 'data'})
            self.log_test("Database Store", "PASS", f"Stored scan result with ID: {scan_id}")

            # Retrieve results
            results = get_scan_results('test_scan', limit=5)
            self.log_test("Database Retrieve", "PASS", f"Retrieved {len(results)} scan results")

        except Exception as e:
            self.log_test("Database Operations", "FAIL", str(e))

    async def test_caching_system(self):
        """Test Redis caching functionality."""
        try:
            from decoyable.cache import scan_secrets_cached, scan_dependencies_cached

            # Test cache functions exist
            if callable(scan_secrets_cached) and callable(scan_dependencies_cached):
                self.log_test("Caching System", "PASS", "Cache functions available")
            else:
                self.log_test("Caching System", "FAIL", "Cache functions not callable")

        except Exception as e:
            self.log_test("Caching System", "FAIL", str(e))

    async def test_docker_integration(self):
        """Test Docker integration."""
        try:
            import os
            if os.path.exists("docker-compose.yml"):
                self.log_test("Docker Integration", "PASS", "docker-compose.yml found")
            else:
                self.log_test("Docker Integration", "SKIP", "No docker-compose.yml found")

        except Exception as e:
            self.log_test("Docker Integration", "FAIL", str(e))

    async def test_ai_providers(self):
        """Test AI provider integrations."""
        try:
            from decoyable.llm import create_multi_provider_router

            router = create_multi_provider_router()

            # Check if any providers are configured
            if router and hasattr(router, 'providers'):
                provider_count = len(router.providers)
                if provider_count > 0:
                    self.log_test("AI Providers", "PASS", f"Found {provider_count} AI providers")
                else:
                    self.log_test("AI Providers", "SKIP", "No AI providers configured")
            else:
                self.log_test("AI Providers", "SKIP", "AI router not available")

        except Exception as e:
            self.log_test("AI Providers", "SKIP", f"AI providers not available: {str(e)}")

    async def run_unit_tests(self):
        """Run the unit test suite."""
        try:
            # Run pytest programmatically
            import pytest
            import sys
            from io import StringIO

            # Capture output
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()

            try:
                # Run tests
                result = pytest.main([
                    "tests/",
                    "-v",
                    "--tb=short",
                    "--disable-warnings"
                ])
            finally:
                sys.stdout = old_stdout

            if result == 0:
                self.log_test("Unit Tests", "PASS", "All unit tests passed")
            else:
                output = captured_output.getvalue()
                # Count failures
                failed_count = output.count("FAILED")
                passed_count = output.count("PASSED")
                self.log_test("Unit Tests", "PARTIAL", f"{passed_count} passed, {failed_count} failed")

        except Exception as e:
            self.log_test("Unit Tests", "FAIL", str(e))

    async def run_all_tests(self):
        """Run all test categories."""
        print("🚀 Starting Comprehensive DECOYABLE System Test Suite v1.2.1")
        print("=" * 70)

        # Core scanning features
        await self.test_secrets_scanning()
        await self.test_dependency_scanning()
        await self.test_sast_scanning()
        await self.test_ai_analysis()

        # Defense and security
        await self.test_honeypot_functionality()

        # Infrastructure
        await self.test_database_operations()
        await self.test_caching_system()
        await self.test_docker_integration()

        # AI and external services
        await self.test_ai_providers()

        # CLI and testing
        self.test_cli_commands()
        await self.run_unit_tests()

        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY - DECOYABLE v1.2.1")
        print(f"Total Tests: {self.test_count}")
        print(f"Passed: {self.pass_count}")
        print(f"Failed: {self.fail_count}")
        success_rate = self.pass_count / self.test_count * 100 if self.test_count > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")

        if self.fail_count == 0:
            print("🎉 ALL TESTS PASSED! Ready for v1.2.1 release")
        elif success_rate >= 80:
            print("⚠️  MOST TESTS PASSED - Minor issues to address")
        else:
            print("❌ SIGNIFICANT ISSUES - Address before release")

        return self.results


if __name__ == "__main__":
    suite = DecoyableTestSuite()
    asyncio.run(suite.run_all_tests())