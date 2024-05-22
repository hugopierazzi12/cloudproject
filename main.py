from flask import Flask, request, jsonify
import hashlib
from google.cloud import bigquery
import requests
from datetime import datetime
import os
import json

# Écrire les informations d'authentification dans un fichier temporaire
service_account_info = {
  "type": "service_account",
  "project_id": "cloudproject-424110",
  "private_key_id": "cd884a9677b1eb1f20e4b1fe209eff92636fb73e",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDYg+fLrQz0Xm2W\nYaJWa/Yj1tWNPIbIrofefc3eahQsDzJVymELk+VeHmR6ySeE6rOUHt6z7JmTsul9\nrrDVwtSPlYB8K46rsOCsFcJnMwlFkIPW+O2P0ml1KfCl7ydwm2Cf+Zo6MsYBD4yv\nrQiHKfF89rlMBBpbFDntjMdx4LjqhPEzf5B7AXUaUe9zdz3isrxxb6s7hC7oGkTY\nUl0vvMwAsiNx9vc4rFgTpiF3t71SQEv/DIBnojKay14QB74VzzNCzDTxUEHxF/tL\nZB38TUZVyTi51yxVb+fcAWuanWP+cYX8x9yj9q81k4i/2EKt3CeX2i3jr614gnAL\nVBm8oyOJAgMBAAECggEAIBpcw+MehNw8cPv8g0ZiOlmoE9c53+ca77clD3mYkJjX\nPIezoHEXJP+qI9eQE8HuCwQRvslR0yfHvZIpl6RZ+okvAho+PwBMq89VIhKb6RPe\nrID/zl+jMdNcYmolpalwKAAtKTxuhek9ka29Ejd6ni4B9v6zvrXuyeViDCVHHcR+\n/JHWo9M+bi68mo3aAfmiOmQyqB4xd0XL6k7zN1EdytkkEKRLgj6eSxCqXLiCRUxp\npcqdWjn3VDKHOS/dyJe9vw8rsqP2E8Js9iCHPXbG1k7E12y4IKLfUvPFBVKmAT7X\nR5ITCVF39/v2WjmdPiyeO3TcWaw1Fk4y49uPJhLzRQKBgQD7Yyn+ReO/1RFh15Lo\nNavGXgOT9C2ycXUB6Pl1RM9WP+1ryUBTNU0KanuhYBk3HhwJ/SNjW6XLc+jBC2Ga\nyNUtqzZvLrTG64cpxVDVlWiciPeuo8YWwEAeaFfMaG627Deyy7ATEdTLnuSyNWyw\nF+sdlDG7/iZ80tBCd4Nq55Wm1QKBgQDcfO//2cSmJNZB0fdNJrr2yVlRpOEeEGGC\ntpPbzHARi2U53Hwf6zXtfZD4hI8NrJr+6IAofcSM35zjFwWtr1kNWXCKVnAE1tsq\nHsioZXhbqKumyKufQ9jG//Csvc/73XD74/BrL7vp3CSjEi0mMfdgpcTWLXgZOD7D\nMEkUN5LL5QKBgQCzn4ul8HJn4+rjqpGB8remqg6MbXEpjAA7OSjmLiCoVE1lMwwP\naIp/4s4r5Oqfg5gtWv8qQ5YX5d5t8Z/wZYhNdYUTtJ/fcvPFWQQFWRjCoOu5kbQ9\nFWm7UHtLx2M0uVyjGP/a4GbYh9SJsbrTqIOLQxS2a0c88bV1iMgSXx+DcQKBgHSf\n3S5+mIatC2uLTPzRFKm+vPDzfmOxlHJYcoMbctfE3MkrN7iGaGLzPQBG1YgNGXrl\nrgw84f8FtG1l2woQqtDl0yJJMD1PDGQOHmL8MRqCcDDrCeRXNc2kyUAFsoJtkfqa\niauYdxPu7q4Wyize1xOW+zOyn0jvuDr0SmNYNdyFAoGAHcbvQHzUM4vXkPBus6A0\nfumrfatmYCwVKl8zwUA5NgO/cZrdVIeO75RghYZ8M7kcbE92wSrd6wa2tQBFw6EO\nzXK93b3jSVfV+eKYrx7ZpZLLPx0TRv/2QEQhKJ3yCRj681/LF+Tw8+ZvXE51LdtY\nuwg34ehcKtzQy5aQFF64JlU=\n-----END PRIVATE KEY-----\n",
  "client_email": "cloudproject@cloudproject-424110.iam.gserviceaccount.com",
  "client_id": "115004387933230655429",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/cloudproject%40cloudproject-424110.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

with open('service_account.json', 'w') as f:
    json.dump(service_account_info, f)

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
        
        # Appeler l'API openweather et ajouter les valeurs résultantes au dictionnaire `data`
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

# Compléter l'endpoint suivant.
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
