from flask import Flask, render_template
import requests
import os
from datetime import datetime, timezone
from twilio.rest import Client
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('WPP_TWILLIO')
YOUR_WHATSAPP_NUMBER = os.getenv('WPP')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/")
def index():
    url = "https://dcoh.watch/api/v1/Overwatch/Titans"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        cocijo_data = next((item for item in data.get('maelstroms', []) if item['name'] == 'Cocijo'), None)

        if cocijo_data:
            progress_percentage = cocijo_data['totalProgress'] * 100
            heart_progress_percentage = cocijo_data['heartProgress'] * 100
            hearts_remaining = cocijo_data['heartsRemaining']
            heart_progress_label = f"Progresso coração #{9 - hearts_remaining}" if hearts_remaining <= 8 else "Coração desconhecido"

            completion_time_str = cocijo_data['completionTimeEstimate']
            completion_time = datetime.fromisoformat(completion_time_str.replace("Z", "+00:00"))
            current_time = datetime.now(timezone.utc)
            remaining_time = completion_time - current_time

            remaining_hours, remainder = divmod(remaining_time.total_seconds(), 3600)
            remaining_minutes = remainder // 60
            formatted_remaining_time = f"{int(remaining_hours):02}:{int(remaining_minutes):02}"

            if heart_progress_percentage >= 90:
                message_body = (
                    f"🚨 Acorda vagabundo: O progresso do coração atingiu {heart_progress_percentage:.2f}%!\n"
                    f"Estimativa de conclusão: {formatted_remaining_time}.\n"
                    f"VAI EXPLODIR! 💥"
                )
                send_whatsapp_message(message_body)

            return render_template(
                "index.html",
                cocijo=cocijo_data,
                progress=progress_percentage,
                heart_progress=heart_progress_percentage,
                heart_progress_label=heart_progress_label,
                time_estimate=formatted_remaining_time
            )
        else:
            return render_template("index.html", error="Nenhum objeto com o nome 'Cocijo' encontrado.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao fazer a requisição: {e}")
        return render_template("index.html", error=f"Erro ao fazer a requisição: {e}")
    except ValueError as json_error:
        logger.error(f"Erro ao processar JSON: {json_error}")
        return render_template("index.html", error=f"Erro ao processar JSON: {json_error}")

def send_whatsapp_message(message_body):
    try:
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message_body,
            to=YOUR_WHATSAPP_NUMBER
        )
        logger.info(f"Mensagem do WPP enviada com sucesso: SID {message.sid}")
    except Exception as e:
        logger.error(f"Erro ao enviar a mensagem: {e}")
        raise

if __name__ == "__main__":
    app.run(debug=True)
