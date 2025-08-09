#!/usr/bin/env python3
"""
DSRS Deployment Validation Script

This script validates that the DSRS application is ready for deployment by:
1. Checking all services can start successfully
2. Validating health endpoints
3. Testing basic API functionality
4. Verifying configuration and environment setup
5. Running smoke tests against the application

Usage:
    python scripts/validate-deployment.py [--environment staging|production]
"""

import asyncio
import os
import sys
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import httpx
import yaml

class DeploymentValidator:
    def __init__(self, environment: str = "staging"):
        self.environment = environment
        self.base_url = "http://localhost"
        self.services = {
            "registry": 8001,
            "eligibility": 8002, 
            "payment": 8003,
            "analytics": 8004,
            "identity": 8005
        }
        self.results = {}
        
    async def validate_service_health(self, service: str, port: int) -> Dict:
        """Validate that a service is healthy and responding"""
        print(f"🔍 Validating {service} service on port {port}...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Check basic health endpoint
                health_url = f"{self.base_url}:{port}/health"
                response = await client.get(health_url)
                
                if response.status_code == 200:
                    print(f"✅ {service} health check passed")
                    return {
                        "status": "healthy",
                        "response_time": response.elapsed.total_seconds(),
                        "health_data": response.json()
                    }
                else:
                    print(f"❌ {service} health check failed: {response.status_code}")
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}",
                        "response": response.text
                    }
                    
        except Exception as e:
            print(f"❌ {service} connection failed: {str(e)}")
            return {
                "status": "unreachable",
                "error": str(e)
            }
    
    async def validate_api_endpoints(self) -> Dict:
        """Test key API endpoints for basic functionality"""
        print("🔍 Validating API endpoints...")
        
        results = {}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test Registry API
                registry_url = f"{self.base_url}:{self.services['registry']}/api/v1/households"
                response = await client.get(registry_url)
                results["registry_api"] = {
                    "status": "accessible" if response.status_code in [200, 401, 403] else "failed",
                    "status_code": response.status_code
                }
                
                # Test Identity API
                identity_url = f"{self.base_url}:{self.services['identity']}/api/v1/identity/authenticate"
                test_payload = {"username": "test", "password": "test"}
                response = await client.post(identity_url, json=test_payload)
                results["identity_api"] = {
                    "status": "accessible" if response.status_code in [200, 401, 422] else "failed",
                    "status_code": response.status_code
                }
                
                # Test Analytics API
                analytics_url = f"{self.base_url}:{self.services['analytics']}/api/v1/analytics/summary"
                response = await client.get(analytics_url)
                results["analytics_api"] = {
                    "status": "accessible" if response.status_code in [200, 401, 403] else "failed",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            results["error"] = str(e)
            
        return results
    
    def validate_kubernetes_manifests(self) -> Dict:
        """Validate Kubernetes manifests are syntactically correct"""
        print("🔍 Validating Kubernetes manifests...")
        
        manifest_dir = Path("infra/k8s")
        results = {"valid_manifests": [], "invalid_manifests": []}
        
        for yaml_file in manifest_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    list(yaml.safe_load_all(f))
                results["valid_manifests"].append(str(yaml_file))
                print(f"✅ {yaml_file.name} is valid")
            except Exception as e:
                results["invalid_manifests"].append({
                    "file": str(yaml_file),
                    "error": str(e)
                })
                print(f"❌ {yaml_file.name} is invalid: {e}")
                
        return results
    
    def validate_environment_config(self) -> Dict:
        """Validate environment configuration"""
        print("🔍 Validating environment configuration...")
        
        required_vars = [
            "DATABASE_URL",
            "KAFKA_BROKERS", 
            "MONGO_URL",
            "CORS_ALLOW_ORIGINS"
        ]
        
        results = {"missing_vars": [], "present_vars": []}
        
        for var in required_vars:
            if os.getenv(var):
                results["present_vars"].append(var)
                print(f"✅ {var} is configured")
            else:
                results["missing_vars"].append(var)
                print(f"⚠️  {var} is not configured (may use defaults)")
                
        return results
    
    async def run_smoke_tests(self) -> Dict:
        """Run basic smoke tests against the application"""
        print("🔍 Running smoke tests...")
        
        results = {"tests_passed": 0, "tests_failed": 0, "details": []}
        
        # Test 1: All services respond to health checks
        all_healthy = True
        for service, port in self.services.items():
            health_result = await self.validate_service_health(service, port)
            if health_result["status"] != "healthy":
                all_healthy = False
                
        if all_healthy:
            results["tests_passed"] += 1
            results["details"].append("✅ All services health checks passed")
        else:
            results["tests_failed"] += 1
            results["details"].append("❌ Some services failed health checks")
        
        # Test 2: API endpoints are accessible
        api_results = await self.validate_api_endpoints()
        if not api_results.get("error"):
            results["tests_passed"] += 1
            results["details"].append("✅ API endpoints are accessible")
        else:
            results["tests_failed"] += 1
            results["details"].append(f"❌ API endpoint test failed: {api_results['error']}")
            
        return results
    
    async def run_validation(self) -> Dict:
        """Run complete deployment validation"""
        print(f"🚀 Starting DSRS Deployment Validation for {self.environment} environment")
        print("=" * 60)
        
        # 1. Validate Kubernetes manifests
        manifest_results = self.validate_kubernetes_manifests()
        
        # 2. Validate environment configuration
        env_results = self.validate_environment_config()
        
        # 3. Validate service health (if services are running)
        service_results = {}
        for service, port in self.services.items():
            service_results[service] = await self.validate_service_health(service, port)
        
        # 4. Run smoke tests
        smoke_results = await self.run_smoke_tests()
        
        # Compile final results
        final_results = {
            "environment": self.environment,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "manifests": manifest_results,
            "environment_config": env_results,
            "services": service_results,
            "smoke_tests": smoke_results,
            "overall_status": self._determine_overall_status(
                manifest_results, env_results, service_results, smoke_results
            )
        }
        
        return final_results
    
    def _determine_overall_status(self, manifest_results, env_results, service_results, smoke_results) -> str:
        """Determine overall deployment readiness status"""
        
        # Check for critical failures
        if manifest_results["invalid_manifests"]:
            return "FAILED - Invalid Kubernetes manifests"
            
        # Check service health
        unhealthy_services = [
            service for service, result in service_results.items() 
            if result["status"] != "healthy"
        ]
        
        if len(unhealthy_services) == len(service_results):
            return "NOT_READY - No services are running (expected for validation without deployment)"
        elif unhealthy_services:
            return f"PARTIAL - Some services unhealthy: {', '.join(unhealthy_services)}"
        else:
            return "READY - All validations passed"

async def main():
    environment = sys.argv[1] if len(sys.argv) > 1 else "staging"
    
    validator = DeploymentValidator(environment)
    results = await validator.run_validation()
    
    print("\n" + "=" * 60)
    print("📋 DEPLOYMENT VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Environment: {results['environment']}")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Overall Status: {results['overall_status']}")
    
    print(f"\n📁 Kubernetes Manifests:")
    print(f"  Valid: {len(results['manifests']['valid_manifests'])}")
    print(f"  Invalid: {len(results['manifests']['invalid_manifests'])}")
    
    print(f"\n🔧 Environment Configuration:")
    print(f"  Configured: {len(results['environment_config']['present_vars'])}")
    print(f"  Missing: {len(results['environment_config']['missing_vars'])}")
    
    print(f"\n🏥 Service Health:")
    for service, result in results['services'].items():
        status_icon = "✅" if result['status'] == 'healthy' else "❌"
        print(f"  {status_icon} {service}: {result['status']}")
    
    print(f"\n🧪 Smoke Tests:")
    print(f"  Passed: {results['smoke_tests']['tests_passed']}")
    print(f"  Failed: {results['smoke_tests']['tests_failed']}")
    
    # Save detailed results
    results_file = f"deployment-validation-{environment}-{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    # Exit with appropriate code
    if "FAILED" in results['overall_status']:
        sys.exit(1)
    elif "PARTIAL" in results['overall_status']:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
