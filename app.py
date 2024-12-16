from flask import Flask, render_template
import requests
from datetime import datetime, timezone

app = Flask(__name__)

@app.route("/")
def index():
    url = "https://dcoh.watch/api/v1/Overwatch/Titans"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        cocijo_data = next((item for item in data['maelstroms'] if item['name'] == 'Cocijo'), None)

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
        return render_template("index.html", error=f"Erro ao fazer a requisição: {e}")
    except ValueError as json_error:
        return render_template("index.html", error=f"Erro ao processar JSON: {json_error}")

if __name__ == "__main__":
    app.run(debug=True)
