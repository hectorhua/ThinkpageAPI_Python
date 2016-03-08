# -*- coding: UTF-8 -*-
# __author__ = 'zhonghua'

def gene_items_cn():
    settings = {}
    for option in ['city_name', 'city_name_weather', 'city_name_en_weather', \
                   'json_all_redis', \
                   'caacwfnew24', 'caacwfnew48', 'caacwfnew72', \
                   'current_status', 'current_temperature', 'current_humidity', 'current_wind_power', 'current_wind_direction', 'feel_temperature', 'visibility', 'atmospheric', 'observe_time', 'observe_all', \
                   'AQI', 'PM25', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'air_quality', 'air_last_update', 'air_all', \
                   'dressing_brief', 'dressing_details', 'ultraviolet_brief', 'ultraviolet_details', 'car_washing_brief', 'car_washing_details', 'travel_brief', 'travel_details', 'flu_brief', 'flu_details', 'sport_brief', 'sport_details', 'index_all', \
                   'forecast_name', 'forecast_all0', 'forecast_all1', 'forecast_all2', 'forecast_all3', 'forecast_all4', 'forecast_all5', 'forecast_all6']:
        settings[option] = ''
    for option in ['forecast_date', 'forecast_week', 'status_day_night', 'wind_direction_power', 'temperature_high', 'temperature_low', 'forecast_all', \
                   'forecast_date_en', 'forecast_week_en', 'status_day_night_en', 'wind_direction_power_en', 'temperature_high_en', 'temperature_low_en', 'forecast_all_en']:
        settings[option] = []
        settings[option][:] = []
    return settings

def gene_items_en():
    settings = {}
    for option in ['json_all_redis_en', \
                   'current_status_en', 'current_temperature_en', 'current_humidity_en', 'current_wind_power_en', 'current_wind_direction_en', 'feel_temperature_en', 'visibility_en', 'atmospheric_en', 'observe_time_en', 'observe_all_en', \
                   'AQI_en', 'PM25_en', 'PM10_en', 'SO2_en', 'NO2_en', 'CO_en', 'O3_en', 'air_quality_en', 'air_last_update_en', 'air_all_en', \
                   'dressing_brief_en', 'dressing_details_en', 'ultraviolet_brief_en', 'ultraviolet_details_en', 'car_washing_brief_en', 'car_washing_details_en', 'travel_brief_en', 'travel_details_en', 'flu_brief_en', 'flu_details_en', 'sport_brief_en', 'sport_details_en', 'index_all_en', \
                   'forecast_name_en', 'forecast_all_en0', 'forecast_all_en1', 'forecast_all_en2', 'forecast_all_en3', 'forecast_all_en4', 'forecast_all_en5', 'forecast_all_en6']:
        settings[option] = ''
    for option in ['forecast_date', 'forecast_week', 'status_day_night', 'wind_direction_power', 'temperature_high', 'temperature_low', 'forecast_all', \
                   'forecast_date_en', 'forecast_week_en', 'status_day_night_en', 'wind_direction_power_en', 'temperature_high_en', 'temperature_low_en', 'forecast_all_en']:
        settings[option] = []
        settings[option][:] = []
    return settings

wf_items_cn = gene_items_cn()
wf_items_en = gene_items_en()

write_redis_item = ['city_ID', 'city_name', 'city_name_en', 'city_name_weather', 'city_name_en_weather', \
                    'json_all', 'json_all_en', 'json_all_redis', 'json_all_redis_en', \
                    'caacwfnew24', 'caacwfnew48', 'caacwfnew72', \
                    'observe_all', 'observe_all_en', \
                    'forecast_name', 'forecast_all0', 'forecast_all1', 'forecast_all2', 'forecast_all3', 'forecast_all4', 'forecast_all5', 'forecast_all6', \
                        'forecast_name_en', 'forecast_all_en0', 'forecast_all_en1', 'forecast_all_en2', 'forecast_all_en3', 'forecast_all_en4', 'forecast_all_en5', 'forecast_all_en6', \
                    'index_all', 'index_all_en', \
                    'air_all', 'air_all_en']