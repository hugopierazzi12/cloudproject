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
    XXX
}

credentials = service_account.Credentials.from_service_account_info(json_key)

# Initialisation du client BigQuery avec les informations d'authentification
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

YOUR_PASSWORD = "TonMotDePasseSécurisé"
YOUR_HASH_PASSWD = hashlib.sha256(YOUR_PASSWORD.encode()).hexdigest()

# Initialisation du client Text-to-Speech de Google Cloud avec les informations d'authentification
tts_client = texttospeech.TextToSpeechClient(credentials=credentials)

# Clé API OpenAI
openai.api_key = "XXX"

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
