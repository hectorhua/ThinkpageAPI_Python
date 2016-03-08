# -*- coding: UTF-8 -*-
# __author__ = 'zhonghua'
# think_alarm.py
# 2015-11-09
# get alarm_info from thinkpageAPI

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# set user-defined python lib path to use other libs like webscraping, redis...
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '/home/prouser/.local/lib/python2.6/site-packages/'))
import redis
import config
import logging.config
from webscraping import download
try:
    import json
except ImportError:
    import simplejson as json

# config setting
settings = config.settings
# logging setting
logging.config.fileConfig('logger.conf')
logger=logging.getLogger('alarm')

# connect to redis
try:
    r = redis.Redis(host = settings['redisHost'], port = int(settings['redisPort']), db = 0)
except Exception, e:
    logger.error('Error: connect redis {0}, {1}: {2}'.format(settings['redisHost'], settings['redisPort'], str(e)))
else:
    logger.debug('Success: connect to redis')

def write_alarm_redis(alarm_info):
    """Write weather alarm info into redis
    """
    global r
    try:
        r.hset('AdditionalWeather', 'alarm', alarm_info)
    except Exception, e:
        logger.error('Error: hset AdditionalWeather alarm: {0}'.format(str(e)))
    else:
        logger.info('Success: hset AdditionalWeather alarm')

def get_alarm():
    """Use webscraping.download fatch weather alarm info with assembled url
    """
    global settings
    D = download.Download()
    url_alarm = settings['url_alarm_header'] + settings['key']
    logger.info('url_alarm = {0}'.format(url_alarm))
    alarm_txt = D.get(url_alarm, write_cache=False, read_cache=False)
    if alarm_txt:
        try:
            json.loads(alarm_txt, encoding='utf-8')
        except Exception, e:
            logger.error('Error: alarm_txt to json.loads')
        else:
            logger.info('Success: get alarm info.')
            return alarm_txt
    else:
        logger.error('Error: get_alarm is NULL.')

if __name__ == '__main__':
    logger.info('########## Program start.')
    alarm_info = get_alarm()
    if alarm_info:
        write_alarm_redis(alarm_info)
    logger.info('########## Program end.')