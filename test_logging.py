
import logging
import sys

# 强制配置日志到标准错误
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

# 测试日志输出
print("=== 开始日志测试 ===", file=sys.stderr)
logging.debug("这是一条DEBUG测试日志")
logging.info("这是一条INFO测试日志")
logging.warning("这是一条WARNING测试日志")
logging.error("这是一条ERROR测试日志")

print("=== 日志测试完成 ===", file=sys.stderr)
