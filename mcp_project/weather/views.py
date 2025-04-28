from django.http import JsonResponse
import requests
import urllib.parse
from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json

def to_ascii(words):
    encoded_text = urllib.parse.quote(words.replace('台', '臺'))
    return encoded_text

def get_weather_json_data(location_name, element_name):
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091?Authorization=CWA-86108200-E310-47A5-9328-65BDD0D5BB93&LocationName={to_ascii(location_name)}&ElementName={to_ascii(element_name)}&sort=time&format=JSON"
    data = requests.get(url)   # 取得 JSON 檔案的內容為文字
    return data.json()

def data_summary(json_data):
    # 取出時間與溫度資料
    time_entries = json_data["records"]["Locations"][0]["Location"][0]["WeatherElement"][0]["Time"]

    # 建立一個每天溫度列表
    daily_temperatures = defaultdict(list)

    for entry in time_entries:
        start_time = entry["StartTime"]
        date_only = datetime.fromisoformat(start_time).date()  # 只取到日期部分
        temp = entry["ElementValue"][0]["MaxTemperature"]
        if temp:
            daily_temperatures[date_only].append(float(temp))

    # 整理每天溫度範圍
    daily_ranges = {}
    for date, temps in daily_temperatures.items():
        min_temp = min(temps)
        max_temp = max(temps)
        daily_ranges[date.isoformat()] = f"{min_temp}°C - {max_temp}°C"
    
    return daily_ranges

def get_weather(request):
    try:
        input_raw = request.GET.get('input')
        # 固定查詢台北市的最高溫度
        try:
            # 嘗試當成 JSON 解析
            input_parsed = json.loads(input_raw)
            if isinstance(input_parsed, dict) and 'city' in input_parsed:
                city = input_parsed['city']
            else:
                city = input_raw  # fallback
        except:
            city = input_raw  # fallback
        raw_data = get_weather_json_data(city, '最高溫度')
        summary = data_summary(raw_data)
        return JsonResponse({
            'status': 'success',
            'location': city,
            'data': summary
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    



def get_date(request):
    try:
        today = datetime.now(ZoneInfo("Asia/Taipei")).date()
        result = {}

        # 中文星期對照表
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

        for i in range(-7, 8):
            target_date = today + timedelta(days=i)
            label = ""

            if i == 0:
                label = "今天"
            elif i == -1:
                label = "昨天"
            elif i == 1:
                label = "明天"
            elif i < 0:
                label = f"{abs(i)}天前"
            elif i > 0:
                label = f"{i}天後"

            # 取得星期幾（target_date.weekday() 會回傳 0=星期一, 6=星期日）
            weekday = weekdays[target_date.weekday()]

            # 每一天記錄更多資訊：日期 + 星期
            result[label] = {
                "date": target_date.isoformat(),
                "weekday": weekday
            }

        return JsonResponse({
            'status': 'success',
            'dates': result
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)