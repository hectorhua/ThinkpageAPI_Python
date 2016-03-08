# -*- coding: UTF-8 -*-
# __author__ = 'zhonghua'
# think_forecast.py
# 2015-11-10
# get forecast_info from thinkpageAPI

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# set user-defined python lib path to use other libs like webscraping, redis...
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '/home/prouser/.local/lib/python2.6/site-packages/'))
import redis
import config
import logging.config
import csv
import wf_items
import threading
import Queue
from webscraping import download, common, adt
try:
    import json
except ImportError:
    import simplejson as json

# config setting
settings = config.settings

# logging setting
logging.config.fileConfig('logger.conf')
logger=logging.getLogger('forecast')

# q_citys store all urls
q_citys = Queue.Queue()

# define counter
counter = 0

# connect to redis
try:
    r = redis.Redis(host = settings['redisHost'], port = int(settings['redisPort']), db = 0)
except Exception, e:
    logger.error('Error: connect redis {0}, {1}: {2}'.format(settings['redisHost'], settings['redisPort'], str(e)))
else:
    logger.debug('Success: connect to redis')

def gene_url(cityID):
    """Generate forecast urls with args in settings
    """
    global settings
    cityURL = []
    city_url_cn = settings['url_header'] + cityID + '&language=' + settings['lang_CN'] + settings['url_tail'] + settings['key']
    city_url_en = settings['url_header'] + cityID + '&language=' + settings['lang_EN'] + settings['url_tail'] + settings['key']
    cityURL.append(city_url_cn)
    cityURL.append(city_url_en)
    return cityURL

def get_city_forecast(cityURL):
    """Download forecast txt from thinkpageAPI with cityURL
    """
    logger.debug('in get_city_forecast')
    D = download.Download()
    forecast_txt = D.get(cityURL, delay=0.01, write_cache=False, read_cache=False)
    loop_num = 0
    while 1:
        if forecast_txt:
            break
        if loop_num >= int(settings['skipNum']):
            break
        forecast_txt = D.get(cityURL, delay=0.01, write_cache=False, read_cache=False)
        loop_num += 1
        logger.debug('looping city: {0}, {1}'.format(loop_num, cityURL))
    if forecast_txt:
        try:
            json.loads(forecast_txt, encoding='utf-8')
        except Exception, e:
            logger.error('Error: alarm_txt to json.loads, url = {0}'.format(cityURL))
            return
        else:
            return forecast_txt
    else:
        logger.error('Error: forecast_txt is NULL, url = {0}'.format(cityURL))
        return

def integra_forecast_cn(forecast_json_cn, cityenName):
    """Integrate CN forecast info
    """
    logger.debug('in integra_forecast_cn, cityenName = {0}'.format(cityenName))

    wfitem_cn = wf_items.gene_items_cn()
    cityID = ''
    # 解析中文信息
    if forecast_json_cn['status'] == 'OK':
        # 获取基本信息
        try:
            cityID = forecast_json_cn['weather'][0]['city_id']
            wfitem_cn['city_name'] = forecast_json_cn['weather'][0]['city_name']
            wfitem_cn['city_name_weather'] = forecast_json_cn['weather'][0]['city_name'] + '地区天气预报:'
            wfitem_cn['city_name_en_weather'] = 'WEATHER FORECAST FOR ' + cityenName + ':'
            wfitem_cn['observe_time'] = forecast_json_cn['weather'][0]['last_update']
        except Exception, e:
            logger.warning('Get basic_cn info exception: {0}, {1}'.format(cityID, str(e)))
        # 获取实时气象
        try:
            wfitem_cn['current_status'] = '当前气象:' + forecast_json_cn['weather'][0]['now']['text']
            wfitem_cn['current_temperature'] = current_temperature = '气温:' + forecast_json_cn['weather'][0]['now']['temperature'] + 'C'
            wfitem_cn['current_humidity'] = current_humidity = '湿度:' +  forecast_json_cn['weather'][0]['now']['humidity'] + '%'
            wfitem_cn['current_wind_power'] = current_wind_power = forecast_json_cn['weather'][0]['now']['wind_scale'] + '级'
            wfitem_cn['current_wind_direction'] = current_wind_direction = forecast_json_cn['weather'][0]['now']['wind_direction'] + '风'
            wfitem_cn['feel_temperature'] = feel_temperature = '体感:' + forecast_json_cn['weather'][0]['now']['feels_like'] + 'C'
            wfitem_cn['visibility'] = visibility = '能见度:' + forecast_json_cn['weather'][0]['now']['visibility'] + '公里'
            wfitem_cn['atmospheric'] = atmospheric = '气压:' + forecast_json_cn['weather'][0]['now']['pressure'] + 'hpa'
            wfitem_cn['observe_all'] = '实时气象:' + forecast_json_cn['weather'][0]['now']['text'] + ' ' + \
                                    current_temperature + ' ' + feel_temperature + ' ' + current_humidity + ' ' + \
                                    current_wind_direction + ' ' + current_wind_power + ' ' + visibility + ' ' + atmospheric + ' ' + \
                                    '更新时间:' + forecast_json_cn['weather'][0]['last_update']
        except Exception, e:
            logger.warning('Get current_cn info exception: {0}, {1}'.format(cityID, str(e)))
        # 获取未来天气
        wfitem_cn['forecast_name'] = '未来预报:'
        try:
            for i in range(7):
                forecast_date = forecast_json_cn['weather'][0]['future'][i]['date']
                forecast_week = forecast_json_cn['weather'][0]['future'][i]['day']
                status_day_night = forecast_json_cn['weather'][0]['future'][i]['text']
                wind_direction_power = forecast_json_cn['weather'][0]['future'][i]['wind']
                temperature_high = '最高气温:' + forecast_json_cn['weather'][0]['future'][i]['high'] + 'C'
                temperature_low = '最低气温:' + forecast_json_cn['weather'][0]['future'][i]['low'] + 'C'
                wfitem_cn['forecast_date'].append(forecast_date)
                wfitem_cn['forecast_week'].append(forecast_week)
                wfitem_cn['status_day_night'].append(status_day_night)
                wfitem_cn['wind_direction_power'].append(wind_direction_power)
                wfitem_cn['temperature_high'].append(temperature_high)
                wfitem_cn['temperature_low'].append(temperature_low)
                wfitem_cn['forecast_all'].append(forecast_date + forecast_week + ':' + status_day_night + ' ' + wind_direction_power + ' ' + temperature_high + ' ' + temperature_low)
            wfitem_cn['forecast_all0'] = wfitem_cn['forecast_all'][0]
            wfitem_cn['forecast_all1'] = wfitem_cn['forecast_all'][1]
            wfitem_cn['forecast_all2'] = wfitem_cn['forecast_all'][2]
            wfitem_cn['forecast_all3'] = wfitem_cn['forecast_all'][3]
            wfitem_cn['forecast_all4'] = wfitem_cn['forecast_all'][4]
            wfitem_cn['forecast_all5'] = wfitem_cn['forecast_all'][5]
            wfitem_cn['forecast_all6'] = wfitem_cn['forecast_all'][6]
            logger.debug('#############length = {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'.format(cityID, \
                           len(wfitem_cn['forecast_date']), len(wfitem_cn['forecast_week']), len(wfitem_cn['status_day_night']), len(wfitem_cn['wind_direction_power']), \
                           len(wfitem_cn['temperature_high']), len(wfitem_cn['temperature_low']), len(wfitem_cn['forecast_all'])))
        except Exception, e:
            logger.warning('Get future_cn info exception: {0}, {1}, length of date={2}, week={3}, day_n={4}, direc={5}, tempH={6}, tempL={7}, foreAll={8}'.format(cityID, str(e), \
                           len(wfitem_cn['forecast_date']), len(wfitem_cn['forecast_week']), len(wfitem_cn['status_day_night']), len(wfitem_cn['wind_direction_power']), \
                           len(wfitem_cn['temperature_high']), len(wfitem_cn['temperature_low']), len(wfitem_cn['forecast_all'])))
        # 获取生活指数
        try:
            wfitem_cn['dressing_brief'] = dressing_brief = forecast_json_cn['weather'][0]['today']['suggestion']['dressing']['brief']
            wfitem_cn['ultraviolet_brief'] = ultraviolet_brief = forecast_json_cn['weather'][0]['today']['suggestion']['uv']['brief']
            wfitem_cn['car_washing_brief'] = car_washing_brief = forecast_json_cn['weather'][0]['today']['suggestion']['car_washing']['brief']
            wfitem_cn['travel_brief'] = travel_brief = forecast_json_cn['weather'][0]['today']['suggestion']['travel']['brief']
            wfitem_cn['flu_brief'] = flu_brief = forecast_json_cn['weather'][0]['today']['suggestion']['flu']['brief']
            wfitem_cn['sport_brief'] = sport_brief = forecast_json_cn['weather'][0]['today']['suggestion']['sport']['brief']
            wfitem_cn['index_all'] = '穿衣指数:' + dressing_brief + ' ' + '紫外线指数:' + ultraviolet_brief + ' ' + '洗车指数:' + car_washing_brief + ' ' + \
                                   '旅游指数:' + travel_brief + ' ' + '感冒指数:' + flu_brief + ' ' + '运动指数:' + sport_brief
            wfitem_cn['dressing_details'] = forecast_json_cn['weather'][0]['today']['suggestion']['dressing']['details']
            wfitem_cn['ultraviolet_details'] = forecast_json_cn['weather'][0]['today']['suggestion']['uv']['details']
            wfitem_cn['car_washing_details'] = forecast_json_cn['weather'][0]['today']['suggestion']['car_washing']['details']
            wfitem_cn['travel_details'] = forecast_json_cn['weather'][0]['today']['suggestion']['travel']['details']
            wfitem_cn['flu_details'] = forecast_json_cn['weather'][0]['today']['suggestion']['flu']['details']
            wfitem_cn['sport_details'] = forecast_json_cn['weather'][0]['today']['suggestion']['sport']['details']
        except Exception, e:
            logger.warning('Get index_cn info exception: {0}, {1}'.format(cityID, str(e)))
        # 获取空气质量
        try:
            wfitem_cn['AQI'] = AQI = 'AQI:' + forecast_json_cn['weather'][0]['now']['air_quality']['city']['aqi']
            wfitem_cn['PM25'] = PM25 = 'PM25:' + forecast_json_cn['weather'][0]['now']['air_quality']['city']['pm25']
            wfitem_cn['PM10'] = PM10 = 'PM10:' + forecast_json_cn['weather'][0]['now']['air_quality']['city']['pm10']
            wfitem_cn['SO2'] = SO2 = 'SO2:' + forecast_json_cn['weather'][0]['now']['air_quality']['city']['so2']
            wfitem_cn['NO2'] = NO2 = 'NO2:' +  forecast_json_cn['weather'][0]['now']['air_quality']['city']['no2']
            wfitem_cn['CO'] = CO =  'CO:' + forecast_json_cn['weather'][0]['now']['air_quality']['city']['co']
            wfitem_cn['O3'] = O3 =  'O3:' + forecast_json_cn['weather'][0]['now']['air_quality']['city']['o3']
            wfitem_cn['air_quality'] = air_quality =  '空气质量:' + forecast_json_cn['weather'][0]['now']['air_quality']['city']['quality']
            # wfitem_cn['air_last_update'] = air_last_update =  '' + forecast_json_cn['weather'][0]['now']['air_quality']['city']['last_update']
            wfitem_cn['air_all'] = air_quality + ' ' + AQI + ' ' + PM25 + ' ' + PM10 + ' ' + SO2 + ' ' + NO2 + ' ' + CO + ' ' + O3
        except Exception, e:
            logger.warning('Get air_quality_cn info exception: {0}, {1}'.format(cityID, str(e)))
        # 组合json_all_redis
        json_all_redis = {}
        try:
            json_all_redis['future'] = forecast_json_cn['weather'][0]['future']
            json_all_redis['index'] = forecast_json_cn['weather'][0]['today']
            json_all_redis['now'] = forecast_json_cn['weather'][0]['now']
            json_all_redis['last_update'] = forecast_json_cn['weather'][0]['last_update']
            json_all_redis['city_id'] = forecast_json_cn['weather'][0]['city_id']
            json_all_redis['city_name'] = forecast_json_cn['weather'][0]['city_name']
            json_all_redis['status'] = 'OK'
            json_all_redis_str = (json.dumps(json_all_redis)).decode("unicode-escape")
            wfitem_cn['json_all_redis'] = json_all_redis_str
        except Exception, e:
            logger.warning('Integrate json_all_redis exception: {0}, {1}'.format(cityID, str(e)))
        # 组合caacwfnew24, caacwfnew48, caacwfnew72
        try:
            if wfitem_cn['wind_direction_power'][0] == '未知' or len(wfitem_cn['wind_direction_power'][0]) == 0:
                windCaacwfnew24 = forecast_json_cn['weather'][0]['now']['wind_direction'] + '风' + forecast_json_cn['weather'][0]['now']['wind_scale'] + '级'
            else:
                windCaacwfnew24 = wfitem_cn['wind_direction_power'][0]
            wfitem_cn['caacwfnew24'] = forecast_json_cn['weather'][0]['city_name'] + '|' + wfitem_cn['status_day_night'][0] + '|' + windCaacwfnew24 + '|' + forecast_json_cn['weather'][0]['future'][0]['high'] + '|' + forecast_json_cn['weather'][0]['future'][0]['low']
            wfitem_cn['caacwfnew48'] = forecast_json_cn['weather'][0]['city_name'] + '|' + wfitem_cn['status_day_night'][1] + '|' +  wfitem_cn['wind_direction_power'][1] + '|' + forecast_json_cn['weather'][0]['future'][1]['high'] + '|' + forecast_json_cn['weather'][0]['future'][1]['low']
            wfitem_cn['caacwfnew72'] = forecast_json_cn['weather'][0]['city_name'] + '|' + wfitem_cn['status_day_night'][2] + '|' +  wfitem_cn['wind_direction_power'][2] + '|' + forecast_json_cn['weather'][0]['future'][2]['high'] + '|' + forecast_json_cn['weather'][0]['future'][2]['low']
        except Exception, e:
            logger.warning('Integrate caacwfnew24,48,72 exception: {0}, {1}, length of date={2}, week={3}, day_n={4}, direc={5}, tempH={6}, tempL={7}, foreAll={8}'.format(cityID, str(e), \
                           len(wfitem_cn['forecast_date']), len(wfitem_cn['forecast_week']), len(wfitem_cn['status_day_night']), len(wfitem_cn['wind_direction_power']), \
                           len(wfitem_cn['temperature_high']), len(wfitem_cn['temperature_low']), len(wfitem_cn['forecast_all'])))
    return wfitem_cn

def integra_forecast_en(forecast_json_en):
    """Integrate EN forecast info
    """
    logger.debug('in integra_forecast_en')
    wfitem_en = wf_items.gene_items_en()

    # 解析英文信息
    if forecast_json_en['status'] == 'OK':
        cityID = forecast_json_en['weather'][0]['city_id']
        # 获取实时气象
        try:
            wfitem_en['current_status_en'] = forecast_json_en['weather'][0]['now']['text']
            wfitem_en['current_temperature_en'] = current_temperature_en = 'Temp:' + forecast_json_en['weather'][0]['now']['temperature'] + 'C'
            wfitem_en['current_humidity_en'] = current_humidity_en = 'Humidity:' +  forecast_json_en['weather'][0]['now']['humidity'] + '%'
            wfitem_en['current_wind_power_en'] = current_wind_power_en = forecast_json_en['weather'][0]['now']['wind_scale'] + 'scale'
            wfitem_en['current_wind_direction_en'] = current_wind_direction_en = 'Wind:' + forecast_json_en['weather'][0]['now']['wind_direction']
            wfitem_en['feel_temperature_en'] = feel_temperature_en = 'Feel:' + forecast_json_en['weather'][0]['now']['feels_like'] + 'C'
            wfitem_en['visibility_en'] = visibility_en = 'Visibility:' + forecast_json_en['weather'][0]['now']['visibility'] + 'Km'
            wfitem_en['atmospheric_en'] = atmospheric_en = 'Pressure:' + forecast_json_en['weather'][0]['now']['pressure'] + 'hpa'
            wfitem_en['observe_all_en'] = 'Now:' + forecast_json_en['weather'][0]['now']['text'] + ' ' + \
                                    current_temperature_en + ' ' + feel_temperature_en + ' ' + current_humidity_en + ' ' + \
                                    current_wind_direction_en + ' ' + current_wind_power_en + ' ' + visibility_en + ' ' + atmospheric_en + ' ' + \
                                    'update:' + forecast_json_en['weather'][0]['last_update']
        except Exception, e:
            logger.warning('Get current_en info exception: {0}, {1}'.format(cityID, str(e)))
        # 获取未来天气
        wfitem_en['forecast_name_en'] = 'Weather Forecast:'
        try:
            for i in range(7):
                forecast_date_en = forecast_json_en['weather'][0]['future'][i]['date']
                forecast_week_en = forecast_json_en['weather'][0]['future'][i]['day']
                status_day_night_en = forecast_json_en['weather'][0]['future'][i]['text']
                wind_direction_power_en = forecast_json_en['weather'][0]['future'][i]['wind']
                temperature_high_en = 'High:' + forecast_json_en['weather'][0]['future'][i]['high'] + 'C'
                temperature_low_en = 'Low:' + forecast_json_en['weather'][0]['future'][i]['low'] + 'C'
                wfitem_en['forecast_date_en'].append(forecast_date_en)
                wfitem_en['forecast_week_en'].append(forecast_week_en)
                wfitem_en['status_day_night_en'].append(status_day_night_en)
                wfitem_en['wind_direction_power_en'].append(wind_direction_power_en)
                wfitem_en['temperature_high_en'].append(temperature_high_en)
                wfitem_en['temperature_low_en'].append(temperature_low_en)
                wfitem_en['forecast_all_en'].append(forecast_date_en + forecast_week_en + ':' + status_day_night_en + ' ' + wind_direction_power_en + ' ' + temperature_high_en + ' ' + temperature_low_en)
            wfitem_en['forecast_all_en0'] = wfitem_en['forecast_all_en'][0]
            wfitem_en['forecast_all_en1'] = wfitem_en['forecast_all_en'][1]
            wfitem_en['forecast_all_en2'] = wfitem_en['forecast_all_en'][2]
            wfitem_en['forecast_all_en3'] = wfitem_en['forecast_all_en'][3]
            wfitem_en['forecast_all_en4'] = wfitem_en['forecast_all_en'][4]
            wfitem_en['forecast_all_en5'] = wfitem_en['forecast_all_en'][5]
            wfitem_en['forecast_all_en6'] = wfitem_en['forecast_all_en'][6]
        except Exception, e:
            logger.warning('Get future_en info exception: {0}, {1}, length of date={2}, week={3}, day_n={4}, direc={5}, tempH={6}, tempL={7}, foreAll={8}'.format(cityID, str(e), \
                           len(wfitem_en['forecast_date_en']), len(wfitem_en['forecast_week_en']), len(wfitem_en['status_day_night_en']), len(wfitem_en['wind_direction_power_en']), \
                           len(wfitem_en['temperature_high_en']), len(wfitem_en['temperature_low_en']), len(wfitem_en['forecast_all_en'])))
        # 获取生活指数
        try:
            wfitem_en['dressing_brief_en'] = dressing_brief_en = forecast_json_en['weather'][0]['today']['suggestion']['dressing']['brief']
            wfitem_en['ultraviolet_brief_en'] = ultraviolet_brief_en = forecast_json_en['weather'][0]['today']['suggestion']['uv']['brief']
            wfitem_en['car_washing_brief_en'] = car_washing_brief_en = forecast_json_en['weather'][0]['today']['suggestion']['car_washing']['brief']
            wfitem_en['travel_brief_en'] = travel_brief_en = forecast_json_en['weather'][0]['today']['suggestion']['travel']['brief']
            wfitem_en['flu_brief_en'] = flu_brief_en = forecast_json_en['weather'][0]['today']['suggestion']['flu']['brief']
            wfitem_en['sport_brief_en'] = sport_brief_en = forecast_json_en['weather'][0]['today']['suggestion']['sport']['brief']
            wfitem_en['index_all_en'] = 'Dressing:' + dressing_brief_en + ' ' + 'Ultraviolet:' + ultraviolet_brief_en + ' ' + 'Car_washing:' + car_washing_brief_en + ' ' + \
                                   'Travel:' + travel_brief_en + ' ' + 'Flu:' + flu_brief_en + ' ' + 'Sport:' + sport_brief_en

            wfitem_en['dressing_details_en'] = forecast_json_en['weather'][0]['today']['suggestion']['dressing']['details']
            wfitem_en['ultraviolet_details_en'] = forecast_json_en['weather'][0]['today']['suggestion']['uv']['details']
            wfitem_en['car_washing_details_en'] = forecast_json_en['weather'][0]['today']['suggestion']['car_washing']['details']
            wfitem_en['travel_details_en'] = forecast_json_en['weather'][0]['today']['suggestion']['travel']['details']
            wfitem_en['flu_details_en'] = forecast_json_en['weather'][0]['today']['suggestion']['flu']['details']
            wfitem_en['sport_details_en'] = forecast_json_en['weather'][0]['today']['suggestion']['sport']['details']
        except Exception, e:
            logger.warning('Get index_en info exception: {0}, {1}'.format(cityID, str(e)))
        # 获取空气质量
        try:
            wfitem_en['AQI_en'] = AQI_en = 'AQI:' + forecast_json_en['weather'][0]['now']['air_quality']['city']['aqi']
            wfitem_en['PM25_en'] = PM25_en = 'PM25:' + forecast_json_en['weather'][0]['now']['air_quality']['city']['pm25']
            wfitem_en['PM10_en'] = PM10_en = 'PM10:' + forecast_json_en['weather'][0]['now']['air_quality']['city']['pm10']
            wfitem_en['SO2_en'] = SO2_en = 'SO2:' + forecast_json_en['weather'][0]['now']['air_quality']['city']['so2']
            wfitem_en['NO2_en'] = NO2_en = 'NO2:' +  forecast_json_en['weather'][0]['now']['air_quality']['city']['no2']
            wfitem_en['CO_en'] = CO_en =  'CO:' + forecast_json_en['weather'][0]['now']['air_quality']['city']['co']
            wfitem_en['O3_en'] = O3_en =  'O3:' + forecast_json_en['weather'][0]['now']['air_quality']['city']['o3']
            wfitem_en['air_quality_en'] = air_quality_en =  'Air_quality:' + forecast_json_en['weather'][0]['now']['air_quality']['city']['quality']
            # wfitem_en['air_last_update_en'] = air_last_update_en =  '' + forecast_json_en['weather'][0]['now']['air_quality']['city']['last_update']
            wfitem_en['air_all_en'] = air_quality_en + ' ' + AQI_en + ' ' + PM25_en + ' ' + PM10_en + ' ' + SO2_en + ' ' + NO2_en + ' ' + CO_en + ' ' + O3_en
        except Exception, e:
            logger.warning('Get air_quality_en info exception: {0}, {1}'.format(cityID, str(e)))
        # 组合json_all_redis_en
        json_all_redis_en = {}
        try:
            json_all_redis_en['future'] = forecast_json_en['weather'][0]['future']
            json_all_redis_en['index'] = forecast_json_en['weather'][0]['today']
            json_all_redis_en['now'] = forecast_json_en['weather'][0]['now']
            json_all_redis_en['last_update'] = forecast_json_en['weather'][0]['last_update']
            json_all_redis_en['city_id'] = forecast_json_en['weather'][0]['city_id']
            json_all_redis_en['city_name'] = forecast_json_en['weather'][0]['city_name']
            json_all_redis_en['status'] = 'OK'
            json_all_redis_en_str = json.dumps(json_all_redis_en)
            wfitem_en['json_all_redis_en'] = json_all_redis_en_str
        except Exception, e:
            logger.warning('Integrate json_all_redis_en exception: {0}, {1}'.format(cityID, str(e)))
    return wfitem_en

def parse_forecast(forecast_txt_cn, forecast_txt_en, cityID, cityenName):
    """Try json.loads forecast_txt_cn and forecast_txt_en, distribute into integrate function
    """
    global counter
    logger.debug('in parse_forecast')
    wfitem = {}
    wfitem['city_ID'] = cityID
    wfitem['city_name_en'] = cityenName
    # json_all为原始json数据
    wfitem['json_all'] = forecast_txt_cn
    wfitem['json_all_en'] = forecast_txt_en

    wfitem_cn = {}
    try:
        forecast_json_cn = json.loads(forecast_txt_cn, encoding='utf-8')
    except Exception, e:
        logger.error('Error: forecast_txt_cn to json.loads, cityID = {0}'.format(cityID))
    else:
        logger.debug('cityID = {0}, cityenName = {1}'.format(cityID, cityenName))
        wfitem_cn = integra_forecast_cn(forecast_json_cn, cityenName)
    # logger.debug(json.dumps(wfitem_cn).decode("unicode-escape"))
    wfitem_en = {}
    try:
        forecast_json_en = json.loads(forecast_txt_en, encoding='utf-8')
    except Exception, e:
        logger.error('Error: forecast_txt_en to json.loads, cityID = {0}'.format(cityID))
    else:
        wfitem_en = integra_forecast_en(forecast_json_en)
    # logger.debug(json.dumps(wfitem_en).decode("unicode-escape"))
    # combine all wfitems
    wfitems = wfitem.copy()
    try:
        wfitems.update(wfitem_cn)
        wfitems.update(wfitem_en)
    except Exception, e:
        logger.error('Error: Merge wfitems: {0}'.format(cityID))
    else:
        logger.info('Success: Merge wfitems: {0}, counter = {1}'.format(cityID, counter))
    # logger.debug(json.dumps(wfitems).decode("unicode-escape"))
    return wfitems

def write_redis(wfitem, cityID):
    """Write the wfitem into Redis with structure defined by wf_items.write_redis_item
    """
    global r, settings
    logger.debug('in write_redis')
    for item in wf_items.write_redis_item:
        try:
            r.hset(cityID, item, wfitem[item])
        except Exception, e:
            logger.warning('Write redis in r.hset exception {0}'.format(str(e)))
            # logger.debug("item = {0}  wfitem[item] = {1}".format(item, wfitem[item]))
    logger.debug('Success: write_redis')

def main(city_info):
    """test
    """
    logger.debug('in main')
    city_url_cn = city_url_en =cityID = cityenName = cityName = ''
    forecast_txt_cn = forecast_txt_en = ''
    city_url_cn,  city_url_en, cityID, cityenName = city_info.split('|')
    forecast_txt_cn = get_city_forecast(city_url_cn)
    forecast_txt_en = get_city_forecast(city_url_en)
    if forecast_txt_cn and forecast_txt_en:
        # logger.debug('forecast_txt_cn = '+forecast_txt_cn)
        # logger.debug('forecast_txt_en = '+forecast_txt_en)
        # cityName read from csv file is gbk code, uni_cityName = cityName.decode('gbk')
        wfitem = parse_forecast(forecast_txt_cn, forecast_txt_en, cityID, cityenName)
        write_redis(wfitem, cityID)
    else:
        logger.warning('Get forecast_txt_cn or forecast_txt_en exception: {0}'.format(cityID))

def thread_task():
    global counter
    while 1:
        if q_citys.empty():
            break
        else:
            city_info = q_citys.get()
            main(city_info)
            counter += 1
def add_threads():
    logger.debug('in add_threads')

    # 线程队列
    threads = []
    for i in range(10):
        threads.append(threading.Thread(target=thread_task))
    # 启动线程
    for t in threads:
        t.start()
    # 阻塞主线程
    logger.debug('Current has {0} threads'.format((threading.activeCount() - 1)))
    for t in threads:
        t.join()

def read_city():
    global q_citys
    logger.info('in read_city')
    city_csv = csv.reader(file('citylist.csv'))
    for line in city_csv:
        # line[0] is cityID, like CHBJ000000, line[2] is city_en_name, like beijing
        # logger.debug('cityID cityName cityenName = {0} {1} {2}'.format(line[0], line[1], line[2]))
        # logger.debug('city_info = ' + url_item[0] + ' ' + url_item[1])
        url_item = gene_url(line[0])
        q_citys.put(url_item[0] + '|' + url_item[1] + '|' + line[0] + '|' + line[2])
    logger.info('finish read_city')

if __name__ == '__main__':
    logger.info('########## Program start.')
    # for (key, value) in settings.items():
    #     print key, value
    # read city in csv file and generte city_url store in
    read_city()
    add_threads()

    logger.info('########## Program end.')