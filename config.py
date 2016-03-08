# -*- coding: UTF-8 -*-
#__author__ = 'zhonghua'

import re
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '/home/pengli/python-site-packages/lib/python2.6/site-packages/'))
import ConfigParser

def read_settings(settings_file='settings.ini'):
    """Read settings
    """
    cfg = ConfigParser.ConfigParser()
    cfg.read(settings_file)
    settings = {}
    # 常规参数
    for option in ['areaid_list', 'url_header', 'url_tail', \
                   'url_alarm_header', 'lang_CN', 'lang_EN', 'city_num', \
                   'key', 'citylist', 'proxyFlag', 'proxyHost', 'proxyPort',\
                   'redisHost', 'redisPort', 'sleepTime', 'skipNum']:
        try:
            settings[option] = cfg.get('setting', option).strip()
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError), e:
            settings[option] = ''
    return settings

def settings2dict(settings_file='settings.ini'):
    """Convert settings into dictionary
    """
    settings = {}
    for line in open(settings_file):
        if not line.startswith('#'):
            m = re.compile(r'([^=]+)\s*=\s*(.+)').search(line)
            if m:
                settings[m.groups()[0].strip()] = m.groups()[1].strip()
    return settings

# 用户可修改的配置参数
settings = read_settings()