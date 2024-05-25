import streamlit as st
from google.cloud import bigquery
import pandas as pd
from google.oauth2 import service_account
import json
import requests
import datetime

# Service account key details
service_account_info = {key_json
}

credentials = service_account.Credentials.from_service_account_info(service_account_info)

client = bigquery.Client(credentials=credentials, project=credentials.project_id)

def get_data_from_bigquery():
    query = """
    SELECT * FROM `cloudproject-424110.weather_data.weather_records`
    ORDER BY date DESC, time DESC
    """
    query_job = client.query(query)
    results = query_job.result()
    return results.to_dataframe()

def get_outdoor_weather(api_key, latitude, longitude):
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric'
    response = requests.get(url)
    data = response.json()
    if 'main' in data and 'weather' in data:
        outdoor_temp = data['main']['temp']
        outdoor_temp_max = data['main']['temp_max']
        outdoor_temp_min = data['main']['temp_min']
        outdoor_humidity = data['main']['humidity']
        weather_icon = data['weather'][0]['icon']
        return outdoor_temp, outdoor_temp_max, outdoor_temp_min, outdoor_humidity, weather_icon
    else:
        return None, None, None, None, None

def get_forecast(api_key, city_name):
    base_url = 'http://api.openweathermap.org/data/2.5/forecast'
    complete_url = f"{base_url}?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(complete_url)
    
    if response.status_code == 200:
        data = response.json()
        forecasts = data['list']
        forecast_data = []
        
        for forecast in forecasts:
            forecast_time = forecast['dt_txt']
            if '12:00:00' in forecast_time:  # Filter for noon forecasts
                temp = forecast['main']['temp']
                temp_min = forecast['main']['temp_min']
                temp_max = forecast['main']['temp_max']
                weather_description = forecast['weather'][0]['description']
                icon = forecast['weather'][0]['icon']
                
                forecast_data.append({
                    'Date': forecast_time,
                    'Day': pd.to_datetime(forecast_time).strftime('%A'),
                    'Temperature': temp,
                    'Min Temp': temp_min,
                    'Max Temp': temp_max,
                    'Description': weather_description,
                    'Icon': f"http://openweathermap.org/img/wn/{icon}.png"
                })
                if len(forecast_data) >= 5:  # Limit to 5 forecasts
                    break
        
        df = pd.DataFrame(forecast_data)
        return df
    else:
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

data = get_data_from_bigquery()

# Your OpenWeatherMap API key
api_key = "dc205f6b07d82ca369a1a66980ea5009"
city_name = 'lausanne'

outdoor_temp, outdoor_temp_max, outdoor_temp_min, outdoor_humidity, weather_icon = get_outdoor_weather(api_key, 46.516, 6.6328)
forecast_df = get_forecast(api_key, city_name)

# CSS to customize appearance
page_bg_img = '''
<style>
.stApp {
    background-image: url("https://imgur.com/QyHdWgV.png");
    background-size: cover;
}

.big-font {
    font-size:50px !important;
}

.container {
    padding: 10px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 5px;
    margin-bottom: 10px;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

st.title("Weather Dashboard")

st.markdown(f'<p class="big-font">{pd.to_datetime("today").strftime("%Y-%m-%d")}</p>', unsafe_allow_html=True)
st.markdown(f'<p class="big-font">{pd.to_datetime("now").strftime("%H:%M")}</p>', unsafe_allow_html=True)

# Use columns to display containers
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.write("### Indoor Data")
    if not data.empty:
        current_data = data.iloc[0]
        st.write(f"Indoor Temperature: {current_data['indoor_temp']} °C")
        st.write(f"Indoor Humidity: {current_data['indoor_humidity']} %")
    else:
        st.write("No data available")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.write("### Outdoor Data")
    if outdoor_temp is not None:
        st.write(f"Current Temperature: {outdoor_temp} °C")
        st.write(f"Max Temperature: {outdoor_temp_max} °C")
        st.write(f"Min Temperature: {outdoor_temp_min} °C")
        st.write(f"Humidity: {outdoor_humidity} %")
        if weather_icon:
            icon_url = f"http://openweathermap.org/img/wn/{weather_icon}@2x.png"
            st.image(icon_url, width=100)
    else:
        st.write("Outdoor Temperature: Data not available")
        st.write("Weather icon not available")
    st.markdown('</div>', unsafe_allow_html=True)

# Add the 5-day forecast section aligned horizontally
st.write("### 5-Day Forecast")
if not forecast_df.empty:
    cols = st.columns(5)
    for i, (index, row) in enumerate(forecast_df.iterrows()):
        with cols[i]:
            st.markdown(f"**{row['Day']}**")
            st.markdown(f"Temp: {row['Temperature']} °C")
            st.image(row['Icon'], width=100)
            if i >= 4:
                break
else:
    st.write("No forecast data available")

st.write("### Historical Data")
columns_to_plot = ['date', 'indoor_temp', 'indoor_humidity']
if 'outdoor_temp_max' in data.columns:
    columns_to_plot.append('outdoor_temp_max')
st.line_chart(data[columns_to_plot].set_index('date'))

st.write("### Historical Data Table")
st.dataframe(data)
