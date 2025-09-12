#!/usr/bin/env python
"""
Comprehensive test runner for Anthony Store
This script runs all tests with detailed reporting and coverage analysis
"""
import os
import sys
import subprocess
import json
import time
from pathlib import Path
import argparse

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

class TestRunner:
    """Comprehensive test runner with detailed reporting"""
    
    def __init__(self):
        self.project_root = project_root
        self.test_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'coverage': 0,
            'duration': 0,
            'failed_tests': []
        }
    
    def run_command(self, command, cwd=None):
        """Run command and return result"""
        if isinstance(command, str):
            command = command.split()
        
        cwd = cwd or self.project_root
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            return result
        except subprocess.TimeoutExpired:
            print("Test execution timed out!")
            return None
        except Exception as e:
            print(f"Error running command: {e}")
            return None
    
    def run_unit_tests(self):
        """Run unit tests with pytest"""
        print("Running unit tests...")
        
        command = [
            'python', '-m', 'pytest',
            'tests/',
            '-v',
            '--tb=short',
            '--cov=apps',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
            '--cov-report=json:coverage.json',
            '--junit-xml=test-results.xml',
            '--cov-fail-under=80'
        ]
        
        start_time = time.time()
        result = self.run_command(command)
        end_time = time.time()
        
        if result:
            self.test_results['duration'] = end_time - start_time
            
            # Parse test results from output
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'passed' in line and 'failed' in line:
                    # Parse pytest summary line
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'passed':
                            self.test_results['passed'] = int(parts[i-1])
                        elif part == 'failed':
                            self.test_results['failed'] = int(parts[i-1])
                        elif part == 'skipped':
                            self.test_results['skipped'] = int(parts[i-1])
            
            # Parse coverage from JSON file
            coverage_file = self.project_root / 'coverage.json'
            if coverage_file.exists():
                try:
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                        self.test_results['coverage'] = coverage_data['totals']['percent_covered']
                except Exception:
                    pass
            
            self.test_results['total_tests'] = (
                self.test_results['passed'] + 
                self.test_results['failed'] + 
                self.test_results['skipped']
            )
            
            return result.returncode == 0
        
        return False
    
    def run_integration_tests(self):
        """Run integration tests"""
        print("Running integration tests...")
        
        command = [
            'python', '-m', 'pytest',
            'tests/test_comprehensive_*.py',
            '-v',
            '--tb=short',
            '-m', 'not slow'
        ]
        
        result = self.run_command(command)
        return result and result.returncode == 0
    
    def run_api_tests(self):
        """Run API endpoint tests"""
        print("Running API tests...")
        
        command = [
            'python', '-m', 'pytest',
            'tests/',
            '-k', 'api or endpoint or view',
            '-v'
        ]
        
        result = self.run_command(command)
        return result and result.returncode == 0
    
    def run_model_tests(self):
        """Run model tests"""
        print("Running model tests...")
        
        command = [
            'python', '-m', 'pytest',
            'tests/',
            '-k', 'model',
            '-v'
        ]
        
        result = self.run_command(command)
        return result and result.returncode == 0
    
    def run_security_tests(self):
        """Run security tests"""
        print("Running security tests...")
        
        # Check for common security issues
        command = [
            'python', 'manage.py', 'check', '--deploy'
        ]
        
        result = self.run_command(command)
        return result and result.returncode == 0
    
    def run_performance_tests(self):
        """Run performance tests"""
        print("Running performance tests...")
        
        command = [
            'python', '-m', 'pytest',
            'tests/',
            '-k', 'performance',
            '-v'
        ]
        
        result = self.run_command(command)
        return result and result.returncode == 0
    
    def lint_code(self):
        """Run code linting"""
        print("Running code linting...")
        
        # Run flake8
        flake8_result = self.run_command(['flake8', 'apps/', 'config/'])
        
        # Run black check
        black_result = self.run_command(['black', '--check', 'apps/', 'config/'])
        
        # Run isort check
        isort_result = self.run_command(['isort', '--check-only', 'apps/', 'config/'])
        
        lint_passed = True
        if flake8_result and flake8_result.returncode != 0:
            print("Flake8 linting failed:")
            print(flake8_result.stdout)
            lint_passed = False
        
        if black_result and black_result.returncode != 0:
            print("Black formatting check failed:")
            print(black_result.stdout)
            lint_passed = False
        
        if isort_result and isort_result.returncode != 0:
            print("isort import sorting check failed:")
            print(isort_result.stdout)
            lint_passed = False
        
        return lint_passed
    
    def check_migrations(self):
        """Check for missing migrations"""
        print("Checking for missing migrations...")
        
        command = ['python', 'manage.py', 'makemigrations', '--check', '--dry-run']
        result = self.run_command(command)
        
        if result and result.returncode != 0:
            print("Missing migrations detected:")
            print(result.stdout)
            return False
        
        return True
    
    def validate_models(self):
        """Validate Django models"""
        print("Validating Django models...")
        
        command = ['python', 'manage.py', 'check']
        result = self.run_command(command)
        
        if result and result.returncode != 0:
            print("Model validation failed:")
            print(result.stdout)
            return False
        
        return True
    
    def test_database_operations(self):
        """Test basic database operations"""
        print("Testing database operations...")
        
        try:
            from django.db import connection
            from django.contrib.auth.models import User
            from apps.customers.models import Customer
            from apps.categories.models import Category
            from apps.products.models import Product, Brand
            
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] != 1:
                    return False
            
            # Test model operations
            test_user = User.objects.create_user(
                username='test_db_user',
                email='test@example.com',
                password='testpass123'
            )
            
            test_customer = Customer.objects.create(
                user=test_user,
                first_name='Test',
                last_name='Customer',
                id_number='12345678',
                phone_number='+254707497200',
                email='test@example.com',
                address_line_1='Test Address',
                city='Nairobi',
                state_province='Nairobi',
                postal_code='00100',
                country='Kenya'
            )
            
            test_category = Category.objects.create(
                name='Test Category',
                description='Test category description'
            )
            
            test_brand = Brand.objects.create(
                name='Test Brand',
                description='Test brand description'
            )
            
            test_product = Product.objects.create(
                name='Test Product',
                description='Test product description',
                price=99.99,
                category=test_category,
                brand=test_brand,
                sku='TEST001',
                stock_quantity=10
            )
            
            # Cleanup test data
            test_product.delete()
            test_brand.delete()
            test_category.delete()
            test_customer.delete()
            test_user.delete()
            
            print("Database operations test passed")
            return True
            
        except Exception as e:
            print(f"Database operations test failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints availability"""
        print("Testing API endpoints...")
        
        try:
            from django.test import Client
            from django.urls import reverse
            
            client = Client()
            
            # Test public endpoints
            endpoints = [
                ('category-list', {}),
                ('product-list', {}),
                ('schema-swagger-ui', {}),
                ('health-check', {}),
            ]
            
            for endpoint_name, kwargs in endpoints:
                try:
                    url = reverse(endpoint_name, kwargs=kwargs)
                    response = client.get(url)
                    if response.status_code not in [200, 301, 302]:
                        print(f"Endpoint {endpoint_name} failed with status {response.status_code}")
                        return False
                except Exception as e:
                    print(f"Error testing endpoint {endpoint_name}: {e}")
                    return False
            
            print("API endpoints test passed")
            return True
            
        except Exception as e:
            print(f"API endpoints test failed: {e}")
            return False
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("Anthony STORE - TEST REPORT")
        print("="*60)
        print(f"Business: Anthony Store")
        print(f"Contact: anthonymakori2@gmail.com")
        print(f"Phone: +254707497200")
        print("="*60)
        
        print(f"\nTest Summary:")
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed']}")
        print(f"Failed: {self.test_results['failed']}")
        print(f"Skipped: {self.test_results['skipped']}")
        print(f"Coverage: {self.test_results['coverage']:.2f}%")
        print(f"Duration: {self.test_results['duration']:.2f} seconds")
        
        if self.test_results['failed'] > 0:
            print(f"\nFailed Tests:")
            for test in self.test_results['failed_tests']:
                print(f"  - {test}")
        
        # Overall status
        if self.test_results['failed'] == 0 and self.test_results['coverage'] >= 80:
            print(f"\n ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT")
        else:
            print(f"\n SOME TESTS FAILED - REVIEW REQUIRED")
        
        print("="*60)
    
    def run_all_tests(self, test_types=None):
        """Run all tests"""
        print("Starting comprehensive test suite for Anthony Store...")
        print(f"Contact: anthonymakori2@gmail.com | Phone: +254707497200")
        print("-" * 60)
        
        test_types = test_types or [
            'migrations', 'models', 'database', 'unit', 'integration', 
            'api', 'security', 'lint', 'endpoints'
        ]
        
        results = {}
        
        # Run each test type
        if 'migrations' in test_types:
            results['migrations'] = self.check_migrations()
        
        if 'models' in test_types:
            results['models'] = self.validate_models()
        
        if 'database' in test_types:
            results['database'] = self.test_database_operations()
        
        if 'unit' in test_types:
            results['unit'] = self.run_unit_tests()
        
        if 'integration' in test_types:
            results['integration'] = self.run_integration_tests()
        
        if 'api' in test_types:
            results['api'] = self.run_api_tests()
        
        if 'security' in test_types:
            results['security'] = self.run_security_tests()
        
        if 'lint' in test_types:
            results['lint'] = self.lint_code()
        
        if 'endpoints' in test_types:
            results['endpoints'] = self.test_api_endpoints()
        
        # report
        self.generate_report()
        
        # individual test results
        print("\nDetailed Results:")
        for test_type, passed in results.items():
            status = " PASSED" if passed else " FAILED"
            print(f"  {test_type.upper()}: {status}")
        
        return all(results.values())

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Comprehensive test runner for Anthony Store'
    )
    parser.add_argument(
        '--type',
        choices=['unit', 'integration', 'api', 'models', 'security', 'lint', 'all'],
        default='all',
        help='Type of tests to run'
    )
    parser.add_argument(
        '--coverage-only',
        action='store_true',
        help='Only run coverage analysis'
    )
    parser.add_argument(
        '--fast',
        action='store_true',
        help='Run only fast tests'
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        if args.coverage_only:
            success = runner.run_unit_tests()
        elif args.type == 'all':
            if args.fast:
                test_types = ['migrations', 'models', 'unit', 'lint']
            else:
                test_types = None
            success = runner.run_all_tests(test_types)
        else:
            # Run specific test type
            test_methods = {
                'unit': runner.run_unit_tests,
                'integration': runner.run_integration_tests,
                'api': runner.run_api_tests,
                'models': runner.validate_models,
                'security': runner.run_security_tests,
                'lint': runner.lint_code
            }
            
            method = test_methods.get(args.type)
            if method:
                success = method()
                runner.generate_report()
            else:
                print(f"Unknown test type: {args.type}")
                success = False
        
        if success:
            print("\n All tests completed successfully!")
            print("Anthony Store is ready for deployment!")
            sys.exit(0)
        else:
            print("\n Some tests failed!")
            print("Please review the results and fix issues before deployment.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nTest execution cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest execution failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
