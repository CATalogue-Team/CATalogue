import asyncio
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_command(*args, cwd=None):
    """异步执行命令并返回退出码"""
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd
    )

    async def read_stream(stream, logger_func):
        while True:
            line = await stream.readline()
            if not line:
                break
            try:
                logger_func(line.decode('utf-8').rstrip())
            except UnicodeDecodeError:
                logger_func(line.decode('gbk', errors='replace').rstrip())

    # 创建任务并行读取stdout和stderr
    stdout_task = asyncio.create_task(read_stream(proc.stdout, logger.info))
    stderr_task = asyncio.create_task(read_stream(proc.stderr, logger.error))

    # 等待进程结束
    return_code = await proc.wait()
    
    # 等待输出读取完成
    await asyncio.wait([stdout_task, stderr_task])

    return return_code

async def main():
    try:
        # 初始化PostgreSQL数据库
        if not Path("pgdata").exists():
            ret = await run_command("initdb", "-D", "pgdata")
            if ret != 0:
                raise RuntimeError("数据库初始化失败")

        # 创建数据库
        ret = await run_command("createdb", "-h", "localhost", "-p", "5432", "catalogue")
        if ret != 0:
            raise RuntimeError("数据库创建失败")

        # 运行数据库迁移
        ret = await run_command("alembic", "upgrade", "head")
        if ret != 0:
            raise RuntimeError("数据库迁移失败")

        # 创建超级管理员
        ret = await run_command("python", "scripts/create_superadmin.py")
        if ret != 0:
            raise RuntimeError("超级管理员创建失败")

        logger.info("数据库初始化完成")

    except Exception as e:
        logger.error(f"初始化失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
