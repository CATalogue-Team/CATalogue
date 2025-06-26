#!/usr/bin/env python3
"""全项目覆盖率测试脚本"""
import subprocess
import sys
from pathlib import Path

def run_tests():
    # 运行单元测试
    print("运行单元测试...")
    unit_result = subprocess.run([
        "pytest", 
        "-c", "pytest-full.ini",
        "--cov-config=.coveragerc",
        "tests/unit"
    ], capture_output=True, text=True)
    print(unit_result.stdout)
    
    # 运行集成测试
    print("\n运行集成测试...")
    integration_result = subprocess.run([
        "pytest",
        "-c", "pytest-full.ini",
        "tests/integration"
    ], capture_output=True, text=True)
    print(integration_result.stdout)
    
    # 运行端到端测试
    print("\n运行端到端测试...")
    e2e_result = subprocess.run([
        "pytest",
        "-c", "pytest-full.ini",
        "tests/e2e/test_deployment.py",
        "tests/e2e/test_initialization.py"
    ], capture_output=True, text=True)
    print(e2e_result.stdout)
    
    # 运行性能测试
    print("\n运行性能测试...")
    perf_result = subprocess.run([
        "locust",
        "-f", "tests/performance/test_load.py",
        "--headless",
        "--users", "100",
        "--spawn-rate", "10",
        "--run-time", "1m"
    ], capture_output=True, text=True)
    print(perf_result.stdout)
    
    # 生成合并覆盖率报告
    print("\n生成合并覆盖率报告...")
    subprocess.run([
        "coverage", "combine"
    ])
    subprocess.run([
        "coverage", "html",
        "--title=CATalogue 全项目覆盖率报告"
    ])
    
    return all([
        unit_result.returncode == 0,
        integration_result.returncode == 0,
        e2e_result.returncode == 0
    ])

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
