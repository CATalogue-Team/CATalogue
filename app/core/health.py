
from colorama import init, Fore
from app.core.health_check import EnvironmentChecker

init(autoreset=True)

def run_health_checks(app):
    """执行环境检查任务"""
    env_checker = EnvironmentChecker(app)
    
    # 执行检查
    if app.config['FLASK_ENV'] == 'development':
        print(f"\n{Fore.CYAN}=== 开发环境检查 ==={Fore.RESET}")
        checks = env_checker.check_dev_environment()
        
        # 开发模式特定初始化
        if app.config.get('AUTO_INIT_DB', True):
            try:
                from init_db import init_database
                print(f"\n{Fore.YELLOW}正在初始化数据库...{Fore.RESET}")
                init_database(skip_samples=True)
                checks['db_initialized'] = True
                print(f"{Fore.GREEN}数据库初始化完成{Fore.RESET}")
            except Exception as e:
                print(f"{Fore.RED}[!] 数据库初始化失败: {str(e)}{Fore.RESET}")
                checks['db_initialized'] = False
    else:
        print(f"\n{Fore.CYAN}=== 生产环境检查 ==={Fore.RESET}")
        checks = env_checker.check_prod_environment()
    
    # 自动修复
    if app.config.get('AUTO_REPAIR', False):
        repaired = env_checker.run_auto_repair(checks)
        for check_name, fixed in repaired.items():
            if fixed:
                checks[check_name] = True
                print(f"{Fore.GREEN}✓ 已自动修复: {check_name.replace('_', ' ')}{Fore.RESET}")
    
    # 打印检查结果
    print(f"\n{Fore.CYAN}=== 检查结果 ==={Fore.RESET}")
    for check, passed in checks.items():
        status = f"{Fore.GREEN}✓" if passed else f"{Fore.RED}✗"
        print(f"{status} {check.replace('_', ' ')}{Fore.RESET}")
    
    # 保存结果
    env_checker.save_check_results(checks)
    print(f"\n{Fore.CYAN}==================={Fore.RESET}")
    
    return all(checks.values())
