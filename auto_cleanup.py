#!/usr/bin/env python
"""
独立的自动清理脚本
可以配置为系统cron任务或Windows计划任务
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cleanup_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_cleanup():
    """执行清理任务"""
    try:
        # 动态导入Flask应用
        from app import app, mongo

        with app.app_context():
            logger.info("开始执行自动清理任务...")

            # 计算7天前的日期
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            logger.info(f"清理条件：创建时间早于 {seven_days_ago.strftime('%Y-%m-%d %H:%M:%S')}")

            # 查询要删除的用户（未验证、非管理员、超过7天）
            query = {
                'email_verified': False,
                'created_at': {'$lt': seven_days_ago},
                'is_admin': False  # 保护管理员账户
            }

            # 先获取要删除的用户数量
            count_to_delete = mongo.db.users.count_documents(query)

            if count_to_delete == 0:
                logger.info("没有需要清理的用户")
                return 0

            # 执行删除
            result = mongo.db.users.delete_many(query)

            # 记录结果
            deleted_count = result.deleted_count
            if deleted_count > 0:
                logger.info(f"✅ 清理完成，删除了 {deleted_count} 个超过7天未验证的用户")

                # 获取一些示例用户（用于记录）
                sample_users = list(mongo.db.users.find(
                    query,
                    {'email': 1, 'username': 1, 'created_at': 1}
                ).limit(5))

                if sample_users:
                    emails = [u['email'] for u in sample_users]
                    logger.info(f"清理的用户示例: {', '.join(emails)}")
            else:
                logger.info("没有用户被清理")

            return deleted_count

    except Exception as e:
        logger.error(f"清理任务执行失败: {e}")
        return 0


if __name__ == '__main__':
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)

    logger.info("=" * 50)
    logger.info("开始运行自动清理服务")

    result = run_cleanup()

    logger.info(f"清理服务运行完成，结果: {result}")
    logger.info("=" * 50)