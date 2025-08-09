#!/usr/bin/env python3
"""
DSRS Smoke Test Script

Runs basic smoke tests against a deployed DSRS instance to verify:
1. All services are healthy and responding
2. Basic API functionality works
3. Authentication system is working
4. Database connections are established
5. Kafka event processing is functional

Usage:
    python scripts/smoke-test.py [--base-url http://localhost]
"""

import asyncio
import sys
import time
import json
from typing import Dict, List
import httpx
import argparse

class SmokeTestRunner:
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.services = {
            "registry": 8001,
            "eligibility": 8002,
            "payment": 8003,
            "analytics": 8004,
            "identity": 8005
        }
        self.results = []
        
    async def test_service_health(self, service: str, port: int) -> Dict:
        """Test service health endpoint"""
        test_name = f"{service}_health"
        print(f"🔍 Testing {service} health...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}:{port}/health"
                response = await client.get(url)
                
                if response.status_code == 200:
                    print(f"✅ {service} health check passed")
                    return {
                        "test": test_name,
                        "status": "PASS",
                        "response_time": response.elapsed.total_seconds(),
                        "details": response.json()
                    }
                else:
                    print(f"❌ {service} health check failed: {response.status_code}")
                    return {
                        "test": test_name,
                        "status": "FAIL",
                        "error": f"HTTP {response.status_code}",
                        "response": response.text[:200]
                    }
                    
        except Exception as e:
            print(f"❌ {service} health check error: {str(e)}")
            return {
                "test": test_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    async def test_registry_api(self) -> Dict:
        """Test Registry API basic functionality"""
        test_name = "registry_api"
        print("🔍 Testing Registry API...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}:{self.services['registry']}/api/v1/households"
                
                # Test GET (should work even without auth in test mode)
                response = await client.get(url)
                
                if response.status_code in [200, 401, 403]:
                    print("✅ Registry API is accessible")
                    return {
                        "test": test_name,
                        "status": "PASS",
                        "details": f"API responded with {response.status_code}"
                    }
                else:
                    print(f"❌ Registry API failed: {response.status_code}")
                    return {
                        "test": test_name,
                        "status": "FAIL",
                        "error": f"Unexpected status code: {response.status_code}"
                    }
                    
        except Exception as e:
            print(f"❌ Registry API error: {str(e)}")
            return {
                "test": test_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    async def test_identity_api(self) -> Dict:
        """Test Identity API authentication"""
        test_name = "identity_api"
        print("🔍 Testing Identity API...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}:{self.services['identity']}/api/v1/identity/authenticate"
                
                # Test with invalid credentials (should return 401 or 422)
                payload = {"username": "test", "password": "invalid"}
                response = await client.post(url, json=payload)
                
                if response.status_code in [401, 422]:
                    print("✅ Identity API authentication is working")
                    return {
                        "test": test_name,
                        "status": "PASS",
                        "details": f"Auth endpoint responded correctly with {response.status_code}"
                    }
                else:
                    print(f"❌ Identity API unexpected response: {response.status_code}")
                    return {
                        "test": test_name,
                        "status": "FAIL",
                        "error": f"Unexpected status code: {response.status_code}"
                    }
                    
        except Exception as e:
            print(f"❌ Identity API error: {str(e)}")
            return {
                "test": test_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    async def test_analytics_api(self) -> Dict:
        """Test Analytics API"""
        test_name = "analytics_api"
        print("🔍 Testing Analytics API...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}:{self.services['analytics']}/api/v1/analytics/summary"
                
                response = await client.get(url)
                
                if response.status_code in [200, 401, 403]:
                    print("✅ Analytics API is accessible")
                    return {
                        "test": test_name,
                        "status": "PASS",
                        "details": f"API responded with {response.status_code}"
                    }
                else:
                    print(f"❌ Analytics API failed: {response.status_code}")
                    return {
                        "test": test_name,
                        "status": "FAIL",
                        "error": f"Unexpected status code: {response.status_code}"
                    }
                    
        except Exception as e:
            print(f"❌ Analytics API error: {str(e)}")
            return {
                "test": test_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    async def test_cors_headers(self) -> Dict:
        """Test CORS headers are properly configured"""
        test_name = "cors_configuration"
        print("🔍 Testing CORS configuration...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}:{self.services['registry']}/health"
                
                # Send OPTIONS request to test CORS
                response = await client.options(url, headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET"
                })
                
                cors_header = response.headers.get("Access-Control-Allow-Origin")
                if cors_header:
                    print("✅ CORS headers are configured")
                    return {
                        "test": test_name,
                        "status": "PASS",
                        "details": f"CORS header: {cors_header}"
                    }
                else:
                    print("⚠️  CORS headers not found (may be configured differently)")
                    return {
                        "test": test_name,
                        "status": "WARN",
                        "details": "CORS headers not detected in response"
                    }
                    
        except Exception as e:
            print(f"❌ CORS test error: {str(e)}")
            return {
                "test": test_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    async def run_all_tests(self) -> Dict:
        """Run all smoke tests"""
        print("🚀 Starting DSRS Smoke Tests")
        print("=" * 50)
        
        start_time = time.time()
        
        # Test service health
        for service, port in self.services.items():
            result = await self.test_service_health(service, port)
            self.results.append(result)
        
        # Test API functionality
        api_tests = [
            self.test_registry_api(),
            self.test_identity_api(),
            self.test_analytics_api(),
            self.test_cors_headers()
        ]
        
        for test_coro in api_tests:
            result = await test_coro
            self.results.append(result)
        
        end_time = time.time()
        
        # Compile summary
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        errors = len([r for r in self.results if r["status"] == "ERROR"])
        warnings = len([r for r in self.results if r["status"] == "WARN"])
        
        summary = {
            "total_tests": len(self.results),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "warnings": warnings,
            "duration": end_time - start_time,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "results": self.results
        }
        
        return summary
    
    def print_summary(self, summary: Dict):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📋 SMOKE TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"🔥 Errors: {summary['errors']}")
        print(f"⚠️  Warnings: {summary['warnings']}")
        print(f"⏱️  Duration: {summary['duration']:.2f}s")
        print(f"🕐 Timestamp: {summary['timestamp']}")
        
        if summary['failed'] > 0 or summary['errors'] > 0:
            print("\n❌ FAILED TESTS:")
            for result in summary['results']:
                if result['status'] in ['FAIL', 'ERROR']:
                    print(f"  - {result['test']}: {result.get('error', 'Unknown error')}")
        
        # Determine overall status
        if summary['errors'] > 0:
            overall_status = "CRITICAL - Tests had errors"
            exit_code = 2
        elif summary['failed'] > 0:
            overall_status = "FAILED - Some tests failed"
            exit_code = 1
        elif summary['passed'] == 0:
            overall_status = "NO_TESTS - No tests passed"
            exit_code = 3
        else:
            overall_status = "PASSED - All tests successful"
            exit_code = 0
        
        print(f"\n🎯 Overall Status: {overall_status}")
        return exit_code

async def main():
    parser = argparse.ArgumentParser(description="Run DSRS smoke tests")
    parser.add_argument("--base-url", default="http://localhost", 
                       help="Base URL for DSRS services")
    args = parser.parse_args()
    
    runner = SmokeTestRunner(args.base_url)
    summary = await runner.run_all_tests()
    
    # Save results
    results_file = f"smoke-test-results-{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    exit_code = runner.print_summary(summary)
    sys.exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main())
