from flask import Flask, render_template, jsonify
import requests

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
            return render_template("index.html", cocijo=cocijo_data, progress=progress_percentage, heart_progress=heart_progress_percentage)
        else:
            return render_template("index.html", error="Nenhum objeto com o nome 'Cocijo' encontrado.")
    except requests.exceptions.RequestException as e:
        return render_template("index.html", error=f"Erro ao fazer a requisição: {e}")
    except ValueError as json_error:
        return render_template("index.html", error=f"Erro ao processar JSON: {json_error}")
    ##


if __name__ == "__main__":
    app.run(debug=True)
