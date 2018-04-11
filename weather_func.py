import requests

def get_db_data(ct, cur):
    cur.execute("SELECT * FROM info WHERE city = %s", [ct])
    return cur.fetchone()

def get_api_data(city):
    payload = {'q': city, 'APPID':'02485176f4257a69383d168ccf8c169c', 'units':'imperial'}
    r = requests.get('https://api.openweathermap.org/data/2.5/weather', params=payload)
    weather_data = r.json()
    temp = weather_data['main']['temp']
    temp_min = weather_data['main']['temp_min']
    temp_max = weather_data['main']['temp_max']
    description = weather_data['weather'][0]['description']
    wind_speed = weather_data['wind']['speed']
    return temp, temp_min, temp_max, description, wind_speed