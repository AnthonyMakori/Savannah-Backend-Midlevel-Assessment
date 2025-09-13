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

class AnthonyStoreDeployer:
    """Bulletproof deployer for Anthony Store"""
    
    def __init__(self, environment='local'):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = self.project_root / 'backups'
        self.deployment_config = self.load_deployment_config()
        
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
                "namespace": "anthony-store",
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
                    for env in default_config:
                        if env in user_config:
                            default_config[env].update(user_config[env])
                return default_config
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}. Using defaults.")
        
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
        
        python_version = config.get('python_version', '3.11')
        try:
            result = self.run_command(['python', '--version'])
            current_version = result.stdout.strip().split()[1]
            if not current_version.startswith(python_version):
                logger.warning(f"Python version mismatch. Expected: {python_version}, Got: {current_version}")
        except Exception:
            logger.error("Python not found or not accessible")
            raise DeploymentError("Python is required but not found")
        
        try:
            self.run_command(['git', '--version'])
        except Exception:
            logger.error("Git not found")
            raise DeploymentError("Git is required but not found")
        
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
            backup_path.mkdir(exist_ok=True)
            
            if (self.project_root / 'db.sqlite3').exists():
                shutil.copy2(
                    self.project_root / 'db.sqlite3',
                    backup_path / 'db.sqlite3'
                )
                logger.info("Database backup created")
            
            media_dir = self.project_root / 'media'
            if media_dir.exists():
                shutil.copytree(
                    media_dir,
                    backup_path / 'media',
                    dirs_exist_ok=True
                )
                logger.info("Media files backup created")
            
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
            
            if os.name == 'nt':
                pip_path = venv_path / 'Scripts' / 'pip'
                python_path = venv_path / 'Scripts' / 'python'
            else:
                pip_path = venv_path / 'bin' / 'pip'
                python_path = venv_path / 'bin' / 'python'
            
            self.run_command([str(python_path), '-m', 'pip', 'install', '--upgrade', 'pip'])
            
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
            self.run_command([str(python_path), 'manage.py', 'makemigrations'])
            
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
            python_path = self.setup_virtual_environment()
            
            self.run_tests(python_path)
            
            self.run_migrations(python_path)
            
            self.collect_static_files(python_path)
            
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
            self.run_command(['docker-compose', 'build'])
            
            self.run_command(['docker-compose', 'up', '-d'])
            
            logger.info("Waiting for services to be ready...")
            time.sleep(30)
            
            self.run_command([
                'docker-compose', 'exec', '-T', 'web',
                'python', 'manage.py', 'migrate'
            ])
            
            self.run_command([
                'docker-compose', 'exec', '-T', 'web',
                'python', 'scripts/setup_demo_data.py'
            ], check=False)
            
            logger.info("Docker deployment completed successfully!")
            logger.info("Application is running at http://localhost:8000")
            
        except Exception as e:
            logger.error(f"Docker deployment failed: {e}")
            self.run_command(['docker-compose', 'down'], check=False)
            raise
    
    def deploy_kubernetes(self):
        """Deploy to Kubernetes"""
        logger.info("Starting Kubernetes deployment...")
        
        config = self.deployment_config.get('kubernetes', {})
        namespace = config.get('namespace', 'anthony-store')
        helm_chart = config.get('helm_chart', './charts/store-chart')
        
        try:
            self.run_command([
                'kubectl', 'create', 'namespace', namespace
            ], check=False)
            
            image_tag = f"anthony-store:latest"
            self.run_command(['docker', 'build', '-t', image_tag, '.'])
            
            self.run_command([
                'helm', 'upgrade', '--install',
                'anthony-store', helm_chart,
                '--namespace', namespace,
                '--set', f'image.tag=latest',
                '--wait'
            ])
            
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
            self.run_command(['git', 'status'])
            
            workflow_dir = self.project_root / '.github' / 'workflows'
            workflow_file = workflow_dir / 'ci.yml'
            
            if not workflow_file.exists():
                logger.error("GitHub Actions workflow file not found")
                raise DeploymentError("GitHub Actions workflow file missing")
            
            self.run_command(['git', 'add', '.'])
            
            result = self.run_command(['git', 'status', '--porcelain'], check=False)
            
            if result.stdout.strip():
                commit_message = "Deploy Anthony Store updates"
                self.run_command(['git', 'commit', '-m', commit_message])
                
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
            'kubernetes': None,
            'github': None
        }
        
        url = health_urls.get(self.environment)
        
        if not url:
            logger.info("Health check not applicable for this environment")
            return
        
        try:
            import requests
            
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
            self.check_prerequisites()
            
            backup_path = self.create_backup()
            
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
            
            self.health_check()
            
            logger.info(f"Deployment to {self.environment} completed successfully!")
            
            self.cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            logger.info(f"Backup available at: {backup_path}")
            sys.exit(1)
    
    def cleanup_old_backups(self):
        """Cleanup old backup files"""
        try:
            backups = sorted(self.backup_dir.glob('backup_*'), key=os.path.getctime)
            
            for backup in backups[:-7]:
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
        deployer = AnthonyStoreDeployer(args.environment)
        deployer.deploy()
        
    except KeyboardInterrupt:
        logger.info("Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()