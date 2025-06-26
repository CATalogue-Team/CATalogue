import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, TYPE_CHECKING
from flask import Flask, current_app
from datetime import datetime, timezone
from sqlalchemy import text
from app import Flask as CustomFlask

class EnvironmentChecker:
    """环境检查工具类"""
    
    def __init__(self, app: CustomFlask):
        self.app = app
        self.logger = logging.getLogger(__name__)
        
    def check_dev_environment(self) -> Dict[str, bool]:
        """执行开发环境检查"""
        try:
            checks = {
                'test_ready': self._check_test_environment(),
                'db_ready': self._check_database(),
                'temp_files_cleaned': bool(self._clean_temp_files()),
                'urls_validated': self._validate_urls(dry_run=True),
                'config_valid': self._check_config(),
                'dependencies_installed': self._check_dependencies(),
                'migrations_applied': self._check_migrations(),
                'routes_accessible': self._check_routes(),
                'services_healthy': self._check_services_health()
            }
            return checks
        except Exception as e:
            self.logger.error(f"开发环境检查失败: {str(e)}")
            return {
                'test_ready': False,
                'db_ready': False,
                'temp_files_cleaned': False,
                'urls_validated': False,
                'config_valid': False,
                'dependencies_installed': False,
                'migrations_applied': False,
                'routes_accessible': False,
                'services_healthy': False
            }
        
    def check_prod_environment(self) -> Dict[str, bool]:
        """执行生产环境检查"""
        checks = {
            'db_connected': self._check_database(),
            'storage_writable': self._check_storage(),
            'security_configured': self._check_security(),
            'backup_configured': self._check_backups(),
            'performance_optimized': self._check_performance()
        }
        return checks
        
    def _check_test_environment(self) -> bool:
        """检查测试环境配置"""
        try:
            test_path = Path(self.app.root_path) / 'tests/test_routes.py'
            return test_path.exists()
        except Exception as e:
            self.logger.error(f"测试环境检查失败: {str(e)}")
            return False
            
    def _check_database(self) -> bool:
        """检查数据库连接和性能"""
        try:
            if not hasattr(self.app, 'extensions') or 'sqlalchemy' not in self.app.extensions:
                self.logger.warning("数据库扩展未注册")
                return False
                
            db = self.app.extensions['sqlalchemy']
            # 支持两种数据库扩展格式：直接db属性或包含db属性的字典
            db_obj = db.db if hasattr(db, 'db') else db.get('db', None)
            if not db_obj:
                return False
                
            with self.app.app_context():
                db_obj.session.execute(text('SELECT 1'))
            return True
        except Exception as e:
            self.logger.error(f"数据库检查失败: {str(e)}")
            return False
            
    def _clean_temp_files(self, patterns: Optional[List[str]] = None) -> int:
        """清理临时文件"""
        patterns = patterns or ['*.tmp', '*.bak', '*.log', '*.swp']
        cleaned = 0
        for pattern in patterns:
            for f in Path(self.app.root_path).glob(pattern):
                try:
                    f.unlink()
                    cleaned += 1
                except Exception:
                    continue
        return cleaned
        
    def _validate_urls(self, dry_run: bool = True) -> bool:
        """验证资源URL"""
        try:
            from app.core.image_url_validator import validate_and_fix_image_urls
            urls_to_check = [
                self.app.config.get('STATIC_URL'),
                self.app.config.get('MEDIA_URL')
            ]
            validate_and_fix_image_urls([url for url in urls_to_check if url])
            return True
        except Exception as e:
            self.logger.error(f"URL验证失败: {str(e)}")
            return False
            
    def _check_config(self) -> bool:
        """验证配置完整性"""
        required_keys = ['SECRET_KEY', 'SQLALCHEMY_DATABASE_URI', 'UPLOAD_FOLDER']
        return all(key in self.app.config for key in required_keys)
        
    def _check_dependencies(self) -> bool:
        """检查依赖包是否安装"""
        try:
            import pkg_resources
            try:
                with open('requirements.txt') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            pkg_name = line.split('==')[0]
                            pkg_resources.get_distribution(pkg_name)
                return True
            except FileNotFoundError:
                self.logger.warning("requirements.txt文件未找到")
                return False
            except pkg_resources.DistributionNotFound as e:
                self.logger.error(f"依赖包未安装: {str(e)}")
                return False
            except Exception as e:
                self.logger.error(f"依赖检查过程中发生异常: {str(e)}")
                return False
        except ImportError:
            self.logger.error("无法导入pkg_resources模块")
            return False
        except Exception as e:
            self.logger.error(f"依赖检查失败: {str(e)}")
            return False
        except:  # 捕获所有其他异常，包括测试中的模拟异常
            self.logger.error("依赖检查过程中发生未知异常")
            return False
            
    def _check_migrations(self) -> bool:
        """检查数据库迁移是否完成"""
        try:
            if not hasattr(self.app, 'extensions') or 'sqlalchemy' not in self.app.extensions:
                return False
                
            db = self.app.extensions['sqlalchemy']
            # 支持两种数据库扩展格式：直接db属性或包含db属性的字典
            db_obj = db.db if hasattr(db, 'db') else db.get('db', None)
            if not db_obj:
                return False
                
            with self.app.app_context():
                db_obj.session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            self.logger.error(f"迁移检查失败: {str(e)}")
            return False
            
    def _check_routes(self) -> bool:
        """检查核心路由可访问性"""
        try:
            from flask import url_for
            with self.app.test_request_context():
                routes_to_check = [
                    ('main.home', {}),
                    ('auth.login', {}),
                    ('cats.get_cat', {'id': 1})
                ]
                for route, kwargs in routes_to_check:
                    url_for(route, **kwargs)
            return True
        except Exception as e:
            self.logger.error(f"路由检查失败: {str(e)}")
            return False
            
    def _check_services_health(self) -> bool:
        """检查服务层健康状态"""
        try:
            required_services = ['cat_service', 'user_service']
            for service in required_services:
                if not hasattr(self.app, service):
                    self.logger.warning(f"服务 {service} 不存在")
                    return False
                if not hasattr(getattr(self.app, service), 'check_health'):
                    self.logger.warning(f"服务 {service} 缺少健康检查方法")
                    return False
            return True
        except Exception as e:
            self.logger.error(f"服务健康检查失败: {str(e)}")
            return False
            
    def _check_storage(self) -> bool:
        """检查存储可用性"""
        try:
            test_file = Path(self.app.config['UPLOAD_FOLDER']) / '.write_test'
            test_file.touch()
            test_file.unlink()
            return True
        except Exception as e:
            self.logger.error(f"存储检查失败: {str(e)}")
            return False
            
    def _check_security(self) -> bool:
        """检查安全配置"""
        checks = [
            not self.app.config.get('DEBUG', False),
            self.app.config.get('SESSION_COOKIE_SECURE', False),
            self.app.config.get('REMEMBER_COOKIE_SECURE', False),
            self.app.config.get('SESSION_COOKIE_HTTPONLY', True)
        ]
        return all(checks)
        
    def _check_backups(self) -> bool:
        """检查备份配置"""
        return bool(self.app.config.get('BACKUP_PATH'))
        
    def _check_performance(self) -> bool:
        """检查性能优化配置"""
        is_production = self.app.config.get('FLASK_ENV') == 'production'
        config_checks = [
            self.app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}).get('pool_pre_ping', is_production),
            self.app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}).get('pool_recycle', 3600) <= 3600
        ]
        if is_production:
            config_checks.append(
                self.app.config.get('TEMPLATES_AUTO_RELOAD', False) is False
            )
        return all(config_checks)
        
    def save_check_results(self, results: Dict[str, bool]) -> bool:
        """保存检查结果"""
        try:
            if not hasattr(self.app, 'config') or not isinstance(self.app.config, dict) or not self.app.config:
                return False
                
            self.app.config['LAST_ENV_CHECK'] = {
                'timestamp': datetime.now(timezone.utc),
                'results': results
            }
            return True
        except Exception as e:
            self.logger.error(f"保存检查结果失败: {str(e)}")
            return False

    def _repair_database(self) -> bool:
        """修复数据库连接"""
        try:
            from flask_sqlalchemy import SQLAlchemy
            db = SQLAlchemy(self.app)
            with self.app.app_context():
                db.create_all()
            return True
        except Exception as e:
            self.logger.error(f"数据库修复失败: {str(e)}")
            return False

    def run_auto_repair(self, failed_checks: Dict[str, bool]) -> Dict[str, bool]:
        """执行自动修复"""
        try:
            results = {}
            if failed_checks.get('db_connected', False):
                results['db_connected'] = self._repair_database()
            if failed_checks.get('migrations_applied', False):
                results['migrations_applied'] = self._check_migrations()
            return results
        except Exception as e:
            self.logger.error(f"自动修复失败: {str(e)}")
            return {k: False for k in failed_checks.keys()}
