# Google Weather
### *Kevin Pocthier and Hugo Pierazzi*

<br>
<br>

<p align="center">
  <img src="https://imgur.com/l7QXu4L.png" alt="Google Weather" style="width:50%;">
</p>

<br>

## Trailer and Explanation

[Youtube Video](https://youtu.be/xZMuOwHl4E0) 

<br>

## Google Weather IoT Solution

We are excited to introduce our IoT solution, **Google Weather**. Our product provides a variety of measurements, including:

- Indoor and outdoor temperature
- CO2 levels
- Humidity levels
- Weather forecasts
- Historical data

## Key Features of Our Box

Our device comes with several functionalities:

- Real-time weather announcements
- Light signals based on sensor information
- Vibration alerts

## Dashboard

Our Dashboard, like our device, enables you to view various indoor and outdoor weather data, along with historical data presented in graphs and tables.

<p align="center">
  <img src="https://imgur.com/3pisUPv.png" alt="Google Weather" style="width:50%;">
</p>

<br>


## Project Structure

### Flask Folder

This folder contains all the necessary documents to run and deploy the backend of our product, primarily the `main.py` file. This file handles most of the functionalities and integrates APIs such as Text-to-Speech, OpenAI, and OpenWeather. It also sends the data collected by the device to BigQuery. The Text-to-Speech system, managed with GPT-3.5 from OpenAI, is also controlled from this backend.

[Access the Flask Backend](https://weather-monitor-zsladhfraq-ew.a.run.app)

### Streamlit Folder

This folder includes the documents required to set up and deploy Streamlit on Cloud Run. The main file, `Dashboard.py`, provides a sleek and functional layout for our application. One of its primary functions is to fetch the BigQuery data collected by the M5Stack and display it on our dashboard.

[Access the Streamlit Dashboard](https://streamlit-dashboard-zsladhfraq-ew.a.run.app)

### UIFlow File

This file contains the complete code for our M5Stack. It defines the Flask routes and establishes an effective and relevant layout. Here’s a summary of its functions and the information displayed on the screen:

- Weather announcements triggered by the motion detector, limited to once per minute to avoid spam. These announcements Text-to-Speech are generated using a GPT-3.5 prompt and information from the OpenWeather [API](https://openweathermap.org/api)
.
- Vibration alert when CO2 levels exceed 600 ppm, indicating poor air quality.
- LED indicators: Red when humidity is between 40-59%, blue when above 60%, and green when below 40%.
- Wifi solution: In the event of a connection failure, you can have back-up wifis.

<p align="center">
  <img src="https://imgur.com/AzPbQLW.png" alt="Google Weather" style="width:50%;">
</p>

<br>

<br>

## Screen Presentation and Design Choices

For the presentation of our screen on the M5Stack device, we decided to display all the information on a single page. This approach simplifies the use of the device and provides a quick overview of all the necessary weather information. Our goal is to make the interface intuitive by using icons, which is especially important given the small screen size. The weather forecast for the next five days is also displayed, specifically at noon, to give users a practical overview of upcoming conditions.

To enhance the user experience, we integrated vocal announcements of the current weather, triggered by the motion sensor. This feature allows users to get the weather information just before leaving the house. Additionally, the information is updated every three seconds to ensure real-time accuracy. These design choices were made to maximize usability and efficiency in a compact and user-friendly format.


## Distribution of Work

<table style="width:100%; border: 2px solid black;">
  <tr>
    <th style="background-color:#1E90FF; color:white; padding:10px;">Kevin</th>
    <th style="background-color:#000000; color:white; padding:10px;">Hugo</th>
  </tr>
  <tr>
    <td style="background-color:#f0f0f0; padding:20px; vertical-align:top;">
      M5Stack Visual, Sensors, Flask, Video, (450 lines approximately)
    </td>
    <td style="background-color:#f0f0f0; padding:20px; vertical-align:top;">
      Flask, BigQuery, Text-To-Speech, Video (450 lines approximately)
    </td>
  </tr>
</table>
