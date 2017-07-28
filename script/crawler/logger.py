import logging
#import logging.handlers

#LOG_FILE = 'tst.log'

#handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5)# 实例化handler
handler = logging.StreamHandler(); #输出到控制台
fmt = '[%(asctime)s - %(filename)s:%(lineno)s - %(name)s] : %(message)s'

formatter = logging.Formatter(fmt)# 实例化formatter 
handler.setFormatter(formatter)# 为handler添加formatter 

logger = logging.getLogger('tst')# 获取名为tst的logger 
logger.addHandler(handler)# 为logger添加handler 
logger.setLevel(logging.DEBUG)

#logger.info('first info message')
#logger.debug('first debug message')

def info(message):
    logger.info(message)

def debug(message):
    logger.debug(message)
