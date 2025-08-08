from sqlalchemy.orm import declarative_base

Base = declarative_base()

# 确保所有模型都被加载
metadata = Base.metadata
