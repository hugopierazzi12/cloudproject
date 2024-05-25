from flask import Flask, request, jsonify, Response
from google.cloud import bigquery, texttospeech
import requests
import hashlib
import json
from google.oauth2 import service_account
import openai

app = Flask(__name__)

# Configuration de la clé Google Cloud
json_key = {
    "type": "service_account",
    "project_id": "cloudproject-424110",
    "private_key_id": "cd884a9677b1eb1f20e4b1fe209eff92636fb73e",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDYg+fLrQz0Xm2W\nYaJWa/Yj1tWNPIbIrofefc3eahQsDzJVymELk+VeHmR6ySeE6rOUHt6z7JmTsul9\nrrDVwtSPlYB8K46rsOCsFcJnMwlFkIPW+O2P0ml1KfCl7ydwm2Cf+Zo6MsYBD4yv\nrQiHKfF89rlMBBpbFDntjMdx4LjqhPEzf5B7AXUaUe9zdz3isrxxb6s7hC7oGkTY\nUl0vvMwAsiNx9vc4rFgTpiF3t71SQEv/DIBnojKay14QB74VzzNCzDTxUEHxF/tL\nZB38TUZVyTi51yxVb+fcAWuanWP+cYX8x9yj9q81k4i/2EKt3CeX2i3jr614gnAL\nVBm8oyOJAgMBAAECggEAIBpcw+MehNw8cPv8g0ZiOlmoE9c53+ca77clD3mYkJjX\nPIezoHEXJP+qI9eQE8HuCwQRvslR0yfHvZIpl6RZ+okvAho+PwBMq89VIhKb6RPe\nrID/zl+jMdNcYmolpalwKAAtKTxuhek9ka29Ejd6ni4B9v6zvrXuyeViDCVHHcR+\n/JHWo9M+bi68mo3aAfmiOmQyqB4xd0XL6k7zN1EdytkkEKRLgj6eSxCqXLiCRUxp\npcqdWjn3VDKHOS/dyJe9vw8rsqP2E8Js9iCHPXbG1k7E12y4IKLfUvPFBVKmAT7X\nR5ITCVF39/v2WjmdPiyeO3TcWaw1Fk4y49uPJhLzRQKBgQD7Yyn+ReO/1RFh15Lo\nNavGXgOT9C2ycXUB6Pl1RM9WP+1ryUBTNU0KanuhYBk3HhwJ/SNjW6XLc+jBC2Ga\nyNUtqzZvLrTG64cpxVDVlWiciPeuo8YWwEAeaFfMaG627Deyy7ATEdTLnuSyNWyw\nF+sdlDG7/iZ80tBCd4Nq55Wm1QKBgQDcfO//2cSmJNZB0fdNJrr2yVlRpOEeEGGC\ntpPbzHARi2U53Hwf6zXtfZD4hI8NrJr+6IAofcSM35zjFwWtr1kNWXCKVnAE1tsq\nHsioZXhbqKumyKufQ9jG//Csvc/73XD74/BrL7vp3CSjEi0mMfdgpcTWLXgZOD7D\nMEkUN5LL5QKBgQCzn4ul8HJn4+rjqpGB8remqg6MbXEpjAA7OSjmLiCoVE1lMwwP\naIp/4s4r5Oqfg5gtWv8qQ5YX5d5t8Z/wZYhNdYUTtJ/fcvPFWQQFWRjCoOu5kbQ9\nFWm7UHtLx2M0uVyjGP/a4GbYh9SJsbrTqIOLQxS2a0c88bV1iMgSXx+DcQKBgHSf\n3S5+mIatC2uLTPzRFKm+vPDzfmOxlHJYcoMbctfE3MkrN7iGaGLzPQBG1YgNGXrl\nrgw84f8FtG1l2woQqtDl0yJJMD1PDGQOHmL8MRqCcDDrCeRXNc2kyUAFsoJtkfqa\niauYdxPu7q4Wyize1xOW+zOyn0jvuDr0SmNYNdyFAoGAHcbvQHzUM4vXkPBus6A0\nfumrfatmYCwVKl8zwUA5NgO/cZrdVIeO75RghYZ8M7kcbE92wSrd6wa2tQBFw6EO\nzXK93b3jSVfV+eKYrx7ZpZLLPx0TRv/2QEQhKJ3yCRj681/LF+Tw8+ZvXE51LdtY\nuwg34ehcKtzQy5aQFF64JlU=\n-----END PRIVATE KEY-----\n",
    "client_email": "cloudproject@cloudproject-424110.iam.gserviceaccount.com",
    "client_id": "115004387933230655429",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/cloudproject-424110.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

credentials = service_account.Credentials.from_service_account_info(json_key)

# Initialisation du client BigQuery avec les informations d'authentification
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

YOUR_PASSWORD = "TonMotDePasseSécurisé"
YOUR_HASH_PASSWD = hashlib.sha256(YOUR_PASSWORD.encode()).hexdigest()

# Initialisation du client Text-to-Speech de Google Cloud avec les informations d'authentification
tts_client = texttospeech.TextToSpeechClient(credentials=credentials)

# Clé API OpenAI
openai.api_key = "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"

# Nouvelle méthode pour initialiser le client OpenAI
client_openai = openai.OpenAI(api_key=openai.api_key)

def generate_weather_advice(description):
    prompt = f"Based on the current weather: {description}, what recommendations should I provide? Start with the forecast, then follow with the advice. Please avoid using special characters, use letters only. Lastly, ensure the advice is concise, limited to one complete sentence."

    response = client_openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def text_to_speech(text):
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code='en-US',
        name='en-US-Wavenet-D',
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16)  # LINEAR16 pour WAV

    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config)

    output_file = 'output.wav'
    with open(output_file, 'wb') as out:
        out.write(response.audio_content)

    return output_file

def get_outdoor_weather():
    API_key = "dc205f6b07d82ca369a1a66980ea5009"
    city = "Lausanne"
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}&units=metric'
    response = requests.get(url)
    data = response.json()
    return {
        "outdoor_temp": round(data['main']['temp']),
        "outdoor_humidity": round(data['main']['humidity']),
        "outdoor_weather": data['weather'][0]['description']
    }

@app.route('/send-to-bigquery', methods=['POST'])
def send_to_bigquery():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if data["passwd"] != YOUR_HASH_PASSWD:
            return jsonify({"status": "failed", "message": "Incorrect Password!"}), 401
        
        indoor_data = data["values"]
        outdoor_data = get_outdoor_weather()
        combined_data = {**indoor_data, **outdoor_data}
        
        print("Received data:", combined_data)  # Debugging

        # Building the query
        query = f"""
        INSERT INTO cloudproject-424110.weather_data.weather_records (date, time, indoor_temp, indoor_humidity, outdoor_temp, outdoor_humidity, outdoor_weather)
        VALUES ('{combined_data['date']}', '{combined_data['time']}', {combined_data['indoor_temp']}, {combined_data['indoor_humidity']}, {combined_data['outdoor_temp']}, {combined_data['outdoor_humidity']}, '{combined_data['outdoor_weather']}')
        """

        try:
            query_job = client.query(query)
            query_job.result()  # Wait for the job to complete
            print("Data inserted successfully")
        except Exception as e:
            print("Error inserting data:", e)  # Debugging
            return jsonify({"status": "failed", "message": str(e)}), 500
        
        return jsonify({"status": "success", "data": combined_data})
    return jsonify({"status": "failed"}), 400

@app.route('/get_text_to_speech', methods=['GET'])
def text_to_speech_route():
    text = request.args.get('text')
    if not text:
        return jsonify({"status": "failed", "message": "Text parameter is required"}), 400

    output_file = text_to_speech(text)
    
    def generate():
        with open(output_file, 'rb') as f:
            yield from f

    return Response(generate(), mimetype='audio/wav')

@app.route('/get_weather_advice', methods=['GET'])
def get_weather_advice():
    city = "Lausanne"
    API_key = "dc205f6b07d82ca369a1a66980ea5009"
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}&units=metric'
    weather_response = requests.get(url).json()
    description = weather_response['weather'][0]['description']

    generated_advice = generate_weather_advice(description)
    return jsonify({"advice": generated_advice})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
