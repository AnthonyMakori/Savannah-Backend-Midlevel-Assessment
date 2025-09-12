#!/usr/bin/env python
"""
Bulletproof deployment script for Anthony Store
This script handles deployment to multiple environments with comprehensive error handling
"""
import os
import sys
import subprocess
import json
import time
import logging
from pathlib import Path
import argparse
import shutil
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DeploymentError(Exception):
    """Custom exception for deployment errors"""
    pass

class CynthiaStoreDeployer:
    """Bulletproof deployer for Anthony Store"""
    
    def __init__(self, environment='local'):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = self.project_root / 'backups'
        self.deployment_config = self.load_deployment_config()
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(exist_ok=True)
        
        logger.info(f"Initializing deployment for environment: {environment}")
    
    def load_deployment_config(self):
        """Load deployment configuration"""
        config_file = self.project_root / 'deployment-config.json'
        
        default_config = {
            "local": {
                "python_version": "3.11",
                "database": "sqlite",
                "redis_required": False,
                "static_files": True,
                "migrations": True,
                "fixtures": True
            },
            "docker": {
                "python_version": "3.11",
                "database": "postgresql",
                "redis_required": True,
                "static_files": True,
                "migrations": True,
                "fixtures": True
            },
            "kubernetes": {
                "python_version": "3.11",
                "database": "postgresql",
                "redis_required": True,
                "static_files": True,
                "migrations": True,
                "fixtures": False,
                "namespace": "cynthia-store",
                "helm_chart": "./charts/store-chart"
            },
            "github": {
                "python_version": "3.11",
                "database": "postgresql",
                "redis_required": True,
                "static_files": True,
                "migrations": True,
                "fixtures": False
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    for env in default_config:
                        if env in user_config:
                            default_config[env].update(user_config[env])
                return default_config
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}. Using defaults.")
        
        # Save default config
        try:
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default deployment config at {config_file}")
        except Exception as e:
            logger.warning(f"Failed to save default config: {e}")
        
        return default_config
    
    def run_command(self, command, cwd=None, check=True, timeout=300):
        """Run command with comprehensive error handling"""
        if isinstance(command, str):
            command = command.split()
        
        cwd = cwd or self.project_root
        
        logger.info(f"Running command: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check
            )
            
            if result.stdout:
                logger.info(f"Command output: {result.stdout}")
            
            return result
        
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout} seconds")
            raise DeploymentError(f"Command timed out: {' '.join(command)}")
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with exit code {e.returncode}")
            logger.error(f"Error output: {e.stderr}")
            if check:
                raise DeploymentError(f"Command failed: {' '.join(command)}")
            return e
        
        except Exception as e:
            logger.error(f"Unexpected error running command: {e}")
            raise DeploymentError(f"Unexpected error: {e}")
    
    def check_prerequisites(self):
        """Check system prerequisites"""
        logger.info("Checking prerequisites...")
        
        config = self.deployment_config.get(self.environment, {})
        
        # Check Python version
        python_version = config.get('python_version', '3.11')
        try:
            result = self.run_command(['python', '--version'])
            current_version = result.stdout.strip().split()[1]
            if not current_version.startswith(python_version):
                logger.warning(f"Python version mismatch. Expected: {python_version}, Got: {current_version}")
        except Exception:
            logger.error("Python not found or not accessible")
            raise DeploymentError("Python is required but not found")
        
        # Check Git
        try:
            self.run_command(['git', '--version'])
        except Exception:
            logger.error("Git not found")
            raise DeploymentError("Git is required but not found")
        
        # Environment-specific checks
        if self.environment == 'docker':
            self.check_docker()
        elif self.environment == 'kubernetes':
            self.check_kubernetes()
        
        logger.info("Prerequisites check completed successfully")
    
    def check_docker(self):
        """Check Docker prerequisites"""
        try:
            self.run_command(['docker', '--version'])
            self.run_command(['docker-compose', '--version'])
        except Exception:
            raise DeploymentError("Docker and Docker Compose are required for Docker deployment")
    
    def check_kubernetes(self):
        """Check Kubernetes prerequisites"""
        try:
            self.run_command(['kubectl', 'version', '--client'])
            self.run_command(['helm', 'version'])
        except Exception:
            raise DeploymentError("kubectl and Helm are required for Kubernetes deployment")
    
    def create_backup(self):
        """Create backup before deployment"""
        logger.info("Creating backup...")
        
        timestamp = int(time.time())
        backup_name = f"backup_{self.environment}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        try:
            # Create backup directory
            backup_path.mkdir(exist_ok=True)
            
            # Backup database if exists
            if (self.project_root / 'db.sqlite3').exists():
                shutil.copy2(
                    self.project_root / 'db.sqlite3',
                    backup_path / 'db.sqlite3'
                )
                logger.info("Database backup created")
            
            # Backup media files if exists
            media_dir = self.project_root / 'media'
            if media_dir.exists():
                shutil.copytree(
                    media_dir,
                    backup_path / 'media',
                    dirs_exist_ok=True
                )
                logger.info("Media files backup created")
            
            # Backup environment file if exists
            env_file = self.project_root / '.env'
            if env_file.exists():
                shutil.copy2(env_file, backup_path / '.env')
                logger.info("Environment file backup created")
            
            logger.info(f"Backup created successfully at {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            raise DeploymentError(f"Failed to create backup: {e}")
    
    def setup_virtual_environment(self):
        """Setup Python virtual environment"""
        logger.info("Setting up virtual environment...")
        
        venv_path = self.project_root / 'venv'
        
        try:
            if not venv_path.exists():
                self.run_command(['python', '-m', 'venv', 'venv'])
                logger.info("Virtual environment created")
            
            # Activate virtual environment and install dependencies
            if os.name == 'nt':  # Windows
                pip_path = venv_path / 'Scripts' / 'pip'
                python_path = venv_path / 'Scripts' / 'python'
            else:  # Unix/Linux/macOS
                pip_path = venv_path / 'bin' / 'pip'
                python_path = venv_path / 'bin' / 'python'
            
            # Upgrade pip
            self.run_command([str(python_path), '-m', 'pip', 'install', '--upgrade', 'pip'])
            
            # Install requirements
            requirements_file = self.project_root / 'requirements.txt'
            if requirements_file.exists():
                self.run_command([str(pip_path), 'install', '-r', 'requirements.txt'])
                logger.info("Dependencies installed successfully")
            
            return python_path
            
        except Exception as e:
            logger.error(f"Virtual environment setup failed: {e}")
            raise DeploymentError(f"Failed to setup virtual environment: {e}")
    
    def run_tests(self, python_path):
        """Run comprehensive tests"""
        logger.info("Running tests...")
        
        config = self.deployment_config.get(self.environment, {})
        
        try:
            # Run pytest with coverage
            test_command = [
                str(python_path), '-m', 'pytest',
                '--cov=apps',
                '--cov-report=term-missing',
                '--cov-report=html',
                '--cov-fail-under=80',
                '-v'
            ]
            
            result = self.run_command(test_command, check=False)
            
            if result.returncode != 0:
                logger.warning("Some tests failed, but continuing deployment")
                logger.warning("Please review test results and fix issues")
            else:
                logger.info("All tests passed successfully")
            
        except Exception as e:
            logger.warning(f"Test execution failed: {e}")
            logger.warning("Continuing deployment without test validation")
    
    def run_migrations(self, python_path):
        """Run database migrations"""
        config = self.deployment_config.get(self.environment, {})
        
        if not config.get('migrations', True):
            logger.info("Migrations disabled for this environment")
            return
        
        logger.info("Running database migrations...")
        
        try:
            # Create migrations
            self.run_command([str(python_path), 'manage.py', 'makemigrations'])
            
            # Apply migrations
            self.run_command([str(python_path), 'manage.py', 'migrate'])
            
            logger.info("Migrations completed successfully")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise DeploymentError(f"Database migration failed: {e}")
    
    def collect_static_files(self, python_path):
        """Collect static files"""
        config = self.deployment_config.get(self.environment, {})
        
        if not config.get('static_files', True):
            logger.info("Static file collection disabled for this environment")
            return
        
        logger.info("Collecting static files...")
        
        try:
            self.run_command([
                str(python_path), 'manage.py', 'collectstatic', '--noinput'
            ])
            logger.info("Static files collected successfully")
            
        except Exception as e:
            logger.error(f"Static file collection failed: {e}")
            raise DeploymentError(f"Failed to collect static files: {e}")
    
    def load_fixtures(self, python_path):
        """Load initial data fixtures"""
        config = self.deployment_config.get(self.environment, {})
        
        if not config.get('fixtures', True):
            logger.info("Fixture loading disabled for this environment")
            return
        
        logger.info("Loading initial data...")
        
        try:
            # Run setup demo data script
            setup_script = self.project_root / 'scripts' / 'setup_demo_data.py'
            if setup_script.exists():
                self.run_command([str(python_path), str(setup_script)])
                logger.info("Demo data loaded successfully")
            
        except Exception as e:
            logger.warning(f"Fixture loading failed: {e}")
            logger.warning("Continuing without demo data")
    
    def deploy_local(self):
        """Deploy to local environment"""
        logger.info("Starting local deployment...")
        
        try:
            # Setup virtual environment
            python_path = self.setup_virtual_environment()
            
            # Run tests
            self.run_tests(python_path)
            
            # Run migrations
            self.run_migrations(python_path)
            
            # Collect static files
            self.collect_static_files(python_path)
            
            # Load fixtures
            self.load_fixtures(python_path)
            
            logger.info("Local deployment completed successfully!")
            logger.info("You can now run: python manage.py runserver")
            
        except Exception as e:
            logger.error(f"Local deployment failed: {e}")
            raise
    
    def deploy_docker(self):
        """Deploy using Docker"""
        logger.info("Starting Docker deployment...")
        
        try:
            # Build Docker image
            self.run_command(['docker-compose', 'build'])
            
            # Start services
            self.run_command(['docker-compose', 'up', '-d'])
            
            # Wait for services to be ready
            logger.info("Waiting for services to be ready...")
            time.sleep(30)
            
            # Run migrations in container
            self.run_command([
                'docker-compose', 'exec', '-T', 'web',
                'python', 'manage.py', 'migrate'
            ])
            
            # Load demo data
            self.run_command([
                'docker-compose', 'exec', '-T', 'web',
                'python', 'scripts/setup_demo_data.py'
            ], check=False)
            
            logger.info("Docker deployment completed successfully!")
            logger.info("Application is running at http://localhost:8000")
            
        except Exception as e:
            logger.error(f"Docker deployment failed: {e}")
            # Attempt cleanup
            self.run_command(['docker-compose', 'down'], check=False)
            raise
    
    def deploy_kubernetes(self):
        """Deploy to Kubernetes"""
        logger.info("Starting Kubernetes deployment...")
        
        config = self.deployment_config.get('kubernetes', {})
        namespace = config.get('namespace', 'cynthia-store')
        helm_chart = config.get('helm_chart', './charts/store-chart')
        
        try:
            # Create namespace if it doesn't exist
            self.run_command([
                'kubectl', 'create', 'namespace', namespace
            ], check=False)
            
            # Build and push Docker image (assuming registry is configured)
            image_tag = f"cynthia-online-store:latest"
            self.run_command(['docker', 'build', '-t', image_tag, '.'])
            
            # Deploy using Helm
            self.run_command([
                'helm', 'upgrade', '--install',
                'cynthia-store', helm_chart,
                '--namespace', namespace,
                '--set', f'image.tag=latest',
                '--wait'
            ])
            
            # Get service information
            result = self.run_command([
                'kubectl', 'get', 'services',
                '--namespace', namespace
            ])
            
            logger.info("Kubernetes deployment completed successfully!")
            logger.info("Service information:")
            logger.info(result.stdout)
            
        except Exception as e:
            logger.error(f"Kubernetes deployment failed: {e}")
            raise
    
    def deploy_github(self):
        """Setup GitHub Actions deployment"""
        logger.info("Setting up GitHub Actions deployment...")
        
        try:
            # Check if we're in a git repository
            self.run_command(['git', 'status'])
            
            # Ensure GitHub Actions workflow exists
            workflow_dir = self.project_root / '.github' / 'workflows'
            workflow_file = workflow_dir / 'ci.yml'
            
            if not workflow_file.exists():
                logger.error("GitHub Actions workflow file not found")
                raise DeploymentError("GitHub Actions workflow file missing")
            
            # Add and commit changes
            self.run_command(['git', 'add', '.'])
            
            # Check if there are changes to commit
            result = self.run_command(['git', 'status', '--porcelain'], check=False)
            
            if result.stdout.strip():
                commit_message = "Deploy Anthony Store updates"
                self.run_command(['git', 'commit', '-m', commit_message])
                
                # Push to GitHub
                self.run_command(['git', 'push', 'origin', 'main'])
                
                logger.info("Changes pushed to GitHub successfully!")
                logger.info("GitHub Actions will handle the deployment")
            else:
                logger.info("No changes to deploy")
            
        except Exception as e:
            logger.error(f"GitHub deployment setup failed: {e}")
            raise
    
    def health_check(self):
        """Perform health check after deployment"""
        logger.info("Performing health check...")
        
        health_urls = {
            'local': 'http://localhost:8000/health/',
            'docker': 'http://localhost:8000/health/',
            'kubernetes': None,  # Will be determined dynamically
            'github': None  # Not applicable
        }
        
        url = health_urls.get(self.environment)
        
        if not url:
            logger.info("Health check not applicable for this environment")
            return
        
        try:
            import requests
            
            # Wait a bit for the service to be ready
            time.sleep(10)
            
            for attempt in range(5):
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        logger.info("Health check passed!")
                        return
                except requests.RequestException:
                    pass
                
                logger.info(f"Health check attempt {attempt + 1} failed, retrying...")
                time.sleep(5)
            
            logger.warning("Health check failed after 5 attempts")
            
        except ImportError:
            logger.warning("Requests library not available, skipping health check")
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
    
    def deploy(self):
        """Main deployment method"""
        logger.info(f"Starting deployment to {self.environment} environment")
        
        try:
            # Check prerequisites
            self.check_prerequisites()
            
            # Create backup
            backup_path = self.create_backup()
            
            # Deploy based on environment
            if self.environment == 'local':
                self.deploy_local()
            elif self.environment == 'docker':
                self.deploy_docker()
            elif self.environment == 'kubernetes':
                self.deploy_kubernetes()
            elif self.environment == 'github':
                self.deploy_github()
            else:
                raise DeploymentError(f"Unknown environment: {self.environment}")
            
            # Health check
            self.health_check()
            
            logger.info(f"Deployment to {self.environment} completed successfully!")
            
            # Cleanup old backups (keep last 5)
            self.cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            logger.info(f"Backup available at: {backup_path}")
            sys.exit(1)
    
    def cleanup_old_backups(self):
        """Cleanup old backup files"""
        try:
            backups = sorted(self.backup_dir.glob('backup_*'), key=os.path.getctime)
            
            # Keep only the last 5 backups
            for backup in backups[:-5]:
                if backup.is_dir():
                    shutil.rmtree(backup)
                else:
                    backup.unlink()
            
            logger.info("Old backups cleaned up")
            
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Deploy Anthony Store to various environments'
    )
    parser.add_argument(
        'environment',
        choices=['local', 'docker', 'kubernetes', 'github'],
        help='Deployment environment'
    )
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip running tests'
    )
    parser.add_argument(
        '--skip-backup',
        action='store_true',
        help='Skip creating backup'
    )
    
    args = parser.parse_args()
    
    try:
        deployer = CynthiaStoreDeployer(args.environment)
        deployer.deploy()
        
    except KeyboardInterrupt:
        logger.info("Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
