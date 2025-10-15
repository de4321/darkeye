# 配置log系统，使用的时候import logging就可以使用
import logging
from logging.handlers import TimedRotatingFileHandler
from config import LOG_FILE


# 创建 logger
logger = logging.getLogger()#全局唯一
logger.setLevel(logging.DEBUG)  # 可调节 DEBUG/INFO/WARNING/...

# 控制台输出
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'))
logger.addHandler(console_handler)

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_FILE.touch(exist_ok=True)  # 如果文件不存在则创建

# 文件输出，按天分文件，最多保留7天
file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight', backupCount=7, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s %(funcName)s - %(message)s'))
logger.addHandler(file_handler)

logging.info("--------------------log配置完成--------------------")