from colorama import init, Fore, Back, Style
from tabulate import tabulate
import time

class TestReporter:
    """测试报告工具类"""
    
    @staticmethod
    def _print_box(title, content, color=Fore.CYAN):
        """打印带边框的标题和内容"""
        print(f"\n{color}╔{'═'*(len(title)+2)}╗")
        print(f"║ {title} ║")
        print(f"╚{'═'*(len(title)+2)}╝{Style.RESET_ALL}")
        print(content)
    
    @staticmethod
    def start_test(name):
        """开始测试"""
        TestReporter._print_box(f"▶ 开始测试: {name}", "", Fore.CYAN)
        
    @staticmethod    
    def end_test(name, duration):
        """结束测试"""
        TestReporter._print_box(
            f"◀ 测试完成: {name}",
            f"{Fore.GREEN}耗时: {duration:.2f}s{Style.RESET_ALL}",
            Fore.CYAN
        )
        
    @staticmethod
    def test_step(description):
        """测试步骤"""
        print(f"\n{Fore.YELLOW}▷ {description}{Style.RESET_ALL}")
        return None
        
    @staticmethod
    def success(message):
        """测试成功"""
        print(f"{Back.GREEN}{Fore.WHITE} ✓ {Style.RESET_ALL} {Fore.GREEN}{message}{Style.RESET_ALL}")
        
    @staticmethod
    def failure(message):
        """测试失败"""
        print(f"{Back.RED}{Fore.WHITE} ✗ {Style.RESET_ALL} {Fore.RED}{message}{Style.RESET_ALL}")
        
    @staticmethod
    def summary(results):
        """生成测试总结报告"""
        headers = ["测试项", "状态", "耗时(s)"]
        table = []
        for name, status, duration in results:
            color = Fore.GREEN if status == "通过" else Fore.RED
            table.append([
                f"{color}{name}{Style.RESET_ALL}",
                f"{color}{status}{Style.RESET_ALL}",
                f"{duration:.2f}"
            ])
            
        print("\n" + "="*50)
        print(f"{Fore.CYAN}测试总结报告{Style.RESET_ALL}")
        print("="*50)
        print(tabulate(table, headers, tablefmt="grid"))
