with open('/Users/skomorohovaleks/PycharmProjects/TG-Bot/.venv/api_key_2.txt', 'r') as file:
    API_KEY = file.read().strip()

import requests

def forecast(city_name = "Moscow"):
    # URL и параметры
    location_url = "http://dataservice.accuweather.com/locations/v1/cities/search"
    params = {
        "apikey": API_KEY,
        "q": city_name,
        "language": "en-us",
        "details": "false"
    }

    # Выполнение запроса

    response = requests.get(location_url, params=params)

    match response.status_code:
        case 200:
            data = response.json()
            if data:
                location_key = data[0].get("Key")
                print(f"Location Key for {city_name}: {location_key}")

            else:
                return f"No results found for city: {city_name}"
        case 304:
            return 'Нету интернета(((('
        case 401:
            return 'Ошибка подключения к серверу (не удаётся авторизоваться по данному api ключу)'
        case 503:
            return 'Сервис временно недоступен.'
        case 504:
            return 'Сервер долго отвечает(((('
        case _:
            return f"Error: {response.status_code}, {response.text}"

    weather_url = f'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}'
    params = {
        'apikey': API_KEY,
        'details': 'true'
    }

    response2 = requests.get(weather_url, params=params)
    if response2.status_code == 200:
        data = response2.json()
        print(f'Данные получены')
    else:
        return f"Ошибка получения Weather Data: {response2.status_code}, {response2.text}"

    # rain_probability = fc_data[0]['RainProbability']  # %
    # temperature = fc_data[0]['Temperature']['Value']  # Unit: F
    # wind_speed = fc_data[0]['WindGust']['Speed']['Value']  # Unit: mi/h
    # humidity = fc_data[0]['RelativeHumidity']  # %
    #
    # needed_data = {
    #     'rain_probability': rain_probability,
    #     'temperature': temperature,
    #     'wind_speed': wind_speed,
    #     'humidity': humidity
    # }

    # Извлечение данных
    forecast_data = []
    for day in data["DailyForecasts"]:
        date = day["Date"]
        wind_speed = day["Day"]["Wind"]["Speed"]["Value"]
        wind_direction = day["Day"]["Wind"]["Direction"]["Localized"]
        humidity = day["Day"]["RelativeHumidity"]["Average"]
        precipitation = day["Day"]["PrecipitationProbability"]
        temp_max = day["Temperature"]["Maximum"]["Value"]
        temp_min = day["Temperature"]["Minimum"]["Value"]

        forecast_data.append({
            "Date": date,
            "WindSpeed": wind_speed,
            "WindDirection": wind_direction,
            "Humidity": humidity,
            "PrecipitationProbability": precipitation,
            "TemperatureMax": temp_max,
            "TemperatureMin": temp_min
        })
    return forecast_data
