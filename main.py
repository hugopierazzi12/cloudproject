from flask import Flask, request, jsonify
import hashlib
from google.cloud import bigquery
import requests
from datetime import datetime
import os

# Définir les informations d'authentification pour Google Cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"

# Créer le client BigQuery
client = bigquery.Client(project="cloudproject-424110")

# Mot de passe hashé pour l'authentification
YOUR_HASH_PASSWD = "7d23152dbf2c72714cd5be64064f3d7ac437c54539c80893b8d911a237f931c8"

app = Flask(__name__)

# Récupérer les noms de colonnes de la base de données
q = """
SELECT * FROM `cloudproject-424110.weather_data.weather_records` LIMIT 10
"""
query_job = client.query(q)
df = query_job.to_dataframe()

@app.route('/send-to-bigquery', methods=['GET', 'POST'])
def send_to_bigquery():
    if request.method == 'POST':
        if request.get_json(force=True)["passwd"] != YOUR_HASH_PASSWD:
            raise Exception("Incorrect Password!")
        data = request.get_json(force=True)["values"]
        
        # Pour l'exercice 2 : Appeler l'API openweather et ajouter les valeurs résultantes au dictionnaire `data`
        API_key = "dc205f6b07d82ca369a1a66980ea5009"
        city = "Lausanne"
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}&units=metric'
        
        response = requests.get(url)
        weather_data = response.json()
        
        data["outdoor_temp"] = round(weather_data['main']['temp'])
        data["outdoor_humidity"] = round(weather_data['main']['humidity'])
        data["outdoor_weather"] = weather_data['weather'][0]['description']
        
        # Construire la requête d'insertion
        q = """INSERT INTO `cloudproject-424110.weather_data.weather_records` """
        names = ""
        values = ""
        for k, v in data.items():
            names += f"""{k},"""
            if df.dtypes[k] == float:
                values += f"""{v},"""
            else:
                # Les valeurs de type string dans la requête doivent être entourées de guillemets simples
                values += f"""'{v}',"""
        
        # Supprimer la dernière virgule
        names = names[:-1]
        values = values[:-1]
        q = q + f""" ({names})""" + f""" VALUES({values})"""
        
        query_job = client.query(q)
        query_job.result()  # Attendre que la requête soit terminée
        return {"status": "success", "data": data}
    return {"status": "failed"}

# Pour l'exercice 3 : Compléter l'endpoint suivant.
@app.route('/get_outdoor_weather', methods=['GET', 'POST'])
def get_outdoor_weather():
    if request.method == 'POST':
        if request.get_json(force=True)["passwd"] != YOUR_HASH_PASSWD:
            raise Exception("Incorrect Password!")
        # Récupérer les dernières valeurs de température extérieure de la base de données
        q = """
        SELECT outdoor_temp, outdoor_humidity, outdoor_weather 
        FROM `cloudproject-424110.weather_data.weather_records`
        ORDER BY date DESC, time DESC
        LIMIT 1
        """
        query_job = client.query(q)
        result = query_job.to_dataframe().to_dict(orient='records')[0]
        return {"status": "success", "data": result}
    return {"status": "failed"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
